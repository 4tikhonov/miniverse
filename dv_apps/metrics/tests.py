"""
Tests for the metrics functions.
Note: This loads 10,000+ objects and uses them for all of the tests

Example of calling a single test:
python manage.py test dv_apps.metrics.tests.MetricsCountTests.test_date_params

"""
from __future__ import print_function

from dv_apps.metrics.metrics_test_base import MetricsTestBase

from dv_apps.metrics.stats_util_dataverses import StatsMakerDataverses
from dv_apps.metrics.stats_util_datasets import StatsMakerDatasets
from dv_apps.metrics.stats_util_files import StatsMakerFiles



class MetricsCountTests(MetricsTestBase):
    """
    Test metrics from StatsMakerDataverses
    Note: MetricsTestBase loads 10k+ objects from fixtures
    """

    def try_data_params(self, **params):
        """Used for checking date param logic"""

        stats_maker = StatsMakerDataverses(**params)
        r = stats_maker.get_dataverse_count_published()
        return r


    def test_date_params(self):
        """Test date params"""
        # Note: All date param checking is in parent class StatsMakerBase
        #   e.g. it's the same in:
        #     StatsMakerDataverses, StatsMakerDatasets, and StatsMakerFiles
        #

        # Year cannot be zero
        kwargs = dict(selected_year=0)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year cannot be zero.')

        # Year cannot be negative
        kwargs = dict(selected_year=-1)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year must be digits.')

        kwargs = dict(selected_year='-1')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year must be digits.')

        # Year cannot be a 'dog'
        kwargs = dict(selected_year='dog')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year must be digits.')

        # Year CAN be 9999
        kwargs = dict(selected_year=9999)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), False)

        # Not more than 4-digit year
        kwargs = dict(selected_year=10000)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year cannot be more than 4-digits (YYYY)')

        # Not more than 4-digit year (as a string)
        kwargs = dict(selected_year='10000')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The year cannot be more than 4-digits (YYYY)')

        # Bad year - '123'
        kwargs = dict(start_date='123-02-01')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'Start date is invalid.  Use YYYY-MM-DD format.')

        # Bad year - '0000'
        kwargs = dict(start_date='0000-02-1')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'Start date is invalid.  Use YYYY-MM-DD format.')

        # OK year - '0001', with day '1'
        kwargs = dict(start_date='0001-02-1')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), False)

        # Bad day.  31st day of Feb
        kwargs = dict(start_date='1968-02-31')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'Start date is invalid.  Use YYYY-MM-DD format.')

        # End date (uses same function as start date check)
        # Bad day. 14th month
        kwargs = dict(end_date='1968-14-01')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'End date is invalid.  Use YYYY-MM-DD format.')

        # OK - start day / end day
        kwargs = dict(start_date='2000-01-01',\
                    end_date='2000-01-02')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), False)

        # OK - start day / end day - same day
        kwargs = dict(start_date='2000-01-01',\
                    end_date='2000-01-01')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), False)

        # Bad - start day / end day
        kwargs = dict(start_date='2010-01-01',\
                    end_date='1968-12-01')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The start date cannot be after the end date.')

        # Bad - start day / end day
        kwargs = dict(start_date='2010-01-02',\
                    end_date='2010-01-01')
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, 'The start date cannot be after the end date.')

        # Bad selected_year, start_date combo
        kwargs = dict(start_date='2015-01-02',\
                    selected_year=2014)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, "The 'selected_year' (2014)' cannot be before the 'start_date' year (2015-01-02)")

        # OK selected_year, start_date combo. selected_year not needed, but ok
        kwargs = dict(start_date='2015-03-02',\
                    selected_year=2015)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), False)

        # Bad selected_year, end_date combo
        kwargs = dict(end_date='2012-01-02',\
                    selected_year=2014)
        r = self.try_data_params(**kwargs)
        self.assertEqual(r.has_error(), True)
        self.assertEqual(r.error_message, "The 'selected_year' (2014)' cannot be after the 'end_date' year (2012-01-02)")


    def test_01_dataverse_total_counts(self):
        """Count total dataverses: published, unpublished, all"""
        print ('Count total dataverses: published, unpublished, all')

        stats_maker = StatsMakerDataverses()

        # Count published dataverse
        r = stats_maker.get_dataverse_count_published()
        self.assertEqual(r.result_data, 187)

        # Count unpublished dataverse
        r = stats_maker.get_dataverse_count_unpublished()
        self.assertEqual(r.result_data, 169)

        # Count all dataverses
        r = stats_maker.get_dataverse_count()
        self.assertEqual(r.result_data, 356)



    def test_02_dataverse_counts_by_month_published(self):
        """Test published dataverse counts by month"""
        print ('Test published dataverse counts by month')

        kwargs=dict(selected_year=2016)
        stats_maker = StatsMakerDataverses(**kwargs)

        r = stats_maker.get_dataverse_counts_by_month_published()

        # check number of months
        self.assertEqual(len(r.result_data), 7)

        # check 1st month
        first_month = {'cnt': 5,
         'month_name': 'Jan',
         'month_num': 1,
         'running_total': 131,
         'year_num': 2016,
         'yyyy_mm': '2016-01'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 4,
             'month_name': 'Jul',
             'month_num': 7,
             'running_total': 187,
             'year_num': 2016,
             'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)



    def test_03_dataverse_counts_by_month_unpublished(self):
        """Test unpublished dataverse counts by month"""
        print ('Test unpublished dataverse counts by month')

        stats_maker = StatsMakerDataverses()

        r = stats_maker.get_dataverse_counts_by_month_unpublished()

        # check number of months
        self.assertEqual(len(r.result_data), 16)

        # check 1st month
        first_month = {'cnt': 13,
             'month_name': 'Apr',
             'month_num': 4,
             'running_total': 13,
             'year_num': 2015,
             'yyyy_mm': '2015-04'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 6,
             'month_name': 'Jul',
             'month_num': 7,
             'running_total': 169,
             'year_num': 2016,
             'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)


    def test_04_dataverse_counts_by_month_all(self):
        """Test all dataverse counts by month"""
        print ('Test all dataverse counts by month')

        stats_maker = StatsMakerDataverses()

        r = stats_maker.get_dataverse_counts_by_month()

        # check number of months
        self.assertEqual(len(r.result_data), 16)

        # check 1st month
        first_month = {'cnt': 39,
             'month_name': 'Apr',
             'month_num': 4,
             'running_total': 39,
             'year_num': 2015,
             'yyyy_mm': '2015-04'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 10,
             'month_name': 'Jul',
             'month_num': 7,
             'running_total': 356,
             'year_num': 2016,
             'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)

    def test_05_dataset_total_counts(self):
        """Count total datasets: published, unpublished, all"""
        print ('Count total datasets: published, unpublished, all')

        kwargs=dict(start_date='2016-01-01')
        stats_maker = StatsMakerDatasets(**kwargs)

        # Count published dataset
        r = stats_maker.get_dataset_count_published()
        self.assertEqual(r.result_data, 85)

        # Count unpublished dataset
        r = stats_maker.get_dataset_count_unpublished()
        self.assertEqual(r.result_data, 198)

        # Count all datasets
        r = stats_maker.get_dataset_count()
        self.assertEqual(r.result_data, 283)


    def test_06_dataset_counts_published(self):
        """Test published dataset counts by month"""
        print ('Test published dataset counts by month')

        stats_maker = StatsMakerDatasets()

        r = stats_maker.get_dataset_counts_by_create_date_published()

        # check number of months
        self.assertEqual(len(r.result_data), 16)

        # check 1st month
        first_month = {'cnt': 21,
         'month_name': 'Apr',
         'month_num': 4,
         'running_total': 21,
         'year_num': 2015,
         'yyyy_mm': '2015-04'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 4,
         'month_name': 'Jul',
         'month_num': 7,
         'running_total': 227,
         'year_num': 2016,
         'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)

    def test_07_dataset_counts_unpublished(self):
        """Test unpublished dataset counts by month"""
        print ('Test unpublished dataset counts by month')

        stats_maker = StatsMakerDatasets()

        r = stats_maker.get_dataset_counts_by_create_date_unpublished()

        # check number of months
        self.assertEqual(len(r.result_data), 16)

        # check 1st month
        first_month = {'cnt': 15,
         'month_name': 'Apr',
         'month_num': 4,
         'running_total': 15,
         'year_num': 2015,
         'yyyy_mm': '2015-04'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 94,
             'month_name': 'Jul',
             'month_num': 7,
             'running_total': 343,
             'year_num': 2016,
             'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)

    def test_08_dataset_counts_all(self):
        """Test all dataset counts by month"""
        print ('Test all dataset counts by month')

        stats_maker = StatsMakerDatasets()

        r = stats_maker.get_dataset_counts_by_create_date()

        # check number of months
        self.assertEqual(len(r.result_data), 16)

        # check 1st month
        first_month = {'cnt': 36,
             'month_name': 'Apr',
             'month_num': 4,
             'running_total': 36,
             'year_num': 2015,
             'yyyy_mm': '2015-04'}
        self.assertEqual(r.result_data[0], first_month)

        # check last month
        last_month = {'cnt': 98,
             'month_name': 'Jul',
             'month_num': 7,
             'running_total': 570,
             'year_num': 2016,
             'yyyy_mm': '2016-07'}
        self.assertEqual(r.result_data[-1], last_month)


    def test_09_file_total_counts(self):
        """Count total files: published, unpublished, all"""
        print ('Count total files: published, unpublished, all')

        stats_maker = StatsMakerFiles()

        # Count published file
        r = stats_maker.get_datafile_count_published()
        self.assertEqual(r.result_data, 1014)

        # Count unpublished file
        r = stats_maker.get_datafile_count_unpublished()
        self.assertEqual(r.result_data, 570)

        # Count all files
        r = stats_maker.get_datafile_count()
        self.assertEqual(r.result_data, 1584)

    def test_10_file_downloads_by_month_published(self):
        """File downloads by month: published,"""
        print ('File downloads by month: published')

        kwargs = dict(start_date='2015-05-30',\
                    end_date='2015-10-01')
        stats_maker = StatsMakerFiles(**kwargs)

        r = stats_maker.get_file_downloads_by_month_published()

        # check number of months
        self.assertEqual(len(r.result_data), 4)

        # check last month
        last_month = {'cnt': 6,
             'month_name': 'Sep',
             'month_num': 9,
             'running_total': 125,
             'year_num': 2015,
             'yyyy_mm': '2015-09'}
        self.assertEqual(r.result_data[-1], last_month)


    def test_10_file_downloads_by_month_unpublished(self):
        """File downloads by month: unpublished,"""
        print ('File downloads by month: unpublished')

        kwargs = dict(start_date='2015-02-01',\
                    end_date='2015-11-01')

        stats_maker = StatsMakerFiles(**kwargs)
        r = stats_maker.get_file_downloads_by_month_unpublished()

        # check number of months
        self.assertEqual(len(r.result_data), 0)

        # check data -- very rare to have downloaded "unpublished" files
        self.assertEqual(r.result_data, [])

    def test_12_file_downloads_by_month_all(self):
        """File downloads by month: all"""
        print ('File downloads by month: all')

        kwargs = dict(selected_year=2015)
        stats_maker = StatsMakerFiles(**kwargs)
        r = stats_maker.get_file_downloads_by_month()

        # check number of months
        self.assertEqual(len(r.result_data), 9)

        # check last month
        last_month = {'cnt': 22,
             'month_name': 'Dec',
             'month_num': 12,
             'running_total': 237,
             'year_num': 2015,
             'yyyy_mm': '2015-12'}
        self.assertEqual(r.result_data[-1], last_month)
