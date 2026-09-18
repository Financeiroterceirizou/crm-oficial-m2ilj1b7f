#!/usr/bin/env python3
# Relatório Gerencial Mensal — TERCEIRIZOU (v3, 2026-09-17)
# Feedback Vinícius aplicado: logo + laranja (#ff501c); Categorias Receitas/Despesas
# (despesas por categoria cadastrada); DRE caixa + DRE competência; "Receitas em aberto
# até DD/MM/AAAA" por cliente; "Saldo nas Contas dia DD/MM/AAAA" por conta (sem zero);
# projeção com gráfico; Resultado 12m por categoria; Comparativo 13 meses por categoria.
# Fonte: API Controlle v1 (token do Vinícius, validado 17/09).
import json, urllib.request
from collections import defaultdict
from datetime import date

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

TOKEN = "U2FsdGVkX1+UD4cDxFUwPtqM8bbBBHWrO08Nli1iK5BvAUBXDHMtdGwLG4OfXH5o/4hfrxcmYdK7jAO4oD5UeLpY5ICS6jYUmk8hH9r/6NI="
BASE = "https://api-v1.controlle.com"
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")

def req(url):
    r = urllib.request.Request(url)
    for k, v in UA.items():
        r.add_header(k, v)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))

def tx_list(start, end, **filtros):
    url = f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}&page={{p}}&orderBy=date&orderByCardinality=ASC"
    for k, v in filtros.items():
        url += f"&{k}={v}"
    out, page = [], 1
    while True:
        tl = req(url.format(p=page)).get("results", {}).get("transactionsList", [])
        out.extend(tl)
        if len(tl) < 100:
            return out
        page += 1

def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s

# ================= DADOS =================
MES_FIM = date(2026, 8, 31)
fim = MES_FIM.isoformat()

bal = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2026-08-01&end_date={fim}")["results"]
entradas_mes, saidas_mes = bal["revenuesDone"], bal["expensesDone"]
entradas_prev, saidas_prev = bal["revenuesPreview"], bal["expensesPreview"]

txs = tx_list("2026-08-01", fim)
normais = [t for t in txs if not (t.get("ds_transaction") or "").startswith("Transferência")]
desp_cat = defaultdict(int)
for t in normais:
    if t["value_in_cent"] < 0:
        for c in (t.get("apportionments_plan_account") or []):
            desp_cat[c.get("ds_category") or "?"] += c.get("value") or 0

abertas = tx_list("2017-01-01", fim, **{"activity_type": "1", "situation": "[0]"})
por_cliente = defaultdict(int)
for t in abertas:
    nome = (t.get("name_contact") or "").strip() or (t.get("ds_transaction") or "").strip()[:45]
    if nome.startswith("Transferência"):
        continue
    por_cliente[nome] += t.get("value_in_cent") or 0
total_aberto = sum(por_cliente.values())

contas = req(f"{BASE}/account/v1/accounts").get("results", [])
saldos_conta = []
for c in contas:
    if c.get("status") != 1:
        continue
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={fim}&id_account_main={c['id']}")["results"]
    saldo = b["balanceDone"]
    if saldo != 0:
        saldos_conta.append((c["ds_account"], saldo))

MESES = [("2025-09-30","set/25"),("2025-10-31","out/25"),("2025-11-30","nov/25"),("2025-12-31","dez/25"),
         ("2026-01-31","jan/26"),("2026-02-28","fev/26"),("2026-03-31","mar/26"),("2026-04-30","abr/26"),
         ("2026-05-31","mai/26"),("2026-06-30","jun/26"),("2026-07-31","jul/26"),("2026-08-31","ago/26"),
         ("2026-09-17","set/26*")]
comp_mensal = []
for fim_m, label in MESES:
    ini_m = fim_m[:8] + "01"
    if label.startswith("set/25"):
        ini_m = "2025-09-01"
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini_m}&end_date={fim_m}")["results"]
    comp_mensal.append((label, b["revenuesDone"], b["expensesDone"], b["balanceDone"]))

