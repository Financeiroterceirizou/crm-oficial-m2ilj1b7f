#!/usr/bin/env python3
# DRE GERENCIAL MENSAL — UNILAGES (por CENTRO DE CUSTO) — v1.0, 2026-10-22 (pedido Vinícius)
#   Dia 04 de cada mês: DRE do mês anterior (regime de caixa) com entradas e saídas por
#   categoria (ordem do plano de contas) + Despesas Detalhadas + Resultado 12m + Fluxo 30 dias.
#   CCs: CORREIA PINTO, CURITIBANOS, LAGES+BM ADM (agrupados), OTACILIO COSTA, SAO JOAQUIM,
#   URUBICI + GERAL. Envio SÓ henrique@terceirizou.com.br.
# Uso: python3 dre_unilages_cc.py [YYYY-MM-DD-geracao] [YYYY-MM-ref] [cc]
import json, os, sys, urllib.request, time, http.client
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
TOKEN = os.environ.get("CONTROLLE_TOKEN_UNILAGES") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c"); LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a"); CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-unilages.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}

CCS = {
    "correia_pinto": (170560, "CORREIA PINTO"),
    "curitibanos":   (170563, "CURITIBANOS"),
    "lages_bm_adm":  ([170559, 170812], "LAGES + BM ADM"),
    "otacilio_costa":(170561, "OTACILIO COSTA"),
    "sao_joaquim":   (170564, "SAO JOAQUIM"),
    "urubici":       (170562, "URUBICI"),
}
_cc = sys.argv[3] if len(sys.argv) > 3 else "geral"
if _cc == "geral":
    CC_IDS, CC_NOME, ARQ_TAG = None, "GERAL (todos os centros de custo)", "Geral"
else:
    _ids, _nome = CCS[_cc]
    CC_IDS, CC_NOME = (_ids if isinstance(_ids, list) else [_ids]), _nome
    ARQ_TAG = _cc

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
        except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, OSError) as e:
            if i < tries - 1:
                time.sleep(5 * (i + 1)); continue
            raise

def tx_list(start, end, min_esperado=0):
    """Pagina até página vazia (a API às vezes devolve página curta sem erro — instabilidade).
    Se min_esperado informado e não atingido, refaz tudo."""
    for tentativa in range(3):
        out, page, vazia = [], 1, False
        while not vazia:
            tl = req(f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
                     f"&page={page}&orderBy=date&orderByCardinality=ASC").get("results", {}).get("transactionsList", [])
            out.extend(tl)
            if not tl:
                vazia = True
            page += 1
            if page > 200:
                break
        if len(out) >= min_esperado:
            return out
        time.sleep(5 * (tentativa + 1))
    return out

def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s

def bdate(t): return (t.get("dt_billing") or t.get("dt_due") or "")[:10]
def cat_id(t):
    cats = t.get("apportionments_plan_account") or []
    return cats[0].get("id_category") if cats else None
def cat_nome(t):
    cats = t.get("apportionments_plan_account") or []
    return (cats[0].get("ds_category") or "(sem categoria)") if cats else "(sem categoria)"
def eh_99(t):
    return any((c.get("ds_category") or "").startswith("99.01") or (c.get("ds_category") or "").lower().startswith("transferencia")
               for c in (t.get("apportionments_plan_account") or []))
def tem_cc(t):
    if CC_IDS is None: return True
    ids = {c.get("cost_center_id") for c in (t.get("apportionments_cost_center") or [])}
    return bool(ids & set(CC_IDS))

HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_REF = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date(HOJE.year, HOJE.month, 1) - timedelta(days=1)
FIM_MES = (MES_REF.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
HOJE_LABEL = HOJE.strftime("%d/%m/%Y")

# ===== plano de contas (ordem) =====
_plano = req(f"{BASE}/plan-account/v1/planAccountsEntities").get("results", [])
_plano_ativos = [p for p in _plano if p.get("status") == 1]
_pai_de = {}
for p in _plano_ativos:
    if p.get("id_plan_accounts_parent"):
        _pai_de[p["id"]] = p["id_plan_accounts_parent"]
by_parent = defaultdict(list)
for p in _plano_ativos:
    if p.get("id_plan_accounts_parent"):
        by_parent[p["id_plan_accounts_parent"]].append(p)
pais_ordem = [p for p in _plano_ativos if not p.get("id_plan_accounts_parent")]

# ===== lançamentos do mês no CC =====
_tx = tx_list(MES_REF.replace(day=1).isoformat(), FIM_MES.isoformat(), min_esperado=300)
mes_tx = [t for t in _tx if t.get("situation") in (1, 2) and tem_cc(t) and not eh_99(t)]

# DRE por categoria (agrupada no PAI — entradas e saídas por categoria)
valores = defaultdict(lambda: [0, 0])  # cat_id → [entradas, saídas] (valor direto do pai)
n_por_cat = defaultdict(lambda: [0, 0])
for t in mes_tx:
    cid = cat_id(t)
    if cid is None: continue
    pai = _pai_de.get(cid, cid)
    v = t["value_in_cent"]
    idx = 0 if v > 0 else 1
    valores[pai][idx] += v
    n_por_cat[pai][idx] += 1
com_mov = {cid for cid, (e, s) in valores.items() if e or s}

# ordenar: pais na ordem do plano, filhos com movimento abaixo
def _cod(nome):
    import re
    m = re.match(r"(\d+)", nome or "")
    return int(m.group(1)) if m else 999
linhas = []
for pai in sorted(pais_ordem, key=lambda p: _cod(p.get("ds_category"))):
    if pai["id"] in com_mov:
        e, s = valores[pai["id"]]
        linhas.append(("cat", pai.get("ds_category"), e + s, n_por_cat[pai["id"]][0] + n_por_cat[pai["id"]][1]))
# categorias com movimento fora do plano ativo
ids_no_plano = {p["id"] for p in pais_ordem}
for cid in sorted(com_mov - ids_no_plano, key=lambda x: valores[x][0] + valores[x][1]):
    e, s = valores[cid]
    linhas.append(("cat", "(categoria fora do plano ativo)", e + s, n_por_cat[cid][0] + n_por_cat[cid][1]))

tot_rec = sum(e for cid, (e, s) in valores.items() if e > 0)
tot_desp = sum(s for cid, (e, s) in valores.items() if s < 0)
resultado = tot_rec + tot_desp

# ===== resultado 12 meses + fluxo 30 dias =====
def _add_m(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)
INI_12 = _add_m(MES_REF, -11)
meses_12 = []
for i in range(0, 12):
    ini_m = _add_m(INI_12, i)
    fim_m = _add_m(ini_m, 1) - timedelta(days=1)
    _lab = ini_m.strftime("%b").lower()
    _lab = {"jan":"jan","feb":"fev","mar":"mar","apr":"abr","may":"mai","jun":"jun","jul":"jul","aug":"ago","sep":"set","oct":"out","nov":"nov","dec":"dez"}[_lab]
    meses_12.append((ini_m.isoformat()[:7], f"{_lab}/{str(ini_m.year)[2:]}"))
_tx12 = tx_list(f"{INI_12.year}-01-01", f"{MES_REF.year + 1}-12-31", min_esperado=5000)
tx_cc12 = [t for t in _tx12 if t.get("situation") in (1, 2) and tem_cc(t) and not eh_99(t)]
comp12 = {m: [0, 0] for m, _ in meses_12}
for t in tx_cc12:
    m = bdate(t)[:7]
    if m in comp12:
        v = t["value_in_cent"]
        comp12[m][0 if v > 0 else 1] += v
tot12_e = sum(v[0] for v in comp12.values())
tot12_s = sum(v[1] for v in comp12.values())
res12 = tot12_e + tot12_s
MES_COR = _add_m(MES_REF, 1)
FIM_COR = MES_COR.replace(day=28) + timedelta(days=4)
FIM_COR = FIM_COR - timedelta(days=FIM_COR.day)
MES_SEG = _add_m(MES_REF, 2)
FIM_SEG = MES_SEG.replace(day=28) + timedelta(days=4)
FIM_SEG = FIM_SEG - timedelta(days=FIM_SEG.day)
_tx_fc = tx_list(MES_COR.isoformat(), FIM_SEG.isoformat())
fc_cor = [t for t in _tx_fc if bdate(t)[:7] == MES_COR.isoformat()[:7] and tem_cc(t) and not eh_99(t)]
fc_seg = [t for t in _tx_fc if bdate(t)[:7] == MES_SEG.isoformat()[:7] and tem_cc(t) and not eh_99(t)]
fc_cor_e = sum(t["value_in_cent"] for t in fc_cor if t["value_in_cent"] > 0)
fc_cor_s = sum(t["value_in_cent"] for t in fc_cor if t["value_in_cent"] < 0)
fc_seg_e = sum(t["value_in_cent"] for t in fc_seg if t["value_in_cent"] > 0)
fc_seg_s = sum(t["value_in_cent"] for t in fc_seg if t["value_in_cent"] < 0)

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=PRETO, spaceAfter=1)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceBefore=12, spaceAfter=3)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, spaceBefore=10, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#777777"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph
def P_val(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(brl(cents), s)
def tabela(rows, widths, fs=8):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONTNAME", (0,0), (-1,-1), "Helvetica"), ("FONTSIZE", (0,0), (-1,-1), fs),
          ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
          ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
          ("BACKGROUND", (0,0), (-1,0), LARANJA), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
          ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
          ("LINEBELOW", (0,-1), (-1,-1), 0.7, LARANJA)]
    t.setStyle(TableStyle(st))
    return t
