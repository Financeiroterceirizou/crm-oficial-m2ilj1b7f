#!/usr/bin/env python3
"""Guarda de envio dos DREs por CC da UNILAGES (cron 16c262aa2551ff3d).

Motivo: o fechamento do mês anterior continua correndo nos primeiros dias do mês.
Sem trava, uma segunda rodada no mesmo mês reenviaria a DRE com números diferentes.

Regra: um mês de referência (YYYY-MM) é enviado UMA vez.
Reenvio deliberado = apagar a entrada do mês em enviados.json.

Uso:
  python3 guard.py check YYYY-MM                  -> 0 livre | 3 já enviado
  python3 guard.py record YYYY-MM <arquivo> <id> <resumo>
  python3 guard.py diff YYYY-MM <resumo>          -> 0 igual | 4 mudou
"""
import datetime
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(_DIR, "enviados.json")


def load():
    if not os.path.exists(ARQ):
        return {}
    try:
        with open(ARQ) as f:
            return json.load(f)
    except Exception:
        return {}


def save(d):
    tmp = ARQ + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, ARQ)


def main():
    if len(sys.argv) < 3:
        print("uso: guard.py check|record|diff YYYY-MM ...")
        return 2
    cmd, ref = sys.argv[1], sys.argv[2]
    d = load()

    if cmd == "check":
        if ref in d:
            e = d[ref]
            print(f"JA_ENVIADO {ref} em {e.get('data')} (resend {e.get('id')}) — {e.get('arquivo')}")
            return 3
        print(f"LIVRE {ref} — nenhum envio registrado")
        return 0

    if cmd == "record":
        if len(sys.argv) < 5:
            print("uso: guard.py record YYYY-MM <arquivo> <id> <resumo>")
            return 2
        d[ref] = {"data": datetime.date.today().isoformat(),
                  "arquivo": sys.argv[3], "id": sys.argv[4],
                  "resumo": sys.argv[5] if len(sys.argv) > 5 else ""}
        save(d)
        print(f"REGISTRADO {ref}: {d[ref]}")
        return 0

    if cmd == "diff":
        e = d.get(ref)
        if not e or not e.get("resumo"):
            print(f"SEM_REFERENCIA {ref} — não há resumo do envio para comparar")
            return 0
        if len(sys.argv) < 4:
            print("uso: guard.py diff YYYY-MM <resumo>")
            return 2
        if sys.argv[3] == e["resumo"]:
            print(f"IGUAL {ref} — números idênticos ao envio de {e.get('data')}")
            return 0
        print(f"DIVERGENCIA {ref} — enviado em {e.get('data')} com [{e['resumo']}] "
              f"e a rodada de hoje gerou [{sys.argv[3]}]")
        return 4

    print(f"comando desconhecido: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
