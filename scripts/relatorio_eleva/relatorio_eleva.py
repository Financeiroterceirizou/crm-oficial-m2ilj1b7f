#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RELATÓRIO GERENCIAL — ELEVA — v1.0, 2026-10-24 (pedido Vinícius)
#   11 seções: comparativo 13m competência + caixa (sem CC HNSC MICHELLE), DRE mês anterior
#   competência + caixa (sem HNSC MICHELLE), fluxo de caixa realizado (caixa), previsões
#   competência + caixa (sem HNSC MICHELLE), previsão de fluxo, DRE por CC (LARISSA, MICHELLE),
#   DRE por TAG (clientes, competência, só tags com movimento), saldos das contas em 30/09.
#   Logos Eleva + Terceirizou na capa.
import sys, os, json, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage, KeepTogether
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_ELEVA") or open(os.path.join(_dir, ".controlle_token")).read().strip()
BASE = "https://api-v1.controlle.com"
UAH = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UAH.items(): r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (409, 500, 502, 503) and i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise

# ---- parâmetros ----
HOJE = date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat())
MES_REF = HOJE.replace(day=1) - timedelta(days=1)          # mês anterior (setembro)
FIM_MES = (MES_REF.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
MES_ATUAL = HOJE.replace(day=1)                             # mês atual (outubro)
FIM_ATUAL = (MES_ATUAL.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
MES_PT = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
          7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}

# ---- helpers de dados ----
def bdate(t): return (t.get("dt_billing") or t.get("dt_due") or "")[:10]
def cdate(t): return (t.get("dt_competence") or bdate(t))[:10]
def cc_names(t):
    return [c.get("ds_cost_center") for c in (t.get("apportionments_cost_center") or [])]
def tag_names(t):
    return [x.get("ds_tag") for x in (t.get("array_tags") or [])]
def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "(sem categoria)") if cats else "(sem categoria)"
def cat_id(t):
    cats = t.get("apportionments_plan_account") or []
    return cats[0].get("id_category") if cats else None
def valor_efetivo(t):
    """Valor real: payment_in_cent quando pago (sit 1,2), value_in_cent quando pendente."""
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]
def eh_transferencia(t):
    cats = t.get("apportionments_plan_account") or []
    return any((c.get("ds_category") or "").startswith("90") for c in cats)
def tem_cc(t, nome):
    return nome in cc_names(t)

CC_EXCLUIDO = "HNSC MICHELLE"
TAGS_CLIENTE = ["MARIA VITORIA", "BELVIVERE", "DERMON", "JULIA SOARES", "ESPLENDICE",
                "LUCIANA LEAES", "MINDRA", "NAIANA", "OUTROS"]

def tx_list(ini, fim):
    out, page = [], 1
    while True:
        tl = req(f"{BASE}/transaction/v1/transactions/list?start_date={ini}&end_date={fim}"
                 f"&page={page}&orderBy=date&orderByCardinality=ASC").get("results", {}).get("transactionsList", [])
        out.extend(tl)
        if len(tl) < 100: break
        page += 1
    return out

contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]

def saldo_em(dia):
    tot = 0
    for c in contas:
        b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={dia}&id_account_main={c['id']}")["results"]
        tot += b["balanceDone"]
    return tot

def balances_mes(ini, fim):
    e = s = 0
    for c in contas:
        b = req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini}&end_date={fim}&id_account_main={c['id']}")["results"]
        e += b["revenuesDone"]; s += b["expensesDone"]
    return e, s

# ---- dados ----
INI_13 = MES_REF.replace(day=1) - timedelta(days=365)
tx_13m = tx_list(INI_13.isoformat(), FIM_ATUAL.isoformat())
pagos_13m = [t for t in tx_13m if t.get("situation") in (1, 2) and not eh_transferencia(t)]
mes_tx = [t for t in pagos_13m if MES_REF.replace(day=1).isoformat() <= bdate(t) <= FIM_MES.isoformat()]
prev_completa = [t for t in tx_list(MES_ATUAL.isoformat(), FIM_ATUAL.isoformat())
                 if t.get("situation") in (0, 1, 2) and not eh_transferencia(t)]

