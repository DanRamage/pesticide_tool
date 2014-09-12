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
import logging

logger = logging.getLogger("pesticide_tool")

class ActiveIngredient(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.TextField(unique=True)
  display_name = models.TextField(unique=False)
  cumulative_score = models.FloatField(blank=True, null=True)
  relative_potential_ecosystem_hazard = models.CharField(max_length=50, blank=True, null=True)

  warnings = models.ManyToManyField('Warning', blank=True, null=True)
  pests_treated = models.ManyToManyField('Pest')
  pesticide_classes = models.ManyToManyField('PesticideClass')
  brands = models.ManyToManyField('Brand')

  def __unicode__(self):
    return self.name

  @property
  def toDict(self):
    warnings = []
    if self.warnings:
      warnings = [warning.toDict for warning in self.warnings.all()]
    pesticide_classes = []
    if self.pesticide_classes:
      pesticide_classes = [pc.toDict for pc in self.pesticide_classes.all()]
    brands = []
    if self.brands:
      brands = [brand.toDict for brand in self.brands.all()]
    ai = {
      "id" : self.row_id,
      "name": self.name,
      "display_name": self.display_name,
      "cumulative_score": self.cumulative_score,
      "relative_potential_ecosystem_hazard": self.relative_potential_ecosystem_hazard,
      "warnings": warnings,
      "pesticide_classes": pesticide_classes,
      "brands": brands
    }
    return ai

class PesticideClass(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=128)
  def __unicode__(self):
    return self.name

  @property
  def toDict(self):
    pc = {
      'id': self.row_id,
      'name': self.name
    }
    return pc

class Brand(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.TextField()
  label_url = models.TextField(null=True)

  special_local_need = models.NullBooleanField(null=True)
  restricted_use = models.NullBooleanField(null=True)
  experimental_use = models.NullBooleanField(null=True)

  formulation = models.CharField(max_length=50, blank=True, null=True, default=None)
  epa_registration_number = models.CharField(unique=False, max_length=50)

  company_name = models.ManyToManyField('Company', blank=True)
  company_number = models.IntegerField(blank=True, null=True)

  pesticide_type = models.ManyToManyField('PesticideClass')
  active_ingredients = models.ManyToManyField('BrandFormulation')
  application_areas = models.ManyToManyField('ApplicationArea')
  pests_treated = models.ManyToManyField('Pest')

  def __unicode__(self):
    return self.name

  @property
  def toDict(self):
    pt = []
    if self.pesticide_type:
      pt = [pt.toDict for pt in self.pesticide_type.all()]
    ai = []
    if self.active_ingredients:
      ai = [ai.toDict for ai in self.active_ingredients.all()]
    aa = []
    if self.application_areas:
      aa = [aa.toDict for aa in self.application_areas.order_by('name').all()]
    pest = []
    if self.pests_treated:
      pest = [pest.toDict for pest in self.pests_treated.order_by('name').all()]
    brand = {
      'id': self.row_id,
      'name': self.name,
      'label_url': self.label_url,
      'special_local_need': self.special_local_need,
      'restricted_use': self.restricted_use,
      'experimental_use': self.experimental_use,
      'formulation': self.formulation,
      'pesticide_type': pt,
      'active_ingredients': ai,
      'application_areas': aa,
      'pests_treated': pest
    }
    if logger:
      logger.debug("Brand: %s" % (brand))
    return brand
class Company(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.TextField()
  epa_id = models.CharField(max_length=25)

  def __unicode__(self):
    return self.name

class BrandFormulation(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  brand_id = models.ForeignKey('Brand', null=True)
  #brand_id = models.ManyToManyField('Brand', null=False)
  brand_name = models.TextField()
  active_ingredient = models.ForeignKey('ActiveIngredient', null=False)
  percentage_active_ingredient = models.FloatField(null=False)

  def __unicode__(self):
    return self.active_ingredient

  @property
  def toDict(self):
    formulation = {
      'id': self.row_id,
      'brand_name': self.brand_name,
      'active_ingredient': self.active_ingredient.display_name,
      'percent_active_ingredient': self.percentage_active_ingredient
    }
    return formulation

class Pest(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(max_length=128)

  display_name = models.CharField(max_length=128)

  image_url = models.TextField(null=True)

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

  @property
  def toDict(self):
    pest = {
      'id': self.row_id,
      'name': self.name,
      'display_name': self.display_name,
      'image_url': self.image_url
    }

    return pest

class ActiveIngredientClass(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=256)
  display_name = models.CharField(max_length=256)

  active_ingredient = models.ManyToManyField('ActiveIngredient', blank=True, null=True)

  def __unicode__(self):
    return self.name

class ApplicationArea(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=256, blank=False)

  #brand = models.ManyToManyField('Brand', blank=True, null=True)

  def __unicode__(self):
    return self.name

  @property
  def toDict(self):
    aa = {
      'id': self.row_id,
      'name': self.name
    }

    return aa

class Warning(models.Model):
  row_id = models.IntegerField(primary_key=True)
  row_entry_date = models.DateTimeField(blank=True, null=True)
  row_update_date = models.DateTimeField(blank=True, null=True)
  name = models.CharField(unique=True, max_length=50)
  display_name = models.CharField(max_length=50)
  image_url = models.TextField(blank=True, null=True)

  def __unicode__(self):
    return self.name

  def admin_thumbnail(self):
    if self.image_url:
      return u'<img src="%s" />' % (self.image_url)
    else:
      return u''

  admin_thumbnail.short_description = 'Thumbnail'
  admin_thumbnail.allow_tags = True

  @property
  def toDict(self):
    warning = {
      'id': self.row_id,
      'name': self.name,
      'display_name': self.display_name,
      'image_url': self.image_url
    }
    return warning

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

  @property
  def toDict(self):
    sub_categories = [
      {
        'id': sub_cat.row_id,
        'name': sub_cat.name,
        'image_url': sub_cat.image_url
      }
      for sub_cat in self.sub_categories.all()
    ]
    category_dict = {
        'id': self.row_id,
        'name': self.name,
        'image_url': self.image_url,
        'sub_categories': sub_categories
    }
    return category_dict




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
