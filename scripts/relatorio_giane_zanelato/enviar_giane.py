#!/usr/bin/env python3
# Envio do Relatório Mensal GIANE ZANELATO SAUDE CAPILAR por e-mail (Resend).
# Uso: python3 enviar_giane.py [caminho-do-pdf]
#   Sem argumento: usa o PDF de hoje (artifacts/YYMMDD_Relatorio_Giane_Zanelato.pdf).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatário: vinicius@terceirizou.com.br (padrão; destino do cliente a definir pelo Vinícius).
import base64, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]
BCC = []

_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "artifacts", f"{date.today().strftime('%y%m%d')}_Relatorio_Giane_Zanelato.pdf")

if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    anexos = [{"filename": os.path.basename(pdf_path), "content": base64.b64encode(f.read()).decode()}]

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

# idempotência inclui a hora do PDF (regeneração = reenvio legítimo; mesmo arquivo = bloqueado)
hora_pdf = date.today().strftime("%Y%m%d") + "-" + str(int(os.path.getmtime(pdf_path)) % 100000)

html = """<p>Boa tarde!</p>
<p>Segue em anexo o <b>relatório gerencial mensal da GIANE ZANELATO SAÚDE CAPILAR</b> (fonte Controlle).</p>
<p>Inclui: Comparativo dos últimos 13 meses por categoria (meses sem movimentação excluídos),
Receitas e Despesas do mês anterior, Despesas em aberto, Previsão de Receitas e Despesas do mês
corrente e Previsão de Fluxo de Caixa para os próximos 6 meses.</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "subject": f"Relatório Gerencial Mensal — GIANE ZANELATO SAÚDE CAPILAR — {date.today().strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-giane/1.0")
destinos = "-".join((TO + BCC))
req.add_header("Idempotency-Key", f"relatorio-giane-{hora_pdf}-{len(anexos)}-{destinos}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    nomes = " + ".join(a["filename"] for a in anexos)
    print(f"OK: enviado (id {out.get('id')}) — {nomes} → {', '.join(TO)}")
