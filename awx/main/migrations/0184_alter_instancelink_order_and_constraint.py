# Generated by Django 3.2.16 on 2023-04-26 11:50

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0183_instance_peers_from_control_nodes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instancelink',
            options={'ordering': ('id',)},
        ),
        migrations.AddConstraint(
            model_name='instancelink',
            constraint=models.CheckConstraint(
                check=models.Q(('source', django.db.models.expressions.F('target')), _negated=True), name='source_and_target_can_not_be_equal'
            ),
        ),
    ]
