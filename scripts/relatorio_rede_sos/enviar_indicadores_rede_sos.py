#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Envio do relatório MENSAL de indicadores da REDE SOS SC NORTE por e-mail (Resend) → henrique@.
# Uso: python3 enviar_indicadores_rede_sos.py [ano]
import os, sys, json, urllib.request, base64, hashlib
from datetime import date
_dir = os.path.dirname(os.path.abspath(__file__))
HOJE = date.today()
ANO = sys.argv[1] if len(sys.argv) > 1 else str(HOJE.year)
pdf = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_RedeSOS_{ANO}.pdf"
xlsx = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_RedeSOS_{ANO}.xlsx"
if not (os.path.exists(pdf) and os.path.exists(xlsx)):
    print(f"ERRO: arquivos não encontrados: {pdf} / {xlsx}")
    sys.exit(1)
KEY = open(os.path.join(_dir, "..", "relatorio_allt", ".resend_key")).read().strip()
idem = "rede-ind-" + hashlib.md5((str(os.path.getmtime(pdf)) + str(os.path.getmtime(xlsx))).encode()).hexdigest()[:10]
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": ["henrique@terceirizou.com.br"],
    "bcc": ["financeiro@terceirizou.com.br"],
    "subject": f"Rede SOS SC Norte — Indicadores Gerenciais — {ANO}",
    "html": ("<p>Bom dia Henrique!</p>"
             f"<p>Segue o relatório de <b>indicadores gerenciais da Rede SOS SC Norte — {ANO}</b>.</p>"
             "<p>Uma folha por ano (2026; em janeiro/2027 abre a folha do novo ano), com os blocos de "
             "Receitas, Despesas e Indicadores, todos em regime de caixa.</p>"
             "<p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>"),
    "attachments": [
        {"filename": os.path.basename(pdf), "content": base64.b64encode(open(pdf, "rb").read()).decode()},
        {"filename": os.path.basename(xlsx), "content": base64.b64encode(open(xlsx, "rb").read()).decode()},
    ],
}
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": idem}
rq = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(rq, timeout=120) as resp:
    print("enviado:", json.loads(resp.read().decode()).get("id"))
