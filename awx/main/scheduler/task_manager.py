# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved

# Python
from datetime import timedelta
import logging
import uuid
import json
import time
import sys
import signal

# Django
from django.db import transaction
from django.utils.translation import gettext_lazy as _, gettext_noop
from django.utils.timezone import now as tz_now
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# AWX
from awx.main.dispatch.reaper import reap_job
from awx.main.models import (
    Instance,
    UnifiedJob,
    WorkflowApproval,
    WorkflowJob,
    WorkflowJobNode,
    WorkflowJobTemplate,
)
from awx.main.scheduler.dag_workflow import WorkflowDAG
from awx.main.utils.pglock import advisory_lock
from awx.main.utils import (
    get_type_for_model,
    ScheduleTaskManager,
    ScheduleWorkflowManager,
)
from awx.main.utils.common import task_manager_bulk_reschedule
from awx.main.signals import disable_activity_stream
from awx.main.constants import ACTIVE_STATES
from awx.main.scheduler.dependency_graph import DependencyGraph
from awx.main.scheduler.task_manager_models import TaskManagerInstances
from awx.main.scheduler.task_manager_models import TaskManagerInstanceGroups
import awx.main.analytics.subsystem_metrics as s_metrics
from awx.main.utils import decrypt_field


logger = logging.getLogger('awx.main.scheduler')


def timeit(func):
    def inner(*args, **kwargs):
        t_now = time.perf_counter()
        result = func(*args, **kwargs)
        dur = time.perf_counter() - t_now
        args[0].subsystem_metrics.inc(f"{args[0].prefix}_{func.__name__}_seconds", dur)
        return result

    return inner


class TaskBase:
    def __init__(self, prefix=""):
        self.prefix = prefix
        # initialize each metric to 0 and force metric_has_changed to true. This
        # ensures each task manager metric will be overridden when pipe_execute
        # is called later.
        self.subsystem_metrics = s_metrics.Metrics(auto_pipe_execute=False)
        self.start_time = time.time()
        self.start_task_limit = settings.START_TASK_LIMIT
        for m in self.subsystem_metrics.METRICS:
            if m.startswith(self.prefix):
                self.subsystem_metrics.set(m, 0)

    def timed_out(self):
        """Return True/False if we have met or exceeded the timeout for the task manager."""
        elapsed = time.time() - self.start_time
        if elapsed >= settings.TASK_MANAGER_TIMEOUT:
            logger.warning(f"{self.prefix} manager has run for {elapsed} which is greater than TASK_MANAGER_TIMEOUT of {settings.TASK_MANAGER_TIMEOUT}.")
            return True
        return False

    @timeit
    def get_tasks(self, filter_args):
        wf_approval_ctype_id = ContentType.objects.get_for_model(WorkflowApproval).id
        qs = UnifiedJob.objects.filter(**filter_args).exclude(launch_type='sync').exclude(polymorphic_ctype_id=wf_approval_ctype_id).order_by('created')
        self.all_tasks = [t for t in qs]

    def record_aggregate_metrics(self, *args):
        if not settings.IS_TESTING():
            # increment task_manager_schedule_calls regardless if the other
            # metrics are recorded
            s_metrics.Metrics(auto_pipe_execute=True).inc(f"{self.prefix}__schedule_calls", 1)
            # Only record metrics if the last time recording was more
            # than SUBSYSTEM_METRICS_TASK_MANAGER_RECORD_INTERVAL ago.
            # Prevents a short-duration task manager that runs directly after a
            # long task manager to override useful metrics.
            current_time = time.time()
            time_last_recorded = current_time - self.subsystem_metrics.decode(f"{self.prefix}_recorded_timestamp")
            if time_last_recorded > settings.SUBSYSTEM_METRICS_TASK_MANAGER_RECORD_INTERVAL:
                logger.debug(f"recording {self.prefix} metrics, last recorded {time_last_recorded} seconds ago")
                self.subsystem_metrics.set(f"{self.prefix}_recorded_timestamp", current_time)
                self.subsystem_metrics.pipe_execute()
            else:
                logger.debug(f"skipping recording {self.prefix} metrics, last recorded {time_last_recorded} seconds ago")

    def record_aggregate_metrics_and_exit(self, *args):
        self.record_aggregate_metrics()
        sys.exit(1)

    def schedule(self):
        # Lock
        with task_manager_bulk_reschedule():
            with advisory_lock(f"{self.prefix}_lock", wait=False) as acquired:
                with transaction.atomic():
                    if acquired is False:
                        logger.debug(f"Not running {self.prefix} scheduler, another task holds lock")
                        return
                    logger.debug(f"Starting {self.prefix} Scheduler")
                    # if sigterm due to timeout, still record metrics
                    signal.signal(signal.SIGTERM, self.record_aggregate_metrics_and_exit)
                    self._schedule()
                    commit_start = time.time()

                if self.prefix == "task_manager":
                    self.subsystem_metrics.set(f"{self.prefix}_commit_seconds", time.time() - commit_start)
                self.record_aggregate_metrics()
                logger.debug(f"Finishing {self.prefix} Scheduler")


