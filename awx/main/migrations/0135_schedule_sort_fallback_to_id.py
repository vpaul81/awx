# Generated by Django 2.2.16 on 2021-03-29 15:30

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0134_unifiedjob_ansible_version'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='schedule',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('next_run'), descending=True, nulls_last=True), 'id']},
        ),
    ]
