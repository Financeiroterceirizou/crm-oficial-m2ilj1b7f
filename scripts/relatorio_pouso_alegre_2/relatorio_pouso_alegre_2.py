#!/usr/bin/env python3
# Relatório Mensal — POUSO ALEGRE 2 (VERONA) VISTORIA — v1.0, 2026-09-29 (formato Uberlândia v1.2 + competência)
# Uso: python3 relatorio_pouso_alegre_2.py [YYYY-MM-DD]  (default: hoje)
# Gera UM PDF (logo Terceirizou na capa e símbolo no canto inferior direito das páginas seguintes) + UM Excel.
# Estrutura (v1.0):
#   Capa COMPACTA + 1. Receitas e Despesas por categoria do mês anterior NA MESMA PÁGINA
#   (REGIME DE COMPETÊNCIA: janela larga + dt_competence, INCLUI NÃO PAGOS, sem transferências;
#   06.01 Distribuição de Resultado em negrito) · 2. Comparativo 6 meses por categoria
#   (REGIME DE COMPETÊNCIA: inclui não pagos; Média no lugar do Total, R$ inteiros, + linha Resultado do mês) ·
#   3. Previsão de despesas do mês corrente (caixa) · 4. Saldo nas contas dia 31/08 ·
#   5. Despesas em aberto até 31/08 (mesma página do saldo quando couber) · 6. Resumo "Previsão para <mês>"
# Excel: título na 1ª linha de cada aba + Comparativo com coluna Média + linha "Resultado do mês"
#   (média e total dos 6 meses) + aba "Previsão <mês>" + aba "Detalhe <mês>" (competência, por categoria).
# Fonte: API Controlle v1 (token Pouso Alegre 2). Envio: MENSAL dia 04 14:00 → vinicius@terceirizou.com.br.
import json, os, sys, urllib.request
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image as RLImage)

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_POUSO_ALEGRE_2") or open(os.path.join(_dir, ".controlle_token_pouso_alegre_2")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
LOGO = os.path.join(_dir, "logo-terceirizou.png")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

def req(url):
    r = urllib.request.Request(url)
    for k, v in UA.items():
        r.add_header(k, v)
    with urllib.request.urlopen(r, timeout=120) as resp:
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

def brl_int(cents):
    """Sem centavos e sem R$ — matrizes largas (comparativo 6 meses)."""
    v = int(round(cents / 100.0))
    s = f"{abs(v):,}".replace(",", ".")
    return ("-" if v < 0 else "") + s

def add_months(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)

def bdate(t):
    return (t.get("dt_billing") or t.get("dt_due") or "")[:10]

def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "?") if cats else "(sem categoria)"

def ok_ub(t):
    """Filtro padrão: sem transferências entre contas (categoria 99.01 ou descrição 'Transferência')."""
    for c in (t.get("apportionments_plan_account") or []):
        if (c.get("ds_category") or "").startswith("99.01"):
            return False
    if (t.get("ds_transaction") or "").upper().startswith("TRANSFERÊNCIA"):
        return False
    return True

def agrupa_por_categoria(txs, so_negativas=False, so_positivas=False):
    g = defaultdict(lambda: [0, 0])
    for t in txs:
        v = t["value_in_cent"]
        if so_negativas and v >= 0: continue
        if so_positivas and v <= 0: continue
        g[cat_nome(t)][0] += v
        g[cat_nome(t)][1] += 1
    return g

def dias_uteis(ini, fim, feriados=()):
    n, d = 0, ini
    while d <= fim:
        if d.weekday() < 5 and d not in feriados:
            n += 1
        d += timedelta(days=1)
    return n

# ===== datas =====
HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_ANT = add_months(HOJE.replace(day=1), -1)          # mês anterior (agosto)
FIM_MES_ANT = MES_ANT.replace(day=28) + timedelta(days=4)
FIM_MES_ANT = FIM_MES_ANT - timedelta(days=FIM_MES_ANT.day)  # último dia do mês anterior (31/08)
MES_COR = HOJE.replace(day=1)                          # mês corrente (setembro)
FIM_MES_COR = MES_COR.replace(day=28) + timedelta(days=4)
FIM_MES_COR = FIM_MES_COR - timedelta(days=FIM_MES_COR.day)

