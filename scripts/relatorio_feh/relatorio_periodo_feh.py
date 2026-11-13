#!/usr/bin/env python3
# FRATERNIDADE E HARMONIA — relatório de PERÍODO (01/10/2026 a 12/11/2026), separado por centro de custo.
# Uso: python3 relatorio_periodo_feh.py [INI=2026-10-01] [FIM=2026-11-12]
#
# 5 blocos pedidos pelo Vinícius (12/11):
#   1. valor arrecadado no período, total por categoria, por CC
#   2. pagamentos realizados no período, total por categoria, por CC + os 3 mais expressivos
#   3. valores a receber em atraso até a data final: SÓ quantidade de devedores e valor de cada um
#      (nunca o nome do contato)
#   4. saldo nas contas, por CC
#   5. saldo do Tronco de Solidariedade, por CC
#
# Regras da casa aplicadas: negativo em vermelho, A4 limpo, matrizes sem "R$" e com centavos
# arredondados; saldos com centavos (precisam reconciliar); logo e títulos centralizados.
import json, os, sys, urllib.request, urllib.error, http.client, time
from collections import defaultdict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image as RLImage, KeepTogether, PageBreak)

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-terceirizou.png")
LOGO_FEH = os.path.join(_dir, "logo-feh.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")

INI = sys.argv[1] if len(sys.argv) > 1 else "2026-10-01"
FIM = sys.argv[2] if len(sys.argv) > 2 else "2026-11-12"
CC_FEH, CC_FIL = 170068, 170069
NOMES_CC = {CC_FEH: "F e H", CC_FIL: "FILOSÓFICO"}


def req(url, tries=5):
    """Retry em falha de rede: a API do Controlle corta a conexão no meio com frequência."""
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items():
                r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504) and i < tries - 1:
                time.sleep(3 * (i + 1)); continue
            raise
        except (urllib.error.URLError, http.client.IncompleteRead, ConnectionError,
                TimeoutError, OSError):
            if i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            raise


def tx_list(start, end):
    """Pagina até a página VAZIA. Parar em len < 100 perde lançamento em silêncio."""
    out, page = [], 1
    while True:
        url = (f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
               f"&page={page}&orderBy=date&orderByCardinality=ASC")
        tl = req(url).get("results", {}).get("transactionsList", [])
        if not tl:
            return out
        out.extend(tl)
        page += 1


def bdate(t):
    return (t.get("dt_billing") or t.get("dt_due") or "")[:10]


def cc_de(t):
    """Centro de custo do lançamento. Sem CC = saldo de abertura = F e H (decisão Vinícius 04/11)."""
    ids = {a.get("cost_center_id") for a in (t.get("apportionments_cost_center") or [])}
    return CC_FIL if CC_FIL in ids else CC_FEH


def cat_de(t):
    c = t.get("apportionments_plan_account") or []
    return (c[0].get("ds_category") if c else "(sem categoria)")


def eh_transferencia(t):
    for c in (t.get("apportionments_plan_account") or []):
        if (c.get("ds_category") or "").startswith("99.01"):
            return True
    return (t.get("ds_transaction") or "").upper().startswith("TRANSFERÊNCIA")


# ===== dados =====
bruto = tx_list("2017-01-01", "2026-12-31")
# dedup pela chave de PAGAMENTO: o mesmo id_transactions pode vir 2x quando há baixa parcial
# (cada baixa tem id_transactions_payments próprio). Dedup só por id perderia uma das parcelas.
vistos, tudo = set(), []
for t in bruto:
    k = (t["id_transactions"], t.get("id_transactions_payments"))
    if k in vistos:
        continue
    vistos.add(k)
    tudo.append(t)

periodo = [t for t in tudo if INI <= bdate(t) <= FIM and t.get("situation") in (1, 2)
           and not eh_transferencia(t)]

rec = defaultdict(lambda: defaultdict(int))
desp = defaultdict(lambda: defaultdict(int))
for t in periodo:
    v = t["value_in_cent"]
    (rec if v > 0 else desp)[cc_de(t)][cat_de(t)] += v

# três pagamentos mais expressivos de cada CC
top3 = {}
for cc in (CC_FEH, CC_FIL):
    top3[cc] = sorted([t for t in periodo if cc_de(t) == cc and t["value_in_cent"] < 0],
                      key=lambda x: x["value_in_cent"])[:3]

# atrasados: receita pendente com vencimento até a data final (todas as competências)
atras = [t for t in tudo if t.get("situation") == 0 and t["value_in_cent"] > 0
         and not eh_transferencia(t) and (t.get("dt_due") or "")[:10] <= FIM]
