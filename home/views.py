from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from produk.models import Produk
# Create your views here.
def index(request):
    kategori_dict = dict(Produk.KATEGORI_CHOICES)
    produk = Produk.objects.all()

    for p in produk:
        p.kategori_label = kategori_dict.get(p.kategori, '')

    context = {
      'title': "Bubu Petshop",

      'kategori_produk': kategori_dict,
      'produk_list': produk[:4],  # opsional jika ingin 4 produk terbaru
    }
    return render(request, 'home/index.html', context)


