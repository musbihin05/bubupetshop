from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from produk.models import Produk
from django.db.models.functions import Random
# Create your views here.
def index(request):
    kategori_dict = dict(Produk.KATEGORI_CHOICES)
    produk = list(Produk.objects.order_by(Random())[:20])

    for p in produk:
        p.kategori_label = kategori_dict.get(p.kategori, '')

    context = {
      'title': "Bubu Petshop",

      'kategori_produk': kategori_dict,
      'produk_list': produk[:20],  # opsional jika ingin berapa produk yang ditampilkan
    }
    return render(request, 'home/index.html', context)


