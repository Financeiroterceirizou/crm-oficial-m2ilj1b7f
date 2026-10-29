#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# INDICADORES MENSAIS — REDE SOS SC NORTE — v1.0, 2026-10-29 (pedido Vinícius)
#   1 folha por ano (2026; jan/2027 = folha nova). 3 blocos: RECEITAS · DESPESAS · INDICADORES.
#   Regime de CAIXA (dt_billing + valor pago; sit 1,2), sem transferências entre contas.
#   Meses não fechados (cutoff dia 05) ficam em branco.
# Uso: python3 indicadores_rede_sos.py [ano]
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from PIL import Image as PILImage
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_REDE_SOS") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c"); LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a"); FUNDO_HDR = colors.HexColor("#e8e8e8")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO_REDE = os.path.join(_dir, "logo-rede.jpg")
LOGO_TZ = os.path.join(_dir, "logo-terceirizou.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
MES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
          7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# ===== categorias-raiz do plano REDE SOS (ids) =====
REC_VENDAS = 9210751        # Receitas de Vendas e de Serviços
REC_DIRETORIA = 9275261     # Receita com Diretoria (Aporte do Sócios)
REC_FINANCEIRAS = 9210752   # Receitas Financeiras (Rendimentos de Aplicações)
IMP_VENDAS = 9210754        # Impostos sobre Vendas e sobre Serviços
DESP_ADM = 9210759          # Despesas Administrativas
DESP_COLAB = 9210758        # Despesas com Colaboradores
DESP_DIRETORIA = 9210762    # Despesas com Diretoria (Pró-Labore, Distribuição)
DESP_VEIC = 9210761         # Despesas com Veículos
DESP_COM = 9210765          # Despesas Comerciais e com marketing
DESP_FIN = 9210763          # Despesas Financeiras
EMPREST = 9210766           # Empréstimos e Financiamentos
PARCEL = 9210767            # Parcelamentos e Dívidas
ENT_EMPREST = 10504474      # Entrada de Empréstimos
TRANSF_CONTAS = 9210898     # Transferencia entre Contas (fora de tudo)

def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items():
                r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 409) and i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            raise

def tx_list(start, end):
    out, page = [], 1
    while True:
        tl = req(f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
                 f"&page={page}&orderBy=date&orderByCardinality=ASC").get("results", {}).get("transactionsList", [])
        out.extend(tl)
        if len(tl) < 100:
            return out
        page += 1

def bdate(t):
    return (t.get("dt_billing") or t.get("dt_due") or "")[:10]

def valor_efetivo(t):
    """Valor real de caixa: pago (sit 1,2) usa payment_in_cent; pendente usa value_in_cent."""
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]

# ===== árvore do plano de contas: cada subcategoria → sua categoria-raiz =====
def carregar_plano():
    plano = [p for p in req(f"{BASE}/plan-account/v1/planAccountsEntities").get("results", [])
             if p.get("status") == 1]
    by_id = {p["id"]: p for p in plano}
    raiz_de = {}
    def sobe(pid):
        vistos = set()
        while pid is not None and pid in by_id and pid not in vistos:
            vistos.add(pid)
            pai = by_id[pid].get("id_plan_accounts_parent")
            if pai is None:
                return pid
            pid = pai
        return pid
    for p in plano:
        raiz_de[p["id"]] = sobe(p["id"])
    return plano, by_id, raiz_de

PLANO, BY_ID, RAIZ_DE = carregar_plano()

def raiz(cid):
    """Id da categoria-raiz de uma categoria (se ela já é raiz, retorna ela mesma)."""
    return RAIZ_DE.get(cid, cid)

def nome_cat(cid):
    p = BY_ID.get(cid)
    return (p or {}).get("ds_category") or str(cid)

def cats_de(t):
    return [c.get("id_category") for c in (t.get("apportionments_plan_account") or [])]

def eh_transf(t):
    return TRANSF_CONTAS in {raiz(c) for c in cats_de(t) if c is not None}

