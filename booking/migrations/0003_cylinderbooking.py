# Generated by Django 5.1.6 on 2025-02-14 08:23

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_connectionrequest_rejection_reason_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CylinderBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cylinder_type', models.CharField(choices=[('LPG', 'LPG'), ('Commercial', 'Commercial')], max_length=50)),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cylinder_bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
