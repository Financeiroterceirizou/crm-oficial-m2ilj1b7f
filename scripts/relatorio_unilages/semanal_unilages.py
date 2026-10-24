#!/usr/bin/env python3
# RELATÓRIO SEMANAL UNILAGES — v1.0, 2026-10-21 (pedido Vinícius)
#   Toda sexta-feira: consolidado PAGO acumulado do mês (dia 1 → a Nª sexta do mês),
#   a PAGAR até o último dia do mês corrente, a PAGAR do mês seguinte (previsibilidade)
#   + DETALHE das despesas do mês seguinte (lançamento a lançamento por categoria).
#   Regime de caixa; GERAL (todos os CCs, sem 99.01 transferências). Envio SÓ henrique@.
# Uso: python3 semanal_unilages.py [YYYY-MM-DD] (default: hoje)
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_UNILAGES") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c"); LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a"); CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-terceirizou.png"); SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}

def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items(): r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and i < tries - 1:
                time.sleep(3 * (i + 1)); continue
            raise

def tx_list(start, end):
    out, page = [], 1
    while True:
        tl = req(f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
                 f"&page={page}&orderBy=date&orderByCardinality=ASC").get("results", {}).get("transactionsList", [])
        out.extend(tl)
        if len(tl) < 100: return out
        page += 1

def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s

def bdate(t): return (t.get("dt_billing") or t.get("dt_due") or "")[:10]
def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "?") if cats else "(sem categoria)"
def eh_99(t):
    return any((c.get("ds_category") or "").startswith("99.") or (c.get("ds_category") or "").lower().startswith("transfer")
               for c in (t.get("apportionments_plan_account") or []))

HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
# Nª sexta-feira do mês (a data de referência é a própria sexta)
n_sexta = (HOJE.day - 1) // 7 + 1 if HOJE.weekday() == 4 else None
# se rodar fora de sexta, usar a última sexta anterior
if HOJE.weekday() != 4:
    sexta = HOJE - timedelta(days=(HOJE.weekday() - 4) % 7 + 0)  # última sexta <= hoje
    while sexta.weekday() != 4 or sexta.month != HOJE.month:
        sexta -= timedelta(days=7)
        if sexta.month != HOJE.month:
            sexta = HOJE.replace(day=1)
            while sexta.weekday() != 4:
                sexta += timedelta(days=1)
            break
    n_sexta = (sexta.day - 1) // 7 + 1
    DIA_REF = sexta
else:
    DIA_REF = HOJE
