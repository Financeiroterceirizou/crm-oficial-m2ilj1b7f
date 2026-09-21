#!/usr/bin/env python3
"""Envia o resumo diário por e-mail via Resend API (domínio próprio terceirizou.com.br).

Histórico: o MCP gmail está sem conta conectada no canal do cron desde 02/09
(6 ocorrências até 21/09) — bloqueio de plataforma. Desde 21/09 o envio é
direto pela API do Resend. A chave fica em resend_key.txt (LOCAL, fora do Git —
o secret scanning do GitHub rejeita commit com a chave embutida).
User-Agent e Idempotency-Key obrigatórios (causa dos 502 de 16/09 no hook do CRM).
"""
import json
import os
import sys
import urllib.request
import urllib.error

AQUI = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "resumo_diario.html")
DATA = sys.argv[2] if len(sys.argv) > 2 else ""  # formato DD/MM/YYYY

FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["contato@terceirizou.com.br"]
UA = "terceirizou-crm-resumo/1.0"


def enviar_resend(html: str) -> str:
    with open(os.path.join(AQUI, "resend_key.txt")) as f:
        key = f.read().strip()
    payload = json.dumps({
        "from": FROM,
        "to": TO,
        "subject": f"Resumo Diário — Captação de Leads [{DATA}]",
        "html": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Idempotency-Key": f"resumo-diario-{DATA.replace('/', '')}-1600",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read().decode())
    return f"resend:200 id={body.get('id')}"


def main():
    html = open(HTML_PATH, encoding="utf-8").read()
    try:
        print(enviar_resend(html))
        return 0
    except urllib.error.HTTPError as e:
        print(f"ERRO resend HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERRO resend: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
