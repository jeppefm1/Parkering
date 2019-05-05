### Views er det som koder al Django/Python koden (altså modeller og formularer) ###
# sammen med HTML-koden. Det er nødvendigt, da views skaber sammenhæng og giver
# HTML en kontekst, som gør det muligt at bruge Django-funktioner på siderne.
###                                                                              ###

import numpy as np
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

#Til at sende emails
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
#Henter mailadresse fra instillingerne
from django.conf import settings

# Til grafer
import plotly.offline as py
import plotly.graph_objs as go

# Startsiden skal vide om brugeren er logget ind. Hvis det er sandt, så skal
# den vide


def rm_dups(nums):
    set(tuple(element) for element in nums)
    return [list(t) for t in set(tuple(element) for element in nums)]

def homepage(request):
    current_user = request.user
    uid = current_user.id
    if current_user.is_authenticated:
        return render(request=request,
                      template_name="main/home.html",
                      context={"plates":Plates.objects.filter(userid=uid),
                      "logs":Log.objects.filter(numberplate__in=Plates.objects.filter(userid=uid).values('plateNumber')).order_by('-entered'),
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

def totalStats(request):
    current_user = request.user
    uid = current_user.id
    if current_user.is_authenticated:
        # De to QuerySet initialiseres
        logs = Log.objects.filter(numberplate__in=Plates.objects.filter(userid=uid).values('plateNumber'),exited__isnull=False).order_by('exited')
        parkplace = ParkingEntity.objects.all()
        # Variable og lister initialiseres
        total = 0
        hours = 0

        x = []
        y1 = []
        y2 = []
        for log in logs:
            for house in parkplace:
                if house.id == log.entid:
                    hourlyRate = house.hourlyRate
            duration = log.get_time_diff()
            subtotal = duration * hourlyRate

            # Først adderes det
            hours += duration
            total += subtotal
            # Herefter tilføjes det til et array
            x.append(log.exited)
            y1.append(hours)
            y2.append(total)

        trace_duration = go.Scatter(
            x=x,
            y=y1,
            name = "Varighed",
            line = dict(color = '#17BECF'),
            opacity = 0.8,
            hoverinfo = 'name+y')

        trace_pay = go.Scatter(
            x=x,
            y=y2,
            name = "Beløb",
            line = dict(color = 'rgb(148, 103, 189)'),
            opacity = 0.8,
            yaxis = 'y2',
            hoverinfo = 'name+y')

        data = [trace_pay,trace_duration]

        layout = dict(
            title='Samlet beløb og tid',
            showlegend=False,
            yaxis=dict(
                title='Total varighed i timer',
                titlefont=dict(
                    color='#17BECF'
                ),
                tickfont=dict(
                    color='#17BECF'
                ),
            ),
            yaxis2=dict(
                title='Totalt beløb i kroner',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            ),
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label='1m',
                             step='month',
                             stepmode='backward'),
                        dict(count=6,
                             label='6m',
                             step='month',
                             stepmode='backward'),
                        dict(label='alt',
                             step='all')
                    ])
                ),
                type='date'
            )
        )

        fig = dict(data=data, layout=layout)

        div = py.plot(fig, config={'displayModeBar': False}, auto_open=False, output_type='div')

        return render(request=request,
                      template_name="main/total.html",
                      context={"plates":Plates.objects.filter(userid=uid),"logs":logs,
                      "uid":uid,"total":total,"hours":hours,'graph':div})
    else: return render(request=request,template_name="main/total.html")


class deleteplate(DeleteView):
    model = Plates
    success_url = reverse_lazy('main:addplate')
