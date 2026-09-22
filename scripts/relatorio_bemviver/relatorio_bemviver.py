#!/usr/bin/env python3
# Relatórios Semanais — BEM VIVER (ILPI) — v1.4, 2026-09-21
# Uso: python3 relatorio_bemviver.py [YYYY-MM-DD]  (default: hoje)
# Gera UM PDF + UM Excel com os 11 relatórios no padrão dos exemplos de 14/09
#   + Comparativo 13 meses em PDF PRÓPRIO PAISAGEM.
# Fonte: API Controlle v1 (token Bem Viver). Envio: segunda-feira 14:00 → financeirodabemviver@gmail.com
#
# v1.4 (feedback Vinícius 21/09 23:25 — ÚLTIMO AJUSTE):
#   - Comparativo PDF: série "Resultado do mês" (entradas+saídas) no lugar de Saldo realizado
#   - Inadimplência: dois somatórios — TOTAL e EXCLUINDO Negociação Judicial (01.97) e
#     Possível Perda de Receita (01.99)
#   - Layout: KeepTogether — relatório completo numa página (título + tabela juntos;
#     demonstrativos quebram por bloco de categoria, nunca no meio de um bloco)
#   - Excel: abas separadas "Detalhe Previsão mês corrente" e "Detalhe Previsão mês seguinte"
#
# v1.3 (feedback 21/09 22:35 e 23:04): Média no comparativo (PDF+Excel); Consolidado com
#   Total de Receitas/Despesas/Resultado; Despesas em aberto com demonstrativo; Saldo colorido;
#   Fluxo 12m sem gráfico; Excel com cores/negrito/centralizado; detalhes agrupados por categoria.
# v1.2 (feedback 21/09): comparativo inteiro sem R$ + verde/vermelho; ordem por categoria;
#   inadimplência com todos os lançamentos; títulos únicos.
# v1.1 (feedback 21/09): filtro centro de custo BEM VIVER + transferências fora; comparativo paisagem.
# v1.0 (2026-09-21): pacote original com 11 relatórios.
import json, os, sys, urllib.request
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)

BASE = "https://api-v1.controlle.com"
_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".controlle_token_bemviver")
TOKEN = os.environ.get("CONTROLLE_TOKEN_BEMVIVER") or (open(_token).read().strip() if os.path.exists(_token) else "")
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
TAG_BOLETO = 130213  # "Boleto Emitido"

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
    """Sem centavos e sem R$ — matrizes largas (comparativo 13 meses)."""
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

def tem_tag(t, id_tag):
    return any((tg.get("id_tag") == id_tag) for tg in (t.get("array_tags") or []))

def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "?") if cats else "(sem categoria)"

CC_BEM_VIVER = 169959  # centro de custo BEM VIVER — filtro obrigatório em todos os relatórios

def ok_bv(t):
    """Filtro padrão Bem Viver: rateio no centro de custo BEM VIVER e sem transferências entre contas."""
    if not any(c.get("cost_center_id") == CC_BEM_VIVER for c in (t.get("apportionments_cost_center") or [])):
        return False
    for c in (t.get("apportionments_plan_account") or []):
        if (c.get("ds_category") or "").startswith("99.01"):  # Transferência entre Contas
            return False
    if (t.get("ds_transaction") or "").startswith("Transferência de"):
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

# ===== datas =====
HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
DIA_ANT = HOJE - timedelta(days=1)
MES_REF = HOJE.replace(day=1)              # mês corrente
MES_SEG = add_months(MES_REF, 1)           # mês seguinte
FIM_MES_ANT = MES_REF - timedelta(days=1)  # último dia do mês anterior
INI_SEM, FIM_SEM = HOJE, HOJE + timedelta(days=6 - HOJE.weekday())  # seg→dom
if INI_SEM.weekday() != 0:  # garante segunda→domingo
    INI_SEM = HOJE - timedelta(days=HOJE.weekday())
    FIM_SEM = INI_SEM + timedelta(days=6)

