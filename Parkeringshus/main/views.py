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
from .forms import NewUserForm, PlateForm
from django.contrib.auth import login, logout, authenticate
from django.views.generic.edit import DeleteView
# Til at vise beskeder, f.eks. når man logger ind
from django.contrib import messages
# Datetime til at holde øje med tiden
from datetime import datetime

#Til at sende emails
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
#Henter mailadresse fra instillingerne
from django.conf import settings

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

#Funktion til at sende html emails
def send_html_email(to_list, subject, template_name, context, sender=settings.DEFAULT_FROM_EMAIL):
    msg_html = render_to_string(template_name, context)
    msg = EmailMessage(subject=subject, body=msg_html, from_email=sender, bcc=to_list)
    msg.content_subtype = "html"  # Main content is now text/html
    return msg.send()


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Kontoen {username} er nu blevet oprettet.")

            #Send velkomsts mail
            template_name="main/velkomstMail.html"
            to_list = [form.cleaned_data.get('email')]
            subject = "Velkommen til Parkering.tk"
            context = {'username': username}
            send_html_email(to_list, subject, template_name, context, sender=settings.DEFAULT_FROM_EMAIL)


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
    return render(request, 'main/support.html')

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