# meses do comparativo (13)
meses_13 = []
for i in range(0, 13):
    ini_m = INI_13 + timedelta(days=32 * i)
    ini_m = date(ini_m.year, ini_m.month, 1)
    lab = f"{ini_m.month:02d}/{str(ini_m.year)[2:]}"
    meses_13.append((ini_m.isoformat()[:7], lab))
comp13 = {m: [0, 0] for m, _ in meses_13}          # competência
comp13c = {m: [0, 0] for m, _ in meses_13}         # caixa
for t in pagos_13m:
    if tem_cc(t, CC_EXCLUIDO): continue
    mc, mx = cdate(t)[:7], bdate(t)[:7]
    if mc in comp13:
        v = t["value_in_cent"]
        comp13[mc][0 if v > 0 else 1] += v
    if mx in comp13c:
        v = valor_efetivo(t)
        comp13c[mx][0 if v > 0 else 1] += v

# saldos
saldo_ini_mes_ant = saldo_em((MES_REF.replace(day=1) - timedelta(days=1)).isoformat())
saldo_fim_mes_ant = saldo_em(FIM_MES.isoformat())
bal_e, bal_s = balances_mes(MES_REF.replace(day=1).isoformat(), FIM_MES.isoformat())

# ---- estilos ----
LARANJA = HexColor("#FF501C"); LARANJA_CLARO = HexColor("#fdf0e8")
VERDE = HexColor("#1a7f37"); VERMELHO = HexColor("#c0271d"); PRETO = HexColor("#1a1a1a")
CINZA = HexColor("#6b6b6b"); FUNDO_HDR = HexColor("#2b2b2b")
def st(nome, **kw):
    base = dict(fontName="Helvetica", fontSize=8, leading=10, textColor=PRETO)
    base.update(kw); return ParagraphStyle(nome, **base)
h1 = st("h1", fontSize=15, leading=19, fontName="Helvetica-Bold", textColor=PRETO)
h2 = st("h2", fontSize=10.5, leading=14, fontName="Helvetica-Bold", textColor=LARANJA)
cell = st("c"); cellc = st("cc", alignment=1); cellr = st("cr", alignment=2)
cellb = st("cb", fontName="Helvetica-Bold"); cellrb = st("crb", alignment=2, fontName="Helvetica-Bold")
cellw = st("cw", textColor=colors.white, fontName="Helvetica-Bold", fontSize=7.5, leading=9)
cellwc = st("cwc", textColor=colors.white, fontName="Helvetica-Bold", fontSize=7.5, leading=9, alignment=1)
cellwr = st("cwr", textColor=colors.white, fontName="Helvetica-Bold", fontSize=7.5, leading=9, alignment=2)
def P(txt, style=cell): return Paragraph(str(txt), style)
def P_val(cents, style=cellr, bold=False):
    v = cents / 100
    cor = VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO
    s2 = ParagraphStyle(style.name + "_v", parent=style, textColor=cor)
    if bold: s2.fontName = "Helvetica-Bold"
    return P(f"{'-' if v < 0 else ''}R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), s2)
def P_int(cents, style, bold=False):
    reais = round(cents / 100)
    s2 = ParagraphStyle(style.name + "_i", parent=style,
                        textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s2.fontName = "Helvetica-Bold"
    return P((("-" if reais < 0 else "") + f"{abs(reais):,}".replace(",", ".")) if reais else "0", s2)
def tabela(rows, widths, fs=None, hpad=4):
    t = Table(rows, colWidths=widths, repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), FUNDO_HDR),
              ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#d9d9d9")),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), hpad), ("BOTTOMPADDING", (0, 0), (-1, -1), hpad),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#f7f7f7")])]
    t.setStyle(TableStyle(estilo))
    return t
def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(LARANJA)
    canvas.rect(1.2 * cm, 0.8 * cm, 0.5 * cm, 0.5 * cm, stroke=0, fill=1)
    canvas.setFont("Helvetica", 7); canvas.setFillColor(CINZA)
    canvas.drawRightString(A4[0] - 1.2 * cm, 0.9 * cm, f"Página {doc.page}")
    canvas.restoreState()

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Eleva_{MES_REF.strftime('%Y%m')}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.4 * cm, rightMargin=1.4 * cm,
                        topMargin=1.4 * cm, bottomMargin=1.6 * cm,
                        title=f"Relatório Gerencial — Eleva — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year}")
