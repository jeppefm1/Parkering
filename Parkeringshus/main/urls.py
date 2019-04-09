from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = "main"

urlpatterns = [
	path('', views.homepage, name="homepage"),
	path('registrer/', views.register, name="registrer"),
	path('logout/', views.logout_request, name="logout"),
	path('login/', views.login_request, name="login"),
	path('password_reset/',  auth_views.PasswordResetView.as_view(template_name = 'templates/main/password_reset.html'), name="password_reset"),
	path('password_reset_done/',  auth_views.PasswordResetDoneView.as_view(template_name = 'templates/main/password_reset_done.html'), name="password_reset_done"),
	path('password-rese-confirm/<uidb64>/<token>/',  auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
	path('support/', views.support, name="login"),
	path('addplate/', views.addplate, name="addplate"),
	re_path('addplate/(?P<pk>\d+)/delete/$', views.deleteplate.as_view(), name="delete_plate"),
]
