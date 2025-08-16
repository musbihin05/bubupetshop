from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



from . import views

urlpatterns = [
    path("", views.index , name="index"),
    path("tambah", views.tambah_booking, name="tambah_booking"),
    path("detail/<int:booking_id>/", views.detail_booking, name="detail_booking"),
    path("pembayaran/<int:booking_id>/", views.detail_pembayaran, name="detail_pembayaran"),
]