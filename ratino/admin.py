from django.contrib import admin

from ratino.models import Rate


# Register your models here.

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('text', 'rate')
