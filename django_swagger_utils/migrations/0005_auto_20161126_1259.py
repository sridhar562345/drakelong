# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-26 12:59


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_swagger_utils', '0004_latency_duplicate_queries'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('app_name', models.CharField(max_length=100)),
                ('operation_id', models.CharField(max_length=500)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        )
    ]