# feriados nacionais fixos no semestre corrente (mês corrente e anterior)
FERIADOS = set()
for y in (MES_COR.year, MES_ANT.year):
    for d, m in ((1,1),(21,4),(1,5),(7,9),(12,10),(2,11),(15,11),(25,12)):
        FERIADOS.add(date(y, m, d))

HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")

# ===== dados =====
# 1. Receitas e Despesas por categoria do mês anterior — REGIME DE COMPETÊNCIA
# (janela larga + filtro dt_competence; inclui não pagos; sem transferências)
_tx_janela = tx_list(f"{MES_ANT.year}-01-01", f"{MES_ANT.year + 1}-12-31")
mes_ant_tx = [t for t in _tx_janela if (t.get("dt_competence") or "")[:7] == f"{MES_ANT.year}-{MES_ANT.month:02d}" and ok_ub(t)]
ant_rec = agrupa_por_categoria(mes_ant_tx, so_positivas=True)
ant_desp = agrupa_por_categoria(mes_ant_tx, so_negativas=True)
ant_entradas = sum(v for v, _ in ant_rec.values())
ant_saidas = sum(v for v, _ in ant_desp.values())
ant_resultado = ant_entradas + ant_saidas

# 2. Comparativo dos últimos 06 meses por categoria — REGIME DE COMPETÊNCIA (inclui não pagos, sem transferências)
INI_6 = add_months(MES_ANT, -5)
meses_6 = []
for i in range(0, 6):
    ini_m = add_months(INI_6, i)
    fim_m = add_months(ini_m, 1) - timedelta(days=1)
    meses_6.append((ini_m.isoformat(), fim_m.isoformat(), f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"))
# REGIME DE COMPETÊNCIA: janela larga + filtro dt_competence; inclui não pagos
_tx_janela_6 = tx_list(f"{INI_6.year}-01-01", f"{MES_ANT.year + 1}-12-31")
matriz_6 = defaultdict(lambda: defaultdict(int))
for t in _tx_janela_6:
    if not ok_ub(t):
        continue
    mes = (t.get("dt_competence") or "")[:7]
    for c in (t.get("apportionments_plan_account") or []):
        matriz_6[c.get("ds_category") or "?"][mes] += c.get("value") or 0

# 3. Previsão de despesas para o mês corrente por categoria (pago + pendente, sem transferências)
prev_cor = [t for t in tx_list(MES_COR.isoformat(), FIM_MES_COR.isoformat()) if ok_ub(t)]
prev_desp = agrupa_por_categoria(prev_cor, so_negativas=True)
prev_desp_total = sum(v for v, _ in prev_desp.values())

# 4. Saldo nas contas no último dia do mês anterior
contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
saldos_conta = []
for c in contas:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={FIM_MES_ANT.isoformat()}&id_account_main={c['id']}")["results"]
    saldos_conta.append((c["ds_account"], b["balanceDone"]))
saldos_conta = [(n, v) for n, v in saldos_conta if v != 0]
total_saldos = sum(v for _, v in saldos_conta)

# 5. Despesas em aberto até o último dia do mês anterior
desp_aberto = [t for t in tx_list(f"{FIM_MES_ANT.year}-01-01", FIM_MES_ANT.isoformat(), **{"activity_type": "0", "situation": "[0]"})
               if bdate(t) <= FIM_MES_ANT.isoformat() and ok_ub(t)]
g_desp_aberto = agrupa_por_categoria(desp_aberto)
total_desp_aberto = sum(v for v, _ in g_desp_aberto.values())

# 6. Resumo — Previsão de Resultado do Mês corrente (faturamento pela COMPETÊNCIA do mês anterior)
DU_ANT = dias_uteis(MES_ANT, FIM_MES_ANT, FERIADOS)
DU_COR = dias_uteis(MES_COR, FIM_MES_COR, FERIADOS)
FAT_ANT = ant_entradas
MEDIA_DIA = FAT_ANT / DU_ANT if DU_ANT else 0
FAT_PREV = round(MEDIA_DIA * DU_COR)
DESP_PREV = prev_desp_total
RESULT_PREV = FAT_PREV + DESP_PREV
SALDO_PREV_FIM = RESULT_PREV + total_desp_aberto + total_saldos

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=PRETO, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=LARANJA, spaceBefore=14, spaceAfter=3)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, textColor=PRETO, spaceBefore=10, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#777777"), spaceAfter=10)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=12.5)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
VERDE = colors.HexColor("#1a7f37")   # receitas
VERMELHO = colors.HexColor("#c0392b")  # despesas

def P_val(cents, style):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl(cents), s)

