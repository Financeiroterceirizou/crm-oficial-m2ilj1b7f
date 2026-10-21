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
# Envio: MENSAL dia 05 às 14:00 → vinicius@terceirizou.com.br (Resend).
#   Regra (Vinícius 20/10): relatório do dia 05 traz dados até o mês ANTERIOR fechado
#   (ex.: 05/11 → dados até outubro). Meses não fechados = "—" em todos os indicadores.
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
    fim_mes = (date(ANO, mes, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    fechado = date.today() >= fim_mes
    d = por_mes.get(mes, defaultdict(int))
    m = MANUAL.get(mes, {})
    if not fechado:
        # mês em andamento ou futuro: "—" em TODOS os indicadores (relatório do dia 05
        # mostra dados até o mês anterior fechado)
        for _row in (hosp_row, ticket_row, rec_row, desp_row, resop_row, apor_row, juros_row,
                     entemp_row, inv_row, saiemp_row, despfin_row, resfin_row, inad_row,
                     despab_row, distrib_row):
            _row.append(None)
        continue
    # hóspedes/ticket: manual se existir; senão None
    hosp_row.append(m.get("hosp"))
    ticket_row.append(m.get("ticket"))
    # inad/desp_ab: manual até ago; a partir de setembro Controlle
    if mes < INAD_CTL_DE and mes in m:
        inad_row.append(m["inad"])
        despab_row.append(m["desp_ab"])
    else:
        inad_row.append(abertos[mes][0] / 100 if abertos[mes][0] else 0.0)
        despab_row.append(abertos[mes][1] / 100 if abertos[mes][1] else 0.0)
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

# ===== agrupamento em 3 blocos =====
BLOCOS = [
    ("RESULTADO ADMINISTRATIVO", [
        ("Nº Hóspedes", hosp_row, "qtd"),
        ("Ticket Médio", ticket_row, "ticket"),
    ]),
    ("RESULTADO OPERACIONAL E FINANCEIRO", [
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
    ]),
    ("ATRASADOS E DISTRIBUIÇÃO", [
        ("Inadimplência", inad_row, "moeda_pos"),
        ("Despesas em Aberto", despab_row, "moeda_pos"),
        ("Distribuição aos Sócios", distrib_row, "moeda"),
    ]),
]
# cores de fundo por bloco (harmonia: laranja suave, cinza claro, bege claro)
FUNDO_BLOCO = {0: colors.HexColor("#fdf0e8"), 1: colors.HexColor("#f4f7f4"), 2: colors.HexColor("#f6f3ed")}

# ===== PDF (paisagem, 1 folha, 3 blocos) =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=PRETO, spaceAfter=1)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=7, textColor=colors.HexColor("#777777"), spaceAfter=4)
bt = ParagraphStyle("bt", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=6.8)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph

ARQ_PDF = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ANO}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=landscape(A4), leftMargin=1.2*cm, rightMargin=1.2*cm,
                        topMargin=1.1*cm, bottomMargin=1.3*cm,
                        title=f"Indicadores Gerenciais — Centrovita Braço do Norte {ANO}")
E = []

# cabeçalho: logo Centrovita (esquerda) + logo Terceirizou (direita)
if os.path.exists(LOGO_CV):
    logo_cv = RLImage(LOGO_CV, width=3.6*cm, height=3.6*cm*1501/2668)
    logo_cv.hAlign = "LEFT"
    cab = []
    LOGO_TZ = os.path.join(_dir, "logo-terceirizou-completa.png")
    if os.path.exists(LOGO_TZ):
        # proporção real da logo completa (não distorcer)
        from PIL import Image as PILImage
        w0, h0 = PILImage.open(LOGO_TZ).size
        logo_tz = RLImage(LOGO_TZ, width=4.2*cm, height=4.2*cm*h0/w0)
        logo_tz.hAlign = "RIGHT"
        cab = [[logo_cv, logo_tz]]
    else:
        cab = [[logo_cv, ""]]
    t_cab = Table(cab, colWidths=[16*cm, 6*cm])
    t_cab.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                               ("ALIGN", (1,0), (1,0), "RIGHT")]))
    E.append(t_cab)
    E.append(Spacer(1, 2))
E.append(P("<b>CENTROVITA BRAÇO DO NORTE — Indicadores Gerenciais</b>", h1))
E.append(P(f"Ano {ANO} · Gerado em {HOJE_LABEL} · Regime de caixa · Fonte: Controlle + planilha de ocupação · Terceirizou — mais do que terceirizar o financeiro", sub))

def fmt(v, tipo):
    if v is None:
        return ""
    if tipo == "qtd":
        return str(int(v))
    if tipo in ("moeda", "moeda_pos", "res", "ticket"):
        vv = int(round(v))
        s = f"{abs(vv):,}".replace(",", ".")
        return ("-" if vv < 0 else "") + s
    return brl(int(round(v * 100)))

