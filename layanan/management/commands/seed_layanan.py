from django.core.management.base import BaseCommand
from layanan.models import LayananGrooming, LayananPenitipan, LayananKesehatan

class Command(BaseCommand):
    help = 'Seed layanan data'

    def handle(self, *args, **kwargs):
        LayananGrooming.objects.create(nama_grooming="Grooming Kucing", harga_grooming=100000)
        LayananGrooming.objects.create(nama_grooming="Grooming Anjing", harga_grooming=150000)
        LayananPenitipan.objects.create(jenis_penitipan="Penitipan Kucing", harga_penitipan=200000, kapasitas_penitipan=3)
        LayananPenitipan.objects.create(jenis_penitipan="Penitipan Anjing", harga_penitipan=250000, kapasitas_penitipan=2)
        LayananKesehatan.objects.create(nama_kesehatan="Vaksin Kucing", harga_kesehatan=300000)
        LayananKesehatan.objects.create(nama_kesehatan="Vaksin Anjing", harga_kesehatan=350000)
        self.stdout.write(self.style.SUCCESS('Layanan data seeded successfully.'))
