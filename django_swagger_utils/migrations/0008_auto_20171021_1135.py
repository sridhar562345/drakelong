# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 11:35


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_swagger_utils', '0006_apicallback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lastaccess',
            name='operation_id',
            field=models.CharField(max_length=100)
        )
    ]
