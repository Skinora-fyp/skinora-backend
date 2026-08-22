"""
Skinora -- single-page A4 progress report.
All Y positions are absolute so the layout is guaranteed to fit one page.
"""
import io
import os
from typing import Optional
from datetime import datetime

import requests as http
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

# ── Palette (RGB) ───────────────────────────────────────────
_DARK        = (35,  36,  28)
_GREEN       = (110, 119, 51)
_LIME        = (190, 202, 92)
_CREAM       = (246, 244, 236)
_CREAM_DARK  = (235, 233, 222)
_MUTED       = (156, 154, 140)
_BORDER      = (215, 212, 200)
_WHITE       = (255, 255, 255)

_IMPROVED    = (62,  122, 42)
_NO_CHANGE   = (138, 107, 30)
_WORSE       = (176, 94,  60)

_BG_IMPROVED  = (228, 245, 224)
_BG_NO_CHANGE = (255, 248, 230)
_BG_WORSE     = (253, 240, 236)

# ── Logo (backend → up 3 dirs → frontend/public/assets) ────
_HERE      = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.normpath(
    os.path.join(_HERE, '..', '..', '..', 'frontend', 'public', 'assets', 'skinora_logo.png')
)

_LOGO_BYTES_CACHE: Optional[io.BytesIO] = None   # forward-ref; type set after typing import


