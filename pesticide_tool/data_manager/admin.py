from django.contrib import admin
from models import *

# Register your models here.
"""
class LayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'layer_type', 'url')
    search_fields = ['name', 'layer_type']
    ordering = ('name','metadatatable')
    exclude = ('slug_name',)
"""
class ActiveIngredientAdmin(admin.ModelAdmin):
  list_display = ('name', 'row_id')
  search_fields = ['name']
  ordering = ('name','row_id')

class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'admin_thumbnail')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class SubCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'admin_thumbnail')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class PestAdmin(admin.ModelAdmin):
  list_display = ('name', 'admin_thumbnail')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class WarningAdmin(admin.ModelAdmin):
  list_display = ('name', 'admin_thumbnail')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class BrandFormulationAdmin(admin.ModelAdmin):
  list_display = ('active_ingredient', 'brand_name')
  ordering = ('percentage_active_ingredient', 'row_id')
  search_fields = ['name']

class CompanyAdmin(admin.ModelAdmin):
  list_display = ('name', 'epa_id')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class ApplicationAreaAdmin(admin.ModelAdmin):
  list_display = ('name', 'row_id')
  ordering = ('name', 'row_id')
  search_fields = ['name']

class BrandAdmin(admin.ModelAdmin):
  list_display = ('name', 'row_id')
  ordering = ('name', 'row_id')
  search_fields = ['name']

admin.site.register(ActiveIngredient, ActiveIngredientAdmin)
admin.site.register(PesticideClass)#, PesticideClassAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(BrandFormulation, BrandFormulationAdmin)
admin.site.register(Pest, PestAdmin)
admin.site.register(Warning, WarningAdmin)
admin.site.register(PestType)#, PestTypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ApplicationArea, ApplicationAreaAdmin)
