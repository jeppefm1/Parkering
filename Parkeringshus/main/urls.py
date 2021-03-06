# urls.py indeholder informationer om hvilket 'view' serveren skal sende til
# browseren når den efterspørger et bestemt URL
from django.urls import path, re_path
# De views som er blevet lavet skal bruges, derfor importeres de
from . import views

app_name = "main"

# URL-mønsteret indstilles. Her refererer det første i path() til underdomænet, det
# andet til hvilken view der skal vises, og hvilket navn det kan refereres til.
urlpatterns = [
	path('', views.homepage, name="homepage"),
	path('total/', views.totalStats, name="totalStats"),
	path('registrer/', views.register, name="registrer"),
	path('logout/', views.logout_request, name="logout"),
	path('support/', views.support, name="login"),
	path('addplate/', views.addplate, name="addplate"),
	re_path('addplate/(?P<pk>\d+)/delete/$', views.deleteplate.as_view(), name="delete_plate"),
]
