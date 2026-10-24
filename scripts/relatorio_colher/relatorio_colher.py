#!/usr/bin/env python3
# RELATÓRIO GERENCIAL — COLHER SOLUÇÕES EM PUBLICIDADE E TI — v1.0, 2026-10-24 (pedido Vinícius)
#   Replicado do modelo ALLT (mesmo layout): 6 seções + 2 logos na capa + cron dia 05 09:00.
#   6 relatórios em 1 PDF (A4, impressão) + Excel: comparativo 13m, receitas/despesas do mês
#   anterior (DRE por subcategoria), fluxo de caixa do mês anterior, previsão rec/desp do mês
#   atual, previsão de fluxo do mês atual, resultado 12m. Regime de caixa. Logo Allt + Terceirizou.
# Uso: python3 relatorio_allt.py [YYYY-MM-DD] (default: hoje; mês anterior = ref)
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image as RLImage, KeepTogether)

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_COLHER") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c"); LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a"); CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-colher.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}

def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items(): r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (409, 500, 502, 503) and i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, OSError):
            if i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise

def tx_list(start, end, min_esperado=0):
    for tentativa in range(3):
        out, page, vazia = [], 1, False
        while not vazia:
            tl = req(f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
                     f"&page={page}&orderBy=date&orderByCardinality=ASC").get("results", {}).get("transactionsList", [])
            out.extend(tl)
            if not tl: vazia = True
            page += 1
            if page > 200: break
        if len(out) >= min_esperado:
            return out
        time.sleep(5 * (tentativa + 1))
    return out

def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s

def bdate(t): return (t.get("dt_billing") or t.get("dt_due") or "")[:10]
def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "(sem categoria)") if cats else "(sem categoria)"
def cat_id(t):
    cats = t.get("apportionments_plan_account") or []
    return cats[0].get("id_category") if cats else None
def valor_efetivo(t):
    """Valor real: payment_in_cent quando pago (sit 1,2), value_in_cent quando pendente.
    O balances (done) usa o valor PAGO — assim a DRE bate com o fluxo e o saldo."""
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]


def eh_99(t):
    return any((c.get("ds_category") or "").startswith("99.") or (c.get("ds_category") or "").lower().startswith("transferencia")
               for c in (t.get("apportionments_plan_account") or []))

HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_REF = date(HOJE.year, HOJE.month, 1) - timedelta(days=1)  # mês anterior
FIM_MES = (MES_REF.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
MES_ATUAL = HOJE.replace(day=1)
FIM_ATUAL = (MES_ATUAL.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
DIA_ANT = HOJE - timedelta(days=1)

# ===== plano (ordem) =====
_plano = [p for p in req(f"{BASE}/plan-account/v1/planAccountsEntities").get("results", []) if p.get("status") == 1]
by_parent = defaultdict(list)
for p in _plano:
    if p.get("id_plan_accounts_parent"):
        by_parent[p["id_plan_accounts_parent"]].append(p)
pais_ordem = [p for p in _plano if not p.get("id_plan_accounts_parent")]
def _cod(nome):
    import re
    m = re.match(r"(\d+)", nome or "")
    return int(m.group(1)) if m else 999

# ===== dados =====
tx_13m = tx_list((MES_REF.replace(day=1) - timedelta(days=365)).isoformat(), FIM_MES.isoformat())
pagos_13m = [t for t in tx_13m if t.get("situation") in (1, 2) and not eh_99(t)]
mes_tx = [t for t in pagos_13m if MES_REF.replace(day=1).isoformat() <= bdate(t) <= FIM_MES.isoformat()]
# previsão completa do mês atual = TODOS os lançamentos do mês (pagos/recebidos sit 1,2 +
# pendentes sit 0, inclusive vencidos a pagar/receber) — pedido Vinícius 24/10 11:41
prev_completa = [t for t in tx_list(MES_ATUAL.isoformat(), FIM_ATUAL.isoformat())
                 if t.get("situation") in (0, 1, 2) and not eh_99(t)]
prev_atual = [t for t in prev_completa if t.get("situation") == 0]
prev_pago_atual = [t for t in prev_completa if t.get("situation") in (1, 2)]

# comparativo 13 meses
INI_13 = MES_REF.replace(day=1) - timedelta(days=365)
meses_13 = []
for i in range(0, 13):
    ini_m = INI_13 + timedelta(days=32 * i)
    ini_m = date(ini_m.year, ini_m.month, 1)
    if ini_m > MES_REF.replace(day=1): ini_m = MES_REF.replace(day=1)
    fim_m = (ini_m.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    lab = f"{ini_m.strftime('%b').lower()}"
    lab = {"jan":"jan","feb":"fev","mar":"mar","apr":"abr","may":"mai","jun":"jun","jul":"jul","aug":"ago","sep":"set","oct":"out","nov":"nov","dec":"dez"}[lab]
    meses_13.append((ini_m.isoformat()[:7], f"{lab}/{str(ini_m.year)[2:]}"))
comp13 = {m: [0, 0] for m, _ in meses_13}
for t in pagos_13m:
    m = bdate(t)[:7]
    if m in comp13:
        v = valor_efetivo(t)
        comp13[m][0 if v > 0 else 1] += v

# saldos das contas (para fluxo de caixa)
contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
def saldo_em(dia):
    tot = 0
    for c in contas:
        b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={dia}&id_account_main={c['id']}")["results"]
        tot += b["balanceDone"]
    return tot
saldo_ini_mes_ant = saldo_em((MES_REF.replace(day=1) - timedelta(days=1)).isoformat())
saldo_fim_mes_ant = saldo_em(FIM_MES.isoformat())
saldo_hoje = saldo_em(DIA_ANT.isoformat())

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=PRETO, spaceAfter=1)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceBefore=14, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#777777"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=7.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph
def P_val_int(cents, style, bold=False):
    """R$ + valor em reais (sem centavos) — colunas estreitas."""
    reais = round(cents / 100)
    st = ParagraphStyle("vi_" + style.name, parent=style, fontSize=6, leading=7,
                        textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: st.fontName = "Helvetica-Bold"
    txt = ("-" if reais < 0 else "") + f"{abs(reais):,}".replace(",", ".")
    return P(f"R$ {txt}" if reais else "R$ 0", st)

def P_val(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(brl(cents), s)
def tabela(rows, widths, fs=7.5, hpad=6):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), fs),
          ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5),
          ("LEFTPADDING", (0,0), (-1,-1), hpad), ("RIGHTPADDING", (0,0), (-1,-1), hpad),
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

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Colher_{MES_REF.strftime('%Y%m')}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.2*cm, rightMargin=1.2*cm,
                        topMargin=1.3*cm, bottomMargin=1.6*cm,
                        title=f"Relatório Gerencial — Colher Soluções em Publicidade e TI — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year}")
E = []
from PIL import Image as PILImage
if os.path.exists(LOGO):
    w0, h0 = PILImage.open(LOGO).size
    img = RLImage(LOGO, width=3.2*cm, height=3.2*cm*h0/w0)
    img.hAlign = "LEFT"
LOGO_TZ = os.path.join(_dir, "logo-terceirizou-completa.png")
if os.path.exists(LOGO_TZ):
    wt, ht = PILImage.open(LOGO_TZ).size
    img_tz = RLImage(LOGO_TZ, width=4.6*cm, height=4.6*cm*ht/wt)
    img_tz.hAlign = "RIGHT"
    t_cab = Table([[img, img_tz]], colWidths=[9.5*cm, 8.5*cm])
    t_cab.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                               ("ALIGN", (1,0), (1,0), "RIGHT")]))
    E.append(t_cab)
elif os.path.exists(LOGO):
    E.append(img)
E.append(Spacer(1, 6))
E.append(P("<b>COLHER SOLUÇÕES EM PUBLICIDADE E TI — Relatório Gerencial</b>", ParagraphStyle("h1c", parent=h1, alignment=1)))
E.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · Regime de caixa · Terceirizou — mais do que terceirizar o financeiro", ParagraphStyle("subc", parent=sub, alignment=1, spaceAfter=0)))
E.append(Spacer(1, 8))

