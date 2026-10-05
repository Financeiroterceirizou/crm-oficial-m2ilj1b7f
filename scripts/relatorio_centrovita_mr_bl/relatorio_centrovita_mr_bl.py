#!/usr/bin/env python3
# Relatório Mensal — CENTROVITA MAURO RAMOS + BARRA DA LAGOA (ILPI, sócio Henrique) — licença CENTROVITA MAURO RAMOS
# v1.2, 2026-10-04 (últimos ajustes de layout do Vinícius)
#   v1.2: pág 1 = PAISAGEM com capa compacta + banda MR + comparativo 13m + Receitas e Despesas do
#     mês anterior juntos; KeepTogether em todos os relatórios (nenhum quebra no meio; se não couber,
#     o relatório inteiro vai para a página seguinte); NOVO relatório 6 "Projeção de Fluxo de Caixa —
#     Próximos 12 Meses" por CC (MR, BL) + CONSOLIDADO (lançamentos previstos por CC, saldo de partida
#     = saldo real em 30/09; consolidado fecha exato com o balancePreview da API); Excel: resultado
#     previsto do mês nas abas de previsão + abas "Proj fluxo 12m" (MR/BL/consolidado).
#   v1.1: capa compacta, comparativo em paisagem, título "Previsão de Receitas e Despesas", fluxo por CC.
#   v1.0: pacote único (filtro por CC + consolidado).
# Uso: python3 relatorio_centrovita_mr_bl.py [YYYY-MM-DD]  (default: hoje; relatórios do MES_ANT)
# Estrutura do PDF único (13 páginas):
#   PÁG 1 (paisagem) — capa compacta + MAURO RAMOS: 1. Comparativo 13 meses (competência) +
#     2. Receitas e Despesas do mês anterior (competência)
#   MR: 3. Previsão de Receitas e Despesas do mês corrente · 4. Fluxo de Caixa 13m realizado (por CC) ·
#     5. Saldo nas contas · 6. Projeção de Fluxo de Caixa 12m
#   BARRA DA LAGOA (CC 157107): mesmos 6 relatórios
#   CONSOLIDADO: 2 + 3 + 5 + 6 das duas unidades somadas
# Contas (mapeamento Vinícius 04/10):
#   BARRA DA LAGOA → Cora Barra da Lagoa (213167) + Banco Inter Barra da Lagoa (213168) +
#     Banco Inter Investimentos Barra da Lagoa (213169) + Banco BTG Investimento Barra da Lagoa (224034)
#   MAURO RAMOS → Cora Mauro Ramos (212452) + Banco Inter Mauro Ramos (212451) +
#     Banco Inter Investimentos Mauro Ramos (212453) + Banco BTG Investimento Mauro Ramos (224031)
#   Consolidado → as 8 contas
# Filtros: sem transferências entre contas (99.01 ou descrição TRANSFERÊNCIA) + CC da unidade.
# Fonte: API Controlle v1. Envio: vinicius@terceirizou.com.br (cron mensal dia 04 14:00).
import json, os, sys, urllib.request, time
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle,
                                PageBreak, Image as RLImage, KeepTogether,
                                BaseDocTemplate, PageTemplate, Frame, NextPageTemplate)
from reportlab.lib.pagesizes import landscape
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_CVMRBL") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37")
VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-terceirizou.png")

UNIDADES = {
    "MAURO RAMOS": {
        "cc": "MAURO RAMOS", "cid": 157108,
        "contas": ["Cora Mauro Ramos", "Banco Inter Investimentos Mauro Ramos", "Banco BTG Investimento Mauro Ramos", "Banco Inter Mauro Ramos"],
    },
    "BARRA DA LAGOA": {
        "cc": "BARRA DA LAGOA", "cid": 157107,
        "contas": ["Cora Barra da Lagoa", "Banco Inter Barra da Lagoa", "Banco Inter Investimentos Barra da Lagoa", "Banco BTG Investimento Barra da Lagoa"],
    },
}

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

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

def brl_int(cents):
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

def ok_cc(t, ccs):
    """Filtro: sem transferências entre contas + CC da unidade (ou conjunto)."""
    for c in (t.get("apportionments_plan_account") or []):
        if (c.get("ds_category") or "").startswith("99.01"):
            return False
    if (t.get("ds_transaction") or "").upper().startswith("TRANSFERÊNCIA"):
        return False
    aps = t.get("apportionments_cost_center") or []
    if not aps:
        return False
    return any((a.get("ds_cost_center") or "").upper() in ccs for a in aps)

