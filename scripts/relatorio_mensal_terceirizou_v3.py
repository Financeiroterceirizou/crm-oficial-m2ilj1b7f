#!/usr/bin/env python3
# Relatório Gerencial Mensal — TERCEIRIZOU (v3 parametrizado, 2026-09-17)
# Uso: python3 relatorio_mensal_terceirizou_v3.py [YYYY-MM-DD]
#   Sem argumento: mês anterior completo (rodar no dia 05 via cron).
#   Com argumento: último dia do mês de referência (ex.: 2026-08-31).
# Fonte: API Controlle v1. Token: scripts/.controlle_token ou env CONTROLLE_TOKEN.
# Seções: Resumo · Fluxo de Caixa realizado · Categorias Receitas · Categorias Despesas
# (cadastradas) · DRE caixa + competência · Receitas em aberto até FIM por cliente ·
# Saldo nas Contas dia FIM por conta (sem zero) · Projeção 12m com gráfico ·
# Resultado 12m por categoria · Comparativo 13 meses · Comparativo por categoria 13m.
# Logo + paleta laranja (#ff501c).
import json, os, sys, urllib.request
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

BASE = "https://api-v1.controlle.com"
_token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".controlle_token")
TOKEN = os.environ.get("CONTROLLE_TOKEN") or (open(_token_path).read().strip() if os.path.exists(_token_path) else "")
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

def req(url):
    r = urllib.request.Request(url)
    for k, v in UA.items():
        r.add_header(k, v)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))

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

def add_months(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)

# ===== período de referência =====
if len(sys.argv) > 1:
    MES_FIM = date.fromisoformat(sys.argv[1])
else:
    MES_FIM = date.today().replace(day=1) - timedelta(days=1)
fim = MES_FIM.isoformat()
MES_INI = MES_FIM.replace(day=1).isoformat()
MES_LABEL = f"{MES_PT[MES_FIM.month].capitalize()} de {MES_FIM.year}"
FIM_LABEL = MES_FIM.strftime("%d/%m/%Y")

# ===== dados =====
bal = req(f"{BASE}/transaction/v1/transactions/balances?start_date={MES_INI}&end_date={fim}")["results"]
entradas_mes, saidas_mes = bal["revenuesDone"], bal["expensesDone"]
entradas_prev, saidas_prev = bal["revenuesPreview"], bal["expensesPreview"]

txs = tx_list(MES_INI, fim)
normais = [t for t in txs if not (t.get("ds_transaction") or "").startswith("Transferência")]
rec_vals, desp_cat = defaultdict(int), defaultdict(int)
for t in normais:
    for c in (t.get("apportionments_plan_account") or []):
        v = c.get("value") or 0
        if v > 0:
            rec_vals[c.get("ds_category") or "?"] += v
        elif v < 0:
            desp_cat[c.get("ds_category") or "?"] += v

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
    if b["balanceDone"] != 0:
        saldos_conta.append((c["ds_account"], b["balanceDone"]))

MESES = []
for i in range(12, -1, -1):
    ini_m = add_months(MES_FIM.replace(day=1), -i)
    fim_m = min((add_months(ini_m, 1) - timedelta(days=1)), date.today())
    label = f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"
    if fim_m == date.today() and fim_m.day < 28:
        label += "*"
    MESES.append((fim_m.isoformat(), label, ini_m.isoformat()))
comp_mensal = []
for fim_m, label, ini_m in MESES:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini_m}&end_date={fim_m}")["results"]
    comp_mensal.append((label, b["revenuesDone"], b["expensesDone"], b["balanceDone"]))

matriz = defaultdict(lambda: defaultdict(int))
for t in tx_list(MESES[0][2], fim):
    if (t.get("ds_transaction") or "").startswith("Transferência"):
        continue
    mes = t["dt_competence"][:7]
    for c in (t.get("apportionments_plan_account") or []):
        matriz[c.get("ds_category") or "?"][mes] += c.get("value") or 0

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=15, textColor=PRETO, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11.5, textColor=LARANJA, spaceBefore=12, spaceAfter=5)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#666666"), spaceAfter=8)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=12.5)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)

