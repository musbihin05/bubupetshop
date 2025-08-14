from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("", views.index , name="index"),
    path("login", views.loginView , name="login"),
    path('logout', LogoutView.as_view(next_page='home:index'), name='logout'),
    path('update-profile', views.update_profile, name='update_profile'),
    path('change-password', views.change_password, name='change_password'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)