E = []

# ---- capa ----
E.append(Spacer(1, 0.4 * cm))
_logos = []
LOGO_E = os.path.join(_dir, "logo-eleva.png")
if os.path.exists(LOGO_E):
    w0, h0 = PILImage.open(LOGO_E).size
    _logos.append(RLImage(LOGO_E, width=4.2 * cm, height=4.2 * cm * h0 / w0))
LOGO_TZ = os.path.join(_dir, "logo-terceirizou-completa.png")
if os.path.exists(LOGO_TZ):
    wt, ht = PILImage.open(LOGO_TZ).size
    _logos.append(RLImage(LOGO_TZ, width=5.2 * cm, height=5.2 * cm * ht / wt))
if _logos:
    lt = Table([_logos], colWidths=[A4[0] / len(_logos)] * len(_logos))
    lt.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    E.append(lt)
E.append(Spacer(1, 0.8 * cm))
E.append(P("<b>ELEVA — Relatório Gerencial</b>", ParagraphStyle("h1c", parent=h1, alignment=1)))
E.append(Spacer(1, 0.2 * cm))
E.append(P(f"{MES_PT[MES_REF.month].capitalize()} de {MES_REF.year}", ParagraphStyle("sub", parent=st("s2"), alignment=1, fontSize=11, textColor=CINZA)))
E.append(Spacer(1, 0.5 * cm))
E.append(P("Regimes: competência e caixa (pagamento) · Centros de custo e tags por cliente", ParagraphStyle("sub2", parent=st("s3"), alignment=1, fontSize=8.5, textColor=CINZA)))
E.append(PageBreak())

# ---- 1) comparativo 13m competência ----
def bloco_comparativo(titulo, comp):
    rows = [[P("<b>Mês</b>", cell)] + [P(f"<b>{lab}</b>", cellc) for _, lab in meses_13] + [P("<b>Média</b>", cellc), P("<b>Total</b>", cellc)],
            [P("Entrada realizada", cell)] + [P_int(comp[m][0], cellr) for m, _ in meses_13],
            [P("Saída realizada", cell)] + [P_int(comp[m][1], cellr) for m, _ in meses_13],
            [P("Resultado do mês", cellb)] + [P_int(comp[m][0] + comp[m][1], cellrb) for m, _ in meses_13]]
    n = len(meses_13)
    med_e = round(sum(v[0] for v in comp.values()) / n)
    med_s = round(sum(v[1] for v in comp.values()) / n)
    rows[1].append(P_int(med_e, cellrb, True)); rows[1].append(P_int(sum(v[0] for v in comp.values()), cellrb, True))
    rows[2].append(P_int(med_s, cellrb, True)); rows[2].append(P_int(sum(v[1] for v in comp.values()), cellrb, True))
    rows[3].append(P_int(med_e + med_s, cellrb, True)); rows[3].append(P_int(sum(v[0] + v[1] for v in comp.values()), cellrb, True))
    return rows, n

_cmp1_t = P(f"Comparativo dos Últimos 13 Meses — Regime de Competência (sem CC {CC_EXCLUIDO})", h2)
rows1, n13 = bloco_comparativo(None, comp13)
E.append(KeepTogether([_cmp1_t, tabela(rows1, [2.6*cm] + [1.15*cm]*13 + [1.4*cm, 1.6*cm], fs=6.5, hpad=2)]))
E.append(Spacer(1, 0.5 * cm))

# ---- 2) comparativo 13m caixa ----
_cmp2_t = P(f"Comparativo dos Últimos 13 Meses — Regime Caixa/Pagamento (sem CC {CC_EXCLUIDO})", h2)
rows2, _ = bloco_comparativo(None, comp13c)
E.append(KeepTogether([_cmp2_t, tabela(rows2, [2.6*cm] + [1.15*cm]*13 + [1.4*cm, 1.6*cm], fs=6.5, hpad=2)]))
E.append(PageBreak())

