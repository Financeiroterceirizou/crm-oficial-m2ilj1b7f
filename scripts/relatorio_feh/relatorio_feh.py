#!/usr/bin/env python3
# Relatórios Mensais — FRATERNIDADE E HARMONIA (F e H | FILOSÓFICO) — v1.2, 2026-10-14
#   v1.2 (14/10): saldo anterior/final = soma das movimentações DO CC (a conta CORA é
#     compartilhada entre os 2 CCs — saldo de conta não separa os pacotes).
#   v1.1 (feedback Vinícius 14/10): comparativo 12m POR CATEGORIA (matriz + totais por mês);
#     fluxo de caixa com SALDO ANTERIOR (31/08) e SALDO FINAL (30/09).
#   Layout NASPOLINI (logo capa compacta + símbolo no rodapé). Regime de CAIXA (sit in 1,2).
#   Dois pacotes em ARQUIVOS SEPARADOS (pedido Vinícius 14/10): feh | filosofico
#     feh        → CC "F e H" (170068)
#     filosofico → CC "FILOSOFICO" (170069)
#   Relatórios (pedido Vinícius 14/10):
#     1. Comparativo dos últimos 12 meses POR CATEGORIA (caixa; matriz + entradas/saídas/resultado do mês)
#     2. Fluxo de Caixa do mês anterior por categoria (caixa) + saldo anterior e saldo final do CC
#     3. Receitas em aberto até o último dia do mês anterior, POR IRMÃO (agrupa name_contact)
#     4. Resultado dos últimos 12 meses (caixa; totais por mês + linha de total)
#     5. Saldo Tronco de Solidariedade no último dia do mês anterior — TODAS as movimentações
#        (sit qualquer) do CC do pacote com a TAG "TRONCO DE SOLIDARIEDADE <pacote>" do início
#        até o último dia do mês anterior; saldo = soma
# Uso: python3 relatorio_feh.py [YYYY-MM-DD] [feh|filosofico]  (default: hoje, feh)
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image as RLImage, KeepTogether)
from reportlab.lib.utils import ImageReader

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_FEH") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37")
VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-terceirizou.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

# ===== pacote (centro de custo) =====
PACOTES = {
    "feh":        {"nome": "F e H",        "cc_id": 170068, "tag_tronco": "TRONCO DE SOLIDARIEDADE F e H",        "arq": "F_e_H"},
    "filosofico": {"nome": "FILOSÓFICO",   "cc_id": 170069, "tag_tronco": "TRONCO DE SOLIDARIEDADE FILOSÓFICO",   "arq": "Filosofico"},
}
_p = sys.argv[2] if len(sys.argv) > 2 else "feh"
PK = PACOTES[_p]
CC_ID = PK["cc_id"]
TAG_TRONCO = PK["tag_tronco"]

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

def tem_tag(t, ds_tag):
    return any((tg.get("ds_tag") or "").upper() == ds_tag.upper() for tg in (t.get("array_tags") or []))

def no_cc(t):
    """CC do pacote + sem transferências entre contas (categoria 99.01 ou descrição Transferência)."""
    for c in (t.get("apportionments_plan_account") or []):
        if (c.get("ds_category") or "").startswith("99.01"):
            return False
    if (t.get("ds_transaction") or "").upper().startswith("TRANSFERÊNCIA"):
        return False
    ids = {c.get("cost_center_id") for c in (t.get("apportionments_cost_center") or [])}
    return CC_ID in ids

# ===== datas =====
HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_ANT = add_months(HOJE.replace(day=1), -1)          # mês anterior
FIM_MES_ANT = MES_ANT.replace(day=28) + timedelta(days=4)
FIM_MES_ANT = FIM_MES_ANT - timedelta(days=FIM_MES_ANT.day)
HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")

