#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# INDICADORES MENSAIS — SUPORTE PROTEÇÃO VEICULAR — v1.0, 2026-10-30 (pedido Vinícius)
#   Licença Controlle da UNILAGES (mesma licença, outra entidade fiscal).
#   1 folha por ano (2026; jan/2027 = folha nova). 3 blocos: RECEITAS · DESPESAS · INDICADORES.
#   Regime de CAIXA (dt_billing + valor pago), transferências entre contas fora.
# Uso: python3 indicadores_suporte.py [ano]
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
TOKEN = os.environ.get("CONTROLLE_TOKEN_SUPORTE") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
PRETO = colors.HexColor("#1a1a1a"); FUNDO_HDR = colors.HexColor("#e8e8e8")
VERDE = colors.HexColor("#1a7f37"); VERMELHO = colors.HexColor("#c0392b")
LOGO_SUP = os.path.join(_dir, "logo-suporte.png")
LOGO_TZ = os.path.join(_dir, "logo-terceirizou.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")
MES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
          7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# ===== categorias-raiz do plano SUPORTE (ids) =====
# receitas
R01 = 10220849   # 01 RECEITAS
R02F = 10220962  # 02 RECEITA FINANCEIRA
R03 = 10491134   # 03 ENTRADA DE EMPRESTIMOS, FINANCIAMENTOS E INVESTIDORES
R04 = 10491135   # 04 APORTE DOS SOCIOS
R05 = 10491136   # 05 RECEITA DE EVENTOS
R06 = 10491138   # 06 VENDA DE SALVADOS
R9902 = 10270815  # 99.02 - Estorno Baixa Boleto
RDEVTED = None    # "DEVOLUCAO TED" não existe no plano (linha fica zerada; lacuna sinalizada)

# despesas
D02 = 10220863   # 02 DEDUÇÕES DAS RECEITAS
D10 = 10220867   # 10 RH SALARIOS/FOLHA
D11 = 10491438   # 11 RH TRIBUTOS
D12 = 10491441   # 12 RH COM PESSOAL
D13 = 10491444   # 13 RH RESCISÕES
D14 = 10491445   # 14 RH BENEFÍCIOS
D15 = 10492901   # 15 OUTRAS RH
D20 = 10220887   # 20 ADM FUNCIONAMENTO
D21 = 10496717   # 21 ADM MANUTENÇÃO
D22 = 10496718   # 22 ADM IMOBILIZADOS
D23 = 10496719   # 23 OUTRAS ADM
D24 = 10496720   # 24 ADM VIAGEM
D25 = 10496721   # 25 OUTRAS ADM NÃO MENCIONADAS
D30 = 10496736   # 30 COMERCIAIS COMISSIONAMENTO
D31 = 10220931   # 31 COMERCIAIS PREMIOS
D32 = 10496737   # 32 COMERCIAIS OPERAÇÃO
D40 = 10496740   # 40 MARKETING PUBLICIDADE
D41 = 10220954   # 41 MARKETING GERAL
D42 = 10496744   # 42 MARKETING SERVIÇOS DE TERCEIROS
D50 = 10220940   # 50 EVENTOS RATEAVEIS
D51 = 10509471   # 51 EVENTOS NÃO RATEÁVEIS
D52 = 10496741   # 52 EVENTOS RASTREAMENTO
D53 = 10509477   # 53 EVENTOS ASSISTÊNCIA 24H
D54 = 10509478   # 54 EVENTOS COM PRODUTOS
D55 = 10509714   # 55 EVENTO A IDENTIFICAR
D60 = 10220957   # 60 INVESTIMENTOS FINANCEIROS
D61 = 10220967   # 61 DESPESA FINANCEIRA
D90 = 10220973   # 90 DISTRIBUICAO DE RESULTADOS
D96 = 10220983   # 96 SAIDAS DE EMPRESTIMOS
TRANSF = {10220988, 10491428, 10221133, 10221134}   # transferências entre contas (fora)

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
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]

def carregar_plano():
    plano = [p for p in req(f"{BASE}/plan-account/v1/planAccountsEntities").get("results", [])
             if p.get("status") == 1]
    by_id = {p["id"]: p for p in plano}
    raiz_de = {}
    for p in plano:
        cid, vistos = p["id"], set()
        while cid in by_id and by_id[cid].get("id_plan_accounts_parent") and cid not in vistos:
            vistos.add(cid)
            cid = by_id[cid]["id_plan_accounts_parent"]
        raiz_de[p["id"]] = cid
    return by_id, raiz_de

