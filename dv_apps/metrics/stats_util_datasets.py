"""
Create metrics for Datasets.
This may be used for APIs, views with visualizations, etc.
"""
#from django.db.models.functions import TruncMonth  # 1.10
from collections import OrderedDict

from django.db import models
from django.db.models import Q

from dv_apps.utils.date_helper import format_yyyy_mm_dd,\
    get_month_name_abbreviation,\
    month_year_iterator
from dv_apps.dvobjects.models import DvObject, DTYPE_DATASET, DTYPE_DATAFILE
from dv_apps.datasets.models import Dataset
from dv_apps.datafiles.models import Datafile
from dv_apps.dataverses.models import Dataverse, DATAVERSE_TYPE_UNCATEGORIZED
from dv_apps.guestbook.models import GuestBookResponse, RESPONSE_TYPE_DOWNLOAD
from dv_apps.metrics.stats_util_base import StatsMakerBase, TruncYearMonth


class StatsMakerDatasets(StatsMakerBase):

    def __init__(self, **kwargs):
        """
        Start and end dates are optional.

        start_date = string in YYYY-MM-DD format
        end_date = string in YYYY-MM-DD format
        """
        super(StatsMakerDatasets, self).__init__(**kwargs)

    # ----------------------------
    #  Datafile counts
    # ----------------------------
    def get_datafile_count(self, **extra_filters):
        """
        Return the Datafile count
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        filter_params = self.get_date_filter_params()
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        return True, Datafile.objects.filter(**filter_params).count()

    def get_datafile_count_published(self):
        """
        Return the count of published Dataverses
        """
        return self.get_datafile_count(**self.get_is_published_filter_param())


    def get_datafile_count_unpublished(self):
        """
        Return the count of published Dataverses
        """
        return self.get_datafile_count(**self.get_is_NOT_published_filter_param())


    # ----------------------------
    #  Dataverse counts
    # ----------------------------
    def get_dataverse_count_published(self):
        """
        Return the count of published Dataverses
        """
        return self.get_dataverse_count(**self.get_is_published_filter_param())


    def get_dataverse_count_unpublished(self):
        """
        Return the count of unpublished Dataverses
        """
        return self.get_dataverse_count(**self.get_is_NOT_published_filter_param())


    def get_dataverse_count(self, **extra_filters):
        """
        Return the Dataverse count
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        filter_params = self.get_date_filter_params()
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        return True, Dataverse.objects.filter(**filter_params).count()

    # ----------------------------
    #   Dataset counts (single number totals)
    # ----------------------------
    def get_dataset_count(self, **extra_filters):
        """
        Return the Dataset count
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        filter_params = self.get_date_filter_params()
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        return True, Dataset.objects.filter(**filter_params).count()

    def get_dataset_count_published(self):
        """
        Return the count of published Dataverses
        """
        return self.get_dataset_count(**self.get_is_published_filter_param())


    def get_dataset_count_unpublished(self):
        """
        Return the count of unpublished Dataverses
        """
        return self.get_dataset_count(**self.get_is_NOT_published_filter_param())

    # ----------------------------
    #   Dataset counts by create date
    # ----------------------------
    def get_dataset_counts_by_create_date(self, **extra_filters):
        """
        Get # of datasets created each month
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        filter_params = self.get_date_filter_params()
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        return self.get_dataset_count_by_month(date_param='dvobject__createdate',\
            **extra_filters)


    def get_dataset_counts_by_create_date_published(self):
        """
        Get # of --PUBLISHED-- datasets created each month
        """
        return self.get_dataset_counts_by_create_date(**self.get_is_published_filter_param())


    def get_dataset_counts_by_create_date_unpublished(self):
        """
        Get # of --UNPUBLISHED-- datasets created each month
        """
        return self.get_dataset_counts_by_create_date(**self.get_is_NOT_published_filter_param())


    def get_dataset_counts_by_publication_date(self):
        """
        Get # of datasets published each month
        """
        return self.get_dataset_count_by_month(date_param='dvobject__publicationdate')


    def get_dataset_counts_by_modification_date(self):
        """
        Get # of datasets modified each month

        Not great b/c only the last modified date is recorded
        """
        return self.get_dataset_count_by_month(date_param='dvobject__modificationtime')


    def get_dataset_count_by_month(self, date_param='dvobject__createdate', **extra_filters):
        """
        Return dataset counts by month
        """
        # Was an error found earlier?
        #
        if self.was_error_found():
            return self.get_error_msg_return()

        # -----------------------------------
        # (1) Build query filters
        # -----------------------------------

        # Exclude records where dates are null
        #   - e.g. a record may not have a publication date
        if date_param == 'dvobject__createdate':
            exclude_params = {}
        else:
            exclude_params = { '%s__isnull' % date_param : True}

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params()

        # Add extra filters from kwargs
        #
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        # -----------------------------------
        # (2) Construct query
        # -----------------------------------

        # add exclude filters date filters
        #
        ds_counts_by_month = Dataset.objects.select_related('dvobject'\
                            ).exclude(**exclude_params\
                            ).filter(**filter_params)

        # annotate query adding "month_yyyy_dd" and "cnt"
        #
        ds_counts_by_month = ds_counts_by_month.annotate(\
            month_yyyy_dd=TruncYearMonth('%s' % date_param)\
            ).values('month_yyyy_dd'\
            ).annotate(cnt=models.Count('dvobject_id')\
            ).values('month_yyyy_dd', 'cnt'\
            ).order_by('%smonth_yyyy_dd' % self.time_sort)

        print ds_counts_by_month.query

        # -----------------------------------
        # (3) Format results
        # -----------------------------------
        running_total = 0   # hold the running total count
        formatted_records = []  # move from a queryset to a []

        for d in ds_counts_by_month:
            # running total
            running_total += d['cnt']
            d['running_total'] = running_total

            # Add year and month numbers
            d['year_num'] = int(d['month_yyyy_dd'][0:4])
            month_num = int(d['month_yyyy_dd'][5:])
            d['month_num'] = month_num

            # Add month name
            month_name_found, month_name = get_month_name_abbreviation(month_num)
            if month_name_found:
                d['month_name'] = month_name
            else:
                # Log it!!!!!!
                pass

            # Add formatted record
            formatted_records.append(d)

        return True, formatted_records



    def get_dataverse_counts_by_month_unpublished(self):
        """
        Get # of --UNPUBLISHED-- datasets created each month
        """
        return self.get_dataverse_counts_by_month(**self.get_is_NOT_published_filter_param())


    def get_dataverse_counts_by_month_published(self):
        """
        Get # of --UNPUBLISHED-- datasets created each month
        """
        return self.get_dataverse_counts_by_month(**self.get_is_published_filter_param())


    def get_dataverse_counts_by_month(self, date_param='dvobject__createdate', **extra_filters):
        """
        Return Dataverse counts by month
        """
        # Was an error found earlier?
        #
        if self.was_error_found():
            return self.get_error_msg_return()

        # -----------------------------------
        # (1) Build query filters
        # -----------------------------------

        # Exclude records where dates are null
        #   - e.g. a record may not have a publication date
        exclude_params = { '%s__isnull' % date_param : True}

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params()

        # Add extra filters from kwargs
        #
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        # -----------------------------------
        # (2) Construct query
        # -----------------------------------

        # add exclude filters date filters
        #
        dv_counts_by_month = Dataverse.objects.select_related('dvobject'\
                            ).exclude(**exclude_params\
                            ).filter(**filter_params)

        # annotate query adding "month_yyyy_dd" and "cnt"
        #
        dv_counts_by_month = dv_counts_by_month.annotate(\
            month_yyyy_dd=TruncYearMonth('%s' % date_param)\
            ).values('month_yyyy_dd'\
            ).annotate(cnt=models.Count('dvobject_id')\
            ).values('month_yyyy_dd', 'cnt'\
            ).order_by('%smonth_yyyy_dd' % self.time_sort)

        #print (ds_counts_by_month)

        # -----------------------------------
        # (3) Format results
        # -----------------------------------
        running_total = 0   # hold the running total count
        formatted_records = []  # move from a queryset to a []

        for d in dv_counts_by_month:
            # running total
            running_total += d['cnt']
            d['running_total'] = running_total

            # Add year and month numbers
            d['year_num'] = int(d['month_yyyy_dd'][0:4])
            month_num = int(d['month_yyyy_dd'][5:])
            d['month_num'] = month_num

            # Add month name
            month_name_found, month_name = get_month_name_abbreviation(month_num)
            if month_name_found:
                d['month_name'] = month_name
            else:
                # Log it!!!!!!
                pass

            # Add formatted record
            formatted_records.append(d)

        return True, formatted_records

    def make_month_lookup(self, stats_queryset):
        """Make a dict from the 'stats_queryset' with a key of YYYY-MMDD"""

        d = {}
        for info in stats_queryset:
            d[info['month_yyyy_dd']] = info
        return d


    def create_month_year_iterator(self, create_date_info, pub_date_info):
        """
        Get the range of create and pub dates
        """
        #import ipdb; ipdb.set_trace()
        if len(pub_date_info) == 0:
            # No pub date, return create date ranges
            if len(create_date_info) == 1:
                # create start/end dates are the same
                first_date = create_date_info[0]
                last_date = first_date
            elif len(create_date_info) > 1:
                # different start/end dates
                first_date = create_date_info[0]
                last_date = create_date_info[-1]
            else:
                # no start/end dates for pub date or create date
                return None   # No pub date or create date info
        else:
            # We have a pub date and a create date
            first_date = min([create_date_info[0], pub_date_info[0]])
            last_date = max([create_date_info[-1], pub_date_info[-1]])

        return month_year_iterator(first_date['year_num'],\
                            first_date['month_num'],\
                            last_date['year_num'],\
                            last_date['month_num'],\
                            )

    def get_dataset_counts_by_create_date_and_pub_date(self):
        """INCOMPLETE - Combine create and publication date stats info"""

        if self.was_error_found():
            return self.get_error_msg_return()

        # (1) Get the stats for datasets *created* each month
        #
        success, create_date_info = self.get_dataset_counts_by_create_date()
        if not success:
            self.add_error('Failed to retrieve dataset counts by create date')

        # (2) Get the stats for datasets *published* each month
        #
        success, pub_date_info = self.get_dataset_counts_by_publication_date()
        if not success:
            self.add_error('Failed to retrieve dataset counts by publication date')

        # (3) Make dicts of these stats.  Key is YYYY-MMDD
        #
        create_date_dict = self.make_month_lookup(create_date_info)
        pub_date_dict = self.make_month_lookup(pub_date_info)

        # (4) Get list of months in YYYY-MMDD format to iterate through
        #
        month_iterator = self.create_month_year_iterator(create_date_info, pub_date_info)
        #import ipdb; ipdb.set_trace()
        #for yyyy, mm in
        #print 'pub_date_info', len(pub_date_info)

        #months_in_pub_only = set(pub_date_dict.keys()) - set(create_date_dict.keys())

        # Iterate through create_date_info
        formatted_dict = OrderedDict()
        formatted_list = []

        last_pub_running_total = 0
        for dataset_info in create_date_info:
            current_month = dataset_info['month_yyyy_dd']

            # Are there publication date numbers for this month?
            #
            pub_info = pub_date_dict.get(current_month, None)
            if pub_info:    # Yes, Add it to the create date dict
                dataset_info['pub_cnt'] = pub_info['cnt']
                dataset_info['pub_running_total'] = pub_info['running_total']
                last_pub_running_total = pub_info['running_total']
            else:           # No, Add last running total to the create date dict
                dataset_info['pub_cnt'] = 0    # No datasets published this month
                dataset_info['pub_running_total'] = last_pub_running_total

            formatted_dict[current_month] = dataset_info
            formatted_list.append(dataset_info)

        # NOT DONE - NEED TO CHECK for MISSING MONTHS ADD PUB ONLY MONTHS! by using month_iterator



        return True, formatted_list

    def get_downloads_by_month(self):
        """
        Using the GuestBookResponse object, find the number of file
        downloads per month
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        filter_params = self.get_date_filter_params(date_var_name='responsetime')
        filter_params['downloadtype'] = RESPONSE_TYPE_DOWNLOAD

        file_counts_by_month = GuestBookResponse.objects.filter(**filter_params\
            ).annotate(month_yyyy_dd=TruncYearMonth('responsetime')\
            ).values('month_yyyy_dd'\
            ).annotate(cnt=models.Count('guestbook_id')\
            ).values('month_yyyy_dd', 'cnt'\
            ).order_by('%smonth_yyyy_dd' % self.time_sort)

        formatted_records = []  # move from a queryset to a []
        file_running_total = 0
        for d in file_counts_by_month:
            file_running_total += d['cnt']
            d['running_total'] = file_running_total

            # Add year and month numbers
            d['year_num'] = int(d['month_yyyy_dd'][0:4])
            month_num = int(d['month_yyyy_dd'][5:])
            d['month_num'] = month_num

            # Add month name
            month_name_found, month_name = get_month_name_abbreviation(month_num)
            if month_name_found:
                d['month_name'] = month_name
            else:
                # Log it!!!!!!
                pass

            formatted_records.append(d)

        return True, formatted_records

    def get_dataverse_counts_by_type_published(self, exclude_uncategorized=True):
        """Return dataverse counts by 'dataversetype' for published dataverses"""

        return self.get_dataverse_counts_by_type(exclude_uncategorized,\
                **self.get_is_published_filter_param())


    def get_dataverse_counts_by_type_unpublished(self, exclude_uncategorized=True):
        """Return dataverse counts by 'dataversetype' for unpublished dataverses"""

        return self.get_dataverse_counts_by_type(exclude_uncategorized,\
                **self.get_is_NOT_published_filter_param())


    def get_dataverse_counts_by_type(self, exclude_uncategorized=True, **extra_filters):
        """
        Return dataverse counts by 'dataversetype'

        Optional if a dataverse is uncategorized:
            - Specifying 'uncategorized_replacement_name' will
                set "UNCATEGORIZED" to another string

        Returns: { "dv_counts_by_type": [
                        {
                            "total_count": 356,
                            "dataversetype": "RESEARCH_PROJECTS",
                            "type_count": 85,
                            "percent_string": "23.9%"
                        },
                        {
                            "total_count": 356,
                            "dataversetype": "TEACHING_COURSES",
                            "type_count": 10,
                            "percent_string": "2.8%"
                        }
                            ... etc
                    ]
                }
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params('dvobject__createdate')

        # Add extra filters
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        if exclude_uncategorized:
            exclude_params = dict(dataversetype=DATAVERSE_TYPE_UNCATEGORIZED)
        else:
            exclude_params = {}

        dataverse_counts_by_type = Dataverse.objects.select_related('dvobject'\
                    ).filter(**filter_params\
                    ).exclude(**exclude_params\
                    ).values('dataversetype'\
                    ).order_by('dataversetype'\
                    ).annotate(type_count=models.Count('dataversetype')\
                    ).order_by('-type_count')

        # Count all dataverses
        #
        total_count = sum([rec.get('type_count', 0) for rec in dataverse_counts_by_type])
        total_count = total_count + 0.0

        # Format the records, adding 'total_count' and 'percent_string' to each one
        #
        formatted_records = []
        for rec in dataverse_counts_by_type:

            if total_count > 0:
                float_percent = rec.get('type_count', 0) / total_count
                rec['percent_string'] = '{0:.1%}'.format(float_percent)
                rec['total_count'] = int(total_count)

            rec['dataversetype_label'] = rec['dataversetype'].replace('_', ' ')

            formatted_records.append(rec)

        return True, formatted_records

    def get_dataverse_affiliation_counts(self):
        """
        Return dataverse counts by 'affiliation'

        Returns: dv_counts_by_affiliation": [
            {
                "affiliation": "University of Oxford",
                "affil_count": 2,
                "total_count": 191,
                "percent_string": "1.0%"
            },
            {
                "affiliation": "University of Illinois",
                "affil_count": 1,
                "total_count": 191,
                "percent_string": "0.5%"
            }
            ...
        ]
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params('dvobject__createdate')

        dataverse_counts_by_affil = Dataverse.objects.select_related('dvobject'\
                    ).filter(**filter_params\
                    ).values('affiliation'\
                    ).order_by('affiliation'\
                    ).annotate(affil_count=models.Count('affiliation')\
                    ).order_by('-affil_count')

        # Count all dataverses
        #
        total_count = sum([rec.get('affil_count', 0) for rec in dataverse_counts_by_affil])
        total_count = total_count + 0.0

        # Format the records, adding 'total_count' and 'percent_string' to each one
        #
        formatted_records = []
        for rec in dataverse_counts_by_affil:

            if total_count > 0:
                float_percent = rec.get('affil_count', 0) / total_count
                rec['percent_string'] = '{0:.1%}'.format(float_percent)
                rec['total_count'] = int(total_count)

            formatted_records.append(rec)

        return True, formatted_records

    '''
    def get_number_of_datafile_types(self):
        """Return the number of distinct contenttypes found in Datafile objects"""
        if self.was_error_found():
            return self.get_error_msg_return()

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params('dvobject__createdate')

        datafile_counts_by_type = Datafile.objects.select_related('dvobject'\
                    ).filter(**filter_params\
                    ).values('contenttype'\
                    ).distinct().count()

        return True, dict(datafile_counts_by_type=datafile_counts_by_type)
    '''

    def get_datafile_content_type_counts_published(self):
        """Return datafile counts by 'content type' for published files"""

        return self.get_datafile_content_type_counts(\
            **self.get_is_published_filter_param())

    def get_datafile_content_type_counts_unpublished(self):
        """Return datafile counts by 'content type' for unpublished files"""

        return self.get_datafile_content_type_counts(\
            **self.get_is_NOT_published_filter_param())

    def get_datafile_content_type_counts(self, **extra_filters):
        """
        Return datafile counts by 'content type'

        "datafile_content_type_counts": [
                {
                    "total_count": 1584,
                    "contenttype": "text/tab-separated-values",
                    "type_count": 187,
                    "percent_string": "11.8%"
                },
                {
                    "total_count": 1584,
                    "contenttype": "image/jpeg",
                    "type_count": 182,
                    "percent_string": "11.5%"
                },
                {
                    "total_count": 1584,
                    "contenttype": "text/plain",
                    "type_count": 147,
                    "percent_string": "9.3%"
                }
            ]
        """
        if self.was_error_found():
            return self.get_error_msg_return()

        # Retrieve the date parameters
        #
        filter_params = self.get_date_filter_params('dvobject__createdate')

        # Add extra filters
        if extra_filters:
            for k, v in extra_filters.items():
                filter_params[k] = v

        datafile_counts_by_type = Datafile.objects.select_related('dvobject'\
                    ).filter(**filter_params\
                    ).values('contenttype'\
                    ).order_by('contenttype'\
                    ).annotate(type_count=models.Count('contenttype')\
                    ).order_by('-type_count')

        # Count all dataverses
        #
        total_count = sum([rec.get('type_count', 0) for rec in datafile_counts_by_type])
        total_count = total_count + 0.0

        # Format the records, adding 'total_count' and 'percent_string' to each one
        #
        formatted_records = []
        #num = 0
        for rec in datafile_counts_by_type:

            if total_count > 0:
                float_percent = rec.get('type_count', 0) / total_count
                rec['percent_string'] = '{0:.1%}'.format(float_percent)
                rec['total_count'] = int(total_count)
                #num+=1
                #rec['num'] = num
            formatted_records.append(rec)

        return True, formatted_records

    def get_files_per_dataset(self):
        """
        To do
        """

        # Pull file counts under each dataset
        files_per_dataset = DvObject.objects.filter(dtype=DTYPE_DATAFILE\
                    ).filter(**filter_params\
                    ).values('owner'\
                    ).annotate(parent_count=models.Count('owner')\
                    ).order_by('-parent_count')

        # Bin this data
