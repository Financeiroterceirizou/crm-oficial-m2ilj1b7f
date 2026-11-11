#!/usr/bin/env python3
"""Kit visual terceirizou 2026 - helpers para os decks de marca.

Identidade: AmpleSoft Light (tudo minusculo), laranja #E15125, grafite #2B2C2E,
fundo branco ou grafite, cards cinza, simbolo "3" no canto.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

W, H = 13.333, 7.5
FONT = "AmpleSoft Light"
DARK = RGBColor(0x2B, 0x2C, 0x2E)
ORANGE = RGBColor(0xE1, 0x51, 0x25)
CARD = RGBColor(0xF5, 0xF5, 0xF6)
LINE = RGBColor(0xE3, 0xE4, 0xE6)
GREY = RGBColor(0x6B, 0x6C, 0x6E)
LGREY = RGBColor(0xC7, 0xC8, 0xCA)
PINK = RGBColor(0xFB, 0xE9, 0xE3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

ATIVOS = os.path.join(os.path.dirname(__file__), "..", "..", "work", "brand2026", "ativos")
ICONES = os.path.join(ATIVOS, "icones")


def _a(*p):
    return os.path.abspath(os.path.join(ATIVOS, *p))


def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs, bg="white"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    cor = DARK if bg == "dark" else WHITE
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = cor
    return s


def txt(slide, x, y, w, h, texto, size=14, color=DARK, bold=False, ls=None,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space=0, caps=False, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    linhas = texto if isinstance(texto, (list, tuple)) else [texto]
    for i, linha in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if ls:
            p.line_spacing = ls
        if space and i:
            p.space_before = Pt(space)
        r = p.add_run()
        r.text = linha.upper() if caps else linha
        f = r.font
        f.name = FONT
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        f.color.rgb = color
    return tb


def rich(slide, x, y, w, h, partes, size=14, color=DARK, ls=None, space=0):
    """partes: lista de (texto, dict) ou str. dict aceita color/size/bold."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    if ls:
        p.line_spacing = ls
    for item in partes:
        t, st = (item, {}) if isinstance(item, str) else item
        r = p.add_run()
        r.text = t
        r.font.name = FONT
        r.font.size = Pt(st.get("size", size))
        r.font.bold = st.get("bold", False)
        r.font.color.rgb = st.get("color", color)
    return tb


def card(slide, x, y, w, h, fill=CARD, line=LINE, radius=8000, lw=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    try:
        sh.adjustments[0] = radius / 100000.0
    except Exception:
        pass
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh


def rect(slide, x, y, w, h, fill, line=None, lw=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh


def hline(slide, x, y, w, color=LINE, lw=1.0):
    sh = slide.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + w), Inches(y))
    sh.line.color.rgb = color
    sh.line.width = Pt(lw)
    return sh


def pic_fit(slide, path, x, y, w, h, esc=0.8, ancora="centro"):
    """encaixa a imagem dentro da caixa (x,y,w,h) preservando a proporcao original.
    esc = fracao maxima da caixa que a imagem pode ocupar."""
    from PIL import Image
    iw, ih = Image.open(path).size
    alt_max = h * esc
    larg_max = w * esc
    alt = alt_max
    larg = alt * iw / ih
    if larg > larg_max:
        larg = larg_max
        alt = larg * ih / iw
    px = x + (w - larg) / 2 if ancora == "centro" else x + 0.01
    py = y + (h - alt) / 2 if ancora == "centro" else y + 0.01
    return slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(larg), Inches(alt))


