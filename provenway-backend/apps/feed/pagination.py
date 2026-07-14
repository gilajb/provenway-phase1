import base64

from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class FeedCursorPagination(BasePagination):
    """Cursor pagination for GET /api/v1/feed/, keyed on (created_at, id).

    Engineering Doc §5.1: feeds are cursor-based (unlike search, which is
    offset-based) specifically so new updates posted mid-scroll don't
    shift page boundaries and cause skipped or duplicated entries.

    This is a hand-rolled keyset implementation rather than a subclass of
    rest_framework.pagination.CursorPagination, despite core.pagination
    already having a DefaultCursorPagination: DRF's CursorPagination only
    encodes *one* ordering field's value into the cursor position (its
    paginate_queryset reads `self.ordering[0]` alone when building the
    `__lt`/`__gt` filter — the rest of an `ordering` tuple only affects
    the SQL ORDER BY, not what the cursor remembers). Two updates sharing
    the exact same `created_at` — which does happen with fast successive
    writes, and easily happens in tests — would still be at risk of being
    skipped or duplicated across a page boundary with that approach. This
    class encodes both `created_at` and `id` in the cursor and filters
    with `created_at < cursor.created_at OR (created_at == cursor's AND
    id < cursor.id)`, which is a strict "not yet seen" filter regardless
    of timestamp collisions. `id` is a UUID here and carries no
    chronological meaning of its own — it's purely a tiebreaker to make
    the ordering total.
    """

    page_size = 20
    max_page_size = 50
    page_size_query_param = "page_size"
    cursor_query_param = "cursor"

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.page_size = self._get_page_size(request)

        cursor = self._decode_cursor(request.query_params.get(self.cursor_query_param))
        qs = queryset.order_by("-created_at", "-id")

        if cursor is not None:
            cursor_created_at, cursor_id = cursor
            qs = qs.filter(
                Q(created_at__lt=cursor_created_at)
                | Q(created_at=cursor_created_at, id__lt=cursor_id)
            )

        # Fetch one extra row to know whether there's a next page without
        # a separate COUNT query.
        page_plus_one = list(qs[: self.page_size + 1])
        self.has_next = len(page_plus_one) > self.page_size
        self.page = page_plus_one[: self.page_size]
        return self.page

    def get_paginated_response(self, data):
        return Response(
            {
                "results": data,
                "next_cursor": self._next_cursor(),
                "has_next": self.has_next,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "results": schema,
                "next_cursor": {"type": "string", "nullable": True},
                "has_next": {"type": "boolean"},
            },
        }

    def _next_cursor(self):
        if not self.has_next or not self.page:
            return None
        last = self.page[-1]
        return self._encode_cursor(last.created_at, last.id)

    def _get_page_size(self, request):
        if self.page_size_query_param:
            raw = request.query_params.get(self.page_size_query_param)
            if raw:
                try:
                    size = int(raw)
                except (TypeError, ValueError):
                    size = None
                if size and size > 0:
                    return min(size, self.max_page_size)
        return self.page_size

    @staticmethod
    def _encode_cursor(created_at, id_) -> str:
        raw = f"{created_at.isoformat()}|{id_}"
        return base64.urlsafe_b64encode(raw.encode()).decode()

    @staticmethod
    def _decode_cursor(raw_cursor):
        if not raw_cursor:
            return None
        try:
            decoded = base64.urlsafe_b64decode(raw_cursor.encode()).decode()
            ts_part, id_part = decoded.rsplit("|", 1)
        except (ValueError, UnicodeDecodeError, TypeError):
            return None

        dt = parse_datetime(ts_part)
        if dt is None or not id_part:
            # Invalid/garbled cursor — fail open to "start of feed" rather
            # than erroring, same tolerance a malformed offset param gets
            # from DRF's own pagination classes.
            return None
        return dt, id_part