# 1) Comparativo 13 meses
_cmp_titulo = P(f"Comparativo dos Últimos 13 Meses — {meses_13[0][1]} a {meses_13[-1][1]}", h2)
def P_int(cents, style, bold=False):
    """Valor em reais SEM R$ e sem centavos — colunas estreitas do comparativo."""
    reais = round(cents / 100)
    st = ParagraphStyle("pi_" + style.name, parent=style, fontSize=6, leading=7,
                        textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: st.fontName = "Helvetica-Bold"
    return P((("-" if reais < 0 else "") + f"{abs(reais):,}".replace(",", ".")) if reais else "0", st)

rows = [[P("<b>Mês</b>", cell)] + [P(f"<b>{lab}</b>", cellc) for _, lab in meses_13] + [P("<b>Média</b>", cellc), P("<b>Total</b>", cellc)],
        [P("Entrada realizada", cell)] + [P_int(comp13[m][0], cellr) for m, _ in meses_13],
        [P("Saída realizada", cell)] + [P_int(comp13[m][1], cellr) for m, _ in meses_13],
        [P("Resultado do mês", cellb)] + [P_int(comp13[m][0] + comp13[m][1], cellrb) for m, _ in meses_13]]
med_e = round(sum(v[0] for v in comp13.values()) / 13)
med_s = round(sum(v[1] for v in comp13.values()) / 13)
rows[1].append(P_int(med_e, cellrb, True)); rows[1].append(P_int(sum(v[0] for v in comp13.values()), cellrb, True))
rows[2].append(P_int(med_s, cellrb, True)); rows[2].append(P_int(sum(v[1] for v in comp13.values()), cellrb, True))
rows[3].append(P_int(med_e + med_s, cellrb, True)); rows[3].append(P_int(sum(v[0] + v[1] for v in comp13.values()), cellrb, True))
# categorias com movimentação nos 13 meses (matriz categoria × mês)
mat13 = defaultdict(lambda: defaultdict(int))
for t in pagos_13m:
    m = bdate(t)[:7]
    if m in comp13:
        mat13[cat_nome(t)][m] += valor_efetivo(t)
for cat in sorted(mat13):
    vals = [mat13[cat].get(m, 0) for m, _ in meses_13]
    if not any(vals):
        continue
    rows.append([P(cat, cell)] + [P_int(v, cellr) for v in vals]
                + [P_int(round(sum(vals) / 13), cellrb), P_int(sum(vals), cellrb)])
t = tabela(rows, [3.4*cm] + [1.02*cm]*13 + [1.3*cm, 1.5*cm], fs=6.5, hpad=2)
E.append(KeepTogether([_cmp_titulo, t]))

# 2) Receitas e Despesas do mês anterior (DRE por subcategoria)
_dre_titulo = P(f"Receitas e Despesas — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (realizado)", h2)
valores = defaultdict(lambda: [0, 0])
n_por = defaultdict(lambda: [0, 0])
for t in mes_tx:
    cid = cat_id(t)
    if cid is None: continue
    v = valor_efetivo(t)
    valores[cid][0 if v > 0 else 1] += v
    n_por[cid][0 if v > 0 else 1] += 1
com_mov = {cid for cid, (e, s) in valores.items() if e or s}
linhas_dre = []
for pai in sorted(pais_ordem, key=lambda p: _cod(p.get("ds_category"))):
    for _s in sorted(by_parent.get(pai["id"], []), key=lambda p: _cod(p.get("ds_category"))):
        if _s["id"] in com_mov:
            e, s = valores[_s["id"]]
            linhas_dre.append((_s.get("ds_category"), e + s, n_por[_s["id"]][0] + n_por[_s["id"]][1]))
    if pai["id"] in com_mov:
        e, s = valores[pai["id"]]
        linhas_dre.append((pai.get("ds_category"), e + s, n_por[pai["id"]][0] + n_por[pai["id"]][1]))
tot_rec = sum(e for cid, (e, s) in valores.items() if e > 0)
tot_desp = sum(s for cid, (e, s) in valores.items() if s < 0)
dre_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for nome, v, n in linhas_dre:
    dre_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
dre_rows.append([P("<b>Total de Receitas</b>", cellrb), P(f"<b>{sum(n2[0] for n2 in n_por.values())}</b>", cellc), P_val(tot_rec, cellrb, True)])
dre_rows.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n2[1] for n2 in n_por.values())}</b>", cellc), P_val(tot_desp, cellrb, True)])
APORTE_ID = 10188313  # 05.01 Aporte do Sócio
aporte_mes = valores.get(APORTE_ID, [0, 0])[0]  # entradas da subcategoria 05.01
if aporte_mes:
    # com aporte no mês: mostrar Resultado Operacional (sem aporte) e Resultado Financeiro
    res_op = tot_rec - aporte_mes + tot_desp
    res_fin = tot_rec + tot_desp
    dre_rows.append([P("<b>Resultado Operacional (sem aporte do sócio)</b>", cellrb), P("", cellc), P_val(res_op, cellrb, True)])
    dre_rows.append([P("<b>Resultado Financeiro (com aporte)</b>", cellrb), P(f"<b>{len(mes_tx)}</b>", cellc), P_val(res_fin, cellrb, True)])
    _n_res = 4