# ---- DRE por categoria (usada nas seções 3, 4, 9, 10) ----
pais_ordem = []
by_parent = defaultdict(list)
vistos = set()
for t in tx_13m:
    cats = t.get("apportionments_plan_account") or []
    if not cats: continue
    c0 = cats[0]
    pid = c0.get("id_parent_category")
    cid, nome = c0.get("id_category"), c0.get("ds_category") or ""
    if cid and cid not in vistos:
        vistos.add(cid)
        cod = nome.split(" ")[0] if nome[:2].isdigit() else "zz"
        if pid:
            by_parent[pid].append({"id": cid, "ds_category": nome, "_cod": cod})
        else:
            pais_ordem.append({"id": cid, "ds_category": nome, "_cod": cod})
def _cod(c): return c.get("_cod") or "zz"

def dre_rows(tx, titulo_total="Total", regime="caixa"):
    valores = defaultdict(lambda: [0, 0])
    n_por = defaultdict(lambda: [0, 0])
    for t in tx:
        cid = cat_id(t)
        if cid is None: continue
        v = t["value_in_cent"] if regime == "comp" else valor_efetivo(t)
        valores[cid][0 if v > 0 else 1] += v
        n_por[cid][0 if v > 0 else 1] += 1
    com_mov = {cid for cid, (e, s) in valores.items() if e or s}
    rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
    tot_e = tot_s = 0
    for pai in sorted(pais_ordem, key=_cod):
        tem = False
        for _s in sorted(by_parent.get(pai["id"], []), key=_cod):
            if _s["id"] in com_mov:
                tem = True
                e, s = valores[_s["id"]]
                rows.append([P("   " + _s.get("ds_category"), cell), P(str(n_por[_s["id"]][0] + n_por[_s["id"]][1]), cellc), P_val(e, cellr), P_val(s, cellr), P_val(e + s, cellr)])
        if pai["id"] in com_mov:
            tem = True
            e, s = valores[pai["id"]]
            rows.append([P(f"<b>{pai.get('ds_category')}</b>", cellb), P(f"<b>{n_por[pai['id']][0] + n_por[pai['id']][1]}</b>", cellc), P_val(e, cellrb), P_val(s, cellrb), P_val(e + s, cellrb)])
        if tem:
            tot_e += valores[pai["id"]][0]; tot_s += valores[pai["id"]][1]
    rows.append([P(f"<b>{titulo_total}</b>", cellrb), P(f"<b>{sum(x[0] + x[1] for x in n_por.values())}</b>", cellc), P_val(tot_e, cellrb, True), P_val(tot_s, cellrb, True), P_val(tot_e + tot_s, cellrb, True)])
    return rows

# ---- 3) DRE mês anterior competência ----
sem_hnsc = lambda tx: [t for t in tx if not tem_cc(t, CC_EXCLUIDO)]
_dre1_t = P(f"Receitas e Despesas — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} — Regime de Competência (sem CC {CC_EXCLUIDO})", h2)
E.append(KeepTogether([_dre1_t, tabela(dre_rows(sem_hnsc(mes_tx), regime="comp"), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm])]))
E.append(Spacer(1, 0.5 * cm))

# ---- 4) DRE mês anterior caixa ----
_dre2_t = P(f"Receitas e Despesas — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} — Regime Caixa/Pagamento (sem CC {CC_EXCLUIDO})", h2)
E.append(KeepTogether([_dre2_t, tabela(dre_rows(sem_hnsc(mes_tx)), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm])]))
E.append(PageBreak())

# ---- 5) fluxo de caixa realizado (caixa, COM HNSC) ----
_fx_t = P(f"Fluxo de Caixa — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regime caixa)", h2)
fx_rows = [[P("<b>Descrição</b>", cell), P("<b>Valor</b>", cellr)],
           [P("Saldo inicial", cell), P_val(saldo_ini_mes_ant, cellr)],
           [P("(+) Entradas (baixas do mês)", cell), P_val(bal_e, cellr)],
           [P("(−) Saídas (baixas do mês)", cell), P_val(bal_s, cellr)],
           [P("<b>Saldo final</b>", cellrb), P_val(saldo_fim_mes_ant, cellrb, True)]]
