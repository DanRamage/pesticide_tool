from django.conf.urls import patterns
from views import *

urlpatterns = patterns('',
    (r'^category', pest_category),
    (r'^start', start_page),
    (r'^pesticide_search', pesticide_search),
    (r'^brand/(?P<brand_name>[\w-]*)', brand_page),
    (r'^brand_name/(?P<brand_name>[^a-zA-Z0-9%&/]+)', brand_page),
    (r'^active_ingredient/ai_name/(?P<ai_name>[^/]+)', ai_info_page),
    (r'^active_ingredient/pest_name/(?P<pest_name>[^/]+)', get_ai_for_pest),

    (r'^pest_ai_page/(?P<pest_name>[\w-]*)', pest_ai_page),
    (r'^get_info_for_brand/(?P<brand>[\w-]*)', get_info_for_brand),
    (r'^get_pests_for_subcategory/(?P<sub_category>[\w-]*)', get_pests_for_subcategory),
    (r'^get_ai_for_pest/(?P<pest>[\w-]*)', get_ai_for_pest),

    (r'^get_categories', get_categories),
    (r'^get_pestcide_ai_names', get_pestcide_ai_names),
    #(r'^get_ai/(?P<ai>[\w-]*)', get_ai),

)