else:
    # sem aporte: apenas o resultado do mês
    dre_rows.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{len(mes_tx)}</b>", cellc), P_val(tot_rec + tot_desp, cellrb, True)])
    _n_res = 3
t = tabela(dre_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(dre_rows)-_n_res+1), (-1,len(dre_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([_dre_titulo, t]))

# 3) Fluxo de Caixa do mês anterior — entradas/saídas pelo BALANCES do mês (data de baixa),
# que fecha com os saldos real (o dt_billing pode divergir da baixa — pedido Vinícius 24/10)
_b_mes = req(f"{BASE}/transaction/v1/transactions/balances?start_date={MES_REF.replace(day=1).isoformat()}&end_date={FIM_MES.isoformat()}")["results"]
fx_e = _b_mes["revenuesDone"]
fx_s = _b_mes["expensesDone"]
fx_rows = [[P("<b>Descrição</b>", cell), P("<b>Valor</b>", cellr)],
           [P("Saldo inicial", cell), P_val(saldo_ini_mes_ant, cellr)],
           [P("(+) Entradas", cell), P_val(fx_e, cellr)],
           [P("(−) Saídas", cell), P_val(fx_s, cellr)],
           [P("<b>Saldo final</b>", cellrb), P_val(saldo_fim_mes_ant, cellrb, True)]]
t = tabela(fx_rows, [8*cm, 5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(fx_rows)-1), (-1,len(fx_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([P(f"Fluxo de Caixa — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (realizado)", h2), t]))

# 4) Previsão de Receitas e Despesas do mês atual (pendente a partir de hoje)
_pv_titulo = P(f"Previsão de Receitas e Despesas — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year} (realizado + previsto)", h2)
valores_p = defaultdict(lambda: [0, 0])
n_por_p = defaultdict(lambda: [0, 0])
for t in prev_completa:
    cid = cat_id(t)
    if cid is None: continue
    v = valor_efetivo(t)
    valores_p[cid][0 if v > 0 else 1] += v
    n_por_p[cid][0 if v > 0 else 1] += 1
com_mov_p = {cid for cid, (e, s) in valores_p.items() if e or s}
prev_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor previsto</b>", cellr)]]
for pai in sorted(pais_ordem, key=lambda p: _cod(p.get("ds_category"))):
    for _s in sorted(by_parent.get(pai["id"], []), key=lambda p: _cod(p.get("ds_category"))):
        if _s["id"] in com_mov_p:
            e, s = valores_p[_s["id"]]
            prev_rows.append([P(_s.get("ds_category"), cell), P(str(n_por_p[_s["id"]][0] + n_por_p[_s["id"]][1]), cellc), P_val(e + s, cellr)])
    if pai["id"] in com_mov_p:
        e, s = valores_p[pai["id"]]
        prev_rows.append([P(pai.get("ds_category"), cell), P(str(n_por_p[pai["id"]][0] + n_por_p[pai["id"]][1]), cellc), P_val(e + s, cellr)])
tot_rec_p = sum(e for cid, (e, s) in valores_p.items() if e > 0)
tot_desp_p = sum(s for cid, (e, s) in valores_p.items() if s < 0)
prev_rows.append([P("<b>Total de Receitas (realizado + previsto)</b>", cellrb), P(f"<b>{sum(n2[0] for n2 in n_por_p.values())}</b>", cellc), P_val(tot_rec_p, cellrb, True)])
prev_rows.append([P("<b>Total de Despesas (realizado + previsto)</b>", cellrb), P(f"<b>{sum(n2[1] for n2 in n_por_p.values())}</b>", cellc), P_val(tot_desp_p, cellrb, True)])
prev_rows.append([P("<b>Resultado previsto do mês</b>", cellrb), P(f"<b>{len(prev_completa)}</b>", cellc), P_val(tot_rec_p + tot_desp_p, cellrb, True)])
t = tabela(prev_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(prev_rows)-3), (-1,len(prev_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([_pv_titulo, t]))

# 5) Previsão de Fluxo de Caixa do mês atual (título + tabela juntos)
_fx_titulo = P(f"Previsão de Fluxo de Caixa — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year}", h2)
pago_atual_e = sum(t["value_in_cent"] for t in prev_pago_atual if t["value_in_cent"] > 0)
pago_atual_s = sum(t["value_in_cent"] for t in prev_pago_atual if t["value_in_cent"] < 0)
fxp_rows = [[P("<b>Descrição</b>", cell), P("<b>Valor</b>", cellr)],
            [P(f"Saldo inicial ({FIM_MES.strftime('%d/%m')})", cell), P_val(saldo_fim_mes_ant, cellr)],
            [P("(+) Entradas do mês (realizado + previsto)", cell), P_val(tot_rec_p, cellr)],
            [P("(−) Saídas do mês (realizado + previsto)", cell), P_val(tot_desp_p, cellr)],
            [P("<b>Saldo final projetado</b>", cellrb), P_val(saldo_fim_mes_ant + tot_rec_p + tot_desp_p, cellrb, True)]]
t = tabela(fxp_rows, [8*cm, 5*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(fxp_rows)-1), (-1,len(fxp_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([_fx_titulo, t]))

# 6) Resultado dos últimos 12 meses
_rs_titulo = P(f"Resultado dos Últimos 12 Meses — {meses_13[1][1]} a {meses_13[-1][1]}", h2)
rs_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
for m, lab in meses_13[1:]:
    e_m, s_m = comp13[m]
    rs_rows.append([P(lab, cell), P_val(e_m, cellr), P_val(s_m, cellr), P_val(e_m + s_m, cellrb)])
tot12_e = sum(comp13[m][0] for m, _ in meses_13[1:])
tot12_s = sum(comp13[m][1] for m, _ in meses_13[1:])
rs_rows.append([P("<b>Resultado 12 meses</b>", cellrb), P_val(tot12_e, cellrb, True), P_val(tot12_s, cellrb, True), P_val(tot12_e + tot12_s, cellrb, True)])
t = tabela(rs_rows, [3*cm, 4.3*cm, 4.3*cm, 4.4*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rs_rows)-1), (-1,len(rs_rows)-1), LARANJA_CLARO)]))
E.append(KeepTogether([_rs_titulo, t]))

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Colher_{MES_REF.strftime('%Y%m')}.xlsx"
wb = Workbook(); ws = wb.active; ws.title = "Relatório"
FILL_H = PatternFill("solid", fgColor="FF501C"); FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF"); FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
def sec(w, titulo, header):
    w.append((titulo,))
    w.merge_cells(start_row=w.max_row, start_column=1, end_row=w.max_row, end_column=len(header))
    c = w.cell(row=w.max_row, column=1)
    c.font = Font(bold=True, size=11, color="FF501C")
    w.append(header)
    for cc in w[w.max_row]: cc.fill = FILL_H; cc.font = FH
def linha_val(w, vals, bold=False, fill=False):
    w.append(vals)
    r = w.max_row
    for j, cc in enumerate(w[r], 1):
        if isinstance(cc.value, (int, float)) and j > 1:
            cc.number_format = '"R$" #,##0.00'
            cc.font = Font(bold=bold, color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
        elif bold:
            cc.font = FB
        if fill:
            cc.fill = FILL_T

ws.append((f"COLHER SOLUÇÕES EM PUBLICIDADE E TI — Relatório Gerencial — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regime de caixa)",))
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=15)
c = ws.cell(row=1, column=1); c.font = Font(bold=True, size=13, color="FF501C")
ws.row_dimensions[1].height = 24
# 1) comparativo 13m
sec(ws, "Comparativo dos Últimos 13 Meses", ("Mês",) + tuple(lab for _, lab in meses_13) + ("Média", "Total"))
linha_val(ws, ("Entrada realizada",) + tuple(comp13[m][0] / 100 for m, _ in meses_13) + (med_e / 100, sum(v[0] for v in comp13.values()) / 100))
linha_val(ws, ("Saída realizada",) + tuple(comp13[m][1] / 100 for m, _ in meses_13) + (med_s / 100, sum(v[1] for v in comp13.values()) / 100))
linha_val(ws, ("Resultado do mês",) + tuple((comp13[m][0] + comp13[m][1]) / 100 for m, _ in meses_13) + ((med_e + med_s) / 100, sum(v[0] + v[1] for v in comp13.values()) / 100), bold=True, fill=True)
# 2) DRE do mês
sec(ws, f"Receitas e Despesas — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (realizado)", ("Categoria", "Lançamentos", "Valor"))
for nome, v, n in linhas_dre:
    linha_val(ws, (nome, n, v / 100))
linha_val(ws, ("Total de Receitas", sum(n2[0] for n2 in n_por.values()), tot_rec / 100), bold=True, fill=True)
linha_val(ws, ("Total de Despesas", sum(n2[1] for n2 in n_por.values()), tot_desp / 100), bold=True, fill=True)
if aporte_mes:
    linha_val(ws, ("Resultado Operacional (sem aporte do sócio)", (tot_rec - aporte_mes + tot_desp) / 100), bold=True, fill=True)
    linha_val(ws, ("Resultado Financeiro (com aporte)", (tot_rec + tot_desp) / 100), bold=True, fill=True)
else:
    linha_val(ws, ("Resultado do mês", len(mes_tx), (tot_rec + tot_desp) / 100), bold=True, fill=True)
# 3) fluxo mês anterior
sec(ws, f"Fluxo de Caixa — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (realizado)", ("Descrição", "Valor"))
linha_val(ws, ("Saldo inicial", saldo_ini_mes_ant / 100))
linha_val(ws, ("(+) Entradas", comp13[MES_REF.isoformat()[:7]][0] / 100))
linha_val(ws, ("(−) Saídas", comp13[MES_REF.isoformat()[:7]][1] / 100))
linha_val(ws, ("Saldo final", saldo_fim_mes_ant / 100), bold=True, fill=True)
# 4) previsão rec/desp mês atual
sec(ws, f"Previsão de Receitas e Despesas — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year} (pendente)", ("Categoria", "Lançamentos", "Valor previsto"))
for pai in sorted(pais_ordem, key=lambda p: _cod(p.get("ds_category"))):
    for _s in sorted(by_parent.get(pai["id"], []), key=lambda p: _cod(p.get("ds_category"))):
        if _s["id"] in com_mov_p:
            e, s = valores_p[_s["id"]]
            linha_val(ws, (_s.get("ds_category"), n_por_p[_s["id"]][0] + n_por_p[_s["id"]][1], (e + s) / 100))
    if pai["id"] in com_mov_p:
        e, s = valores_p[pai["id"]]
        linha_val(ws, (pai.get("ds_category"), n_por_p[pai["id"]][0] + n_por_p[pai["id"]][1], (e + s) / 100))
linha_val(ws, ("Total de Receitas previstas", sum(n2[0] for n2 in n_por_p.values()), tot_rec_p / 100), bold=True, fill=True)
linha_val(ws, ("Total de Despesas previstas", sum(n2[1] for n2 in n_por_p.values()), tot_desp_p / 100), bold=True, fill=True)
linha_val(ws, ("Resultado previsto", len(prev_atual), (tot_rec_p + tot_desp_p) / 100), bold=True, fill=True)
# 5) previsão fluxo mês atual
sec(ws, f"Previsão de Fluxo de Caixa — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year}", ("Descrição", "Valor"))
linha_val(ws, (f"Saldo inicial ({FIM_MES.strftime('%d/%m')})", saldo_fim_mes_ant / 100))
linha_val(ws, ("(+) Entradas do mês (realizado + previsto)", tot_rec_p / 100))
linha_val(ws, ("(−) Saídas do mês (realizado + previsto)", tot_desp_p / 100))
linha_val(ws, ("Saldo final projetado", (saldo_fim_mes_ant + tot_rec_p + tot_desp_p) / 100), bold=True, fill=True)
# 6) resultado 12m
sec(ws, f"Resultado dos Últimos 12 Meses — {meses_13[1][1]} a {meses_13[-1][1]}", ("Mês", "Entradas", "Saídas", "Resultado"))
for m, lab in meses_13[1:]:
    e_m, s_m = comp13[m]
    linha_val(ws, (lab, e_m / 100, s_m / 100, (e_m + s_m) / 100))
linha_val(ws, ("Resultado 12 meses", tot12_e / 100, tot12_s / 100, (tot12_e + tot12_s) / 100), bold=True, fill=True)
ws.column_dimensions["A"].width = 30
from openpyxl.utils import get_column_letter as _gcl
for j in range(2, 17):
    ws.column_dimensions[_gcl(j)].width = 12

# aba: TODOS os lançamentos realizados (13 meses)
ws_l = wb.create_sheet("Lançamentos 13m")
ws_l.append((f"Todos os lançamentos realizados — {meses_13[0][1]} a {meses_13[-1][1]} (regime de caixa)",))
ws_l.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
c_l = ws_l.cell(row=1, column=1); c_l.font = Font(bold=True, size=12, color="FF501C")
ws_l.row_dimensions[1].height = 22
ws_l.append(("Data", "Categoria", "Descrição", "Conta", "Valor"))
for cc in ws_l[2]: cc.fill = FILL_H; cc.font = FH
for t in sorted(pagos_13m, key=bdate):
    d = bdate(t)
    ws_l.append((f"{d[8:10]}/{d[5:7]}/{d[:4]}", cat_nome(t), (t.get("ds_transaction") or "")[:60],
                 t.get("ds_account_main") or "", t["value_in_cent"] / 100))
for row in ws_l.iter_rows(min_row=3):
    cc = row[4]
    if isinstance(cc.value, (int, float)):
        cc.number_format = '"R$" #,##0.00'
        cc.font = Font(color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
for col, w in zip("ABCDE", (12, 40, 55, 22, 16)):
    ws_l.column_dimensions[col].width = w
ws_l.freeze_panes = "A3"

# aba: previsão completa do mês atual (realizado + pendente)
ws_p = wb.create_sheet(f"Previsão {MES_PT[MES_ATUAL.month][:3]}")
ws_p.append((f"Mês atual ({MES_PT[MES_ATUAL.month].capitalize()}/{MES_ATUAL.year}) — realizado + pendente (regime de caixa)",))
ws_p.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
c_p = ws_p.cell(row=1, column=1); c_p.font = Font(bold=True, size=12, color="FF501C")
ws_p.row_dimensions[1].height = 22
ws_p.append(("Situação", "Data", "Categoria", "Descrição", "Conta", "Valor"))
for cc in ws_p[2]: cc.fill = FILL_H; cc.font = FH
for t in sorted(prev_completa, key=bdate):
    d = bdate(t)
    sit = "Pago/Recebido" if t.get("situation") in (1, 2) else "Pendente"
    ws_p.append((sit, f"{d[8:10]}/{d[5:7]}/{d[:4]}", cat_nome(t), (t.get("ds_transaction") or "")[:60],
                 t.get("ds_account_main") or "", t["value_in_cent"] / 100))
for row in ws_p.iter_rows(min_row=3):
    cc = row[5]
    if isinstance(cc.value, (int, float)):
        cc.number_format = '"R$" #,##0.00'
        cc.font = Font(color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
for col, w in zip("ABCDEF", (14, 12, 40, 55, 22, 16)):
    ws_p.column_dimensions[col].width = w
ws_p.freeze_panes = "A3"

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