def agrupa(txs, so_negativas=False, so_positivas=False):
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
MES_ANT = add_months(HOJE.replace(day=1), -1)
FIM_MES_ANT = MES_ANT.replace(day=28) + timedelta(days=4)
FIM_MES_ANT = FIM_MES_ANT - timedelta(days=FIM_MES_ANT.day)
MES_COR = HOJE.replace(day=1)
FIM_MES_COR = MES_COR.replace(day=28) + timedelta(days=4)
FIM_MES_COR = FIM_MES_COR - timedelta(days=FIM_MES_COR.day)
INI_13 = add_months(MES_ANT, -12)   # 13 meses

FERIADOS = set()
for y in (MES_COR.year, MES_ANT.year):
    for d, m in ((1,1),(21,4),(1,5),(7,9),(12,10),(2,11),(15,11),(25,12)):
        FERIADOS.add(date(y, m, d))

HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")

# ===== dados (uma leitura só) =====
_tx = tx_list(f"{INI_13.year}-01-01", f"{MES_ANT.year + 1}-12-31")

def meses_13():
    out = []
    for i in range(0, 13):
        ini_m = add_months(INI_13, i)
        fim_m = add_months(ini_m, 1) - timedelta(days=1)
        out.append((ini_m.isoformat(), fim_m.isoformat(), f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"))
    return out
MESES13 = meses_13()

def dados_unidade(nome, cid):
    ccs = {nome}
    mes_ant_tx = [t for t in _tx if (t.get("dt_competence") or "")[:7] == f"{MES_ANT.year}-{MES_ANT.month:02d}" and ok_cc(t, ccs)]
    rec = agrupa(mes_ant_tx, so_positivas=True)
    desp = agrupa(mes_ant_tx, so_negativas=True)
    matriz = defaultdict(lambda: defaultdict(int))
    fluxo = []  # (label, saldo_ini, entradas, saidas, saldo_fim)
    # FLUXO DE CAIXA POR CENTRO DE CUSTO: lançamentos com CC da unidade, sem transferências
    # entre contas — EXCETO transferências internas da unidade (pareadas por uuid ou
    # descrição+data), que se anulam entre as contas da unidade e NÃO entram no fluxo.
    # Transferências ENTRE unidades (ex.: MR→BL) contam como movimento real de cada lado.
    # Saldo final de cada mês = saldo real via balances (casa 1:1 com o relatório de saldos).
    contas_un = set(UNIDADES[nome]["contas"])
    def transf(t):
        return ("TRANSFERÊNCIA" in (t.get("ds_transaction") or "").upper()
                or "para Banco" in (t.get("ds_transaction") or ""))
    tr_all = [t for t in _tx if transf(t)]
    por_uuid = defaultdict(list)
    for t in tr_all:
        if t.get("transaction_related_uuid"):
            por_uuid[t["transaction_related_uuid"]].append(t)
    pares = []
    usadas = set()
    for u, lst in por_uuid.items():
        if len(lst) >= 2:
            pares.append((lst[0], lst[1])); usadas.update(id(x) for x in lst[:2])
    resto = [t for t in tr_all if id(t) not in usadas]
    por_chave = defaultdict(list)
    for t in resto:
        # parear por descrição+data (valores OPOSTOS casam dentro do grupo)
        por_chave[((t.get("ds_transaction") or "")[:60], t.get("dt_billing") or t.get("dt_due") or "")].append(t)
    usadas2 = set()
    for k, lst in por_chave.items():
        neg = [t for t in lst if t["value_in_cent"] < 0 and id(t) not in usadas2]
        pos = [t for t in lst if t["value_in_cent"] > 0 and id(t) not in usadas2]
        for a in neg:
            for b in pos:
                if id(b) in usadas2: continue
                if a["value_in_cent"] == -b["value_in_cent"]:
                    pares.append((a, b)); usadas2.update((id(a), id(b)))
                    break
    def transf_interna(t):
        """True se a transferência é par INTERNO à unidade (anula — não é movimento da unidade)."""
        for a, b in pares:
            if t is a or t is b:
                contas_par = {a.get("ds_account_main"), b.get("ds_account_main")}
                return contas_par <= contas_un
        return False
    def transf_da_unidade(t):
        """True se a transferência toca a unidade (perna dela)."""
        return t.get("ds_account_main") in contas_un
    def ok_fluxo(t):
        if ok_cc(t, ccs):
            return True
        if transf(t):
            if not transf_da_unidade(t):
                return False  # transferência de OUTRA unidade → fora do fluxo desta
            # interna (par dentro da unidade) anula → fora; entre unidades/órfã → movimento real → entra
            return not transf_interna(t)
        return False
    id_contas = {}
    for c in req(f"{BASE}/account/v1/accounts").get("results", []):
        if c["ds_account"] in contas_un and c.get("status") == 1:
            id_contas[c["id"]] = c["ds_account"]
    def saldo_real(dia):
        tot = 0
        for cid_ in id_contas:
            b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={dia}&id_account_main={cid_}")["results"]
            tot += b["balanceDone"]
        return tot
    saldo_acum = saldo_real((date.fromisoformat(MESES13[0][0]) - timedelta(days=1)).isoformat())
    for i, (ini_m, fim_m, lab) in enumerate(MESES13):
        txs_m = [t for t in _tx if ini_m <= bdate(t) <= fim_m and ok_fluxo(t)]
        ent = sum(t["value_in_cent"] for t in txs_m if t["activity_type"] == 1)
        sai = sum(t["value_in_cent"] for t in txs_m if t["activity_type"] == 0)
        saldo_fim_real = saldo_real(fim_m)
        fluxo.append((lab, saldo_acum, ent, sai, saldo_fim_real))
        saldo_acum = saldo_fim_real
        # competência para o comparativo
        txs_c = [t for t in _tx if (t.get("dt_competence") or "")[:7] == fim_m[:7] and ok_cc(t, ccs)]
        for t in txs_c:
            for c in (t.get("apportionments_plan_account") or []):
                matriz[c.get("ds_category") or "?"][fim_m[:7]] += c.get("value") or 0
    # previsão mês corrente (caixa: pago + pendente)
    prev_tx = [t for t in _tx if MES_COR.isoformat() <= bdate(t) <= FIM_MES_COR.isoformat() and ok_cc(t, ccs)]
    prev_rec = agrupa(prev_tx, so_positivas=True)
    prev_desp = agrupa(prev_tx, so_negativas=True)
    # PROJEÇÃO 12M: lançamentos previstos por CC mês a mês (janela do MÊS, não cumulativa)
    # + saldo real de partida (preenchido depois, após os saldos)
    proj = []
    for i in range(1, 13):
        ini_m = add_months(MES_COR, i - 1)
        fim_m = add_months(ini_m, 1) - timedelta(days=1)
        lab = f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"
        txs_m = [t for t in _tx if ini_m.isoformat() <= bdate(t) <= fim_m.isoformat() and ok_cc(t, ccs)]
        ent = sum(t["value_in_cent"] for t in txs_m if t["activity_type"] == 1)
        sai = sum(t["value_in_cent"] for t in txs_m if t["activity_type"] == 0)
        proj.append((lab, ent, sai))
    return {
        "rec": rec, "desp": desp,
        "entradas": sum(v for v, _ in rec.values()), "saidas": sum(v for v, _ in desp.values()),
        "matriz": matriz,
        "fluxo": fluxo,
        "prev_rec": prev_rec, "prev_desp": prev_desp,
        "prev_rec_total": sum(v for v, _ in prev_rec.values()),
        "prev_desp_total": sum(v for v, _ in prev_desp.values()),
        "mes_ant_tx": mes_ant_tx, "prev_tx": prev_tx,
        "proj": proj,
    }

# saldos por unidade no último dia do mês anterior
def saldos_unidade(nome):
    saldos = []
    for c in req(f"{BASE}/account/v1/accounts").get("results", []):
        if c["ds_account"] in UNIDADES[nome]["contas"] and c.get("status") == 1:
            b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={FIM_MES_ANT.isoformat()}&id_account_main={c['id']}")["results"]
            saldos.append((c["ds_account"], b["balanceDone"]))
    return [(n, v) for n, v in saldos if v != 0]

print("buscando dados...")
D = {nome: dados_unidade(nome, u["cid"]) for nome, u in UNIDADES.items()}
S = {nome: saldos_unidade(nome) for nome in UNIDADES}
for nome in UNIDADES:
    tot = sum(v for _, v in S[nome])
    D[nome]["saldos"] = S[nome]
    D[nome]["saldo_total"] = tot
    # projeção 12m: saldo acumulado = saldo real de 30/09 + movimentos previstos do mês
    saldo_ac = tot
    proj_ac = []
    for lab, ent, sai in D[nome]["proj"]:
        saldo_ac += ent + sai
        proj_ac.append((lab, ent, sai, saldo_ac))
    D[nome]["proj_ac"] = proj_ac
# consolidado: proj = soma das duas unidades (saldo = soma dos saldos acumulados)
if len(UNIDADES) == 2:
    nomes = list(UNIDADES)
    proj_c = []
    for i in range(12):
        lab = D[nomes[0]]["proj_ac"][i][0]
        ent = D[nomes[0]]["proj_ac"][i][1] + D[nomes[1]]["proj_ac"][i][1]
        sai = D[nomes[0]]["proj_ac"][i][2] + D[nomes[1]]["proj_ac"][i][2]
        saldo = D[nomes[0]]["proj_ac"][i][3] + D[nomes[1]]["proj_ac"][i][3]
        proj_c.append((lab, ent, sai, saldo))
    D["CONSOLIDADO"] = {"proj_ac": proj_c}
print("dados prontos")

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=PRETO, spaceAfter=4)
h1c = ParagraphStyle("h1c", parent=h1, fontSize=15, alignment=1, spaceAfter=2)
h1u = ParagraphStyle("h1u", parent=h1, fontSize=17, textColor=colors.white, alignment=1, spaceBefore=6, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=LARANJA, spaceBefore=14, spaceAfter=3)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, textColor=PRETO, spaceBefore=10, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#777777"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)

def P_val(cents, style):
    s = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl(cents), s)