MES_REF = HOJE.replace(day=1)
FIM_MES = (MES_REF.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
MES_SEG = (FIM_MES + timedelta(days=1))
FIM_SEG = (MES_SEG.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

# ===== dados =====
tx_pago = [t for t in tx_list(MES_REF.isoformat(), DIA_REF.isoformat())
           if t.get("situation") in (1, 2) and not eh_99(t)]
tx_apagar_mes = [t for t in tx_list(DIA_REF.isoformat(), FIM_MES.isoformat())
                 if t.get("situation") == 0 and not eh_99(t) and t["value_in_cent"] < 0]
tx_apagar_seg = [t for t in tx_list(MES_SEG.isoformat(), FIM_SEG.isoformat())
                 if t.get("situation") == 0 and not eh_99(t) and t["value_in_cent"] < 0]

# consolidado pago por categoria (dia 1 → Nª sexta)
por_cat = defaultdict(lambda: [0, 0])
for t in tx_pago:
    v = t["value_in_cent"]
    por_cat[cat_nome(t)][0 if v > 0 else 1] += v
tot_e = sum(v[0] for v in por_cat.values())
tot_s = sum(v[1] for v in por_cat.values())

# a pagar por categoria (mês corrente e mês seguinte)
por_cat_ap = defaultdict(int)
for t in tx_apagar_mes:
    por_cat_ap[cat_nome(t)] += t["value_in_cent"]
por_cat_seg = defaultdict(int)
for t in tx_apagar_seg:
    por_cat_seg[cat_nome(t)] += t["value_in_cent"]

# ===== PDF =====
styles = getSampleStyleSheet()
h1c = ParagraphStyle("h1c", parent=styles["Heading1"], fontSize=13, textColor=PRETO, alignment=1, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#ff501c"), spaceBefore=12, spaceAfter=3)
subc = ParagraphStyle("subc", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#777777"), alignment=1, spaceAfter=0)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
P = Paragraph
def P_val(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(brl(cents), s)
def tabela(rows, widths, fs=8):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), fs),
          ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
          ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
          ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
    t.setStyle(TableStyle(st))
    return t
def rodape(canvas, doc):
    if os.path.exists(SIMBOLO):
        alt = 1.2 * cm
        canvas.drawImage(SIMBOLO, 18.4*cm, 1.1*cm, width=alt*372/553, height=alt, mask="auto")

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Semanal_Unilages_{HOJE.strftime('%Y%m%d')}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.3*cm, bottomMargin=1.6*cm,
                        title=f"Relatório Semanal Unilages — {DIA_REF.strftime('%d/%m/%Y')}")
E = []
if os.path.exists(LOGO):
    img = RLImage(LOGO, width=5*cm, height=5*cm*561/1600); img.hAlign = "CENTER"; E.append(img)
E.append(Spacer(1, 6))
E.append(P("<b>UNILAGES — RELATÓRIO SEMANAL</b>", h1c))
E.append(P(f"Gerado em {HOJE.strftime('%d/%m/%Y')} · {n_sexta}ª sexta-feira do mês · Fonte: Controlle · Regime de caixa · GERAL (todos os centros de custo)", subc))
E.append(Spacer(1, 6))

# 1) consolidado pago (dia 1 → Nª sexta)
E.append(P(f"Consolidado Pago — 01/{MES_REF.month:02d} a {DIA_REF.strftime('%d/%m')} ({n_sexta}ª sexta)", h2))
rows = [[P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
for cat in sorted(por_cat):
    e_c, s_c = por_cat[cat]
    rows.append([P(cat, cell), P_val(e_c, cellr), P_val(s_c, cellr), P_val(e_c + s_c, cellrb)])
rows.append([P(f"<b>Total — {n_sexta}ª sexta ({DIA_REF.strftime('%d/%m')})</b>", cellrb), P_val(tot_e, cellrb, True), P_val(tot_s, cellrb, True), P_val(tot_e + tot_s, cellrb, True)])
t = tabela(rows, [7.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
E.append(t)

# 2) a pagar até o fim do mês corrente
E.append(P(f"A Pagar — de {DIA_REF.strftime('%d/%m')} até 30/{MES_SEG.month-1 if MES_SEG.month>1 else 12:02d} (fim do mês corrente)", h2))
rows = [[P("<b>Categoria</b>", cell), P("<b>Valor a pagar</b>", cellr), P("<b>Lançamentos</b>", cellc)]]
for cat in sorted(por_cat_ap):
    rows.append([P(cat, cell), P_val(por_cat_ap[cat], cellr), P(str(len([t for t in tx_apagar_mes if cat_nome(t) == cat])), cellc)])
rows.append([P("<b>Total a pagar (mês corrente)</b>", cellrb), P_val(sum(por_cat_ap.values()), cellrb, True), P(f"<b>{len(tx_apagar_mes)}</b>", cellc)])
t = tabela(rows, [7.5*cm, 3.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
E.append(t)

# 3) a pagar do mês seguinte
E.append(P(f"A Pagar — {MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (previsto)", h2))
rows = [[P("<b>Categoria</b>", cell), P("<b>Valor a pagar</b>", cellr), P("<b>Lançamentos</b>", cellc)]]
for cat in sorted(por_cat_seg):
    rows.append([P(cat, cell), P_val(por_cat_seg[cat], cellr), P(str(len([t for t in tx_apagar_seg if cat_nome(t) == cat])), cellc)])
rows.append([P("<b>Total a pagar (mês seguinte)</b>", cellrb), P_val(sum(por_cat_seg.values()), cellrb, True), P(f"<b>{len(tx_apagar_seg)}</b>", cellc)])
t = tabela(rows, [7.5*cm, 3.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
E.append(t)

# 4) detalhe das despesas do mês seguinte (lançamento a lançamento)
E.append(PageBreak())
E.append(P(f"Despesas do Mês Seguinte — {MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (lançamento a lançamento)", h2))
por_cat_d = defaultdict(list)
for t in tx_apagar_seg:
    por_cat_d[cat_nome(t)].append(t)
for cat in sorted(por_cat_d):
    txs_c = sorted(por_cat_d[cat], key=bdate)
    rows = [[P("<b>Data</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell), P("<b>Valor</b>", cellr)]]
    for t in txs_c:
        d = bdate(t)
        rows.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell), P((t.get("ds_transaction") or "")[:70], cell),
                     P(t.get("ds_account_main") or "", cell), P_val(t["value_in_cent"], cellr)])
    rows.append([P("<b>Total</b>", cellrb), P(f"<b>{cat}</b>", cellrb), P(f"<b>{len(txs_c)}</b>", cellc), P_val(sum(t["value_in_cent"] for t in txs_c), cellrb)])
    tt = tabela(rows, [2.2*cm, 8.3*cm, 3.5*cm, 3*cm])
    tt.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
    E.append(P(f"<b>{cat}</b>", ParagraphStyle("h3s", parent=styles["Heading3"], fontSize=9, spaceBefore=8, spaceAfter=2)))
    E.append(tt)

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", subc))
doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Semanal_Unilages_{HOJE.strftime('%Y%m%d')}.xlsx"
wb = Workbook(); ws = wb.active; ws.title = "Semanal"
FILL_H = PatternFill("solid", fgColor="FF501C"); FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF"); FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
ws.append((f"UNILAGES — Relatório Semanal — {n_sexta}ª sexta ({DIA_REF.strftime('%d/%m/%Y')}) — regime de caixa",))
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
c = ws.cell(row=1, column=1); c.font = Font(bold=True, size=12, color="FF501C"); c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 22
def sec(titulo):
    ws.append((titulo, "", "", ""))
    r = ws.max_row
    for cc in ws[r]: cc.fill = FILL_H; cc.font = FH
    ws.append(("Categoria", "Entradas", "Saídas", "Resultado") if "Pago" in titulo else ("Categoria", "Valor a pagar", "Lançamentos", ""))
    for cc in ws[ws.max_row]: cc.font = FB
sec(f"Consolidado Pago — 01/{MES_REF.month:02d} a {DIA_REF.strftime('%d/%m')} ({n_sexta}ª sexta)")
for cat in sorted(por_cat):
    e_c, s_c = por_cat[cat]
    ws.append((cat, e_c / 100, s_c / 100, (e_c + s_c) / 100))
ws.append((f"Total — {n_sexta}ª sexta", tot_e / 100, tot_s / 100, (tot_e + tot_s) / 100))
for cc in ws[ws.max_row]: cc.font = FB; cc.fill = FILL_T
sec(f"A Pagar — até o fim do mês corrente ({MES_PT[MES_REF.month].capitalize()})")
for cat in sorted(por_cat_ap):
    ws.append((cat, por_cat_ap[cat] / 100, len([t for t in tx_apagar_mes if cat_nome(t) == cat]), ""))
ws.append(("Total a pagar (mês corrente)", sum(por_cat_ap.values()) / 100, len(tx_apagar_mes), ""))
for cc in ws[ws.max_row]: cc.font = FB; cc.fill = FILL_T
sec(f"A Pagar — {MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (previsto)")
for cat in sorted(por_cat_seg):
    ws.append((cat, por_cat_seg[cat] / 100, len([t for t in tx_apagar_seg if cat_nome(t) == cat]), ""))
ws.append(("Total a pagar (mês seguinte)", sum(por_cat_seg.values()) / 100, len(tx_apagar_seg), ""))
for cc in ws[ws.max_row]: cc.font = FB; cc.fill = FILL_T
for row in ws.iter_rows(min_row=3):
    for cc in row[1:]:
        if isinstance(cc.value, (int, float)) and abs(cc.value) > 1 or (isinstance(cc.value, float) and cc.value != 0):
            if "Entradas" in str(ws.cell(row=2, column=2).value) or True:
                if cc.column in (2, 3, 4) and isinstance(cc.value, (int, float)) and abs(cc.value) < 100000000 and (abs(cc.value) > 0.005 or cc.value == 0) and cc.value == cc.value:
                    if abs(cc.value) > 1000 or cc.column == 2 or cc.column == 3:
                        pass
for row in ws.iter_rows(min_row=3):
    for cc in row[1:3]:
        if isinstance(cc.value, (int, float)):
            cc.number_format = '"R$" #,##0.00'
            cc.font = Font(bold=bool(row[0].font and row[0].font.bold),
                           color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
ws.column_dimensions["A"].width = 50
for col in ("B", "C", "D"):
    ws.column_dimensions[col].width = 18
ws.freeze_panes = "A3"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")

# ===== envio (SÓ henrique@terceirizou.com.br) =====
def enviar():
    import base64, hashlib
    _key = open(os.path.join(_dir, ".resend_key")).read().strip()
    _h = {"Authorization": f"Bearer {_key}", "User-Agent": "terceirizou-relatorios/1.0",
          "Content-Type": "application/json", "Idempotency-Key": ""}
    _idem = "unilages-semanal-" + HOJE.strftime("%Y%m%d") + "-" + hashlib.md5(
        (str(os.path.getmtime(ARQ_PDF)) + str(os.path.getmtime(ARQ_XLSX))).encode()).hexdigest()[:8]
    _corpo = {
        "from": "Terceirizou <financeiro@terceirizou.com.br>",
        "to": ["henrique@terceirizou.com.br"],
        "subject": f"Unilages — Relatório Semanal — {n_sexta}ª sexta ({DIA_REF.strftime('%d/%m/%Y')})",
        "html": ("<p>Bom dia Henrique!</p>"
                 f"<p>Segue o <b>relatório semanal da Unilages</b> ({n_sexta}ª sexta-feira, {DIA_REF.strftime('%d/%m/%Y')}):</p>"
                 "<p>• <b>Consolidado Pago</b> — do dia 01 até a sexta desta semana<br>"
                 "• <b>A Pagar até o fim do mês corrente</b><br>"
                 "• <b>A Pagar do mês seguinte</b> (com detalhe lançamento a lançamento)</p>"
                 "<p>Qualquer dúvida estamos à disposição.</p><p>Obrigado!</p>"),
        "attachments": [
            {"filename": os.path.basename(ARQ_PDF), "content": base64.b64encode(open(ARQ_PDF, "rb").read()).decode()},
            {"filename": os.path.basename(ARQ_XLSX), "content": base64.b64encode(open(ARQ_XLSX, "rb").read()).decode()},
        ],
    }
    _h["Idempotency-Key"] = _idem
    _r = urllib.request.Request("https://api.resend.com/emails", json.dumps(_corpo).encode(), headers=_h)
    with urllib.request.urlopen(_r, timeout=120) as resp:
        print(f"ENVIO OK: {json.loads(resp.read().decode()).get('id')}")

if os.environ.get("UNILAGES_SEMANAL_ENVIAR") == "1":
    enviar()
