from optparse import make_option
import logging

from django.core.management.base import BaseCommand

from ... models import *
from _pesticideClemsonWebRequest import clemsonWebService

logger = logging.getLogger('pesticide_tool')


def queryClemsonWebService(config_file):
  if logger:
    logger.info("Starting active ingredient lookups.")
  webService = clemsonWebService(config_file, 'pesticide_tool')
  #for layer in Layer.objects.all().order_by('name'):
  for active_ingredient in ActiveIngredient.objects.all().order_by('name'):
    if logger:
      logger.debug("%s retrieving info." % (active_ingredient.name))
    info = webService.searchByActiveIngredient(active_ingredient.name)

  if logger:
    logger.info("FInished active ingredient lookups.")

class Command(BaseCommand):
  option_list = BaseCommand.option_list  + (
      make_option("--ConfigFile", dest="config_file"),
      make_option("--ImportFromWeb", dest="import_from_web", action='store_true', default='false'),
  )

  def handle(self, *args, **options):
    if options['import_from_web']:
      queryClemsonWebService(options['config_file'])

    return