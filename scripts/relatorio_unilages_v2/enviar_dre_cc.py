#!/usr/bin/env python3
"""Envio do pacote DRE Gerencial UNILAGES por centro de custo — Resend — henrique@.
1 e-mail com os 7 PDFs + o Excel consolidado.
Uso: python3 enviar_dre_cc.py YYYYMM
Idempotency-Key = YYYYMM + mtime dos anexos + destinatário (regeneração = reenvio legítimo).
"""
import base64
import hashlib
import json
import os
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
FROM = "Terceirizou <financeiro@terceirizou.com.br>"
TO = ["henrique@terceirizou.com.br"]
UA = "terceirizou-relatorios-unilages/1.0"

MES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
          7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

PACOTES = [
    ("Geral", "GERAL (todos os centros de custo)"),
    ("correia_pinto", "Correia Pinto"),
    ("curitibanos", "Curitibanos"),
    ("lages_bm_adm", "Lages + BM ADM"),
    ("otacilio_costa", "Otacilio Costa"),
    ("sao_joaquim", "Sao Joaquim"),
    ("urubici", "Urubici"),
]


def main():
    if len(sys.argv) < 2:
        print("uso: enviar_dre_cc.py YYYYMM")
        return 2
    ref = sys.argv[1]
    ano, mes = int(ref[:4]), int(ref[4:6])
    dia = __import__("datetime").date.today().strftime("%y%m%d")

    anexos = []
    for tag, _ in PACOTES:
        p = os.path.join(RAIZ, "artifacts", f"{dia}_DRE_Unilages_{tag}_{ref}.pdf")
        anexos.append((os.path.basename(p), p))
    xlsx = os.path.join(RAIZ, "artifacts", f"{dia}_DRE_Unilages_Completo_{ref}.xlsx")
    anexos.append((os.path.basename(xlsx), xlsx))

    faltando = [n for n, p in anexos if not os.path.exists(p)]
    if faltando:
        print(f"FALTA: {', '.join(faltando)}")
        return 1

    lista = "<ul>" + "".join(f"<li>{label}</li>" for _, label in PACOTES) + "</ul>"
    html = f"""
<p>Bom dia Henrique!</p>
<p>Segue a <b>DRE Gerencial da Unilages</b> de <b>{MES_PT[mes]} de {ano}</b> por centro de custo
(regime de caixa, categorias na ordem do plano de contas):</p>
{lista}
<p><b>Anexos:</b> 7 PDFs (1 por centro de custo) + 1 Excel consolidado com a DRE e as Despesas
Detalhadas de cada centro de custo.</p>
<p>Fonte: Controlle. Qualquer d&uacute;vida estamos &agrave; disposi&ccedil;&atilde;o.</p>
<p>Obrigado!</p>
<p>Att,<br>Terceirizou</p>
"""

    chave = open(os.path.join(AQUI, ".resend_key")).read().strip()
    payload = {
        "from": FROM,
        "to": TO,
        "subject": f"DRE Gerencial Unilages — {MES_PT[mes]} de {ano} (por centro de custo)",
        "html": html,
        "attachments": [
            {"filename": nome, "content": base64.b64encode(open(p, "rb").read()).decode()}
            for nome, p in anexos
        ],
    }
    assinatura = ref + "|" + ",".join(str(int(os.path.getmtime(p))) for _, p in anexos) + "|" + ",".join(TO)
    idem = "unilages-dre-cc-" + hashlib.md5(assinatura.encode()).hexdigest()[:16]
    req = urllib.request.Request("https://api.resend.com/emails", json.dumps(payload).encode(), headers={
        "Authorization": f"Bearer {chave}", "Content-Type": "application/json",
        "User-Agent": UA, "Idempotency-Key": idem}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        body = json.loads(r.read().decode())
    total = sum(os.path.getsize(p) for _, p in anexos)
    print(f"OK: resend id {body.get('id')} · {len(anexos)} anexos · {total/1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