matriz = defaultdict(lambda: defaultdict(int))
for t in tx_list("2025-09-01", "2026-09-17"):
    if (t.get("ds_transaction") or "").startswith("Transferência"):
        continue
    mes = t["dt_competence"][:7]
    for c in (t.get("apportionments_plan_account") or []):
        matriz[c.get("ds_category") or "?"][mes] += c.get("value") or 0

# ================= PDF =================
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=15, textColor=PRETO, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11.5, textColor=LARANJA, spaceBefore=12, spaceAfter=5)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#666666"), spaceAfter=8)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=12.5)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)

def tabela(rows, widths, header=True, align_right_from=1):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 8),
             ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
             ("VALIGN", (0,0), (-1,-1), "MIDDLE")]
    if header:
        style += [("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                  ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0,i), (-1,i), CINZA))
    style.append(("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA))
    t.setStyle(TableStyle(style))
    return t

P = Paragraph
doc = SimpleDocTemplate("artifacts/relatorio-terceirizou-agosto-2026-v3.pdf", pagesize=A4,
                        leftMargin=1.6*cm, rightMargin=1.6*cm, topMargin=1.4*cm, bottomMargin=1.4*cm)
E = []

logo = Image("artifacts/logo-terceirizou.png", width=6.2*cm, height=6.2*cm*702/2000)
E.append(logo)
E.append(Spacer(1, 4))
E.append(P("<b>Relatório Gerencial Mensal</b>", h1))
E.append(P("Agosto de 2026 · Fechamento · Fonte: Controlle · Gerado em 17/09/2026", sub))

E.append(P("Resumo do mês", h2))
resumo = [
    [P("<b>Indicador</b>", cell), P("<b>Agosto/2026</b>", cellr), P("<b>Julho/2026</b>", cellr)],
    [P("Entradas (realizado)", cell), P(brl(entradas_mes), cellr), P("R$ 74.402,22", cellr)],
    [P("Saídas (realizado)", cell), P(brl(saidas_mes), cellr), P("-R$ 69.491,43", cellr)],
    [P("<b>Resultado</b>", cellrb), P(f"<b>{brl(entradas_mes+saidas_mes)}</b>", cellrb), P("<b>+R$ 4.910,79</b>", cellrb)],
    [P("Saldo em 31/08", cell), P("R$ 31.315,62", cellr), P("R$ 38.834,91", cellr)],
]
E.append(tabela(resumo, [7*cm, 4.5*cm, 4.5*cm]))

E.append(P("Fluxo de Caixa — realizado", h2))
E.append(P(f"Entradas realizadas de {brl(entradas_mes)} e saídas de {brl(saidas_mes)} em agosto. "
           f"Considerando os lançamentos previstos (não pagos/não recebidos), as entradas chegam a {brl(entradas_prev)} "
           f"e as saídas a {brl(saidas_prev)}.", body))

E.append(P("Categorias Receitas", h2))
rec_rows = [[P("<b>Categoria</b>", cell), P("<b>Valor</b>", cellr)]]
rec_vals = [("Receitas (planos, licenças, direcionado)", 6935767), ("Receitas Financeiras", 50863)]
for nome, v in rec_vals:
    rec_rows.append([P(nome, cell), P(brl(v), cellr)])
rec_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(6986630)}</b>", cellrb)])
E.append(tabela(rec_rows, [11*cm, 5*cm]))

E.append(P("Categorias Despesas (categorias cadastradas)", h2))
desp_rows = [[P("<b>Categoria cadastrada</b>", cell), P("<b>Valor</b>", cellr)]]
for nome, v in sorted(desp_cat.items(), key=lambda x: x[1]):
    desp_rows.append([P(nome, cell), P(brl(v), cellr)])
desp_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(saidas_mes)}</b>", cellrb)])
E.append(tabela(desp_rows, [11*cm, 5*cm]))

E.append(P("DRE Gerencial — regime caixa", h2))
dre = [
    [P("<b>Conta</b>", cell), P("<b>Agosto/2026</b>", cellr), P("<b>% receita</b>", cellr)],
    [P("Receita total", cell), P(brl(entradas_mes), cellr), P("100,0%", cellr)],
    [P("(-) Custos Operacionais", cell), P("-R$ 47.314,32", cellr), P("67,7%", cellr)],
    [P("(-) Despesas de RH", cell), P("-R$ 13.222,58", cellr), P("18,9%", cellr)],
    [P("(-) Despesas Administrativas e Comerciais", cell), P("-R$ 13.067,27", cellr), P("18,7%", cellr)],
    [P("(-) Impostos sobre Faturamento", cell), P("-R$ 3.700,92", cellr), P("5,3%", cellr)],
    [P("(-) Despesas Financeiras", cell), P("-R$ 80,50", cellr), P("0,1%", cellr)],
    [P("<b>Resultado do mês</b>", cellrb), P(f"<b>{brl(entradas_mes+saidas_mes)}</b>", cellrb), P("<b>-10,8%</b>", cellrb)],
]
E.append(tabela(dre, [9*cm, 3.5*cm, 3.5*cm]))

E.append(P("DRE Gerencial — regime competência (inclui não pagos e não recebidos)", h2))
dre_c = [
    [P("<b>Conta</b>", cell), P("<b>Agosto/2026</b>", cellr), P("<b>% receita</b>", cellr)],
    [P("Receita total (realizada + a receber)", cell), P(brl(entradas_prev), cellr), P("100,0%", cellr)],
    [P("(-) Despesas totais (realizadas + a pagar)", cell), P(brl(saidas_prev), cellr), P("105,4%", cellr)],
    [P("<b>Resultado do mês (competência)</b>", cellrb), P(f"<b>{brl(entradas_prev+saidas_prev)}</b>", cellrb), P("<b>-5,4%</b>", cellrb)],
]
E.append(tabela(dre_c, [9*cm, 3.5*cm, 3.5*cm]))

E.append(P(f"Receitas em aberto até 31/08/2026", h2))
E.append(P(f"Total em aberto: <b>{brl(total_aberto)}</b> em {len(por_cliente)} clientes (lançamentos de entrada não pagos desde o início das atividades):", body))
ab_rows = [[P("<b>Cliente</b>", cell), P("<b>Valor em aberto</b>", cellr)]]
for nome, v in sorted(por_cliente.items(), key=lambda x: -x[1]):
    ab_rows.append([P(nome, cell), P(brl(v), cellr)])
ab_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(total_aberto)}</b>", cellrb)])
E.append(tabela(ab_rows, [11*cm, 5*cm]))
E.append(Spacer(1, 4))
E.append(P("Nota: parte desses valores pode ser receita já recebida e não conciliada — validar antes de cobrança.", body))

E.append(P("Saldo nas Contas dia 31/08/2026", h2))
sc_rows = [[P("<b>Conta</b>", cell), P("<b>Saldo em 31/08/2026</b>", cellr)]]
for nome, v in saldos_conta:
    sc_rows.append([P(nome, cell), P(brl(v), cellr)])
sc_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(sum(v for _, v in saldos_conta))}</b>", cellrb)])
E.append(tabela(sc_rows, [11*cm, 5*cm]))