def P_val_int(cents, style):
    """Valor colorido sem centavos e sem R$ — matrizes largas (comparativo 6 meses)."""
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl_int(cents), s)

def tabela(rows, widths, fs=7.5):
    t = Table(rows, colWidths=widths, repeatRows=1)
    style = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), fs),
             ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
             ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
             ("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
             ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
             ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0,i), (-1,i), CINZA))
    t.setStyle(TableStyle(style))
    return t

def tabela_cat(titulo, grupos, total_label="Total"):
    rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nome, (v, n) in sorted(grupos.items(), key=lambda x: x[0]):
        rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tot = sum(v for v, _ in grupos.values())
    rows.append([P(f"<b>{total_label}</b>", cellrb), P(f"<b>{sum(n for _, n in grupos.values())}</b>", cellc), P_val(tot, cellrb)])
    t = tabela(rows, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
    return [P(f"<b>{titulo}</b>", h2), t]

P = Paragraph
ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Pouso_Alegre_2.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.3*cm, bottomMargin=1.3*cm,
                        title="Relatório Gerencial — Pouso Alegre 2 (Verona) Vistoria")
E = []

# ===== capa compacta + 1º relatório na MESMA página =====
h1c = ParagraphStyle("h1c", parent=h1, fontSize=13, alignment=1, spaceAfter=1)
h2c = ParagraphStyle("h2c", parent=h2, fontSize=11, alignment=1, spaceBefore=2, spaceAfter=2)
subc = ParagraphStyle("subc", parent=sub, fontSize=8, alignment=1, spaceAfter=0)
if os.path.exists(LOGO):
    img = RLImage(LOGO, width=5.5*cm, height=5.5*cm*561/1600)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 10))
E.append(P("<b>POUSO ALEGRE 2 (VERONA) VISTORIA</b>", h1c))
E.append(P("Relatório Gerencial Mensal", h2c))
E.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · Ref.: {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year}", subc))
E.append(Spacer(1, 8))

# ===== 1. Receitas e Despesas por categoria do mês anterior (competência) =====
bloco = []
bloco.append(P(f"Receitas e Despesas por Categoria — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de competência)", h2))
rd_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for nome, (v, n) in sorted(ant_rec.items()):
    rd_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
rd_rows.append([P("<b>Total de Receitas</b>", cellrb), P(f"<b>{sum(n for _, n in ant_rec.values())}</b>", cellc), P_val(ant_entradas, cellrb)])
for nome, (v, n) in sorted(ant_desp.items()):
    if nome.startswith("06.01"):  # Distribuição de Resultado: negrito, cor padrão das categorias
        rd_rows.append([P(f"<b>{nome}</b>", cell), P(f"<b>{n}</b>", cellc), P_val(v, cellb)])
    else:
        rd_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
rd_rows.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n for _, n in ant_desp.values())}</b>", cellc), P_val(ant_saidas, cellrb)])
rd_rows.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{len(mes_ant_tx)}</b>", cellc), P_val(ant_resultado, cellrb)])
t = tabela(rd_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rd_rows)-3), (-1,len(rd_rows)-1), LARANJA_CLARO)]))
bloco.append(t)
E.extend(bloco)

