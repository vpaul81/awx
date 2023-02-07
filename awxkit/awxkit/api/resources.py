class Resources(object):
    _activity = r'activity_stream/\d+/'
    _activity_stream = 'activity_stream/'
    _ad_hoc_command = r'ad_hoc_commands/\d+/'
    _ad_hoc_command_relaunch = r'ad_hoc_commands/\d+/relaunch/'
    _ad_hoc_commands = 'ad_hoc_commands/'
    _ad_hoc_event = r'ad_hoc_command_events/\d+/'
    _ad_hoc_events = r'ad_hoc_commands/\d+/events/'
    _ad_hoc_related_cancel = r'ad_hoc_commands/\d+/cancel/'
    _ad_hoc_relaunch = r'ad_hoc_commands/\d+/relaunch/'
    _ansible_facts = r'hosts/\d+/ansible_facts/'
    _application = r'applications/\d+/'
    _applications = 'applications/'
    _auth = 'auth/'
    _authtoken = 'authtoken/'
    _bulk = 'bulk/'
    _bulk_job_launch = 'bulk/job_launch/'
    _bulk_host_create = 'bulk/host_create/'
    _config = 'config/'
    _config_attach = 'config/attach/'
    _credential = r'credentials/\d+/'
    _credential_access_list = r'credentials/\d+/access_list/'
    _credential_copy = r'credentials/\d+/copy/'
    _credential_input_source = r'credential_input_sources/\d+/'
    _credential_input_sources = 'credential_input_sources/'
    _credential_owner_teams = r'credentials/\d+/owner_teams/'
    _credential_owner_users = r'credentials/\d+/owner_users/'
    _credential_type = r'credential_types/\d+/'
    _credential_types = 'credential_types/'
    _credentials = 'credentials/'
    _dashboard = 'dashboard/'
    _execution_environment = r'execution_environments/\d+/'
    _execution_environments = 'execution_environments/'
    _fact_view = r'hosts/\d+/fact_view/'
    _group = r'groups/\d+/'
    _group_access_list = r'groups/\d+/access_list/'
    _group_children = r'groups/\d+/children/'
    _group_potential_children = r'groups/\d+/potential_children/'
    _group_related_ad_hoc_commands = r'groups/\d+/ad_hoc_commands/'
    _group_related_all_hosts = r'groups/\d+/all_hosts/'
    _group_related_hosts = r'groups/\d+/hosts/'
    _group_related_job_events = r'groups/\d+/job_events/'
    _group_related_job_host_summaries = r'groups/\d+/job_host_summaries/'
    _group_variable_data = r'groups/\d+/variable_data/'
    _groups = 'groups/'
    _host = r'hosts/\d+/'
    _host_groups = r'hosts/\d+/groups/'
    _host_insights = r'hosts/\d+/insights/'
    _host_related_ad_hoc_commands = r'hosts/\d+/ad_hoc_commands/'
    _host_related_fact_version = r'hosts/\d+/fact_versions/\d+/'
    _host_related_fact_versions = r'hosts/\d+/fact_versions/'
    _host_variable_data = r'hosts/\d+/variable_data/'
    _hosts = 'hosts/'
    _instance = r'instances/\d+/'
    _instance_group = r'instance_groups/\d+/'
    _instance_group_related_jobs = r'instance_groups/\d+/jobs/'
    _instance_groups = 'instance_groups/'
    _instance_install_bundle = r'instances/\d+/install_bundle/'
    _instance_peers = r'instances/\d+/peers/'
    _instance_related_jobs = r'instances/\d+/jobs/'
    _instances = 'instances/'
    _inventories = 'inventories/'
    _inventory = r'inventories/\d+/'
    _inventory_access_list = r'inventories/\d+/access_list/'
    _inventory_copy = r'inventories/\d+/copy/'
    _inventory_labels = r'inventories/\d+/labels/'
    _inventory_related_ad_hoc_commands = r'inventories/\d+/ad_hoc_commands/'
    _inventory_related_groups = r'inventories/\d+/groups/'
    _inventory_related_hosts = r'inventories/\d+/hosts/'
    _inventory_related_root_groups = r'inventories/\d+/root_groups/'
    _inventory_related_script = r'inventories/\d+/script/'
    _inventory_related_update_inventory_sources = r'inventories/\d+/update_inventory_sources/'
    _inventory_source = r'inventory_sources/\d+/'
    _inventory_source_schedule = r'inventory_sources/\d+/schedules/\d+/'
    _inventory_source_schedules = r'inventory_sources/\d+/schedules/'
    _inventory_source_updates = r'inventory_sources/\d+/inventory_updates/'
    _inventory_sources = 'inventory_sources/'
    _inventory_sources_related_groups = r'inventory_sources/\d+/groups/'
    _inventory_sources_related_hosts = r'inventory_sources/\d+/hosts/'
    _inventory_sources_related_update = r'inventory_sources/\d+/update/'
    _inventory_tree = r'inventories/\d+/tree/'
    _inventory_update = r'inventory_updates/\d+/'
    _inventory_update_cancel = r'inventory_updates/\d+/cancel/'
    _inventory_update_events = r'inventory_updates/\d+/events/'
    _inventory_updates = 'inventory_updates/'
    _inventory_variable_data = r'inventories/\d+/variable_data/'
    _workflow_approval = r'workflow_approvals/\d+/'
    _workflow_approvals = 'workflow_approvals/'
    _workflow_approval_template = r'workflow_approval_templates/\d+/'
    _workflow_approval_templates = 'workflow_approval_templates/'
    _workflow_job_template_node_create_approval_template = r'workflow_job_template_nodes/\d+/create_approval_template/'
    _job = r'jobs/\d+/'
    _job_cancel = r'jobs/\d+/cancel/'
    _job_create_schedule = r'jobs/\d+/create_schedule/'
    _job_event = r'job_events/\d+/'
    _job_event_children = r'job_events/\d+/children/'
    _job_events = 'job_events/'
    _job_host_summaries = r'jobs/\d+/job_host_summaries/'
    _job_host_summary = r'job_host_summaries/\d+/'
    _job_job_event = r'jobs/\d+/job_events/\d+/'
    _job_job_events = r'jobs/\d+/job_events/'
    _job_labels = r'jobs/\d+/labels/'
    _job_notifications = r'jobs/\d+/notifications/'
    _job_play = r'jobs/\d+/job_plays/\d+/'
    _job_plays = r'jobs/\d+/job_plays/'
    _job_relaunch = r'jobs/\d+/relaunch/'
    _job_start = r'jobs/\d+/start/'
    _job_task = r'jobs/\d+/job_tasks/\d+/'
    _job_tasks = r'jobs/\d+/job_tasks/'
    _job_template = r'job_templates/\d+/'
    _job_template_access_list = r'job_templates/\d+/access_list/'
    _job_template_callback = r'job_templates/\d+/callback/'
    _job_template_copy = r'job_templates/\d+/copy/'
    _job_template_jobs = r'job_templates/\d+/jobs/'
    _job_template_labels = r'job_templates/\d+/labels/'
    _job_template_launch = r'job_templates/\d+/launch/'
    _job_template_schedule = r'job_templates/\d+/schedules/\d+/'
    _job_template_schedules = r'job_templates/\d+/schedules/'
    _job_template_slice_workflow_jobs = r'job_templates/\d+/slice_workflow_jobs/'
    _job_template_survey_spec = r'job_templates/\d+/survey_spec/'
    _job_templates = 'job_templates/'
    _jobs = 'jobs/'
    _label = r'labels/\d+/'
    _labels = 'labels/'
    _me = 'me/'
    _metrics = 'metrics/'
    _mesh_visualizer = 'mesh_visualizer/'
    _notification = r'notifications/\d+/'
    _notification_template = r'notification_templates/\d+/'
    _notification_template_any = r'\w+/\d+/notification_templates_any/\d+/'
    _notification_template_started = r'\w+/\d+/notification_templates_started/\d+/'
    _notification_template_copy = r'notification_templates/\d+/copy/'
    _notification_template_error = r'\w+/\d+/notification_templates_error/\d+/'
    _notification_template_success = r'\w+/\d+/notification_templates_success/\d+/'
    _notification_template_approval = r'\w+/\d+/notification_templates_approvals/\d+/'
    _notification_template_test = r'notification_templates/\d+/test/'
    _notification_templates = 'notification_templates/'
    _notification_templates_any = r'\w+/\d+/notification_templates_any/'
    _notification_templates_started = r'\w+/\d+/notification_templates_started/'
    _notification_templates_error = r'\w+/\d+/notification_templates_error/'
    _notification_templates_success = r'\w+/\d+/notification_templates_success/'
    _notification_templates_approvals = r'\w+/\d+/notification_templates_approvals/'
    _notifications = 'notifications/'
    _object_activity_stream = r'[^/]+/\d+/activity_stream/'
    _org_projects = r'organizations/\d+/projects/'
    _org_teams = r'organizations/\d+/teams/'
    _organization = r'organizations/\d+/'
    _organization_access_list = r'organizations/\d+/access_list/'
    _organization_admins = r'organizations/\d+/admins/'
    _organization_applications = r'organizations/\d+/applications/'
    _organization_execution_environments = r'organizations/\d+/execution_environments/'
    _organization_galaxy_credentials = r'organizations/\d+/galaxy_credentials/'
    _organization_inventories = r'organizations/\d+/inventories/'
    _organization_users = r'organizations/\d+/users/'
    _organizations = 'organizations/'
    _ping = 'ping/'
    _project = r'projects/\d+/'
    _project_access_list = r'projects/\d+/access_list/'
    _project_copy = r'projects/\d+/copy/'
    _project_inventories = r'projects/\d+/inventories/'
    _project_organizations = r'projects/\d+/organizations/'
    _project_playbooks = r'projects/\d+/playbooks/'
    _project_project_updates = r'projects/\d+/project_updates/'
    _project_related_update = r'projects/\d+/update/'
    _project_schedule = r'projects/\d+/schedules/\d+/'
    _project_schedules = r'projects/\d+/schedules/'
    _project_scm_inventory_sources = r'projects/\d+/scm_inventory_sources/'
    _project_teams = r'projects/\d+/teams/'
    _project_update = r'project_updates/\d+/'
    _project_update_cancel = r'project_updates/\d+/cancel/'
    _project_update_events = r'project_updates/\d+/events/'
    _project_update_scm_inventory_updates = r'project_updates/\d+/scm_inventory_updates/'
    _project_updates = 'project_updates/'
    _projects = 'projects/'
    _related_credentials = r'\w+/\d+/credentials/'
    _related_input_sources = r'\w+/\d+/input_sources/'
    _related_instance_groups = r'\w+/\d+/instance_groups/'
    _related_instances = r'\w+/\d+/instances/'
    _related_inventories = r'(?!projects)\w+/\d+/inventories/'  # project related inventories are inventory files (.ini)
    _related_inventory_sources = r'\w+/\d+/inventory_sources/'
    _related_job_templates = r'\w+/\d+/job_templates/'
    _related_notification_templates = r'\w+/\d+/notification_templates/'
    _related_notifications = r'\w+/\d+/notifications/'
    _related_object_roles = r'\w+/\d+/object_roles/'
    _related_projects = r'\w+/\d+/projects/'
    _related_roles = r'\w+/\d+/roles/'
    _related_schedule = r'\w+/\d+/schedules/\d+/'
    _related_schedules = r'\w+/\d+/schedules/'
    _related_stdout = r'\w+/\d+/stdout/'
    _related_teams = r'\w+/\d+/teams/'
    _related_users = r'\w+/\d+/users/'
    _related_workflow_job_templates = r'\w+/\d+/workflow_job_templates/'
    _role = r'roles/\d+/'
    _roles = 'roles/'
    _roles_related_teams = r'roles/\d+/teams/'
    _schedule = r'schedules/\d+/'
    _schedules = 'schedules/'
    _schedules_jobs = r'schedules/\d+/jobs/'
    _schedules_preview = 'schedules/preview/'
    _schedules_zoneinfo = 'schedules/zoneinfo/'
    _setting = r'settings/\w+/'
    _settings = 'settings/'
    _settings_all = 'settings/all/'
    _settings_authentication = 'settings/authentication/'
    _settings_azuread_oauth2 = 'settings/azuread-oauth2/'
    _settings_changed = 'settings/changed/'
    _settings_github = 'settings/github/'
    _settings_github_org = 'settings/github-org/'
    _settings_github_team = 'settings/github-team/'
    _settings_google_oauth2 = 'settings/google-oauth2/'
    _settings_jobs = 'settings/jobs/'
    _settings_ldap = 'settings/ldap/'
    _settings_logging = 'settings/logging/'
    _settings_named_url = 'settings/named-url/'
    _settings_radius = 'settings/radius/'
    _settings_saml = 'settings/saml/'
    _settings_system = 'settings/system/'
    _settings_tacacsplus = 'settings/tacacsplus/'
    _settings_ui = 'settings/ui/'
    _settings_user = 'settings/user/'
    _settings_user_defaults = 'settings/user-defaults/'
    _system_job = r'system_jobs/\d+/'
    _system_job_cancel = r'system_jobs/\d+/cancel/'
    _system_job_events = r'system_jobs/\d+/events/'
    _system_job_template = r'system_job_templates/\d+/'
    _system_job_template_jobs = r'system_job_templates/\d+/jobs/'
    _system_job_template_launch = r'system_job_templates/\d+/launch/'
    _system_job_template_schedule = r'system_job_templates/\d+/schedules/\d+/'
    _system_job_template_schedules = r'system_job_templates/\d+/schedules/'
    _system_job_templates = 'system_job_templates/'
    _system_jobs = 'system_jobs/'
    _team = r'teams/\d+/'
    _team_access_list = r'teams/\d+/access_list/'
    _team_credentials = r'teams/\d+/credentials/'
    _team_permission = r'teams/\d+/permissions/\d+/'
    _team_permissions = r'teams/\d+/permissions/'
    _team_users = r'teams/\d+/users/'
    _teams = 'teams/'
    _token = r'tokens/\d+/'
    _tokens = 'tokens/'
    _unified_job_template = r'unified_job_templates/\d+/'
    _unified_job_templates = 'unified_job_templates/'
    _unified_jobs = 'unified_jobs/'
    _user = r'users/\d+/'
    _user_access_list = r'users/\d+/access_list/'
    _user_admin_organizations = r'users/\d+/admin_of_organizations/'
    _user_credentials = r'users/\d+/credentials/'
    _user_organizations = r'users/\d+/organizations/'
    _user_permission = r'users/\d+/permissions/\d+/'
    _user_permissions = r'users/\d+/permissions/'
    _user_teams = r'users/\d+/teams/'
    _users = 'users/'
    _variable_data = r'.*\/variable_data/'
    _workflow_job = r'workflow_jobs/\d+/'
    _workflow_job_cancel = r'workflow_jobs/\d+/cancel/'
    _workflow_job_labels = r'workflow_jobs/\d+/labels/'
    _workflow_job_node = r'workflow_job_nodes/\d+/'
    _workflow_job_node_always_nodes = r'workflow_job_nodes/\d+/always_nodes/'
    _workflow_job_node_failure_nodes = r'workflow_job_nodes/\d+/failure_nodes/'
    _workflow_job_node_success_nodes = r'workflow_job_nodes/\d+/success_nodes/'
    _workflow_job_nodes = 'workflow_job_nodes/'
    _workflow_job_relaunch = r'workflow_jobs/\d+/relaunch/'
    _workflow_job_template = r'workflow_job_templates/\d+/'
    _workflow_job_template_copy = r'workflow_job_templates/\d+/copy/'
    _workflow_job_template_jobs = r'workflow_job_templates/\d+/workflow_jobs/'
    _workflow_job_template_labels = r'workflow_job_templates/\d+/labels/'
    _workflow_job_template_launch = r'workflow_job_templates/\d+/launch/'
    _workflow_job_template_node = r'workflow_job_template_nodes/\d+/'
    _workflow_job_template_node_always_nodes = r'workflow_job_template_nodes/\d+/always_nodes/'
    _workflow_job_template_node_failure_nodes = r'workflow_job_template_nodes/\d+/failure_nodes/'
    _workflow_job_template_node_success_nodes = r'workflow_job_template_nodes/\d+/success_nodes/'
    _workflow_job_template_nodes = 'workflow_job_template_nodes/'
    _workflow_job_template_schedule = r'workflow_job_templates/\d+/schedules/\d+/'
    _workflow_job_template_schedules = r'workflow_job_templates/\d+/schedules/'
    _workflow_job_template_survey_spec = r'workflow_job_templates/\d+/survey_spec/'
    _workflow_job_template_workflow_nodes = r'workflow_job_templates/\d+/workflow_nodes/'
    _workflow_job_templates = 'workflow_job_templates/'
    _workflow_job_workflow_nodes = r'workflow_jobs/\d+/workflow_nodes/'
    _subscriptions = 'config/subscriptions/'
    _workflow_jobs = 'workflow_jobs/'
    api = '/api/'
    common = api + r'v\d+/'
    v2 = api + 'v2/'

    def __getattr__(self, resource):
        if resource[:3] == '___':
            raise AttributeError('No existing resource: {}'.format(resource))
        # Currently we don't handle anything under:
        # /api/o/
        # /api/login/
        # /api/logout/
        # If/when we do we will probably need to modify this __getattr__ method
        # Also, if we add another API version, this would be handled here
        prefix = 'v2'
        resource = '_' + resource
        return '{0}{1}'.format(getattr(self, prefix), getattr(self, resource))


resources = Resources()
