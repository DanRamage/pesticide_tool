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
  if logger:
    logger.info("View search param: %s" % (sub_category))
  search_term = sub_category
  if(len(search_term) == 0):
    search_term = request.GET['sub_category']
  if logger:
    logger.info("Begin get_pests_for_subcategory: %s" % (search_term))

  sub_cat = SubCategory.objects.filter(name__exact=search_term).prefetch_related('pests').all()[:1]
  json = {
    "pests" : [pest.toDict for pest in sub_cat.pests],
    "success": True
  }
  return HttpResponse(simplejson.dumps(json))