# ===== 2. Comparativo dos últimos 06 meses por categoria (competência) =====
E.append(PageBreak())
E.append(P(f"Comparativo dos Últimos 6 Meses por Categoria ({MES_AB[INI_6.month]}/{str(INI_6.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) — regime de competência", h2))
cat_names_6 = sorted({c for c in matriz_6})
cm_rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{lab}</b>", cellr) for _, _, lab in meses_6] + [P("<b>Média</b>", cellr)]]
for cat in cat_names_6:
    row = [P(cat, cell)]
    vals6 = [matriz_6[cat].get(fim_m_iso[:7], 0) for _, fim_m_iso, _ in meses_6]
    for v in vals6:
        row.append(P_val_int(v, cellr) if v else P("—", cellr))
    row.append(P_val_int(round(sum(vals6) / len(vals6)), cellrb))
    cm_rows.append(row)
# linha de resultado do mês (entradas − saídas de cada mês, pela matriz)
res_row = [P("<b>Resultado do mês</b>", cellb)]
for _, fim_m_iso, lab in meses_6:
    tot_mes = sum(v[fim_m_iso[:7]] for v in matriz_6.values())
    res_row.append(P_val_int(tot_mes, cellrb))
media_res = round(sum(sum(v[fim_m_iso[:7]] for v in matriz_6.values()) for _, fim_m_iso, _ in meses_6) / len(meses_6))
res_row.append(P_val_int(media_res, cellrb))
cm_rows.append(res_row)
E.append(tabela(cm_rows, [5.4*cm] + [1.55*cm]*6 + [1.9*cm], fs=6.5))

# ===== 3. Previsão de despesas para o mês corrente por categoria =====
E.append(PageBreak())
E.append(P(f"Previsão de Despesas — {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year}", h2))
pd_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for nome, (v, n) in sorted(prev_desp.items()):
    pd_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
pd_rows.append([P("<b>Total de Despesas Previstas</b>", cellrb), P(f"<b>{sum(n for _, n in prev_desp.values())}</b>", cellc), P_val(prev_desp_total, cellrb)])
t = tabela(pd_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(pd_rows)-1), (-1,len(pd_rows)-1), LARANJA_CLARO)]))
E.append(t)

# ===== 4. Saldo nas contas no último dia do mês anterior =====
E.append(PageBreak())
E.append(P(f"Saldo nas contas em {FIM_MES_ANT_LABEL}", h2))
sc_rows = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {FIM_MES_ANT_LABEL}</b>", cellr)]]
for nome, v in saldos_conta:
    sc_rows.append([P(nome, cell), P_val(v, cellr)])
sc_rows.append([P("<b>Total</b>", cellrb), P_val(total_saldos, cellrb)])
t = tabela(sc_rows, [11*cm, 5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(sc_rows)-1), (-1,len(sc_rows)-1), LARANJA_CLARO)]))
E.append(t)

# ===== 5. Despesas em aberto até o último dia do mês anterior (mesma página do saldo, se couber) =====
E.append(Spacer(1, 18))
E.append(P(f"Despesas em aberto até {FIM_MES_ANT_LABEL}", h2))
E += tabela_cat("Resumo por categoria", g_desp_aberto, total_label="Total em aberto")
if desp_aberto:
    por_cat = defaultdict(list)
    for t in desp_aberto:
        por_cat[cat_nome(t)].append(t)
    E.append(P("<b>Demonstrativo dos lançamentos</b>", h2))
    for cat in sorted(por_cat):
        txs_cat = sorted(por_cat[cat], key=bdate)
        rows = [[P("<b>Vencimento</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell), P("<b>Situação</b>", cellc), P("<b>Valor</b>", cellr)]]
        for t in txs_cat:
            d = bdate(t)
            rows.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell), P((t.get("ds_transaction") or "")[:70], cell),
                         P(t.get("ds_account_main") or "", cell), P("Aberto", cellc), P_val(t["value_in_cent"], cellr)])
        rows.append([P("<b>Total</b>", cellrb), P(f"<b>{cat}</b>", cellrb), P("", cell), P(f"<b>{len(txs_cat)}</b>", cellc), P_val(sum(t["value_in_cent"] for t in txs_cat), cellrb)])
        tt = tabela(rows, [2.2*cm, 7.3*cm, 3.2*cm, 1.8*cm, 3*cm])
        tt.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
        E.append(P(f"<b>{cat}</b>", h3))
        E.append(tt)

