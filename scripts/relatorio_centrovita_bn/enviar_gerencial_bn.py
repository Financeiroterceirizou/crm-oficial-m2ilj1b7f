#!/usr/bin/env python3
# Envio do pacote mensal CENTROVITA BRAÇO DO NORTE (unidade independente).
# Anexa: Relatório Gerencial (PDF + Excel) e a Planilha de Indicadores do ano (PDF + Excel).
# Destino: vinicius@terceirizou.com.br · bcc financeiro@terceirizou.com.br
# RETIFICAR=1 → assunto e corpo marcados como retificação (reenvio deliberado do mesmo mês).
import base64, hashlib, json, os, sys, urllib.request
from datetime import date

API = "https://api.resend.com/emails"
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["vinicius@terceirizou.com.br"]
BCC = ["financeiro@terceirizou.com.br"]
RETIF = os.environ.get("RETIFICAR") == "1"

_dir = os.path.dirname(os.path.abspath(__file__))
_key = os.environ.get("RESEND_KEY_PATH") or os.path.join(_dir, ".resend_key")
KEY = os.environ.get("RESEND_API_KEY") or open(_key).read().strip()

hoje = os.environ.get("HOJE") or date.today().isoformat()
dia = date.fromisoformat(hoje).strftime("%y%m%d")
ano = str(date.fromisoformat(hoje).year)
art = os.path.join(_dir, "..", "..", "artifacts")

candidatos = [
    os.path.join(art, f"{dia}_Relatorio_Centrovita_BracoDoNorte.pdf"),
    os.path.join(art, f"{dia}_Relatorio_Centrovita_BracoDoNorte.xlsx"),
    os.path.join(art, f"{dia}_Indicadores_Centrovita_BN_{ano}.pdf"),
    os.path.join(art, f"{dia}_Indicadores_Centrovita_BN_{ano}.xlsx"),
]
anexos = []
for p in candidatos:
    if not os.path.exists(p):
        if p.endswith("BracoDoNorte.pdf"):
            print(f"ERRO: pacote não encontrado: {p}")
            sys.exit(1)
        continue
    with open(p, "rb") as f:
        anexos.append({"filename": os.path.basename(p), "content": base64.b64encode(f.read()).decode()})

h = hashlib.md5(open(candidatos[0], "rb").read()).hexdigest()[:10]
idem = f"cvbn-gerencial-{dia}-{h}" + ("-retif" if RETIF else "")

html = ("""<p>Bom dia Vinícius!</p>
<p><b>RETIFICAÇÃO</b> — segue novamente, em anexo, o relatório da Centrovita Braço do Norte.
A versão anterior deste mesmo mês deve ser desconsiderada.</p>""" if RETIF else """<p>Bom dia Vinícius!</p>
<p>Segue em anexo o <b>relatório mensal da Centrovita Braço do Norte</b>
(fonte Controlle, regime de caixa).</p>""") + """
<p>O relatório traz:</p>
<ul>
  <li>Comparativo dos últimos 13 meses por categoria, em regime de caixa</li>
  <li>Receitas e despesas do mês, com aportes, empréstimos e investimento na obra demonstrados e subtraídos</li>
  <li>Hóspedes e ticket médio do mês</li>
  <li>Empréstimos por contraparte</li>
  <li>Despesas e receitas em aberto até o fechamento</li>
  <li>Previsão do mês corrente, fluxo de caixa realizado e projeção dos próximos 12 meses</li>
  <li>Planilha de indicadores do ano</li>
</ul>
<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>
<p>Att,<br>terceirizou — mais do que terceirizar o financeiro</p>"""

payload = {
    "from": FROM,
    "to": TO,
    "bcc": BCC,
    "subject": ("[RETIFICAÇÃO] " if RETIF else "") +
               f"Relatório Mensal — Centrovita Braço do Norte — {date.fromisoformat(hoje).strftime('%d/%m/%Y')}",
    "html": html,
    "attachments": anexos,
}
req = urllib.request.Request(API, json.dumps(payload).encode(), {
    "Authorization": f"Bearer {KEY}",
    "User-Agent": "terceirizou-relatorios/1.0",
    "Content-Type": "application/json",
    "Idempotency-Key": idem,
})
with urllib.request.urlopen(req, timeout=180) as r:
    print("ENVIADO:", json.loads(r.read().decode()).get("id"), "·", len(anexos), "anexos")