# ===== dados =====
# janela completa: 12 meses do comparativo + tudo para o tronco (licença pequena: 2 anos cabem)
INI_12 = add_months(MES_ANT, -11)
_tx = tx_list(f"{INI_12.year}-01-01", f"{MES_ANT.year + 1}-12-31")
tx_cc = [t for t in _tx if no_cc(t)]

# meses do comparativo (mês anterior -11 → mês anterior)
meses_12 = []
for i in range(0, 12):
    ini_m = add_months(INI_12, i)
    fim_m = add_months(ini_m, 1) - timedelta(days=1)
    meses_12.append((ini_m.isoformat()[:7], f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"))

# 1. Comparativo 12 meses (caixa): POR CATEGORIA (matriz categoria × mês) + totais por mês
comp = {m: [0, 0] for m, _ in meses_12}
matriz_12 = defaultdict(lambda: defaultdict(int))
for t in tx_cc:
    if t.get("situation") not in (1, 2):
        continue
    m = bdate(t)[:7]
    if m in comp:
        v = t["value_in_cent"]
        if v > 0:
            comp[m][0] += v
        else:
            comp[m][1] += v
        matriz_12[cat_nome(t)][m] += v

# 2. Fluxo de Caixa do mês anterior por categoria (caixa)
mes_ant_tx = [t for t in tx_cc if bdate(t)[:7] == f"{MES_ANT.year}-{MES_ANT.month:02d}"
              and t.get("situation") in (1, 2)]
rec = defaultdict(lambda: [0, 0])
desp = defaultdict(lambda: [0, 0])
for t in mes_ant_tx:
    v = t["value_in_cent"]
    g = rec if v > 0 else desp
    g[cat_nome(t)][0] += v
    g[cat_nome(t)][1] += 1
tot_rec = sum(v for v, _ in rec.values())
tot_desp = sum(v for v, _ in desp.values())
resultado = tot_rec + tot_desp

# 3. Receitas em aberto até o último dia do mês anterior, POR IRMÃO (contato)
aberto_tx = [t for t in tx_cc
             if t["value_in_cent"] > 0 and t.get("situation") == 0
             and bdate(t) <= FIM_MES_ANT.isoformat()]
por_irmao = defaultdict(lambda: [0, 0])
for t in aberto_tx:
    nome = (t.get("name_contact") or "(sem contato)").strip()
    por_irmao[nome][0] += t["value_in_cent"]
    por_irmao[nome][1] += 1
total_aberto = sum(v for v, _ in por_irmao.values())

# 4. Resultado dos últimos 12 meses (caixa) = comparativo + linha de total
res_12_total = sum(e + s for e, s in comp.values())

# 5. Saldo Tronco de Solidariedade (todas as situações, do início até fim do mês anterior)
#    movimentações do CC com a TAG do tronco — janela desde o início da licença
_tx_tudo = tx_list("2017-01-01", FIM_MES_ANT.isoformat())
tronco_tx = [t for t in _tx_tudo if no_cc(t) and tem_tag(t, TAG_TRONCO)]
saldo_tronco = sum(t["value_in_cent"] for t in tronco_tx)
ent_tronco = sum(t["value_in_cent"] for t in tronco_tx if t["value_in_cent"] > 0)
sai_tronco = sum(t["value_in_cent"] for t in tronco_tx if t["value_in_cent"] < 0)

# saldo anterior/final DO CENTRO DE CUSTO (v1.2): todas as movimentações do CC (sit 1,2)
# até 31/08 = saldo anterior; + resultado do mês = saldo final em 30/09
MES_ANT2 = add_months(MES_ANT, -1)
FIM_MES_ANT2 = MES_ANT2.replace(day=28) + timedelta(days=4)
FIM_MES_ANT2 = FIM_MES_ANT2 - timedelta(days=FIM_MES_ANT2.day)
saldo_anterior = sum(t["value_in_cent"] for t in _tx_tudo
                     if no_cc(t) and t.get("situation") in (1, 2) and bdate(t) <= FIM_MES_ANT2.isoformat())
saldo_final = saldo_anterior + resultado

# saldos das contas no último dia do mês anterior (contexto)
contas_api = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
saldos_conta = []
for c in contas_api:
    try:
        b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={FIM_MES_ANT.isoformat()}&id_account_main={c['id']}")["results"]
        saldos_conta.append((c["ds_account"], b["balanceDone"]))
    except Exception:
        pass
saldos_conta = [(n, v) for n, v in saldos_conta if v != 0]

print("dados prontos")

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=PRETO, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=LARANJA, spaceBefore=14, spaceAfter=3)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, textColor=PRETO, spaceBefore=10, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#777777"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph

def P_val(cents, style):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl(cents), s)

