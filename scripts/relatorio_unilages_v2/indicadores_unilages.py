#!/usr/bin/env python3
# RELATÓRIO GERENCIAL — UNILAGES — Indicadores Mensais por Ano — v1.0, 2026-10-22 (pedido Vinícius)
#   Layout Centrovita BN: 1 folha por ano (2026 jan→dez; jan/2027 = nova folha), 3 blocos com
#   fundos distintos, logo Unilages + Terceirizou, meses sem informação em branco.
#   Regime de CAIXA (situation in 1,2, mês por dt_billing, sem 99.01 transferências).
#   Envio MENSAL → henrique@terceirizou.com.br.
# Uso: python3 indicadores_unilages.py [ano]  (default: ano corrente)
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image as RLImage)

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_UNILAGES") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c"); LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a"); CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO_UNI = os.path.join(_dir, "logo-unilages.png")
LOGO_TZ = os.path.join(_dir, "logo-terceirizou.png")
MES_PT = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

# ===== categorias (IDs do plano UNILAGES) =====
CATS_REC = {  # bloco de receitas por categoria
    "01 RECEITAS": 10226688,
    "02 RECEITA FINANCEIRA": 10226798,
    "03 ENTRADA EMPRÉSTIMOS": 10226813,
    "04 APORTE DOS SÓCIOS": 10226823,
    "05 RECEITA DE EVENTOS": 10331301,
    "06 VENDA DE SALVADOS": 10331443,
    "99.02 ESTORNO BAIXA BOLETO": 10274139,
    "DEVOLUÇÃO TED": 10324535,
}
CATS_DESP = {  # bloco de despesas por categoria
    "02 DEDUÇÕES DAS RECEITAS": 10226699,
    "10 RH SALÁRIOS/FOLHA": 10226703,
    "11 RH TRIBUTOS": 10374394,
    "12 RH COM PESSOAL": 10374399,
    "13 RH RESCISÕES": 10374402,
    "14 RH BENEFÍCIOS": 10374405,
    "15 OUTRAS RH": 10374407,
    "20 ADM FUNCIONAMENTO": 10226724,
    "21 ADM MANUTENÇÃO": 10374922,
    "22 ADM IMOBILIZADOS": 10375069,
    "23 ADM OUTRAS": 10375073,
    "24 ADM VIAGEM": 10375241,
    "25 ADM OUTRAS NÃO MENC.": 10375223,
    "30 COMERCIAL COMISSION.": 10226765,
    "31 COMERCIAL PRÊMIOS": 10375250,
    "32 COMERCIAL OPERAÇÃO": 10375251,
    "40 MKT PUBLICIDADE": 10375555,
    "41 MKT GERAL": 10375557,
    "42 MKT TERCEIROS": 10375558,
    "50 EVENTOS RATEÁVEIS": 10226774,
    "51 EVENTOS NÃO RATEÁVEIS": 10375712,
    "52 EVENTOS RASTREAMENTO": 10375716,
    "53 EVENTOS ASSIST. 24H": 10375858,
    "54 EVENTOS PRODUTOS": 10376018,
    "55 EVENTOS A IDENTIFICAR": 10376024,
    "90 DISTRIBUIÇÃO RESULTADOS": 10226809,
}
# conjuntos para os indicadores
S_REC_OP = {10226688, 10331301, 10331443}  # 01 + 05 + 06
S_DESP_OP = {10226699, 10226703, 10374394, 10374399, 10374402, 10374405, 10374407,  # 02 DED + 10-15 RH
             10226724, 10374922, 10375069, 10375073, 10375241, 10375223,  # 20-25 ADM
             10226765, 10375250, 10375251,  # 30-32 COM
             10375555, 10375557, 10375558,  # 40-42 MKT
             10226774, 10375712, 10375716, 10375858, 10376018, 10376024,  # 50-55 EVENTOS
             10226803}  # 61 DESPESA FINANCEIRA
S_APORTES = {10226823}
S_JUROS = {10226798}
S_ENT_EMP = {10226813}
S_INVEST = {10226792}
S_SAI_EMP = {10226818}
S_DESP_FIN = {10226803}

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
def cat_id(t):
    cats = t.get("apportionments_plan_account") or []
    return cats[0].get("id_category") if cats else None
def eh_99(t):
    return any((c.get("ds_category") or "").startswith("99.01") or (c.get("ds_category") or "").lower().startswith("transferencia")
               for c in (t.get("apportionments_plan_account") or []))