E.append(P("Projeção de fluxo de caixa — 12 meses", h2))
E.append(P("Projeção (base ago/26 a jul/27): entradas médias de ~R$ 69 mil/mês contra saídas de ~R$ 70,7 mil/mês — "
           "acumulado de -R$ 20,5 mil. O saldo permanece positivo, mas com tendência de queda: revisar custos operacionais.", body))
proj = [("ago/26",43209.92),("set/26",41649.21),("out/26",40320.70),("nov/26",38213.19),("dez/26",37829.95),
        ("jan/27",35427.21),("fev/27",33649.17),("mar/27",31795.13),("abr/27",29647.03),("mai/27",25603.51),
        ("jun/27",23825.47),("jul/27",22047.43)]
d = Drawing(17*cm, 5.2*cm)
chart = VerticalBarChart()
chart.x, chart.y, chart.width, chart.height = 42, 14, 430, 120
chart.data = [[v for _, v in proj]]
chart.categoryAxis.categoryNames = [m for m, _ in proj]
chart.categoryAxis.labels.fontName = "Helvetica"
chart.categoryAxis.labels.fontSize = 5.5
chart.categoryAxis.labels.angle = 45
chart.valueAxis.valueMin = 0
chart.valueAxis.valueMax = 50000
chart.valueAxis.valueStep = 10000
chart.valueAxis.labels.fontName = "Helvetica"
chart.valueAxis.labels.fontSize = 6
chart.bars[0].fillColor = LARANJA
chart.bars[0].strokeColor = None
d.add(chart)
for i, (m, v) in enumerate(proj):
    d.add(String(48 + i*36.2, 138, f"{v/1000:.0f}k", fontSize=5.5, fillColor=colors.HexColor("#555555")))