def rodape_simbolo(canvas, doc):
    if os.path.exists(SIMBOLO):
        alt = 1.2 * cm
        canvas.drawImage(SIMBOLO, 18.4*cm, 1.1*cm, width=alt*372/553, height=alt, mask="auto")

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_DRE_Unilages_{ARQ_TAG}_{MES_REF.strftime('%Y%m')}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm,
                        topMargin=1.3*cm, bottomMargin=1.6*cm,
                        title=f"DRE Gerencial — Unilages {CC_NOME} — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year}")
E = []
if os.path.exists(LOGO):
    from PIL import Image as PILImage
    w0, h0 = PILImage.open(LOGO).size
    img = RLImage(LOGO, width=5*cm, height=5*cm*h0/w0)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 8))
E.append(P("<b>UNILAGES — DRE GERENCIAL</b>", ParagraphStyle("h1c", parent=h1, alignment=1)))
E.append(P(CC_NOME, ParagraphStyle("h2c", parent=h2, alignment=1, spaceBefore=2, spaceAfter=2)))
E.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · Ref.: {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} — regime de caixa · Categorias na ordem do plano de contas", ParagraphStyle("subc", parent=sub, alignment=1, spaceAfter=0)))
E.append(Spacer(1, 6))

dre_rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
for tipo, nome, v, n in linhas:
    dre_rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
dre_rows.append([P("<b>Total de Receitas</b>", cellrb), P(f"<b>{sum(n2[0] for n2 in n_por_cat.values())}</b>", cellc), P_val(tot_rec, cellrb, True)])
dre_rows.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n2[1] for n2 in n_por_cat.values())}</b>", cellc), P_val(tot_desp, cellrb, True)])
dre_rows.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{len(mes_tx)}</b>", cellc), P_val(resultado, cellrb, True)])
t = tabela(dre_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(dre_rows)-3), (-1,len(dre_rows)-1), LARANJA_CLARO)]))
E.append(t)

# ===== Despesas detalhadas =====
E.append(PageBreak())
E.append(P(f"Despesas Detalhadas — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regime de caixa)", h2))
desp_tx = sorted([t for t in mes_tx if t["value_in_cent"] < 0], key=bdate)
por_cat_d = defaultdict(list)
for t in desp_tx:
    por_cat_d[cat_nome(t)].append(t)
for cat in sorted(por_cat_d):
    txs_c = sorted(por_cat_d[cat], key=bdate)
    rows = [[P("<b>Data</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell), P("<b>Valor</b>", cellr)]]
    for t in txs_c:
        d = bdate(t)
        rows.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell), P((t.get("ds_transaction") or "")[:70], cell),
                     P(t.get("ds_account_main") or "", cell), P_val(t["value_in_cent"], cellr)])
    rows.append([P("<b>Total</b>", cellrb), P(f"<b>{cat}</b>", cellrb), P(f"<b>{len(txs_c)}</b>", cellc), P_val(sum(t["value_in_cent"] for t in txs_c), cellrb)])
    tt = tabela(rows, [2.2*cm, 8.3*cm, 3.5*cm, 3*cm])
    tt.setStyle(TableStyle([("BACKGROUND", (0,len(rows)-1), (-1,len(rows)-1), LARANJA_CLARO)]))
    E.append(KeepTogether([P(f"<b>{cat}</b>", h3), tt]))
