# Generated by Django 2.1.7 on 2019-03-12 13:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20190312_1356'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tutorial',
        ),
        migrations.AddField(
            model_name='addplate',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 12, 14, 28, 24, 85249), verbose_name='dato tilføjet'),
        ),
        migrations.AddField(
            model_name='addplate',
            name='state',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='addplate',
            name='userid',
            field=models.IntegerField(default=1),
        ),
    ]
