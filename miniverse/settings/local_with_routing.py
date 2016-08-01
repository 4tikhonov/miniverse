from __future__ import absolute_import
import json
import sys
from os import makedirs
from os.path import join, normpath, isdir, isfile

from .base import *

SECRET_KEY = 'make-a-secret-key'

LOCAL_SETUP_DIR = join(BASE_DIR, 'test_setup')
if not isdir(LOCAL_SETUP_DIR):
    makedirs(LOCAL_SETUP_DIR)

DATABASE_ROUTERS = ['miniverse.settings.db_django_contrib_router.DjangoContribRouter', ]


DATABASES = {
    'django_contrib_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(LOCAL_SETUP_DIR, 'metrics_auth.db3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dvndb_demo',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost'
    }
}
"""
'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dvndb_demo',
    'USER': 'postgres',
    'PASSWORD': '123',
    'HOST': 'localhost'
}

'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dvndb',
    'USER': 'rp',
    'PASSWORD': '123',
    'HOST': 'localhost'
}
"""

SESSION_COOKIE_NAME = 'dv_metrics'

# where static files are collected
STATIC_ROOT = join(LOCAL_SETUP_DIR, 'static')
if not isdir(STATIC_ROOT):
    makedirs(STATIC_ROOT)


########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
    'django.contrib.admindocs',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION
