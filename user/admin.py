from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
  
    def has_add_permission(self, request):
        return request.user.is_superuser
      
    def has_change_permission(self, request, obj = ...):
        return request.user.is_superuser
      
    def has_delete_permission(self, request, obj = ...):
        return request.user.is_superuser
      
    def has_view_permission(self, request, obj = ...):
        return request.user.is_superuser or request.user.is_staff

    model = User
    list_display = ('email', 'nama', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nama', 'no_hp')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
      
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nama', 'no_hp', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'nama')
    ordering = ('email',)

admin.site.register(User, UserAdmin)
