from django.db import models
from datetime import datetime
from django.utils.timezone import utc
from django.core.validators import RegexValidator
import math

# Create your models here.
valid = [RegexValidator(regex='/\S+/', message='Må ikke indeholde mellemrum.', code='nomatch'),RegexValidator(regex='[N][o][n][e]', message='Må ikke indeholde mellemrum.', code='nomatch')]
class Contact(models.Model):
    mail = models.EmailField()
    user = models.CharField(max_length=150)
    subject = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    message = models.TextField()
    file = models.FileField()

class Plates(models.Model):
    plateNumber = models.CharField(max_length=8, verbose_name=u"Nummerplade", blank=True, null=True)
    userid = models.IntegerField(default=1)
    state = models.IntegerField(default=0)
    add_date = models.DateTimeField("dato tilføjet", default=datetime.now())

    def __str__(self):
        return self.plateNumber

class Log(models.Model):
    numberplate = models.CharField(max_length=8)
    entered = models.DateTimeField(default=datetime.now())
    exited = models.DateTimeField(default=datetime.now())
    entid = models.IntegerField(default=1)

    def get_time_diff(self):
        timediffSec = self.exited - self.entered
        timeDiff = timediffSec.total_seconds() / 3600 # Da det er per time, omregnes der fra sekunder til timer
        return math.ceil(timeDiff) # Da det er per påbegyndt time, skal der rundes op.

class ParkingEntity(models.Model):
    name = models.CharField(max_length=20,default="")
    available = models.IntegerField(default=500)
    address = models.CharField(max_length=30)
    hourlyRate = models.IntegerField(default=8)
