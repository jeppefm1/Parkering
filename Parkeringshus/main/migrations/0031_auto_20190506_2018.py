# Generated by Django 2.1.4 on 2019-05-06 18:18

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20190319_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='userid',
        ),
        migrations.AddField(
            model_name='parkingentity',
            name='coords',
            field=models.CharField(default='xd', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parkingentity',
            name='place',
            field=models.CharField(default='xd', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='log',
            name='entered',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 6, 20, 17, 35, 826527)),
        ),
        migrations.AlterField(
            model_name='log',
            name='exited',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 6, 20, 17, 35, 826527)),
        ),
        migrations.AlterField(
            model_name='plates',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 6, 20, 17, 35, 825531), verbose_name='dato tilføjet'),
        ),
        migrations.AlterField(
            model_name='plates',
            name='plateNumber',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='Nummerpladen skal være af formen AT27362 og må ikke indeholde små bogstaver.', regex='^[A-Z]{2}[0-9]{5}')], verbose_name='Nummerplade'),
        ),
    ]
