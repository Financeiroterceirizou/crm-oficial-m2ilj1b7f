#!/usr/bin/env python3
# Envio do Relatório Gerencial Mensal TERCEIRIZOU por e-mail (Resend).
# Uso: python3 enviar.py [caminho-do-pdf]
#   Sem argumento: usa o PDF do mês anterior (artifacts/relatorio-terceirizou-YYYY-MM.pdf).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatários: vinicius@terceirizou.com.br (to) + financeiro@terceirizou.com.br (bcc).
# Anexos: PDF + Excel do mês de referência.
import base64, json, os, sys, urllib.request
from datetime import date, timedelta

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]
BCC = ["financeiro@terceirizou.com.br"]

_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}

# mês de referência = mês anterior (mesma lógica do v4)
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
    mes_ref = os.path.basename(pdf_path).replace("relatorio-terceirizou-", "").replace(".pdf", "")
else:
    MES_FIM = date.today().replace(day=1) - timedelta(days=1)
    mes_ref = MES_FIM.strftime("%Y-%m")
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "artifacts", f"relatorio-terceirizou-{mes_ref}.pdf")

ano, mes = int(mes_ref[:4]), int(mes_ref[5:7])
MES_LABEL = f"{MES_PT[mes].capitalize()} de {ano}"

if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode()

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
anexos = [{"filename": os.path.basename(pdf_path), "content": pdf_b64}]
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

html = f"""<p>Bom dia!</p>
<p>Segue em anexo o <b>Relatório Gerencial Mensal — {MES_LABEL}</b> (fechamento, fonte Controlle).</p>
<p>O relatório inclui: Resumo do mês, Fluxo de Caixa realizado, Categorias Receitas e Despesas,
DRE Gerencial (regime caixa e competência), Receitas em aberto por cliente, Saldo nas contas
e Projeção de fluxo de caixa dos próximos 12 meses.</p>
<p>Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "bcc": BCC,
    "subject": f"Relatório Gerencial Mensal — {MES_LABEL}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-mensal/1.0")
req.add_header("Idempotency-Key", f"relatorio-mensal-{mes_ref}-{date.today().strftime('%Y%m%d')}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    print(f"OK: enviado (id {out.get('id')}) — {os.path.basename(pdf_path)}{' + ' + os.path.basename(xlsx_path) if os.path.exists(xlsx_path) else ''} → {', '.join(TO)} | bcc {', '.join(BCC)}")
