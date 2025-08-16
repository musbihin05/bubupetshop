from django.shortcuts import render, get_object_or_404
from produk.models import Produk
from django.db.models import Count  
import random

# Create your views here.
def index(request):
  
    kategori_dict = dict(Produk.KATEGORI_CHOICES)
    produk = Produk.objects.order_by('?')
    for p in produk:
        p.kategori_label = kategori_dict.get(p.kategori, '')
    
   
    context = {
      'title': "Bubu Petshop",

      'kategori_produk': kategori_dict,
      'produk_list': produk,
    }
    return render(request, 'produk/index.html', context)
  
  
def detail_produk(request, produk_id):
    kategori_dict = dict(Produk.KATEGORI_CHOICES)
  
    produk = get_object_or_404(Produk, id_produk = produk_id)
    produk.kategori_label = kategori_dict.get(produk.kategori, '')

    context = {
      "title": "Detail Produk {}".format(produk.nama_produk),
      "produk": produk
    }
    
    return render(request, 'produk/detail.html', context)

