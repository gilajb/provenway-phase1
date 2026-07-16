"""Generates a PDF portfolio of a project's full build log (Engineering
Doc §1.4.2 / build-plan Track H): title, chronological updates with
photos, and a QR code linking back to the live page.

Uses reportlab, not WeasyPrint — WeasyPrint's native GTK3/Cairo runtime
has no pip-installable wheel and is a well-known pain point on Windows
(this repo's dev environment, per CLAUDE.md), whereas reportlab is
pure-Python with prebuilt wheels. The tradeoff: layout is built from
reportlab's Platypus flowables (Paragraph/Image/Spacer) rather than
HTML/CSS, so a handful of docs/DESIGN.md's tokens are hand-ported below
as constants instead of reused from tokens.css, and the Inter font files
are bundled locally (apps/build_log/static/fonts/) since neither
reportlab nor the PDF format itself can load web fonts.
"""
import io
import os
import re
from xml.sax.saxutils import escape as xml_escape

import requests
from django.conf import settings
from django.utils.html import strip_tags
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

from .qr_service import generate_qr_png

# docs/DESIGN.md — "Architectural Precision" palette. Hand-ported since
# reportlab has no CSS/tokens.css integration.
COLOR_PRIMARY = colors.HexColor("#002e59")
COLOR_PRIMARY_CONTAINER = colors.HexColor("#0c447c")
COLOR_ON_SURFACE = colors.HexColor("#1b1c1a")
COLOR_ON_SURFACE_VARIANT = colors.HexColor("#424750")

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "fonts")
_fonts_registered = False


def _ensure_fonts_registered():
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont("Inter", os.path.join(FONT_DIR, "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Bold", os.path.join(FONT_DIR, "Inter-Bold.ttf")))
    _fonts_registered = True


def _build_styles():
    # `leading` is set explicitly on every style rather than left to
    # reportlab's auto-leading (fontSize * 1.2): the bundled Inter TTFs
    # are static instances sliced from a variable font (see
    # apps/build_log/static/fonts/), and their hhea/OS2 ascent/descent
    # metrics produced a near-zero computed leading — paragraphs were
    # rendering stacked on top of each other instead of stacked
    # vertically. Explicit leading sidesteps relying on those metrics.
    return {
        "title": ParagraphStyle(
            "title", fontName="Inter-Bold", fontSize=24, leading=29,
            textColor=COLOR_PRIMARY, spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "meta", fontName="Inter", fontSize=10, leading=13,
            textColor=COLOR_ON_SURFACE_VARIANT, spaceAfter=16,
        ),
        "qr_caption": ParagraphStyle(
            "qr_caption", fontName="Inter", fontSize=8, leading=10,
            textColor=COLOR_ON_SURFACE_VARIANT, alignment=TA_CENTER, spaceBefore=2,
        ),
        "entry_title": ParagraphStyle(
            "entry_title", fontName="Inter-Bold", fontSize=14, leading=17,
            textColor=COLOR_PRIMARY_CONTAINER, spaceBefore=16, spaceAfter=2,
        ),
        "entry_meta": ParagraphStyle(
            "entry_meta", fontName="Inter", fontSize=9, leading=12,
            textColor=COLOR_ON_SURFACE_VARIANT, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontName="Inter", fontSize=10.5, leading=15,
            textColor=COLOR_ON_SURFACE, spaceAfter=8,
        ),
    }


# ProjectUpdate.body is bleach-sanitized HTML (see
# apps.build_log.models.ALLOWED_BODY_TAGS: p/br/strong/em/u/s/ul/ol/li/
# h3/h4/blockquote/a/code/pre) — reportlab's Paragraph only understands
# its own small XML-like markup subset (b/i/u/br/font/...), not those
# block tags, so they're converted to line breaks and everything else is
# stripped to plain text before being re-escaped for Paragraph.
_BLOCK_CLOSE_TAGS_RE = re.compile(r"</(p|li|h3|h4|blockquote|pre)>", re.IGNORECASE)
_BR_TAG_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def _html_to_paragraph_markup(html: str) -> str:
    if not html:
        return ""
    text = _BLOCK_CLOSE_TAGS_RE.sub("\n", html)
    text = _BR_TAG_RE.sub("\n", text)
    text = strip_tags(text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line)
    return xml_escape(text).replace("\n", "<br/>")


def _fetch_image_flowable(url: str, max_width=150 * mm, max_height=90 * mm):
    """Downloads a Cloudinary-hosted photo and returns a sized Image
    flowable, or None if the fetch fails — a broken/slow photo shouldn't
    fail the whole export.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image(io.BytesIO(response.content))
    except Exception:
        return None

    ratio = min(max_width / img.imageWidth, max_height / img.imageHeight, 1)
    img.drawWidth = img.imageWidth * ratio
    img.drawHeight = img.imageHeight * ratio
    return img


def build_portfolio_pdf(project) -> bytes:
    """Renders `project`'s full build log to PDF bytes."""
    _ensure_fonts_registered()
    styles = _build_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"{project.title} — Provenway Build Log",
    )

    story = [Paragraph(xml_escape(project.title), styles["title"])]

    meta_bits = [project.get_status_display()]
    if project.location_text:
        meta_bits.append(project.location_text)
    story.append(Paragraph(xml_escape(" · ".join(meta_bits)), styles["meta"]))

    qr_png = generate_qr_png(project)
    story.append(Image(qr_png, width=25 * mm, height=25 * mm))
    story.append(Paragraph("Scan to view the live, verified build log", styles["qr_caption"]))
    story.append(Spacer(1, 12 * mm))

    updates = (
        project.updates.select_related("author")
        .prefetch_related("photos")
        .order_by("entry_date", "created_at")
    )
    for update in updates:
        story.append(Paragraph(xml_escape(update.title), styles["entry_title"]))
        entry_meta = (
            f"{update.get_entry_type_display()} · {update.entry_date.strftime('%d %b %Y')} · "
            f"{update.author.display_name}"
        )
        story.append(Paragraph(xml_escape(entry_meta), styles["entry_meta"]))

        if update.body:
            story.append(Paragraph(_html_to_paragraph_markup(update.body), styles["body"]))

        for photo in update.photos.all():
            img = _fetch_image_flowable(photo.url)
            if img is not None:
                story.append(img)
                story.append(Spacer(1, 4 * mm))

    doc.build(story)
    return buffer.getvalue()