def P_val_int(cents, style):
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

def banda_unidade(titulo):
    t = Table([[P(f"<b>{titulo}</b>", h1u)]], colWidths=[18*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LARANJA),
                           ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
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
ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_MR_BL.pdf"
doc = BaseDocTemplate(ARQ_PDF, title="Relatório Gerencial — Centrovita Mauro Ramos + Barra da Lagoa",
                      pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.3*cm, bottomMargin=1.3*cm)
fr_p = Frame(1.5*cm, 1.3*cm, A4[0]-3*cm, A4[1]-2.6*cm, id="fr_p")
fr_l = Frame(1.5*cm, 1.3*cm, landscape(A4)[0]-3*cm, landscape(A4)[1]-2.6*cm, id="fr_l")

def _marca(canvas, doc_):
    """Símbolo Terceirizou no canto inferior direito (todas as páginas menos a capa)."""
    if doc_.page > 1:
        sim_path = os.path.join(_dir, "simbolo-terceirizou.png")
        if os.path.exists(sim_path):
            from PIL import Image as PILImage2
            sw, sh = PILImage2.open(sim_path).size
            alt = 0.85*cm
            img_s = RLImage(sim_path, width=alt*sw/sh, height=alt)
            img_s.drawOn(canvas, canvas._pagesize[0]-1.9*cm, 0.8*cm)

doc.addPageTemplates([
    PageTemplate(id="landscape", frames=[fr_l], pagesize=landscape(A4), onPage=_marca),
    PageTemplate(id="portrait", frames=[fr_p], pagesize=A4, onPage=_marca),
])
E = []

# CAPA COMPACTA: pág 1 em PAISAGEM (acompanha o comparativo na mesma página)
subc_center = ParagraphStyle("subc_center", parent=sub, fontSize=8, alignment=1, spaceAfter=0)
if os.path.exists(LOGO):
    img = RLImage(LOGO, width=4.2*cm, height=4.2*cm*561/1600)
    img.hAlign = "CENTER"
    E.append(img)
E.append(Spacer(1, 4))
E.append(P("<b>CENTROVITA MAURO RAMOS + BARRA DA LAGOA</b>", h1c))
E.append(P(f"Relatório Gerencial Mensal · Gerado em {HOJE_LABEL} · Fonte: Controlle · Ref.: {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year}", subc_center))
E.append(Spacer(1, 4))

def bloco_unidade(nome, d, primeira=False):
    """6 relatórios de uma unidade. primeira=True: sem PageBreak (continua na capa)."""
    els = []
    if not primeira:
        els.append(NextPageTemplate("portrait"))
        els.append(PageBreak())
    els.append(banda_unidade(nome))
    els.append(Spacer(1, 6))
    # 1. Comparativo 13 meses (competência) — MESMA PÁGINA DA CAPA (paisagem)
    els.append(NextPageTemplate("landscape"))
    els.append(PageBreak())
    els.append(P(f"Comparativo dos Últimos 13 Meses por Categoria ({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) — regime de competência", h2))
    cats = sorted({c for c in d["matriz"]})
    rows = [[P("<b>Categoria</b>", cell)] + [P(f"<b>{lab}</b>", cellr) for _, _, lab in MESES13] + [P("<b>Média</b>", cellr), P("<b>Total</b>", cellr)]]
    for cat in cats:
        row = [P(cat, cell)]
        vals13 = [d["matriz"][cat].get(fim_m_iso[:7], 0) for _, fim_m_iso, _ in MESES13]
        for v in vals13:
            row.append(P_val_int(v, cellr) if v else P("—", cellr))
        row.append(P_val_int(round(sum(vals13) / len(vals13)), cellrb))
        row.append(P_val_int(sum(vals13), cellrb))
        rows.append(row)
    els.append(tabela(rows, [6.0*cm] + [1.35*cm]*13 + [1.6*cm, 1.8*cm], fs=7))
    # 2. Receitas e Despesas do mês anterior consolidadas (competência) — MESMA PÁGINA (paisagem)
    els.append(Spacer(1, 10))
    els.append(KeepTogether(tabela_cat(f"Receitas e Despesas — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de competência)", d["rec"], total_label="Total de Receitas")))
    rows2 = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nm, (v, n) in sorted(d["desp"].items()):
        rows2.append([P(nm, cell), P(str(n), cellc), P_val(v, cellr)])
    rows2.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n for _, n in d['desp'].values())}</b>", cellc), P_val(d["saidas"], cellrb)])
    rows2.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{len(d['mes_ant_tx'])}</b>", cellc), P_val(d["entradas"] + d["saidas"], cellrb)])
    t = tabela(rows2, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows2)-2), (-1,len(rows2)-1), LARANJA_CLARO)]))
    els.append(t)
    # 3. Previsão de Receitas e Despesas do mês corrente (caixa)
    els.append(PageBreak())
    els.append(KeepTogether(tabela_cat(f"Previsão de Receitas e Despesas — {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)", d["prev_rec"], total_label="Total previsto")))
    rows3 = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nm, (v, n) in sorted(d["prev_desp"].items()):
        rows3.append([P(nm, cell), P(str(n), cellc), P_val(v, cellr)])
    rows3.append([P("<b>Total de Despesas Previstas</b>", cellrb), P(f"<b>{sum(n for _, n in d['prev_desp'].values())}</b>", cellc), P_val(d["prev_desp_total"], cellrb)])
    t = tabela(rows3, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows3)-1), (-1,len(rows3)-1), LARANJA_CLARO)]))
    els.append(t)
    # 4. Fluxo de Caixa dos últimos 13 meses (realizado, por CC)
    els.append(PageBreak())
    rows4 = [[P("<b>Mês</b>", cell), P("<b>Saldo inicial</b>", cellr), P("<b>Entradas</b>", cellr), P("<b>Saídas</b>", cellr), P("<b>Saldo final</b>", cellr)]]
    for lab, si, ent, sai, sf in d["fluxo"]:
        rows4.append([P(lab, cell), P_val(si, cellr), P_val(ent, cellr), P_val(sai, cellr), P_val(sf, cellrb)])
    t = tabela(rows4, [3.2*cm, 3.4*cm, 3.4*cm, 3.4*cm, 3.6*cm], fs=7)
    els.append(KeepTogether([P(f"Fluxo de Caixa — Últimos 13 Meses ({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) — realizado", h2), t]))
    els.append(P("Nota: fluxo por centro de custo. Transferências entre contas da própria unidade "
                 "se anulam (não alteram o saldo); transferências entre unidades contam como movimento. "
                 "Saldo final = saldo real das contas da unidade.", sub))
    # 5. Saldo nas contas
    els.append(Spacer(1, 16))
    rows5 = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {FIM_MES_ANT_LABEL}</b>", cellr)]]
    for nm, v in d["saldos"]:
        rows5.append([P(nm, cell), P_val(v, cellr)])
    rows5.append([P("<b>Total</b>", cellrb), P_val(d["saldo_total"], cellrb)])
    t = tabela(rows5, [11*cm, 5*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows5)-1), (-1,len(rows5)-1), LARANJA_CLARO)]))
    els.append(KeepTogether([P(f"Saldo nas contas em {FIM_MES_ANT_LABEL}", h2), t]))
    # 6. Projeção de Fluxo de Caixa — próximos 12 meses (por CC)
    els.append(PageBreak())
    rows6 = [[P("<b>Mês</b>", cell), P("<b>Entradas previstas</b>", cellr), P("<b>Saídas previstas</b>", cellr), P("<b>Saldo previsto</b>", cellr)]]
    for lab, ent, sai, saldo in d["proj_ac"]:
        rows6.append([P(lab, cell), P_val(ent, cellr), P_val(sai, cellr), P_val(saldo, cellrb)])
    t = tabela(rows6, [3.6*cm, 4.4*cm, 4.4*cm, 4.6*cm], fs=7.5)
    els.append(KeepTogether([P(f"Projeção de Fluxo de Caixa — Próximos 12 Meses ({MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} a {MES_PT[add_months(MES_COR,11).month].capitalize()} de {add_months(MES_COR,11).year})", h2), t,
                             P("Nota: saldo de partida = saldo real em " + FIM_MES_ANT_LABEL + "; movimentos = lançamentos previstos do Controlle (aportes e despesas recorrentes).", sub)]))
    return els