BY_ID, RAIZ_DE = carregar_plano()

def raiz(cid):
    return RAIZ_DE.get(cid, cid)

def cats_raiz(t):
    return {raiz(c.get("id_category")) for c in (t.get("apportionments_plan_account") or [])
            if c.get("id_category")}

def eh_transf(t):
    ids = cats_raiz(t)
    return bool(ids) and ids <= TRANSF

HOJE = date.today()
ANOS = [int(sys.argv[1])] if len(sys.argv) > 1 else list(range(2026, HOJE.year + 1))

tx_todos = tx_list(f"{ANOS[0]}-01-01", HOJE.isoformat())
pagos = [t for t in tx_todos if t.get("situation") in (1, 2) and not eh_transf(t)]

por_cat = defaultdict(lambda: defaultdict(int))
for t in pagos:
    d = bdate(t)
    if not d: continue
    ano, mes = int(d[:4]), int(d[5:7])
    v = valor_efetivo(t)
    for cid in cats_raiz(t):
        if cid is not None:
            por_cat[(ano, mes)][cid] += v

def serie(ano, cat_id):
    if cat_id is None:
        return [0] * 12
    return [por_cat[(ano, m)].get(cat_id, 0) for m in range(1, 13)]

def fim_mes(ano, m):
    return (date(ano, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

# ===== estilos =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=12.5, textColor=PRETO, spaceAfter=1)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica", fontSize=6.8,
                     textColor=colors.HexColor("#777777"), spaceAfter=2)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=5.7, leading=6.6)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", fontSize=6.2)
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
    canvas.saveState()
    if os.path.exists(SIMBOLO):
        try:
            w0, h0 = PILImage.open(SIMBOLO).size
            canvas.drawImage(SIMBOLO, 1.0 * cm, 0.5 * cm, width=0.48 * cm,
                             height=0.48 * cm * h0 / w0, mask="auto")
        except Exception:
            pass
    canvas.setFont("Helvetica", 6.5); canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawRightString(landscape(A4)[0] - 1.0 * cm, 0.65 * cm, f"Página {doc_.page}")
    canvas.restoreState()

def corta(vals, ano):
    out = []
    for m, v in enumerate(vals, start=1):
        if date(ano, m, 1) > HOJE:
            out.append(None)
        elif HOJE < fim_mes(ano, m) + timedelta(days=5):
            out.append(None)
        else:
            out.append(v)
    return out