def pic(slide, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(path, Inches(x), Inches(y), **kw)


def symbol(slide, dark=False, h=0.92, x=None, y=None, op=1.0):
    from PIL import Image
    s = "simbolo-branco.png" if dark else "simbolo-laranja.png"
    path = _a(s)
    iw, ih = Image.open(path).size
    hh = h
    ww = h * iw / ih
    x = (W - 0.45 - ww) if x is None else x
    y = (H - 0.35 - hh) if y is None else y
    p = pic(slide, path, x, y, ww, hh)
    if op < 1:
        _alpha(p, op)
    return p


def _alpha(shape, op):
    from lxml import etree
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    blip = shape._element.find(".//" + ns + "blip")
    if blip is None:
        return
    alpha = etree.SubElement(blip, ns + "alphaModFix")
    alpha.set("amt", str(int(op * 100000)))


def logo(slide, variant="horizontal-branco", x=0.6, y=0.5, w=3.2):
    path = _a("logo-%s.png" % variant)
    from PIL import Image
    iw, ih = Image.open(path).size
    return pic(slide, path, x, y, w, w * ih / iw)


_PGC = {"n": 1}


def page(slide, n=None, dark=False):
    """n=None numera pela ordem de criacao; n fixo mantem a numeracao manual do deck"""
    if n is None:
        _PGC["n"] += 1
        num = _PGC["n"]
    else:
        num = n
        _PGC["n"] = max(_PGC["n"], n)
    txt(slide, 0.6, 7.02, 2.0, 0.24, str(num).zfill(2), 9,
        LGREY if not dark else RGBColor(0x7A, 0x7B, 0x7D))


# ------------------------------------------------------------------ blocos

def eyebrow(slide, label, icon=None, dark=False, y=0.55, x=0.6):
    if icon:
        pic(slide, os.path.join(ICONES, icon + ".png"), x, y + 0.01, 0.26, 0.26)
        tx = x + 0.38
    else:
        tx = x
    txt(slide, tx, y, 9.0, 0.3, label, 12, ORANGE)


def title(slide, texto, y=1.0, size=30, w=11.9, color=DARK, x=0.6, h=1.2):
    return txt(slide, x, y, w, h, texto, size, color, ls=1.08)


def lead(slide, texto, y=2.4, size=14, w=10.6, color=GREY):
    return txt(slide, 0.6, y, w, 0.9, texto, size, color, ls=1.35)


def capa(prs, kicker, titulo, sub, tipo, rodape="uso interno · 2026"):
    s = blank(prs, "dark")
    logo(s, "horizontal-branco", 0.6, 0.5, 3.2)
    selo = card(s, 0.6, 2.15, 4.9, 0.5, fill=PINK, line=None, radius=50000)
    txt(s, 0.6, 2.15, 4.9, 0.5, kicker, 12.5, DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    txt(s, 0.6, 2.98, 11.6, 2.1, titulo, 44, WHITE, ls=1.04)
    txt(s, 0.6, 5.25, 10.4, 1.0, sub, 14.5, LGREY, ls=1.35)
    txt(s, 0.6, 6.62, 8.0, 0.32, rodape, 11, RGBColor(0x8A, 0x8B, 0x8D))
    symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
    return s


def divisor(prs, selo, titulo, apoio=None, n=None):
    s = blank(prs, "dark")
    if selo:
        card(s, 0.6, 1.65, 6.2, 0.5, fill=PINK, line=None, radius=50000)
        txt(s, 0.6, 1.65, 6.2, 0.5, selo, 12.5, DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    txt(s, 0.6, 2.6, 11.4, 2.2, titulo, 36, WHITE, ls=1.08)
    if apoio:
        txt(s, 0.6, 5.05, 10.6, 1.0, apoio, 14, LGREY, ls=1.35)
    symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
    page(s, n, dark=True)
    return s


def cards3(prs, itens, y=2.75, h=3.3, eyebrow_txt=None, titulo=None, top=1.0,
           sub=None, icon=None, num=False):
    """itens: [(titulo, texto)] x3 ou x4."""
    s = blank(prs)
    if eyebrow_txt:
        eyebrow(s, eyebrow_txt, icon)
    if titulo:
        title(s, titulo, y=top + 0.45)
    if sub:
        txt(s, 0.6, top + 1.45, 11.6, 0.8, sub, 14, GREY, ls=1.35)
    n = len(itens)
    gap = 0.22
    larg = (12.13 - gap * (n - 1)) / n
    x = 0.6
    for i, item in enumerate(itens, 1):
        t, corpo = item[0], item[1]
        card(s, x, y, larg, h)
        if num:
            txt(s, x + 0.32, y + 0.3, 1.0, 0.4, str(i).zfill(2), 12, ORANGE)
        txt(s, x + 0.32, y + (0.72 if num else 0.42), larg - 0.64, 0.75, t, 16.5, DARK, ls=1.12)
        txt(s, x + 0.32, y + (1.55 if num else 1.3), larg - 0.64, h - 1.7, corpo, 13, GREY, ls=1.4)
        x += larg + gap
    symbol(s)
    return s


def duas_colunas(prs, eyebrow_txt, titulo, esq_titulo, esq_itens, dir_titulo, dir_itens,
                 icon=None, note=None, dark_card=True):
    s = blank(prs)
    eyebrow(s, eyebrow_txt, icon)
    title(s, titulo)
    card(s, 0.6, 2.55, 5.85, 3.75, fill=CARD if not dark_card else DARK, line=None if dark_card else LINE)
    txt(s, 0.95, 2.9, 5.1, 0.5, esq_titulo, 15, WHITE if dark_card else DARK)
    txt(s, 0.95, 3.55, 5.15, 2.5, esq_itens, 13.5, LGREY if dark_card else GREY, ls=1.45, space=9)
    txt(s, 6.85, 2.8, 5.6, 0.5, dir_titulo, 15, DARK)
    txt(s, 6.85, 3.45, 5.55, 2.9, dir_itens, 13.5, GREY, ls=1.45, space=9)
    if note:
        txt(s, 6.85, 6.25, 5.4, 0.5, note, 11.5, LGREY, ls=1.3)
    symbol(s)
    return s


def tabela(slide, x, y, w, cols, rows, header=True, cw=None, rh=0.44, size=12.5,
           hcolor=ORANGE, zebra=True, bold_col0=False):
    """Tabela desenhada a mao (controle total de layout)."""
    n = len(cols)
    cw = cw or [w / n] * n
    yy = y
    if header:
        rect(slide, x, yy, w, rh, DARK)
        cx = x
        for i, c in enumerate(cols):
            txt(slide, cx + 0.16, yy, cw[i] - 0.2, rh, c, 11.5, WHITE, anchor=MSO_ANCHOR.MIDDLE)
            cx += cw[i]
        yy += rh
    for j, row in enumerate(rows):
        if zebra and j % 2 == 1:
            rect(slide, x, yy, w, rh, CARD)
        cx = x
        for i, cell in enumerate(row):
            cor = DARK if (i == 0 and bold_col0) else GREY
            if isinstance(cell, tuple):
                cell, cor = cell
            txt(slide, cx + 0.16, yy, cw[i] - 0.24, rh, cell, size, cor,
                bold=(i == 0 and bold_col0), anchor=MSO_ANCHOR.MIDDLE)
            cx += cw[i]
        yy += rh
    return yy


def citacao(prs, texto, autor=None, eyebrow_txt=None, n=None):
    s = blank(prs, "dark")
    if eyebrow_txt:
        txt(s, 0.6, 1.2, 9.0, 0.3, eyebrow_txt, 12, ORANGE)
    txt(s, 0.6, 1.9, 11.0, 3.4, texto, 32, WHITE, ls=1.14)
    if autor:
        txt(s, 0.6, 5.6, 9.0, 0.4, autor, 13, LGREY)
    symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
    if n:
        page(s, n, dark=True)
    return s


def bullets(slide, x, y, w, itens, size=13.5, color=GREY, gap=0.42, bullet_color=ORANGE, mark="·"):
    yy = y
    for it in itens:
        txt(slide, x, yy, 0.2, 0.3, mark, size + 2, bullet_color)
        txt(slide, x + 0.24, yy, w - 0.24, gap + 0.15, it, size, color, ls=1.35)
        yy += gap
    return yy


def kpi_band(slide, itens, y=5.55, w_total=12.13, x=0.6):
    """itens: [(numero, legenda)] ate 4."""
    n = len(itens)
    larg = w_total / n
    for i, (num, leg) in enumerate(itens):
        xx = x + i * larg
        txt(slide, xx, y, larg - 0.3, 0.6, num, 32, ORANGE, ls=1.0)
        txt(slide, xx, y + 0.62, larg - 0.35, 0.6, leg, 11.5, GREY, ls=1.3)
        if i:
            v = slide.shapes.add_connector(1, Inches(xx - 0.2), Inches(y + 0.05), Inches(xx - 0.2), Inches(y + 1.0))
            v.line.color.rgb = LINE
            v.line.width = Pt(1)


def matriz(slide, x, y, w, h, quad, ponto, px, py, cor=ORANGE, lx=0.2, ly=-0.5):
    """quad: [(rotulo, qx, qy)] com qx/qy 0..1. rotulo do ponto em lx,ly (inches)."""
    from pptx.enum.shapes import MSO_SHAPE
    rect(slide, x, y, w, h, CARD, line=LINE)
    m = slide.shapes.add_connector(1, Inches(x + w / 2), Inches(y), Inches(x + w / 2), Inches(y + h))
    m.line.color.rgb = LGREY
    m.line.width = Pt(1)
    m2 = slide.shapes.add_connector(1, Inches(x), Inches(y + h / 2), Inches(x + w), Inches(y + h / 2))
    m2.line.color.rgb = LGREY
    m2.line.width = Pt(1)
    for rot, qx, qy in quad:
        cx = x + (0.28 if qx < 0.5 else w / 2 + 0.22)
        cy = y + (0.24 if qy >= 0.5 else h / 2 + 0.22)
        txt(slide, cx, cy, w / 2 - 0.5, 0.55, rot, 11, LGREY, ls=1.2)
    d = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + px * w - 0.11), Inches(y + (1 - py) * h - 0.11), Inches(0.22), Inches(0.22))
    d.fill.solid()
    d.fill.fore_color.rgb = cor
    d.line.color.rgb = WHITE
    d.line.width = Pt(1.5)
    d.shadow.inherit = False
    txt(slide, x + px * w + lx, y + (1 - py) * h + ly, 3.4, 0.45, ponto, 13, DARK, bold=True)