def bloco_consolidado():
    """Consolidado: 2 (mês anterior) + 3 (previsão) + 5 (saldo) + 6 (projeção 12m)."""
    els = []
    els.append(NextPageTemplate("portrait"))
    els.append(PageBreak())
    els.append(banda_unidade("CONSOLIDADO — MAURO RAMOS + BARRA DA LAGOA"))
    els.append(Spacer(1, 6))
    rec_c = defaultdict(lambda: [0, 0])
    desp_c = defaultdict(lambda: [0, 0])
    prec_c = defaultdict(lambda: [0, 0])
    pdesp_c = defaultdict(lambda: [0, 0])
    for nome in UNIDADES:
        d = D[nome]
        for k, (v, n) in d["rec"].items():
            rec_c[k][0] += v; rec_c[k][1] += n
        for k, (v, n) in d["desp"].items():
            desp_c[k][0] += v; desp_c[k][1] += n
        for k, (v, n) in d["prev_rec"].items():
            prec_c[k][0] += v; prec_c[k][1] += n
        for k, (v, n) in d["prev_desp"].items():
            pdesp_c[k][0] += v; pdesp_c[k][1] += n
    ent_c = sum(v for v, _ in rec_c.values()); sai_c = sum(v for v, _ in desp_c.values())
    saldos_c = [(nm, v) for nome in UNIDADES for nm, v in D[nome]["saldos"]]
    tot_c = sum(v for _, v in saldos_c)
    # 2. mês anterior
    els.append(KeepTogether(tabela_cat(f"Receitas e Despesas — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de competência)", rec_c, total_label="Total de Receitas")))
    rows2 = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nm, (v, n) in sorted(desp_c.items()):
        rows2.append([P(nm, cell), P(str(n), cellc), P_val(v, cellr)])
    rows2.append([P("<b>Total de Despesas</b>", cellrb), P(f"<b>{sum(n for _, n in desp_c.values())}</b>", cellc), P_val(sai_c, cellrb)])
    rows2.append([P("<b>Resultado do mês</b>", cellrb), P(f"<b>{sum(len(D[n]['mes_ant_tx']) for n in UNIDADES)}</b>", cellc), P_val(ent_c + sai_c, cellrb)])
    t = tabela(rows2, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows2)-2), (-1,len(rows2)-1), LARANJA_CLARO)]))
    els.append(t)
    # 3. previsão mês corrente
    els.append(PageBreak())
    els.append(KeepTogether(tabela_cat(f"Previsão de Receitas e Despesas — {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)", prec_c, total_label="Total previsto")))
    rows3 = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nm, (v, n) in sorted(pdesp_c.items()):
        rows3.append([P(nm, cell), P(str(n), cellc), P_val(v, cellr)])
    rows3.append([P("<b>Total de Despesas Previstas</b>", cellrb), P(f"<b>{sum(n for _, n in pdesp_c.values())}</b>", cellc), P_val(sum(v for v, _ in pdesp_c.values()), cellrb)])
    t = tabela(rows3, [11*cm, 2.5*cm, 3*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows3)-1), (-1,len(rows3)-1), LARANJA_CLARO)]))
    els.append(t)
    # 5. saldo nas contas
    els.append(Spacer(1, 16))
    rows5 = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {FIM_MES_ANT_LABEL}</b>", cellr)]]
    for nm, v in saldos_c:
        rows5.append([P(nm, cell), P_val(v, cellr)])
    rows5.append([P("<b>Total</b>", cellrb), P_val(tot_c, cellrb)])
    t = tabela(rows5, [11*cm, 5*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,len(rows5)-1), (-1,len(rows5)-1), LARANJA_CLARO)]))
    els.append(KeepTogether([P(f"Saldo nas contas em {FIM_MES_ANT_LABEL}", h2), t]))
    # 6. Projeção de Fluxo de Caixa 12m — CONSOLIDADO
    rows6 = [[P("<b>Mês</b>", cell), P("<b>Entradas previstas</b>", cellr), P("<b>Saídas previstas</b>", cellr), P("<b>Saldo previsto</b>", cellr)]]
    for lab, ent, sai, saldo in D["CONSOLIDADO"]["proj_ac"]:
        rows6.append([P(lab, cell), P_val(ent, cellr), P_val(sai, cellr), P_val(saldo, cellrb)])
    t = tabela(rows6, [3.6*cm, 4.4*cm, 4.4*cm, 4.6*cm], fs=7.5)
    els.append(PageBreak())
    els.append(KeepTogether([P(f"Projeção de Fluxo de Caixa — Próximos 12 Meses ({MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} a {MES_PT[add_months(MES_COR,11).month].capitalize()} de {add_months(MES_COR,11).year})", h2), t,
                             P("Nota: saldo de partida = saldo real em " + FIM_MES_ANT_LABEL + " (soma das duas unidades); movimentos = lançamentos previstos do Controlle.", sub)]))
    els.append(Spacer(1, 10))
    els.append(P("Gerado automaticamente pela Terceirizou · dados do Controlle", sub))
    return els

