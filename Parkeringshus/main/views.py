from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Contact, Plates, Log, ParkingEntity
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm, PlateForm
from datetime import datetime

# Create your views here.
def homepage(request):
    current_user = request.user
    uid = current_user.id
    if current_user.is_authenticated:
        return render(request=request,
                      template_name="main/home.html",
                      context={"plates":Plates.objects.filter(userid=uid),"logs":Log.objects.filter(numberplate__in=Plates.objects.filter(userid=uid).values('plateNumber')),"now":datetime.now,"uid":uid,"parkplace":ParkingEntity.objects.all})
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
