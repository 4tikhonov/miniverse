from django.conf.urls import url
#from dv_apps.metrics.views import view_dataset_count
from . import views

urlpatterns = [
    url(r'^datasets/count$', views.view_dataset_count, name='view_dataset_count'),


    #url(r'^datasets/count$', views.view_dataset_count, name='view_dataset_count'),
#(?P<start_date>d{4}-d{2}-d{2})
    #url(r'^view/(?P<dataset_id>\d{1,8})?', view_dataset_detail, name='view_dataset_detail'),
    #url(r'^t/(?P<username>\w{1,50})', 'view_test_query', name='view_test_query_with_username'),

    #url(r'^test-query', 'view_test_query', name='view_test_query'),

 #   url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

  #  url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', 'show_import_success_params', name="show_import_success_params"),

]
