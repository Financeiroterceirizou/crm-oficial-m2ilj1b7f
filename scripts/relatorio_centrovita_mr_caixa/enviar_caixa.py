#!/usr/bin/env python3
# Envio do Relatório Gerencial CENTROVITA — REGIME DE CAIXA (Mauro Ramos + Barra da Lagoa + unificado).
# Resend. Destino: vinicius@terceirizou.com.br (Pedido do Vinícius 09/11).
# RETIFICAR=1 → assunto e corpo marcados como retificação (reenvio deliberado do mesmo mês).
import base64, json, os, sys, urllib.request, hashlib
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]
RETIF = os.environ.get("RETIFICAR") == "1"

_dir = os.path.dirname(os.path.abspath(__file__))
_key_path = os.environ.get("RESEND_KEY_PATH") or os.path.join(_dir, "..", "95b7f382c0a1ba1d", "resend_key.txt")
KEY = os.environ.get("RESEND_API_KEY") or (open(_key_path).read().strip() if os.path.exists(_key_path) else "")

hoje = os.environ.get("HOJE") or date.today().isoformat()
dia = date.fromisoformat(hoje).strftime("%y%m%d")
base = os.path.join(_dir, "..", "..", "artifacts", f"{dia}_Relatorio_Centrovita_Caixa")

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

# Idempotency-Key estável pelo CONTEÚDO (mesmo pacote reenviado = mesmo id no Resend)
h = hashlib.md5(open(base + ".pdf", "rb").read()).hexdigest()[:10]
idem = f"centrovita-caixa-{dia}-{h}" + ("-retif" if RETIF else "")

mes_ref = (date.fromisoformat(hoje).replace(day=1)).strftime("%m/%Y")
html = ("""<p>Bom dia!</p>
<p><b>RETIFICAÇÃO</b> — segue novamente, em anexo, o relatório gerencial do Centrovita
(regime de caixa). A versão anterior deste mesmo mês deve ser desconsiderada.</p>""" if RETIF else """<p>Bom dia!</p>
<p>Segue em anexo o <b>relatório gerencial mensal do Centrovita — regime de caixa</b>
(fonte Controlle), separado por centro de custo e com o consolidado das duas unidades.</p>""") + """
<p><b>Mauro Ramos</b> e <b>Barra da Lagoa</b>, cada um com:</p>
<ul>
  <li>Comparativo dos últimos 13 meses por categoria (caixa)</li>
  <li>Receitas e Despesas do mês anterior, com aportes e investimento demonstrados à parte</li>
  <li>Despesas em aberto até o fechamento</li>
  <li>Previsão de receitas e despesas do mês corrente</li>
  <li>Fluxo de caixa dos últimos 13 meses realizado e projeção dos próximos 12</li>
</ul>
<p><b>Unificado</b>: os mesmos blocos com as duas unidades somadas.</p>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>Terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "subject": ("[RETIFICAÇÃO] " if RETIF else "") +
               f"Relatório Gerencial Mensal — Centrovita (regime de caixa) — {date.fromisoformat(hoje).strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}

req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST")
req.add_header("Authorization", f"Bearer {KEY}")
req.add_header("User-Agent", "terceirizou-relatorio-centrovita-caixa/1.0")
req.add_header("Idempotency-Key", idem)
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req, timeout=90) as resp:
    out = json.loads(resp.read().decode())
    print(f"OK: enviado (id {out.get('id')}) — {', '.join(a['filename'] for a in anexos)} → {', '.join(TO)}")