def P_val_int(cents, style):
    """Sem centavos e sem R$ — matrizes largas (comparativo 12 meses)."""
    v = int(round(cents / 100.0))
    s = f"{abs(v):,}".replace(",", ".")
    s = ("-" if v < 0 else "") + s
    s2 = ParagraphStyle("vi", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(s, s2)

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

def rodape_simbolo(canvas, doc):
    if os.path.exists(SIMBOLO):
        alt = 1.2 * cm
        canvas.drawImage(SIMBOLO, 18.4*cm, 1.1*cm, width=alt*372/553, height=alt, mask="auto")

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Feh_{PK['arq']}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                        topMargin=1.3*cm, bottomMargin=1.6*cm,
                        title=f"Relatório Gerencial — Fraternidade e Harmonia {PK['nome']}")
E = []
h1c = ParagraphStyle("h1c", parent=h1, fontSize=13, alignment=1, spaceAfter=1)
h2c = ParagraphStyle("h2c", parent=h2, fontSize=11, alignment=1, spaceBefore=2, spaceAfter=2)
subc = ParagraphStyle("subc", parent=sub, fontSize=8, alignment=1, spaceAfter=0)
if os.path.exists(LOGO):
    img = RLImage(LOGO, width=5.5*cm, height=5.5*cm*561/1600)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 8))
E.append(P(f"<b>FRATERNIDADE E HARMONIA — {PK['nome']}</b>", h1c))
E.append(P("Relatório Gerencial Mensal", h2c))
E.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · Ref.: {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} — regime de caixa", subc))
E.append(Spacer(1, 6))

# 1. Comparativo dos últimos 12 meses (caixa) — POR CATEGORIA
E.append(P(f"Comparativo dos Últimos 12 Meses por Categoria — {MES_AB[INI_12.month]}/{str(INI_12.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]} (regime de caixa)", h2))
cat_names_12 = sorted({c for c in matriz_12})
cm_rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{lab}</b>", cellr) for _, lab in meses_12] + [P("<b>Total</b>", cellr)]]
for cat in cat_names_12:
    row = [P(cat, cell)]
    for m, lab in meses_12:
        v = matriz_12[cat].get(m, 0)
        row.append(P_val_int(v, cellr) if v else P("—", cellr))
    row.append(P_val_int(sum(matriz_12[cat].values()), cellrb))
    cm_rows.append(row)
# linhas de totais por mês (entradas/saídas/resultado) no rodapé da matriz
tot_e = sum(v[0] for v in comp.values()); tot_s = sum(v[1] for v in comp.values())
row_e = [P("<b>Entradas do mês</b>", cellb)] + [P_val_int(comp[m][0], cellrb) for m, _ in meses_12] + [P_val_int(tot_e, cellrb)]
row_s = [P("<b>Saídas do mês</b>", cellb)] + [P_val_int(comp[m][1], cellrb) for m, _ in meses_12] + [P_val_int(tot_s, cellrb)]
row_r = [P("<b>Resultado do mês</b>", cellb)] + [P_val_int(comp[m][0] + comp[m][1], cellrb) for m, _ in meses_12] + [P_val_int(tot_e + tot_s, cellrb)]
cm_rows += [row_e, row_s, row_r]
t = tabela(cm_rows, [4.2*cm] + [1.25*cm]*12 + [1.9*cm], fs=6)
t.setStyle(TableStyle([("BACKGROUND", (0,len(cm_rows)-3), (-1,len(cm_rows)-1), LARANJA_CLARO)]))
E.append(t)