devedores = {}
for cc in (CC_FEH, CC_FIL):
    g = [t for t in atras if cc_de(t) == cc]
    d = defaultdict(int)
    for t in g:
        d[t.get("id_contacts") or ("sem contato " + str(t["id_transactions"]))] += t["value_in_cent"]
    devedores[cc] = (len(g), sorted(d.values(), reverse=True))

# saldos nas contas por CC (situação 1,2 pela data de caixa)
hist = [t for t in tudo if t.get("situation") in (1, 2)]
contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
saldos = []
for c in contas:
    nome = c["ds_account"]
    do_cc = {cc: sum(t["value_in_cent"] for t in hist
                     if bdate(t) <= FIM and t.get("ds_account_main") == nome and cc_de(t) == cc)
             for cc in (CC_FEH, CC_FIL)}
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01"
            f"&end_date={FIM}&id_account_main={c['id']}")["results"]
    saldos.append((nome, do_cc[CC_FEH], do_cc[CC_FIL], b["balanceDone"]))

# trava: a alocação por CC tem de fechar com o balanceDone de cada conta
for nome, feh, fil, real in saldos:
    if abs((feh + fil) - real) > 1:
        raise SystemExit(f"ABORTADO: {nome} alocação {(feh+fil)/100:,.2f} != balanceDone {real/100:,.2f}")

# Tronco de Solidariedade (tag), por CC
TRONCO = {CC_FEH: "TRONCO DE SOLIDARIEDADE F e H", CC_FIL: "TRONCO DE SOLIDARIEDADE FILOSÓFICO"}
tronco = {}
for cc, tag in TRONCO.items():
    g = [t for t in tudo if any((x.get("ds_tag") or "").upper() == tag.upper()
                                for x in (t.get("array_tags") or []))]
    tronco[cc] = (sum(t["value_in_cent"] for t in g if t["value_in_cent"] > 0),
                  sum(t["value_in_cent"] for t in g if t["value_in_cent"] < 0),
                  sum(t["value_in_cent"] for t in g), len(g))

# ===== estilos =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=12, textColor=PRETO,
                    alignment=1, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, textColor=LARANJA,
                    spaceBefore=14, spaceAfter=4)
subc = ParagraphStyle("subc", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8,
                      textColor=colors.HexColor("#777777"), alignment=1, spaceAfter=6)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8,
                     textColor=colors.HexColor("#777777"), spaceBefore=2, spaceAfter=6)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph


def pnum(cents, style, centavos=False):
    """Valor formatado. Negativo em vermelho (regra da casa)."""
    v = cents / 100
    if centavos:
        s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        s = f"{abs(round(v)):,}".replace(",", ".")
    if v < 0:
        s = "-" + s
    cor = VERMELHO if v < 0 else PRETO
    return P(s, ParagraphStyle("v", parent=style, textColor=cor))


def tabela(rows, widths, fs=8.5, vpad=4):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), fs),
          ("TOPPADDING", (0, 0), (-1, -1), vpad), ("BOTTOMPADDING", (0, 0), (-1, -1), vpad),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BACKGROUND", (0, 0), (-1, 0), LARANJA), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("LINEBELOW", (0, -1), (-1, -1), 0.7, LARANJA)]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), CINZA))
    t.setStyle(TableStyle(st))
    return t


def rodape(canvas, doc):
    if os.path.exists(SIMBOLO):
        alt = 1.2 * cm
        lar = alt * 372 / 553
        canvas.drawImage(SIMBOLO, canvas._pagesize[0] - 1.5 * cm - lar, 1.1 * cm,
                         width=lar, height=alt, mask="auto")


_ml = _mr = 1.6 * cm
_mt, _mb = 1.3 * cm, 1.6 * cm
frame = Frame(_ml, _mb, A4[0] - _ml - _mr, A4[1] - _mt - _mb,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

DIA = FIM[8:10] + "/" + FIM[5:7] + "/" + FIM[:4]
INI_L = INI[8:10] + "/" + INI[5:7] + "/" + INI[:4]
ARQ = f"artifacts/261112_Relatorio_Feh_Periodo_{INI[8:10]}Out_{FIM[8:10]}Nov.pdf"
doc = BaseDocTemplate(ARQ, pagesize=A4, leftMargin=_ml, rightMargin=_mr,
                      topMargin=_mt, bottomMargin=_mb,
                      title="Fraternidade e Harmonia - Relatório do Período")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=rodape)])

E = []
# ---- cabeçalho ----
_imgs, _cel, _lar = [], [], []
for _p, _w in ((LOGO_FEH, 2.2 * cm), (LOGO, 3.2 * cm)):
    if os.path.exists(_p):
        _im = RLImage(_p, width=_w, height=_w * (1 if _p == LOGO_FEH else 561 / 1600))
        if _cel:
            _cel.append(""); _lar.append(1.0 * cm)
        _cel.append(_im); _lar.append(_im.drawWidth)
        _imgs.append(_im)
