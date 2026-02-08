import os
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth  # <-- IMPORTANT


# Rows in the same order as your Excel template
DEFAULT_ROWS = [
    "FABRIC",
    "LINE POST",
    "LINE POST CAP",
    "TIES LINE POST",
    "TOP RAIL",
    "TIES TOP RAIL",
    "CORNER POST",
    "GATE POST",
    "CORNER POST CAPS",
    "GATE POST CAPS",
    "TENSION BARS",
    "BB END POST-",
    "BB CORNER POST",
    "OTHER BB",
    "TENBNDS END POST",
    "TENBNDS CORNER POST",
    "OTHER TENBNDS",
    'C/B - 5/16" X 1-1/4"',
    "RAIL ENDS",
    "TENSION WIRE",
    "LINE RAIL CLAMPS",
    "TRUSS ROD - 3/8 X",
    "TRUSS TIGHTENERS",
    "SS GATES",
    "SLIDING GATES",
    "SS HINGES",
    "DD GATES",
    "DD HINGES",
    "WINDSCREEN",
    "CONCRETE",
    "QUICK ROCK",
]


def _norm_key(s: str) -> str:
    return (s or "").strip().upper()


def _fit_one_line(text: str, max_w: float, font="Helvetica", size=8) -> str:
    """Trim text with ellipsis so it fits on one line within max_w."""
    if not text:
        return ""
    s = str(text)
    if stringWidth(s, font, size) <= max_w:
        return s
    ell = "…"
    max_w2 = max_w - stringWidth(ell, font, size)
    if max_w2 <= 0:
        return ""
    while s and stringWidth(s, font, size) > max_w2:
        s = s[:-1]
    return s + ell


def _draw_chainlink_order_form(c: canvas.Canvas, project: dict, items_by_row: dict, rows: list[str]) -> None:
    """Draws the PDF content onto an existing reportlab canvas."""
    W, H = letter

    # ---- Page geometry ----
    left = 40
    right = W - 40
    top = H - 35

    # ---- Title ----
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, top, "ESTIMATING & ORDER FORM CHAINLINK")

    y = top - 28
    c.setFont("Helvetica", 9)

    # ---- Header lines ----
    c.drawString(left, y, "PROJECT:")
    c.line(left + 55, y - 2, left + 260, y - 2)

    c.drawString(W - 260, y, "DUE DATE")
    c.line(W - 210, y - 2, W - 120, y - 2)

    c.drawString(W - 115, y, "ORDER DATE")
    c.line(W - 55, y - 2, W - 40, y - 2)

    y -= 18
    c.drawString(left, y, "Job Name")
    c.line(left + 55, y - 2, left + 260, y - 2)

    c.drawString(W - 260, y, "PO #")
    c.line(W - 230, y - 2, W - 120, y - 2)

    y -= 18
    c.drawString(left, y, "HEIGHT-STYLE:")
    c.line(left + 75, y - 2, left + 180, y - 2)

    # ---- Fill header values ----
    c.setFont("Helvetica-Bold", 9)

    proj_val = str(project.get("project", "") or "")[:30]
    due_val = str(project.get("due_date", "") or "")[:12]
    order_val = str(project.get("order_date", "") or "")[:12]
    job_val = str(project.get("job_name", "") or "")[:30]
    po_val = str(project.get("po", "") or "")[:16]
    hs_val = str(project.get("height_style", "") or "")[:20]

    if proj_val:
        c.drawString(left + 58, top - 28, proj_val)
    if due_val:
        c.drawString(W - 208, top - 28, due_val)
    if order_val:
        c.drawString(W - 113, top - 28, order_val)
    if job_val:
        c.drawString(left + 58, top - 46, job_val)
    if po_val:
        c.drawString(W - 228, top - 46, po_val)
    if hs_val:
        c.drawString(left + 78, top - 64, hs_val)

    c.setFont("Helvetica", 8)

    # ---- Table ----
    table_top = y - 18
    table_left = left
    table_right = right
    table_bottom = 65

    # MATERIALS | QUANTITY | DESCRIPTION | PRODUCT CODE
    x0 = table_left
    x1 = x0 + 150   # Materials
    x2 = x1 + 75    # Quantity
    x3 = x2 + 250   # Description
    x4 = table_right  # Product Code stretches

    header_h = 18
    row_h = 14

    # Outer box
    c.rect(table_left, table_bottom, table_right - table_left, table_top - table_bottom, stroke=1, fill=0)

    # Vertical lines
    for x in (x1, x2, x3):
        c.line(x, table_bottom, x, table_top)

    # Header separator
    c.line(table_left, table_top - header_h, table_right, table_top - header_h)

    # Header labels centered
    c.setFont("Helvetica-Bold", 8)
    header_y = table_top - 13
    c.drawCentredString((x0 + x1) / 2, header_y, "MATERIALS")
    c.drawCentredString((x1 + x2) / 2, header_y, "QUANTITY")
    c.drawCentredString((x2 + x3) / 2, header_y, "DESCRIPTION")
    c.drawCentredString((x3 + x4) / 2, header_y, "PDT CD")
    c.setFont("Helvetica", 8)

    # Normalize keys
    normalized_items = {_norm_key(k): v for k, v in (items_by_row or {}).items()}

    # Rows
    y_row = table_top - header_h
    max_rows = int((y_row - table_bottom) // row_h)
    use_rows = rows[:max_rows]

    for row_name in use_rows:
        y_row -= row_h
        c.line(table_left, y_row, table_right, y_row)

        row = normalized_items.get(_norm_key(row_name), {}) or {}
        qty = row.get("qty", "")
        desc = row.get("desc", "")
        code = row.get("code", "")

        # Materials label (left aligned)
        c.drawString(x0 + 3, y_row + 4, row_name)

        # Quantity centered
        if qty not in ("", None):
            c.drawCentredString((x1 + x2) / 2, y_row + 4, str(qty))

        # Description centered, forced one line
        desc_w = (x3 - x2) - 8
        desc_txt = _fit_one_line(desc, desc_w, font="Helvetica", size=8)
        if desc_txt:
            c.drawCentredString((x2 + x3) / 2, y_row + 4, desc_txt)

        # Product code centered, forced one line
        code_w = (x4 - x3) - 8
        code_txt = _fit_one_line(code, code_w, font="Helvetica", size=8)
        if code_txt:
            c.drawCentredString((x3 + x4) / 2, y_row + 4, code_txt)

    # Footer timestamp
    c.setFont("Helvetica", 7)
    c.drawRightString(table_right, 50, f"Generated: {datetime.now():%Y-%m-%d %H:%M}")


def export_chainlink_order_form_pdf_bytes(project: dict, items_by_row: dict, rows=None) -> bytes:
    rows = rows or DEFAULT_ROWS
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    _draw_chainlink_order_form(c, project=project, items_by_row=items_by_row, rows=rows)
    c.save()
    buffer.seek(0)
    return buffer.read()


def export_chainlink_order_form_pdf(out_path: str, project: dict, items_by_row: dict, rows=None) -> str:
    rows = rows or DEFAULT_ROWS
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=letter)
    _draw_chainlink_order_form(c, project=project, items_by_row=items_by_row, rows=rows)
    c.save()
    return out_path
