from rest_framework.pagination import CursorPagination


class ProductCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = ('-created_at', '-id')

    allowed_ordering = {
        'price': ('price', 'id'),
        '-price': ('-price', '-id'),
        'created_at': ('created_at', 'id'),
        '-created_at': ('-created_at', '-id'),
    }

    def get_ordering(self, request, queryset, view):
        ordering = request.query_params.get('ordering')

        return self.allowed_ordering.get(
            ordering,
            self.ordering,
        )
