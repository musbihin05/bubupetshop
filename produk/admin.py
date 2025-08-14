from django.contrib import admin
from django.utils.html import format_html
from .models import Produk

class ProdukConfig(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Hanya tampilkan menu jika user adalah superuser
        return request.user.is_superuser or request.user.is_staff
      
    def has_view_permission(self, request, obj = ...):
        return request.user.is_superuser or request.user.is_staff
      
    def has_delete_permission(self, request, obj = ...):
        return request.user.is_superuser 
      
    def has_change_permission(self, request, obj = ...):
        return request.user.is_superuser or request.user.is_staff
      
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff
      
    list_display = ('nama_produk', 'harga_produk_rupiah', 'stok_produk', 'kategori', 'gambar_produk_preview')
    search_fields = ('nama_produk', 'kategori')
    list_filter = ('kategori',)

    def gambar_produk_preview(self, obj):
        if obj.gambar_produk:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="60" height="60" style="object-fit:cover;" /></a>',
                obj.gambar_produk.url,
                obj.gambar_produk.url
            )
        return "-"
    gambar_produk_preview.short_description = "Gambar Produk"
    gambar_produk_preview.admin_order_field = 'gambar_produk'
    
    def harga_produk_rupiah(self, obj):
        # Format harga produk ke rupiah dengan titik sebagai pemisah ribuan
        value = int(obj.harga_produk)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    harga_produk_rupiah.short_description = 'Harga produk'
    harga_produk_rupiah.admin_order_field = 'harga_produk'

admin.site.register(Produk, ProdukConfig)
