from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'),namespace='home')),
    path('syaratdanketentuan/', include(('syaratdanketentuan.urls', 'syaratdanketentuan'), namespace='syaratdanketentuan')),
    path('user/', include(('user.urls', 'user'),namespace='user')),
    path('peliharaan/', include(('peliharaan.urls', 'peliharaan'), namespace='peliharaan')),
    path('produk/', include(('produk.urls', 'produk'), namespace='produk')),
    path('layanan/', include(('layanan.urls', 'layanan'), namespace='layanan')),
    path('booking/', include(('bookinglayanan.urls', 'bookinglayanan'), namespace='bookinglayanan')),
    
]