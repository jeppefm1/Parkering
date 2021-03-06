# Generated by Django 2.1.7 on 2019-03-19 12:35

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20190319_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plateNumber', models.CharField(blank=True, max_length=8, null=True, validators=[django.core.validators.RegexValidator(code='nomatch', message='Må ikke indeholde mellemrum.', regex='/\\S+/'), django.core.validators.RegexValidator(code='nomatch', message='Må ikke indeholde mellemrum.', regex='[N][o][n][e]')], verbose_name='Nummerplade')),
                ('userid', models.IntegerField(default=1)),
                ('state', models.IntegerField(default=0)),
                ('add_date', models.DateTimeField(default=datetime.datetime(2019, 3, 19, 13, 35, 8, 5274), verbose_name='dato tilføjet')),
            ],
        ),
        migrations.DeleteModel(
            name='AddPlate',
        ),
    ]