# 2. Fluxo de Caixa do mês anterior por categoria
E.append(PageBreak())
E.append(P(f"Fluxo de Caixa — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de caixa)", h2))
E.append(P(f"Saldo anterior e saldo final do centro de custo {PK['nome']} (soma das movimentações realizadas).", sub))
fc_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for nome, (v, n) in sorted(rec.items()):
    fc_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
fc_rows.append([P("<b>Total de Entradas</b>", cellrb), P(f"<b>{sum(n for _, n in rec.values())}</b>", cellc), P_val(tot_rec, cellrb)])
for nome, (v, n) in sorted(desp.items()):
    fc_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
fc_rows.append([P("<b>Total de Saídas</b>", cellrb), P(f"<b>{sum(n for _, n in desp.values())}</b>", cellc), P_val(tot_desp, cellrb)])
fc_rows.append([P(f"<b>Saldo anterior em {FIM_MES_ANT2.strftime('%d/%m/%Y')}</b>", cellrb), P("", cell), P_val(saldo_anterior, cellrb)])
fc_rows.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{len(mes_ant_tx)}</b>", cellc), P_val(resultado, cellrb)])
fc_rows.append([P(f"<b>Saldo final em {FIM_MES_ANT_LABEL}</b>", cellrb), P("", cell), P_val(saldo_final, cellrb)])
t = tabela(fc_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(fc_rows)-4), (-1,len(fc_rows)-1), LARANJA_CLARO)]))
E.append(t)

# 3. Receitas em aberto até o último dia do mês anterior, por irmão
E.append(PageBreak())
E.append(P(f"Receitas em Aberto até {FIM_MES_ANT_LABEL} — por Irmão", h2))
ra_rows = [[P("<b>Irmão (contato)</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor em aberto</b>", cellr)]]
for nome, (v, n) in sorted(por_irmao.items(), key=lambda x: -x[1][0]):
    ra_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
ra_rows.append([P("<b>Total em aberto</b>", cellrb), P(f"<b>{len(aberto_tx)}</b>", cellc), P_val(total_aberto, cellrb)])
t = tabela(ra_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(ra_rows)-1), (-1,len(ra_rows)-1), LARANJA_CLARO)]))
E.append(t)
if aberto_tx:
    E.append(Spacer(1, 14))
    E.append(P("<b>Demonstrativo dos lançamentos em aberto</b>", h2))
    por_irmao_tx = defaultdict(list)
    for t in aberto_tx:
        por_irmao_tx[(t.get("name_contact") or "(sem contato)").strip()].append(t)
    for nome in sorted(por_irmao_tx, key=lambda n: -sum(t["value_in_cent"] for t in por_irmao_tx[n])):
        txs_i = sorted(por_irmao_tx[nome], key=bdate)
        rows = [[P("<b>Vencimento</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell), P("<b>Valor</b>", cellr)]]
        for t in txs_i:
            d = bdate(t)
            rows.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell), P((t.get("ds_transaction") or "")[:70], cell),
                         P(t.get("ds_account_main") or "", cell), P_val(t["value_in_cent"], cellr)])
        rows.append([P("<b>Total</b>", cellrb), P(f"<b>{nome}</b>", cellrb), P(f"<b>{len(txs_i)}</b>", cellc), P_val(sum(t["value_in_cent"] for t in txs_i), cellrb)])
        tt = tabela(rows, [2.2*cm, 8.3*cm, 3.5*cm, 3*cm])
        tt.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
        E.append(KeepTogether([P(f"<b>{nome}</b>", h3), tt]))

