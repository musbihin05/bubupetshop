import os
from django.db import models
from datetime import datetime

def produk_image_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    new_filename = f"produk_{timestamp}{ext}"
    return os.path.join("static/produk_images/", new_filename)

class Produk(models.Model):
    KATEGORI_CHOICES = [
        ('food', 'Makanan'),
        ('toy', 'Mainan'),
        ('accessory', 'Aksesoris'),
        ('medicine', 'Obat-obatan')
    ]

    id_produk = models.AutoField(primary_key=True)
    nama_produk = models.CharField(max_length=200)
    harga_produk = models.DecimalField(max_digits=8, decimal_places=2)
    stok_produk = models.IntegerField()
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES)
    deskripsi_produk = models.TextField(blank=True, null=True)
    gambar_produk = models.ImageField(upload_to=produk_image_upload_path, blank=True, null=True)
    
    class Meta:
        db_table = 'produk'  
        verbose_name_plural = "Produk"

    def __str__(self):
        return self.nama_produk