# Generated by Django 2.2.6 on 2019-10-16 22:07

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ChargerDriveProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drive_profile', models.CharField(max_length=20)),
                ('test', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=1000)),
                ('x_name', models.CharField(max_length=20)),
                ('y_name', models.CharField(max_length=20)),
                ('z_name', models.CharField(max_length=20)),
                ('x_active', models.BooleanField(default=True)),
                ('y_active', models.BooleanField(default=False)),
                ('z_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode_active', models.BooleanField(default=True)),
                ('start_cycle_active', models.BooleanField(default=True)),
                ('voltage_active', models.BooleanField(default=True)),
                ('voltage_name', models.CharField(default='upper_cutoff_voltage', max_length=20)),
                ('temperature_active', models.BooleanField(default=True)),
                ('temperature_name', models.CharField(default='temperature', max_length=20)),
                ('drive_profile_active', models.BooleanField(default=False)),
                ('AC_active', models.BooleanField(default=False)),
                ('AC_increment_active', models.BooleanField(default=False)),
                ('charger_active', models.BooleanField(default=False)),
                ('version_number_active', models.BooleanField(default=False)),
                ('charger', models.CharField(default='', max_length=5)),
                ('shorthand', models.CharField(default='', max_length=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FileNameHelper.Category')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ValidMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charID', models.CharField(max_length=5, null=True)),
                ('barcode', models.IntegerField(null=True)),
                ('start_cycle', models.IntegerField(null=True)),
                ('voltage', models.FloatField(null=True)),
                ('temperature', models.IntegerField(null=True)),
                ('AC', models.CharField(choices=[('A', 'Anode'), ('C', 'Cathode')], max_length=1, null=True)),
                ('AC_increment', models.IntegerField(null=True)),
                ('version_number', models.IntegerField(null=True)),
                ('drive_profile_x_numerator', models.IntegerField(null=True)),
                ('drive_profile_x_denominator', models.IntegerField(null=True)),
                ('drive_profile_y_numerator', models.IntegerField(null=True)),
                ('drive_profile_y_denominator', models.IntegerField(null=True)),
                ('drive_profile_z', models.FloatField(null=True)),
                ('date', models.DateField(null=True)),
                ('drive_profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FileNameHelper.ChargerDriveProfile')),
                ('experiment_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='FileNameHelper.ExperimentType')),
            ],
        ),
        migrations.AddField(
            model_name='experimenttype',
            name='subcategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FileNameHelper.SubCategory'),
        ),
        migrations.CreateModel(
            name='DatabaseFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=200)),
                ('root', models.CharField(max_length=200)),
                ('last_modified', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('filesize', models.IntegerField(default=0)),
                ('is_valid', models.BooleanField(default=False)),
                ('deprecated', models.BooleanField(default=False)),
                ('valid_metadata', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FileNameHelper.ValidMetadata')),
            ],
        ),
    ]