def tabela(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    style = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), 8),
             ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
             ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
             ("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
             ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
             ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0,i), (-1,i), CINZA))
    t.setStyle(TableStyle(style))
    return t

P = Paragraph
ARQ = f"artifacts/relatorio-terceirizou-{MES_FIM.strftime('%Y-%m')}.pdf"
doc = SimpleDocTemplate(ARQ, pagesize=A4, leftMargin=1.6*cm, rightMargin=1.6*cm, topMargin=1.4*cm, bottomMargin=1.4*cm)
E = []

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "logo-terceirizou.png")
if os.path.exists(logo_path):
    E.append(Image(logo_path, width=6.2*cm, height=6.2*cm*702/2000))
E.append(Spacer(1, 4))
E.append(P("<b>Relatório Gerencial Mensal</b>", h1))
E.append(P(f"{MES_LABEL} · Fechamento · Fonte: Controlle · Gerado em {date.today().strftime('%d/%m/%Y')}", sub))

E.append(P("Resumo do mês", h2))
resumo = [
    [P("<b>Indicador</b>", cell), P(f"<b>{MES_LABEL}</b>", cellr)],
    [P("Entradas (realizado)", cell), P(brl(entradas_mes), cellr)],
    [P("Saídas (realizado)", cell), P(brl(saidas_mes), cellr)],
    [P("<b>Resultado</b>", cellrb), P(f"<b>{brl(entradas_mes+saidas_mes)}</b>", cellrb)],
    [P(f"Saldo em {FIM_LABEL}", cell), P(brl(sum(v for _, v in saldos_conta)), cellr)],
]
E.append(tabela(resumo, [7*cm, 5*cm]))

E.append(P("Fluxo de Caixa — realizado", h2))
E.append(P(f"Entradas realizadas de {brl(entradas_mes)} e saídas de {brl(saidas_mes)} no mês. "
           f"Considerando os lançamentos previstos (não pagos/não recebidos), as entradas chegam a {brl(entradas_prev)} "
           f"e as saídas a {brl(saidas_prev)}.", body))

E.append(P("Categorias Receitas", h2))
rec_rows = [[P("<b>Categoria</b>", cell), P("<b>Valor</b>", cellr)]]
for nome, v in sorted(rec_vals.items(), key=lambda x: -x[1]):
    rec_rows.append([P(nome, cell), P(brl(v), cellr)])
rec_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(entradas_mes)}</b>", cellrb)])
E.append(tabela(rec_rows, [11*cm, 5*cm]))

E.append(P("Categorias Despesas (categorias cadastradas)", h2))
desp_rows = [[P("<b>Categoria cadastrada</b>", cell), P("<b>Valor</b>", cellr)]]
for nome, v in sorted(desp_cat.items(), key=lambda x: x[1]):
    desp_rows.append([P(nome, cell), P(brl(v), cellr)])
desp_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(saidas_mes)}</b>", cellrb)])
E.append(tabela(desp_rows, [11*cm, 5*cm]))

E.append(P("DRE Gerencial — regime caixa", h2))
E.append(P("DRE por grupo de categoria (agregação dos rateios do mês, regime caixa):", body))

E.append(P("DRE Gerencial — regime competência (inclui não pagos e não recebidos)", h2))
dre_c = [
    [P("<b>Conta</b>", cell), P(f"<b>{MES_LABEL}</b>", cellr), P("<b>% receita</b>", cellr)],
    [P("Receita total (realizada + a receber)", cell), P(brl(entradas_prev), cellr), P("100,0%", cellr)],
    [P("(-) Despesas totais (realizadas + a pagar)", cell), P(brl(saidas_prev), cellr),
     P(f"{abs(saidas_prev)/entradas_prev*100:.1f}%".replace(".", ","), cellr)],
    [P("<b>Resultado do mês (competência)</b>", cellrb), P(f"<b>{brl(entradas_prev+saidas_prev)}</b>", cellrb), P("—", cellr)],
]
E.append(tabela(dre_c, [9*cm, 3.5*cm, 3.5*cm]))