def label_mes(d):
    return f"{MES_PT[d.month].capitalize()} de {d.year}"
def label_curto(d):
    return f"{MES_AB[d.month]}/{str(d.year)[2:]}"

HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")
SEM_LABEL = f"{INI_SEM.strftime('%d/%m/%Y')} até {FIM_SEM.strftime('%d/%m/%Y')}"

# ===== dados =====
# Filtro padrão em TODOS os relatórios: centro de custo BEM VIVER, sem transferências entre contas.
# saldos por conta no dia anterior
contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
saldos_conta = []
for c in contas:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={DIA_ANT.isoformat()}&id_account_main={c['id']}")["results"]
    saldos_conta.append((c["ds_account"], b["balanceDone"]))
saldos_conta = [(n, v) for n, v in saldos_conta if v != 0]

# comparativo 13 meses (realizado): série + matriz por categoria
INI_13 = add_months(MES_REF, -12)
meses_13 = []
for i in range(0, 13):
    ini_m = add_months(INI_13, i)
    fim_m = add_months(ini_m, 1) - timedelta(days=1)
    meses_13.append((ini_m.isoformat(), fim_m.isoformat(), label_curto(ini_m)))
serie_13 = []
for ini_m, fim_m, lab in meses_13:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini_m}&end_date={fim_m}")["results"]
    serie_13.append((lab, b["revenuesDone"], b["expensesDone"], b["balanceDone"]))
matriz_13 = defaultdict(lambda: defaultdict(int))
for t in tx_list(meses_13[0][0], min(meses_13[-1][1], DIA_ANT.isoformat()), **{"situation": "[1]"}):
    if not ok_bv(t):
        continue
    mes = bdate(t)[:7]
    for c in (t.get("apportionments_plan_account") or []):
        matriz_13[c.get("ds_category") or "?"][mes] += c.get("value") or 0

# consolidado do mês (pago até agora)
setembro_pago = [t for t in tx_list(MES_REF.isoformat(), (add_months(MES_REF,1)-timedelta(days=1)).isoformat(), **{"situation": "[1]"}) if ok_bv(t)]
cons_rec = agrupa_por_categoria(setembro_pago, so_positivas=True)
cons_desp = agrupa_por_categoria(setembro_pago, so_negativas=True)
cons_entradas = sum(v for v, _ in cons_rec.values())
cons_saidas = sum(v for v, _ in cons_desp.values())
cons_resultado = cons_entradas + cons_saidas

# despesas em aberto até fim do mês anterior
desp_aberto = [t for t in tx_list(f"{FIM_MES_ANT.year}-01-01", FIM_MES_ANT.isoformat(), **{"activity_type": "0", "situation": "[0]"})
               if bdate(t) <= FIM_MES_ANT.isoformat() and ok_bv(t)]
g_desp_aberto = agrupa_por_categoria(desp_aberto)
total_desp_aberto = sum(v for v, _ in g_desp_aberto.values())

# inadimplência até fim do mês anterior
inad = [t for t in tx_list(f"{FIM_MES_ANT.year}-01-01", FIM_MES_ANT.isoformat(), **{"activity_type": "1", "situation": "[0]"})
        if bdate(t) <= FIM_MES_ANT.isoformat() and ok_bv(t)]
g_inad = agrupa_por_categoria(inad)
total_inad = sum(v for v, _ in g_inad.values())
inad_boleto = [t for t in inad if tem_tag(t, TAG_BOLETO)]
g_inad_boleto = agrupa_por_categoria(inad_boleto)
total_inad_boleto = sum(v for v, _ in g_inad_boleto.values())