# ===== parâmetros =====
HOJE = date.today()
if len(sys.argv) > 1:
    ANOS = [int(sys.argv[1])]
else:
    ANOS = list(range(2026, HOJE.year + 1))

# ===== dados: um único fetch largo =====
INI = f"{ANOS[0]}-01-01"
FIM = HOJE.isoformat()
tx_todos = tx_list(INI, FIM)
pagos = [t for t in tx_todos if t.get("situation") in (1, 2) and not eh_transf(t)]

# valores por categoria-raiz × mês (caixa): {(ano, mes): {cat_id: centavos}}
por_cat = defaultdict(lambda: defaultdict(int))
for t in pagos:
    d = bdate(t)
    if not d: continue
    ano, mes = int(d[:4]), int(d[5:7])
    v = valor_efetivo(t)
    for cid in {raiz(c) for c in cats_de(t) if c is not None}:
        por_cat[(ano, mes)][cid] += v

def serie(ano, cat_id):
    """Série mensal (jan→dez) de uma categoria-raiz no ano informado."""
    return [por_cat[(ano, m)].get(cat_id, 0) for m in range(1, 13)]

def fim_mes(ano, m):
    return (date(ano, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

# ===== estilos =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=12.5, textColor=PRETO, spaceAfter=1)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica", fontSize=6.8,
                     textColor=colors.HexColor("#777777"), spaceAfter=2)
bt = ParagraphStyle("bt", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=5.9, leading=6.8)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", fontSize=6.4)
cellch = ParagraphStyle("cellch", parent=cellh, alignment=1)
P = Paragraph

def fmt_int(cents):
    v = int(round(cents / 100))
    return ("-" if v < 0 else "") + f"{abs(v):,}".replace(",", ".")

def P_val(cents, style, bold=False):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    if bold: s.fontName = "Helvetica-Bold"
    return P(fmt_int(cents), s)

def rodape(canvas, doc_):
    pg = canvas.getPageNumber()
    canvas.saveState()
    if os.path.exists(SIMBOLO):
        try:
            w0, h0 = PILImage.open(SIMBOLO).size
            canvas.drawImage(SIMBOLO, 1.0 * cm, 0.55 * cm, width=0.5 * cm,
                             height=0.5 * cm * h0 / w0, mask="auto")
        except Exception:
            pass
    canvas.setFont("Helvetica", 6.5); canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawRightString(landscape(A4)[0] - 1.0 * cm, 0.7 * cm, f"Página {pg}")
    canvas.restoreState()

# ===== monta as linhas por ano =====
def blocos_do_ano(ano):
    """Retorna (receitas, despesas, indicadores) — cada item: (label, [12 valores], tipo)."""
    rec_op = serie(ano, REC_VENDAS)
    rec_dir = serie(ano, REC_DIRETORIA)
    rec_fin = serie(ano, REC_FINANCEIRAS)
    imp = serie(ano, IMP_VENDAS)
    adm = serie(ano, DESP_ADM)
    colab = serie(ano, DESP_COLAB)
    diret = serie(ano, DESP_DIRETORIA)
    veic = serie(ano, DESP_VEIC)
    com = serie(ano, DESP_COM)
    dfin = serie(ano, DESP_FIN)
    emp = serie(ano, EMPREST)
    parc = serie(ano, PARCEL)
    ent_emp = serie(ano, ENT_EMPREST)
    invest = [0] * 12  # não há categoria de investimento no plano da REDE (lacuna sinalizada)

    rec = [("Receitas de Vendas e de Serviços", rec_op, "rec"),
           ("Receita com Diretoria", rec_dir, "rec"),
           ("Receitas Financeiras", rec_fin, "rec")]
    desp = [("Impostos sobre Vendas e sobre Serviços", imp, "desp"),
            ("Despesas Administrativas", adm, "desp"),
            ("Despesas com Colaboradores", colab, "desp"),
            ("Despesas com Diretoria", diret, "desp"),
            ("Despesas com Veículos", veic, "desp"),
            ("Despesas Comerciais e com marketing", com, "desp"),
            ("Despesas Financeiras", dfin, "desp"),
            ("Empréstimos e Financiamentos", emp, "desp"),
            ("Parcelamentos e Dívidas", parc, "desp")]

    despesas_op = [imp[i] + adm[i] + colab[i] + veic[i] + com[i] + dfin[i] + parc[i] for i in range(12)]
    res_op = [rec_op[i] + despesas_op[i] for i in range(12)]
    # Resultado Financeiro (fórmula do Vinícius): Res. Operacional + Aportes + Juros + Entrada de
    # Empréstimos − Investimentos − Saída de Empréstimos − Despesas Financeiras.
    # Valores já vêm com sinal: saídas negativas. "Diminuir" uma saída = somar o valor negativo.
    res_fin = [res_op[i] + rec_dir[i] + rec_fin[i] + ent_emp[i] + invest[i] + emp[i] + dfin[i]
               for i in range(12)]
    ind = [("Receitas Operacionais", rec_op, "res_rec"),
           ("Despesas Operacionais", despesas_op, "res"),
           ("Resultado Operacional", res_op, "res"),
           ("Aportes", rec_dir, "moeda"),
           ("Juros Aplicação Financeira", rec_fin, "moeda"),
           ("Entrada de Empréstimos", ent_emp, "moeda"),
           ("Investimentos", invest, "moeda"),
           ("Saída de Empréstimos", emp, "moeda"),
           ("Despesas Financeiras", dfin, "moeda"),
           ("Resultado Financeiro", res_fin, "res")]
    return rec, desp, ind

def corta(vals, ano):
    """Zera (None) os meses não fechados: cutoff dia 05 do mês seguinte."""
    out = []
    for m, v in enumerate(vals, start=1):
        if date(ano, m, 1) > HOJE:      # mês futuro
            out.append(None)
        elif HOJE < fim_mes(ano, m) + timedelta(days=5):   # mês não fechado
            out.append(None)
        else:
            out.append(v)
    return out

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_RedeSOS_{ANOS[-1]}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=landscape(A4), leftMargin=0.9 * cm, rightMargin=0.9 * cm,
                        topMargin=0.8 * cm, bottomMargin=0.9 * cm,
                        title=f"Indicadores Gerenciais — Rede SOS SC Norte {ANOS[-1]}")
