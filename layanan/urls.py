from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index , name="index"),
   path("grooming", views.layanan_grooming, name="layanan_grooming"),
   path("penitipan", views.layanan_penitipan, name="layanan_penitipan"),
   path("kesehatan", views.layanan_kesehatan, name="layanan_kesehatan"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