def _logo_buf() -> Optional[io.BytesIO]:
    """Return a small resized PNG of the logo (cached after first call)."""
    global _LOGO_BYTES_CACHE
    if _LOGO_BYTES_CACHE is not None:
        _LOGO_BYTES_CACHE.seek(0)
        return _LOGO_BYTES_CACHE
    if not os.path.isfile(_LOGO_PATH):
        return None
    try:
        img = Image.open(_LOGO_PATH).convert('RGBA')
        img.thumbnail((96, 96), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        _LOGO_BYTES_CACHE = buf
        return _LOGO_BYTES_CACHE
    except Exception:
        return None

# ── Latin-1 text sanitiser ──────────────────────────────────
_SUBS = {
    '—': '--', '–': '-', '’': "'", '‘': "'",
    '“': '"', '”': '"', '…': '...', '•': '-',
    '·': '-', '→': '->', '←': '<-',
}

def _s(text: str) -> str:
    """Replace non-latin-1 characters with safe equivalents."""
    for ch, rep in _SUBS.items():
        text = text.replace(ch, rep)
    return text.encode('latin-1', errors='replace').decode('latin-1')


def _fetch_image(url: str) -> Optional[io.BytesIO]:
    if not url:
        return None
    try:
        r = http.get(url, timeout=6)
        if r.status_code == 200 and r.content:
            buf = io.BytesIO(r.content)
            buf.seek(0)
            return buf
    except Exception:
        pass
    return None


# ────────────────────────────────────────────────────────────
def generate_progress_pdf(user, tracking, old_det, new_det,
                           progress: str, old_score, new_score, delta) -> bytes:
    """
    Generate a professional single-page A4 progress report.
    Uses fixed absolute Y positions so all content fits on one page.
    """
    remedy_name = (tracking.remedy.name  if tracking and tracking.remedy  else 'N/A')
    freq_label  = (tracking.frequency.capitalize() if tracking else 'N/A')
    now_str     = datetime.now().strftime('%d %b %Y')

    next_rem = None
    if tracking and getattr(tracking, 'next_reminder', None):
        next_rem = tracking.next_reminder.strftime('%d %b %Y')

    # ── Canvas ──────────────────────────────────────────────
    pdf = FPDF(unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    W  = 210           # page width
    M  = 12            # left/right margin
    CW = W - 2 * M    # content width (186mm)

    # ════════════════════════════════════════════════════════
    # SECTION 1 — HEADER  (y = 0 → 36)
    # ════════════════════════════════════════════════════════
    HH = 36
    pdf.set_fill_color(*_DARK)
    pdf.rect(0, 0, W, HH, 'F')

    # thin lime bottom stripe on header
    pdf.set_fill_color(*_LIME)
    pdf.rect(0, HH - 1.5, W, 1.5, 'F')

    # Logo (resized in-memory so the PDF stays compact)
    logo_x_end = M
    logo_data  = _logo_buf()
    if logo_data:
        try:
            pdf.image(logo_data, x=M, y=6, w=24, h=24)
            logo_x_end = M + 27
        except Exception:
            pass

    # Brand wordmark
    pdf.set_xy(logo_x_end, 8)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(*_LIME)
    pdf.cell(70, 9, 'SKINORA', border=0)

    pdf.set_xy(logo_x_end, 19)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*_CREAM)
    pdf.cell(70, 5, 'Skin Progress Report', border=0)

    pdf.set_xy(logo_x_end, 26)
    pdf.set_font('Helvetica', 'I', 7.5)
    pdf.set_text_color(170, 168, 155)
    pdf.cell(70, 5, 'AI-powered natural skin care', border=0)

    # Top-right: date + page label
    pdf.set_xy(W - M - 66, 10)
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_text_color(210, 208, 195)
    pdf.cell(66, 5, 'REPORT DATE', border=0, align='R')
    pdf.set_xy(W - M - 66, 16)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*_LIME)
    pdf.cell(66, 6, now_str, border=0, align='R')

    # ════════════════════════════════════════════════════════
    # SECTION 2 — INFO STRIP  (y = 36 → 52)
    # ════════════════════════════════════════════════════════
    IS_Y = 36
    IS_H = 16
    pdf.set_fill_color(*_CREAM_DARK)
    pdf.rect(0, IS_Y, W, IS_H, 'F')

    info_col  = CW / 4
    info_data = [
        ('PREPARED FOR', _s(user.name[:22])),
        ('REMEDY',       _s(remedy_name[:20])),
        ('FREQUENCY',    _s(freq_label)),
        ('NEXT CHECK-IN', _s(next_rem or 'TBD')),
    ]
    for i, (lbl, val) in enumerate(info_data):
        ix = M + i * info_col
        # vertical divider (except for first)
        if i > 0:
            pdf.set_draw_color(*_BORDER)
            pdf.set_line_width(0.3)
            pdf.line(ix - 1, IS_Y + 3, ix - 1, IS_Y + IS_H - 3)
        pdf.set_xy(ix, IS_Y + 2.5)
        pdf.set_font('Helvetica', 'B', 6)
        pdf.set_text_color(*_MUTED)
        pdf.cell(info_col, 4, lbl, border=0)
        pdf.set_xy(ix, IS_Y + 7.5)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(*_DARK)
        pdf.cell(info_col, 5, val, border=0)

    # ════════════════════════════════════════════════════════
    # SECTION 3 — VERDICT BANNER  (y = 52 → 70)
    # ════════════════════════════════════════════════════════
    VB_Y = 52
    VB_H = 18

    vcfg = {
        'improved':  (_IMPROVED,  _BG_IMPROVED,  'IMPROVED',
                      'Your skin is responding well to the remedy. Keep up the routine!'),
        'no_change': (_NO_CHANGE, _BG_NO_CHANGE, 'NO CHANGE YET',
                      'Some remedies take 4-8 weeks. Review your routine or try alternatives.'),
        'worse':     (_WORSE,     _BG_WORSE,     'REGRESSION DETECTED',
                      'Your skin appears to have reacted. Consider switching or consulting a specialist.'),
    }
    v_accent, v_bg, v_label, v_msg = vcfg.get(progress, (_MUTED, _CREAM, 'UNKNOWN', ''))

    pdf.set_fill_color(*v_bg)
    pdf.rect(M, VB_Y, CW, VB_H, 'F')

    # colored left bar
    pdf.set_fill_color(*v_accent)
    pdf.rect(M, VB_Y, 4, VB_H, 'F')

    # verdict label
    pdf.set_xy(M + 8, VB_Y + 4)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*v_accent)
    pdf.cell(55, 6, _s(v_label), border=0)

    # verdict message
    pdf.set_xy(M + 68, VB_Y + 3.5)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(60, 58, 46)
    pdf.cell(CW - 70, 10, _s(v_msg), border=0)

    # thin border
    pdf.set_draw_color(*v_accent)
    pdf.set_line_width(0.4)
    pdf.rect(M, VB_Y, CW, VB_H, 'D')

    # ════════════════════════════════════════════════════════
    # SECTION 4 — HEALTH SCORES  (y = 73 → 96)
    # ════════════════════════════════════════════════════════
    SC_Y = 73

    # Section label
    _section_header(pdf, M, SC_Y, CW, 'HEALTH SCORE COMPARISON')

    BAR_LABEL_W = 40
    BAR_PCT_W   = 16
    BAR_X       = M + BAR_LABEL_W + BAR_PCT_W
    BAR_W       = CW - BAR_LABEL_W - BAR_PCT_W

    by = SC_Y + 8
    for bar_lbl, bar_score in [('Original scan', old_score), ('Check-in scan', new_score)]:
        if bar_score is None:
            by += 9
            continue
        s    = min(max(float(bar_score), 0.0), 1.0)
        fill = _IMPROVED if s >= 0.6 else (_NO_CHANGE if s >= 0.35 else _WORSE)

        pdf.set_xy(M, by)
        pdf.set_font('Helvetica', '', 7.5)
        pdf.set_text_color(*_MUTED)
        pdf.cell(BAR_LABEL_W, 5, bar_lbl, border=0)

        pdf.set_xy(M + BAR_LABEL_W, by)
        pdf.set_font('Helvetica', 'B', 7.5)
        pdf.set_text_color(*_DARK)
        pdf.cell(BAR_PCT_W, 5, f'{s * 100:.1f}%', border=0)

        # track + fill
        pdf.set_fill_color(212, 210, 200)
        pdf.rect(BAR_X, by + 1.2, BAR_W, 3.2, 'F')
        pdf.set_fill_color(*fill)
        pdf.rect(BAR_X, by + 1.2, BAR_W * s, 3.2, 'F')
        by += 9

    # delta
    if delta is not None:
        sign  = '+' if delta >= 0 else ''
        color = _IMPROVED if delta > 0 else (_WORSE if delta < 0 else _MUTED)
        pdf.set_xy(M, by)
        pdf.set_font('Helvetica', 'B', 7.5)
        pdf.set_text_color(*color)
        pdf.cell(CW, 4, _s(f'Change: {sign}{delta * 100:.1f}% health score shift'), border=0)

    # ════════════════════════════════════════════════════════
    # SECTION 5 — SCAN CARDS  (y = 99 → 205)
    # ════════════════════════════════════════════════════════
    SCAN_Y   = 99
    IMG_H    = 58      # image height per card
    DETAIL_H = 45      # detail rows height per card (title + 5 rows)
    CARD_GAP = 5
    CARD_W   = (CW - CARD_GAP) / 2    # ~90.5mm

    _section_header(pdf, M, SCAN_Y, CW, 'SCAN DETAILS')

    CONT_Y   = SCAN_Y + 7   # 106

    def _draw_card(det, title: str, score: float, cx: float):
        """Draw one scan card (image + detail block) at column x=cx."""
        cur_y = CONT_Y

        # ── image area ──────────────────────────────────────
        img_loaded = False
        if det and det.image_url:
            img_data = _fetch_image(det.image_url)
            if img_data:
                try:
                    pdf.image(img_data, x=cx, y=cur_y, w=CARD_W, h=IMG_H)
                    img_loaded = True
                except Exception:
                    pass

        if not img_loaded:
            # placeholder
            pdf.set_fill_color(*_CREAM_DARK)
            pdf.rect(cx, cur_y, CARD_W, IMG_H, 'F')
            pdf.set_xy(cx, cur_y + IMG_H / 2 - 4)
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(*_MUTED)
            pdf.cell(CARD_W, 5, 'No image available', border=0, align='C')

        # thin border around image
        pdf.set_draw_color(*_BORDER)
        pdf.set_line_width(0.3)
        pdf.rect(cx, cur_y, CARD_W, IMG_H, 'D')

        detail_y = cur_y + IMG_H

        # ── title bar (dark) ─────────────────────────────────
        pdf.set_fill_color(*_DARK)
        pdf.rect(cx, detail_y, CARD_W, 7, 'F')
        pdf.set_xy(cx + 4, detail_y + 1.5)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(*_LIME)
        pdf.cell(CARD_W - 8, 5, _s(title.upper()), border=0)

        # ── detail rows (cream bg) ───────────────────────────
        rows_y = detail_y + 7
        pdf.set_fill_color(*_CREAM)
        pdf.rect(cx, rows_y, CARD_W, DETAIL_H - 7, 'F')
        pdf.set_draw_color(*_BORDER)
        pdf.rect(cx, detail_y, CARD_W, DETAIL_H, 'D')  # border around whole detail block

        if det:
            date_str = det.detected_at.strftime('%d %b %Y') if det.detected_at else '-'
            rows = [
                ('Condition',    det.final_condition or '-'),
                ('Skin type',    det.skin_type       or '-'),
                ('Acne status',  det.acne_status      or '-'),
                ('Health score', f'{score * 100:.1f}%'),
                ('Scan date',    date_str),
            ]
        else:
            rows = [('Status', 'No baseline scan'), ('', ''), ('', ''), ('', ''), ('', '')]

        ry = rows_y + 2
        for lbl, val in rows:
            if not lbl:
                ry += 6.2
                continue
            # alternating row bg
            if rows.index((lbl, val)) % 2 == 0:
                pdf.set_fill_color(240, 238, 228)
                pdf.rect(cx + 1, ry, CARD_W - 2, 5.8, 'F')

            pdf.set_xy(cx + 3, ry + 0.5)
            pdf.set_font('Helvetica', '', 7.2)
            pdf.set_text_color(*_MUTED)
            pdf.cell(28, 5, _s(lbl + ':'), border=0)

            pdf.set_xy(cx + 31, ry + 0.5)
            pdf.set_font('Helvetica', 'B', 7.2)
            pdf.set_text_color(*_DARK)
            pdf.cell(CARD_W - 34, 5, _s(str(val)[:24]), border=0)
            ry += 6.2

    _draw_card(old_det, 'Original Scan', old_score or 0.0, M)
    _draw_card(new_det, 'Check-in Scan',  float(new_score), M + CARD_W + CARD_GAP)

    AFTER_CARDS_Y = CONT_Y + IMG_H + DETAIL_H   # ≈ 106 + 58 + 45 = 209

    # ════════════════════════════════════════════════════════
    # SECTION 6 — RECOMMENDATIONS  (y ≈ 212 → 252)
    # ════════════════════════════════════════════════════════
    REC_Y = AFTER_CARDS_Y + 3   # ≈ 212

    _section_header(pdf, M, REC_Y, CW, 'RECOMMENDATIONS')

    rn = _s(remedy_name)
    recs = {
        'improved': [
            f'Continue using {rn} as directed - consistency is key to lasting results.',
            'Keep your application schedule steady: same time, same amount every day.',
            'Stay hydrated, eat balanced meals, and protect skin from prolonged sun exposure.',
            'Your next check-in is scheduled - keep tracking to confirm lasting improvement.',
        ],
        'no_change': [
            f'Give {rn} more time - most natural remedies take 4-8 weeks to show visible change.',
            'Double-check your application method matches the remedy instructions.',
            'Ensure photos are taken in consistent lighting for accurate AI comparison.',
            'Log in to Skinora to explore alternative remedies suited to your skin condition.',
        ],
        'worse': [
            'Pause the current remedy if you are experiencing irritation, redness, or rash.',
            'Consult a certified dermatologist before continuing or switching any treatment.',
            'Document new symptoms with clear photos for your next medical appointment.',
            'Log in to Skinora to explore gentler, clinically-informed alternatives.',
        ],
    }

    rec_y = REC_Y + 7
    pdf.set_font('Helvetica', '', 7.8)
    pdf.set_text_color(*_DARK)
    for idx, rec in enumerate(recs.get(progress, [])):
        # alternating bg
        bg = (248, 246, 238) if idx % 2 == 0 else (240, 238, 228)
        pdf.set_fill_color(*bg)
        pdf.rect(M, rec_y, CW, 6.5, 'F')

        pdf.set_xy(M + 3, rec_y + 0.8)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(*v_accent)
        pdf.cell(5, 5, str(idx + 1) + '.', border=0)

        pdf.set_xy(M + 9, rec_y + 0.8)
        pdf.set_font('Helvetica', '', 7.8)
        pdf.set_text_color(*_DARK)
        pdf.cell(CW - 11, 5, _s(rec), border=0)
        rec_y += 6.5

    # ════════════════════════════════════════════════════════
    # SECTION 7 — NEXT CHECK-IN BOX  (y ≈ after recs, 14mm)
    # ════════════════════════════════════════════════════════
    BOX_Y = rec_y + 5

    pdf.set_fill_color(*_CREAM_DARK)
    pdf.set_draw_color(*_LIME)
    pdf.set_line_width(0.5)
    pdf.rect(M, BOX_Y, CW, 14, 'FD')

    # lime left accent
    pdf.set_fill_color(*_LIME)
    pdf.rect(M, BOX_Y, 3.5, 14, 'F')

    pdf.set_xy(M + 7, BOX_Y + 2.5)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(*_DARK)
    pdf.cell(50, 5, 'NEXT STEPS', border=0)

    pdf.set_xy(M + 7, BOX_Y + 8)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(*_MUTED)
    next_line = f'Next check-in: {next_rem}  |  Frequency: {_s(freq_label)}  |  Remedy: {_s(remedy_name[:22])}'
    pdf.cell(CW - 9, 4.5, _s(next_line), border=0)

    # ════════════════════════════════════════════════════════
    # FOOTER  (fixed at bottom)
    # ════════════════════════════════════════════════════════
    F_Y = 278

    pdf.set_draw_color(*_LIME)
    pdf.set_line_width(0.6)
    pdf.line(M, F_Y, W - M, F_Y)

    pdf.set_fill_color(*_DARK)
    pdf.rect(0, F_Y + 1, W, 18, 'F')

    pdf.set_xy(M, F_Y + 3.5)
    pdf.set_font('Helvetica', 'I', 6.5)
    pdf.set_text_color(*_MUTED)
    pdf.cell(
        CW - 20, 4,
        _s('Skinora -- AI-powered natural skin care. '
           'Recommendations are for educational purposes only and not a substitute for professional medical advice.'),
        border=0,
    )

    pdf.set_xy(M, F_Y + 9)
    pdf.set_font('Helvetica', '', 6.5)
    pdf.set_text_color(140, 140, 120)
    pdf.cell(CW // 2, 4, _s(f'Generated on {now_str}  |  skinora.ai'), border=0)

    pdf.set_xy(W - M - 30, F_Y + 3.5)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*_LIME)
    pdf.cell(30, 8, 'SKINORA', border=0, align='R')

    return bytes(pdf.output())


# ── Helpers ──────────────────────────────────────────────────

def _section_header(pdf: FPDF, x: float, y: float, w: float, title: str):
    """Draw a dark-green section header bar."""
    pdf.set_fill_color(*_GREEN)
    pdf.rect(x, y, w, 6.5, 'F')
    pdf.set_xy(x + 4, y + 1)
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_text_color(*_CREAM)
    pdf.cell(w - 8, 5, title, border=0)
