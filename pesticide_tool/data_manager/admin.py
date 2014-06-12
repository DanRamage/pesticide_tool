from django.contrib import admin

# Register your models here.
class ActiveIngredient(admin.ModelAdmin):
    list_display = ('name', 'row_id')
    search_fields = ['name']
    ordering = ('name')