# previsão mês corrente (pago + pendente) e mês seguinte
prev_mes = [t for t in tx_list(MES_REF.isoformat(), (add_months(MES_REF,1)-timedelta(days=1)).isoformat()) if ok_bv(t)]
g_prev_rec = agrupa_por_categoria(prev_mes, so_positivas=True)
g_prev_desp = agrupa_por_categoria(prev_mes, so_negativas=True)
prev_entradas, prev_saidas = sum(v for v,_ in g_prev_rec.values()), sum(v for v,_ in g_prev_desp.values())
prev_resultado = prev_entradas + prev_saidas

prev_seg = [t for t in tx_list(MES_SEG.isoformat(), (add_months(MES_SEG,1)-timedelta(days=1)).isoformat()) if ok_bv(t)]
g_seg_rec = agrupa_por_categoria(prev_seg, so_positivas=True)
g_seg_desp = agrupa_por_categoria(prev_seg, so_negativas=True)
seg_entradas, seg_saidas = sum(v for v,_ in g_seg_rec.values()), sum(v for v,_ in g_seg_desp.values())
seg_resultado = seg_entradas + seg_saidas

# previsão de receitas da semana (não pagas) — geral e apenas boleto
sem_rec = [t for t in tx_list(INI_SEM.isoformat(), FIM_SEM.isoformat(), **{"activity_type": "1", "situation": "[0]"})
           if INI_SEM.isoformat() <= bdate(t) <= FIM_SEM.isoformat() and ok_bv(t)]
g_sem = agrupa_por_categoria(sem_rec)
total_sem = sum(v for v, _ in g_sem.values())
sem_boleto = [t for t in sem_rec if tem_tag(t, TAG_BOLETO)]
g_sem_boleto = agrupa_por_categoria(sem_boleto)
total_sem_boleto = sum(v for v, _ in g_sem_boleto.values())

# projeção próximos 12 meses (mês corrente → +11)
proj = []
for i in range(0, 12):
    ini_m = add_months(MES_REF, i)
    fim_m = add_months(ini_m, 1) - timedelta(days=1)
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini_m.isoformat()}&end_date={fim_m.isoformat()}")["results"]
    proj.append((label_curto(ini_m), b["revenuesPreview"], b["expensesPreview"], b["balancePreview"]))

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
    """Valor colorido: verde se positivo (receita), vermelho se negativo (despesa)."""
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl(cents), s)

def P_val_int(cents, style):
    """Valor colorido sem centavos e sem R$ — matrizes largas (comparativo 13 meses)."""
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl_int(cents), s)

# NOTE: o comparativo 13 meses é gerado em PDF próprio paisagem (definido após o PDF principal).

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

def tabela_cat(titulo, grupos, positivo=True, total_label="Total"):
    rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nome, (v, n) in sorted(grupos.items(), key=lambda x: x[0]):
        rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tot = sum(v for v, _ in grupos.values())
    rows.append([P(f"<b>{total_label}</b>", cellrb), P(f"<b>{sum(n for _, n in grupos.values())}</b>", cellc), P_val(tot, cellrb)])
    t = tabela(rows, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
    # título + tabela juntos: o relatório completo não quebra no meio
    return [KeepTogether([P(f"<b>{titulo}</b>", h2), t])]

def tabela_lancamentos(txs, titulo=None, total_label="Total"):
    """Demonstrativo dos lançamentos (um bloco por categoria, com total por categoria)."""
    E = []
    primeiro = True
    por_cat = defaultdict(list)
    for t in txs:
        por_cat[cat_nome(t)].append(t)
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
        if primeiro and titulo:
            E.append(KeepTogether([P(f"<b>{titulo}</b>", h2), P(f"<b>{cat}</b>", h3), tt]))
            primeiro = False
        else:
            E.append(KeepTogether([P(f"<b>{cat}</b>", h3), tt]))
    return E

P = Paragraph
ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorios_Bem_Viver.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.3*cm, bottomMargin=1.3*cm)
E = []

