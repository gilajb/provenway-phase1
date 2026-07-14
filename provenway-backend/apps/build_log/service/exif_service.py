"""EXIF extraction for uploaded build log photos (FR-LOG-03, "Should").

Runs synchronously inside the request/response cycle rather than as a
Celery task — matches how apps.profiles' avatar upload is handled
synchronously in this codebase today (no Celery wiring exists yet for
build_log). Worth revisiting as a Celery task per Engineering Doc §4.5
(`process_image_metadata`) once Celery is wired up for this app.
"""

from PIL import ExifTags, Image


def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (tuple, list)):
        return [_json_safe(v) for v in value]
    return str(value)


def extract_exif(file_obj) -> dict | None:
    """Best-effort EXIF extraction. Returns None if no EXIF is present or
    the file can't be decoded — this is a "Should", not a "Must", so
    failures here must never block the upload itself.
    """
    try:
        file_obj.seek(0)
        image = Image.open(file_obj)
        raw_exif = image.getexif()
    except Exception:
        return None
    finally:
        try:
            file_obj.seek(0)
        except Exception:
            pass

    if not raw_exif:
        return None

    exif = {}
    for tag_id, value in raw_exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        exif[tag_name] = _json_safe(value)

    return exif or None