if _cel:
    cab = Table([_cel], colWidths=_lar)
    cab.hAlign = "CENTER"
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 0),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    E.append(cab)
E.append(Spacer(1, 6))
E.append(P("FRATERNIDADE E HARMONIA", h1))
E.append(P(f"Movimentação de {INI_L} a {DIA}, por centro de custo", subc))

# ---- 1. arrecadação ----
E.append(P("1. Valores arrecadados", h2))
E.append(P(f"Recebimentos de {INI_L} a {DIA}, total por categoria. Valores em reais, "
           f"sem centavos.", sub))
cats_rec = sorted(set(c for cc in (CC_FEH, CC_FIL) for c in rec[cc]))
r = [[P("<b>Categoria</b>", cell), P("<b>F e H</b>", cellr),
      P("<b>FILOSÓFICO</b>", cellr), P("<b>Total</b>", cellr)]]
tot = [0, 0]
for cat in cats_rec:
    a, b = rec[CC_FEH].get(cat, 0), rec[CC_FIL].get(cat, 0)
    tot[0] += a; tot[1] += b
    r.append([P(cat, cell), pnum(a, cellr) if a else P("", cellr),
              pnum(b, cellr) if b else P("", cellr), pnum(a + b, cellrb)])
r.append([P("<b>Total arrecadado</b>", cellb), pnum(tot[0], cellrb), pnum(tot[1], cellrb),
          pnum(tot[0] + tot[1], cellrb)])
t = tabela(r, [8.2 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm])
t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 1), (-1, len(r) - 1), LARANJA_CLARO)]))
E.append(t)

# ---- 2. pagamentos ----
E.append(P("2. Pagamentos realizados", h2))
E.append(P(f"Pagamentos de {INI_L} a {DIA}, total por categoria. Valores em reais, "
           f"sem centavos.", sub))
cats_desp = sorted(set(c for cc in (CC_FEH, CC_FIL) for c in desp[cc]))
r = [[P("<b>Categoria</b>", cell), P("<b>F e H</b>", cellr),
      P("<b>FILOSÓFICO</b>", cellr), P("<b>Total</b>", cellr)]]
tot = [0, 0]
for cat in cats_desp:
    a, b = desp[CC_FEH].get(cat, 0), desp[CC_FIL].get(cat, 0)
    tot[0] += a; tot[1] += b
    r.append([P(cat, cell), pnum(a, cellr) if a else P("", cellr),
              pnum(b, cellr) if b else P("", cellr), pnum(a + b, cellrb)])
r.append([P("<b>Total pago</b>", cellb), pnum(tot[0], cellrb), pnum(tot[1], cellrb),
          pnum(tot[0] + tot[1], cellrb)])
t = tabela(r, [8.2 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm])
t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 1), (-1, len(r) - 1), LARANJA_CLARO)]))
E.append(t)

E.append(P("2.1 Os três pagamentos mais expressivos", ParagraphStyle(
    "h3", parent=h2, fontSize=9.5, spaceBefore=10, spaceAfter=3)))
r = [[P("<b>Data</b>", cell), P("<b>Descrição</b>", cell), P("<b>Categoria</b>", cell),
      P("<b>Centro de custo</b>", cell), P("<b>Valor</b>", cellr)]]
for cc in (CC_FEH, CC_FIL):
    for t_ in top3[cc]:
        d = bdate(t_)
        r.append([P(f"{d[8:10]}/{d[5:7]}/{d[:4]}", cell),
                  P((t_.get("ds_transaction") or "")[:52], cell), P(cat_de(t_), cell),
                  P(NOMES_CC[cc], cell), pnum(t_["value_in_cent"], cellr)])
t = tabela(r, [2.2 * cm, 5.7 * cm, 4.3 * cm, 3.0 * cm, 2.6 * cm], vpad=3)   # soma = 17,8 cm (útil)
E.append(KeepTogether([t]))
E.append(P("No centro de custo FILOSÓFICO houve um único pagamento no período, já listado acima. "
           "Valores em reais, sem centavos.", sub))

# ---- 3. atrasados ----
_h3 = [P("3. Valores a receber em atraso", h2)]
_h3.append(P(f"Mensalidades pendentes com vencimento até {DIA}, em qualquer competência. "
           f"Os contatos não são identificados: consta apenas a quantidade de devedores e o "
           f"valor de cada um. Valores em reais, sem centavos.", sub))
