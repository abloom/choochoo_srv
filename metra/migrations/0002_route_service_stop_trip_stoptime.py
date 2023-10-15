# Generated by Django 4.2.6 on 2023-10-14 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metra', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(max_length=12)),
                ('short_name', models.CharField(max_length=32)),
                ('long_name', models.CharField(max_length=128)),
                ('route_color', models.CharField(max_length=6)),
                ('text_color', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=32)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days_of_the_week', models.ManyToManyField(to='metra.dayoftheweek')),
            ],
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_id', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_id', models.CharField(max_length=64)),
                ('direction', models.CharField(choices=[('0', 'Outbound'), ('1', 'Inbound')], max_length=12)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metra.route')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metra.service')),
            ],
        ),
        migrations.CreateModel(
            name='StopTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_time', models.TimeField()),
                ('departure_time', models.TimeField()),
                ('stop_sequence', models.IntegerField()),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metra.stop')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metra.trip')),
            ],
            options={
                'ordering': ['stop_sequence'],
            },
        ),
    ]