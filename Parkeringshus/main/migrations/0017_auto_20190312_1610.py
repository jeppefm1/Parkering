# Generated by Django 2.1.7 on 2019-03-12 15:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20190312_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addplate',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 12, 16, 10, 8, 889633), verbose_name='dato tilføjet'),
        ),
        migrations.AlterField(
            model_name='addplate',
            name='plateNumber',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Nummerplade'),
        ),
    ]
