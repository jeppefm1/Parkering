# Generated by Django 2.1.7 on 2019-03-19 13:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20190319_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='entered',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 44, 16, 114856)),
        ),
        migrations.AlterField(
            model_name='log',
            name='exited',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 44, 16, 114856)),
        ),
        migrations.AlterField(
            model_name='plates',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 44, 16, 114856), verbose_name='dato tilføjet'),
        ),
    ]
