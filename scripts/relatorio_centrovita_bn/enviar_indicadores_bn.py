#!/usr/bin/env python3
# Envio do relatório de INDICADORES CENTROVITA BRAÇO DO NORTE — Resend
# Uso: python3 enviar_indicadores_bn.py [ano]
import sys, os, json, urllib.request, base64, hashlib
from datetime import date

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}
DEST = "vinicius@terceirizou.com.br"

ano = sys.argv[1] if len(sys.argv) > 1 else str(date.today().year)
pdf = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ano}.pdf"
xlsx = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ano}.xlsx"
idem = "cvbn-indicadores-" + ano + "-" + hashlib.md5((str(os.path.getmtime(pdf)) + str(os.path.getmtime(xlsx))).encode()).hexdigest()[:8]
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": [DEST],
    "bcc": ["financeiro@terceirizou.com.br"],
    "subject": f"Indicadores Gerenciais — Centrovita Braço do Norte — {ano}",
    "html": "<p>Boa tarde Vinícius!</p><p>Segue o relatório de <b>indicadores gerenciais da Centrovita Braço do Norte</b> (PDF + Excel): visão anual com indicadores mensais — ocupação, ticket médio, resultado operacional e financeiro, inadimplência e despesas em aberto.</p><p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>",
    "attachments": [
        {"filename": os.path.basename(pdf), "content": base64.b64encode(open(pdf, "rb").read()).decode()},
        {"filename": os.path.basename(xlsx), "content": base64.b64encode(open(xlsx, "rb").read()).decode()},
    ],
}
UAH["Idempotency-Key"] = idem
req_ = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(req_, timeout=120) as resp:
    print(f"OK: {json.loads(resp.read().decode()).get('id')}")
