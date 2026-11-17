#!/usr/bin/env python3
"""Aponta texto cuja ULTIMA linha impressa passa do fundo da faixa em que comeca.

Defeito que originou (13/11, slide 21 do posicionamento): a tabela desenhada
terminava em 5,95" e a nota de apoio tinha o topo em 5,60". A nota imprimia
dentro da faixa cinza da ultima linha. O teste de OVERFLOW nao via (o texto
cabia na propria caixa) e o de colisao tambem nao (nao encostava em imagem).

Regra estreita, para nao gerar ruido:
  - o TOPO do texto cai dentro de um retangulo preenchido (faixa/card);
  - a ultima linha REALMENTE impressa (medida com a fonte, nao a caixa do
    shape, que costuma ser bem maior) termina abaixo do fundo desse retangulo.
Texto inteiramente contido no retangulo e uso normal (header, card, celula).
"""
import sys, os
from pptx import Presentation
from PIL import ImageFont

MARGEM = 0.06  # pol
FONT_PATH = os.path.expanduser("~/.local/share/fonts/AmpleSoftLight-Regular.ttf")
_FONTS = {}


def fonte(px):
    if px not in _FONTS:
        _FONTS[px] = ImageFont.truetype(FONT_PATH, px)
    return _FONTS[px]


def caixa(sh):
    return (sh.left / 914400, sh.top / 914400,
            (sh.left + sh.width) / 914400, (sh.top + sh.height) / 914400)


def fundo_impresso(sh):
    """y da ultima linha realmente impressa, quebrada pela largura da caixa."""
    L, T, R, B = caixa(sh)
    limite = (R - L) * 96.0
    y = T
    for p in sh.text_frame.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        sz = max((r.font.size.pt if r.font.size else 12) for r in runs)
        txt = "".join(r.text for r in runs)
        f = fonte(max(1, int(round(sz * 96 / 72))))
        n, atual = 1, ""
        for w in txt.split(" "):
            t = (atual + " " + w).strip()
            if f.getlength(t) <= limite or not atual:
                atual = t
            else:
                n += 1
                atual = w
        y += n * sz * (p.line_spacing or 1.2) / 72.0
    return min(y, B)


def checar(path, verbose=True):
    prs = Presentation(path)
    probs = []
    for n, s in enumerate(prs.slides, 1):
        textos, faixas = [], []
        for sh in s.shapes:
            try:
                g = caixa(sh)
            except TypeError:
                continue
            if sh.has_text_frame and sh.text_frame.text.strip():
                textos.append((sh, g, sh.text_frame.text.strip().replace("\n", " ")[:44]))
            elif sh.shape_type == 1:
                faixas.append((sh.name, g))
        for sh, tg, txt in textos:
            fundo = fundo_impresso(sh)
            for fnome, fg in faixas:
                if min(tg[2], fg[2]) - max(tg[0], fg[0]) <= 0.2:
                    continue
                if fg[1] + MARGEM < tg[1] < fg[3] - MARGEM and fundo > fg[3] + MARGEM:
                    probs.append((n, txt,
                                  "topo %.2f, faixa %.2f-%.2f, texto imprime ate %.2f"
                                  % (tg[1], fg[1], fg[3], fundo)))
    if verbose:
        print("==", os.path.basename(path), "texto vazando da faixa:", len(probs))
        for p in probs:
            print("  ", p)
    return probs


if __name__ == "__main__":
    t = 0
    for f in sys.argv[1:]:
        t += len(checar(f))
    print("TOTAL:", t)
    sys.exit(1 if t else 0)
