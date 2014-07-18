from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^category', pest_category),
    (r'^$', start_page),
)
