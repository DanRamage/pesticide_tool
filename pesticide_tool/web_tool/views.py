#from django.shortcuts import render
#import warnings

from django.template import RequestContext
from django.shortcuts import render_to_response
from data_manager.models import *
import simplejson
from django.http import HttpResponse
import logging

logger = logging.getLogger("pesticide_tool")

"""
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.db.models.base import ModelBase
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.core import urlresolvers
"""
# Create your views here.
def start_page(request, template='entry_page.html'):
  #context = {'domain': get_domain(8000), 'domain8010': get_domain()}
  return render_to_response(template, context_instance=RequestContext(request))

def pest_category(request, template='pest_category.html'):
  return render_to_response(template, context_instance=RequestContext(request))

def pesticide_search(request, template='pesticide_search.html'):
  active_ingredients = []
  return render_to_response(template, context_instance=RequestContext(request))

def get_pestcide_ai_names(request):
  if logger:
    logger.debug("Begin get_pestcide_names")
  pesticides = Brand.objects.all().only('name').order_by('name')
  ais = ActiveIngredient.objects.all().only('display_name').order_by('display_name')

  json = {
    'pesticides': [rec.name for rec in pesticides],
    'active_ingredients': [rec.display_name for rec in ais]
  }

  if logger:
    logger.debug("End get_pestcide_names. Pesticides: %d AIs: %d." % (len(json['pesticides']), len(json['active_ingredients'])))

  return HttpResponse(simplejson.dumps(json))

def get_ai(request, ai):
  search_term = ai
  if(len(search_term) == 0):
    search_term = request.GET['ai']
  if logger:
    logger.debug("Begin get_ai: %s" % (search_term))

  ai_list = ActiveIngredient.objects.filter(display_name__exact=search_term)\
    .all()\
    .prefetch_related('brands').only("brands__name")\
    .prefetch_related('warnings')\
    .prefetch_related('pesticide_classes')

  ret_data = []
  for ai in ai_list:
    brand_data = []
    for brand in ai.brands.all():
      brand_data.append({
        'name': brand.name
      })
    ret_data.append({
      'name': ai.name,
      'display_name': ai.display_name,
      'cumulative_score': ai.cumulative_score,
      'relative_potential_ecosystem_hazard': ai.relative_potential_ecosystem_hazard.capitalize(),
      'pesticide_classes': [pc.toDict for pc in ai.pesticide_classes.all()],
      'warnings': [warning.toDict for warning in ai.warnings.all()],
      'brands': brand_data
    })

  json = {
    "ai_list" : ret_data,
    "success": True
  }
  if logger:
    logger.debug("Finshied get_ai. Returning %d active ingredients" % (len(json['ai_list'])))
  return HttpResponse(simplejson.dumps(json))



def pest_ai_page(request, pest_name, template='ais_for_pest.html'):
  search_term = pest_name
  if(len(search_term) == 0):
    search_term = request.GET['pest_name']
  if logger:
    logger.debug("Begin pest_ai_page for pest: %s" % (search_term))
  return render_to_response(template, context_instance=RequestContext(request))

"""
def get_categories(request, template='pest_category.html'):
  categories = Category.objects.all().order_by('name')
  context = { 'categories': categories}
  return render_to_response(template, context_instance=RequestContext(request, context))
"""

def get_categories(request):
  json = {
    "categories" : [category.toDict for category in Category.objects.all().order_by('name')],
    "success": True
  }
  return HttpResponse(simplejson.dumps(json))

def get_pests_for_subcategory(request, sub_category):
  search_term = sub_category
  if(len(search_term) == 0):
    search_term = request.GET['sub_category']
  if logger:
    logger.debug("Begin get_pests_for_subcategory: %s" % (search_term))

  sub_cat = SubCategory.objects.filter(name__exact=search_term).prefetch_related('pests').all()[:1].get()
  json = {
    "pests" : [pest.toDict for pest in sub_cat.pests.all()],
    "success": True
  }
  if logger:
    logger.debug("Finshied get_pests_for_subcategory. Returning %d pests" % (len(json['pests'])))
  return HttpResponse(simplejson.dumps(json))

def get_ai_for_pest(request, pest):
  search_term = pest
  if(len(search_term) == 0):
    search_term = request.GET['pest']
  if logger:
    logger.debug("Begin get_ai_for_pest: %s" % (search_term))

  ai_list = ActiveIngredient.objects.filter(pests_treated__display_name__exact=search_term)\
    .order_by('cumulative_score').all()\
    .prefetch_related('brands').only("brands__name")\
    .prefetch_related('warnings')\
    .prefetch_related('pesticide_classes')

  ret_data = []
  for ai in ai_list:
    brand_data = []
    for brand in ai.brands.all():
      brand_data.append({
        'name': brand.name
      })
    ret_data.append({
      'name': ai.name,
      'display_name': ai.display_name,
      'cumulative_score': ai.cumulative_score,
      'relative_potential_ecosystem_hazard': ai.relative_potential_ecosystem_hazard.capitalize(),
      'pesticide_classes': [pc.toDict for pc in ai.pesticide_classes.all()],
      'warnings': [warning.toDict for warning in ai.warnings.all()],
      'brands': brand_data
    })

  json = {
    "ai_list" : ret_data,
    "success": True
  }
  if logger:
    logger.debug("Finshied get_ai_for_pest. Returning %d active ingredients" % (len(json['ai_list'])))
  return HttpResponse(simplejson.dumps(json))

def get_info_for_brand(request, brand):
  search_term = brand
  if(len(search_term) == 0):
    search_term = request.GET['brand']
  if logger:
    logger.debug("Begin get_info_for_brand: %s" % (search_term))

  brand_info = Brand.objects.filter(name__iexact=search_term).all()[:1].get()
  json = {
    'brand_info': brand_info.toDict,
    'success': True
  }
  if logger:
    logger.debug("End get_info_for_brand")
  return HttpResponse(simplejson.dumps(json))
