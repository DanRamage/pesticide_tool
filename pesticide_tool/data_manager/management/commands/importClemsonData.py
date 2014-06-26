from optparse import make_option
import logging
import ConfigParser
import os
import simplejson as json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Max
from ... models import *
from _pesticideClemsonWebRequest import clemsonWebService,product,application_sites

#importClemsonData --ConfigFile=/Users/danramage/Documents/workspace/PesticideProject/pesticide_tool/pesticide_tool/data_manager/management/commands/pesticideDebug.ini --CreateInitialData --StartingActiveIngredient=aminocyclopyrachlor
logger = logging.getLogger('pesticide_tool')


def queryClemsonWebService(**kwargs):
  if logger:
    logger.info("Starting active ingredient lookups.")

  webService = clemsonWebService(kwargs['config_file'], 'pesticide_tool')
  if 'starting_ingredient' in kwargs and kwargs['starting_ingredient']:
    query = ActiveIngredient.objects.filter(name__gte = kwargs['starting_ingredient']).all().order_by('name')
  else:
    query = ActiveIngredient.objects.all().order_by('name')
  #for layer in Layer.objects.all().order_by('name'):
  for active_ingredient in query:
    if logger:
      logger.debug("%s retrieving info." % (active_ingredient.name))
    info = webService.searchByActiveIngredient(active_ingredient.name)

  if logger:
    logger.info("FInished active ingredient lookups.")


def build_dict(model_dict, value, ndx):
  if value not in model_dict:
    model_dict[value] = ndx
    return False
  return True

def build_app_model(area, ndx, date):
  return({
    "pk": ndx,
    "model": "data_manager.ApplicationArea",
    "fields" : {
      "row_entry_date": date,
      "name": area
    }
  })
def build_pesticide_type_model(type, ndx, date):
  return({
    "pk": ndx,
    "model": "data_manager.PesticideClass",
    "fields": {
      "row_entry_date": date,
      "name": type
    }
  })

def build_pest_model(pest, ndx, date):
  return({
    "pk": ndx,
    "model": "data_manager.Pest",
    "fields": {
      "row_entry_date": date,
      "name": pest.name,
      "display_name": pest.display_name,
      "image_url": pest.image_url
    }
  })
def build_company_model(prod, ndx, date):
  return({
    "pk": ndx,
    "model": "data_manager.Company",
    "fields": {
      "row_entry_date": date,
      "name": prod.company_name,
      "epa_id": prod.company_number
    }
  })

def build_active_ingredient(ingr, ndx, date):
  return({
    "pk": ndx,
    "model": "data_manager.ActiveIngredient",
    "fields": {
      "row_entry_date": date,
      "name": ingr.active_ingredient
    }
  })

def build_formulation(ingr, brand_name, ndx, date, lookups):
  return({
    "pk": ndx,
    "model": "data_manager.BrandFormulation",
    "fields": {
      "row_entry_date": date,
      "brand_name": brand_name,
      "active_ingredient": lookups['ai_lookup'][ingr.active_ingredient.lower()],
      "percentage_active_ingredient": ingr.percentage_active_ingredient
    }
  })
def build_brand_model(prod, lookups, ndx, date, ai_for_brand):
  return({
    "pk": ndx,
    "model": "data_manager.Brand",
    "fields": {
      "row_entry_date": date,
      "name": prod.name,
      "label_url": prod.label_url,
      "restricted_use": prod.restricted_use,
      "special_local_need": prod.special_local_need,
      "formulation": prod.formulation,
      "epa_registration_number": prod.epa_registration_number,
      "company_name" : [lookups['company_lookup'][prod.company_name]],
      "company_number": prod.company_number,
      "pesticide_type": [lookups['type_lookup'][prod.pesticide_type.lower()]],
      "pests_treated": [lookups['pest_lookup'][rec.name] for rec in prod.pests_treated],
      "application_areas": [lookups['site_lookup'][rec] for rec in prod.application_areas],
      "active_ingredients": ai_for_brand
    }
  })