class WorkflowManager(TaskBase):
    def __init__(self):
        super().__init__(prefix="workflow_manager")

    @timeit
    def spawn_workflow_graph_jobs(self):
        result = []
        for workflow_job in self.all_tasks:
            if self.timed_out():
                logger.warning("Workflow manager has reached time out while processing running workflows, exiting loop early")
                ScheduleWorkflowManager().schedule()
                # Do not process any more workflow jobs. Stop here.
                # Maybe we should schedule another WorkflowManager run
                break
            dag = WorkflowDAG(workflow_job)
            status_changed = False
            if workflow_job.cancel_flag:
                workflow_job.workflow_nodes.filter(do_not_run=False, job__isnull=True).update(do_not_run=True)
                logger.debug('Canceling spawned jobs of %s due to cancel flag.', workflow_job.log_format)
                cancel_finished = dag.cancel_node_jobs()
                if cancel_finished:
                    logger.info('Marking %s as canceled, all spawned jobs have concluded.', workflow_job.log_format)
                    workflow_job.status = 'canceled'
                    workflow_job.start_args = ''  # blank field to remove encrypted passwords
                    workflow_job.save(update_fields=['status', 'start_args'])
                    status_changed = True
            else:
                workflow_nodes = dag.mark_dnr_nodes()
                WorkflowJobNode.objects.bulk_update(workflow_nodes, ['do_not_run'])
                # If workflow is now done, we do special things to mark it as done.
                is_done = dag.is_workflow_done()
                if is_done:
                    has_failed, reason = dag.has_workflow_failed()
                    logger.debug('Marking %s as %s.', workflow_job.log_format, 'failed' if has_failed else 'successful')
                    result.append(workflow_job.id)
                    new_status = 'failed' if has_failed else 'successful'
                    logger.debug("Transitioning {} to {} status.".format(workflow_job.log_format, new_status))
                    update_fields = ['status', 'start_args']
                    workflow_job.status = new_status
                    if reason:
                        logger.info(f'Workflow job {workflow_job.id} failed due to reason: {reason}')
                        workflow_job.job_explanation = gettext_noop("No error handling paths found, marking workflow as failed")
                        update_fields.append('job_explanation')
                    workflow_job.start_args = ''  # blank field to remove encrypted passwords
                    workflow_job.save(update_fields=update_fields)
                    status_changed = True

            if status_changed:
                if workflow_job.spawned_by_workflow:
                    ScheduleWorkflowManager().schedule()
                workflow_job.websocket_emit_status(workflow_job.status)
                # Operations whose queries rely on modifications made during the atomic scheduling session
                workflow_job.send_notification_templates('succeeded' if workflow_job.status == 'successful' else 'failed')

            if workflow_job.status == 'running':
                spawn_nodes = dag.bfs_nodes_to_run()
                if spawn_nodes:
                    logger.debug('Spawning jobs for %s', workflow_job.log_format)
                else:
                    logger.debug('No nodes to spawn for %s', workflow_job.log_format)
                for spawn_node in spawn_nodes:
                    if spawn_node.unified_job_template is None:
                        continue
                    kv = spawn_node.get_job_kwargs()
                    job = spawn_node.unified_job_template.create_unified_job(**kv)
                    spawn_node.job = job
                    spawn_node.save()
                    logger.debug('Spawned %s in %s for node %s', job.log_format, workflow_job.log_format, spawn_node.pk)
                    can_start = True
                    if isinstance(spawn_node.unified_job_template, WorkflowJobTemplate):
                        workflow_ancestors = job.get_ancestor_workflows()
                        if spawn_node.unified_job_template in set(workflow_ancestors):
                            can_start = False
                            logger.info(
                                'Refusing to start recursive workflow-in-workflow id={}, wfjt={}, ancestors={}'.format(
                                    job.id, spawn_node.unified_job_template.pk, [wa.pk for wa in workflow_ancestors]
                                )
                            )
                            display_list = [spawn_node.unified_job_template] + workflow_ancestors
                            job.job_explanation = gettext_noop(
                                "Workflow Job spawned from workflow could not start because it "
                                "would result in recursion (spawn order, most recent first: {})"
                            ).format(', '.join('<{}>'.format(tmp) for tmp in display_list))
                        else:
                            logger.debug(
                                'Starting workflow-in-workflow id={}, wfjt={}, ancestors={}'.format(
                                    job.id, spawn_node.unified_job_template.pk, [wa.pk for wa in workflow_ancestors]
                                )
                            )
                    if not job._resources_sufficient_for_launch():
                        can_start = False
                        job.job_explanation = gettext_noop(
                            "Job spawned from workflow could not start because it was missing a related resource such as project or inventory"
                        )
                    if can_start:
                        if workflow_job.start_args:
                            start_args = json.loads(decrypt_field(workflow_job, 'start_args'))
                        else:
                            start_args = {}
                        can_start = job.signal_start(**start_args)
                        if not can_start:
                            job.job_explanation = gettext_noop(
                                "Job spawned from workflow could not start because it was not in the right state or required manual credentials"
                            )
                    if not can_start:
                        job.status = 'failed'
                        job.save(update_fields=['status', 'job_explanation'])
                        job.websocket_emit_status('failed')

                    # TODO: should we emit a status on the socket here similar to tasks.py awx_periodic_scheduler() ?
                    # emit_websocket_notification('/socket.io/jobs', '', dict(id=))

        return result

    @timeit
    def get_tasks(self, filter_args):
        self.all_tasks = [wf for wf in WorkflowJob.objects.filter(**filter_args)]

    @timeit
    def _schedule(self):
        self.get_tasks(dict(status__in=["running"], dependencies_processed=True))
        if len(self.all_tasks) > 0:
            self.spawn_workflow_graph_jobs()


