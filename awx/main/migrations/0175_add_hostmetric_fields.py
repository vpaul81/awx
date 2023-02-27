# Generated by Django 3.2.16 on 2023-02-03 09:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0174_ensure_org_ee_admin_roles'),
    ]

    operations = [
        migrations.AlterField(model_name='hostmetric', name='hostname', field=models.CharField(max_length=512, primary_key=False, serialize=True, unique=True)),
        migrations.AddField(
            model_name='hostmetric',
            name='last_deleted',
            field=models.DateTimeField(db_index=True, null=True, help_text='When the host was last deleted'),
        ),
        migrations.AddField(
            model_name='hostmetric',
            name='automated_counter',
            field=models.BigIntegerField(default=0, help_text='How many times was the host automated'),
        ),
        migrations.AddField(
            model_name='hostmetric',
            name='deleted_counter',
            field=models.IntegerField(default=0, help_text='How many times was the host deleted'),
        ),
        migrations.AddField(
            model_name='hostmetric',
            name='deleted',
            field=models.BooleanField(
                default=False, help_text='Boolean flag saying whether the host is deleted and therefore not counted into the subscription consumption'
            ),
        ),
        migrations.AddField(
            model_name='hostmetric',
            name='used_in_inventories',
            field=models.IntegerField(null=True, help_text='How many inventories contain this host'),
        ),
        migrations.AddField(
            model_name='hostmetric', name='id', field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
        ),
    ]
