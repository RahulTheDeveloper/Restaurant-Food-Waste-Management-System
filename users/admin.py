from django.contrib import admin
from .models import Client, AppUser
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client

class ClientAdmin(UserAdmin):
    # Specify fields to display in the admin
    list_display = ('id', 'name', 'email', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('email',)

    # Exclude non-editable fields
    exclude = ('created_at', 'updated_at',)

    # Customize fieldsets for the admin interface
    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'name', 'phone_number', 'address', 'oauth_id', 'is_active')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'phone_number', 'address', 'is_active'),
        }),
    )

# Register the Client model with the customized admin
admin.site.register(Client, ClientAdmin)



class AppUserAdmin(UserAdmin):
    model = AppUser
    list_display = ('username', 'email', 'phone_number', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'phone_number', 'address', 'oauth_id')}),
        (_('Permissions'), {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'is_active'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('email',)

admin.site.register(AppUser, AppUserAdmin)

# admin.site.register(Client, ClientAdmin)
