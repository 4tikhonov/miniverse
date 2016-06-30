from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404

from apps.datasets.models import Dataset, DatasetVersion
from apps.datasetfields.models import DatasetField, DatasetFieldValue, DatasetFieldType
from apps.datasetfields.metadata_formatter import MetadataFormatter

# Create your views here.
def view_list_datasets(request):

    datasets = Dataset.objects.all()
    #datasets = Dataset.objects.select_related('id').all()
    #datasets = DatasetVersion.objects.select_related('dataset').all()

    lookup = dict(datasets=datasets)

    return render_to_response('dataset_list.html', lookup)
    #return HttpResponse('view_list_datasets')

def view_dataset_detail(request, dataset_id):

    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return Http404('dataset_id not found')


    dataset_versions = DatasetVersion.objects.select_related('dataset'\
                    ).filter(dataset=dataset)

    lookup = dict(dataset=dataset,\
                 dataset_versions=dataset_versions)

    if dataset_versions.count() > 0:
        latest_version = dataset_versions[0]

        mdf = MetadataFormatter(latest_version)

        lookup.update(dict(metadata_fields=mdf.metadata_fields,\
                        metadata_blocks=mdf.metadata_blocks))

        #ds_fields = DatasetField.objects.select_related('datasetfieldtype', 'parentdatasetfieldcompoundvalue').filter(datasetversion=latest_version)

        #ds_values = DatasetFieldValue.objects.select_related('datasetfield'\
        #                ,'datasetfield__datasetfieldtype').filter(datasetfield__datasetversion=latest_version)

        #lookup.update(dict(ds_fields=ds_fields,\
        #                    ds_values=ds_values,\
        #                     metadata_fields=mdf.metadata_fields))

    return render_to_response('dataset_detail.html', lookup)