E.append(KeepTogether([_fx_t, tabela(fx_rows, [8*cm, 5*cm])]))
E.append(Spacer(1, 0.5 * cm))

# ---- 6) previsão DRE competência (pagos + não pagos, sem HNSC) ----
_pv1_t = P(f"Previsão de Receitas e Despesas — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year} — Regime de Competência (pagos + não pagos, sem CC {CC_EXCLUIDO})", h2)
E.append(KeepTogether([_pv1_t, tabela(dre_rows(sem_hnsc(prev_completa), regime="comp"), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm])]))
E.append(Spacer(1, 0.5 * cm))

# ---- 7) previsão DRE caixa (pagos + não pagos, sem HNSC) ----
_pv2_t = P(f"Previsão de Receitas e Despesas — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year} — Regime Caixa/Pagamento (pagos + não pagos, sem CC {CC_EXCLUIDO})", h2)
E.append(KeepTogether([_pv2_t, tabela(dre_rows(sem_hnsc(prev_completa)), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm])]))
E.append(PageBreak())

# ---- 8) previsão fluxo de caixa ----
_fxp_t = P(f"Previsão de Fluxo de Caixa — {MES_PT[MES_ATUAL.month].capitalize()} de {MES_ATUAL.year}", h2)
tot_rec_p = sum(valor_efetivo(t) for t in prev_completa if valor_efetivo(t) > 0)
tot_desp_p = sum(valor_efetivo(t) for t in prev_completa if valor_efetivo(t) < 0)
fxp_rows = [[P("<b>Descrição</b>", cell), P("<b>Valor</b>", cellr)],
            [P(f"Saldo inicial ({FIM_MES.strftime('%d/%m')})", cell), P_val(saldo_fim_mes_ant, cellr)],
            [P("(+) Entradas do mês (realizado + previsto)", cell), P_val(tot_rec_p, cellr)],
            [P("(−) Saídas do mês (realizado + previsto)", cell), P_val(tot_desp_p, cellr)],
            [P("<b>Saldo final projetado</b>", cellrb), P_val(saldo_fim_mes_ant + tot_rec_p + tot_desp_p, cellrb, True)]]
E.append(KeepTogether([_fxp_t, tabela(fxp_rows, [8*cm, 5*cm])]))
E.append(Spacer(1, 0.5 * cm))

# ---- 9) DRE por CC (LARISSA, MICHELLE) — competência ----
_cc_t = P(f"Receitas e Despesas por Centro de Custo — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} — Regime de Competência", h2)
for cc_nome in ["LARISSA", "MICHELLE"]:
    tx_cc = [t for t in mes_tx if tem_cc(t, cc_nome)]
    E.append(P(f"<b>Centro de Custo: {cc_nome}</b>", st("ccn", fontName="Helvetica-Bold", fontSize=9.5, textColor=PRETO)))
    if tx_cc:
        E.append(tabela(dre_rows(tx_cc, f"Total {cc_nome}", regime="comp"), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm]))
    else:
        E.append(P("Sem lançamentos no mês.", cell))
    E.append(Spacer(1, 0.4 * cm))
E.append(PageBreak())

# ---- 10) DRE por TAG (clientes) — competência ----
_tag_t = P(f"Receitas e Despesas por Tag — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} — Regime de Competência", h2)
E.append(_tag_t)
tem_tag_alguma = False
for tag in TAGS_CLIENTE:
    tx_tag = [t for t in mes_tx if tag in tag_names(t)]
    if not tx_tag: continue
    tem_tag_alguma = True
    E.append(P(f"<b>Tag: {tag}</b>", st("tgn", fontName="Helvetica-Bold", fontSize=9.5, textColor=PRETO)))
    E.append(tabela(dre_rows(tx_tag, f"Total {tag}", regime="comp"), [7.2*cm, 2.2*cm, 2.6*cm, 2.6*cm, 2.8*cm]))
    E.append(Spacer(1, 0.4 * cm))
