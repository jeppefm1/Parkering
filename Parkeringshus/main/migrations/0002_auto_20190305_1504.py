# Generated by Django 2.1.7 on 2019-03-05 14:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='published',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 5, 15, 4, 48, 286271), verbose_name='dato'),
        ),
    ]