CW = [3.8*cm] + [1.75*cm]*12 + [2.0*cm]  # 26,8cm < 27,3cm úteis (A4 paisagem com margens 1,2cm)
for bi, (titulo, defs) in enumerate(BLOCOS):
    # título do bloco mesclado nas 14 colunas (não quebra linha)
    t_tit = Table([[P(f"<b>{titulo}</b>", bt)]] , colWidths=[sum(CW)])
    t_tit.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LARANJA),
                               ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                               ("LEFTPADDING", (0,0), (-1,-1), 6)]))
    E.append(t_tit)
    rows = [[P("<b>Indicador</b>", cellb)] + [P(f"<b>{MES_PT[m][:3]}</b>", cellc) for m in range(1, 13)] + [P("<b>Total</b>", cellc)]]
    for label, vals, tipo in defs:
        is_res = tipo == "res"
        st_lbl = "cellb" if is_res else "cell"
        row = [P(label, ParagraphStyle(f"l{bi}{label}", parent=globals()[st_lbl]))]
        for v in vals:
            if tipo == "moeda_pos" and v:
                s = ParagraphStyle(f"p{bi}{label}{v}", parent=cellr, textColor=VERMELHO)
                row.append(P(fmt(v, tipo), s))
            elif tipo == "res":
                cor = VERDE if (v or 0) > 0 else VERMELHO if (v or 0) < 0 else PRETO
                s = ParagraphStyle(f"r{bi}{label}{v}", parent=cellrb, textColor=cor)
                row.append(P(fmt(v, tipo), s))
            else:
                row.append(P(fmt(v, tipo), globals()[st_name if False else ("cellrb" if is_res else ("cellr" if tipo in ("moeda","moeda_pos","qtd") else "cellc"))]))
        if tipo in ("moeda", "res"):
            tot = sum(v for v in vals if v is not None)
            row.append(P(fmt(tot, "moeda"), ParagraphStyle(f"t{bi}{label}", parent=cellrb, textColor=(VERDE if tot > 0 else VERMELHO if tot < 0 else PRETO))))
        else:
            row.append(P("", cellrb))
        rows.append(row)
    t = Table(rows, colWidths=CW, repeatRows=1)
    st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 6.8),
          ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#3d3d3d")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
          ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
          ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
    for i, (label, vals, tipo) in enumerate(defs, start=1):
        if tipo == "res":
            st.append(("BACKGROUND", (0,i), (-1,i), LARANJA_CLARO))
        else:
            # cor do bloco na LINHA INTEIRA (leitura facilitada)
            st.append(("BACKGROUND", (0,i), (-1,i), FUNDO_BLOCO[bi]))
    t.setStyle(TableStyle(st))
    E.append(t)
    E.append(Spacer(1, 6))

E.append(P("Nº Hóspedes e Ticket Médio: planilha de ocupação (fev–ago) e informação mensal da operação (set). Inadimplência e Despesas em Aberto: fev–ago da planilha de ocupação; a partir de setembro, Controlle (receitas/despesas em aberto até o último dia do mês). Demais indicadores: Controlle, regime de caixa. Janeiro: casa em implantação (sem operação). Meses sem informação: em branco.", sub))
doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== Excel (3 blocos na MESMA aba) =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{date.today().strftime('%y%m%d')}_Indicadores_Centrovita_BN_{ANO}.xlsx"
wb = Workbook()
ws = wb.active
ws.title = f"Indicadores {ANO}"
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FILL_B = {0: PatternFill("solid", fgColor="FFF3EC"), 1: PatternFill("solid", fgColor="F2F6F2"), 2: PatternFill("solid", fgColor="F7F4EE")}
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"
VERMELHO_XL = "C0392B"
thin = Side(style="thin", color="DDDDDD")
BORDA = Border(left=thin, right=thin, top=thin, bottom=thin)

ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=14)
c = ws.cell(row=1, column=1, value=f"CENTROVITA BRAÇO DO NORTE — Indicadores Gerenciais {ANO}")
c.font = Font(bold=True, size=13, color="FF501C")
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 24

linha = 3
for bi, (titulo, defs) in enumerate(BLOCOS):
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
        ws.cell(row=linha, column=1, value=label).font = Font(bold=tipo == "res", size=9)
        ws.cell(row=linha, column=1).fill = FILL_B[bi]
        ws.cell(row=linha, column=1).border = BORDA
        for j, v in enumerate(vals, 2):
            cc = ws.cell(row=linha, column=j)
            if v is not None:
                cc.value = v
                if tipo == "qtd":
                    cc.number_format = "0"
                else:
                    cc.number_format = '"R$" #,##0.00'
                if tipo == "moeda_pos" and v:
                    cc.font = Font(color=VERMELHO_XL, size=9)
                elif tipo == "res":
                    cc.font = Font(bold=True, color=(VERDE_XL if v > 0 else VERMELHO_XL if v < 0 else "1A1A1A"), size=9)
                else:
                    cc.font = Font(size=9)
            cc.border = BORDA
            cc.fill = FILL_T if tipo == "res" else PatternFill("solid", fgColor="FFFFFF")
        # total
        ct2 = ws.cell(row=linha, column=14)
        if tipo in ("moeda", "res"):
            tot = sum(v for v in vals if v is not None)
            ct2.value = tot
            ct2.number_format = '"R$" #,##0.00'
            ct2.font = Font(bold=True, color=(VERDE_XL if tot > 0 else VERMELHO_XL if tot < 0 else "1A1A1A"), size=9)
        ct2.border = BORDA
        linha += 1
    linha += 2  # espaço entre blocos

ws.column_dimensions["A"].width = 30
for j in range(2, 14):
    ws.column_dimensions[get_column_letter(j)].width = 13
ws.column_dimensions[get_column_letter(14)].width = 15
ws.freeze_panes = "B4"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