for i, nome in enumerate(("MAURO RAMOS", "BARRA DA LAGOA")):
    E.extend(bloco_unidade(nome, D[nome], primeira=(i == 0)))
E.extend(bloco_consolidado())

# símbolo
from PIL import Image as PILImage
img_full = PILImage.open(LOGO)
_w, _h = img_full.size
sim = img_full.crop((0, 0, int(_w * 0.233), _h))
bbox = sim.getbbox()
if bbox:
    sim = sim.crop(bbox)
sim.save(os.path.join(_dir, "simbolo-terceirizou.png"))

doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== Excel =====
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_MR_BL.xlsx"
wb = Workbook()
wb.remove(wb.active)
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"
VERMELHO_XL = "C0392B"
TOT_LABELS = ("Total", "Totais", "Resultado", "Previsão", "Total de Receitas", "Total de Despesas",
              "Total de Despesas Previstas", "Total previsto", "Saldo final")

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

for nome in ("MAURO RAMOS", "BARRA DA LAGOA"):
    d = D[nome]
    tag = "MR" if nome == "MAURO RAMOS" else "BL"
    cats = sorted({c for c in d["matriz"]})
    rows13 = [("Categoria",) + tuple(lab for _, _, lab in MESES13) + ("Média", "Total")]
    for cat in cats:
        vals13 = [d["matriz"][cat].get(fim_m_iso[:7], 0) for _, fim_m_iso, _ in MESES13]
        rows13.append((cat,) + tuple(r_(v) if v else None for v in vals13) +
                      (r_(round(sum(vals13) / len(vals13))), r_(sum(vals13))))
    aba(f"Comp 13m {tag}", rows13, [40] + [11]*13 + [12, 14],
        titulo=f"{nome} — Comparativo dos Últimos 13 Meses por Categoria (competência)")
    aba(f"Mes ant {tag}",
        [("Categoria", "Lançamentos", "Valor")] +
        [(n, n2, r_(v)) for n, (v, n2) in sorted(d["rec"].items())] +
        [("Total de Receitas", sum(n for _, n in d["rec"].values()), r_(d["entradas"]))] +
        [(n, n2, r_(v)) for n, (v, n2) in sorted(d["desp"].items())] +
        [("Total de Despesas", sum(n for _, n in d["desp"].values()), r_(d["saidas"])),
         ("Resultado do mês", len(d["mes_ant_tx"]), r_(d["entradas"] + d["saidas"]))],
        [45, 14, 16], titulo=f"{nome} — Receitas e Despesas de {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (competência)")
    aba(f"Previsao {tag}",
        [("Categoria", "Lançamentos", "Valor")] +
        [(n, n2, r_(v)) for n, (v, n2) in sorted(d["prev_rec"].items())] +
        [("Total previsto", sum(n for _, n in d["prev_rec"].values()), r_(d["prev_rec_total"]))] +
        [(n, n2, r_(v)) for n, (v, n2) in sorted(d["prev_desp"].items())] +
        [("Total de Despesas Previstas", sum(n for _, n in d["prev_desp"].values()), r_(d["prev_desp_total"])),
         ("Resultado previsto do mês", "", r_(d["prev_rec_total"] + d["prev_desp_total"]))],
        [45, 14, 16], titulo=f"{nome} — Previsão de Receitas e Despesas de {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)")
    aba(f"Fluxo 13m {tag}",
        [("Mês", "Saldo inicial", "Entradas", "Saídas", "Saldo final")] +
        [(lab, r_(si), r_(ent), r_(sai), r_(sf)) for lab, si, ent, sai, sf in d["fluxo"]],
        [10, 16, 16, 16, 16], titulo=f"{nome} — Fluxo de Caixa dos Últimos 13 Meses (realizado)")
    aba(f"Saldos {tag}",
        [("Conta", f"Saldo em {FIM_MES_ANT_LABEL}")] +
        [(n, r_(v)) for n, v in d["saldos"]] + [("Total", r_(d["saldo_total"]))],
        [40, 18], titulo=f"{nome} — Saldo nas contas em {FIM_MES_ANT_LABEL}")
    aba(f"Proj fluxo 12m {tag}",
        [("Mês", "Entradas previstas", "Saídas previstas", "Saldo previsto")] +
        [(lab, r_(ent), r_(sai), r_(saldo)) for lab, ent, sai, saldo in d["proj_ac"]],
        [10, 18, 18, 18], titulo=f"{nome} — Projeção de Fluxo de Caixa — Próximos 12 Meses")

