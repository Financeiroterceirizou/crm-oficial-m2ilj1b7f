#!/usr/bin/env python3
# RELATÓRIO SEMANAL — UNILAGES — v1.0, 2026-10-22 (pedido Vinícius)
#   Toda sexta: (1) consolidado PAGO dia 01 → Nª sexta do mês corrente (por categoria);
#   (2) geral de tudo que tem A PAGAR até o fim do mês corrente (não consolidado — lançamento
#   a lançamento); (3) contas a pagar do MÊS SEGUINTE (lançamento a lançamento).
#   Regime de caixa; sem 99.01 transferências. Envio SÓ henrique@terceirizou.com.br.
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
LOGO = os.path.join(_dir, "logo-unilages.png"); SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
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
    return any((c.get("ds_category") or "").startswith("99.01") or (c.get("ds_category") or "").lower().startswith("transferencia")
               for c in (t.get("apportionments_plan_account") or []))

HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
# Nª sexta do mês (se rodar fora de sexta, usa a última sexta anterior do mês)
if HOJE.weekday() == 4:
    DIA_REF = HOJE
else:
    DIA_REF = HOJE - timedelta(days=(HOJE.weekday() - 4) % 7)
    if DIA_REF.month != HOJE.month:
        DIA_REF = HOJE.replace(day=1)
        while DIA_REF.weekday() != 4:
            DIA_REF += timedelta(days=1)
n_sexta = (DIA_REF.day - 1) // 7 + 1
MES_REF = HOJE.replace(day=1)
FIM_MES = (MES_REF.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
MES_SEG = FIM_MES + timedelta(days=1)
FIM_SEG = (MES_SEG.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

# ===== dados =====
tx_pago = [t for t in tx_list(MES_REF.isoformat(), DIA_REF.isoformat())
           if t.get("situation") in (1, 2) and not eh_99(t)]
tx_apagar_mes = [t for t in tx_list(DIA_REF.isoformat(), FIM_MES.isoformat())
                 if t.get("situation") == 0 and not eh_99(t) and t["value_in_cent"] < 0]
tx_apagar_seg = [t for t in tx_list(MES_SEG.isoformat(), FIM_SEG.isoformat())
                 if t.get("situation") == 0 and not eh_99(t) and t["value_in_cent"] < 0]
por_cat = defaultdict(lambda: [0, 0])
for t in tx_pago:
    v = t["value_in_cent"]
    por_cat[cat_nome(t)][0 if v > 0 else 1] += v
tot_e = sum(v[0] for v in por_cat.values())
tot_s = sum(v[1] for v in por_cat.values())

# ===== PDF =====
styles = getSampleStyleSheet()
h1c = ParagraphStyle("h1c", parent=styles["Heading1"], fontSize=13, textColor=PRETO, alignment=1, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#ff501c"), spaceBefore=12, spaceAfter=3)
h3s = ParagraphStyle("h3s", parent=styles["Heading3"], fontSize=9, spaceBefore=8, spaceAfter=2)
subc = ParagraphStyle("subc", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#777777"), alignment=1, spaceAfter=0)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=7.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph
def P_val(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(brl(cents), s)
def tabela(rows, widths, fs=7.5):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), fs),
          ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
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
    img = RLImage(LOGO, width=3.5*cm, height=3.5*cm*PIL_H_W[0]/PIL_H_W[1]) if False else None
from PIL import Image as PILImage
if os.path.exists(LOGO):
    w0, h0 = PILImage.open(LOGO).size
    img = RLImage(LOGO, width=3.5*cm, height=3.5*cm*h0/w0)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 6))
E.append(P("<b>UNILAGES — RELATÓRIO SEMANAL</b>", h1c))
E.append(P(f"Gerado em {HOJE.strftime('%d/%m/%Y')} · {n_sexta}ª sexta-feira do mês · Fonte: Controlle · Regime de caixa", subc))
E.append(Spacer(1, 6))

# 1) consolidado pago (dia 01 → Nª sexta)
E.append(P(f"Consolidado Pago — 01/{MES_REF.month:02d} a {DIA_REF.strftime('%d/%m')} ({n_sexta}ª sexta)", h2))
rows = [[P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
for cat in sorted(por_cat):
    e_c, s_c = por_cat[cat]
    rows.append([P(cat, cell), P_val(e_c, cellr), P_val(s_c, cellr), P_val(e_c + s_c, cellrb)])
rows.append([P(f"<b>Total — {n_sexta}ª sexta ({DIA_REF.strftime('%d/%m')})</b>", cellrb), P_val(tot_e, cellrb, True), P_val(tot_s, cellrb, True), P_val(tot_e + tot_s, cellrb, True)])
t = tabela(rows, [7.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
E.append(t)

# 2) a pagar até o fim do mês corrente (NÃO consolidado — lançamento a lançamento)
E.append(P(f"A Pagar — {DIA_REF.strftime('%d/%m')} até o fim do mês corrente (lançamento a lançamento)", h2))
por_cat_d = defaultdict(list)
for t in tx_apagar_mes:
    por_cat_d[cat_nome(t)].append(t)
tot_ap_mes = sum(t["value_in_cent"] for t in tx_apagar_mes)
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
    E.append(P(f"<b>{cat}</b>", h3s))
    E.append(tt)
rows = [[P(f"<b>Total a pagar até o fim do mês corrente</b>", cellrb), P(f"<b>{len(tx_apagar_mes)}</b>", cellc), P_val(tot_ap_mes, cellrb, True)]]
t = tabela(rows, [11*cm, 2.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), LARANJA_CLARO)]))
E.append(t)

# 3) contas a pagar do mês seguinte (lançamento a lançamento)
E.append(PageBreak())
E.append(P(f"Contas a Pagar — {MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (lançamento a lançamento)", h2))
por_cat_s = defaultdict(list)
for t in tx_apagar_seg:
    por_cat_s[cat_nome(t)].append(t)
tot_ap_seg = sum(t["value_in_cent"] for t in tx_apagar_seg)
for cat in sorted(por_cat_s):
    txs_c = sorted(por_cat_s[cat], key=bdate)
    rows = [[P("<b>Data</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell), P("<b>Valor</b>", cellr)]]
    for t in txs_c:
        d = bdate(t)
        rows.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell), P((t.get("ds_transaction") or "")[:70], cell),
                     P(t.get("ds_account_main") or "", cell), P_val(t["value_in_cent"], cellr)])
    rows.append([P("<b>Total</b>", cellrb), P(f"<b>{cat}</b>", cellrb), P(f"<b>{len(txs_c)}</b>", cellc), P_val(sum(t["value_in_cent"] for t in txs_c), cellrb)])
    tt = tabela(rows, [2.2*cm, 8.3*cm, 3.5*cm, 3*cm])
    tt.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
    E.append(P(f"<b>{cat}</b>", h3s))
    E.append(tt)
rows = [[P(f"<b>Total a pagar — {MES_PT[MES_SEG.month].capitalize()}/{MES_SEG.year}</b>", cellrb), P(f"<b>{len(tx_apagar_seg)}</b>", cellc), P_val(tot_ap_seg, cellrb, True)]]
t = tabela(rows, [11*cm, 2.5*cm, 3.5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), LARANJA_CLARO)]))
E.append(t)

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
ws.append(("Consolidado Pago — 01 a " + DIA_REF.strftime("%d/%m") + f" ({n_sexta}ª sexta)", "Entradas", "Saídas", "Resultado"))
for cc in ws[ws.max_row]: cc.fill = FILL_H; cc.font = FH
ws.append(("Categoria", "Entradas", "Saídas", "Resultado"))
for cc in ws[ws.max_row]: cc.font = FB
for cat in sorted(por_cat):
    e_c, s_c = por_cat[cat]
    ws.append((cat, e_c / 100, s_c / 100, (e_c + s_c) / 100))
