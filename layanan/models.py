from django.db import models
from datetime import datetime
import os


def layanan_image_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    new_filename = f"layanan_{timestamp}{ext}"
    return os.path.join("static/layanan_images/", new_filename)

# Create your models here.
class LayananPenitipan(models.Model):
    id_penitipan = models.AutoField(primary_key=True)
    jenis_penitipan = models.CharField(max_length=100)
    harga_penitipan = models.DecimalField(max_digits=8, decimal_places=2)
    kapasitas_penitipan = models.IntegerField()
    deskripsi_penitipan = models.TextField()
    foto_penitipan = models.ImageField(upload_to=layanan_image_upload_path, blank=True, null=True)

    class Meta:
        db_table = 'layanan_penitipan'
        verbose_name_plural = "Layanan Penitipan"

    def __str__(self):
        return self.jenis_penitipan

class LayananGrooming(models.Model):
    id_grooming = models.AutoField(primary_key=True)
    nama_grooming = models.CharField(max_length=100)
    harga_grooming = models.DecimalField(max_digits=8, decimal_places=2)
    deskripsi_grooming = models.TextField()
    foto_grooming = models.ImageField(upload_to=layanan_image_upload_path, blank=True, null=True)

    class Meta:
        db_table = 'layanan_grooming'
        verbose_name_plural = "Layanan Grooming"

    def __str__(self):
        return self.nama_grooming

class LayananKesehatan(models.Model):
    id_kesehatan = models.AutoField(primary_key=True)
    nama_kesehatan = models.CharField(max_length=100)
    harga_kesehatan = models.DecimalField(max_digits=8, decimal_places=2)
    deskripsi_kesehatan = models.TextField()
    foto_kesehatan = models.ImageField(upload_to=layanan_image_upload_path, blank=True, null=True)
    
    class Meta:
        db_table = 'layanan_kesehatan'
        verbose_name_plural = "Layanan Kesehatan"

    def __str__(self):
        return self.nama_kesehatan