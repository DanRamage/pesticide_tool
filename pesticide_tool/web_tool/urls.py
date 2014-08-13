from django.conf.urls import patterns
from views import *

urlpatterns = patterns('',
    (r'^category', pest_category),
    (r'^start', start_page),
    (r'^pesticide_search', pesticide_search),

    (r'^pest_ai_page/(?P<pest_name>[\w-]*)', pest_ai_page),
    (r'^get_info_for_brand/(?P<brand>[\w-]*)', get_info_for_brand),
    (r'^get_pests_for_subcategory/(?P<sub_category>[\w-]*)', get_pests_for_subcategory),
    (r'^get_ai_for_pest/(?P<pest>[\w-]*)', get_ai_for_pest),

    (r'^get_categories', get_categories),
    (r'^get_pestcide_names', get_pestcide_names),

)
