from django.db import models

# Create your models here.
class RiwayatPenjualan(models.Model):
    id_penjualan = models.AutoField(primary_key=True)
    tanggal_penjualan = models.DateTimeField(auto_now_add=True)
    pelanggan = models.CharField(max_length=255)
    layanan = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ])
    total_penjualan = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'riwayat_penjualan'
        verbose_name_plural = "Riwayat Penjualan"

    def __str__(self):
        return f"Penjualan {self.id_penjualan} - {self.tanggal_penjualan.strftime('%Y-%m-%d %H:%M:%S')}"