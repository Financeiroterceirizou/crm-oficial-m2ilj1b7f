#!/usr/bin/env python3
# Relatório Gerencial Mensal — CENTROVITA BRAÇO DO NORTE — Planilha Resumo de Indicadores
# v1.0, 2026-10-20 (pedido Vinícius 20/10)
#   Layout: planilha resumo com indicadores MENSAIS visíveis por ANO — 1ª folha = 2026
#   (jan→dez); quando chegar em jan/2027, nova folha (pedido Vinícius 20/10).
#   Cores Terceirizou (laranja #FF501C) + logo Centrovita (uploads/675a4f3a).
#   Indicadores (todos CAIXA — situação in 1,2, mês por dt_billing; sem 99.01):
#     Nº Hóspedes / Ticket Médio: planilha Drive (fev-ago) + informado (set=24 / 4.906,86);
#       futuros: aba do mês na planilha do Drive (1Pr2l8h9Y0JTi_WtGX4E-zbfLWun2nNGqxgoYCzWtfho)
#     Receitas Operacionais: categoria 01. RECEITAS (9190487 e filhos) + 02.04 Reembolso Família (9988394)
#     Despesas Operacionais: 01. IMPOSTO (9190492+filhos) + 02. CUSTOS OP (9190494+filhos)
#       + 03. DESPESAS ADM (9190511+filhos) + 04.01 Tarifas (9190540)
#     Resultado Operacional: receitas − despesas operacionais
#     Aportes: 02.01 (9190538) | Juros Aplicação: 02.03 (9190535)
#     Entrada de Empréstimos: 02.02 (9190536) + 02.05 (10335235)
#     Investimentos: 05. INVESTIMENTOS (9190547+filhos)
#     Saída de Empréstimos: 04.03 (9190542) + 04.06 (10335234)
#     Despesas Financeiras: 04.02 (9190541) + 04.04 (9190546)
#     Resultado Financeiro: Res.Op + Aportes + Juros + Ent.Emp − Invest − Saí.Emp − Desp.Fin
#     Inadimplência: receitas em aberto (sit 0) até o último dia do mês (Controlle a partir de set;
#       fev-ago da planilha anexa) | Despesas em Aberto: idem despesas
#     Distribuição aos Sócios: 04.05 (9190545)
# Envio: MENSAL → vinicius@terceirizou.com.br (Resend).
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
TOKEN = os.environ.get("CONTROLLE_TOKEN_CENTROVITA_BN") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37")
VERMELHO = colors.HexColor("#c0392b")
LOGO_CV = os.path.join(_dir, "logo-centrovita.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")

MES_PT = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items():
                r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and i < tries - 1:
                time.sleep(3 * (i + 1))
                continue
            raise

def tx_list(start, end, **filtros):
    out, page = [], 1
    while True:
        url = (f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
               f"&page={page}&orderBy=date&orderByCardinality=ASC")
        for k, v in filtros.items():
            url += f"&{k}={v}"
        tl = req(url).get("results", {}).get("transactionsList", [])
        out.extend(tl)
        if len(tl) < 100:
            return out
        page += 1

def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s

def bdate(t):
    return (t.get("dt_billing") or t.get("dt_due") or "")[:10]

# ===== IDs das categorias (plano Centrovita BN) =====
REC_OP = {9190487, 9190488, 9190489, 9190490, 9190491, 9988373, 9988394}  # 01. RECEITAS + Reembolso Família
DESP_OP = {9190492, 9190493, 9190494, 9190495, 9190496, 9190497, 9190499, 9190501, 9190502,
           9190505, 9190507, 9190508, 9190509, 9190510, 9190511, 9190512, 9190513, 9190514,
           9190515, 9190517, 9190518, 9190525, 9190527, 9190528, 9190530, 9190531, 9190532,
           9190533, 9190521, 9190529, 9190526, 9190519, 9190520, 9190516, 9988397, 9190504,
           9190506, 9190500, 9988375, 9988395, 9190498, 9988377, 9988381, 9988385, 9988386,
           9988387, 9988388, 9988389, 9988392, 9988393, 9988391, 9190540}
