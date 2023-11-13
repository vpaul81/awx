# Generated by Django 4.2.6 on 2023-11-21 02:06

from django.db import migrations
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.management import create_contenttypes

from awx.main.migrations._new_rbac import migrate_to_new_rbac

from ansible_base.rbac.migrations._managed_definitions import setup_managed_role_definitions


def create_contenttypes_as_operation(apps, schema_editor):
    from django.apps.registry import apps as global_apps

    create_contenttypes(global_apps.get_app_config('main'))


def create_permissions_as_operation(apps, schema_editor):
    from django.apps.registry import apps as global_apps

    create_permissions(global_apps.get_app_config('main'))


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0190_profile_is_system_auditor'),
        ('dab_rbac', '__first__'),
    ]

    operations = [
        # make sure permissions and content types have been created by now
        # these normally run in a post_migrate signal but we need them for our logic
        migrations.RunPython(create_contenttypes_as_operation, migrations.RunPython.noop),
        migrations.RunPython(create_permissions_as_operation, migrations.RunPython.noop),
        migrations.RunPython(setup_managed_role_definitions, migrations.RunPython.noop),
        migrations.RunPython(migrate_to_new_rbac, migrations.RunPython.noop),
    ]
