from django.contrib import admin
from models import *

# Register your models here.
class ActiveIngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'row_id')
    search_fields = ['name']
    ordering = ('name','row_id')

admin.site.register(ActiveIngredient, ActiveIngredientAdmin)
admin.site.register(PesticideClass)#, PesticideClassAdmin)
admin.site.register(Brand)#, BrandAdmin)
admin.site.register(BrandFormulation)#, BrandFormulationAdmin)
admin.site.register(Pest)#, PestAdmin)
admin.site.register(Warning)#, WarningAdmin)
admin.site.register(PestType)#, PestTypeAdmin)
admin.site.register(Category)#, CategoryAdmin)
admin.site.register(SubCategory)#, SubCategoryAdmin)
