from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^category', pest_category),
    (r'^start', start_page),
    (r'^get_categories', get_categories),
    (r'^get_pests_for_subcategory/(?P<sub_category>[\w-]*)', get_pests_for_subcategory),
)
