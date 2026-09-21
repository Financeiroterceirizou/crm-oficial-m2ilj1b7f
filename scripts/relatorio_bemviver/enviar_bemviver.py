#!/usr/bin/env python3
# Envio dos Relatórios Semanais BEM VIVER por e-mail (Resend).
# Uso: python3 enviar_bemviver.py [caminho-do-pdf]
#   Sem argumento: usa o PDF de hoje (artifacts/YYMMDD_Relatorios_Bem_Viver.pdf).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatários: financeirodabemviver@gmail.com (to) + financeiro@terceirizou.com.br (bcc).
import base64, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["financeirodabemviver@gmail.com"]
BCC = ["financeiro@terceirizou.com.br"]

_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "artifacts", f"{date.today().strftime('%y%m%d')}_Relatorios_Bem_Viver.pdf")

if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    anexos = [{"filename": os.path.basename(pdf_path), "content": base64.b64encode(f.read()).decode()}]

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

html = """<p>Boa tarde!</p>
<p>Segue em anexo o <b>pacote de relatórios gerenciais semanais da BEM VIVER</b> (fonte Controlle).</p>
<p>Inclui: Comparativo dos últimos 13 meses, Consolidado do mês, Despesas em aberto, Inadimplência
(geral e apenas boleto), Previsão do mês corrente e do mês seguinte, Previsão de receitas da semana
(geral e apenas boleto), Saldo nas contas e Previsão de fluxo de caixa para os próximos 12 meses.</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "bcc": BCC,
    "subject": f"Relatórios Gerenciais Semanais — BEM VIVER — {date.today().strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-bemviver/1.0")
req.add_header("Idempotency-Key", f"relatorio-bemviver-{date.today().strftime('%Y%m%d')}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    print(f"OK: enviado (id {out.get('id')}) — {os.path.basename(pdf_path)}{' + ' + os.path.basename(xlsx_path) if os.path.exists(xlsx_path) else ''} → {', '.join(TO)} | bcc {', '.join(BCC)}")
