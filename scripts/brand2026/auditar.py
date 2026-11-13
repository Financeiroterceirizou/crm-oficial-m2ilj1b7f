#!/usr/bin/env python3
"""Auditoria de layout: mede o texto real (AmpleSoft) e aponta overflow."""
import sys, glob, os
from pptx import Presentation
from pptx.util import Emu
from PIL import ImageFont

FONT_PATH = os.path.expanduser("~/.local/share/fonts/AmpleSoftLight-Regular.ttf")
EMU_PT = 12700
SLIDE_W = 13.3333
SLIDE_H = 7.5


def wrap_lines(texto, size_pt, box_w_in, font_cache={}):
    key = round(size_pt * 4) / 4
    if key not in font_cache:
        font_cache[key] = ImageFont.truetype(FONT_PATH, max(1, int(round(size_pt * 96 / 72))))
    f = font_cache[key]
    maxpx = box_w_in * 96
    linhas = 0
    for par in str(texto).split("\n"):
        palavras = par.split(" ")
        atual = ""
        if not par.strip():
            linhas += 1
            continue
        for p in palavras:
            t = (atual + " " + p).strip()
            if f.getlength(t) <= maxpx or not atual:
                atual = t
            else:
                linhas += 1
                atual = p
        if atual:
            linhas += 1
    return max(1, linhas)


def audit(path, verbose=True):
    prs = Presentation(path)
    probs = []
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:
            try:
                L, T = sh.left / 914400, sh.top / 914400
                W, Hh = sh.width / 914400, sh.height / 914400
            except TypeError:
                continue
            if L + W > SLIDE_W + 0.02 or T + Hh > SLIDE_H + 0.02 or L < -0.02 or T < -0.05:
                probs.append((i, "FORA", sh.name, round(L, 2), round(T, 2), round(W, 2), round(Hh, 2)))
            if not sh.has_text_frame:
                continue
            tf = sh.text_frame
            total_h = 0.0
            for p in tf.paragraphs:
                ts = [r for r in p.runs if r.text.strip()]
                if not ts:
                    total_h += 0.0
                    continue
                size = max((r.font.size.pt if r.font.size else 12) for r in ts)
                txt = "".join(r.text for r in ts)
                ls = p.line_spacing or 1.2
                n = wrap_lines(txt, size, max(0.2, W))
                total_h += n * size * ls / 72.0
            if total_h > Hh + 0.06:
                probs.append((i, "OVERFLOW", sh.name, round(total_h, 2), round(Hh, 2),
                              str(sh.text_frame.text)[:60].replace("\n", " ")))
    if verbose:
        print("==", os.path.basename(path), len(prs.slides), "slides")
        for p in probs:
            print("  ", p)
        if not probs:
            print("   sem problemas")
    return probs


if __name__ == "__main__":
    for f in sys.argv[1:]:
        audit(f)


def colisoes(path, verbose=True):
    """texto que invade imagem (simbolo, logo, icone) ou sai do slide"""
    prs = Presentation(path)
    probs = []
    for i, s in enumerate(prs.slides, 1):
        textos, imgs = [], []
        for sh in s.shapes:
            try:
                box = (sh.left / 914400, sh.top / 914400,
                       (sh.left + sh.width) / 914400, (sh.top + sh.height) / 914400)
            except TypeError:
                continue
            if sh.shape_type == 13:
                # simbolo/logo sao imagens de marca: texto nao pode invadir
                imgs.append((sh.name, box))
            elif sh.has_text_frame and sh.text_frame.text.strip():
                textos.append((sh.name, box, sh.text_frame.text.strip()[:44]))
        for tn, tb, tt in textos:
            for iN, ib in imgs:
                ox = min(tb[2], ib[2]) - max(tb[0], ib[0])
                oy = min(tb[3], ib[3]) - max(tb[1], ib[1])
                if ox > 0.03 and oy > 0.03:
                    area = ox * oy
                    if area > 0.08:
                        probs.append((i, "TEXTO×IMAGEM", tn, iN, round(ox, 2), round(oy, 2), tt))
    if verbose:
        print("==", os.path.basename(path), "colisoes:", len(probs))
        for p in probs:
            print("  ", p)
    return probs


def sobras(path, verbose=True):
    """texto que nao cabe na propria caixa (estimativa com a fonte real)"""
    prs = Presentation(path)
    probs = []
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            W = sh.width / 914400
            Hh = sh.height / 914400
            total = 0.0
            for p in sh.text_frame.paragraphs:
                ts = [r for r in p.runs if r.text.strip()]
                if not ts:
                    continue
                size = max((r.font.size.pt if r.font.size else 12) for r in ts)
                txt = "".join(r.text for r in ts)
                ls = p.line_spacing or 1.2
                n = wrap_lines(txt, size, max(0.2, W))
                total += n * size * ls / 72.0
            if total > Hh + 0.05:
                probs.append((i, sh.name, round(total, 2), round(Hh, 2), sh.text_frame.text.strip()[:50]))
    if verbose:
        print("==", os.path.basename(path), "sobras:", len(probs))
        for p in probs:
            print("  ", p)
    return probs


def texto_invade_imagem(path, verbose=True):
    """mede a largura REAL de cada linha (fonte AmpleSoft) e compara com a area do simbolo/logo."""
    from PIL import ImageFont
    prs = Presentation(path)
    probs = []
    cache = {}

    def fonte(sz):
        k = max(1, int(round(sz * 96 / 72)))
        if k not in cache:
            cache[k] = ImageFont.truetype(FONT_PATH, k)
        return cache[k]

    for i, s in enumerate(prs.slides, 1):
        imgs = []
        for sh in s.shapes:
            if sh.shape_type == 13:
                imgs.append((sh.name, (sh.left / 914400, sh.top / 914400,
                                       (sh.left + sh.width) / 914400, (sh.top + sh.height) / 914400)))
        for sh in s.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            L = sh.left / 914400
            T = sh.top / 914400
            Hh = sh.height / 914400
            linhas = []
            y = T
            ok = True
            for p in sh.text_frame.paragraphs:
                ts = [r for r in p.runs if r.text]
                if not ts:
                    continue
                sz = max((r.font.size.pt if r.font.size else 12) for r in ts)
                txt = "".join(r.text for r in ts)
                f = fonte(sz)
                larg = f.getlength(txt) / 96.0
                ls = p.line_spacing or 1.2
                alt = sz * ls / 72.0
                linhas.append((txt, L, y, L + larg, y + alt))
                y += alt
            for ln in linhas:
                for iN, ib in imgs:
                    ox = min(ln[3], ib[2]) - max(ln[1], ib[0])
                    oy = min(ln[4], ib[3]) - max(ln[2], ib[1])
                    if ox > 0.02 and oy > 0.02:
                        probs.append((i, sh.name, iN, ln[0][:52], round(ox, 2)))
    if verbose:
        print("==", os.path.basename(path), "texto que invade imagem:", len(probs))
        for p in probs:
            print("  ", p)
    return probs
