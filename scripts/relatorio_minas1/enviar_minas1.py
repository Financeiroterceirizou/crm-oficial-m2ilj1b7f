#!/usr/bin/env python3
# Envio dos relatórios MINAS 1 (7 unidades + global) — Resend
import sys, os, time, json, urllib.request, base64, hashlib

_dir = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(_dir, ".resend_key")).read().strip()
UAH = {"Authorization": f"Bearer {KEY}", "User-Agent": "terceirizou-relatorios/1.0",
       "Content-Type": "application/json", "Idempotency-Key": ""}
DEST = "henrique@terceirizou.com.br"

def enviar(pdf, xlsx, unidade, idem):
    UAH["Idempotency-Key"] = idem
    a_pdf = base64.b64encode(open(pdf, "rb").read()).decode()
    a_xl = base64.b64encode(open(xlsx, "rb").read()).decode()
    corpo = {
        "from": "Terceirizou <financeiro@terceirizou.com.br>",
        "to": [DEST],
        "bcc": ["financeiro@terceirizou.com.br"],
        "subject": f"Relatório Gerencial — {unidade} — MINAS 1",
        "html": f"<p>Boa tarde Henrique!</p><p>Segue o relatório gerencial de <b>{unidade}</b> (PDF + Excel).</p><p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>",
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
    pacotes = [("BH2", "BELO HORIZONTE 2"), ("BH3", "BELO HORIZONTE 3"),
               ("CONS", "CONSELHEIRO LAFAIETE"), ("JF1", "JUIZ DE FORA 1"),
               ("MAN", "MANHUAÇU"), ("MUR", "MURIAÉ"), ("UBA", "UBÁ"),
               ("Global", "CONSOLIDADO 7 UNIDADES")]
    for chave, nome in pacotes:
        pdf = f"artifacts/{dia}_Relatorio_Minas1_{chave}.pdf"
        xlsx = f"artifacts/{dia}_Relatorio_Minas1_{chave}.xlsx"
        idem = "minas1-" + dia + "-" + chave.lower() + "-" + hashlib.md5(
            (str(os.path.getmtime(pdf)) + str(os.path.getmtime(xlsx))).encode()).hexdigest()[:8]
        try:
            i = enviar(pdf, xlsx, nome, idem)
            print(f"OK {chave}: {i}")
        except urllib.error.HTTPError as e:
            print(f"ERRO {chave}: {e.code} {e.read().decode()[:200]}")
        time.sleep(2)
