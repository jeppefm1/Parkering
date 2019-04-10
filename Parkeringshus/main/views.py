### Views er det som koder al Django/Python koden (altså modeller og formularer) ###
# sammen med HTML-koden. Det er nødvendigt, da views skaber sammenhæng og giver
# HTML en kontekst, som gør det muligt at bruge Django-funktioner på siderne.
###                                                                              ###


# Henvisninger til sider
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
# De modeller og formularer som bliver brugt
from .models import Contact, Plates, Log, ParkingEntity
from django.contrib.auth.forms import AuthenticationForm
from .forms import NewUserForm, PlateForm, ContactFormAnon, ContactFormUser
from django.contrib.auth import login, logout, authenticate
from django.views.generic.edit import DeleteView
# Til at vise beskeder, f.eks. når man logger ind
from django.contrib import messages
# Datetime til at holde øje med tiden
from datetime import datetime
# Skal kunne sende mails
from django.core.mail import send_mail, BadHeaderError

# Startsiden skal vide om brugeren er logget ind. Hvis det er sandt, så skal
# den vide
def homepage(request):
    current_user = request.user
    uid = current_user.id
    if current_user.is_authenticated:
        return render(request=request,
                      template_name="main/home.html",
                      context={"plates":Plates.objects.filter(userid=uid),
                      "logs":Log.objects.filter(numberplate__in=Plates.objects.filter(userid=uid).values('plateNumber')),
                      "now":datetime.now,"uid":uid,"parkplace":ParkingEntity.objects.all})
    else: return render(request=request,template_name="main/home.html")
def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Kontoen {username} er nu blevet oprettet.")
            login(request, user)
            messages.info(request, f"Du er nu logget ind med {username}.")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            return render(request = request,
                          template_name = "main/register.html",
                          context={"form":form})
    form = NewUserForm
    return render(request,
                  "main/register.html",
                  context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Du er nu logget ud.")
    return redirect("main:homepage")

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Du er nu logget på som {username}")
                return redirect('main:homepage')
            else:
                messages.error(request, "Brugernavn og adgangskode passer ikke.")
        else:
            messages.error(request, "Brugernavn og adgangskode passer ikke.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "main/login.html",
                    context={"form":form})

def support(request):
    current_user = request.user
    if request.method == 'GET':
        if current_user.is_authenticated:
            form = ContactFormUser
        else:
            form = ContactFormAnon()
    else:
        if current_user.is_authenticated:
            form = ContactFormUser(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                input = "Fra: {}\nEmne: {}\nBesked:\n{}\nSendt {}".format(current_user.id,subject,message,datetime.now())
                try:
                    send_mail("Ny besked: " + subject, input, str(current_user.id)+"@parkering.tk", ['parkeringtk@gmail.com'])
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
        else:
            form = ContactFormAnon(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                name = form.cleaned_data['name']
                from_mail = form.cleaned_data['mail']
                input = "Fra mail: {}\nNavn: {}\nEmne: {}\nBesked:\n{}\nSendt {}".format(from_mail,name,subject,message,datetime.now())
                try:
                    send_mail(subject, input, from_mail, ['parkeringtk@gmail.com'])
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')

        return redirect('/support')
        messages.success(request, f"Din besked er blevet sendt.")
    return render(request, "main/support.html", {'form': form})


def addplate(request):
    current_user = request.user
    form = PlateForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            plateNumber = form.cleaned_data.get('plateNumber')
            newPlate = Plates(plateNumber=plateNumber, userid=current_user.id, state=1, add_date=datetime.now())
            newPlate.save()
            messages.info(request, f"Nummerpladen {plateNumber} afventer nu godkendelse.")
            return redirect('main:addplate')
        else:
            messages.error(request, f"Der var noget galt med den indtastede nummerplade, prøv igen.")

    return render(request = request,
                  template_name = "main/addplate.html",
                  context={"form":form,"plates":Plates.objects.all,"uid":current_user.id})

class deleteplate(DeleteView):
    model = Plates
    success_url = reverse_lazy('main:addplate')