# consolidado
rec_c = defaultdict(lambda: [0, 0]); desp_c = defaultdict(lambda: [0, 0])
prec_c = defaultdict(lambda: [0, 0]); pdesp_c = defaultdict(lambda: [0, 0])
for nome in UNIDADES:
    d = D[nome]
    for k, (v, n) in d["rec"].items(): rec_c[k][0] += v; rec_c[k][1] += n
    for k, (v, n) in d["desp"].items(): desp_c[k][0] += v; desp_c[k][1] += n
    for k, (v, n) in d["prev_rec"].items(): prec_c[k][0] += v; prec_c[k][1] += n
    for k, (v, n) in d["prev_desp"].items(): pdesp_c[k][0] += v; pdesp_c[k][1] += n
ent_c = sum(v for v, _ in rec_c.values()); sai_c = sum(v for v, _ in desp_c.values())
aba("Consolidado mes ant",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(rec_c.items())] +
    [("Total de Receitas", sum(n for _, n in rec_c.values()), r_(ent_c))] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(desp_c.items())] +
    [("Total de Despesas", sum(n for _, n in desp_c.values()), r_(sai_c)),
     ("Resultado do mês", sum(len(D[n]["mes_ant_tx"]) for n in UNIDADES), r_(ent_c + sai_c))],
    [45, 14, 16], titulo=f"CONSOLIDADO — Receitas e Despesas de {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (competência)")
