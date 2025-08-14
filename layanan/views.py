from django.shortcuts import render
from .models import LayananGrooming, LayananPenitipan, LayananKesehatan

# Create your views here.
def index(request):
    grooming_services = LayananGrooming.objects.all()[:3]
    penitipan_services = LayananPenitipan.objects.all()[:3]
    kesehatan_services = LayananKesehatan.objects.all()[:3]
    context = {
        'title': "Semua Layanan",
        'grooming_services': grooming_services,
        'penitipan_services': penitipan_services,
        'kesehatan_services': kesehatan_services,
    }
    return render(request, 'layanan/index.html', context)

def layanan_grooming(request):
    grooming_services = LayananGrooming.objects.all()
    context = {
        'title': "Layanan Grooming",
        'grooming_services': grooming_services,
    }
    return render(request, 'layanan/grooming.html', context)
  
def layanan_penitipan(request):
    penitipan_services = LayananPenitipan.objects.all()
    context = {
        'title': "Layanan Penitipan",
        'penitipan_services': penitipan_services,
    }
    return render(request, 'layanan/penitipan.html', context)

def layanan_kesehatan(request):
    kesehatan_services = LayananKesehatan.objects.all()
    context = {
        'title': "Layanan Kesehatan",
        'kesehatan_services': kesehatan_services,
    }
    return render(request, 'layanan/kesehatan.html', context)