DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'PORT': '5432',
        'HOST': 'sccoastalpesticides.org',
        'NAME': 'sccoasta_pesticiderev2',
        'USER': 'sccoasta_pesticide',
        'PASSWORD': 'Lci@2012',
    }
}

#BROKER_URL = "django://" # tell kombu to use the Django database as the message queue
#import djcelery
#djcelery.setup_loader()

#LOG_FILE = "/home2/sccoasta/tmp/pesticide_tool/app.log"
LOG_FILE = "/users/danramage/tmp/app.log"
