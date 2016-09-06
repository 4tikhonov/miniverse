import json
from collections import OrderedDict

from django.http import Http404
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page


from dv_apps.datasets.util import DatasetUtil

def get_pretty_val(request):
    """Quick check of url param to pretty print JSON"""

    if request.GET.get('pretty', None) is not None:
        return True
    return False


#@cache_page(60 * 60 * 2)
@login_required
def view_single_dataset_by_id(request, dataset_version_id):

    try:
        dataset_version = DatasetVersion.objects.select_related('dataset'\
            ).get(pk=dataset_version_id)
    except DatasetVersion.DoesNotExist:
        raise Http404

    return view_single_dataset_version(request, dataset_version)


#@cache_page(60 * 15)
@login_required
def view_single_dataset_version(request, dsv):
    """
    Show JSON for a single DatasetVersion
    """
    if dsv is None:
        raise Http404

    assert isinstance(dsv, DatasetVersion), "dv must be a DatasetVersion object or None"

    is_pretty = request.GET.get('pretty', None)
    if is_pretty is not None:
        is_pretty = True

    resp_dict = OrderedDict()
    resp_dict['status'] = "OK"
    resp_dict['data'] = DatasetUtil(dsv).as_json()
    #model_to_dict(dv)

    if is_pretty:
        s = '<pre>%s</pre>' % json.dumps(resp_dict, indent=4)
        return HttpResponse(s)
    else:
        return JsonResponse(resp_dict)#, content_type='application/json')
