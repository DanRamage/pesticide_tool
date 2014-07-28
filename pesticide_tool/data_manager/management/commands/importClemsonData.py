from optparse import make_option
import logging
import ConfigParser
import os
import simplejson as json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Max
from ... models import *
from _pesticideClemsonWebRequest import clemsonWebService,clemsonCSVWebData,product

#importClemsonData --ConfigFile=/Users/danramage/Documents/workspace/PesticideProject/pesticide_tool/pesticide_tool/data_manager/management/commands/pesticideDebug.ini --CreateInitialData --StartingActiveIngredient=aminocyclopyrachlor
logger = logging.getLogger('pesticide_tool')


def queryClemsonWebService(**kwargs):
  if logger:
    logger.info("Starting active ingredient lookups.")

  webService = clemsonWebService(kwargs['config_file'], 'pesticide_tool')
  if 'starting_ingredient' in kwargs and kwargs['starting_ingredient']:
    query = ActiveIngredient.objects.exclude(relative_potential_ecosystem_hazard__exact='').filter(name__gte = kwargs['starting_ingredient']).all().order_by('name')
  else:
    query = ActiveIngredient.objects.exclude(relative_potential_ecosystem_hazard__exact='').all().order_by('name')
  #for layer in Layer.objects.all().order_by('name'):
  for active_ingredient in query:
    if logger:
      logger.debug("%s retrieving info." % (active_ingredient.name))
    info = webService.searchByActiveIngredient(active_ingredient.name)

  if logger:
    logger.info("FInished active ingredient lookups.")

def queryClemsonCSVData(**kwargs):
  if logger:
    logger.info("Starting csv lookups.")

  webService = clemsonCSVWebData(kwargs['config_file'], 'pesticide_tool')
  query = ActiveIngredient.objects.exclude(relative_potential_ecosystem_hazard__exact='').all().order_by('name')
  for active_ingredient in query:
    if logger:
      logger.debug("%s retrieving info." % (active_ingredient.name))
    webService.searchByActiveIngredient(active_ingredient.name)
  return

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
def active_ingredient(ai_row, row_entry_date):
  return({
    "pk": ai_row.row_id,
    "model": "data_manager.ActiveIngredient",
    "fields":
      {
        "row_entry_date": row_entry_date,
        "name": ai_row.name,
        "display_name": ai_row.display_name,
        "cumulative_score": ai_row.cumulative_score,
        "relative_potential_ecosystem_hazard": ai_row.relative_potential_ecosystem_hazard,
        "warnings": [warning.row_id for warning in ai_row.warnings.all()],
        "pests_treated": [pest.row_id for pest in ai_row.pests_treated.all()],
        "pesticide_classes": [pc.row_id for pc in ai_row.pesticide_classes.all()],
        "brands": []
      }
  })