# ===== 6. Resumo — Previsão para o mês corrente (fontes maiores para leitura) =====
E.append(PageBreak())
h1_res = ParagraphStyle("h1_res", parent=h1, fontSize=18, alignment=1, spaceAfter=14)
rs_cell = ParagraphStyle("rs_cell", parent=cell, fontSize=11)
rs_cellr = ParagraphStyle("rs_cellr", parent=rs_cell, alignment=2)
rs_cellrb = ParagraphStyle("rs_cellrb", parent=rs_cellr, fontName="Helvetica-Bold")
E.append(P(f"Previsão para {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year}", h1_res))
rs_rows = []
rs_rows.append([P(f"<b>Previsão Faturamento {MES_PT[MES_COR.month].capitalize()}</b> (média/dia útil de {MES_AB[MES_ANT.month]} × {DU_COR} dias úteis)", rs_cell),
                P_val(FAT_PREV, rs_cellr)])
rs_rows.append([P(f"<b>Previsão Despesa {MES_PT[MES_COR.month].capitalize()}</b>", rs_cell), P_val(DESP_PREV, rs_cellr)])
rs_rows.append([P(f"<b>Previsão de Resultado {MES_PT[MES_COR.month].capitalize()}</b>", rs_cellrb), P_val(RESULT_PREV, rs_cellrb)])
rs_rows.append([P(f"<b>Despesas em aberto até {FIM_MES_ANT_LABEL}</b>", rs_cell), P_val(total_desp_aberto, rs_cellr)])
rs_rows.append([P(f"<b>Saldo nas contas em {FIM_MES_ANT_LABEL}</b>", rs_cell), P_val(total_saldos, rs_cellr)])
rs_rows.append([P(f"<b>Previsão de Saldo em {FIM_MES_COR.strftime('%d/%m/%Y')}</b>", rs_cellrb), P_val(SALDO_PREV_FIM, rs_cellrb)])
t = tabela(rs_rows, [12*cm, 4.5*cm], fs=11)
t.setStyle(TableStyle([("BACKGROUND", (0,2), (-1,2), LARANJA_CLARO), ("BACKGROUND", (0,5), (-1,5), LARANJA_CLARO)]))
E.append(t)
E.append(Spacer(1, 10))
E.append(P(f"Base do cálculo: faturamento de {MES_PT[MES_ANT.month].capitalize()} (competência) foi {brl(FAT_ANT)} em {DU_ANT} dias úteis "
           f"(média de {brl(int(round(MEDIA_DIA)))} por dia útil). Previsão de setembro: média/dia × {DU_COR} dias úteis. "
           f"Previsão de saldo final = previsão de resultado − despesas em aberto + saldo nas contas.", sub))

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))

# símbolo (o "5" laranja) no canto inferior direito das páginas seguintes
# gerar recorte do símbolo (o "5" laranja = ~23% esquerdo da logo horizontal)
from PIL import Image as PILImage
img_full = PILImage.open(LOGO)
_w, _h = img_full.size
sim = img_full.crop((0, 0, int(_w * 0.233), _h))
bbox = sim.getbbox()
if bbox:
    sim = sim.crop(bbox)
sim.save(os.path.join(_dir, "simbolo-terceirizou.png"))
print(f"simbolo: {sim.size}")

def _desenha_logo(canvas, doc_):
    if not os.path.exists(LOGO):
        return
    canvas.saveState()
    sim_path = os.path.join(_dir, "simbolo-terceirizou.png")
    if os.path.exists(sim_path):
        from PIL import Image as PILImage2
        sw, sh = PILImage2.open(sim_path).size
        alt = 0.85*cm
        img_s = RLImage(sim_path, width=alt*sw/sh, height=alt)
        img_s.drawOn(canvas, A4[0]-1.9*cm, 0.8*cm)
    canvas.restoreState()