if not tem_tag_alguma:
    E.append(P("Sem lançamentos por tag no mês.", cell))

# ---- 11) saldos nas contas em 30/09 ----
_saldo_t = P(f"Saldo nas Contas — {FIM_MES.strftime('%d/%m/%Y')}", h2)
sald_rows = [[P("<b>Conta</b>", cell), P("<b>Saldo</b>", cellr)]]
for c in contas:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={FIM_MES.isoformat()}&id_account_main={c['id']}")["results"]
    sald_rows.append([P(c.get("ds_account") or "", cell), P_val(b["balanceDone"], cellr)])
sald_rows.append([P("<b>Total</b>", cellrb), P_val(saldo_fim_mes_ant, cellrb, True)])
E.append(KeepTogether([_saldo_t, tabela(sald_rows, [10*cm, 4*cm])]))

doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print(f"OK: {ARQ_PDF}")

# ---- Excel ----
from openpyxl.utils import get_column_letter
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Eleva_{MES_REF.strftime('%Y%m')}.xlsx"
wb = Workbook(); ws = wb.active; ws.title = "Relatório"
ws.append((f"ELEVA — Relatório Gerencial — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regimes competência e caixa)",))
ws["A1"].font = Font(bold=True, size=13)
def sec(nome):
    ws.append(("",)); ws.append((nome,)); ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=11, color="FF501C")
def linha(*vals, bold=False, fill=False):
    ws.append(vals)
    r = ws.max_row
    for c in range(1, len(vals) + 1):
        cc2 = ws.cell(row=r, column=c)
        if bold: cc2.font = Font(bold=True)
        if fill: cc2.fill = PatternFill("solid", fgColor="FDF0E8")
        if isinstance(vals[c - 1], (int, float)) and c > 1: cc2.number_format = "#,##0.00"

sec(f"1. Comparativo 13 meses — Competência (sem CC {CC_EXCLUIDO})")
linha("Mês", *[lab for _, lab in meses_13], "Média", "Total", bold=True, fill=True)
n13 = len(meses_13)
linha("Entrada realizada", *[comp13[m][0] / 100 for m, _ in meses_13], round(sum(v[0] for v in comp13.values()) / n13 / 100), sum(v[0] for v in comp13.values()) / 100)
linha("Saída realizada", *[comp13[m][1] / 100 for m, _ in meses_13], round(sum(v[1] for v in comp13.values()) / n13 / 100), sum(v[1] for v in comp13.values()) / 100)
linha("Resultado do mês", *[(comp13[m][0] + comp13[m][1]) / 100 for m, _ in meses_13], round((sum(v[0] for v in comp13.values()) + sum(v[1] for v in comp13.values())) / n13 / 100), (sum(v[0] for v in comp13.values()) + sum(v[1] for v in comp13.values())) / 100, bold=True, fill=True)

sec(f"2. Comparativo 13 meses — Caixa/Pagamento (sem CC {CC_EXCLUIDO})")
linha("Mês", *[lab for _, lab in meses_13], "Média", "Total", bold=True, fill=True)
linha("Entrada realizada", *[comp13c[m][0] / 100 for m, _ in meses_13], round(sum(v[0] for v in comp13c.values()) / n13 / 100), sum(v[0] for v in comp13c.values()) / 100)
linha("Saída realizada", *[comp13c[m][1] / 100 for m, _ in meses_13], round(sum(v[1] for v in comp13c.values()) / n13 / 100), sum(v[1] for v in comp13c.values()) / 100)
linha("Resultado do mês", *[(comp13c[m][0] + comp13c[m][1]) / 100 for m, _ in meses_13], round((sum(v[0] for v in comp13c.values()) + sum(v[1] for v in comp13c.values())) / n13 / 100), (sum(v[0] for v in comp13c.values()) + sum(v[1] for v in comp13c.values())) / 100, bold=True, fill=True)