def build_active_ingredient(ingr, ndx, date):

  return({
    "pk": ndx,
    "model": "data_manager.ActiveIngredient",
    "fields": {
      "row_entry_date": date,
      "name": ingr.active_ingredient,
      "display_name": ingr.active_ingredient,
      "cumulative_score": None,
      "relative_potential_ecosystem_hazard": None,
      "warnings": [],
      "pests_treated": [],
      "pesticide_classes": [],
      "brands": []

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

  #Pull in the initial data from Lisa's spreadsheet if it is available. We want to
  #integrate the Pests into the output here.
  """
  try:
    init_pesticide_obj = None
    init_data_filename = config_file.get('initial_data', 'initial_data_file')
    init_pesticide_data = open(init_data_filename, 'r')
    #COnvert into object
    init_pesticide_obj = json.load(init_pesticide_data)
    init_pesticide_data.close()
  except IOError,e:
    if logger:
      logger.exception(e)
  except ConfigParser.Error, e:
    if logger:
      logger.exception(e)
  """
  #We want to get a list of the active ingredients we have in the database that
  #have the calculations for toxicity so we don't overwrite them. When importing
  #the Clemson data, there are brands with active ingredients we don't have that
  #data for but want to add.
  calculated_ais = []
  existing_pests = []
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
  row_entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  ai_models = {}
  ai_rows = ActiveIngredient.objects.all().order_by('name').prefetch_related('warnings').prefetch_related('pests_treated').prefetch_related('pesticide_classes')
  for row in ai_rows:
    ai_models[row.name] = active_ingredient(row, row_entry_date)
    calculated_ais.append(row.name)
    #For the existing AIs, build the lookups.
    build_dict(lookups['ai_lookup'], row.name.lower(), row.row_id)
  ai_max_row_id = ai_rows.aggregate((Max('row_id')))

  #Build the lookups for the pesticide types we already have in db.
  pesticide_type_rows = PesticideClass.objects.all()
  for row in pesticide_type_rows:
    build_dict(lookups['type_lookup'], row.name.lower(), row.row_id)
  p_type_max_row_id =  pesticide_type_rows.aggregate((Max('row_id')))

  pest_rows = Pest.objects.all().order_by('name')
  for row in pest_rows:
    existing_pests.append(row.name.lower())
    build_dict(lookups['pest_lookup'], row.name.lower(), row.row_id)
  pest_max_row_id = pest_rows.aggregate((Max('row_id')))

  data_dir = config_file.get('output', 'jsonoutdir')
  initial_json = config_file.get('output', 'initial_json')
  brand_json = config_file.get('output', 'brand_only_init_json')

  models = {
    'type_models': [],
    'comp_models': [],
    'pest_models': [],
    'site_models': [],
    'form_models': [],
    'brand_models': [],
    'ai_models': [],
  }
  brands_with_ai = []
  app_ndx = 1
  pest_ndx = 1
  if pest_max_row_id['row_id__max']:
    pest_ndx = pest_max_row_id['row_id__max'] + 1
  #Have to start index past the AIs already in database.
  ingr_ndx = 1
  if ai_max_row_id['row_id__max']:
    ingr_ndx = ai_max_row_id['row_id__max'] + 1
  cmp_ndx = 1
  prod_ndx = 1
  form_ndx = 1
  type_ndx = 1
  if p_type_max_row_id['row_id__max']:
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
          models['comp_models'].append(build_company_model(prod, cmp_ndx, row_entry_date))
          cmp_ndx += 1
        for area in prod.application_areas:
          if build_dict(lookups['site_lookup'], area, app_ndx) == False:
            models['site_models'].append(build_app_model(area, app_ndx, row_entry_date))
            app_ndx += 1
        for pest in prod.pests_treated:
          if build_dict(lookups['pest_lookup'], pest.name, pest_ndx) == False:
            #Pest already in DB?
            if (pest.name.lower() in existing_pests) == False:
              models['pest_models'].append(build_pest_model(pest, pest_ndx, row_entry_date))
              pest_ndx += 1
            else:
              if logger:
                logger.debug("Pest: %s already in database" % (pest.name))
        if build_dict(lookups['type_lookup'], prod.pesticide_type.lower(), type_ndx) == False:
          models['type_models'].append(build_pesticide_type_model(prod.pesticide_type, type_ndx, row_entry_date))
          type_ndx += 1


        if build_dict(lookups['brand_lookup'], prod.name, prod_ndx) == False:
          prod_ndx += 1

        ai_for_brand = []
        for ingr in prod.active_ingredients:
          """
          if build_dict(lookups['ai_lookup'], ingr.active_ingredient.lower(), ingr_ndx) == False:
            #Check to see if the active ingredient is one we already have in the DB.
            #if (ingr.active_ingredient in calculated_ais) == False:
            if(ingr.active_ingredient in ai_models) == False:
              models['ai_models'].append(build_active_ingredient(ingr, ingr_ndx, row_entry_date))
              ingr_ndx += 1
          """
          if (ingr.active_ingredient in ai_models) == False:
            ai_models[ingr.active_ingredient] = build_active_ingredient(ingr, ingr_ndx, row_entry_date)


          #Build the formulation for the brand.
          build_dict(lookups['form_lookup'],  prod.name + '_' + ingr.active_ingredient, form_ndx)
          ai_model = build_formulation(ingr, prod.name, form_ndx, row_entry_date, lookups)
          ai_for_brand.append(ai_model['pk'])
          models['form_models'].append(ai_model)
          form_ndx += 1

        brand_model = build_brand_model(prod, lookups, prod_ndx, row_entry_date, [])
        models['brand_models'].append(brand_model)
        #Add the brand ID into the active ingredients.
        if prod.name == 'ACE GREEN TURF PHOSPHORUS FREE WEED & FEED 29-0-3':
          i = 0;
        for ingr in prod.active_ingredients:
          if ingr.active_ingredient in ai_models:
            ai_models[ingr.active_ingredient]['fields']['brands'].append(brand_model['pk'])

        #Build the brand model that has the AI data.
        brand_model = build_brand_model(prod, lookups, prod_ndx, row_entry_date, ai_for_brand)
        brands_with_ai.append(brand_model)
        #Build the brand list for the AI.
        #ai_brands.append(brand)
      if logger:
        logger.info("Finished processing file: %s" % (file))

  # We want to get the initial set of pests that have the images for the sub categories
  # and add them in the mix.
  """
  if init_pesticide_obj:
    #If we have the pest ndx already in the database, don't try and add it again.
    del_list = []
    for obj in init_pesticide_obj:
      if obj['model'] == 'data_manager.Pest':
        #Change the pk so we don't get duplicate error.
        obj['pk'] = pest_ndx
        for ndx, rec in enumerate(models['pest_models']):
          if rec['fields']['name'] == obj['fields']['name']:
            del_list.append(ndx)
    if len(del_list):
      for ndx in del_list:
        del models['pest_models'][ndx]
  """
  try:
    #Write the initial JSON data for each of the model types. Break them apart since
    #the data is pretty large.
    """
    'type_models': [],
    'comp_models': [],
    'pest_models': [],
    'site_models': [],
    'form_models': [],
    'brand_models': [],
    'ai_models': [],
    """
    file_name = "%s/pests.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['pest_models'], sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/sites.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['site_models'], sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/pesticide_types.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['type_models'], sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/companies.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['comp_models'], sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/pesticide_formulas.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['form_models'], sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/active_ingredients.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(ai_models, sort_keys=True, indent=2 * ' '))
    out_file.close()

    file_name = "%s/brands.json" % (initial_json)
    out_file = open(file_name, "w")
    out_file.write(json.dumps(models['brand_models'], sort_keys=True, indent=2 * ' '))
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
      make_option("--ImportFromCSV", dest="import_from_csv", action='store_true', default='false'),
      make_option("--StartingActiveIngredient", dest="starting_ingredient", default=None),
      make_option("--CreateInitialData", dest="create_init", action='store_true', default='false'),
      make_option("--BuildAIBrands", dest="build_ai_brands", action='store_true', default='false'),
  )

  def handle(self, *args, **options):
    if logger:
      logger.info("Processing command: %s" % (options))
    if options['import_from_web'] is True:
      queryClemsonWebService(config_file = options['config_file'], starting_ingredient=options['starting_ingredient'])
    if options['create_init'] is True:
      createInitialData(config_file = options['config_file'])
    if options['import_from_csv'] is True:
      queryClemsonCSVData(config_file = options['config_file'])
    #if options['build_ai_brands'] is True:
    #  buildBrandsForAIFromDb(config_file = options['config_file'])
    if logger:
      logger.info("Finished processing command")
    return