E.append(P("<b>BEM VIVER — Relatórios Gerenciais Semanais</b>", h1))
E.append(P(f"Gerado em {HOJE_LABEL} (segunda-feira) · Fonte: Controlle · Semana de {SEM_LABEL}", sub))

# 1. Comparativo 13 meses — PDF PRÓPRIO EM PAISAGEM
ARQ_COMP = f"artifacts/{HOJE.strftime('%y%m%d')}_Comparativo_Bem_Viver.pdf"
doc_comp = SimpleDocTemplate(ARQ_COMP, pagesize=landscape(A4), leftMargin=1.2*cm, rightMargin=1.2*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
C = []
C.append(P("<b>BEM VIVER — Comparativo dos últimos 13 meses</b>", h1))
C.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · {label_curto(INI_13)} a {label_curto(MES_REF)} · Apenas pago/recebido · Valores em R$ inteiros", sub))
cm_rows = [[P("<b>Série</b>", cell)] + [P(f"<b>{lab}</b>", cellr) for _, _, lab in meses_13] + [P("<b>Média</b>", cellr), P("<b>Total</b>", cellr)]]
for idx, nome_serie in [(1, "Entrada realizada"), (2, "Saída realizada"), (3, "Resultado do mês")]:
    row = [P(nome_serie, cell)]
    vals = [[e_m, s_m, e_m + s_m][idx-1] for _, e_m, s_m, _ in serie_13]
    for val in vals:
        row.append(P_val_int(val, cellr))
    row.append(P_val_int(round(sum(vals) / len(vals)), cellrb))
    row.append(P_val_int(sum(vals), cellrb))
    cm_rows.append(row)
C.append(tabela(cm_rows, [3.1*cm] + [1.66*cm]*13 + [1.9*cm, 2.2*cm], fs=7))
C.append(Spacer(1, 10))
C.append(P("Detalhamento por categoria (rateio da API; valores realizados; R$ inteiros):", body))
cat_names_13 = sorted({c for c in matriz_13})
mt_rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{lab}</b>", cellr) for _, _, lab in meses_13] + [P("<b>Média</b>", cellr)]]
for cat in cat_names_13:
    row = [P(cat, cell)]
    vals = []
    for _, fim_m_iso, lab in [(a, b, l) for a, b, l in meses_13]:
        v = matriz_13[cat].get(fim_m_iso[:7], 0)
        vals.append(v)
        row.append(P_val_int(v, cellr) if v else P("—", cellr))
    row.append(P_val_int(round(sum(vals) / len(vals)), cellrb))
    mt_rows.append(row)
C.append(tabela(mt_rows, [3.1*cm] + [1.66*cm]*13 + [1.9*cm], fs=6))
C.append(Spacer(1, 10))
C.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc_comp.build(C)
print(f"OK: {ARQ_COMP}")

# 2. Consolidado do mês
cd_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for nome, (v, n) in sorted(cons_rec.items()):
    cd_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
cd_rows.append([P("<b>Total de Receitas</b>", cellrb), P(f"<b>{sum(n for _, n in cons_rec.values())}</b>", cellc), P_val(cons_entradas, cellrb)])
for nome, (v, n) in sorted(cons_desp.items()):
    cd_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
cd_rows.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n for _, n in cons_desp.values())}</b>", cellc), P_val(cons_saidas, cellrb)])
cd_rows.append([P("<b>Resultado consolidado</b>", cellrb), P(f"<b>{len(setembro_pago)}</b>", cellc), P_val(cons_resultado, cellrb)])
t = tabela(cd_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(cd_rows)-3), (-1,len(cd_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([P(f"Consolidado do mês — {label_mes(MES_REF)} (pago/recebido até {HOJE_LABEL})", h2),
                       P(f"{len(setembro_pago)} lançamentos pagos/recebidos no mês.", sub), t]))

# 3. Despesas em aberto — resumo por categoria + demonstrativo dos lançamentos
E += tabela_cat(f"Despesas em aberto até {FIM_MES_ANT_LABEL}", g_desp_aberto, total_label="Total em aberto")
E += tabela_lancamentos(desp_aberto, titulo="Demonstrativo dos lançamentos")

# 4. Inadimplência — resumo + demonstrativo + somatórios (total e excluindo Negociação Judicial / Possível Perda de Receita)
E.append(P(f"Inadimplência até {FIM_MES_ANT_LABEL}", h2))
E += tabela_cat("Resumo por categoria", g_inad, total_label="Total em aberto")
excluir = [v for nome, (v, _) in g_inad.items() if nome.startswith(("01.97", "01.99")) or "Judicial" in nome or "Perda" in nome]
rows = [[P("<b>Composição do total</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)],
        [P("Somatório total (todas as categorias)", cell), P(f"<b>{len(inad)}</b>", cellc), P_val(total_inad, cellr)],
        [P("Somatório excluindo Negociação Judicial e Possível Perda de Receita", cell), P(f"<b>{len(inad) - sum(n for nome, (_, n) in g_inad.items() if nome.startswith(('01.97', '01.99')) or 'Judicial' in nome or 'Perda' in nome)}</b>", cellc), P_val(total_inad - sum(excluir), cellrb)]]
tj = tabela(rows, [11*cm, 2.5*cm, 3*cm])
tj.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
E.append(tj)
E += tabela_lancamentos(inad, titulo="Demonstrativo dos lançamentos")

# 5. Inadimplência apenas boleto — resumo + demonstrativo
E += tabela_cat(f"Inadimplência até {FIM_MES_ANT_LABEL} (Apenas Boleto) — Resumo por categoria (TAG Boleto Emitido)", g_inad_boleto, total_label="Total em aberto (boleto)")
E += tabela_lancamentos(inad_boleto, titulo="Demonstrativo dos lançamentos")

# 6. Previsão do mês corrente
pv_rows = [[P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr)]]
for nome, (v, n) in sorted(g_prev_rec.items()):
    pv_rows.append([P(nome, cell), P_val(v, cellr), P("—", cellr)])
for nome, (v, n) in sorted(g_prev_desp.items()):
    pv_rows.append([P(nome, cell), P("—", cellr), P_val(v, cellr)])
pv_rows.append([P("<b>Totais</b>", cellrb), P_val(prev_entradas, cellrb), P_val(prev_saidas, cellrb)])
pv_rows.append([P("<b>Resultado previsto do mês</b>", cellrb), P(""), P_val(prev_resultado, cellrb)])
t = tabela(pv_rows, [9*cm, 3.75*cm, 3.75*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(pv_rows)-2), (-1,len(pv_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([P(f"Previsão do mês corrente — {label_mes(MES_REF)} (pago + pendente)", h2), t]))

# 7. Previsão do mês seguinte
ps_rows = [[P("<b>Categoria</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr)]]
for nome, (v, n) in sorted(g_seg_rec.items()):
    ps_rows.append([P(nome, cell), P_val(v, cellr), P("—", cellr)])
for nome, (v, n) in sorted(g_seg_desp.items()):
    ps_rows.append([P(nome, cell), P("—", cellr), P_val(v, cellr)])
ps_rows.append([P("<b>Totais</b>", cellrb), P_val(seg_entradas, cellrb), P_val(seg_saidas, cellrb)])
ps_rows.append([P("<b>Resultado previsto do mês</b>", cellrb), P(""), P_val(seg_resultado, cellrb)])
t = tabela(ps_rows, [9*cm, 3.75*cm, 3.75*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(ps_rows)-2), (-1,len(ps_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([P(f"Previsão do mês seguinte — {label_mes(MES_SEG)} (não pagos e não recebidos)", h2), t]))
E.append(PageBreak())

# 8. Previsão de receitas da semana
E += tabela_cat(f"Previsão de Receitas da semana corrente ({SEM_LABEL})", g_sem, total_label="Total previsto")

# 9. Previsão de receitas da semana (apenas boleto)
E += tabela_cat(f"Previsão de Receitas da semana corrente ({SEM_LABEL}) — Apenas Boleto (TAG Boleto Emitido)", g_sem_boleto, total_label="Total previsto (boleto)")

# 10. Saldo nas contas dia anterior
sc_rows = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {DIA_ANT.strftime('%d/%m/%Y')}</b>", cellr)]]
for nome, v in saldos_conta:
    sc_rows.append([P(nome, cell), P_val(v, cellr)])
sc_rows.append([P("<b>Total</b>", cellrb), P_val(sum(v for _, v in saldos_conta), cellrb)])
t = tabela(sc_rows, [11*cm, 5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(sc_rows)-1), (-1,len(sc_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([P(f"Saldo nas contas em {DIA_ANT.strftime('%d/%m/%Y')}", h2), t]))

# 11. Previsão de fluxo de caixa 12 meses
cellrb_big = ParagraphStyle("cellrb_big", parent=cellrb, fontSize=8.5)
pj_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas previstas</b>", cellr), P("<b>Saídas previstas</b>", cellr), P("<b>Saldo projetado</b>", cellr)]]
for lab, e_p, s_p, saldo in proj:
    pj_rows.append([P(lab, cell), P_val(e_p, cellr), P_val(s_p, cellr), P_val(saldo, cellrb_big)])
E.append(KeepTogether([P("Previsão de Fluxo de Caixa — próximos 12 meses", h2), tabela(pj_rows, [3*cm, 4.6*cm, 4.6*cm, 4.6*cm])]))

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorios_Bem_Viver.xlsx"
wb = Workbook()
wb.remove(wb.active)
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"    # receitas / positivos
VERMELHO_XL = "C0392B" # despesas / negativos
TOT_LABELS = ("Total", "Totais", "Resultado", "Saldo final", "Resultado consolidado",
              "Resultado previsto do mês", "Total em aberto", "Total previsto", "Total previsto (boleto)", "Total em aberto (boleto)",
              "Total de Receitas", "Total de Despesas")

def aba(nome, linhas, larguras, pct_from=None):
    ws = wb.create_sheet(nome[:31])
    for r in linhas:
        ws.append(list(r))
    headers = [str(c.value or "") for c in ws[1]]
    # cabeçalho (título): negrito, branco, centralizado
    for c in ws[1]:
        c.fill = FILL_H
        c.font = FH
        c.alignment = Alignment(horizontal="center", vertical="center")
    for row in ws.iter_rows(min_row=2):
        label = str(row[0].value or "")
        is_total = label.startswith(TOT_LABELS)
        if is_total:  # linhas de resultado: negrito e centralizado
            for c in row:
                c.fill = FILL_T
                c.alignment = Alignment(horizontal="center", vertical="center")
            row[0].font = FB
        for j, c in enumerate(row[1:], 2):
            if isinstance(c.value, (int, float)):
                hdr = headers[j-1] if j-1 < len(headers) else ""
                if "Lançamentos" in hdr:  # contagem: sem vírgula e sem R$
                    c.number_format = "0"
                    c.font = Font(bold=is_total)
                elif pct_from and j >= pct_from:
                    c.number_format = "0.0%"
                else:
                    c.number_format = '"R$" #,##0.00'
                    cor = VERDE_XL if c.value > 0 else (VERMELHO_XL if c.value < 0 else "1A1A1A")
                    c.font = Font(bold=is_total or hdr in ("Média", "Total", "Totais"), color=cor)
    for j, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = "A2"

r_ = lambda v: v / 100

def detalhe_agrupado(txs):
    """Lançamentos agrupados por categoria, com total por categoria."""
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

aba("Comparativo 13 meses",
    [("Série",) + tuple(lab for _, _, lab in meses_13) + ("Média", "Total"),
     ("Entrada realizada",) + tuple(r_(e) for _, e, _, _ in serie_13)
        + (r_(round(sum(e for _, e, _, _ in serie_13) / 13)), r_(sum(e for _, e, _, _ in serie_13))),
     ("Saída realizada",) + tuple(r_(s) for _, _, s, _ in serie_13)
        + (r_(round(sum(s for _, _, s, _ in serie_13) / 13)), r_(sum(s for _, _, s, _ in serie_13))),
     ("Resultado do mês",) + tuple(r_(e + s) for _, e, s, _ in serie_13)
        + (r_(round(sum(e + s for _, e, s, _ in serie_13) / 13)), r_(sum(e + s for _, e, s, _ in serie_13)))],
    [20] + [11] * 13 + [11, 13])

aba("Consolidado do mês",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(cons_rec.items())] +
    [("Total de Receitas", sum(n for _, n in cons_rec.values()), r_(cons_entradas))] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(cons_desp.items())] +
    [("Total de Despesas", sum(n for _, n in cons_desp.values()), r_(cons_saidas)),
     ("Resultado consolidado", len(setembro_pago), r_(cons_resultado))],
    [45, 14, 16])

aba("Despesas em aberto",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_desp_aberto.items())] +
    [("Total em aberto", len(desp_aberto), r_(total_desp_aberto))],
    [45, 14, 16])

aba("Inadimplência",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_inad.items())] +
    [("Total em aberto", len(inad), r_(total_inad))],
    [45, 14, 16])

aba("Inadimplência Boleto",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_inad_boleto.items())] +
    [("Total em aberto (boleto)", len(inad_boleto), r_(total_inad_boleto))],
    [45, 14, 16])

aba("Previsão mês corrente",
    [("Categoria", "Entradas", "Saídas")] +
    [(n, r_(v), None) for n, (v, n2) in sorted(g_prev_rec.items())] +
    [(n, None, r_(v)) for n, (v, n2) in sorted(g_prev_desp.items())] +
    [("Totais", r_(prev_entradas), r_(prev_saidas)),
     ("Resultado previsto do mês", None, r_(prev_resultado))],
    [45, 16, 16])

aba("Previsão mês seguinte",
    [("Categoria", "Entradas", "Saídas")] +
    [(n, r_(v), None) for n, (v, n2) in sorted(g_seg_rec.items())] +
    [(n, None, r_(v)) for n, (v, n2) in sorted(g_seg_desp.items())] +
    [("Totais", r_(seg_entradas), r_(seg_saidas)),
     ("Resultado previsto do mês", None, r_(seg_resultado))],
    [45, 16, 16])

aba("Receitas semana",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_sem.items())] +
    [("Total previsto", len(sem_rec), r_(total_sem))],
    [45, 14, 16])

aba("Receitas semana Boleto",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(g_sem_boleto.items())] +
    [("Total previsto (boleto)", len(sem_boleto), r_(total_sem_boleto))],
    [45, 14, 16])

aba("Saldo contas",
    [("Conta", f"Saldo em {DIA_ANT.strftime('%d/%m/%Y')}")] +
    [(n, r_(v)) for n, v in saldos_conta] +
    [("Total", r_(sum(v for _, v in saldos_conta)))],
    [30, 18])

aba("Projeção 12 meses",
    [("Mês", "Entradas previstas", "Saídas previstas", "Saldo projetado")] +
    [(lab, r_(e), r_(s), r_(x)) for lab, e, s, x in proj],
    [12, 18, 18, 18])

aba("Detalhe consolidado do mês", detalhe_agrupado(setembro_pago), [12, 9, 55, 20, 35, 10, 14])
aba("Detalhe Previsão mês corrente", detalhe_agrupado(prev_mes), [12, 9, 55, 20, 35, 10, 14])
aba("Detalhe Previsão mês seguinte", detalhe_agrupado(prev_seg), [12, 9, 55, 20, 35, 10, 14])

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
