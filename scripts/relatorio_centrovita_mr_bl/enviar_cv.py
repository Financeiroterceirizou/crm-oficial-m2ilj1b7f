#!/usr/bin/env python3
# Envio do Relatório Mensal CENTROVITA MAURO RAMOS + BARRA DA LAGOA (Resend).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatário: vinicius@terceirizou.com.br.
import base64, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]

_dir = os.path.dirname(os.path.abspath(__file__))
_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(_dir, "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

pdf_path = os.path.join(_dir, "..", "..", "artifacts", f"{date.today().strftime('%y%m%d')}_Relatorio_Centrovita_MR_BL.pdf")
if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    anexos = [{"filename": os.path.basename(pdf_path), "content": base64.b64encode(f.read()).decode()}]

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

hora_pdf = date.today().strftime("%Y%m%d") + "-" + str(int(os.path.getmtime(pdf_path)) % 100000)

html = """<p>Boa tarde!</p>
<p>Segue em anexo o <b>relatório gerencial mensal do Centrovita Mauro Ramos + Barra da Lagoa</b>
(fonte Controlle, filtro por centro de custo) — arquivo único com:</p>
<p><b>Mauro Ramos</b> e <b>Barra da Lagoa</b> (cada um): Comparativo dos últimos 13 meses por categoria,
Receitas e Despesas do mês anterior, Previsão de Receitas e Despesas do mês corrente,
Fluxo de Caixa dos últimos 13 meses e Saldo nas contas.</p>
<p><b>Consolidado</b>: Receitas e Despesas do mês anterior, Previsão do mês corrente e Saldo nas contas.</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "subject": f"Relatório Gerencial Mensal — Centrovita Mauro Ramos + Barra da Lagoa — {date.today().strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-centrovita/1.0")
req.add_header("Idempotency-Key", f"relatorio-centrovita-mrbl-{hora_pdf}-{len(anexos)}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    nomes = " + ".join(a["filename"] for a in anexos)
    print(f"OK: enviado (id {out.get('id')}) — {nomes} → {', '.join(TO)}")
