# Generated by Django 3.2.13 on 2022-07-14 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0164_remove_inventorysource_update_on_project_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='signature_validation',
            field=models.BooleanField(default=False, help_text='TODO'),
        ),
        migrations.AddField(
            model_name='project',
            name='signature_validation_credential',
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='projects_signature_validation',
                to='main.credential',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='signature_validation_result',
            field=models.BooleanField(default=False, help_text='TODO'),
        ),
    ]