APORTES = {9190538}
JUROS_APL = {9190535}
ENT_EMP = {9190536, 10335235}
INVEST = {9190547, 9190548, 9190549, 9190550, 9190551}
SAI_EMP = {9190542, 10335234}
DESP_FIN = {9190541, 9190546}
DISTRIB = {9190545}

# ===== ano do relatório =====
ANO = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
HOJE_LABEL = date.today().strftime("%d/%m/%Y")

# ===== dados do Controlle (caixa) =====
_tx = tx_list(f"{ANO}-01-01", f"{ANO}-12-31")
por_mes = defaultdict(lambda: defaultdict(int))
for t in _tx:
    if t.get("situation") not in (1, 2):
        continue
    if any((c.get("ds_category") or "").startswith("99.01") for c in (t.get("apportionments_plan_account") or [])):
        continue
    mes = int(bdate(t)[5:7])
    cats = t.get("apportionments_plan_account") or []
    cid = cats[0].get("id_category") if cats else None
    v = t["value_in_cent"]
    if cid in REC_OP: por_mes[mes]["rec_op"] += v
    if cid in DESP_OP: por_mes[mes]["desp_op"] += v
    if cid in APORTES: por_mes[mes]["aportes"] += v
    if cid in JUROS_APL: por_mes[mes]["juros_apl"] += v
    if cid in ENT_EMP: por_mes[mes]["ent_emp"] += v
    if cid in INVEST: por_mes[mes]["invest"] += v
    if cid in SAI_EMP: por_mes[mes]["sai_emp"] += v
    if cid in DESP_FIN: por_mes[mes]["desp_fin"] += v
    if cid in DISTRIB: por_mes[mes]["distrib"] += v

