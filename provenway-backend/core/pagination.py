from rest_framework.pagination import CursorPagination, PageNumberPagination


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    max_page_size = 50
    ordering = "-created_at"
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"


class DefaultOffsetPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"
