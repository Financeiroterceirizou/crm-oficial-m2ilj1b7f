#!/usr/bin/env python3
"""Corrige o laranja do vetor oficial da logo 2023 (.ai) para #E15125.

RAIZ DA DIVERGENCIA: o .ai NAO esta em sRGB, esta em Adobe RGB (1998)
(ICCBased, objeto 43). Nele o laranja esta gravado como (255, 80, 28), que
em sRGB vira #FF4F0F. Por isso o vetor nunca "batia" com o cartao de cores,
que fala #E15125 (sRGB).

#E15125 em sRGB = (196, 82, 44) em Adobe RGB, com retorno exato (conferido).

O arquivo tem DUAS camadas que guardam a cor:
  1. PDF (o que o visualizador mostra): operador `1 0.314 0.11 scn`
  2. Nativa do Illustrator (o que o Illustrator edita): AIPrivateData3..10,
     um unico fluxo zlib fatiado em blocos de 65536 bytes, com a cor
     (1, 0.313725490196078, 0.109803921568627) repetida 44 vezes

Uso: python3 corrigir_ai.py <origem.ai> <destino.ai>
"""
import sys, re, zlib
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, IndirectObject, NameObject

R, G, B = 196 / 255.0, 82 / 255.0, 44 / 255.0
NOVO_NATIVO = ("%.15g %.15g %.15g" % (R, G, B)).encode()
ANTIGO_NATIVO = b"1 0.313725490196078 0.109803921568627"
NOVO_PDF = ("%.6f %.6f %.6f" % (R, G, B)).encode()
PREFIXO = b"%AI12_CompressedData"
PRIMEIRO, ULTIMO = 48, 55


def ler_nativo(raw):
    """o fluxo zlib comeca no objeto 48 (%AI12_CompressedData) e vai ate 55"""
    partes = []
    for n in range(PRIMEIRO, ULTIMO + 1):
        m = re.search(rb"(?<!\d)%d 0 obj" % n, raw)
        if not m:
            raise SystemExit("objeto %d nao encontrado" % n)
        s = raw.find(b"stream", m.start())
        s = raw.find(b"\n", s) + 1
        e = raw.find(b"endstream", s)
        partes.append(raw[s:e])
    return b"".join(partes)


def main(origem, destino):
    raw = open(origem, "rb").read()
    fluxo = ler_nativo(raw)
    assert fluxo.startswith(PREFIXO), "prefixo AIPrivateData ausente"
    nativo = zlib.decompressobj().decompress(fluxo[len(PREFIXO):])
    n = nativo.count(ANTIGO_NATIVO)
    print("nativo: %d bytes | ocorrencias da cor: %d" % (len(nativo), n))
    assert n > 0, "cor nativa nao encontrada"
    novo_nativo = nativo.replace(ANTIGO_NATIVO, NOVO_NATIVO)
    comprimido = PREFIXO + zlib.compress(novo_nativo, 9)
    blocos = [comprimido[i:i + 65536] for i in range(0, len(comprimido), 65536)]
    print("recomprimido: %d bytes em %d blocos" % (len(comprimido), len(blocos)))
    assert len(blocos) <= (ULTIMO - PRIMEIRO + 1), "passou do numero de blocos disponivel"

    escritor = PdfWriter(clone_from=origem)
    # localiza os blocos pelo dicionario /Private -> /AIPrivateDataN
    # ATENCAO: o fluxo zlib comeca em AIPrivateData2 (nao 3). O AIPrivateData1
    # e o %%BoundingBox e o ultimo bloco (10) fica com o resto do fluxo.
    privado = None
    for obj in escritor._objects:
        if isinstance(obj, dict) and "/AIPrivateData2" in obj:
            privado = obj
            break
    if privado is None:
        raise SystemExit("/Private com AIPrivateData2 nao encontrado")
    nomes = ["/AIPrivateData%d" % n for n in range(2, 11)]
    presentes = [k for k in nomes if k in privado]
    print("blocos no /Private: %s" % ", ".join(presentes))
    for i, chave in enumerate(presentes):
        obj = privado[chave].get_object()
        obj.set_data(blocos[i] if i < len(blocos) else b"")
        print("  %s: %d bytes" % (chave, len(blocos[i]) if i < len(blocos) else 0))

    trocadas = 0
    for pagina in escritor.pages:
        try:
            c = pagina.get_contents()
        except Exception:
            continue
        if c is None:
            continue
        dados = c.get_data()
        novo = re.sub(rb"1\s+0\.314\s+0\.11\s+scn", NOVO_PDF + b" scn", dados)
        if novo != dados:
            trocadas += 1
            stream = DecodedStreamObject()
            stream.set_data(novo)
            pagina[NameObject("/Contents")] = escritor._add_object(stream)
    print("paginas com a cor corrigida na camada PDF: %d" % trocadas)

    with open(destino, "wb") as f:
        escritor.write(f)
    print("escrito:", destino)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
