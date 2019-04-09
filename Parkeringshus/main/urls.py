# urls.py indeholder informationer om hvilket 'view' serveren skal sende til
# browseren når den efterspørger et bestemt URL
from django.urls import path, re_path
# De views som er blevet lavet skal bruges, derfor importeres de
from . import views

app_name = "main"

urlpatterns = [
	path('', views.homepage, name="homepage"),
	path('registrer/', views.register, name="registrer"),
	path('logout/', views.logout_request, name="logout"),
	path('login/', views.login_request, name="login"),
	path('support/', views.support, name="login"),
	path('addplate/', views.addplate, name="addplate"),
	re_path('addplate/(?P<pk>\d+)/delete/$', views.deleteplate.as_view(), name="delete_plate"),
]