class DependencyManager(TaskBase):
    def __init__(self):
        super().__init__(prefix="dependency_manager")

    @timeit
    def _schedule(self):
        failing_job_qs = UnifiedJob.objects.filter(
            status='pending', dependencies_processed=False, dependent_jobs__status__in=['failed', 'error']
        ).prefetch_related('dependent_jobs')
        failed_job_ct = 0
        already_failed = set()
        for task in failing_job_qs.iterator():
            messages = []
            for dep in task.dependent_jobs.all():
                if dep.status in ('failed', 'error') or dep.id in already_failed:
                    messages.append(
                        'Previous Task Failed: {"job_type": "%s", "job_name": "%s", "job_id": "%s"}'
                        % (
                            get_type_for_model(type(dep)),
                            dep.name,
                            dep.id,
                        )
                    )
            # if we detect a failed or error dependency, go ahead and fail this
            # task. The errback on the dependency takes some time to trigger,
            # and we don't want the task to enter running state if its
            # dependency has failed or errored.
            task.status = 'failed'
            task.job_explanation = '\n'.join(messages)
            task.save(update_fields=['status', 'job_explanation'])
            task.websocket_emit_status('failed')
            failed_job_ct += 1
            already_failed.add(task.id)

        advancing_job_ct = (
            UnifiedJob.objects.filter(status='pending', dependencies_processed=False)
            .exclude(dependent_jobs__status__in=ACTIVE_STATES + ('failed', 'error', 'canceled'))
            .update(dependencies_processed=True)
        )
        if advancing_job_ct:
            logger.info(f'Dependencies fully processed for {advancing_job_ct} tasks')
            ScheduleTaskManager().schedule()

        self.subsystem_metrics.inc(f"{self.prefix}_pending_processed", advancing_job_ct + failed_job_ct)