# ===== inadimplência e despesas em aberto por mês (Controlle: sit 0, venc <= fim do mês) =====
abertos = defaultdict(lambda: [0, 0])
for mes in range(1, 13):
    fim = (date(ANO, mes, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    ab = [t for t in _tx if t.get("situation") == 0 and bdate(t) <= fim.isoformat()]
    abertos[mes][0] = sum(t["value_in_cent"] for t in ab if t["value_in_cent"] > 0)
    abertos[mes][1] = sum(t["value_in_cent"] for t in ab if t["value_in_cent"] < 0)

# ===== indicadores manuais (planilha Drive + informados) — fev-ago planilha, set informado =====
# fonte: uploads/36dbf9fd (planilha anexa) + mensagem do Vinícius 20/10
MANUAL = {
    2:  dict(hosp=1, ticket=4200.00, inad=0.0, desp_ab=0.0),
    3:  dict(hosp=3, ticket=5066.67, inad=0.0, desp_ab=2500.0),
    4:  dict(hosp=10, ticket=5105.00, inad=0.0, desp_ab=5000.0),
    5:  dict(hosp=17, ticket=4799.95, inad=0.0, desp_ab=7500.0),
    6:  dict(hosp=23, ticket=4696.00, inad=0.0, desp_ab=10000.0),
    7:  dict(hosp=21, ticket=4619.00, inad=8722.23, desp_ab=12000.0),
    8:  dict(hosp=25, ticket=4717.35, inad=29270.23, desp_ab=12000.0),
    9:  dict(hosp=24, ticket=4906.86, inad=None, desp_ab=None),  # inad/desp_ab do Controlle
}
INAD_CTL_DE = 9  # a partir de setembro: Controlle

# ===== montar a tabela de indicadores (jan→dez do ano) =====
linhas = []  # (label, [valores por mês], tipo) tipo: val | res
hosp_row, ticket_row = [], []
rec_row, desp_row, resop_row = [], [], []
apor_row, juros_row, entemp_row = [], [], []
inv_row, saiemp_row, despfin_row = [], [], []
resfin_row, inad_row, despab_row, distrib_row = [], [], [], []
for mes in range(1, 13):
    d = por_mes.get(mes, defaultdict(int))
    m = MANUAL.get(mes, {})
    # hóspedes/ticket: manual se existir; senão None (futuro)
    hosp_row.append(m.get("hosp"))
    ticket_row.append(m.get("ticket"))
    # inad/desp_ab: manual até ago; set em diante Controlle; meses não fechados (fim do mês
    # > hoje) = None — lançamentos futuros não são inadimplência
    fim_mes = (date(ANO, mes, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    fechado = date.today() >= fim_mes
    if mes < INAD_CTL_DE and mes in m:
        inad_row.append(m["inad"])
        despab_row.append(m["desp_ab"])
    elif fechado:
        inad_row.append(abertos[mes][0] / 100 if abertos[mes][0] else 0.0)
        despab_row.append(abertos[mes][1] / 100 if abertos[mes][1] else 0.0)
    else:
        inad_row.append(None)
        despab_row.append(None)
    rec_row.append(d["rec_op"] / 100)
    desp_row.append(d["desp_op"] / 100)
    resop_row.append((d["rec_op"] + d["desp_op"]) / 100)
    apor_row.append(d["aportes"] / 100)
    juros_row.append(d["juros_apl"] / 100)
    entemp_row.append(d["ent_emp"] / 100)
    inv_row.append(d["invest"] / 100)
    saiemp_row.append(d["sai_emp"] / 100)
    despfin_row.append(d["desp_fin"] / 100)
    resfin = (d["rec_op"] + d["desp_op"] + d["aportes"] + d["juros_apl"] + d["ent_emp"]
              + d["invest"] + d["sai_emp"] + d["desp_fin"]) / 100
    resfin_row.append(resfin)
    distrib_row.append(d["distrib"] / 100)

DEF = [
    ("Nº Hóspedes", hosp_row, "qtd"),
    ("Ticket Médio", ticket_row, "ticket"),
    ("Receitas Operacionais", rec_row, "moeda"),
    ("Despesas Operacionais", desp_row, "moeda"),
    ("Resultado Operacional", resop_row, "res"),
    ("Aportes", apor_row, "moeda"),
    ("Juros Aplicação Financeira", juros_row, "moeda"),
    ("Entrada de Empréstimos", entemp_row, "moeda"),
    ("Investimentos", inv_row, "moeda"),
    ("Saída de Empréstimos", saiemp_row, "moeda"),
    ("Despesas Financeiras", despfin_row, "moeda"),
    ("Resultado Financeiro", resfin_row, "res"),
    ("Inadimplência", inad_row, "moeda_pos"),
    ("Despesas em Aberto", despab_row, "moeda_pos"),
    ("Distribuição aos Sócios", distrib_row, "moeda"),
]

# ===== PDF (paisagem, 1 folha) =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, textColor=PRETO, spaceAfter=2)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#777777"), spaceAfter=8)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=7)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph

ARQ_PDF = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ANO}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=landscape(A4), leftMargin=1.2*cm, rightMargin=1.2*cm,
                        topMargin=1.2*cm, bottomMargin=1.5*cm,
                        title=f"Indicadores Gerenciais — Centrovita Braço do Norte {ANO}")
E = []
if os.path.exists(LOGO_CV):
    img = RLImage(LOGO_CV, width=4*cm, height=4*cm*1501/2668)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 4))
E.append(P("<b>CENTROVITA BRAÇO DO NORTE — Indicadores Gerenciais</b>", h1))
E.append(P(f"Ano {ANO} · Gerado em {HOJE_LABEL} · Fonte: Controlle (caixa) + planilha de ocupação · Terceirizou — mais do que terceirizar o financeiro", sub))
E.append(Spacer(1, 4))

hdr = [P("<b>Indicador</b>", cell)] + [P(f"<b>{MES_PT[m][:3]}</b>", cellc) for m in range(1, 13)] + [P("<b>Total</b>", cellc)]
rows = [hdr]
def fmt(v, tipo):
    if v is None:
        return "—"
    if tipo == "qtd":
        return str(int(v))
    if tipo in ("moeda", "moeda_pos", "res", "ticket"):
        # compacto: sem R$ e sem centavos (o mês cabe em 1 linha)
        vv = int(round(v))
        s = f"{abs(vv):,}".replace(",", ".")
        return ("-" if vv < 0 else "") + s
    return brl(int(round(v * 100)))
