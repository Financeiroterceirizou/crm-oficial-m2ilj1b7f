#!/usr/bin/env python3
# Envio do Relatório Mensal UNAÍ 1 (DM) VISTORIA por e-mail (Resend).
# Uso: python3 enviar_unai.py [caminho-do-pdf]
#   Sem argumento: usa o PDF de hoje (artifacts/YYMMDD_Relatorio_Unai.pdf).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatário: vinicius@terceirizou.com.br (to). Periodicidade: MENSAL, dia 04 14:00 (cron 1c07834f831c9007).
# Anexos: Relatório (PDF) + Excel.
# Idempotência: relatorio-unai-AAAAMMDD-mtime-anexos — regeneração do PDF = reenvio legítimo;
# mesmo arquivo = bloqueado (409).
import base64, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]

_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "artifacts", f"{date.today().strftime('%y%m%d')}_Relatorio_Unai.pdf")

if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    anexos = [{"filename": os.path.basename(pdf_path), "content": base64.b64encode(f.read()).decode()}]

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

# (relatório único: PDF + Excel, sem comparativo separado)

# idempotência inclui a hora do PDF (regeneração = reenvio legítimo; mesmo arquivo = bloqueado)
hora_pdf = date.today().strftime("%Y%m%d") + "-" + str(int(os.path.getmtime(pdf_path)) % 100000)

html = """<p>Boa tarde!</p>
<p>Segue em anexo o <b>relatório gerencial mensal da UNAÍ 1 (DM) VISTORIA</b> (fonte Controlle).</p>
<p>Inclui: Receitas e Despesas por categoria do mês anterior, Comparativo dos últimos 6 meses por
categoria, Previsão de despesas do mês corrente, Saldo nas contas no último dia do mês anterior,
Despesas em aberto até o último dia do mês anterior e Resumo com a Previsão de Resultado do mês
(faturamento, despesa, resultado e saldo projetado).</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "subject": f"Relatório Gerencial Mensal — UNAÍ 1 VISTORIA — {date.today().strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-unai/1.0")
req.add_header("Idempotency-Key", f"relatorio-unai-{hora_pdf}-{len(anexos)}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    nomes = " + ".join(a["filename"] for a in anexos)
    print(f"OK: enviado (id {out.get('id')}) — {nomes} → {', '.join(TO)}")