ws.append((f"Total — {n_sexta}ª sexta", tot_e / 100, tot_s / 100, (tot_e + tot_s) / 100))
for cc in ws[ws.max_row]: cc.font = FB; cc.fill = FILL_T
# aba a pagar mês corrente
ws2 = wb.create_sheet("A Pagar (mês corrente)")
ws2.append((f"A Pagar — {DIA_REF.strftime('%d/%m')} até o fim do mês corrente (lançamento a lançamento)",))
ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
c2 = ws2.cell(row=1, column=1); c2.font = Font(bold=True, size=12, color="FF501C")
ws2.row_dimensions[1].height = 22
ws2.append(("Categoria", "Data", "Descrição", "Valor"))
for cc in ws2[2]: cc.fill = FILL_H; cc.font = FH
for cat in sorted(por_cat_d):
    for t in sorted(por_cat_d[cat], key=bdate):
        d = bdate(t)
        ws2.append((cat, f"{d[8:10]}/{d[5:7]}/{d[:4]}", (t.get("ds_transaction") or "")[:60], t["value_in_cent"] / 100))
ws2.append(("TOTAL", "", "", tot_ap_mes / 100))
for cc in ws2[ws2.max_row]: cc.font = FB; cc.fill = FILL_T
# aba a pagar mês seguinte
ws3 = wb.create_sheet(f"A Pagar ({MES_PT[MES_SEG.month][:3]})")
ws3.append((f"Contas a Pagar — {MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (lançamento a lançamento)",))
ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
c3 = ws3.cell(row=1, column=1); c3.font = Font(bold=True, size=12, color="FF501C")
ws3.row_dimensions[1].height = 22
ws3.append(("Categoria", "Data", "Descrição", "Valor"))
for cc in ws3[2]: cc.fill = FILL_H; cc.font = FH
for cat in sorted(por_cat_s):
    for t in sorted(por_cat_s[cat], key=bdate):
        d = bdate(t)
        ws3.append((cat, f"{d[8:10]}/{d[5:7]}/{d[:4]}", (t.get("ds_transaction") or "")[:60], t["value_in_cent"] / 100))
ws3.append(("TOTAL", "", "", tot_ap_seg / 100))
for cc in ws3[ws3.max_row]: cc.font = FB; cc.fill = FILL_T
for w in (ws, ws2, ws3):
    for row in w.iter_rows(min_row=3):
        for cc in row[3:4] if w is not ws else row[1:4]:
            if isinstance(cc.value, (int, float)):
                cc.number_format = '"R$" #,##0.00'
                cc.font = Font(bold=bool(row[0].font and row[0].font.bold),
                               color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
ws.column_dimensions["A"].width = 50
for col in ("B", "C", "D"):
    ws.column_dimensions[col].width = 18
for w in (ws2, ws3):
    for col, wd in zip("ABCD", (34, 12, 55, 16)):
        w.column_dimensions[col].width = wd
    w.freeze_panes = "A3"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")

# ===== envio (SÓ henrique@) =====
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
                 "• <b>A Pagar até o fim do mês corrente</b> (lançamento a lançamento)<br>"
                 "• <b>Contas a Pagar do mês seguinte</b> (lançamento a lançamento)</p>"
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