for label, vals, tipo in DEF:
    is_res = tipo == "res"
    st_name = "cellrb" if is_res else ("cellr" if tipo in ("moeda", "moeda_pos", "qtd") else "cellc")
    st_lbl = "cellb" if is_res else "cell"
    row = [P(label, ParagraphStyle(f"l{label}", parent=globals()[st_lbl], alignment=0))]
    for v in vals:
        if tipo == "moeda_pos" and v:
            s = ParagraphStyle(f"p{label}{v}", parent=cellr, textColor=VERMELHO)
            row.append(P(fmt(v, tipo), s))
        elif tipo == "res":
            cor = VERDE if (v or 0) > 0 else VERMELHO if (v or 0) < 0 else PRETO
            s = ParagraphStyle(f"r{label}{v}", parent=cellrb, textColor=cor)
            row.append(P(fmt(v, tipo), s))
        else:
            row.append(P(fmt(v, tipo), globals()[st_name]))
    # total (só faz sentido para moeda; hóspede/ticket: média ou último)
    if tipo == "moeda":
        tot = sum(v for v in vals if v is not None)
        row.append(P(brl(int(round(tot * 100))), ParagraphStyle(f"t{label}", parent=cellrb, textColor=(VERDE if tot > 0 else VERMELHO if tot < 0 else PRETO), fontName="Helvetica-Bold")))
    elif tipo == "qtd":
        ult = next((v for v in reversed(vals) if v is not None), None)
        row.append(P(str(int(ult)) if ult is not None else "—", cellrb))
    elif tipo == "ticket":
        ts = [v for v in vals if v is not None]
        med = round(sum(ts) / len(ts), 2) if ts else None
        row.append(P(fmt(med, "moeda"), cellrb))
    elif tipo == "moeda_pos":
        row.append(P("—", cellrb))
    else:
        row.append(P("—", cellrb))
    rows.append(row)
t = Table(rows, colWidths=[5.2*cm] + [1.85*cm]*12 + [2.2*cm], repeatRows=1)
style = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 7),
         ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2),
         ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
         ("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
         ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
         ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
for i, (label, vals, tipo) in enumerate(DEF, start=1):
    if tipo == "res":
        style.append(("BACKGROUND", (0,i), (-1,i), LARANJA_CLARO))
    elif i % 2 == 0:
        style.append(("BACKGROUND", (0,i), (-1,i), CINZA))
t.setStyle(TableStyle(style))
E.append(t)

E.append(Spacer(1, 8))
E.append(P("Nº Hóspedes e Ticket Médio: planilha de ocupação (fev–ago) e informação mensal da operação (set). Inadimplência e Despesas em Aberto: fev–ago da planilha de ocupação; a partir de setembro, Controlle (receitas/despesas em aberto até o último dia do mês). Demais indicadores: Controlle, regime de caixa. Janeiro: casa em implantação (sem operação).", sub))
doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ANO}.xlsx"
wb = Workbook()
ws = wb.active
ws.title = f"Indicadores {ANO}"
ws.append((f"CENTROVITA BRAÇO DO NORTE — Indicadores Gerenciais {ANO}",))
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=14)
c = ws.cell(row=1, column=1)
c.font = Font(bold=True, size=13, color="FF501C")
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 24
ws.append(("Indicador",) + tuple(MES_PT[m] for m in range(1, 13)) + ("Total",))
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"
VERMELHO_XL = "C0392B"
for cc in ws[2]:
    cc.fill = FILL_H
    cc.font = FH
    cc.alignment = Alignment(horizontal="center", vertical="center")
for label, vals, tipo in DEF:
    ws.append((label,) + tuple(vals) + (None,))
    r = ws.max_row
    if tipo == "res":
        for cc in ws[r]:
            cc.fill = FILL_T
        ws.cell(row=r, column=1).font = FB
    for j, cc in enumerate(ws[r][1:], 2):
        if isinstance(cc.value, (int, float)):
            if tipo == "qtd":
                cc.number_format = "0"
            else:
                cc.number_format = '"R$" #,##0.00'
                cor = VERMELHO_XL if tipo == "moeda_pos" and cc.value else (VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A")
                cc.font = Font(bold=tipo == "res", color=cor)
ws.column_dimensions["A"].width = 28
for j in range(2, 14):
    ws.column_dimensions[get_column_letter(j)].width = 13
ws.column_dimensions[get_column_letter(14)].width = 15
ws.freeze_panes = "B3"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