def _capa(canvas, doc_):
    pass

def _on_page(canvas, doc_):
    if doc_.page > 1:  # pula a capa
        _desenha_logo(canvas, doc_)

doc.build(E, onFirstPage=_capa, onLaterPages=_on_page)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Pouso_Alegre_2.xlsx"
wb = Workbook()
wb.remove(wb.active)
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"
VERMELHO_XL = "C0392B"
TOT_LABELS = ("Total", "Totais", "Resultado", "Previsão", "Total de Receitas", "Total de Despesas",
              "Total de Despesas Previstas", "Previsão de Saldo")

def aba(nome, linhas, larguras, titulo=None):
    ws = wb.create_sheet(nome[:31])
    if titulo:
        ws.append((titulo,))
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(1, len(larguras)))
        c = ws.cell(row=1, column=1)
        c.font = Font(bold=True, size=12, color="FF501C")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 22
        desloc = 1
    else:
        desloc = 0
    for r in linhas:
        ws.append(list(r))
    hdr_row = desloc + 1
    headers = [str(ws.cell(row=hdr_row, column=j).value or "") for j in range(1, ws.max_column + 1)]
    for c in ws[hdr_row]:
        c.fill = FILL_H
        c.font = FH
        c.alignment = Alignment(horizontal="center", vertical="center")
    for row in ws.iter_rows(min_row=hdr_row + 1):
        label = str(row[0].value or "")
        is_total = label.startswith(TOT_LABELS)
        if is_total:
            for c in row:
                c.fill = FILL_T
                c.alignment = Alignment(horizontal="center", vertical="center")
            row[0].font = FB
        for j, c in enumerate(row[1:], 2):
            if isinstance(c.value, (int, float)):
                hdr = headers[j-1] if j-1 < len(headers) else ""
                if "Lançamentos" in hdr:
                    c.number_format = "0"
                    c.font = Font(bold=is_total)
                else:
                    c.number_format = '"R$" #,##0.00'
                    cor = VERDE_XL if c.value > 0 else (VERMELHO_XL if c.value < 0 else "1A1A1A")
                    c.font = Font(bold=is_total, color=cor)
    for j, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=hdr_row + 1, column=1)

r_ = lambda v: v / 100

aba("Receitas e Despesas " + MES_AB[MES_ANT.month],
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(ant_rec.items())] +
    [("Total de Receitas", sum(n for _, n in ant_rec.values()), r_(ant_entradas))] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(ant_desp.items())] +
    [("Total de Despesas", sum(n for _, n in ant_desp.values()), r_(ant_saidas)),
     ("Resultado do mês", len(mes_ant_tx), r_(ant_resultado))],
    [45, 14, 16], titulo=f"Receitas e Despesas por Categoria — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de competência)")

aba("Comparativo 6 meses",
    [("Categoria",) + tuple(lab for _, _, lab in meses_6) + ("Média", "Total")] +
    [(cat,) + tuple((r_(v) if (v := matriz_6[cat].get(fim_m_iso[:7], 0)) else None) for _, fim_m_iso, _ in meses_6)
     + (r_(round(sum(matriz_6[cat].values()) / len(meses_6))), r_(sum(matriz_6[cat].values())),)
     for cat in cat_names_6],
    [40] + [13]*6 + [13, 15], titulo=f"Comparativo dos Últimos 6 Meses por Categoria ({MES_AB[INI_6.month]}/{str(INI_6.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) — regime de competência")

# linha de resultado do mês no Excel (igual ao PDF: entradas - saídas de cada mês, pela matriz)
_ws_cmp = wb["Comparativo 6 meses"]
_row_res = ["Resultado do mês"]
for _, fim_m_iso, _ in meses_6:
    _tot = sum(v[fim_m_iso[:7]] for v in matriz_6.values())
    _row_res.append(int(round(_tot / 100)) if _tot else None)
