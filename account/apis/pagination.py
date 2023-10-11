from rest_framework import pagination
from rest_framework import status
from rest_framework.response import Response
from account.apis import messages
from account.models import User


class CustomPagination(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "p"
    ordering = "id"

    def get_ordering(self, request):
        ordering = request.query_params.get("ordering", "id")

        valid_ordering_fields = [
            "project__project_name",
            "permission__emp_id",
            "status",
            "users__username",
            "fullName" "id",
        ]
        if ordering.lstrip("-") not in valid_ordering_fields:
            ordering = "id"

        return ordering

    def paginate_queryset(self, queryset, request, view=None):
        ordering = self.get_ordering(request)
        queryset = queryset.order_by(ordering)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        prev_url = self.get_previous_link()
        ordering = self.get_ordering(self.request)

        return Response(
            {
                "count": self.page.paginator.count,
                "next": next_url,
                "previous": prev_url,
                "results": data,
                "ordering": ordering,
            }
        )


class PaginationHandlerMixin(object):
    pagination_class = CustomPagination

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        page = self.paginator.page
        page_size = self.paginator.get_page_size(self.request)
        offset = (page.number - 1) * page_size
        total_items = page.paginator.count
        total_pages = page.paginator.num_pages
        current_page = page.number
        previous_page = current_page - 1 if current_page > 1 else None
        next_page = current_page + 1 if current_page < total_pages else None
        return Response(
            {
                "message": messages.get_success_message(),
                "error": False,
                "code": 200,
                "result": data,
                "pagination": {
                    "total_items": total_items,
                    "total_pages": total_pages,
                    "current_page": current_page,
                    "offset": offset,
                    "limit": page_size,
                    "next": next_page,
                    "previous": previous_page,
                },
            },
            status=status.HTTP_200_OK,
        )
        
        