# mapa subcategoria → categoria pai (todos os filhos do plano)
_plano = req(f"{BASE}/plan-account/v1/planAccountsEntities").get("results", [])
_pai_de = {}
for p in _plano:
    if p.get("status") == 1 and p.get("id_plan_accounts_parent"):
        _pai_de[p["id"]] = p["id_plan_accounts_parent"]
# categorias pai também mapeiam para si mesmas
for _pid in list(CATS_REC.values()) + list(CATS_DESP.values()) + [10226792, 10226803, 10226818, 10226813]:
    _pai_de[_pid] = _pid

ANO = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
HOJE_LABEL = date.today().strftime("%d/%m/%Y")

# ===== dados: por categoria × mês =====
_tx = tx_list(f"{ANO}-01-01", f"{ANO}-12-31")
por_cat_mes = defaultdict(lambda: defaultdict(int))  # cat_pai_id → mês → centavos
for t in _tx:
    if t.get("situation") not in (1, 2): continue
    if eh_99(t): continue
    mes = int(bdate(t)[5:7])
    cid = cat_id(t)
    if cid is None: continue
    # mapear subcategoria → categoria pai (via dicionário de todos os filhos)
    por_cat_mes[_pai_de.get(cid, cid)][mes] += t["value_in_cent"]

# ===== montar linhas da tabela =====
# BLOCO 1 — RECEITAS por categoria
rec_rows = []
for nome, pid in CATS_REC.items():
    rec_rows.append((nome, [por_cat_mes[pid].get(m, 0) / 100 for m in range(1, 13)], "moeda"))
# BLOCO 2 — DESPESAS por categoria
desp_rows = []
for nome, pid in CATS_DESP.items():
    desp_rows.append((nome, [por_cat_mes[pid].get(m, 0) / 100 for m in range(1, 13)], "moeda"))
# BLOCO 3 — INDICADORES
rec_op = [sum(por_cat_mes[pid].get(m, 0) for pid in S_REC_OP) / 100 for m in range(1, 13)]
desp_op = [sum(por_cat_mes[pid].get(m, 0) for pid in S_DESP_OP) / 100 for m in range(1, 13)]
res_op = [rec_op[i] + desp_op[i] for i in range(12)]
aportes = [por_cat_mes[10226823].get(m, 0) / 100 for m in range(1, 13)]
juros = [por_cat_mes[10226798].get(m, 0) / 100 for m in range(1, 13)]
ent_emp = [por_cat_mes[10226813].get(m, 0) / 100 for m in range(1, 13)]
invest = [por_cat_mes[10226792].get(m, 0) / 100 for m in range(1, 13)]
sai_emp = [por_cat_mes[10226818].get(m, 0) / 100 for m in range(1, 13)]
desp_fin = [por_cat_mes[10226803].get(m, 0) / 100 for m in range(1, 13)]
res_fin = [res_op[i] + aportes[i] + juros[i] + ent_emp[i] + invest[i] + sai_emp[i] + desp_fin[i] for i in range(12)]

