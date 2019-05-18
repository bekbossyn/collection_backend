from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'collection_database',
        'USER': 'collection_user',
        'PASSWORD': 'collection_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/home/dev/static/'
MEDIA_ROOT = '/home/dev/media/'

SITE_URL = 'http://188.166.17.34'