tot_d = sum(t["value_in_cent"] for t in desp_tx)
td_rows = [[P("<b>Total de Despesas do mês</b>", cellrb), P(f"<b>{len(desp_tx)}</b>", cellc), P_val(tot_d, cellrb, True)]]
t = tabela(td_rows, [11*cm, 2.5*cm, 3*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), LARANJA_CLARO)]))
E.append(t)

# ===== Resultado dos últimos 12 meses =====
E.append(PageBreak())
E.append(P(f"Resultado dos Últimos 12 Meses — {meses_12[0][1]} a {meses_12[-1][1]} (regime de caixa)", h2))
rs_rows = [[P("<b>Mês</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)]]
for m, lab in meses_12:
    e_m, s_m = comp12[m]
    rs_rows.append([P(lab, cell), P_val(e_m, cellr), P_val(s_m, cellr), P_val(e_m + s_m, cellrb)])
rs_rows.append([P("<b>Resultado 12 meses</b>", cellrb), P_val(tot12_e, cellrb, True), P_val(tot12_s, cellrb, True), P_val(res12, cellrb, True)])
t = tabela(rs_rows, [3*cm, 4.3*cm, 4.3*cm, 4.4*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(rs_rows)-1), (-1,len(rs_rows)-1), LARANJA_CLARO)]))
E.append(t)

# ===== Fluxo de Caixa — mês corrente e mês seguinte =====
E.append(Spacer(1, 18))
E.append(P("Fluxo de Caixa — Previsibilidade 30 dias (regime de caixa)", h2))
fc_rows = [[P("<b>Período</b>", cell), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Resultado</b>", cellr)],
           [P(f"{MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)", cell), P_val(fc_cor_e, cellr), P_val(fc_cor_s, cellr), P_val(fc_cor_e + fc_cor_s, cellrb)],
           [P(f"{MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (previsto)", cell), P_val(fc_seg_e, cellr), P_val(fc_seg_s, cellr), P_val(fc_seg_e + fc_seg_s, cellrb)]]
t = tabela(fc_rows, [6*cm, 3.7*cm, 3.7*cm, 3.6*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,len(fc_rows)-2), (-1,len(fc_rows)-1), LARANJA_CLARO)]))
E.append(t)

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
doc.build(E, onFirstPage=rodape_simbolo, onLaterPages=rodape_simbolo)
print(f"OK: {ARQ_PDF}")

# ===== Excel (por execução: DRE + Detalhe + Resultado 12m + Fluxo) =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_DRE_Unilages_{ARQ_TAG}_{MES_REF.strftime('%Y%m')}.xlsx"
wb = Workbook()
ws = wb.active
ws.title = ("DRE " + MES_REF.strftime("%m%y"))[:31]
ws.append((f"DRE Gerencial — Unilages {CC_NOME} — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regime de caixa)",))
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
c = ws.cell(row=1, column=1)
c.font = Font(bold=True, size=12, color="FF501C")
c.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 22
ws.append(("Categoria", "Lançamentos", "Valor"))
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
for cc in ws[2]:
    cc.fill = FILL_H
    cc.font = FH
    cc.alignment = Alignment(horizontal="center", vertical="center")
for tipo, nome, v, n in linhas:
    ws.append((nome, n, v / 100))
ws.append(("Total de Receitas", sum(n2[0] for n2 in n_por_cat.values()), tot_rec / 100))
ws.append(("Total de Despesas", sum(n2[1] for n2 in n_por_cat.values()), tot_desp / 100))
ws.append(("Resultado do mês", len(mes_tx), resultado / 100))
for r in range(ws.max_row - 2, ws.max_row + 1):
    for cc in ws[r]:
        cc.font = Font(bold=True)
        cc.fill = FILL_T