# meses fechados (relatório mensal dia 05: dados até o mês anterior)
fim_mes = lambda m: (date(ANO, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
fechado = [date.today() >= fim_mes(m) for m in range(1, 13)]
def cortar(row):
    for i, f in enumerate(fechado):
        if not f: row[i] = None
    return row
for i, (nome, vals, tipo) in enumerate(rec_rows): rec_rows[i] = (nome, cortar(list(vals)), tipo)
for i, (nome, vals, tipo) in enumerate(desp_rows): desp_rows[i] = (nome, cortar(list(vals)), tipo)
IND_ROWS = [
    ("Receitas Operacionais", cortar(rec_op), "res_rec"),
    ("Despesas Operacionais", cortar(desp_op), "res"),
    ("Resultado Operacional", cortar(res_op), "res"),
    ("Aportes", cortar(aportes), "moeda"),
    ("Juros Aplicação Financeira", cortar(juros), "moeda"),
    ("Entrada de Empréstimos", cortar(ent_emp), "moeda"),
    ("Investimentos", cortar(invest), "moeda"),
    ("Saída de Empréstimos", cortar(sai_emp), "moeda"),
    ("Despesas Financeiras", cortar(desp_fin), "moeda"),
    ("Resultado Financeiro", cortar(res_fin), "res"),
]

def is_res_row(tipo):
    return tipo in ("res", "res_rec")

BLOCOS = [
    ("RECEITAS", rec_rows, "#fdf0e8"),
    ("DESPESAS", desp_rows, "#f4f7f4"),
    ("INDICADORES", [(n, v, t) for n, v, t in IND_ROWS], "#f6f3ed"),
]

# ===== PDF (paisagem, 1 folha por ano) =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=PRETO, spaceAfter=1)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=7, textColor=colors.HexColor("#777777"), spaceAfter=4)
bt = ParagraphStyle("bt", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=5.8, leading=6.6)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
cellch = ParagraphStyle("cellch", parent=cellh, alignment=1)
P = Paragraph
def fmt(v, tipo):
    if v is None: return ""
    if tipo in ("moeda", "res", "res_rec"):
        vv = int(round(v))
        s = f"{abs(vv):,}".replace(",", ".")
        return ("-" if vv < 0 else "") + s
    return str(v)
def P_val_pdf(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(fmt(cents / 100, "moeda"), s)

ARQ_PDF = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Unilages_{ANO}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=landscape(A4), leftMargin=1.0*cm, rightMargin=1.0*cm,
                        topMargin=0.9*cm, bottomMargin=0.9*cm,
                        title=f"Indicadores Gerenciais — Unilages {ANO}")
E = []
# cabeçalho com as 2 logos
from PIL import Image as PILImage
logo_uni = RLImage(LOGO_UNI, width=1.8*cm, height=1.8*cm*PILImage.open(LOGO_UNI).size[1]/PILImage.open(LOGO_UNI).size[0])
logo_uni.hAlign = "LEFT"
logo_tz = RLImage(LOGO_TZ, width=2.4*cm, height=2.4*cm*PILImage.open(LOGO_TZ).size[1]/PILImage.open(LOGO_TZ).size[0])
logo_tz.hAlign = "RIGHT"
t_cab = Table([[logo_uni, logo_tz]], colWidths=[16*cm, 6*cm])
t_cab.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (1,0), (1,0), "RIGHT")]))
E.append(t_cab)
E.append(P("<b>UNILAGES — Indicadores Gerenciais</b>", h1))
E.append(P(f"Ano {ANO} · Gerado em {HOJE_LABEL} · Regime de caixa · Fonte: Controlle · Terceirizou — mais do que terceirizar o financeiro", sub))

CW = [3.8*cm] + [1.75*cm]*12 + [2.0*cm]
# UMA tabela única com seções (títulos de bloco como linhas) — cabe em 1 página
rows = [[P("<b>Indicador</b>", cellh)] + [P(f"<b>{MES_PT[m][:3]}</b>", cellch) for m in range(1, 13)] + [P("<b>Total</b>", cellch)]]
sec_spans = []  # (linha, fundo) para pintar por seção
linha = 1
for bi, (titulo, defs, fundo) in enumerate(BLOCOS):
    FUNDO = colors.HexColor(fundo)
    rows.append([P(f"<b>{titulo}</b>", bt)] + [P("", cellc)] * 13)
    sec_spans.append((linha, FUNDO, "titulo"))
    linha += 1
    for label, vals, tipo in defs:
        is_res = tipo in ("res", "res_rec")
        st_lbl = "cellb" if is_res else "cell"
        row = [P(label, ParagraphStyle(f"l{bi}{label}", parent=globals()[st_lbl]))]
        for v in vals:
            if v is None:
                row.append(P("", globals()[st_lbl]))
            elif tipo == "res_rec":
                s = ParagraphStyle(f"rr{bi}{label}{v}", parent=cellr, textColor=VERDE)
                row.append(P(fmt(v, "moeda"), s))
            elif tipo == "res":
                cor = VERDE if v > 0 else VERMELHO if v < 0 else PRETO
                s = ParagraphStyle(f"r{bi}{label}{v}", parent=cellrb, textColor=cor)
                row.append(P(fmt(v, "moeda"), s))
            else:
                s = ParagraphStyle(f"m{bi}{label}{v}", parent=cellr, textColor=(VERMELHO if v < 0 else PRETO))
                row.append(P(fmt(v, "moeda"), s))
        if tipo in ("moeda", "res", "res_rec"):
            tot = sum(v for v in vals if v is not None)
            row.append(P(fmt(tot, "moeda"), ParagraphStyle(f"t{bi}{label}", parent=cellrb, textColor=(VERDE if tot > 0 else VERMELHO if tot < 0 else PRETO))))
        else:
            row.append(P("", cellrb))
        rows.append(row)
        sec_spans.append((linha, FUNDO, "res" if is_res else "normal"))
        linha += 1
t = Table(rows, colWidths=CW, repeatRows=1)
st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 5.8),
      ("TOPPADDING", (0,0), (-1,-1), 1), ("BOTTOMPADDING", (0,0), (-1,-1), 1),
      ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
      ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#3d3d3d")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
      ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
      ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
