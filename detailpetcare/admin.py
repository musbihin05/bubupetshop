from django.contrib import admin
from detailpetcare.models import DetailPetcare

# Register your models here.
class DetailPetcareAdmin(admin.ModelAdmin):
  
    list_display = ('nama_petcare', 'tlp_petcare', 'email_petcare', 'alamat_petcare')
    search_fields = ('nama_petcare', 'email_petcare')

admin.site.register(DetailPetcare, DetailPetcareAdmin)