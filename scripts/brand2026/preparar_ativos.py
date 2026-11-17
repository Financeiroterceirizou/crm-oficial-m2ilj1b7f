#!/usr/bin/env python3
"""Prepara os ativos de marca a partir do kit oficial 2023.

Le a pasta do zip original (qualquer normalizacao unicode no nome do arquivo),
recorta o transparente e grava nomes limpos em work/brand2026/ativos/.
"""
import glob, os, re, unicodedata
import numpy as np
from PIL import Image

BASE = "work/brand2026/insumos/logo/Nova Logo ter mais terceirizou 2023"
OUT = "work/brand2026/ativos"
MAXW = 2400


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def indexar():
    idx = []
    for f in glob.glob(os.path.join(BASE, "*.png")):
        n = norm(os.path.basename(f))
        idx.append((n, f))
    return idx


def chave(nome):
    """extrai o identificador entre o prefixo e o '-rgb' do nome normalizado"""
    m = re.search(r"terceirizou-(.+?)-rgb", nome)
    return m.group(1) if m else nome


def achar(idx, exata):
    return [(n, f) for n, f in idx if chave(n) == exata]


# cor oficial da marca (cartao de cores). as artes do kit 2023 vieram em #FF501C.
ALVO = (0xE1, 0x51, 0x25)
RECOLORIR = True


def recolorir(im):
    """troca o laranja da arte pela cor oficial, preservando alfa e antialias"""
    a = np.array(im).astype(int)
    al = a[:, :, 3]
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    laranja = (al > 8) & (r > 120) & (r - b > 40) & (r - g > 40)
    if not laranja.any():
        return im
    a[:, :, 0] = np.where(laranja, ALVO[0], r)
    a[:, :, 1] = np.where(laranja, ALVO[1], g)
    a[:, :, 2] = np.where(laranja, ALVO[2], b)
    return Image.fromarray(a.astype("uint8"), "RGBA")


def exportar(src, dst, maxw=MAXW):
    im = Image.open(src).convert("RGBA")
    im = im.crop(im.getbbox())
    if RECOLORIR:
        im = recolorir(im)
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, dst))
    return im.size


def um(idx, termos, dst, maxw=MAXW):
    achados = achar(idx, termos)
    if len(achados) != 1:
        raise SystemExit("ambiguo/vazio: %s -> %s" % (termos, [os.path.basename(f) for _, f in achados]))
    sz = exportar(achados[0][1], dst, maxw)
    print("%-38s %-22s %s" % (dst, sz, os.path.basename(achados[0][1])[:46]))
    return achados[0][1]


def por_copia(idx, numero, dst, maxw=MAXW):
    """quando o nome oficial repete (duas 'preto sem tagline'), escolhe pelo numero da copia"""
    achados = [(n, f) for n, f in idx if ("copia %d" % numero) in n]
    if len(achados) != 1:
        raise SystemExit("copia %d ambigua: %s" % (numero, [os.path.basename(f) for _, f in achados]))
    sz = exportar(achados[0][1], dst, maxw)
    print("%-38s %-22s %s" % (dst, sz, os.path.basename(achados[0][1])[:46]))


def main():
    idx = indexar()
    # horizontais
    um(idx, "horizontal-branco-com-tagline", "logo-horizontal-branco.png")
    um(idx, "horizontal-branco-sem-tagline", "logo-horizontal-branco-sem-tagline.png")
    um(idx, "horizontal-preto-com-tagline", "logo-horizontal-preto.png")
    um(idx, "horizontal-laranja-branco-com-tagline", "logo-horizontal-laranja-branco.png")
    um(idx, "horizontal-laranja-preto-com-tagline", "logo-horizontal-laranja-preto.png")
    um(idx, "horizontal-laranja-branco-sem-tagline", "logo-horizontal-laranja-branco-sem-tagline.png")
    # o arquivo "preto sem tagline" copia 7 veio com simbolo laranja: o preto puro e a copia 12
    por_copia(idx, 12, "logo-horizontal-preto-sem-tagline.png")
    por_copia(idx, 7, "logo-horizontal-laranja-preto-sem-tagline.png")

    # verticais
    um(idx, "vertical-branco", "logo-vertical-branco.png")
    um(idx, "vertical-laranja", "logo-vertical-laranja.png")
    um(idx, "vertical-laranja-branco", "logo-vertical-laranja-branco.png")
    um(idx, "vertical-laranja-preto", "logo-vertical-laranja-preto.png")
    um(idx, "vertical-preto", "logo-vertical-preto.png")

    # simbolo
    um(idx, "simbolo-laranja", "simbolo-laranja.png", 1200)
    um(idx, "simbolo-branco", "simbolo-branco.png", 1200)
    um(idx, "simbolo-preto", "simbolo-preto.png", 1200)

    # quadrados (bloco)
    um(idx, "quadrado-laranja-branco", "quadrado-laranja-branco.png")
    um(idx, "quadrado-laranja-preto", "quadrado-laranja-preto.png")
    um(idx, "quadrado-laranja", "quadrado-laranja.png")
    um(idx, "quadrado-branco", "quadrado-branco.png")
    um(idx, "quadrado-preto", "quadrado-preto.png")


if __name__ == "__main__":
    main()
