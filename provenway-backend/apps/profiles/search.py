"""Directory search helpers (Session 12 — GET /api/v1/users/).

Two independent concerns live here:

1. Full-text search vector maintenance (`update_search_vector`) — keeps
   `Profile.search_vector` in sync so the GIN index can be used instead of
   an unindexed per-request scan.
2. Geographic radius search (`annotate_distance_km` / `bounding_box`) —
   plain Haversine distance over `Profile.location_lat/lng`, no PostGIS
   dependency since the project doesn't have that extension provisioned.
"""

import math

from django.db import connection
from django.db.models import ExpressionWrapper, F, FloatField, QuerySet
from django.db.models.functions import ACos, Cast, Cos, Radians, Sin

EARTH_RADIUS_KM = 6371.0

# Weighting: the professional's own name matters most for a "find this
# person" search, then their headline/firm (what they do, where), then the
# free-text bio, then raw location text (least specific — lots of profiles
# share a city).
SEARCH_CONFIG = "english"

# Raw SQL, not the ORM, because this vector spans two tables (profiles +
# users via the one-to-one) and Django's QuerySet.update() explicitly
# forbids joined-field references on the right-hand side of a SET clause
# ("Joined field references are not permitted in this query"). A plain
# UPDATE ... FROM is the standard Postgres way to do a cross-table set,
# and it's exactly what the GIN-indexed tsvector column is designed for.
_UPDATE_SEARCH_VECTOR_SQL = """
    UPDATE profiles
    SET search_vector =
        setweight(to_tsvector(%(config)s, coalesce(u.display_name, '')), 'A')
        || setweight(to_tsvector(%(config)s, coalesce(u.headline, '')), 'B')
        || setweight(to_tsvector(%(config)s, coalesce(profiles.firm_name, '')), 'B')
        || setweight(to_tsvector(%(config)s, coalesce(profiles.bio, '')), 'C')
        || setweight(to_tsvector(%(config)s, coalesce(profiles.location_text, '')), 'D')
    FROM users u
    WHERE u.id = profiles.user_id AND profiles.id = %(profile_id)s
"""


def update_search_vector(profile_id) -> None:
    """Recompute and persist search_vector for a single profile.

    Called from apps.profiles.signals after every Profile save and after
    every User save (display_name/headline live on User, not Profile —
    see Profile.search_vector's docstring). A raw UPDATE rather than
    instance.save() so this never re-fires Profile's post_save signal
    (which is what calls this in the first place) and recurses.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            _UPDATE_SEARCH_VECTOR_SQL,
            {"config": SEARCH_CONFIG, "profile_id": str(profile_id)},
        )


def bounding_box(lat: float, lng: float, radius_km: float) -> dict:
    """Cheap pre-filter box so the indexed location_lat/location_lng
    B-tree can narrow the row set before the more expensive Haversine
    computation runs on the (much smaller) remainder.
    """
    lat_delta = radius_km / 111.0  # ~111km per degree of latitude
    # Degrees of longitude per km shrinks toward the poles; guard against
    # division by ~0 near lat=90 with a floor on the cosine term.
    lng_delta = radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))
    return {
        "lat_min": lat - lat_delta,
        "lat_max": lat + lat_delta,
        "lng_min": lng - lng_delta,
        "lng_max": lng + lng_delta,
    }


def annotate_distance_km(queryset: QuerySet, lat: float, lng: float) -> QuerySet:
    """Annotate each row with `distance_km` — great-circle distance from
    (lat, lng) to the profile's location, via the standard Haversine
    formula. location_lat/lng are DecimalField, so they're cast to float
    before the trig functions run (Postgres's trig functions operate on
    double precision, not numeric).
    """
    profile_lat_rad = Radians(Cast(F("location_lat"), FloatField()))
    profile_lng_rad = Radians(Cast(F("location_lng"), FloatField()))

    # The query point's lat/lng are plain Python floats (not DB columns),
    # so their radians/cos/sin are computed once in Python rather than
    # round-tripped through Django Func nodes — cos_query_lat * Cos(...)
    # still builds a valid SQL expression, since Combinable supports a
    # plain number on the left of `*`/`-` against an expression on the
    # right.
    query_lat_rad = math.radians(lat)
    query_lng_rad = math.radians(lng)
    cos_query_lat = math.cos(query_lat_rad)
    sin_query_lat = math.sin(query_lat_rad)

    distance_expr = ExpressionWrapper(
        EARTH_RADIUS_KM
        * ACos(
            cos_query_lat * Cos(profile_lat_rad) * Cos(profile_lng_rad - query_lng_rad)
            + sin_query_lat * Sin(profile_lat_rad)
        ),
        output_field=FloatField(),
    )
    return queryset.annotate(distance_km=distance_expr)