def blocos_do_ano(ano):
    r01 = serie(ano, R01); r02 = serie(ano, R02F); r03 = serie(ano, R03)
    r04 = serie(ano, R04); r05 = serie(ano, R05); r06 = serie(ano, R06)
    r9902 = serie(ano, R9902); rdev = serie(ano, RDEVTED)

    d = {k: serie(ano, k) for k in (D02, D10, D11, D12, D13, D14, D15, D20, D21, D22, D23, D24,
                                    D25, D30, D31, D32, D40, D41, D42, D50, D51, D52, D53, D54,
                                    D55, D60, D61, D90, D96)}

    rec = [("01 RECEITAS", r01, "rec"),
           ("02 RECEITA FINANCEIRA", r02, "rec"),
           ("03 ENTRADA DE EMPRÉSTIMOS, FINANCIAMENTOS E INVESTIDORES", r03, "rec"),
           ("04 APORTE DOS SÓCIOS", r04, "rec"),
           ("05 RECEITA DE EVENTOS", r05, "rec"),
           ("06 VENDA DE SALVADOS", r06, "rec"),
           ("99.02 - Estorno Baixa Boleto", r9902, "rec"),
           ("DEVOLUÇÃO TED", rdev, "rec")]

    desp = [("02 DEDUÇÕES DAS RECEITAS", d[D02], "desp"),
            ("10 DESPESAS DE RH - SALÁRIOS / FOLHA DE PAGAMENTO", d[D10], "desp"),
            ("11 DESPESAS DE RH - TRIBUTOS", d[D11], "desp"),
            ("12 DESPESAS DE RH - COM PESSOAL", d[D12], "desp"),
            ("13 DESPESAS DE RH - COM RESCISÕES", d[D13], "desp"),
            ("14 DESPESAS DE RH - COM BENEFÍCIOS", d[D14], "desp"),
            ("15 OUTRAS DESPESAS DE RH", d[D15], "desp"),
            ("20 DESPESAS ADMINISTRATIVAS - DE FUNCIONAMENTO", d[D20], "desp"),
            ("21 DESPESAS ADMINISTRATIVAS - COM MANUTENÇÃO", d[D21], "desp"),
            ("22 DESPESAS ADMINISTRATIVAS - COM IMOBILIZADOS", d[D22], "desp"),
            ("23 OUTRAS DESPESAS ADMINISTRATIVAS", d[D23], "desp"),
            ("24 DESPESAS ADMINISTRATIVAS - COM VIAGEM", d[D24], "desp"),
            ("25 OUTRAS DESPESAS ADMINISTRATIVAS NÃO MENCIONADAS", d[D25], "desp"),
            ("30 DESPESAS COMERCIAIS - COM COMISSIONAMENTO", d[D30], "desp"),
            ("31 DESPESAS COMERCIAIS - COM PRÊMIOS", d[D31], "desp"),
            ("32 DESPESAS COMERCIAIS - OPERAÇÃO COMERCIAL", d[D32], "desp"),
            ("40 DESPESAS MARKETING - COM PUBLICIDADE", d[D40], "desp"),
            ("41 DESPESA MARKETING GERAL", d[D41], "desp"),
            ("42 DESPESA MARKETING - COM SERVIÇOS DE TERCEIROS", d[D42], "desp"),
            ("50 DESPESAS DE EVENTOS RATEÁVEIS", d[D50], "desp"),
            ("51 DESPESAS DE EVENTOS NÃO RATEÁVEIS", d[D51], "desp"),
            ("52 DESPESA DE EVENTO COM RASTREAMENTO E MONITORAMENTO", d[D52], "desp"),
            ("53 DESPESAS DE EVENTOS COM ASSISTÊNCIA 24 HORAS", d[D53], "desp"),
            ("54 DESPESAS DE EVENTOS COM PRODUTOS", d[D54], "desp"),
            ("55 DESPESAS DE EVENTO A IDENTIFICAR", d[D55], "desp"),
            ("90 DISTRIBUIÇÃO DE RESULTADOS", d[D90], "desp")]

    # indicadores
    rec_op = [r01[i] + r05[i] + r06[i] for i in range(12)]
    desp_cats = [d[k] for k in (D02, D10, D11, D12, D13, D14, D15, D20, D21, D22, D23, D24, D25,
                                D30, D31, D32, D40, D41, D42, D50, D51, D52, D53, D54, D55, D61)]
    desp_op = [sum(c[i] for c in desp_cats) for i in range(12)]
    res_op = [rec_op[i] + desp_op[i] for i in range(12)]
    aportes = r04
    juros = r02
    ent_emp = r03
    invest = d[D60]
    sai_emp = d[D96]
    desp_fin = d[D61]
    res_fin = [res_op[i] + aportes[i] + juros[i] + ent_emp[i] + invest[i] + sai_emp[i] + desp_fin[i]
               for i in range(12)]

    ind = [("Receitas Operacionais", rec_op, "res_rec"),
           ("Despesas Operacionais", desp_op, "res"),
           ("Resultado Operacional", res_op, "res"),
           ("Aportes", aportes, "moeda"),
           ("Juros Aplicação Financeira", juros, "moeda"),
           ("Entrada de Empréstimos", ent_emp, "moeda"),
           ("Investimentos", invest, "moeda"),
           ("Saída de Empréstimos", sai_emp, "moeda"),
           ("Despesas Financeiras", desp_fin, "moeda"),
           ("Resultado Financeiro", res_fin, "res")]
    return rec, desp, ind

ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_Suporte_{ANOS[-1]}.pdf"
doc = SimpleDocTemplate(ARQ_PDF, pagesize=landscape(A4), leftMargin=0.9 * cm, rightMargin=0.9 * cm,
                        topMargin=0.8 * cm, bottomMargin=0.9 * cm,
                        title=f"Indicadores Gerenciais — Suporte Proteção Veicular {ANOS[-1]}")
