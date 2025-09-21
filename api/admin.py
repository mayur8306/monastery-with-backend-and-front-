from django.contrib import admin
from .models import Monastery

@admin.register(Monastery)
class MonasteryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'iframe_url')  # shows in admin list
