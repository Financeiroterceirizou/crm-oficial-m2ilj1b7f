#!/usr/bin/env python3
# Envio dos relatórios DARKE ESTRATEGIA E NEGOCIOS — Resend
# Destinos (Vinícius 09/10): vinicius@terceirizou.com.br + financeiro@darke.cc,
#   BCC financeiro@terceirizou.com.br. Periodicidade: mensal, dia 03 às 14:00.
import sys, os, time, json, urllib.request, base64, hashlib

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}
DESTS = ["vinicius@terceirizou.com.br", "financeiro@darke.cc"]

def enviar(pdf, xlsx, idem):
    UAH["Idempotency-Key"] = idem
    a_pdf = base64.b64encode(open(pdf, "rb").read()).decode()
    a_xl = base64.b64encode(open(xlsx, "rb").read()).decode()
    corpo = {
        "from": "Terceirizou <financeiro@terceirizou.com.br>",
        "to": DESTS,
        "bcc": ["financeiro@terceirizou.com.br"],
        "subject": "Relatório Gerencial — Darke Estratégia e Negócios",
        "html": "<p>Boa tarde Vinícius!</p><p>Segue o relatório gerencial da <b>Darke Estratégia e Negócios</b> (PDF + Excel): comparativo 13 meses, entradas e saídas do mês anterior, previsão do mês corrente, resultado 12 meses, inadimplência e projeção de fluxo de caixa 12 meses.</p><p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>",
        "attachments": [
            {"filename": os.path.basename(pdf), "content": a_pdf},
            {"filename": os.path.basename(xlsx), "content": a_xl},
        ],
    }
    req_ = urllib.request.Request("https://api.resend.com/emails",
                                  json.dumps(corpo).encode(), headers=UAH)
    with urllib.request.urlopen(req_, timeout=120) as resp:
        return json.loads(resp.read().decode()).get("id")

if __name__ == "__main__":
    dia = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%y%m%d")
    pdf = f"artifacts/{dia}_Relatorio_Darke.pdf"
    xlsx = f"artifacts/{dia}_Relatorio_Darke.xlsx"
    idem = "darke-" + dia + "-" + hashlib.md5(
        (str(os.path.getmtime(pdf)) + str(os.path.getmtime(xlsx))).encode()).hexdigest()[:8]
    try:
        i = enviar(pdf, xlsx, idem)
        print(f"OK: {i}")
    except urllib.error.HTTPError as e:
        print(f"ERRO: {e.code} {e.read().decode()[:200]}")
