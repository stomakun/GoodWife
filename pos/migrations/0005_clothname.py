# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-23 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_auto_20180123_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClothName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('pinyin', models.CharField(max_length=20)),
                ('used_count', models.IntegerField()),
                ('price', models.FloatField()),
            ],
        ),
    ]