_res_mensais = [sum(v[fim_m_iso[:7]] for v in matriz_6.values()) for _, fim_m_iso, _ in meses_6]
_row_res.append(int(round(sum(_res_mensais) / len(meses_6) / 100)))
_row_res.append(int(round(sum(_res_mensais) / 100)))
_ws_cmp.append(_row_res)
_r = _ws_cmp.max_row
for _j, _c in enumerate(_ws_cmp[_r], 1):
    if _j == 1:
        _c.font = Font(bold=True)
        _c.fill = FILL_T
    elif isinstance(_c.value, (int, float)):
        _c.number_format = '"R$" #,##0.00'
        _c.font = Font(bold=True, color=(VERDE_XL if _c.value > 0 else VERMELHO_XL if _c.value < 0 else "1A1A1A"))
        _c.fill = FILL_T
    else:
        _c.fill = FILL_T

aba("Previsão Despesas " + MES_AB[MES_COR.month],
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(prev_desp.items())] +
    [("Total de Despesas Previstas", sum(n for _, n in prev_desp.values()), r_(prev_desp_total))],
    [45, 14, 16], titulo=f"Previsão de Despesas — {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year}")

aba("Saldo contas",
    [("Conta", f"Saldo em {FIM_MES_ANT_LABEL}")] +
    [(n, r_(v)) for n, v in saldos_conta] +
    [("Total", r_(total_saldos))],
    [30, 18], titulo=f"Saldo nas contas em {FIM_MES_ANT_LABEL}")

aba("Despesas em aberto",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_desp_aberto.items())] +
    [("Total em aberto", len(desp_aberto), r_(total_desp_aberto))],
    [45, 14, 16], titulo=f"Despesas em aberto até {FIM_MES_ANT_LABEL}")

aba("Previsão " + MES_AB[MES_COR.month],
    [("Item", "Valor"),
     (f"Previsão Faturamento {MES_PT[MES_COR.month].capitalize()} ({DU_COR} dias úteis)", r_(FAT_PREV)),
     (f"Previsão Despesa {MES_PT[MES_COR.month].capitalize()}", r_(DESP_PREV)),
     (f"Previsão de Resultado {MES_PT[MES_COR.month].capitalize()}", r_(RESULT_PREV)),
     (f"Despesas em aberto até {FIM_MES_ANT_LABEL}", r_(total_desp_aberto)),
     (f"Saldo nas contas em {FIM_MES_ANT_LABEL}", r_(total_saldos)),
     (f"Previsão de Saldo em {FIM_MES_COR.strftime('%d/%m/%Y')}", r_(SALDO_PREV_FIM))],
    [55, 18], titulo=f"Previsão para {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year}")

# lançamentos do mês anterior (competência) agrupados por categoria, com total por categoria
def detalhe_agrupado(txs):
    por_cat = defaultdict(list)
    for t in txs:
        por_cat[cat_nome(t)].append(t)
    rows = [("Data", "Tipo", "Descrição", "Conta", "Categoria", "Situação", "Valor")]
    for cat in sorted(por_cat):
        for t in sorted(por_cat[cat], key=bdate):
            d = (t.get("dt_billing") or t.get("dt_due") or "")[:10]
            rows.append((d, "Entrada" if t["activity_type"] == 1 else "Saída",
                         (t["ds_transaction"] or "")[:60], t.get("ds_account_main") or "", cat,
                         "Pago" if t["situation"] == 1 else "Pendente", r_(t["value_in_cent"])))
        rows.append(("Total", "", "", "", cat, "", r_(sum(t["value_in_cent"] for t in por_cat[cat]))))
    return rows

aba("Detalhe " + MES_AB[MES_ANT.month],
    detalhe_agrupado(mes_ant_tx) + [(f"Resultado do mês ({MES_PT[MES_ANT.month].capitalize()})", "", "", "", "", "", r_(ant_resultado))],
    [12, 9, 55, 20, 35, 10, 14],
    titulo=f"Lançamentos de {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} por categoria (competência)")

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
