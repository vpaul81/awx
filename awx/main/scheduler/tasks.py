# Python
import logging

# Django
from django.conf import settings

# AWX
from awx import MODE
from awx.main.scheduler import TaskManager, DependencyManager, WorkflowManager
from awx.main.dispatch.publish import task

logger = logging.getLogger('awx.main.scheduler')


def run_manager(manager, prefix):
    if MODE == 'development' and settings.AWX_DISABLE_TASK_MANAGERS:
        logger.debug(f"Not running {prefix} manager, AWX_DISABLE_TASK_MANAGERS is True. Trigger with GET to /api/debug/{prefix}_manager/")
        return
    manager().schedule()


@task(queue="tower_broadcast_all")
def task_manager():
    run_manager(TaskManager, "task")


@task(queue="tower_broadcast_all")
def dependency_manager():
    run_manager(DependencyManager, "dependency")


@task(queue="tower_broadcast_all")
def workflow_manager():
    run_manager(WorkflowManager, "workflow")
