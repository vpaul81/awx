# Generated by Django 4.2.5 on 2023-10-10 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0187_hop_nodes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceptorAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('port', models.IntegerField()),
                ('protocol', models.CharField(max_length=10)),
                ('websocket_path', models.CharField(blank=True, default='', max_length=255)),
                ('is_internal', models.BooleanField(default=False)),
                ('peers_from_control_nodes', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='instancelink',
            name='source_and_target_can_not_be_equal',
        ),
        migrations.AlterUniqueTogether(
            name='instancelink',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='instancelink',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.instance'),
        ),
        migrations.AddField(
            model_name='receptoraddress',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receptor_addresses', to='main.instance'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='peers',
            field=models.ManyToManyField(related_name='peers_from', through='main.InstanceLink', to='main.receptoraddress'),
        ),
        migrations.AlterField(
            model_name='instancelink',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.receptoraddress'),
        ),
        migrations.AddConstraint(
            model_name='receptoraddress',
            constraint=models.UniqueConstraint(
                fields=('address', 'protocol'), name='unique_receptor_address', violation_error_message='Receptor address + protocol must be unique.'
            ),
        ),
    ]
