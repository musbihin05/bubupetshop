import datetime
import os
from django.db import models
from user.models import User

def peliharaan_image_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    new_filename = f"peliharaan_{timestamp}{ext}"
    return os.path.join("static/peliharaan_images/", new_filename)


# Create your models here.
class Peliharaan(models.Model):

        
  
    JENIS_HEWAN_CHOICES = [
        ('cat', 'Kucing'),
        ('dog', 'Anjing'),
        ('other', 'lainya')
    ]
    
    class Meta:
        db_table = 'peliharaan'
        verbose_name_plural = "Peliharaan"

    id_hewan = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_hewan = models.CharField(max_length=50)
    jenis_hewan = models.CharField(max_length=50, choices=JENIS_HEWAN_CHOICES)
    umur_hewan = models.IntegerField()
    berat_hewan = models.DecimalField(max_digits=5, decimal_places=2)
    keterangan = models.TextField(blank=True, null=True)
    foto_peliharaan = models.ImageField(upload_to=peliharaan_image_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
  
    def __str__(self):
        return self.nama_hewan