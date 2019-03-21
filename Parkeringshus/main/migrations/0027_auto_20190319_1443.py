# Generated by Django 2.1.7 on 2019-03-19 13:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20190319_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=30)),
                ('hourlyRate', models.IntegerField(default=8)),
            ],
        ),
        migrations.AddField(
            model_name='log',
            name='entid',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='log',
            name='entered',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 43, 7, 506398)),
        ),
        migrations.AlterField(
            model_name='log',
            name='exited',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 43, 7, 506398)),
        ),
        migrations.AlterField(
            model_name='plates',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 19, 14, 43, 7, 506398), verbose_name='dato tilføjet'),
        ),
    ]
