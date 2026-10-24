#!/usr/bin/env python3
# Envio do relatório de INDICADORES UNILAGES — Resend — henrique@terceirizou.com.br
import sys, os, json, urllib.request, base64, hashlib
from datetime import date

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}

ano = sys.argv[1] if len(sys.argv) > 1 else str(date.today().year)
pdf = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Unilages_{ano}.pdf"
xlsx = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Unilages_{ano}.xlsx"
idem = "unilages-indicadores-" + ano + "-" + hashlib.md5((str(os.path.getmtime(pdf)) + str(os.path.getmtime(xlsx))).encode()).hexdigest()[:8]
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": ["henrique@terceirizou.com.br"],
    "subject": f"Unilages — Indicadores Gerenciais — {ano}",
    "html": ("<p>Bom dia Henrique!</p>"
             "<p>Segue o relatório de <b>indicadores gerenciais da Unilages</b> (PDF + Excel): visão anual com entradas e saídas por categoria e indicadores mensais — receitas operacionais, despesas operacionais, resultado operacional, aportes, juros, empréstimos, investimentos e resultado financeiro.</p>"
             "<p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>"),
    "attachments": [
        {"filename": os.path.basename(pdf), "content": base64.b64encode(open(pdf, "rb").read()).decode()},
        {"filename": os.path.basename(xlsx), "content": base64.b64encode(open(xlsx, "rb").read()).decode()},
    ],
}
UAH["Idempotency-Key"] = idem
req_ = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(req_, timeout=120) as resp:
    print(f"OK: {json.loads(resp.read().decode()).get('id')}")
