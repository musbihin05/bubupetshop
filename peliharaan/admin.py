from django.contrib import admin
from django.utils.html import format_html
from .models import Peliharaan

# Register your models here.
class PeliharaanConfig(admin.ModelAdmin):
  
   model = Peliharaan
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


   search_fields = ('nama_hewan', 'jenis_hewan')
   list_filter = ('jenis_hewan',)
  
   list_display = (
       'nama_hewan',
       'jenis_hewan',
       'umur_hewan',
       'berat_hewan',
       'foto_peliharaan_preview',
   )
   
   def foto_peliharaan_preview(self, obj):
       if obj.foto_peliharaan:
           return format_html(
               '<a href="{}" target="_blank"><img src="{}" width="60" height="60" style="object-fit:cover;" /></a>',
                obj.foto_peliharaan.url,
                obj.foto_peliharaan.url
           )
       return "-"
   foto_peliharaan_preview.short_description = "Foto Peliharaan"
   foto_peliharaan_preview.admin_order_field = 'foto_peliharaan'

 

admin.site.register(Peliharaan, PeliharaanConfig)