#!/usr/bin/env python3
# Envio dos Relatórios Semanais CENTROVITA BRAÇO DO NORTE por e-mail (Resend).
# Uso: python3 enviar_centrovita_bn.py [caminho-do-pdf]
#   Sem argumento: usa o PDF de hoje (artifacts/YYMMDD_Relatorios_Centrovita_BN.pdf).
# Chave Resend: scripts/95b7f382c0a1ba1d/resend_key.txt (fora do repo) ou env RESEND_API_KEY.
# Destinatários: raulroliveira@hotmail.com + financeirocentrovitabn@gmail.com (to)
#   + financeiro@terceirizou.com.br (bcc).
# Anexos: Comparativo (paisagem) + Relatórios (retrato) + Excel.
# Idempotência: relatorio-centrovita-bn-AAAAMMDD-mtime-anexos-destinos — regeneração do PDF OU mudança
# de destinatários = reenvio legítimo; mesmo arquivo para os mesmos destinos = bloqueado (409).
import base64, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["raulroliveira@hotmail.com", "financeirocentrovitabn@gmail.com"]
BCC = ["financeiro@terceirizou.com.br"]

_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "artifacts", f"{date.today().strftime('%y%m%d')}_Relatorios_Centrovita_BN.pdf")

if not os.path.exists(pdf_path):
    print(f"ERRO: PDF não encontrado: {pdf_path}")
    sys.exit(1)

with open(pdf_path, "rb") as f:
    anexos = [{"filename": os.path.basename(pdf_path), "content": base64.b64encode(f.read()).decode()}]

xlsx_path = pdf_path.replace(".pdf", ".xlsx")
if os.path.exists(xlsx_path):
    with open(xlsx_path, "rb") as f:
        anexos.append({"filename": os.path.basename(xlsx_path), "content": base64.b64encode(f.read()).decode()})

# comparativo 13 meses (PDF próprio em paisagem)
comp_path = pdf_path.replace("_Relatorios_Centrovita_BN.pdf", "_Comparativo_Centrovita_BN.pdf")
if os.path.exists(comp_path):
    with open(comp_path, "rb") as f:
        anexos.insert(0, {"filename": os.path.basename(comp_path), "content": base64.b64encode(f.read()).decode()})

# idempotência inclui a hora do PDF e os destinatários (regeneração ou mudança de destino = reenvio legítimo)
hora_pdf = date.today().strftime("%Y%m%d") + "-" + str(int(os.path.getmtime(pdf_path)) % 100000)
destinos = "-".join((TO + BCC))

html = """<p>Boa tarde!</p>
<p>Segue em anexo o <b>pacote de relatórios gerenciais semanais da CENTROVITA BRAÇO DO NORTE</b> (fonte Controlle).</p>
<p>Inclui: Comparativo dos últimos 13 meses, Consolidado do mês, Despesas em aberto, Inadimplência
(geral e apenas boleto, com todos os lançamentos por categoria), Previsão do mês corrente e do mês
seguinte, Previsão de receitas da semana (geral e apenas boleto), Saldo nas contas e Previsão de fluxo
de caixa para os próximos 12 meses.</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "bcc": BCC,
    "subject": f"Relatórios Gerenciais Semanais — CENTROVITA BRAÇO DO NORTE — {date.today().strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-centrovita-bn/1.0")
req.add_header("Idempotency-Key", f"relatorio-centrovita-bn-{hora_pdf}-{len(anexos)}-{destinos}")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=60) as resp:
    out = json.loads(resp.read().decode())
    nomes = " + ".join(a["filename"] for a in anexos)
    print(f"OK: enviado (id {out.get('id')}) — {nomes} → {', '.join(TO)} | bcc {', '.join(BCC)}")
