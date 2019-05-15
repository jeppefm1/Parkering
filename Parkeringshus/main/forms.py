from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import Plates
from django.contrib.auth import authenticate, login

# Brugerformularen ændres, så også email er nødvendig
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # meta bruges til at sige hvad der skal inkluderes
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# Kontaktformular for anonyme brugere, hvor de skal udfylde email og navn
class ContactFormAnon(forms.Form):
    mail = forms.EmailField(label="Din mailadresse", required=True)
    name = forms.CharField(label="Din navn",required=True)
    subject = forms.CharField(label="Emne",required=True)
    message = forms.CharField(label="Besked", widget=forms.Textarea(attrs={'class' : 'materialize-textarea'}), required=True)
    file = forms.FileField(label="Eventuel fil", required=False)

# brugerkontakt kræver ikke navn og mail, da brugernavnet er givet
class ContactFormUser(forms.Form):
    subject = forms.CharField(label="Emne", required=True)
    message = forms.CharField(label="Besked", widget=forms.Textarea(attrs={'class' : 'materialize-textarea'}), required=True)
    file = forms.FileField(label="Eventuel fil", required=False)

# tilføjelse af nummerplade, hvor kun plateNumber skal udfyldes (resten sker automatisk)
class PlateForm(forms.ModelForm):
    class Meta:
        model = Plates
        fields = ['plateNumber']
