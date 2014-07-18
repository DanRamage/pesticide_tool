#from django.shortcuts import render
#import warnings

from django.template import RequestContext
from django.shortcuts import render_to_response
from data_manager.models import *
import simplejson as json
from django.http import HttpResponse

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

def category(request, template='pest_category.html'):
  return render_to_response(template, context_instance=RequestContext(request))

"""
def get_categories(request, template='pest_category.html'):
  categories = Category.objects.all().order_by('name')
  context = { 'categories': categories}
  return render_to_response(template, context_instance=RequestContext(request, context))
"""

def get_categories(request):
  json = {
    "categories" : [category.toDict for category in Category.objects.all().order_by('name')]
    "success": True
  }
  return HttpResponse(json.dumps(json))