E.append(d)

E.append(PageBreak())
E.append(P("Resultado dos últimos 12 meses por categoria", h2))
r12 = [
    [P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)],
    [P("RECEITAS", cell), P("R$ 292.324,61", cellr), P("—", cellr), P("R$ 292.324,61", cellr)],
    [P("RECEITAS FINANCEIRAS", cell), P("R$ 2.001,67", cellr), P("—", cellr), P("R$ 2.001,67", cellr)],
    [P("CUSTOS OPERACIONAIS", cell), P("—", cellr), P("-R$ 192.836,42", cellr), P("-R$ 192.836,42", cellr)],
    [P("DESPESAS ADMINISTRATIVAS E COMERCIAS", cell), P("—", cellr), P("-R$ 30.702,01", cellr), P("-R$ 30.702,01", cellr)],
    [P("DESPESAS DE RH", cell), P("—", cellr), P("-R$ 54.268,81", cellr), P("-R$ 54.268,81", cellr)],
    [P("DESPESAS FINANCEIRAS", cell), P("—", cellr), P("-R$ 318,70", cellr), P("-R$ 318,70", cellr)],
    [P("IMPOSTOS SOBRE FATURAMENTO", cell), P("—", cellr), P("-R$ 14.525,12", cellr), P("-R$ 14.525,12", cellr)],
    [P("<b>Resultado geral (jan–set/2026)</b>", cellrb), P("<b>R$ 294.326,28</b>", cellrb), P("<b>-R$ 292.651,06</b>", cellrb), P("<b>+R$ 1.675,22</b>", cellrb)],
]
E.append(tabela(r12, [7.5*cm, 3.2*cm, 3.2*cm, 3.2*cm]))

E.append(P("Comparativo mês a mês — últimos 13 meses", h2))
cm_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Saldo final</b>", cellr)]]
for label, e_m, s_m, saldo in comp_mensal:
    cm_rows.append([P(label, cell), P(brl(e_m), cellr), P(brl(s_m), cellr), P(brl(saldo), cellr)])
E.append(tabela(cm_rows, [3.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))

E.append(P("Comparativo por categoria (agregação por rateio da API; *set/26 parcial)", h2))
cat_names = sorted({c for c in matriz})
meses_cols = ["2025-09","2025-10","2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"]
labels = ["set/25","out/25","nov/25","dez/25","jan/26","fev/26","mar/26","abr/26","mai/26","jun/26","jul/26","ago/26","set/26*"]
cc_rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{l}</b>", cellr) for l in labels]]
for cat in cat_names:
    row = [P(cat, cell)]
    for m in meses_cols:
        v = matriz[cat].get(m, 0)
        row.append(P(brl(v) if v else "—", cellr))
    cc_rows.append(row)
E.append(tabela(cc_rows, [4.2*cm] + [0.98*cm]*13))

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc.build(E)
print("OK v3")
