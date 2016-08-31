"""
LTS (Library Technical Systems) Production URLs
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Dataverse Metrics (Miniverse)'

urlpatterns = [
    # Examples:
    # url(r'^$', 'miniverse.views.home', name='home'),
    url(r'^dr2m/', include('dv_apps.dvobjects.urls')),

    url(r'^dataset/', include('dv_apps.datasets.urls')),

    url(r'^miniverse/map/', include('dv_apps.installations.urls')),

    url(r'^miniverse/metrics/', include('dv_apps.metrics.urls')),

    # temp experiment
    url(r'^dvobjects/', include('dv_apps.dvobject_api.urls')),

    url(r'^miniverse/miniverse-admin/', include(admin.site.urls)),

]