E = []
for idx_ano, ano in enumerate(ANOS):
    if idx_ano > 0:
        E.append(PageBreak())
    logos = []
    if os.path.exists(LOGO_SUP):
        w0, h0 = PILImage.open(LOGO_SUP).size
        logos.append(RLImage(LOGO_SUP, width=4.4 * cm, height=4.4 * cm * h0 / w0))
    if os.path.exists(LOGO_TZ):
        wt, ht = PILImage.open(LOGO_TZ).size
        logos.append(RLImage(LOGO_TZ, width=3.6 * cm, height=3.6 * cm * ht / wt))
    if logos:
        t_cab = Table([logos], colWidths=[landscape(A4)[0] / len(logos)] * len(logos))
        t_cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        E.append(t_cab)
        E.append(Spacer(1, 0.15 * cm))
    E.append(P("<b>SUPORTE PROTEÇÃO VEICULAR — Indicadores Gerenciais</b>", h1))
    E.append(P(f"Ano {ano} · Gerado em {HOJE.strftime('%d/%m/%Y')} · Fonte: Controlle "
               f"· Terceirizou — mais do que terceirizar o financeiro", sub))

    rec, desp, ind = blocos_do_ano(ano)
    BLOCOS = [("RECEITAS", [(lb, corta(v, ano), tp) for lb, v, tp in rec], "#fdf0e8"),
              ("DESPESAS", [(lb, corta(v, ano), tp) for lb, v, tp in desp], "#f4f7f4"),
              ("INDICADORES", [(lb, corta(v, ano), tp) for lb, v, tp in ind], "#f6f3ed")]

    CW = [7.4 * cm] + [1.42 * cm] * 12 + [1.5 * cm]
    rows = [[P("<b>Indicador</b>", cellh)] + [P(f"<b>{MES_PT[m][:3]}</b>", cellch) for m in range(1, 13)]
            + [P("<b>Total</b>", cellch)]]
    faixas = []
    linha = 1
    for titulo, defs, fundo in BLOCOS:
        F = colors.HexColor(fundo)
        rows.append([P(f"<b>{titulo}</b>", ParagraphStyle(f"bt{titulo}", parent=cellb, fontSize=7.4,
                                                           textColor=PRETO))] + [P("", cellc)] * 13)
        faixas.append((linha, linha, F))
        linha += 1
        ini_bloco = linha
        for label, vals, tipo in defs:
            bold = tipo in ("res", "res_rec")
            row = [P(label, cellb if bold else cell)]
            tot, tem = 0, False
            for v in vals:
                if v is None:
                    row.append(P("", cellrb if bold else cellr))
                else:
                    tem = True; tot += v
                    row.append(P_val(v, cellrb if bold else cellr, bold))
            row.append(P_val(tot, cellrb, True) if tem else P("", cellrb))
            rows.append(row)
            linha += 1
        faixas.append((ini_bloco, linha - 1, F))

    t = Table(rows, colWidths=CW, repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), FUNDO_HDR),
              ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9d9d9")),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 1.4), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
              ("LEFTPADDING", (0, 0), (-1, -1), 2.2), ("RIGHTPADDING", (0, 0), (-1, -1), 2.2)]
    for ini, fim, F in faixas:
        estilo.append(("BACKGROUND", (0, ini), (-1, fim), F))
    t.setStyle(TableStyle(estilo))
    E.append(t)

doc.build(E, onFirstPage=rodape, onLaterPages=rodape)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Indicadores_Suporte_{ANOS[-1]}.xlsx"
wb = Workbook()
for idx_ano, ano in enumerate(ANOS):
    ws = wb.active if idx_ano == 0 else wb.create_sheet(f"{ano}")
    ws.title = str(ano)
    ws.append((f"SUPORTE PROTEÇÃO VEICULAR — Indicadores Gerenciais — {ano} (regime de caixa)",))
    ws["A1"].font = Font(bold=True, size=12)
    rec, desp, ind = blocos_do_ano(ano)
    BLOCOS = [("RECEITAS", [(lb, corta(v, ano), tp) for lb, v, tp in rec], "FDF0E8"),
              ("DESPESAS", [(lb, corta(v, ano), tp) for lb, v, tp in desp], "F4F7F4"),
              ("INDICADORES", [(lb, corta(v, ano), tp) for lb, v, tp in ind], "F6F3ED")]
    for titulo, defs, cor in BLOCOS:
        ws.append(("",))
        ws.append((titulo,))
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=10.5, color="FF501C")
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
    ws.column_dimensions["A"].width = 52
    for col in range(2, 15):
        ws.column_dimensions[get_column_letter(col)].width = 10
wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