E = []

for idx_ano, ano in enumerate(ANOS):
    if idx_ano > 0:
        E.append(PageBreak())
    # cabeçalho com as 2 logos
    logos = []
    if os.path.exists(LOGO_REDE):
        w0, h0 = PILImage.open(LOGO_REDE).size
        logos.append(RLImage(LOGO_REDE, width=2.0 * cm, height=2.0 * cm * h0 / w0))
    if os.path.exists(LOGO_TZ):
        wt, ht = PILImage.open(LOGO_TZ).size
        logos.append(RLImage(LOGO_TZ, width=3.6 * cm, height=3.6 * cm * ht / wt))
    if logos:
        t_cab = Table([logos], colWidths=[landscape(A4)[0] / len(logos)] * len(logos))
        t_cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        E.append(t_cab)
        E.append(Spacer(1, 0.15 * cm))
    E.append(P("<b>REDE SOS SC NORTE — Indicadores Gerenciais</b>", h1))
    E.append(P(f"Ano {ano} · Gerado em {HOJE.strftime('%d/%m/%Y')} · Fonte: Controlle "
               f"· Terceirizou — mais do que terceirizar o financeiro", sub))

    rec, desp, ind = blocos_do_ano(ano)
    BLOCOS = [("RECEITAS", [(lb, corta(v, ano), tp) for lb, v, tp in rec], "#fdf0e8"),
              ("DESPESAS", [(lb, corta(v, ano), tp) for lb, v, tp in desp], "#f4f7f4"),
              ("INDICADORES", [(lb, corta(v, ano), tp) for lb, v, tp in ind], "#f6f3ed")]

    CW = [5.0 * cm] + [1.68 * cm] * 12 + [1.9 * cm]
    rows = [[P("<b>Indicador</b>", cellh)] + [P(f"<b>{MES_PT[m][:3]}</b>", cellch) for m in range(1, 13)]
            + [P("<b>Total</b>", cellch)]]
    faixas = []   # (linha_ini, linha_fim, cor)
    linha = 1
    for titulo, defs, fundo in BLOCOS:
        F = colors.HexColor(fundo)
        rows.append([P(f"<b>{titulo}</b>", ParagraphStyle(f"bt{titulo}", parent=cellb, fontSize=7.6,
                                                           textColor=PRETO))] + [P("", cellc)] * 13)
        faixas.append((linha, linha, F))
        linha += 1
        ini_bloco = linha
        for label, vals, tipo in defs:
            bold = tipo in ("res", "res_rec")
            row = [P(label, cellb if bold else cell)]
            tot = 0
            tem = False
            for v in vals:
                if v is None:
                    row.append(P("", cellrb if bold else cellr))
                else:
                    tem = True
                    tot += v
                    row.append(P_val(v, cellrb if bold else cellr, bold))
            row.append(P_val(tot, cellrb, True) if tem else P("", cellrb))
            rows.append(row)
            linha += 1
        faixas.append((ini_bloco, linha - 1, F))

    t = Table(rows, colWidths=CW, repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), FUNDO_HDR),
              ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9d9d9")),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
              ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5)]
    for ini, fim, F in faixas:
        estilo.append(("BACKGROUND", (0, ini), (-1, fim), F))
    t.setStyle(TableStyle(estilo))
    E.append(t)

doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_RedeSOS_{ANOS[-1]}.xlsx"
wb = Workbook()
for idx_ano, ano in enumerate(ANOS):
    ws = wb.active if idx_ano == 0 else wb.create_sheet(f"{ano}")
    ws.title = str(ano)
    ws.append((f"REDE SOS SC NORTE — Indicadores Gerenciais — {ano} (regime de caixa)",))
    ws["A1"].font = Font(bold=True, size=12)
    rec, desp, ind = blocos_do_ano(ano)
    BLOCOS = [("RECEITAS", [(lb, corta(v, ano), tp) for lb, v, tp in rec], "FDF0E8"),
              ("DESPESAS", [(lb, corta(v, ano), tp) for lb, v, tp in desp], "F4F7F4"),
              ("INDICADORES", [(lb, corta(v, ano), tp) for lb, v, tp in ind], "F6F3ED")]
    for titulo, defs, cor in BLOCOS:
        ws.append(("",))
        ws.append((titulo,))
        r = ws.max_row
        ws.cell(row=r, column=1).font = Font(bold=True, size=10.5, color="FF501C")
        ws.append(("Indicador", *[MES_PT[m][:3] for m in range(1, 13)], "Total"))
        r = ws.max_row
        for c in range(1, 15):
            cell_ = ws.cell(row=r, column=c)
            cell_.font = Font(bold=True)
            cell_.fill = PatternFill("solid", fgColor="E8E8E8")
            cell_.alignment = Alignment(horizontal="center" if c > 1 else "left")
        for label, vals, tipo in defs:
            tot = sum(v for v in vals if v is not None)
            ws.append((label, *[(None if v is None else round(v / 100, 2)) for v in vals], round(tot / 100, 2)))
            r = ws.max_row
            for c in range(1, 15):
                cell_ = ws.cell(row=r, column=c)
                cell_.fill = PatternFill("solid", fgColor=cor)
                if c > 1:
                    cell_.number_format = "#,##0"
                    cell_.alignment = Alignment(horizontal="right")
                if tipo in ("res", "res_rec"):
                    cell_.font = Font(bold=True)
    ws.column_dimensions["A"].width = 40
    for col in range(2, 15):
        ws.column_dimensions[get_column_letter(col)].width = 10
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
