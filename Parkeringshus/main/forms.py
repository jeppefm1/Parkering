from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import Plates
from django.contrib.auth import authenticate, login

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class ContactFormAnon(forms.Form):
    mail = forms.EmailField(label="Din mailadresse", required=True)
    name = forms.CharField(label="Din navn",required=True)
    subject = forms.CharField(label="Emne",required=True)
    message = forms.CharField(label="Besked", widget=forms.Textarea(attrs={'class' : 'materialize-textarea'}), required=True)
    file = forms.FileField(label="Eventuel fil", required=False)

class ContactFormUser(forms.Form):
    subject = forms.CharField(label="Emne", required=True)
    message = forms.CharField(label="Besked", widget=forms.Textarea(attrs={'class' : 'materialize-textarea'}), required=True)
    file = forms.FileField(label="Eventuel fil", required=False)

class PlateForm(forms.ModelForm):
    class Meta:
        model = Plates
        fields = ['plateNumber']