def createInitialData(**kwargs):
  config_file = ConfigParser.RawConfigParser()
  config_file.read(kwargs['config_file'])

  #We want to get a list of the active ingredients we have in the database that
  #have the calculations for toxicity so we don't overwrite them. When importing
  #the Clemson data, there are brands with active ingredients we don't have that
  #data for but want to add.
  calculated_ais = []
  #Build the init data for the active ingredient models.
  lookups = {
    'pest_lookup' : {},
    'company_lookup' : {},
    'site_lookup' : {},
    'brand_lookup': {},
    'ai_lookup': {},
    'form_lookup' : {},
    'type_lookup' :{}
  }

  ai_rows = ActiveIngredient.objects.all().order_by('name')
  for row in ai_rows:
    calculated_ais.append(row.name)
    #For the existing AIs, build the lookups.
    build_dict(lookups['ai_lookup'], row.name.lower(), row.row_id)
  ai_max_row_id = ai_rows.aggregate((Max('row_id')))

  #Build the lookups for the pesticide types we already have in db.
  pesticide_type_rows = PesticideClass.objects.all()
  for row in pesticide_type_rows:
    build_dict(lookups['type_lookup'], row.name.lower(), row.row_id)
  p_type_max_row_id =  pesticide_type_rows.aggregate((Max('row_id')))

  data_dir = config_file.get('output', 'jsonoutdir')
  initial_json = config_file.get('output', 'initial_json')
  brand_json = config_file.get('output', 'brand_only_init_json')
  row_entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  models = []
  brands_with_ai = []
  app_ndx = 1
  pest_ndx = 1
  #Have to start index past the AIs already in database.
  ingr_ndx = ai_max_row_id['row_id__max'] + 1
  cmp_ndx = 1
  prod_ndx = 1
  form_ndx = 1
  type_ndx = p_type_max_row_id['row_id__max'] + 1

  for file in os.listdir(data_dir):
    if file.endswith(".json"):
      if logger:
        logger.info("Processing file: %s" % (file))
      file_obj = open("%s/%s" % (data_dir,file), "r")
      json_data = json.load(file_obj)
      product_list = []
      for active_ingr in json_data.keys():
        brands = json_data[active_ingr]
        for brand in brands:
          prod = product()
          prod.load_from_json(brand)
          product_list.append(prod)

      #Make a pass to build the unique values for the active ingredients, pests, and application
      #sites. In the initial JSON we have to create their models and we need their pk ids to
      #make the relations.
      for prod in product_list:
        if build_dict(lookups['company_lookup'], prod.company_name, cmp_ndx) == False:
          models.append(build_company_model(prod, cmp_ndx, row_entry_date))
          cmp_ndx += 1
        for area in prod.application_areas:
          if build_dict(lookups['site_lookup'], area, app_ndx) == False:
            models.append(build_app_model(area, app_ndx, row_entry_date))
            app_ndx += 1
        for pest in prod.pests_treated:
          if build_dict(lookups['pest_lookup'], pest.name, pest_ndx) == False:
            models.append(build_pest_model(pest, pest_ndx, row_entry_date))
            pest_ndx += 1

        if build_dict(lookups['type_lookup'], prod.pesticide_type.lower(), type_ndx) == False:
          models.append(build_pesticide_type_model(prod.pesticide_type, type_ndx, row_entry_date))
          type_ndx += 1


        if build_dict(lookups['brand_lookup'], prod.name, prod_ndx) == False:
          prod_ndx += 1

        ai_for_brand = []
        for ingr in prod.active_ingredients:
          if build_dict(lookups['ai_lookup'], ingr.active_ingredient.lower(), ingr_ndx) == False:
            #Check to see if the active ingredient is one we already have in the DB.
            if (ingr.active_ingredient in calculated_ais) == False:
              models.append(build_active_ingredient(ingr, ingr_ndx, row_entry_date))
              ingr_ndx += 1

          #Build the formulation for the brand.
          build_dict(lookups['form_lookup'],  prod.name + '_' + ingr.active_ingredient.lower(), form_ndx)
          ai_model = build_formulation(ingr, prod.name, form_ndx, row_entry_date, lookups)
          ai_for_brand.append(ai_model['pk'])
          models.append(ai_model)
          form_ndx += 1

        brand_model = build_brand_model(prod, lookups, prod_ndx, row_entry_date, [])
        models.append(brand_model)
        #Build the brand model that has the AI data.
        brand_model = build_brand_model(prod, lookups, prod_ndx, row_entry_date, ai_for_brand)
        brands_with_ai.append(brand_model)
      if logger:
        logger.info("Finished processing file: %s" % (file))
      break
  try:
    out_file = open(initial_json, "w")
    out_file.write(json.dumps(models, sort_keys=True, indent=2 * ' '))
    out_file.close()

    out_file = open(brand_json, "w")
    out_file.write(json.dumps(brands_with_ai, sort_keys=True, indent=2 * ' '))
    out_file.close()
  except Exception, e:
    logger.exception(e)

  return

class Command(BaseCommand):
  option_list = BaseCommand.option_list  + (
      make_option("--ConfigFile", dest="config_file"),
      make_option("--ImportFromWeb", dest="import_from_web", action='store_true', default='false'),
      make_option("--StartingActiveIngredient", dest="starting_ingredient", default=None),
      make_option("--CreateInitialData", dest="create_init", action='store_true', default='false'),
  )

  def handle(self, *args, **options):
    if logger:
      logger.info("Processing command: %s" % (options))
    if options['import_from_web'] is True:
      queryClemsonWebService(config_file = options['config_file'], starting_ingredient=options['starting_ingredient'])
    if options['create_init'] is True:
      createInitialData(config_file = options['config_file'])
    if logger:
      logger.info("Finished processing command")
    return