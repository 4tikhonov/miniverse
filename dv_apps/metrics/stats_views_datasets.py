from .stats_view_base import StatsViewSwagger
from .stats_util_datasets import StatsMakerDatasets



class DatasetTotalCounts(StatsViewSwagger):
    """API View - Total count of all Dataverses"""

    # Define the swagger attributes
    # Note: api_path must match the path in urls.py
    #
    api_path = '/datasets/count'
    summary = ('Simple count of published Datasets')
    description = ('Returns number of published Datasets')
    description_200 = 'Number of published Datasets'
    param_names = StatsViewSwagger.UNPUBLISHED_PARAMS + StatsViewSwagger.PRETTY_JSON_PARAM
    tags = [StatsViewSwagger.TAG_DATASETS]

    def get_stats_result(self, request):
        """Return the StatsResult object for this statistic"""
        stats_datasets = StatsMakerDatasets(**request.GET.dict())

        if self.is_published_and_unpublished(request):
            stats_result = stats_datasets.get_dataset_count()
        elif self.is_unpublished(request):
            stats_result = stats_datasets.get_dataset_count_unpublished()
        else:
            stats_result = stats_datasets.get_dataset_count_published()

        return stats_result


class DatasetCountByMonthView(StatsViewSwagger):
    """API View - Published Dataset counts by Month"""

    # Define the swagger attributes
    # Note: api_path must match the path in urls.py
    #
    api_path = '/datasets/count/monthly'
    summary = ('Number of published Datasets by'
            ' the month they were created*.  (*'
            ' Not month published)')
    description = ('Returns a list of counts and'
            ' cumulative counts of all datasts added in a month')
    description_200 = 'A list of Dataset counts by month'
    tags = [StatsViewSwagger.TAG_DATASETS]


    def get_stats_result(self, request):
        """Return the StatsResult object for this statistic"""
        stats_datasets = StatsMakerDatasets(**request.GET.dict())

        if self.is_published_and_unpublished(request):
            stats_result = stats_datasets.get_dataset_counts_by_create_date()
        elif self.is_unpublished(request):
            stats_result = stats_datasets.get_dataset_counts_by_create_date_unpublished()
        else:
            stats_result = stats_datasets.get_dataset_counts_by_create_date_published()

        return stats_result