E.append(PageBreak())
E.append(KeepTogether(_h3))
for cc in (CC_FEH, CC_FIL):
    n_lanc, vals = devedores[cc]
    r = [[P(f"<b>Devedor</b>", cell), P("<b>Valor</b>", cellr)]]
    for i, v in enumerate(vals, 1):
        r.append([P(f"Devedor {i}", cell), pnum(v, cellr)])
    r.append([P(f"<b>Total</b>", cellb), pnum(sum(vals), cellrb)])
    tt = tabela(r, [7.0 * cm, 4.0 * cm], vpad=3)
    tt.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 1), (-1, len(r) - 1), LARANJA_CLARO)]))
    E.append(KeepTogether([P(f"<b>{NOMES_CC[cc]}: {len(vals)} devedores, "
                             f"{n_lanc} lançamentos em atraso</b>",
                             ParagraphStyle("mini", parent=cellb, spaceBefore=6, spaceAfter=3)),
                           tt]))
_tot_atraso = sum(sum(devedores[cc][1]) for cc in (CC_FEH, CC_FIL)) / 100
_tot_fmt = f"{_tot_atraso:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
E.append(P(f"Total em atraso até {DIA}: "
           f"{len(devedores[CC_FEH][1]) + len(devedores[CC_FIL][1])} devedores, "
           f"R$ {_tot_fmt}", sub))

# ---- 4. saldos nas contas ----
E.append(P("4. Saldos nas contas", h2))
r = [[P("<b>Conta</b>", cell), P("<b>F e H</b>", cellr),
      P("<b>FILOSÓFICO</b>", cellr), P("<b>Total</b>", cellr)]]
s_tot = [0, 0, 0]
for nome, feh, fil, real in saldos:
    if real == 0 and feh == 0 and fil == 0:
        continue                      # conta zerada, fora da peça
    s_tot[0] += feh; s_tot[1] += fil; s_tot[2] += real
    r.append([P(nome, cell), pnum(feh, cellr, True) if feh else P("", cellr),
              pnum(fil, cellr, True) if fil else P("", cellr), pnum(real, cellrb, True)])
r.append([P("<b>Total</b>", cellb), pnum(s_tot[0], cellrb, True), pnum(s_tot[1], cellrb, True),
          pnum(s_tot[2], cellrb, True)])
t = tabela(r, [7.0 * cm, 3.6 * cm, 3.6 * cm, 4.2 * cm])
t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 1), (-1, len(r) - 1), LARANJA_CLARO)]))
E.append(t)
E.append(P(f"Saldo em {DIA}, com centavos. A conta inicial e a conta do Tronco de Solidariedade "
           f"estão zeradas: todo o movimento do período passou pela conta CORA.", sub))

# ---- 5. tronco ----
E.append(P("5. Saldo do Tronco de Solidariedade", h2))
r = [[P("<b>Item</b>", cell), P("<b>F e H</b>", cellr),
      P("<b>FILOSÓFICO</b>", cellr), P("<b>Total</b>", cellr)]]
ent = [tronco[CC_FEH][0], tronco[CC_FIL][0]]
sai = [tronco[CC_FEH][1], tronco[CC_FIL][1]]
sal = [tronco[CC_FEH][2], tronco[CC_FIL][2]]
r.append([P("Entradas (desde a abertura)", cell), pnum(ent[0], cellr), pnum(ent[1], cellr),
          pnum(ent[0] + ent[1], cellr)])
r.append([P("Saídas (desde a abertura)", cell), pnum(sai[0], cellr), pnum(sai[1], cellr),
          pnum(sai[0] + sai[1], cellr)])
r.append([P(f"<b>Saldo em {DIA}</b>", cellb), pnum(sal[0], cellrb), pnum(sal[1], cellrb),
          pnum(sal[0] + sal[1], cellrb)])
t = tabela(r, [7.0 * cm, 3.6 * cm, 3.6 * cm, 4.2 * cm])
t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 1), (-1, len(r) - 1), LARANJA_CLARO)]))
E.append(t)
E.append(P("Movimentações identificadas pela tag do Tronco de Solidariedade em cada centro de "
           "custo, de todas as competências. Valores em reais, sem centavos.", sub))

E.append(Spacer(1, 12))
E.append(P("terceirizou · dados do Controlle", sub))
doc.build(E)
print(f"OK: {ARQ}")
print(f"  arrecadado F eH {sum(rec[CC_FEH].values())/100:,.2f} | FIL {sum(rec[CC_FIL].values())/100:,.2f}")
print(f"  pago F eH {sum(desp[CC_FEH].values())/100:,.2f} | FIL {sum(desp[CC_FIL].values())/100:,.2f}")
print(f"  atraso F eH {sum(devedores[CC_FEH][1])/100:,.2f} | FIL {sum(devedores[CC_FIL][1])/100:,.2f}")