# 4. Resultado dos últimos 12 meses
E.append(PageBreak())
E.append(P(f"Resultado dos Últimos 12 Meses — {MES_AB[INI_12.month]}/{str(INI_12.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]} (regime de caixa)", h2))
rs_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
for m, lab in meses_12:
    e_m, s_m = comp[m]
    rs_rows.append([P(lab, cell), P_val(e_m, cellr), P_val(s_m, cellr), P_val(e_m + s_m, cellrb)])
rs_rows.append([P("<b>Resultado 12 meses</b>", cellrb), P_val(tot_e, cellrb), P_val(tot_s, cellrb), P_val(res_12_total, cellrb)])
t = tabela(rs_rows, [3*cm, 4.3*cm, 4.3*cm, 4.4*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rs_rows)-1), (-1,len(rs_rows)-1), LARANJA_CLARO)]))
E.append(t)

# 5. Saldo Tronco de Solidariedade
E.append(Spacer(1, 18))
E.append(P(f"Saldo Tronco de Solidariedade {PK['nome']} em {FIM_MES_ANT_LABEL}", h2))
tr_rows = [[P("<b>Item</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)],
           [P("Entradas no tronco (desde o início)", cell), P(f"<b>{sum(1 for t in tronco_tx if t['value_in_cent'] > 0)}</b>", cellc), P_val(ent_tronco, cellr)],
           [P("Saídas do tronco (desde o início)", cell), P(f"<b>{sum(1 for t in tronco_tx if t['value_in_cent'] < 0)}</b>", cellc), P_val(sai_tronco, cellr)],
           [P(f"<b>Saldo Tronco de Solidariedade em {FIM_MES_ANT_LABEL}</b>", cellrb), P(f"<b>{len(tronco_tx)}</b>", cellc), P_val(saldo_tronco, cellrb)]]
t = tabela(tr_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(tr_rows)-1), (-1,len(tr_rows)-1), LARANJA_CLARO)]))
E.append(t)
E.append(Spacer(1, 8))
E.append(P(f"Movimentações do Centro de Custo {PK['nome']} com a tag {TAG_TRONCO}, do início da licença até {FIM_MES_ANT_LABEL} (todas as situações).", sub))

# contexto: saldos nas contas
E.append(Spacer(1, 14))
E.append(P(f"Saldo nas contas em {FIM_MES_ANT_LABEL}", h2))
sc_rows = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {FIM_MES_ANT_LABEL}</b>", cellr)]]
for nome, v in saldos_conta:
    sc_rows.append([P(nome, cell), P_val(v, cellr)])
sc_rows.append([P("<b>Total</b>", cellrb), P_val(sum(v for _, v in saldos_conta), cellrb)])
t = tabela(sc_rows, [11*cm, 5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(sc_rows)-1), (-1,len(sc_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([t]))

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc.build(E, onFirstPage=rodape_simbolo, onLaterPages=rodape_simbolo)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Feh_{PK['arq']}.xlsx"
wb = Workbook()
wb.remove(wb.active)
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"
VERMELHO_XL = "C0392B"
TOT_LABELS = ("Total", "Resultado", "Saldo")

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

# 1. comparativo 12m por categoria
_cmp_rows = [("Categoria",) + tuple(lab for _, lab in meses_12) + ("Total",)]
for cat in cat_names_12:
    _cmp_rows.append((cat,) + tuple((r_(matriz_12[cat].get(m, 0)) if matriz_12[cat].get(m, 0) else None) for m, _ in meses_12)
                     + (r_(sum(matriz_12[cat].values())),))
_cmp_rows.append(("Entradas do mês",) + tuple(r_(comp[m][0]) for m, _ in meses_12) + (r_(tot_e),))
_cmp_rows.append(("Saídas do mês",) + tuple(r_(comp[m][1]) for m, _ in meses_12) + (r_(tot_s),))
_cmp_rows.append(("Resultado do mês",) + tuple(r_(comp[m][0] + comp[m][1]) for m, _ in meses_12) + (r_(tot_e + tot_s),))
aba("Comparativo 12 meses", _cmp_rows, [40] + [12]*12 + [14],
    titulo=f"Comparativo dos Últimos 12 Meses por Categoria ({MES_AB[INI_12.month]}/{str(INI_12.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) — regime de caixa")

# 2. fluxo de caixa mês anterior
aba("Fluxo " + MES_AB[MES_ANT.month],
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(rec.items())] +
    [("Total de Entradas", sum(n for _, n in rec.values()), r_(tot_rec))] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(desp.items())] +
    [("Total de Saídas", sum(n for _, n in desp.values()), r_(tot_desp)),
     (f"Saldo anterior em {FIM_MES_ANT2.strftime('%d/%m/%Y')}", "", r_(saldo_anterior)),
     ("Resultado do mês", len(mes_ant_tx), r_(resultado)),
     (f"Saldo final em {FIM_MES_ANT_LABEL}", "", r_(saldo_final))],
    [45, 14, 16],
    titulo=f"Fluxo de Caixa — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de caixa)")

