#!/usr/bin/env python3
# Envio das DREs da SUORTE PROTEÇÃO VEICULAR — Resend — SÓ henrique@terceirizou.com.br
import os, json, urllib.request, base64, hashlib
from datetime import date

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}

arqs = sorted([f for f in os.listdir("artifacts") if f.startswith(date.today().strftime("%y%m%d") + "_DRE_Suporte")])
anexos = [{"filename": f, "content": base64.b64encode(open(f"artifacts/{f}", "rb").read()).decode()} for f in arqs]
idem = "suporte-dre-" + hashlib.md5(",".join(f"{f}:{os.path.getmtime('artifacts/' + f)}" for f in arqs).encode()).hexdigest()[:10]
corpo = {
    "from": "Terceirizou <financeiro@terceirizou.com.br>",
    "to": ["henrique@terceirizou.com.br"],
    "subject": "Suporte Proteção Veicular — DREs Gerenciais Setembro/2026 (Geral + 6 centros de custo)",
    "html": ("<p>Bom dia Henrique!</p>"
             "<p>Segue o pacote de relatórios da <b>Suporte Proteção Veicular</b> — setembro/2026, regime de caixa:</p>"
             "<p>• <b>DRE Geral</b> (todos os centros de custo) com Comparativo dos Últimos 12 Meses, DRE do mês, Despesas Detalhadas, Resultado 12 meses e Fluxo de Caixa 30 dias<br>"
             "<p>• <b>DRE por centro de custo</b>: Chapecó, Xanxerê, São Miguel do Oeste, Concórdia, MD e Paraná — cada uma com DRE do mês, Despesas Detalhadas, Resultado 12 meses e Fluxo de Caixa 30 dias</p>"
             "<p>PDF e Excel de cada um em anexo. Qualquer dúvida estamos à disposição.</p>"
             "<p>Obrigado!</p>"),
    "attachments": anexos,
}
UAH["Idempotency-Key"] = idem
req_ = urllib.request.Request("https://api.resend.com/emails", json.dumps(corpo).encode(), headers=UAH)
with urllib.request.urlopen(req_, timeout=120) as resp:
    print(f"OK: {json.loads(resp.read().decode()).get('id')} ({len(anexos)} anexos)")
