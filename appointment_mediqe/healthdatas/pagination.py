from rest_framework.pagination import PageNumberPagination

class HealthDataPagination(PageNumberPagination):
    page_size = 10 # number of data in a page
    page_size_query_param = 'page_size'  # allow user to override via query param
    max_page_size = 100  # prevent abuse of large page sizes