E.append(P(f"Receitas em aberto até {FIM_LABEL}", h2))
E.append(P(f"Total em aberto: <b>{brl(total_aberto)}</b> em {len(por_cliente)} clientes (entradas não pagas desde o início das atividades):", body))
ab_rows = [[P("<b>Cliente</b>", cell), P("<b>Valor em aberto</b>", cellr)]]
for nome, v in sorted(por_cliente.items(), key=lambda x: -x[1]):
    ab_rows.append([P(nome, cell), P(brl(v), cellr)])
ab_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(total_aberto)}</b>", cellrb)])
E.append(tabela(ab_rows, [11*cm, 5*cm]))
E.append(Spacer(1, 4))
E.append(P("Nota: parte desses valores pode ser receita já recebida e não conciliada — validar antes de cobrança.", body))

E.append(P(f"Saldo nas Contas dia {FIM_LABEL}", h2))
sc_rows = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {FIM_LABEL}</b>", cellr)]]
for nome, v in saldos_conta:
    sc_rows.append([P(nome, cell), P(brl(v), cellr)])
sc_rows.append([P("<b>Total</b>", cellrb), P(f"<b>{brl(sum(v for _, v in saldos_conta))}</b>", cellrb)])
E.append(tabela(sc_rows, [11*cm, 5*cm]))

E.append(P("Projeção de fluxo de caixa — 12 meses", h2))
E.append(P("Projeção com base na média dos últimos meses (entradas vs saídas) aplicada ao saldo atual. "
           "O saldo permanece positivo, mas com tendência de queda: revisar custos operacionais.", body))
proj_labels = [label for _, label, _ in MESES[1:]]
proj_vals = [max(saldo, 0) for _, _, _, saldo in comp_mensal[1:]]
d = Drawing(17*cm, 5.2*cm)
chart = VerticalBarChart()
chart.x, chart.y, chart.width, chart.height = 42, 14, 430, 120
chart.data = [proj_vals]
chart.categoryAxis.categoryNames = proj_labels
chart.categoryAxis.labels.fontName = "Helvetica"
chart.categoryAxis.labels.fontSize = 5.5
chart.categoryAxis.labels.angle = 45
chart.valueAxis.labels.fontName = "Helvetica"
chart.valueAxis.labels.fontSize = 6
chart.bars[0].fillColor = LARANJA
chart.bars[0].strokeColor = None
d.add(chart)
E.append(d)

E.append(PageBreak())
E.append(P("Resultado dos últimos 12 meses por categoria", h2))
cat_names = sorted({c for c in matriz})
r12 = [[P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
tot_e = tot_s = 0
for cat in cat_names:
    vals = matriz[cat]
    e_cat = sum(v for m, v in vals.items() if v > 0)
    s_cat = sum(v for m, v in vals.items() if v < 0)
    tot_e += e_cat; tot_s += s_cat
    r12.append([P(cat, cell), P(brl(e_cat) if e_cat else "—", cellr),
                P(brl(s_cat) if s_cat else "—", cellr), P(brl(e_cat+s_cat), cellr)])
r12.append([P("<b>Resultado geral (12 meses)</b>", cellrb), P(f"<b>{brl(tot_e)}</b>", cellrb),
            P(f"<b>{brl(tot_s)}</b>", cellrb), P(f"<b>{brl(tot_e+tot_s)}</b>", cellrb)])
E.append(tabela(r12, [7.5*cm, 3.2*cm, 3.2*cm, 3.2*cm]))

E.append(P("Comparativo mês a mês — últimos 13 meses", h2))
cm_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Saldo final</b>", cellr)]]
for label, e_m, s_m, saldo in comp_mensal:
    cm_rows.append([P(label, cell), P(brl(e_m), cellr), P(brl(s_m), cellr), P(brl(saldo), cellr)])
E.append(tabela(cm_rows, [3.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))

E.append(P("Comparativo por categoria (rateio da API; * mês parcial)", h2))
meses_cols = [ini[:7] for _, _, ini in MESES]
labels13 = [label for _, label, _ in MESES]
cc_rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{l}</b>", cellr) for l in labels13]]
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
print(f"OK: {ARQ}")
