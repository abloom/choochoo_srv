# Generated by Django 4.2.6 on 2023-10-15 03:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metra', '0002_route_service_stop_trip_stoptime'),
    ]

    operations = [
        migrations.CreateModel(
            name='RouteToDisplay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(max_length=12)),
            ],
        ),
        migrations.AlterField(
            model_name='service',
            name='service_id',
            field=models.CharField(max_length=32, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='stoptime',
            unique_together={('trip', 'stop')},
        ),
        migrations.CreateModel(
            name='StopToDisplay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_id', models.CharField(max_length=64)),
                ('route_to_display', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stops_to_display', to='metra.routetodisplay')),
            ],
        ),
    ]