for ln, FUNDO, tipo_l in sec_spans:
    if tipo_l == "titulo":
        st.append(("BACKGROUND", (0,ln), (-1,ln), LARANJA))
        st.append(("SPAN", (0,ln), (-1,ln)))
    elif tipo_l == "res":
        st.append(("BACKGROUND", (0,ln), (-1,ln), LARANJA_CLARO))
    else:
        st.append(("BACKGROUND", (0,ln), (-1,ln), FUNDO))
t.setStyle(TableStyle(st))
E.append(t)
E.append(Spacer(1, 2))
E.append(P("Res. Op = 01 + 05 + 06 receitas − (02 DED + 10-15 RH + 20-25 ADM + 30-32 COM + 40-42 MKT + 50-55 EVENTOS + 61 DESP FIN). Res. Fin = Res. Op + Aportes + Juros + Ent. Empréstimos − Invest − Saí. Empréstimos − Desp. Fin. Meses sem informação: em branco.",
           ParagraphStyle("notaf", parent=sub, fontSize=6, leading=7)))
doc.build(E)
print(f"OK: {ARQ_PDF}")


# ===== Excel (3 blocos na MESMA aba) =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Unilages_{ANO}.xlsx"
wb = Workbook()
ws = wb.active
ws.title = f"Indicadores {ANO}"
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
thin = Side(style="thin", color="DDDDDD")
BORDA = Border(left=thin, right=thin, top=thin, bottom=thin)

ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=14)
c = ws.cell(row=1, column=1, value=f"UNILAGES — Indicadores Gerenciais {ANO}")
c.font = Font(bold=True, size=13, color="FF501C")
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 24

linha = 3
for bi, (titulo, defs, fundo) in enumerate(BLOCOS):
    cor_fundo = fundo.replace("#", "")
    ws.cell(row=linha, column=1, value=titulo)
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=14)
    ct = ws.cell(row=linha, column=1)
    ct.fill = FILL_H
    ct.font = FH
    ct.alignment = Alignment(horizontal="left", vertical="center")
    for j in range(1, 15):
        ws.cell(row=linha, column=j).fill = FILL_H
    ws.row_dimensions[linha].height = 18
    linha += 1
    ws.cell(row=linha, column=1, value="Indicador")
    for m in range(1, 13):
        ws.cell(row=linha, column=1 + m, value=MES_PT[m])
    ws.cell(row=linha, column=14, value="Total")
    for cc in ws[linha]:
        cc.font = Font(bold=True, size=9)
        cc.alignment = Alignment(horizontal="center" if cc.column > 1 else "left", vertical="center")
        cc.border = BORDA
    linha += 1
    for label, vals, tipo in defs:
        ws.cell(row=linha, column=1, value=label).font = Font(bold=tipo in ("res", "res_rec"), size=9)
        ws.cell(row=linha, column=1).fill = PatternFill("solid", fgColor=cor_fundo)
        ws.cell(row=linha, column=1).border = BORDA
        for j, v in enumerate(vals, 2):
            cc = ws.cell(row=linha, column=j)
            if v is not None:
                cc.value = v
                cc.number_format = '"R$" #,##0.00'
                if tipo == "res_rec":
                    cc.font = Font(color=VERDE_XL, size=9)
                elif tipo == "res":
                    cc.font = Font(bold=True, color=(VERDE_XL if v > 0 else VERMELHO_XL if v < 0 else "1A1A1A"), size=9)
                else:
                    cc.font = Font(color=(VERMELHO_XL if v < 0 else "1A1A1A"), size=9)
            cc.border = BORDA
        ct2 = ws.cell(row=linha, column=14)
        if tipo in ("moeda", "res", "res_rec"):
            tot = sum(v for v in vals if v is not None)
            ct2.value = tot
            ct2.number_format = '"R$" #,##0.00'
            ct2.font = Font(bold=True, color=(VERDE_XL if tot > 0 else VERMELHO_XL if tot < 0 else "1A1A1A"), size=9)
        ct2.border = BORDA
        if tipo in ("res", "res_rec"):
            for j in range(1, 15):
                ws.cell(row=linha, column=j).fill = FILL_T
        linha += 1
    linha += 2

ws.column_dimensions["A"].width = 30
for j in range(2, 14):
    ws.column_dimensions[get_column_letter(j)].width = 13
ws.column_dimensions[get_column_letter(14)].width = 15
ws.freeze_panes = "B4"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
