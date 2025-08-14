from django.contrib import admin
from django.utils.html import format_html
from .models import LayananPenitipan, LayananGrooming, LayananKesehatan

class LayananPenitipanAdmin(admin.ModelAdmin):
  
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
  
    list_display = ('jenis_penitipan', 'kapasitas_penitipan', 'harga_penitipan_rupiah', 'deskripsi_penitipan')
    
    search_fields = ['jenis_penitipan', 'deskripsi_penitipan']
    list_filter = ['kapasitas_penitipan', 'harga_penitipan']
    
    def harga_penitipan_rupiah(self, obj):
        value = int(obj.harga_penitipan)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    harga_penitipan_rupiah.short_description = 'Harga penitipan'
    harga_penitipan_rupiah.admin_order_field = 'harga_penitipan'

class LayananGroomingAdmin(admin.ModelAdmin):
  
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
      
    list_display = ('nama_grooming', 'harga_grooming_rupiah', 'deskripsi_grooming')
    search_fields = ['nama_grooming', 'deskripsi_grooming']
    list_filter = ['harga_grooming']
    
    def harga_grooming_rupiah(self, obj):
        value = int(obj.harga_grooming)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    harga_grooming_rupiah.short_description = 'Harga grooming'
    harga_grooming_rupiah.admin_order_field = 'harga_grooming'

class LayananKesehatanAdmin(admin.ModelAdmin):
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
  
    list_display = ('nama_kesehatan', 'harga_kesehatan_rupiah', 'deskripsi_kesehatan')
    search_fields = ['nama_kesehatan', 'deskripsi']
    list_filter = ['harga_kesehatan']

    def harga_kesehatan_rupiah(self, obj):
        value = int(obj.harga_kesehatan)
        rupiah = f"Rp {value:,}".replace(",", ".")
        return format_html('<span>{}</span>', rupiah)
    harga_kesehatan_rupiah.short_description = 'Harga kesehatan'
    harga_kesehatan_rupiah.admin_order_field = 'harga_kesehatan'

admin.site.register(LayananPenitipan, LayananPenitipanAdmin)
admin.site.register(LayananGrooming, LayananGroomingAdmin)
admin.site.register(LayananKesehatan, LayananKesehatanAdmin)
