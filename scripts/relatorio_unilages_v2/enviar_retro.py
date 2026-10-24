#!/usr/bin/env python3
"""Envia os pacotes retroativos DRE Unilages (mai/jun/jul 2026) para henrique@.
21 PDFs + 1 Excel consolidado via Resend (from financeiro@, UA + Idempotency-Key)."""
import base64, hashlib, json, os, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["henrique@terceirizou.com.br"]
UA = "terceirizou-relatorios-unilages/1.0"

CCS = [
    ("Geral", "GERAL"),
    ("correia_pinto", "Correia Pinto"),
    ("curitibanos", "Curitibanos"),
    ("lages_bm_adm", "Lages + BM Adm"),
    ("otacilio_costa", "Otacilio Costa"),
    ("sao_joaquim", "Sao Joaquim"),
    ("urubici", "Urubici"),
]
MESES = [("202605", "Maio"), ("202606", "Junho"), ("202607", "Julho")]

anexos = []
for tag, label in CCS:
    for m, mes in MESES:
        p = f"artifacts/261022_DRE_Unilages_{tag}_{m}.pdf"
        anexos.append((os.path.basename(p), p))
anexos.append(("261022_DRE_Unilages_Completo_Mai_Jun_Jul_2026.xlsx",
               "artifacts/261022_DRE_Unilages_Completo_Mai_Jun_Jul_2026.xlsx"))

total = sum(os.path.getsize(p) for _, p in anexos)
print(f"anexos: {len(anexos)} · total {total/1e6:.1f} MB")

lista = "<ul>" + "".join(f"<li>{label} — {mes}</li>" for label, mes in
                          [(l, m) for _, l in CCS for _, m in MESES]) + "</ul>"
html = f"""
<p>Henrique, bom dia!</p>
<p>Segue a DRE Gerencial da Unilages no layout de S&atilde;o Joaquim (por subcategoria, regime de caixa) para os meses de <b>maio, junho e julho de 2026</b>, de todos os centros de custo:</p>
{lista}
<p><b>Anexos:</b> 21 PDFs (1 por centro de custo e m&ecirc;s) + 1 arquivo Excel consolidado com todos os relat&oacute;rios (aba Resumo + DRE e Despesas Detalhadas de cada pacote).</p>
<p>Fonte: Controlle. Qualquer d&uacute;vida estamos &agrave; disposi&ccedil;&atilde;o.</p>
<p>Obrigado!</p>
<p>Att,<br>Terceirizou</p>
"""

payload = {
    "from": FROM,
    "to": TO,
    "subject": "DRE Gerencial Unilages — Maio, Junho e Julho 2026 (todos os centros de custo)",
    "html": html,
    "attachments": [
        {"filename": name, "content": base64.b64encode(open(p, "rb").read()).decode()}
        for name, p in anexos
    ],
}
key = open(os.path.join(AQUI, "resend_key.txt")).read().strip()
idem = "unilages-retro-mai-jun-jul-" + hashlib.md5(json.dumps(payload["attachments"]).encode()).hexdigest()[:10]
req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(payload).encode(), headers={
    "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": UA,
    "Idempotency-Key": idem}, method="POST")
with urllib.request.urlopen(req, timeout=120) as r:
    body = json.loads(r.read().decode())
print(f"resend:200 id={body.get('id')}")