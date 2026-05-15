from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    # Keeps product list responses to 6 items and adds count/next/previous links.
    page_size = 6