def dre_excel(titulo, tx, regime="caixa"):
    sec(titulo)
    valores = defaultdict(lambda: [0, 0]); n_por = defaultdict(lambda: [0, 0])
    for t in tx:
        cid = cat_id(t)
        if cid is None: continue
        v = t["value_in_cent"] if regime == "comp" else valor_efetivo(t)
        valores[cid][0 if v > 0 else 1] += v; n_por[cid][0 if v > 0 else 1] += 1
    com_mov = {cid for cid, (e, s) in valores.items() if e or s}
    linha("Categoria", "Lançamentos", "Entradas", "Saídas", "Resultado", bold=True, fill=True)
    tot_e = tot_s = 0
    for pai in sorted(pais_ordem, key=_cod):
        tem = False
        for _s in sorted(by_parent.get(pai["id"], []), key=_cod):
            if _s["id"] in com_mov:
                tem = True; e, s = valores[_s["id"]]
                linha("   " + _s.get("ds_category"), n_por[_s["id"]][0] + n_por[_s["id"]][1], e / 100, s / 100, (e + s) / 100)
        if pai["id"] in com_mov:
            tem = True; e, s = valores[pai["id"]]
            linha(pai.get("ds_category"), n_por[pai["id"]][0] + n_por[pai["id"]][1], e / 100, s / 100, (e + s) / 100, bold=True)
        if tem: tot_e += valores[pai["id"]][0]; tot_s += valores[pai["id"]][1]
    linha("Total", sum(x[0] + x[1] for x in n_por.values()), tot_e / 100, tot_s / 100, (tot_e + tot_s) / 100, bold=True, fill=True)

dre_excel(f"3. Receitas e Despesas — Competência (sem CC {CC_EXCLUIDO})", sem_hnsc(mes_tx), regime="comp")
dre_excel(f"4. Receitas e Despesas — Caixa/Pagamento (sem CC {CC_EXCLUIDO})", sem_hnsc(mes_tx))
sec("5. Fluxo de Caixa — mês anterior (caixa)")
linha("Descrição", "Valor", bold=True, fill=True)
linha("Saldo inicial", saldo_ini_mes_ant / 100)
linha("(+) Entradas (baixas do mês)", bal_e / 100)
linha("(−) Saídas (baixas do mês)", bal_s / 100)
linha("Saldo final", saldo_fim_mes_ant / 100, bold=True, fill=True)
dre_excel(f"6. Previsão — Competência (pagos + não pagos, sem CC {CC_EXCLUIDO})", sem_hnsc(prev_completa), regime="comp")
dre_excel(f"7. Previsão — Caixa/Pagamento (pagos + não pagos, sem CC {CC_EXCLUIDO})", sem_hnsc(prev_completa))
sec("8. Previsão de Fluxo de Caixa — mês atual")
linha("Descrição", "Valor", bold=True, fill=True)
linha(f"Saldo inicial ({FIM_MES.strftime('%d/%m')})", saldo_fim_mes_ant / 100)
linha("(+) Entradas do mês (realizado + previsto)", tot_rec_p / 100)
linha("(−) Saídas do mês (realizado + previsto)", tot_desp_p / 100)
linha("Saldo final projetado", (saldo_fim_mes_ant + tot_rec_p + tot_desp_p) / 100, bold=True, fill=True)
for cc_nome in ["LARISSA", "MICHELLE"]:
    dre_excel(f"9. Receitas e Despesas — CC {cc_nome} — Competência", [t for t in mes_tx if tem_cc(t, cc_nome)], regime="comp")
for tag in TAGS_CLIENTE:
    tx_tag = [t for t in mes_tx if tag in tag_names(t)]
    if tx_tag:
        dre_excel(f"10. Receitas e Despesas — Tag {tag} — Competência", tx_tag, regime="comp")
sec(f"11. Saldo nas Contas — {FIM_MES.strftime('%d/%m/%Y')}")
linha("Conta", "Saldo", bold=True, fill=True)
for c in contas:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={FIM_MES.isoformat()}&id_account_main={c['id']}")["results"]
    linha(c.get("ds_account") or "", b["balanceDone"] / 100)
linha("Total", saldo_fim_mes_ant / 100, bold=True, fill=True)
ws.column_dimensions["A"].width = 42
for col in range(2, 20):
    ws.column_dimensions[get_column_letter(col)].width = 14
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
