from __future__ import absolute_import
import os
from os.path import join#, normpath, isdir, isfile
import dj_database_url

from .base import *

# Set the secret key
SECRET_KEY = os.environ['SECRET_KEY']

# Cookie name
SESSION_COOKIE_NAME = 'dv_metrics_dev'


#INTERNAL_IPS = ()   # Heroku IP

ALLOWED_HOSTS = ['54.235.72.96',]


## Database settings via Heroku url
#
#  We have two databases:
#   - Heroku db for django + "installations" app
#   - external Dataverse db for reading stats
#
DATABASE_ROUTERS = ['miniverse.settings.db_django_contrib_router.DjangoContribRouter', ]


HEROKU_DB_CONFIG = dj_database_url.config(conn_max_age=500)

# Set the Miniverse admin url
DATABASES['miniverse_admin_db'].update(HEROKU_DB_CONFIG)
DATABASES['miniverse_admin_db']['TEST'] = {'MIRROR': 'default'}

# Set the Dataverse url
DV_DEMO_DATABASE_URL = dj_database_url.parse(os.environ['DV_DEMO_DATABASE_URL'])
DATABASES['default'].update(DV_DEMO_DATABASE_URL)

# Heroku specific urls
ROOT_URLCONF = 'miniverse.urls_heroku_dev'


"""
DATABASES = {
    'miniverse_admin_db': HEROKU_DB_CONFIG,
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dvn_thedata',   #  dvn_thedata dvndb_demo
        'USER': 'postgres', # dv_readonly, postgres
        'PASSWORD': '123',
        'HOST': 'localhost'
    }
}
"""

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    join(PROJECT_ROOT, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
