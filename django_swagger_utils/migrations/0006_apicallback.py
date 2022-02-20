# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 10:46


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_swagger_utils', '0005_auto_20161126_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='APICallback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('source', models.CharField(max_length=200)),
                ('app_name', models.CharField(max_length=100)),
                ('operation_id', models.CharField(max_length=500)),
                ('post_url', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
