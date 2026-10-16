#!/usr/bin/env python3
# Envio da DRE GERENCIAL UNILAGES (CC SAO JOAQUIM) — Resend
# Uso: python3 enviar_unilages.py <arquivo-pdf>
import sys, os, json, urllib.request, base64, hashlib
from datetime import date

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}
DEST = "vinicius@terceirizou.com.br"

if len(sys.argv) > 1:
    pdf = sys.argv[1]
else:
    pdf = f"artifacts/{date.today().strftime('%y%m%d')}_DRE_Unilages_Sao_Joaquim_{date.today().strftime('%Y%m')}.pdf"
xlsx = pdf.replace(".pdf", ".xlsx")
idem = "unilages-dre-" + hashlib.md5((pdf + str(os.path.getmtime(pdf))).encode()).hexdigest()[:10]
a_pdf = base64.b64encode(open(pdf, "rb").read()).decode()
anexos = [{"filename": os.path.basename(pdf), "content": a_pdf}]
if os.path.exists(xlsx):
    anexos.append({"filename": os.path.basename(xlsx), "content": base64.b64encode(open(xlsx, "rb").read()).decode()})
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": [DEST],
    "bcc": ["financeiro@terceirizou.com.br"],
    "subject": "Modelo DRE Gerencial — Unilages (São Joaquim) — Abril/2026",
    "html": "<p>Bom dia Vinícius!</p><p>Segue o <b>modelo de DRE Gerencial da Unilages</b> (centro de custo São Joaquim, abril/2026, regime de caixa): entradas e saídas por categoria na ordem do plano de contas, apenas categorias com movimentação no mês.</p><p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>",
    "attachments": anexos,
}
UAH["Idempotency-Key"] = idem
req_ = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(req_, timeout=120) as resp:
    print(f"OK: {json.loads(resp.read().decode()).get('id')}")
