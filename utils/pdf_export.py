"""
pdf_export.py — Convert a markdown research report to a styled PDF using reportlab.
"""
import re
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def _clean_inline(text: str) -> str:
    """Convert basic markdown inline formatting to ReportLab XML."""
    # Bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
    # Escape bare ampersands that aren't already entities
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', text)
    return text


def markdown_to_pdf_bytes(markdown_text: str, title: str = "Research Report") -> bytes:
    """
    Convert a markdown string to PDF bytes.
    Returns raw PDF bytes that can be written to a file or returned via Streamlit.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title=title
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ──────────────────────────────────────
    style_h1 = ParagraphStyle(
        "H1", parent=styles["Heading1"],
        fontSize=20, spaceAfter=10, spaceBefore=16,
        textColor=colors.HexColor("#1a1a2e"),
        leading=24
    )
    style_h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        fontSize=15, spaceAfter=8, spaceBefore=14,
        textColor=colors.HexColor("#16213e"),
        leading=18
    )
    style_h3 = ParagraphStyle(
        "H3", parent=styles["Heading3"],
        fontSize=12, spaceAfter=6, spaceBefore=10,
        textColor=colors.HexColor("#0f3460"),
        leading=15
    )
    style_body = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10.5, spaceAfter=6, leading=15,
        textColor=colors.HexColor("#2d2d2d")
    )
    style_bullet = ParagraphStyle(
        "Bullet", parent=style_body,
        leftIndent=20, bulletIndent=8,
        spaceAfter=4
    )
    style_source = ParagraphStyle(
        "Source", parent=style_body,
        fontSize=9, textColor=colors.HexColor("#555555"),
        leftIndent=12
    )

    story = []
    lines = markdown_text.split("\n")

    for line in lines:
        raw = line.rstrip()

        # ── Headings ──────────────────────────────────────
        if raw.startswith("### "):
            text = _clean_inline(raw[4:].strip())
            story.append(Paragraph(text, style_h3))

        elif raw.startswith("## "):
            text = _clean_inline(raw[3:].strip())
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
            story.append(Paragraph(text, style_h2))

        elif raw.startswith("# "):
            text = _clean_inline(raw[2:].strip())
            story.append(Paragraph(text, style_h1))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a2e")))
            story.append(Spacer(1, 6))

        # ── Horizontal rule ───────────────────────────────
        elif raw.strip() in ("---", "***", "___"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
            story.append(Spacer(1, 4))

        # ── Bullet points ─────────────────────────────────
        elif raw.startswith("- ") or raw.startswith("* "):
            text = _clean_inline(raw[2:].strip())
            story.append(Paragraph(f"• {text}", style_bullet))

        elif re.match(r"^\d+\. ", raw):
            text = _clean_inline(re.sub(r"^\d+\. ", "", raw).strip())
            story.append(Paragraph(f"• {text}", style_bullet))

        # ── Source lines (URLs) ───────────────────────────
        elif "http" in raw and raw.strip().startswith("http"):
            story.append(Paragraph(raw.strip(), style_source))

        # ── Empty line → small spacer ─────────────────────
        elif raw.strip() == "":
            story.append(Spacer(1, 5))

        # ── Normal paragraph ──────────────────────────────
        else:
            text = _clean_inline(raw.strip())
            if text:
                story.append(Paragraph(text, style_body))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
