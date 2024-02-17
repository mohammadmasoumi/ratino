from django.contrib import admin

from divar_homepage.models import DivarProfile, Scope


# Register your models here.

@admin.register(DivarProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')

@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
