#!/usr/bin/env python3
"""Deck 3 - MANUAL DE IDENTIDADE VISUAL terceirizou 2026."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import deck_kit
from deck_kit import *  # noqa
from PIL import Image

_a = deck_kit._a

OUT = "artifacts/manual-identidade-visual-terceirizou-2026.pptx"
prs = new_deck()


def ar(path):
    iw, ih = Image.open(path).size
    return iw / ih


def logoem(slide, variant, x, y, w):
    p = _a("logo-%s.png" % variant)
    return pic(slide, p, x, y, w, w / ar(p))


def area_marcada(slide, x, y, w, h, label=None, color=ORANGE):
    """retangulo pontilhado de area de reserva/construcao"""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.background()
    sh.line.color.rgb = color
    sh.line.width = Pt(1.0)
    sh.line.dash_style = 4  # dash
    sh.shadow.inherit = False
    if label:
        txt(slide, x, y - 0.3, w, 0.25, label, 9.5, color)
    return sh


def spec(slide, x, y, w, h, titulo, linhas, dark=False):
    """caixa de especificacao tecnica"""
    card(slide, x, y, w, h, fill=DARK if dark else CARD, line=None if dark else LINE)
    txt(slide, x + 0.28, y + 0.24, w - 0.5, 0.3, titulo, 10.5, ORANGE)
    yy = y + 0.62
    for rot, val in linhas:
        txt(slide, x + 0.28, yy, 1.5, 0.26, rot, 9.5, LGREY if dark else GREY)
        txt(slide, x + 1.75, yy, w - 2.0, 0.28, val, 10, WHITE if dark else DARK)
        yy += 0.34


def grade_logos(s, itens, y=2.32, cols=3, topo_nota=6.42):
    """itens: (arquivo, fundo, titulo, uso). dimensiona sozinho para nao invadir a nota."""
    n = len(itens)
    linhas = (n + cols - 1) // cols
    label_h = 0.5
    disp = topo_nota - 0.12 - y
    if linhas == 1:
        ch = min(2.2, disp - label_h)
        gapy = 0
    else:
        ch = (disp - label_h * linhas - 0.3) / linhas
        gapy = 0.3
    w = (12.13 - 0.26 * (cols - 1)) / cols
    for i, (arq, fnd, tit, uso) in enumerate(itens):
        row = i // cols
        na_linha = min(cols, n - row * cols)
        col = i - row * cols
        # centraliza quando a ultima linha fica incompleta
        x0 = 0.6 + (cols - na_linha) * (w + 0.26) / 2.0
        x = x0 + col * (w + 0.26)
        yy = y + row * (ch + gapy + label_h)
        rect(s, x, yy, w, ch, fnd, line=(LINE if fnd == WHITE else None))
        path = _a(arq)
        iw, ih = Image.open(path).size
        esc = 0.60 if ("vertical" in arq or "simbolo" in arq) else 0.80
        alt = ch * esc
        larg = alt * iw / ih
        if larg > w * 0.86:
            larg = w * 0.86
            alt = larg * ih / iw
        pic(s, path, x + (w - larg) / 2, yy + (ch - alt) / 2, larg, alt)
        txt(s, x, yy + ch + 0.08, w, 0.22, tit, 9.5, ORANGE)
        txt(s, x, yy + ch + 0.29, w, 0.2, uso, 9, GREY)


# 01 capa ------------------------------------------------------------
capa(prs, "manual de identidade visual",
     ["o sistema visual", "da terceirizou."],
     "logo, cor, tipografia, grid e aplicação. o que pode, o que não pode e por quê. versão 1 · 2026.",
     "documento de marca · uso interno e agências")

# 02 sumário
s = blank(prs)
eyebrow(s, "conteúdo", "camadas")
title(s, ["o que este manual resolve."], y=0.95, size=30, w=9.0)
grupos = [("01", "a marca", "logo, versões, área de reserva, usos errados"),
          ("02", "cor", "paleta, proporção, contraste, fundos"),
          ("03", "tipografia", "ampleSoft, hierarquia, tamanhos mínimos"),
          ("04", "composição", "grid, margens, respiro, símbolo"),
          ("05", "elementos", "ícones, foto, gráfico, selo"),
          ("06", "aplicação", "apresentação, proposta, social, papelaria")]
x, y = 0.6, 2.35
for i, (n, t, c) in enumerate(grupos):
    col, row = i % 3, i // 3
    xx = 0.6 + col * 4.07
    yy = 2.35 + row * 2.0
    txt(s, xx, yy, 0.6, 0.3, n, 11.5, ORANGE)
    txt(s, xx, yy + 0.35, 3.4, 0.4, t, 17, DARK)
    txt(s, xx, yy + 0.85, 3.5, 0.9, c, 11.5, GREY, ls=1.35)
symbol(s)
page(s)

# 03 divisor marca
divisor(prs, "01 · a marca", ["um sistema de logos.", "não uma logo só."],
        "a marca tem quatro famílias, para quatro tipos de espaço. escolher a família errada é o erro mais comum e o mais visível.")

# 04 a logo
s = blank(prs)
eyebrow(s, "a logo", "tag")
title(s, ["símbolo, nome e assinatura.", "um só conjunto."], y=0.95, size=28, w=9.6)
rect(s, 0.6, 2.4, 8.4, 3.9, DARK)
logoem(s, "horizontal-branco", 2.05, 3.6, 5.5)
txt(s, 0.9, 5.95, 6.0, 0.3, "versão principal · fundo grafite", 9.5, RGBColor(0x9A, 0x9B, 0x9D))
spec(s, 9.25, 2.4, 3.48, 3.9, "anatomia", [
    ("símbolo", "“3” estilizado, laranja"),
    ("nome", "ter mais terceirizou"),
    ("assinatura", "terceirização financeira"),
    ("desenho", "ampleSoft light, minúsculo"),
], dark=False)
txt(s, 0.6, 6.55, 11.9, 0.35,
    "a assinatura “terceirização financeira” existe em todas as famílias e pode ser omitida nas peças de campanha.", 11.5, GREY)
symbol(s)
page(s)

# 05 as quatro famílias
s = blank(prs)
eyebrow(s, "as quatro famílias", "camadas")
title(s, ["cada família tem um espaço.", "escolher é a primeira decisão."], y=0.95, size=28, w=10.4)
familias = [
    ("horizontal", "logo-horizontal-branco.png", DARK, "capa, slide, assinatura de e-mail", "1 linha · 2,85:1"),
    ("quadrado", "quadrado-laranja-preto.png", WHITE, "post, card, carrossel, avatar", "2 linhas · 2,07:1"),
    ("vertical", "logo-vertical-laranja-preto.png", WHITE, "story, banner estreito, roll-up", "empilhada · 0,68:1"),
    ("símbolo", "simbolo-laranja.png", WHITE, "canto, favicon, marca d’água", "só o “3” · 0,68:1"),
]
for i, (nome, arq, fnd, uso, prop) in enumerate(familias):
    x = 0.6 + i * 3.07
    rect(s, x, 2.35, 2.92, 2.45, fnd, line=(LINE if fnd == WHITE else None))
    path = _a(arq)
    esc = 0.62 if ("vertical" in arq or "simbolo" in arq) else 0.80
    pic_fit(s, path, x, 2.35, 2.92, 2.45, esc=esc)
    txt(s, x, 4.95, 2.9, 0.3, nome, 15, DARK)
    txt(s, x, 5.32, 2.9, 0.3, prop, 10, ORANGE)
    txt(s, x, 5.62, 2.9, 0.8, uso, 10.5, GREY, ls=1.3)
txt(s, 0.6, 6.6, 11.9, 0.5,
    "as quatro famílias têm o mesmo desenho. nunca misturar duas na mesma peça: um slide usa horizontal, o post da mesma campanha usa quadrado.", 11, GREY)
symbol(s)
page(s)

# 06 horizontais
s = blank(prs)
eyebrow(s, "família horizontal", "camadas")
title(s, ["cinco versões de cor.", "com e sem assinatura."], y=0.95, size=27, w=9.6)
itens = [("logo-horizontal-branco.png", DARK, "branco", "fundo escuro, vídeo, foto"),
         ("logo-horizontal-preto.png", WHITE, "preto", "documento, contrato, branco"),
         ("logo-horizontal-laranja-preto.png", WHITE, "laranja e preto", "quando o laranja precisa aparecer"),
         ("logo-horizontal-laranja-branco.png", DARK, "laranja e branco", "fundo escuro com símbolo laranja"),
         ("logo-horizontal-branco-sem-tagline.png", DARK, "branco sem assinatura", "espaço curto, rodapé"),
         ("logo-horizontal-laranja-preto-sem-tagline.png", WHITE, "laranja e preto sem assinatura", "campanha, peça de venda")]
grade_logos(s, itens)
txt(s, 0.6, 6.5, 11.9, 0.4, "a versão sem assinatura é a mesma logo, só sem a linha “terceirização financeira”. não é outra marca.", 10.5, GREY)
symbol(s)
page(s)

# 07 quadrados
s = blank(prs)
eyebrow(s, "família quadrada", "camadas")
title(s, ["o bloco de duas linhas.", "para peça social."], y=0.95, size=27, w=9.4)
itens = [("quadrado-laranja-preto.png", WHITE, "laranja e preto", "padrão para post em fundo claro"),
         ("quadrado-laranja-branco.png", DARK, "laranja e branco", "post em fundo escuro"),
         ("quadrado-branco.png", DARK, "branco", "fundo escuro com foto"),
         ("quadrado-preto.png", WHITE, "preto", "peça impressa 1 cor"),
         ("quadrado-laranja.png", WHITE, "laranja", "peça de campanha, alto contraste")]
grade_logos(s, itens, cols=3)
txt(s, 0.6, 6.5, 11.9, 0.4, "o quadrado quebra “terceirizou” em duas linhas. só usar onde a largura é limitada: feed, card, avatar quadrado.", 10.5, GREY)
symbol(s)
page(s)

# 08 verticais
s = blank(prs)
eyebrow(s, "família vertical", "camadas")
title(s, ["a versão empilhada.", "para espaço estreito."], y=0.95, size=27, w=9.6)
itens = [("logo-vertical-laranja-preto.png", WHITE, "laranja e preto", "story em fundo claro"),
         ("logo-vertical-laranja-branco.png", DARK, "laranja e branco", "story e banner escuro"),
         ("logo-vertical-branco.png", DARK, "branco", "foto e vídeo escuro"),
         ("logo-vertical-preto.png", WHITE, "preto", "impresso, roll-up"),
         ("logo-vertical-laranja.png", WHITE, "laranja", "peça 1 cor de campanha")]
grade_logos(s, itens, cols=5, topo_nota=6.28)
txt(s, 0.6, 6.35, 11.9, 0.6,
    ["bloco alto: nome em cima, símbolo embaixo. é a única família que pode receber a assinatura em coluna, quando o suporte for muito estreito.",
     "nunca usar a vertical dentro de slide 16:9, ela sobra espaço e some."], 10.5, GREY, ls=1.35)
symbol(s)
page(s)

# 09 símbolo isolado
s = blank(prs)
eyebrow(s, "símbolo isolado", "bussola")
title(s, ["o “3” sozinho", "carrega a marca."], y=0.95, size=28, w=8.2)
caixas = [("laranja", "simbolo-laranja.png", WHITE, "canto de slide, marca d’água, favicon"),
          ("branco", "simbolo-branco.png", DARK, "fundo escuro, capa, fechamento"),
          ("preto", "simbolo-preto.png", WHITE, "documento impresso, peça 1 cor")]
for i, (t, f, fnd, uso) in enumerate(caixas):
    x = 0.6 + i * 2.92
    rect(s, x, 2.4, 2.72, 2.7, fnd, line=(LINE if fnd == WHITE else None))
    p = _a(f)
    iw, ih = Image.open(p).size
    hh = 1.85
    ww = hh * iw / ih  # proporcao real do arquivo
    pic(s, p, x + (2.72 - ww) / 2, 2.4 + (2.7 - hh) / 2, ww, hh)
    txt(s, x, 5.22, 2.7, 0.3, t, 13, DARK)
    txt(s, x, 5.52, 2.7, 0.6, uso, 10.5, GREY, ls=1.3)
txt(s, 9.6, 2.45, 3.1, 0.3, "quando usar", 10.5, ORANGE)
txt(s, 9.6, 2.85, 3.1, 2.4,
    ["como elemento de canto, sempre menor e discreto.",
     "nunca no lugar da logo em peça institucional.",
     "nunca em cima de foto sem área limpa."], 11.5, GREY, ls=1.4, space=9)
txt(s, 0.6, 6.35, 11.9, 0.5, "o símbolo é assinatura, não ilustração. se aparecer grande demais, virou enfeite.", 11.5, GREY)
symbol(s)
page(s)

# 10 área de reserva
s = blank(prs)
eyebrow(s, "área de reserva", "check-circulo")
title(s, ["o espaço ao redor", "é parte da logo."], y=0.95, size=28, w=8.6)
rect(s, 0.6, 2.4, 8.4, 3.7, WHITE, line=LINE)
area_marcada(s, 1.35, 3.0, 6.9, 2.55, None)
logoem(s, "horizontal-preto", 2.5, 3.62, 4.6)
c = s.shapes.add_connector(1, Inches(2.5), Inches(3.3), Inches(2.5), Inches(3.62))
c.line.color.rgb = ORANGE
c.line.width = Pt(1)
txt(s, 2.0, 3.16, 0.6, 0.3, "x", 13, ORANGE)
txt(s, 1.35, 5.6, 6.9, 0.3, "x = altura do símbolo “3”", 10, ORANGE, align=PP_ALIGN.CENTER)
spec(s, 9.25, 2.4, 3.48, 3.7, "regra", [
    ("margem", "mínima de 1x em todos os lados"),
    ("1x", "altura do símbolo"),
    ("vale para", "as 4 famílias"),
    ("exceção", "capa e fechamento de deck"),
])
txt(s, 0.6, 6.45, 11.9, 0.35,
    "a reserva é medida pela altura do símbolo, não pela altura da logo. numa versão vertical, a reserva é maior.", 11.5, GREY)
symbol(s)
page(s)

# 11 usos errados
s = blank(prs)
eyebrow(s, "usos errados", "alerta")
title(s, ["o que nunca fazer", "com a logo."], y=0.95, size=28, w=8.0)
erros = ["esticar ou achatar", "girar", "trocar as cores", "aplicar sombra", "contornar", "usar sobre foto cheia"]
for i, e in enumerate(erros):
    col, row = i % 3, i // 3
    x = 0.6 + col * 4.07
    y = 2.35 + row * 2.1
    rect(s, x, y, 3.85, 1.5, CARD, line=LINE)
    if i == 0:
        # exemplo de uso errado: a logo esticada. a imagem e gerada ja com a
        # proporcao errada e inserida nessa mesma proporcao, para a distorcao
        # ser a do exemplo e nao um artefato de insercao.
        alvo_w, alvo_h = 2.30, 0.42
        src = Image.open(_a("logo-horizontal-preto.png")).convert("RGBA")
        tmp = "work/brand2026/tmp_esticada.png"
        src.resize((int(alvo_w * 300), int(alvo_h * 300)), Image.LANCZOS).save(tmp)
        pic(s, tmp, x + 0.75, y + 0.55, alvo_w, alvo_h)
    elif i == 1:
        p = s.shapes.add_picture(_a("logo-horizontal-preto.png"), Inches(x + 0.6), Inches(y + 0.25), width=Inches(2.5))
        p.rotation = 12
    elif i == 2:
        s.shapes.add_picture(_a("logo-horizontal-laranja-branco.png"), Inches(x + 0.5), Inches(y + 0.55), width=Inches(2.8))
    elif i == 3:
        p = s.shapes.add_picture(_a("logo-horizontal-preto.png"), Inches(x + 0.5), Inches(y + 0.5), width=Inches(2.8))
        p.shadow.inherit = True
    elif i == 4:
        p = s.shapes.add_picture(_a("logo-horizontal-preto.png"), Inches(x + 0.5), Inches(y + 0.5), width=Inches(2.8))
        p.line.color.rgb = ORANGE
        p.line.width = Pt(2.5)
    else:
        rect(s, x + 0.15, y + 0.15, 3.55, 1.2, RGBColor(0x8E, 0x6A, 0x55))
        s.shapes.add_picture(_a("logo-horizontal-branco.png"), Inches(x + 0.5), Inches(y + 0.45), width=Inches(2.8))
    txt(s, x, y + 1.55, 3.85, 0.3, "× " + e, 11.5, ORANGE)
txt(s, 0.6, 6.75, 11.9, 0.3, "em dúvida, use o arquivo original. não redesenhe, não recorte, não “melhore”.", 11, GREY)
symbol(s)
page(s)

# 09 divisor cor
divisor(prs, "02 · cor", ["duas cores,", "nenhuma terceira."],
        "o laranja é energia e ação. o grafite é seriedade. juntos, fazem a marca parecer firme sem ficar fria.")

# 10 paleta
s = blank(prs)
eyebrow(s, "paleta", "tag")
title(s, ["as cores oficiais", "e as de apoio."], y=0.95, size=28, w=8.4)
# laranja
rect(s, 0.6, 2.35, 5.9, 1.9, ORANGE)
txt(s, 0.95, 2.55, 5.0, 0.3, "laranja terceirizou", 13, WHITE)
txt(s, 0.95, 2.95, 5.0, 0.9, ["#E15125", "R 225 · G 81 · B 37 · C 0 M 79 Y 87 K 0"], 17, WHITE, ls=1.4)
txt(s, 0.95, 3.75, 5.0, 0.3, "pantone 1655 C (referência de impressão)", 10, RGBColor(0xFF, 0xE0, 0xD6))
# grafite
rect(s, 6.83, 2.35, 5.9, 1.9, DARK)
txt(s, 7.18, 2.55, 5.0, 0.3, "grafite", 13, WHITE)
txt(s, 7.18, 2.95, 5.0, 0.9, ["#2B2C2E", "R 43 · G 44 · B 46 · C 0 M 0 Y 0 K 100"], 17, WHITE, ls=1.4)
txt(s, 7.18, 3.75, 5.0, 0.3, "preto de texto e fundo institucional", 10, RGBColor(0x9A, 0x9B, 0x9D))
# apoio
apoio = [("#FFFFFF", WHITE, "branco de fundo", DARK), ("#F5F5F6", RGBColor(0xF5, 0xF5, 0xF6), "cinza de card", DARK),
         ("#E3E4E6", RGBColor(0xE3, 0xE4, 0xE6), "linha e divisória", DARK), ("#6B6C6E", RGBColor(0x6B, 0x6C, 0x6E), "cinza de texto", WHITE),
         ("#C7C8CA", RGBColor(0xC7, 0xC8, 0xCA), "texto de apoio", WHITE), ("#FBE9E3", RGBColor(0xFB, 0xE9, 0xE3), "pêssego de selo", DARK)]
txt(s, 0.6, 4.55, 5.0, 0.3, "cores de apoio", 10.5, ORANGE)
for i, (hexv, cor, nome, fg) in enumerate(apoio):
    x = 0.6 + i * 2.02
    rect(s, x, 4.95, 1.85, 1.1, cor, line=LINE)
    txt(s, x + 0.12, 5.06, 1.6, 0.3, hexv, 10.5, fg)
    txt(s, x + 0.12, 5.55, 1.65, 0.4, nome, 9, fg)
txt(s, 0.6, 6.3, 11.9, 0.4, "nenhuma cor fora desta lista entra em peça da marca. degradê, neon e dourado estão proibidos.", 11.5, GREY)
symbol(s)
page(s)

# 11 proporção
s = blank(prs)
eyebrow(s, "proporção", "check-circulo")
title(s, ["quanto de cada cor", "em cada peça."], y=0.95, size=28, w=8.4)
barras = [("peça institucional", [("branco", 65, WHITE), ("grafite", 25, DARK), ("laranja", 10, ORANGE)]),
          ("peça de campanha", [("branco", 45, WHITE), ("grafite", 25, DARK), ("laranja", 30, ORANGE)]),
          ("peça social", [("grafite", 55, DARK), ("branco", 25, WHITE), ("laranja", 20, ORANGE)])]
y = 2.4
for nome, partes in barras:
    txt(s, 0.6, y, 3.0, 0.3, nome, 12, DARK)
    x = 3.75
    for rot, pct, cor in partes:
        w = 7.6 * pct / 100.0
        rect(s, x, y - 0.04, w, 0.42, cor, line=LINE)
        if pct >= 12:
            txt(s, x + 0.1, y - 0.04, w - 0.2, 0.42, "%d%%" % pct, 9.5, (WHITE if cor != WHITE else GREY), anchor=MSO_ANCHOR.MIDDLE)
        x += w
    y += 0.95
txt(s, 0.6, 5.35, 11.9, 0.35, "regra do laranja", 10.5, ORANGE)
txt(s, 0.6, 5.7, 11.9, 1.0,
    ["o laranja é acento, não fundo de página inteira. quando ele domina, a marca fica infantil e a leitura cansa.",
     "em peça de campanha pode subir para 30%. em documento e proposta, não passar de 10%."], 12.5, GREY, ls=1.4, space=6)
symbol(s)
page(s)

# 12 contraste
s = blank(prs)
eyebrow(s, "contraste e fundo", "olho-cortado")
title(s, ["onde a logo pode", "e onde ela desaparece."], y=0.95, size=28, w=8.8)
combos = [("branco sobre grafite", "horizontal-branco", DARK, True),
          ("preto sobre branco", "horizontal-preto", WHITE, True),
          ("branco sobre laranja", "horizontal-branco", ORANGE, True),
          ("preto sobre grafite", "horizontal-preto", DARK, False)]
for i, (t, var, fnd, ok) in enumerate(combos):
    x = 0.6 + i * 3.07
    rect(s, x, 2.4, 2.9, 1.9, fnd, line=(LINE if fnd == WHITE else None))
    logoem(s, var, x + 0.42, 2.95, 2.05)
    txt(s, x, 4.42, 2.9, 0.3, ("✓ " if ok else "× ") + t, 10.5, ORANGE if not ok else DARK)
txt(s, 0.6, 5.1, 11.9, 0.35, "sobre foto", 10.5, ORANGE)
txt(s, 0.6, 5.45, 11.9, 1.2,
    ["só com área limpa ou com véu de 60% de grafite. se a foto for clara ou cheia de detalhe, escolha outra foto.",
     "a logo nunca compete com a imagem: ela assina."], 12.5, GREY, ls=1.4, space=6)
symbol(s)
page(s)

# 13 divisor tipo
divisor(prs, "03 · tipografia", ["uma fonte só,", "bem usada."],
        "ampleSoft light em tudo. o que muda é tamanho, peso e espaço. misturar fontes é o jeito mais rápido de parecer amador.")

# 14 tipografia
s = blank(prs)
eyebrow(s, "tipografia", "documento-grafico")
title(s, ["ampleSoft light.", "minúscula por padrão."], y=0.95, size=28, w=9.4)
card(s, 0.6, 2.35, 7.4, 2.3)
txt(s, 0.95, 2.55, 6.6, 1.7, "aabbccddeeffgghhiijjkkllmmnnooppqqrrssttuuvvwwxxyyzz", 21, DARK, ls=1.35)
txt(s, 0.95, 3.85, 6.6, 0.5, "0123456789 .,:;!?@#%&*()[]{}", 15, GREY)
spec(s, 8.3, 2.35, 4.43, 2.3, "fonte oficial", [
    ("família", "ampleSoft light"),
    ("fallback", "inter light / segoe ui light"),
    ("peso", "só regular. sem bold"),
    ("caixa", "tudo minúsculo, exceto sigla"),
])
txt(s, 0.6, 4.95, 7.4, 0.35, "hierarquia", 10.5, ORANGE)
hier = [("título de capa", "44 – 64 pt", "laranja ou branco"),
        ("título de slide", "28 – 32 pt", "grafite"),
        ("subtítulo / lead", "14 – 16 pt", "cinza #6B6C6E"),
        ("corpo", "11 – 13 pt", "grafite ou cinza"),
        ("legenda e nota", "9 – 10 pt", "cinza claro #C7C8CA")]
y = 5.3
for a, b, c in hier:
    txt(s, 0.6, y, 2.6, 0.26, a, 11, DARK)
    txt(s, 3.3, y, 1.6, 0.26, b, 11, GREY)
    txt(s, 5.0, y, 3.1, 0.26, c, 11, GREY)
    y += 0.3
txt(s, 8.3, 5.0, 4.4, 1.5,
    ["negrito não existe na marca. para dar ênfase, use tamanho, cor ou espaço. nunca peso.", "a fonte não tem “º” e “ª”: escreva “1o” como “1º” apenas em texto externo, ou reescreva."], 11, GREY, ls=1.4, space=8)
symbol(s)
page(s)

# 15 exemplo tipográfico
s = blank(prs, "dark")
txt(s, 0.6, 1.2, 9.0, 0.3, "exemplo de hierarquia", 11, ORANGE)
txt(s, 0.6, 1.75, 10.6, 1.0, "seu financeiro organizado.", 44, WHITE)
txt(s, 0.6, 2.95, 10.6, 0.9, "sua decisão com direção.", 44, WHITE)
txt(s, 0.6, 4.15, 9.4, 1.2,
    "mais do que terceirizar o financeiro: dados organizados, leitura gerencial e direcionamento para a tomada de decisão.",
    15, LGREY, ls=1.4)
txt(s, 0.6, 5.75, 9.0, 0.3, "capa · 44 pt · linha 1,04 · branco sobre grafite", 10, RGBColor(0x8A, 0x8B, 0x8D))
symbol(s, dark=True, h=2.0, x=11.6, y=4.7)
page(s, dark=True)

# 16 divisor composição
divisor(prs, "04 · composição", ["grid, margem", "e respiro."],
        "o layout é sempre o mesmo: margem de 0,6, doze colunas, título no topo e símbolo no canto. o que muda é o conteúdo.")

# 17 grid
s = blank(prs)
eyebrow(s, "grid", "camadas")
title(s, ["a diagramação padrão", "do slide 16:9."], y=0.95, size=28, w=8.8)
# slide mockup com grid
mx, my, mw, mh = 0.6, 2.35, 7.6, 4.28
rect(s, mx, my, mw, mh, WHITE, line=LINE)
cols = 12
cw = mw / cols
for i in range(cols):
    if i % 2 == 0:
        rect(s, mx + i * cw, my, cw, mh, RGBColor(0xFA, 0xF7, 0xF5))
for i in range(cols + 1):
    c = s.shapes.add_connector(1, Inches(mx + i * cw), Inches(my), Inches(mx + i * cw), Inches(my + mh))
    c.line.color.rgb = RGBColor(0xF0, 0xD9, 0xD1)
    c.line.width = Pt(0.5)
# margem
area_marcada(s, mx + 0.6 * mw / 13.333, my + 0.5 * mh / 7.5, mw - 1.2 * mw / 13.333, mh - 1.0 * mh / 7.5, None)
txt(s, mx + 0.35, my + 0.18, 4.0, 0.3, "área útil · margem 0,6 in", 9, ORANGE)
txt(s, mx + 0.6, my + 1.0, 4.6, 0.8, "título entra aqui,\nquebrado em duas linhas.", 13, DARK, ls=1.25)
spec(s, 8.55, 2.35, 4.18, 2.1, "medidas", [
    ("formato", "16:9 · 13,333 × 7,5 in"),
    ("margem", "0,6 in em todos os lados"),
    ("colunas", "12 · gutter 0,22 in"),
    ("símbolo", "canto inferior direito, 0,45 in da borda"),
])
txt(s, 8.55, 4.65, 4.2, 0.3, "regra de respiro", 10.5, ORANGE)
txt(s, 8.55, 5.0, 4.2, 1.6,
    ["nunca encher o slide. se não cabe, é sinal de que o conteúdo precisa ser dividido em dois.",
     "um slide, uma ideia."], 11.5, GREY, ls=1.4, space=8)
symbol(s)
page(s)

# 18 divisor elementos
divisor(prs, "05 · elementos", ["ícone, foto", "e gráfico."],
        "os elementos existem para ajudar a leitura, não para decorar. cada um tem uma função e um limite.")

# 19 ícones
s = blank(prs)
eyebrow(s, "ícones", "check-circulo")
title(s, ["traço fino, uma cor,", "nunca decorativo."], y=0.95, size=28, w=8.8)
nomes = ["conversa", "documento-grafico", "relogio", "cofrinho", "pessoa-check", "escudo",
         "camadas", "pessoas", "calendario-relogio", "cedula", "engrenagem", "escudo"]
x, y = 0.6, 2.4
for i, n in enumerate(nomes):
    col = i % 6
    xx = 0.6 + col * 1.32
    if i == 6:
        xx = 0.6
        y += 1.4
    card(s, xx, y, 1.15, 1.15)
    pic(s, os.path.join(ICONES, n + ".png"), xx + 0.3, y + 0.3, 0.55, 0.55)
txt(s, 9.0, 2.4, 3.7, 0.3, "regras", 10.5, ORANGE)
txt(s, 9.0, 2.8, 3.75, 3.4,
    ["só laranja sobre fundo claro, branco sobre fundo escuro.",
     "tamanho entre 0,24 e 0,6 in. acima disso, vira ilustração.",
     "nunca dentro de círculo colorido, nunca com sombra.",
     "um ícone por bloco, no máximo."], 11.5, GREY, ls=1.4, space=10)
txt(s, 0.6, 6.05, 11.9, 0.5, "os ícones vêm do mesmo conjunto. não misturar família de traço diferente.", 11.5, GREY)
symbol(s)
page(s)

# 20 foto
s = blank(prs)
eyebrow(s, "fotografia", "olho-cortado")
title(s, ["gente trabalhando.", "não banco de imagem."], y=0.95, size=28, w=9.0)
cards_f = [("sim", "time real, mesa real, tela real. luz natural. mão na massa."),
           ("sim", "close de número, papel, extrato, sistema. o detalhe conta a história."),
           ("não", "aperto de mão, gráfico subindo, pessoa sorrindo para o laptop."),
           ("não", "foto escura com texto por cima. nunca.")]
for i, (t, c) in enumerate(cards_f):
    x = 0.6 + (i % 2) * 6.17
    y = 2.35 + (i // 2) * 1.85
    card(s, x, y, 5.95, 1.65, fill=(PINK if t == "sim" else CARD), line=None if t == "sim" else LINE)
    txt(s, x + 0.3, y + 0.22, 0.8, 0.3, t, 11, ORANGE)
    txt(s, x + 1.05, y + 0.22, 4.6, 1.2, c, 12.5, DARK, ls=1.35)
txt(s, 0.6, 6.25, 11.9, 0.5, "tratamento: dessaturar levemente e manter o laranja só no que é da marca.", 11.5, GREY)
symbol(s)
page(s)

# 21 gráficos
s = blank(prs)
eyebrow(s, "dados e gráficos", "documento-grafico")
title(s, ["o gráfico segue", "a paleta. sempre."], y=0.95, size=28, w=8.4)
# exemplo de barras
bx, by = 0.6, 2.4
rect(s, bx, by, 6.2, 3.4, WHITE, line=LINE)
bars = [("jan", 0.45), ("fev", 0.6), ("mar", 0.52), ("abr", 0.78), ("mai", 0.68), ("jun", 0.92)]
for i, (m, v) in enumerate(bars):
    h = 2.1 * v
    cor = ORANGE if i == 5 else RGBColor(0xD9, 0xDA, 0xDC)
    rect(s, bx + 0.65 + i * 0.88, by + 2.85 - h, 0.52, h, cor)
    txt(s, bx + 0.55 + i * 0.88, by + 2.95, 0.7, 0.25, m, 9, GREY)
txt(s, bx + 0.35, by + 0.25, 5.0, 0.3, "receita por mês · exemplo", 9.5, GREY)
txt(s, 7.15, 2.4, 5.6, 0.3, "regras de gráfico", 10.5, ORANGE)
txt(s, 7.15, 2.8, 5.62, 3.1,
    ["uma cor de destaque: só o dado que importa fica laranja.",
     "sem efeito 3d, sem sombra, sem gradiente.",
     "eixo sem linha pesada. número direto na barra quando der.",
     "título sempre com a leitura, não com o nome da variável."], 11.5, GREY, ls=1.4, space=10)
txt(s, 0.6, 6.1, 11.9, 0.5, "gráfico sem leitura é enfeite. escreva o que ele quer dizer antes de desenhar.", 11.5, GREY)
symbol(s)
page(s)

# 22 divisor aplicação
divisor(prs, "06 · aplicação", ["onde a marca", "aparece."],
        "quatro peças que a equipe vai produzir toda semana. se essas quatro estiverem certas, o resto segue.")

# 23 apresentação
s = blank(prs)
eyebrow(s, "apresentação", "camadas")
title(s, ["o slide padrão", "e suas variações."], y=0.95, size=28, w=8.4)
# miniaturas de slides
def mini_slide(x, y, dark=False, tipo="conteudo"):
    rect(s, x, y, 3.7, 2.08, DARK if dark else WHITE, line=None if dark else LINE)
    if tipo == "conteudo":
        txt(s, x + 0.16, y + 0.14, 1.4, 0.2, "eyebrow", 6.5, ORANGE)
        txt(s, x + 0.16, y + 0.36, 3.2, 0.5, ["título em duas", "linhas aqui."], 10, WHITE if dark else DARK, ls=1.1)
        for k in range(3):
            rect(s, x + 0.16 + k * 1.15, y + 1.05, 1.05, 0.75, RGBColor(0x3A, 0x3B, 0x3D) if dark else CARD)
        p = _a("simbolo-branco.png" if dark else "simbolo-laranja.png")
        pic_fit(s, p, x + 3.05, y + 1.3, 0.55, 0.7, esc=0.95)
    elif tipo == "capa":
        p = _a("logo-horizontal-branco.png")
        pic(s, p, x + 0.16, y + 0.14, 1.5)
        txt(s, x + 0.16, y + 0.9, 3.2, 0.7, ["título", "de capa."], 15, WHITE, ls=1.05)
        pic_fit(s, _a("simbolo-branco.png"), x + 2.95, y + 1.2, 0.6, 0.8, esc=0.92)
    else:
        txt(s, x + 0.16, y + 0.6, 3.2, 0.8, ["grande ideia", "em uma frase."], 13, WHITE, ls=1.1)
        pic_fit(s, _a("simbolo-branco.png"), x + 2.95, y + 1.2, 0.6, 0.8, esc=0.92)
mini_slide(0.6, 2.35, False, "conteudo")
mini_slide(4.55, 2.35, True, "capa")
mini_slide(8.5, 2.35, True, "divisor")
for x, l in [(0.6, "conteúdo"), (4.55, "capa"), (8.5, "divisor")]:
    txt(s, x, 4.52, 3.6, 0.3, l, 10, GREY)
spec(s, 0.6, 4.95, 5.9, 1.75, "o que nunca muda", [
    ("logo", "capa e fechamento"),
    ("símbolo", "canto inferior direito"),
    ("margem", "0,6 in"),
], dark=False)
spec(s, 6.83, 4.95, 5.9, 1.75, "o que pode variar", [
    ("fundo", "branco ou grafite"),
    ("número", "até 4 cards por slide"),
    ("imagem", "só quando for prova real"),
], dark=False)
symbol(s)
page(s)

# 24 proposta
s = blank(prs)
eyebrow(s, "proposta e contrato", "documento-grafico")
title(s, ["documento de cliente", "tem regra própria."], y=0.95, size=28, w=9.2)
# mockup A4
rect(s, 0.6, 2.35, 3.2, 4.2, WHITE, line=LINE)
logoem(s, "horizontal-preto", 0.85, 2.6, 1.4)
txt(s, 0.85, 4.25, 2.7, 1.6, ["proposta comercial", "cliente · data", "", "escopo, prazo, valor"], 8.5, GREY, ls=1.5)
rect(s, 0.85, 6.15, 2.7, 0.02, ORANGE)
txt(s, 4.1, 2.45, 4.3, 0.3, "capa", 10.5, ORANGE)
txt(s, 4.1, 2.8, 4.3, 1.6,
    ["logo completa centralizada ou no topo, título do documento e nome do cliente.",
     "sem imagem de banco, sem gráfico decorativo."], 11.5, GREY, ls=1.4, space=8)
txt(s, 4.1, 4.5, 4.3, 0.3, "páginas internas", 10.5, ORANGE)
txt(s, 4.1, 4.85, 4.3, 1.7,
    ["logo só no rodapé, pequena. título em grafite, tabela sem sombra, negativo em vermelho quando for análise financeira."], 11.5, GREY, ls=1.4)
txt(s, 8.7, 2.45, 4.0, 0.3, "regra de ouro", 10.5, ORANGE)
txt(s, 8.7, 2.8, 4.05, 3.4,
    ["proposta não é catálogo. é argumento: problema, caminho, escopo, valor.",
     "nada de análise do período anterior como prova, quando a proposta é de preço alto.",
     "nenhum travessão no texto. “terceirizou” sempre em minúsculo."], 11.5, GREY, ls=1.4, space=10)
symbol(s)
page(s)

# 25 social
s = blank(prs)
eyebrow(s, "social", "instagram")
title(s, ["post, carrossel e story", "com a mesma cara."], y=0.95, size=28, w=9.0)
# 3 mockups
for i, (rot, w_, h_) in enumerate([("post 1080×1080", 2.35, 2.35), ("carrossel", 2.35, 2.35), ("story 1080×1920", 1.55, 2.75)]):
    x = 0.6 + i * 2.55
    y = 2.4
    rect(s, x, y, w_, h_, DARK)
    if i < 2:
        txt(s, x + 0.18, y + 0.35, w_ - 0.36, 1.5, ["seu dinheiro", "sai todo mês."], 15, WHITE, ls=1.1)
        txt(s, x + 0.18, y + h_ - 0.55, 1.2, 0.3, "@termaisterceirizou", 6, LGREY)
        pic_fit(s, _a("simbolo-branco.png"), x + w_ - 0.55, y + h_ - 0.9, 0.4, 0.5, esc=0.9)
    else:
        txt(s, x + 0.16, y + 0.5, w_ - 0.32, 1.6, ["o mês", "fechou."], 15, WHITE, ls=1.1)
        pic_fit(s, _a("simbolo-branco.png"), x + w_ - 0.5, y + h_ - 0.85, 0.4, 0.5, esc=0.9)
    txt(s, x, y + h_ + 0.12, w_, 0.3, rot, 9.5, GREY)
txt(s, 8.3, 2.4, 4.45, 0.3, "regras sociais", 10.5, ORANGE)
txt(s, 8.3, 2.8, 4.45, 3.3,
    ["texto grande o suficiente para ler no celular sem zoom.",
     "fundo escuro para conteúdo de dor, claro para conteúdo de prova.",
     "o símbolo sempre no canto, pequeno.",
     "nunca logo completa dentro do post: ela já está no perfil."], 11.5, GREY, ls=1.4, space=10)
symbol(s)
page(s)

# 26 papelaria
s = blank(prs)
eyebrow(s, "papelaria e assinatura", "envelope")
title(s, ["o básico do dia a dia."], y=0.95, size=28, w=8.0)
# cartão
rect(s, 0.6, 2.4, 3.4, 2.0, DARK)
logoem(s, "horizontal-branco", 0.85, 2.62, 2.0)
txt(s, 0.85, 3.75, 2.9, 0.4, ["vinícius oliveira da costa", "(48) 99122-6496"], 7.5, LGREY, ls=1.5)
txt(s, 0.6, 4.55, 3.4, 0.3, "cartão · frente", 9.5, GREY)
rect(s, 4.2, 2.4, 3.4, 2.0, WHITE, line=LINE)
pic_fit(s, _a("simbolo-laranja.png"), 4.2, 2.4, 3.4, 2.0, esc=0.5)
txt(s, 4.2, 4.55, 3.4, 0.3, "cartão · verso", 9.5, GREY)
# assinatura email
card(s, 8.0, 2.4, 4.73, 2.0, fill=CARD, line=LINE)
logoem(s, "horizontal-preto", 8.28, 2.62, 1.5)
txt(s, 8.28, 3.5, 4.2, 0.8,
    ["vinícius oliveira da costa", "consultor financeiro · terceirizou", "(48) 99122-6496 · terceirizou.com.br"], 8, GREY, ls=1.5)
txt(s, 8.0, 4.55, 4.0, 0.3, "assinatura de e-mail", 9.5, GREY)
txt(s, 0.6, 5.2, 11.9, 0.35, "medidas", 10.5, ORANGE)
txt(s, 0.6, 5.55, 11.9, 1.1,
    ["cartão 9 × 5 cm, 300 g, laminação fosca · papel timbrado A4 com margem 2 cm · assinatura de e-mail sem imagem pesada, sempre com a versão curta da logo.",
     "fonte do e-mail: ampleSoft quando disponível; se não, arial 10 pt na cor grafite."], 11.5, GREY, ls=1.4, space=6)
symbol(s)
page(s)

# 27 arquivos
s = blank(prs)
eyebrow(s, "arquivos", "chaves")
title(s, ["o que está na pasta", "e como usar."], y=0.95, size=28, w=8.0)
cols = ["arquivo", "formato", "para que serve"]
rows = [["horizontal", "7 arquivos png + .ai", "branco, preto, laranja/preto, laranja/branco, com e sem assinatura"],
        ["quadrado", "5 arquivos png", "laranja/preto, laranja/branco, laranja, branco, preto"],
        ["vertical", "5 arquivos png", "laranja/preto, laranja/branco, laranja, branco, preto"],
        ["símbolo", "3 arquivos png", "laranja, branco, preto"],
        ["fonte ampleSoft", "ttf", "instalar na máquina antes de editar"],
        ["vetor da logo", "ai / svg", "para ampliar sem perder qualidade"]]
tabela(s, 0.6, 2.35, 12.13, cols, rows, cw=[2.5, 3.2, 6.43], rh=0.5, size=11.5, bold_col0=True)
txt(s, 0.6, 6.05, 11.9, 0.6, "todos os arquivos originais ficam na pasta oficial da marca. não usar versão retirada de post ou de print.", 11.5, GREY)
symbol(s)
page(s)

# 28 checklist
s = blank(prs)
eyebrow(s, "checklist final", "check-circulo")
title(s, ["antes de mandar para", "o cliente ou publicar."], y=0.95, size=28, w=9.2)
checks = ["a logo é o arquivo original?",
          "a área de reserva está respeitada?",
          "só entrou cor da paleta?",
          "a fonte é ampleSoft?",
          "o laranja é acento, não fundo?",
          "tem mais de um ícone por bloco?",
          "o símbolo está no canto, discreto?",
          "tem travessão ou “terceirizou” maiúsculo?"]
for i, c in enumerate(checks):
    col = i // 4
    y = 2.4 + (i % 4) * 0.82
    x = 0.6 + col * 6.2
    pic(s, os.path.join(ICONES, "check-circulo.png"), x, y + 0.02, 0.26, 0.26)
    txt(s, x + 0.4, y, 5.5, 0.5, c, 13, DARK, ls=1.25)
txt(s, 0.6, 6.1, 11.9, 0.5, "um “não” é motivo para voltar. nenhuma exceção vale a pena.", 12, ORANGE)
symbol(s)
page(s)

# 29 fecho
s = blank(prs, "dark")
logo(s, "horizontal-branco", 0.6, 0.55, 3.0)
txt(s, 0.6, 2.5, 10.8, 1.7, ["a marca é o que", "não muda quando muda a peça."], 36, WHITE, ls=1.12)
txt(s, 0.6, 4.75, 9.6, 1.0, ["manual de identidade visual · v1 · 2026",
                              "terceirização financeira consultiva · florianópolis e tubarão/sc"], 12, RGBColor(0x9A, 0x9B, 0x9D), ls=1.4)
symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
page(s, dark=True)

cp = prs.core_properties
cp.title = "manual de identidade visual · terceirizou · 2026"
cp.author = "terceirizou"
cp.subject = "logo, cor, tipografia, grid e aplicação"
prs.save(OUT)
print("ok", OUT, len(prs.slides), "slides")
