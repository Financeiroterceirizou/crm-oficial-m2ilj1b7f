#!/usr/bin/env python3
# Envio da DRE GISELE URNAU — Resend — SÓ henrique@terceirizou.com.br
import os, json, urllib.request, base64, hashlib
from datetime import date

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}

arqs = sorted([f for f in os.listdir("artifacts") if f.startswith(date.today().strftime("%y%m%d") + "_DRE_Gisele")])
anexos = [{"filename": f, "content": base64.b64encode(open(f"artifacts/{f}", "rb").read()).decode()} for f in arqs]
idem = "gisele-dre-" + hashlib.md5(",".join(f"{f}:{os.path.getmtime('artifacts/' + f)}" for f in arqs).encode()).hexdigest()[:10]
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": ["henrique@terceirizou.com.br"],
    "subject": "Gisele Urnau Assessoria de Comunicação — DRE Gerencial Setembro/2026",
    "html": ("<p>Bom dia Henrique!</p>"
             "<p>Segue o pacote de relatórios da <b>Gisele Urnau Assessoria de Comunicação</b> — setembro/2026, regime de caixa:</p>"
             "<p>• <b>DRE do mês</b> (entradas e saídas por categoria, na ordem do plano de contas)<br>"
             "• <b>Despesas Detalhadas</b> (despesa por despesa)<br>"
             "• <b>Comparativo dos Últimos 12 Meses</b><br>"
             "• <b>Receita / Faturamento Mês a Mês</b> (12 meses, por categoria de receita)<br>"
             "• <b>Resultado dos Últimos 12 Meses</b><br>"
             "• <b>Fluxo de Caixa 30 dias</b> (mês corrente pago+pendente e mês seguinte previsto)</p>"
             "<p>PDF e Excel em anexo. Qualquer dúvida estamos à disposição.</p>"
             "<p>Obrigado!</p>"),
    "attachments": anexos,
}
UAH["Idempotency-Key"] = idem
req_ = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(req_, timeout=120) as resp:
    print(f"OK: {json.loads(resp.read().decode()).get('id')} ({len(anexos)} anexos)")
