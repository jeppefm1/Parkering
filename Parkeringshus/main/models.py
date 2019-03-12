from django.db import models
from datetime import datetime
from django.core.validators import RegexValidator

# Create your models here.

class Contact(models.Model):
    mail = models.EmailField()
    user = models.CharField(max_length=150)
    subject = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    message = models.TextField()
    file = models.FileField()

class AddPlate(models.Model):
    plateNumber = models.CharField(max_length=8, validators=[RegexValidator(regex='/\S+/', message='Må ikke indeholde mellemrum.', code='nomatch'),RegexValidator(regex='[N][o][n][e]', message='Må ikke indeholde mellemrum.', code='nomatch')], verbose_name=u"Nummerplade", blank=True, null=True)
    userid = models.IntegerField(default=1)
    state = models.IntegerField(default=0)
    add_date = models.DateTimeField("dato tilføjet", default=datetime.now())

    def __str__(self):
        return self.plateNumber
