from django.db import models
from layanan.models import LayananPenitipan, LayananGrooming, LayananKesehatan
from peliharaan.models import Peliharaan
from user.models import User
import os
import datetime
from django.utils import timezone  # Tambahkan import ini
from datetime import timedelta



def buktibayar_image_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    new_filename = f"buktibayar_{timestamp}{ext}"
    return os.path.join("static/buktibayar_images/", new_filename)

# Create your models here.
class BookingLayanan(models.Model):
    JENIS_LAYANAN_CHOICES = [
        ('grooming', 'Grooming'),
        ('sitting', 'Penitipan'),
        ('medical', 'Kesehatan'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('confirmed', 'Dikonfirmasi'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    id_booking = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    id_hewan = models.ForeignKey(Peliharaan, on_delete=models.CASCADE)
    tipe_layanan = models.CharField(max_length=20, choices=JENIS_LAYANAN_CHOICES)
    harga_booking = models.DecimalField(max_digits=8, decimal_places=2)

    booking_penitipan = models.ForeignKey(
        LayananPenitipan, null=True, blank=True, on_delete=models.SET_NULL)
    booking_grooming = models.ForeignKey(
        LayananGrooming, null=True, blank=True, on_delete=models.SET_NULL)
    booking_kesehatan = models.ForeignKey(
        LayananKesehatan, null=True, blank=True, on_delete=models.SET_NULL)

    tanggal_booking = models.DateTimeField(null=True, blank=True)  # Gunakan null=True, blank=True untuk fleksibilitas
    tanggal_selesai = models.DateTimeField(null=True, blank=True)
    durasi_layanan = models.IntegerField(null=True, blank=True)
    status_booking = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    catatan_booking = models.TextField(blank=True, null=True)
    bukti_pembayaran = models.ImageField(
        upload_to=buktibayar_image_upload_path, blank=True, null=True)

    class Meta:
        db_table = 'booking_layanan'
        verbose_name_plural = "Daftar Booking"


    def __str__(self):
        return f"{self.id_booking} - {self.tipe_layanan}"
    
# Di bookinglayanan/models.py
class DailyCapacity(models.Model):
    layanan_penitipan = models.ForeignKey(LayananPenitipan, on_delete=models.CASCADE)
    tanggal = models.DateField()
    kapasitas_tersedia = models.IntegerField()

    class Meta:
        unique_together = ('layanan_penitipan', 'tanggal',)
        verbose_name_plural = "Daily Capacities"

    def __str__(self):
        # Ubah .nama_layanan menjadi .jenis_penitipan
        return f"Kapasitas pada {self.tanggal} untuk {self.layanan_penitipan.jenis_penitipan}"