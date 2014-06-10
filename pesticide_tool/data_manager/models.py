# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class ActiveIngredient(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)
    cumulative_score = models.FloatField(blank=True, null=True)
    relative_potential_ecosystem_hazard = models.CharField(max_length=-1, blank=True)

    warning = models.ForeignKey('Warning', blank=True, null=True)


class Brand(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)
    label_url = models.CharField(max_length=-1, blank=True)

    active_ingredients = models.ManyToManyField('ActiveIngredient')
    application_areas = models.ManyToManyField('ApplicationArea')
    pests_treated = models.ManyToManyField('ApplicationArea')

class BrandFormulation(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    brand_id = models.ForeignKey('Brand', null=False)
    active_ingredient = models.ForeignKey('ActiveIngredient', null=False)
    percentage_active_ingredient = models.FloatField(null=False)
    
class Pest(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)
    image_url = models.CharField(max_length=-1, blank=True)

    pesticides = models.ManyToManyField('ActiveIngredient', blank=True, null=True)

class ActiveIngredientClass(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)

    active_ingredient = models.ManyToManyField('ActiveIngredient', blank=True, null=True)

class ApplicationArea(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)

    brand = models.ManyToManyField('Brand', blank=True, null=True)

class Warning(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=-1)
    image_url = models.CharField(max_length=-1, blank=True)


class PestType(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)


class Category(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)
    image_url = models.CharField(max_length=-1, blank=True)

class SubCategory(models.Model):
    row_id = models.IntegerField(primary_key=True)
    row_entry_date = models.DateTimeField(blank=True, null=True)
    row_update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=-1)
    image_url = models.CharField(max_length=-1, blank=True)

    category = models.ForeignKey('Category', null=True)
    pests = models.ForeignKey('Pest', null=True)

"""
class PestToPesticide(models.Model):
    row_id = models.IntegerField(primary_key=True)
    pest = models.ForeignKey(Pest, blank=True, null=True)
    pesticide = models.ForeignKey('Pesticide', blank=True, null=True)

class ApplicationAreaToBrand(models.Model):
    row_id = models.IntegerField(primary_key=True)
    application_area = models.ForeignKey(ApplicationArea, blank=True, null=True)
    brand = models.ForeignKey('Brand', blank=True, null=True)


class BrandToPesticide(models.Model):
    row_id = models.IntegerField(primary_key=True)
    brand = models.ForeignKey(Brand, blank=True, null=True)
    pesticide = models.ForeignKey('Pesticide', blank=True, null=True)


class PestToSubCategory(models.Model):
    row_id = models.IntegerField(primary_key=True)
    pest = models.ForeignKey(Pest, blank=True, null=True)
    sub_category = models.ForeignKey('SubCategory', blank=True, null=True)

class PestTypeToPest(models.Model):
    row_id = models.IntegerField(primary_key=True)
    pest_type = models.ForeignKey(PestType, blank=True, null=True)
    pest = models.ForeignKey(Pest, blank=True, null=True)


class PesticideClassToPesticide(models.Model):
    row_id = models.IntegerField(primary_key=True)
    pesticide_class = models.ForeignKey(PesticideClass, blank=True, null=True)
    pesticide = models.ForeignKey(Pesticide, blank=True, null=True)


class SubCategoryToCategory(models.Model):
    row_id = models.IntegerField(primary_key=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    sub_category = models.ForeignKey(SubCategory, blank=True, null=True)


class WarningToPesticide(models.Model):
    row_id = models.IntegerField(primary_key=True)
    warning = models.ForeignKey(Warning, blank=True, null=True)
    pesticide = models.ForeignKey(Pesticide)
"""
