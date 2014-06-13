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
  name = models.CharField(unique=True, max_length=50)
  display_name = models.CharField(unique=True, max_length=50)
  cumulative_score = models.FloatField(blank=True, null=True)
  relative_potential_ecosystem_hazard = models.CharField(max_length=50, blank=True)

  warnings = models.ManyToManyField('Warning', blank=True, null=True)
  pests_treated = models.ManyToManyField('Pest')
  pesticide_classes = models.ManyToManyField('PesticideClass')
  brands = models.ManyToManyField('Brand')

  def __unicode__(self):
    return self.name

class PesticideClass(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  def __unicode__(self):
    return self.name

class Brand(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.TextField()
  label_url = models.TextField(blank=True)

  restricted_use = models.BooleanField(blank=True)
  special_local_need = models.BooleanField(blank=True)

  epa_registration_number = models.CharField(unique=True, max_length=50)

  company_name = models.ManyToManyField('Company', blank=True)
  pesticide_type = models.ManyToManyField('PesticideClass')
  active_ingredients = models.ManyToManyField('BrandFormulation')
  application_areas = models.ManyToManyField('ApplicationArea')
  pests_treated = models.ManyToManyField('Pest')

  def __unicode__(self):
    return self.name

class Company(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.TextField()
  epa_id = models.CharField(max_length=25)

class BrandFormulation(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  brand_id = models.ForeignKey('Brand', null=False)
  active_ingredient = models.ForeignKey('ActiveIngredient', null=False)
  percentage_active_ingredient = models.FloatField(null=False)

  def __unicode__(self):
    return self.name

class Pest(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)

  display_name2 = models.CharField(unique=True, max_length=50)

  image_url = models.TextField(blank=True)

  pesticides = models.ManyToManyField('ActiveIngredient', blank=True, null=True)

  def __unicode__(self):
    return self.name

  def admin_thumbnail(self):
    if self.image_url:
      return u'<img src="%s" />' % (self.image_url)
    else:
      return u''

  admin_thumbnail.short_description = 'Thumbnail'
  admin_thumbnail.allow_tags = True

class ActiveIngredientClass(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  display_name = models.CharField(unique=True, max_length=50)

  active_ingredient = models.ManyToManyField('ActiveIngredient', blank=True, null=True)

  def __unicode__(self):
    return self.name

class ApplicationArea(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)

  #brand = models.ManyToManyField('Brand', blank=True, null=True)

  def __unicode__(self):
    return self.name

class Warning(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  image_url = models.TextField(blank=True)

  def __unicode__(self):
    return self.name

class PestType(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)

  def __unicode__(self):
    return self.name

class Category(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  image_url = models.TextField()

  sub_categories = models.ManyToManyField('SubCategory', null=True)

  def __unicode__(self):
    return self.name

  def admin_thumbnail(self):
    if self.image_url:
      return u'<img src="%s" />' % (self.image_url)
    else:
      return u''

  admin_thumbnail.short_description = 'Thumbnail'
  admin_thumbnail.allow_tags = True

class SubCategory(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  image_url = models.TextField(blank=True)

  #category = models.ForeignKey('Category', null=True)
  pests = models.ManyToManyField('Pest', null=True)

  def __unicode__(self):
    return self.name

  def admin_thumbnail(self):
    if self.image_url:
      return u'<img src="%s" />' % (self.image_url)
    else:
      return u''

  admin_thumbnail.short_description = 'Thumbnail'
  admin_thumbnail.allow_tags = True

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