class TaskManager(TaskBase):
    def __init__(self):
        """
        Do NOT put database queries or other potentially expensive operations
        in the task manager init. The task manager object is created every time a
        job is created, transitions state, and every 30 seconds on each tower node.
        More often then not, the object is destroyed quickly because the NOOP case is hit.

        The NOOP case is short-circuit logic. If the task manager realizes that another instance
        of the task manager is already running, then it short-circuits and decides not to run.
        """
        # start task limit indicates how many pending jobs can be started on this
        # .schedule() run. Starting jobs is expensive, and there is code in place to reap
        # the task manager after 5 minutes. At scale, the task manager can easily take more than
        # 5 minutes to start pending jobs. If this limit is reached, pending jobs
        # will no longer be started and will be started on the next task manager cycle.
        self.time_delta_job_explanation = timedelta(seconds=30)
        super().__init__(prefix="task_manager")

    def after_lock_init(self):
        """
        Init AFTER we know this instance of the task manager will run because the lock is acquired.
        """
        self.dependency_graph = DependencyGraph()
        self.instances = TaskManagerInstances(self.all_tasks)
        self.instance_groups = TaskManagerInstanceGroups(instances_by_hostname=self.instances)
        self.controlplane_ig = self.instance_groups.controlplane_ig

    @timeit
    def start_task(self, task, instance_group, instance=None):
        self.dependency_graph.add_job(task)
        self.subsystem_metrics.inc(f"{self.prefix}_tasks_started", 1)
        self.start_task_limit -= 1
        if self.start_task_limit == 0:
            # schedule another run immediately after this task manager
            ScheduleTaskManager().schedule()
        from awx.main.tasks.system import handle_work_finish

        # update capacity for control node and execution node
        if task.controller_node:
            self.instances[task.controller_node].consume_capacity(settings.AWX_CONTROL_NODE_TASK_IMPACT)
        if task.execution_node:
            self.instances[task.execution_node].consume_capacity(task.task_impact)

        task_actual = {
            'type': get_type_for_model(type(task)),
            'id': task.id,
        }

        task.status = 'waiting'

        (start_status, opts) = task.pre_start()
        if not start_status:
            task.status = 'failed'
            if task.job_explanation:
                task.job_explanation += ' '
            task.job_explanation += 'Task failed pre-start check.'
            task.save()
            # TODO: run error handler to fail sub-tasks and send notifications
        else:
            if type(task) is WorkflowJob:
                task.status = 'running'
                task.send_notification_templates('running')
                logger.debug('Transitioning %s to running status.', task.log_format)
                # Call this to ensure Workflow nodes get spawned in timely manner
                ScheduleWorkflowManager().schedule()
            # at this point we already have control/execution nodes selected for the following cases
            else:
                task.instance_group = instance_group
                execution_node_msg = f' and execution node {task.execution_node}' if task.execution_node else ''
                logger.debug(
                    f'Submitting job {task.log_format} controlled by {task.controller_node} to instance group {instance_group.name}{execution_node_msg}.'
                )
            with disable_activity_stream():
                task.celery_task_id = str(uuid.uuid4())
                task.save()
                task.log_lifecycle("waiting")

        # apply_async does a NOTIFY to the channel dispatcher is listening to
        # postgres will treat this as part of the transaction, which is what we want
        if task.status != 'failed' and type(task) is not WorkflowJob:
            task_cls = task._get_task_class()
            task_cls.apply_async(
                [task.pk],
                opts,
                queue=task.get_queue_name(),
                uuid=task.celery_task_id,
                callbacks=[{'task': handle_work_finish.name, 'kwargs': {'task_actual': task_actual}}],
                errbacks=[{'task': handle_work_finish.name, 'kwargs': {'task_actual': task_actual}}],
            )

        # In exception cases, like a job failing pre-start checks, we send the websocket status message
        # for jobs going into waiting, we omit this because of performance issues, as it should go to running quickly
        if task.status != 'waiting':
            task.websocket_emit_status(task.status)  # adds to on_commit

    @timeit
    def process_running_tasks(self, running_tasks):
        for task in running_tasks:
            if type(task) is WorkflowJob:
                ScheduleWorkflowManager().schedule()
            self.dependency_graph.add_job(task)

    @timeit
    def process_pending_tasks(self, pending_tasks):
        tasks_to_update_job_explanation = []
        for task in pending_tasks:
            if self.start_task_limit <= 0:
                break
            if self.timed_out():
                logger.warning("Task manager has reached time out while processing pending jobs, exiting loop early")
                break
            blocked_by = self.dependency_graph.task_blocked_by(task)
            if blocked_by:
                self.subsystem_metrics.inc(f"{self.prefix}_tasks_blocked", 1)
                task.log_lifecycle("blocked", blocked_by=blocked_by)
                job_explanation = gettext_noop(f"waiting for {blocked_by._meta.model_name}-{blocked_by.id} to finish")
                if task.job_explanation != job_explanation:
                    if task.created < (tz_now() - self.time_delta_job_explanation):
                        task.job_explanation = job_explanation
                        tasks_to_update_job_explanation.append(task)
                continue

            if isinstance(task, WorkflowJob):
                # Previously we were tracking allow_simultaneous blocking both here and in DependencyGraph.
                # Double check that using just the DependencyGraph works for Workflows and Sliced Jobs.
                self.start_task(task, None, None)
                continue

            found_acceptable_queue = False

            # Determine if there is control capacity for the task
            if task.capacity_type == 'control':
                control_impact = task.task_impact + settings.AWX_CONTROL_NODE_TASK_IMPACT
            else:
                control_impact = settings.AWX_CONTROL_NODE_TASK_IMPACT
            control_instance = self.instance_groups.fit_task_to_most_remaining_capacity_instance(
                task, instance_group_name=settings.DEFAULT_CONTROL_PLANE_QUEUE_NAME, impact=control_impact, capacity_type='control'
            )
            if not control_instance:
                self.task_needs_capacity(task, tasks_to_update_job_explanation)
                logger.debug(f"Skipping task {task.log_format} in pending, not enough capacity left on controlplane to control new tasks")
                continue

            task.controller_node = control_instance.hostname

            # All task.capacity_type == 'control' jobs should run on control plane, no need to loop over instance groups
            if task.capacity_type == 'control':
                task.execution_node = control_instance.hostname
                execution_instance = self.instances[control_instance.hostname].obj
                task.log_lifecycle("controller_node_chosen")
                task.log_lifecycle("execution_node_chosen")
                self.start_task(task, self.controlplane_ig, execution_instance)
                found_acceptable_queue = True
                continue

            for instance_group in self.instance_groups.get_instance_groups_from_task_cache(task):
                if instance_group.is_container_group:
                    self.start_task(task, instance_group, None)
                    found_acceptable_queue = True
                    break

                # at this point we know the instance group is NOT a container group
                # because if it was, it would have started the task and broke out of the loop.
                execution_instance = self.instance_groups.fit_task_to_most_remaining_capacity_instance(
                    task, instance_group_name=instance_group.name, add_hybrid_control_cost=True
                ) or self.instance_groups.find_largest_idle_instance(instance_group_name=instance_group.name, capacity_type=task.capacity_type)

                if execution_instance:
                    task.execution_node = execution_instance.hostname
                    # If our execution instance is a hybrid, prefer to do control tasks there as well.
                    if execution_instance.node_type == 'hybrid':
                        control_instance = execution_instance
                        task.controller_node = execution_instance.hostname

                    task.log_lifecycle("controller_node_chosen")
                    task.log_lifecycle("execution_node_chosen")
                    logger.debug(
                        "Starting {} in group {} instance {} (remaining_capacity={})".format(
                            task.log_format, instance_group.name, execution_instance.hostname, execution_instance.remaining_capacity
                        )
                    )
                    execution_instance = self.instances[execution_instance.hostname].obj
                    self.start_task(task, instance_group, execution_instance)
                    found_acceptable_queue = True
                    break
                else:
                    logger.debug(
                        "No instance available in group {} to run job {} w/ capacity requirement {}".format(
                            instance_group.name, task.log_format, task.task_impact
                        )
                    )
            if not found_acceptable_queue:
                self.task_needs_capacity(task, tasks_to_update_job_explanation)
        UnifiedJob.objects.bulk_update(tasks_to_update_job_explanation, ['job_explanation'])

    def task_needs_capacity(self, task, tasks_to_update_job_explanation):
        task.log_lifecycle("needs_capacity")
        job_explanation = gettext_noop("This job is not ready to start because there is not enough available capacity.")
        if task.job_explanation != job_explanation:
            if task.created < (tz_now() - self.time_delta_job_explanation):
                # Many launched jobs are immediately blocked, but most blocks will resolve in a few seconds.
                # Therefore we should only update the job_explanation after some time has elapsed to
                # prevent excessive task saves.
                task.job_explanation = job_explanation
                tasks_to_update_job_explanation.append(task)
        logger.debug("{} couldn't be scheduled on graph, waiting for next cycle".format(task.log_format))

    def reap_jobs_from_orphaned_instances(self):
        # discover jobs that are in running state but aren't on an execution node
        # that we know about; this is a fairly rare event, but it can occur if you,
        # for example, SQL backup an awx install with running jobs and restore it
        # elsewhere
        for j in UnifiedJob.objects.filter(
            status__in=['pending', 'waiting', 'running'],
        ).exclude(execution_node__in=Instance.objects.exclude(node_type='hop').values_list('hostname', flat=True)):
            if j.execution_node and not j.is_container_group_task:
                logger.error(f'{j.execution_node} is not a registered instance; reaping {j.log_format}')
                reap_job(j, 'failed')

    def process_tasks(self):
        running_tasks = [t for t in self.all_tasks if t.status in ['waiting', 'running']]
        self.process_running_tasks(running_tasks)
        self.subsystem_metrics.inc(f"{self.prefix}_running_processed", len(running_tasks))

        pending_tasks = [t for t in self.all_tasks if t.status == 'pending']

        self.process_pending_tasks(pending_tasks)
        self.subsystem_metrics.inc(f"{self.prefix}_pending_processed", len(pending_tasks))

    def timeout_approval_node(self, task):
        if self.timed_out():
            logger.warning("Task manager has reached time out while processing approval nodes, exiting loop early")
            # Do not process any more workflow approval nodes. Stop here.
            # Maybe we should schedule another TaskManager run
            return
        timeout_message = _("The approval node {name} ({pk}) has expired after {timeout} seconds.").format(name=task.name, pk=task.pk, timeout=task.timeout)
        logger.warning(timeout_message)
        task.timed_out = True
        task.status = 'failed'
        task.send_approval_notification('timed_out')
        task.websocket_emit_status(task.status)
        task.job_explanation = timeout_message
        task.save(update_fields=['status', 'job_explanation', 'timed_out'])

    def get_expired_workflow_approvals(self):
        # timeout of 0 indicates that it never expires
        qs = WorkflowApproval.objects.filter(status='pending').exclude(timeout=0).filter(expires__lt=tz_now())
        return qs

    @timeit
    def _schedule(self):
        self.get_tasks(dict(status__in=["pending", "waiting", "running"], dependencies_processed=True))

        self.after_lock_init()
        self.reap_jobs_from_orphaned_instances()

        if len(self.all_tasks) > 0:
            self.process_tasks()

        for workflow_approval in self.get_expired_workflow_approvals():
            self.timeout_approval_node(workflow_approval)
