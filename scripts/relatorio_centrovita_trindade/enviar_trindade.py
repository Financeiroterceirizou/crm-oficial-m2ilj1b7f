#!/usr/bin/env python3
# Envio do Relatório Gerencial CENTROVITA TRINDADE — REGIME DE CAIXA.
# Resend. Destinos: vinicius@terceirizou.com.br + financeiroslcentrovitatrindade@gmail.com
# (pedido do Vinícius, 10/11). bcc financeiro@ para arquivo interno.
# RETIFICAR=1 → assunto e corpo marcados como retificação (reenvio deliberado do mesmo mês).
import base64, json, os, sys, urllib.request, hashlib
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br", "financeiroslcentrovitatrindade@gmail.com"]
BCC = ["financeiro@terceirizou.com.br"]
RETIF = os.environ.get("RETIFICAR") == "1"

_dir = os.path.dirname(os.path.abspath(__file__))
_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(_dir, "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

hoje = os.environ.get("HOJE") or date.today().isoformat()
dia = date.fromisoformat(hoje).strftime("%y%m%d")
base = os.path.join(_dir, "..", "..", "artifacts", f"{dia}_Relatorio_Centrovita_Trindade")

anexos = []
for ext in (".pdf", ".xlsx"):
    p = base + ext
    if not os.path.exists(p):
        if ext == ".pdf":
            print(f"ERRO: PDF não encontrado: {p}")
            sys.exit(1)
        continue
    with open(p, "rb") as f:
        anexos.append({"filename": os.path.basename(p), "content": base64.b64encode(f.read()).decode()})

# Idempotency-Key estável pelo CONTEÚDO (mesmo pacote = mesmo id no Resend)
h = hashlib.md5(open(base + ".pdf", "rb").read()).hexdigest()[:10]
idem = f"centrovita-trindade-{dia}-{h}" + ("-retif" if RETIF else "")

html = ("""<p>Bom dia!</p>
<p><b>RETIFICAÇÃO</b> — segue novamente, em anexo, o relatório gerencial do Centrovita Trindade.
A versão anterior deste mesmo mês deve ser desconsiderada.</p>""" if RETIF else """<p>Bom dia!</p>
<p>Segue em anexo o <b>relatório gerencial mensal do Centrovita Trindade</b>
(fonte Controlle, regime de caixa).</p>""") + """
<p>O relatório traz:</p>
<ul>
  <li>Comparativo dos últimos meses por categoria (caixa)</li>
  <li>Receitas e Despesas do mês anterior, com aportes e investimento demonstrados à parte</li>
  <li>Despesas em aberto até o fechamento</li>
  <li>Previsão de receitas e despesas do mês corrente</li>
  <li>Fluxo de caixa realizado e projeção dos próximos 12 meses</li>
</ul>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "bcc": BCC,
    "subject": ("[RETIFICAÇÃO] " if RETIF else "") +
               f"Relatório Gerencial Mensal — Centrovita Trindade — {date.fromisoformat(hoje).strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-centrovita-trindade/1.0")
req.add_header("Idempotency-Key", idem)
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=90) as resp:
    out = json.loads(resp.read().decode())
    print(f"OK: enviado (id {out.get('id')}) — {', '.join(a['filename'] for a in anexos)} → {', '.join(TO)}")