aba("Consolidado previsao",
    [("Categoria", "Lançamentos", "Valor")] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(prec_c.items())] +
    [("Total previsto", sum(n for _, n in prec_c.values()), r_(sum(v for v, _ in prec_c.values())))] +
    [(n, n2, r_(v)) for n, (v, n2) in sorted(pdesp_c.items())] +
    [("Total de Despesas Previstas", sum(n for _, n in pdesp_c.values()), r_(sum(v for v, _ in pdesp_c.values()))),
     ("Resultado previsto do mês", "", r_(sum(v for v, _ in prec_c.values()) + sum(v for v, _ in pdesp_c.values())))],
    [45, 14, 16], titulo=f"CONSOLIDADO — Previsão de {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)")
aba("Consolidado proj 12m",
    [("Mês", "Entradas previstas", "Saídas previstas", "Saldo previsto")] +
    [(lab, r_(ent), r_(sai), r_(saldo)) for lab, ent, sai, saldo in D["CONSOLIDADO"]["proj_ac"]],
    [10, 18, 18, 18], titulo="CONSOLIDADO — Projeção de Fluxo de Caixa — Próximos 12 Meses")
saldos_c = [(nm, v) for nome in UNIDADES for nm, v in D[nome]["saldos"]]
aba("Consolidado saldos",
    [("Conta", f"Saldo em {FIM_MES_ANT_LABEL}")] +
    [(n, r_(v)) for n, v in saldos_c] +
    [("Total", r_(sum(v for _, v in saldos_c)))],
    [40, 18], titulo=f"CONSOLIDADO — Saldo nas contas em {FIM_MES_ANT_LABEL}")

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
