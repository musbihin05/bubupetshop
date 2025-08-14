from django.db import models

# Create your models here.
class DetailPetcare(models.Model):
    id = models.AutoField(primary_key=True)
    nama_petcare = models.CharField(max_length=50)
    tlp_petcare = models.CharField(max_length=20)
    email_petcare = models.CharField(max_length=100)
    alamat_petcare = models.TextField(blank=True, null=True)
    maps_petcare = models.CharField(max_length=1000, blank=True, null=True)
    deskripsi_petcare = models.TextField(blank=True, null=True)
    rekening_petcare = models.CharField(max_length=100, blank=True, null=True)
    pemilik_rekening = models.CharField(max_length=100, blank=True, null=True)
    nama_bank = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'detail_petcare'
        verbose_name_plural = "Detail Petcare"

    def __str__(self):
        return self.nama_petcare