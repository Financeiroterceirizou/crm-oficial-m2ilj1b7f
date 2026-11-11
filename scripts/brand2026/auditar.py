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