# 3. receitas em aberto por irmão
aba("Em aberto por irmão",
    [("Irmão (contato)", "Lançamentos", "Valor em aberto")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(por_irmao.items(), key=lambda x: -x[1][0])] +
    [("Total em aberto", len(aberto_tx), r_(total_aberto))],
    [40, 14, 18],
    titulo=f"Receitas em Aberto até {FIM_MES_ANT_LABEL} — por Irmão")

# 4. resultado 12m (mesma matriz do comparativo, com linha final de resultado)
aba("Resultado 12 meses",
    [("Mês", "Entradas", "Saídas", "Resultado")] +
    [(lab, r_(comp[m][0]), r_(comp[m][1]), r_(comp[m][0] + comp[m][1])) for m, lab in meses_12] +
    [("Resultado 12 meses", r_(tot_e), r_(tot_s), r_(res_12_total))],
    [14, 18, 18, 18],
    titulo=f"Resultado dos Últimos 12 Meses — regime de caixa")

# 5. tronco de solidariedade
aba("Tronco Solidariedade",
    [("Item", "Lançamentos", "Valor"),
     ("Entradas no tronco (desde o início)", sum(1 for t in tronco_tx if t["value_in_cent"] > 0), r_(ent_tronco)),
     ("Saídas do tronco (desde o início)", sum(1 for t in tronco_tx if t["value_in_cent"] < 0), r_(sai_tronco)),
     (f"Saldo Tronco de Solidariedade em {FIM_MES_ANT_LABEL}", len(tronco_tx), r_(saldo_tronco))],
    [45, 14, 18],
    titulo=f"Saldo Tronco de Solidariedade {PK['nome']} em {FIM_MES_ANT_LABEL} (tag {TAG_TRONCO}, CC {PK['nome']})")

# saldos nas contas
aba("Saldo contas",
    [("Conta", f"Saldo em {FIM_MES_ANT_LABEL}")] +
    [(n, r_(v)) for n, v in saldos_conta] + [("Total", r_(sum(v for _, v in saldos_conta)))],
    [30, 18], titulo=f"Saldo nas contas em {FIM_MES_ANT_LABEL}")

# detalhe dos lançamentos do tronco
det_rows = [("Data", "Descrição", "Conta", "Situação", "Valor")]
for t in sorted(tronco_tx, key=bdate):
    d = bdate(t)
    det_rows.append((d, (t.get("ds_transaction") or "")[:80], t.get("ds_account_main") or "",
                     "Pago" if t.get("situation") in (1, 2) else "Aberto", r_(t["value_in_cent"])))
det_rows.append(("Total", "", "", "", r_(saldo_tronco)))
aba("Detalhe Tronco", det_rows, [12, 58, 24, 10, 16],
    titulo=f"Movimentações do Tronco de Solidariedade {PK['nome']} até {FIM_MES_ANT_LABEL}")

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
