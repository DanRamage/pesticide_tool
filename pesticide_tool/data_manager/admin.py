from django.contrib import admin
from models import *

# Register your models here.
class ActiveIngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'row_id')
    search_fields = ['name']
    ordering = ('name')

admin.site.register(ActiveIngredient, ActiveIngredientAdmin)