for row in ws.iter_rows(min_row=3):
    cc = row[2]
    if isinstance(cc.value, (int, float)):
        cc.number_format = '"R$" #,##0.00'
        cc.font = Font(bold=bool(row[0].font and row[0].font.bold),
                       color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
    if isinstance(row[1].value, (int, float)):
        row[1].number_format = "0"
ws.column_dimensions["A"].width = 50
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 16
ws.freeze_panes = "A3"

ws2 = wb.create_sheet(("Detalhe Despesas " + MES_REF.strftime("%m%y"))[:31])
ws2.append((f"Despesas Detalhadas — Unilages {CC_NOME} — {MES_PT[MES_REF.month].capitalize()} de {MES_REF.year} (regime de caixa)",))
ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
c2 = ws2.cell(row=1, column=1)
c2.font = Font(bold=True, size=12, color="FF501C")
c2.alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 22
ws2.append(("Categoria", "Data", "Descrição", "Conta", "Valor"))
for cc in ws2[2]:
    cc.fill = FILL_H
    cc.font = FH
for cat in sorted(por_cat_d):
    for t in sorted(por_cat_d[cat], key=bdate):
        d = bdate(t)
        ws2.append((cat, f"{d[8:10]}/{d[5:7]}/{d[:4]}", (t.get("ds_transaction") or "")[:60], t.get("ds_account_main") or "", t["value_in_cent"] / 100))
ws2.append(("TOTAL", "", "", "", tot_d / 100))
for cc in ws2[ws2.max_row]:
    cc.font = FB
    cc.fill = FILL_T
for row in ws2.iter_rows(min_row=3):
    cc = row[4]
    if isinstance(cc.value, (int, float)):
        cc.number_format = '"R$" #,##0.00'
        cc.font = Font(bold=bool(row[0].font and row[0].font.bold),
                       color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
for col, w in zip("ABCDE", (40, 12, 55, 24, 16)):
    ws2.column_dimensions[col].width = w
ws2.freeze_panes = "A3"

ws3 = wb.create_sheet("Resultado 12 meses")
ws3.append((f"Resultado dos Últimos 12 Meses — {CC_NOME} (regime de caixa)",))
ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
c3 = ws3.cell(row=1, column=1)
c3.font = Font(bold=True, size=12, color="FF501C")
c3.alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[1].height = 22
ws3.append(("Mês", "Entradas", "Saídas", "Resultado"))
for cc in ws3[2]:
    cc.fill = FILL_H
    cc.font = FH
    cc.alignment = Alignment(horizontal="center", vertical="center")
for m, lab in meses_12:
    ws3.append((lab, comp12[m][0] / 100, comp12[m][1] / 100, (comp12[m][0] + comp12[m][1]) / 100))
ws3.append(("Resultado 12 meses", tot12_e / 100, tot12_s / 100, res12 / 100))
for r in range(ws3.max_row, ws3.max_row + 1):
    for cc in ws3[r]:
        cc.font = Font(bold=True)
        cc.fill = FILL_T
for row in ws3.iter_rows(min_row=3):
    for cc in row[1:]:
        if isinstance(cc.value, (int, float)):
            cc.number_format = '"R$" #,##0.00'
            cc.font = Font(bold=bool(row[0].font and row[0].font.bold),
                           color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
for col, w in zip("ABCD", (14, 18, 18, 18)):
    ws3.column_dimensions[col].width = w
ws3.freeze_panes = "A3"

ws4 = wb.create_sheet("Fluxo 30 dias")
ws4.append((f"Fluxo de Caixa — Previsibilidade 30 dias — {CC_NOME} (regime de caixa)",))
ws4.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
c4 = ws4.cell(row=1, column=1)
c4.font = Font(bold=True, size=12, color="FF501C")
c4.alignment = Alignment(horizontal="center", vertical="center")
ws4.row_dimensions[1].height = 22
ws4.append(("Período", "Entradas", "Saídas", "Resultado"))
for cc in ws4[2]:
    cc.fill = FILL_H
    cc.font = FH
    cc.alignment = Alignment(horizontal="center", vertical="center")
ws4.append((f"{MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)", fc_cor_e / 100, fc_cor_s / 100, (fc_cor_e + fc_cor_s) / 100))
ws4.append((f"{MES_PT[MES_SEG.month].capitalize()} de {MES_SEG.year} (previsto)", fc_seg_e / 100, fc_seg_s / 100, (fc_seg_e + fc_seg_s) / 100))
for r in range(ws4.max_row - 1, ws4.max_row + 1):
    for cc in ws4[r]:
        cc.font = Font(bold=True)
        cc.fill = FILL_T
for row in ws4.iter_rows(min_row=3):
    for cc in row[1:]:
        if isinstance(cc.value, (int, float)):
            cc.number_format = '"R$" #,##0.00'
            cc.font = Font(bold=True, color=(VERDE_XL if cc.value > 0 else VERMELHO_XL if cc.value < 0 else "1A1A1A"))
for col, w in zip("ABCD", (34, 18, 18, 18)):
    ws4.column_dimensions[col].width = w
ws4.freeze_panes = "A3"
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
