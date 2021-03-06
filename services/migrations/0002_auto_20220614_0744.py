# Generated by Django 3.2.11 on 2022-06-14 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riderrequest',
            name='deriver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deriver_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='riderrequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
