#!/usr/bin/env python3
# Relatório Gerencial — CENTROVITA BRAÇO DO NORTE
# UNIDADE INDEPENDENTE · REGIME DE CAIXA · todas as movimentações
# v1.0, 2026-11-12 — pedido do Vinícius: "a CENTROVITA BRAÇO DO NORTE é uma unidade
# independente. Gere/atualize a automação MENSAL CENTROVITA BRAÇO DO NORTE com todas as
# movimentações de acordo com os parâmetros já orientados anteriormente".
# Molde: relatorio_centrovita_trindade (regime de caixa, unidade única, sem consolidado).
#
# LICENÇA PRÓPRIA E INDEPENDENTE: token e plano de contas só desta unidade. Não existe
# consolidação com Mauro Ramos/Barra da Lagoa/Araranguá/Trindade, e os empréstimos
# lançados nesta licença são com TERCEIROS (Bem Viver, Araranguá, Florence, pessoas
# físicas), não movimento entre casas do mesmo grupo.
#
# REGIME DE CAIXA: situation in (1,2) = baixado + agendado, mês apurado por dt_billing.
# Fora do caixa: TRANSFERÊNCIA ENTRE CONTAS (type == 1 e descrição "TRANSFERÊNCIA").
# VALOR EFETIVO: payment_in_cent quando existe (pago com ajuste) — é o que fecha com balances.
# TRAVAS (abortam antes de gerar qualquer página):
#   1) lista do mês == revenuesDone/expensesDone do balances, em cada mês do comparativo
#   2) saldo inicial + entradas + saídas == saldo final, em cada mês
#   3) soma dos saldos das contas == balanceDone da licença na data de referência
# Nenhum ajuste automático: lançamento sem classificação vai para o bloco "Lançamentos em
# Outros (a classificar)" e continua contando no caixa — o relatório não remenda a origem.
#
# USO: python3 relatorio_centrovita_bn_caixa.py [YYYY-MM-DD]   (default: hoje)
import json, os, sys, urllib.request, time, http.client
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
                                Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage)

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_CENTROVITA_BN") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37")
VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-centrovita.png")
LOGO_T = os.path.join(_dir, "logo-terceirizou-completa.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")

CLIENTE = "CENTROVITA BRAÇO DO NORTE"
MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

# ===== plano de contas desta licença (Centrovita Braço do Norte) =====
# ROTEAMENTO POR NOME COMPLETO, nunca por prefixo curto: "02.05 Entrada de Empréstimo entre
# Casas" (10335235) e "02.05 Plantão Extra" (9190506) COMPARTILHAM o código 02.05, e o prefixo
# "02.05 " misturava despesa de plantão com empréstimo. Mesma armadilha em "02.01 Aporte dos
# Sócios" x "02.01 Salários" e em "02.03 Juros Aplicação Financeira" x "02.03 Adiantamento (Vale)".
REC_PREFIXO = "01."                                                  # 01.01/01.02/01.03/01.99
REEMBOLSO = "02.04 Reembolso Família"                                # receita, não despesa
APORTE = "02.01 Aporte dos Sócios"                                   # fora do resultado
JUROS = "02.03 Juros Aplicação Financeira"
ENT_EMPR = ("02.05 Entrada de Empréstimo entre Casas",)
SAI_EMPR = ("04.03 Parcela de Empréstimo ou Financiamento a Bancos",
            "04.06 Saida de Empréstimo outras Casas")
CAPEX_PREFIXOS = ("05.0",)                                           # 05.01 a 05.04
DESP_PREFIXOS = ("02.", "03.")                                       # operacional
OUTROS = "Outros"
CAT_MENSAL = "01.01 Mensalidades"                                    # base hóspedes/ticket


def eh_receita(c):     return c.startswith(REC_PREFIXO) or c == REEMBOLSO
def eh_aporte(c):      return c == APORTE
def eh_juros(c):       return c == JUROS
def eh_reembolso(c):   return c == REEMBOLSO
def eh_ent_empr(c):    return c in ENT_EMPR
def eh_sai_empr(c):    return c in SAI_EMPR
def eh_capex(c):       return c.startswith(CAPEX_PREFIXOS)
def eh_desp_op(c):     return (c.startswith(DESP_PREFIXOS) and not (
                               eh_aporte(c) or eh_juros(c) or eh_reembolso(c)
                               or eh_ent_empr(c) or eh_sai_empr(c)))


def req(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items():
                r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and i < tries - 1:
                time.sleep(3 * (i + 1)); continue
            raise
        except (http.client.IncompleteRead, OSError, ValueError):
            if i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            raise


def tx_list(start, end):
    out, page = [], 1
    while True:
        url = (f"{BASE}/transaction/v1/transactions/list?start_date={start}&end_date={end}"
               f"&page={page}&orderBy=date&orderByCardinality=ASC")
        tl = req(url).get("results", {}).get("transactionsList", [])
        if not tl:
            return out
        out.extend(tl)
        page += 1


def bal(ini, fim):
    return req(f"{BASE}/transaction/v1/transactions/balances?start_date={ini}&end_date={fim}")["results"]


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
    return date(y, m % 12 + 1, 1)


def bdate(t):
    return (t.get("dt_billing") or t.get("dt_due") or "")[:10]


def cat_nome(t):
    a = t.get("apportionments_plan_account") or []
    return (a[0].get("ds_category") or "(sem categoria)") if a else "(sem categoria)"


def cat_secundarias(t):
    """Categorias além da primeira (rateio)."""
    a = t.get("apportionments_plan_account") or []
    return [(x.get("ds_category") or "(sem categoria)") for x in a[1:]]


def eh_transferencia(t):
    if t.get("type") == 1:
        return True
    d = (t.get("ds_transaction") or "").upper()
    if d.startswith("TRANSFERÊNCIA") or d.startswith("TRANSFERENCIA"):
        return True
    for c in (t.get("apportionments_plan_account") or []):
        ds = (c.get("ds_category") or "")
        if ds.startswith("99.01") or ds.lower().startswith("transfer"):
            return True
    return False


def ok_caixa(t):
    return not eh_transferencia(t)


def valor_efetivo(t):
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]



# ===== datas =====
HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_ANT = add_months(HOJE.replace(day=1), -1)
FIM_MES_ANT = (MES_ANT.replace(day=28) + timedelta(days=4)) - timedelta(days=(MES_ANT.replace(day=28) + timedelta(days=4)).day)
MES_COR = HOJE.replace(day=1)
FIM_MES_COR = (MES_COR.replace(day=28) + timedelta(days=4)) - timedelta(days=(MES_COR.replace(day=28) + timedelta(days=4)).day)
REF = f"{MES_ANT.year}-{MES_ANT.month:02d}"
HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")

# ÂNCORA: primeiro lançamento da licença é 06/05/2025 (APORTE RAUL). Antes disso não há
# movimento; meses vazios só alargariam a tabela sem informação.
ANCORA = date(2025, 5, 1)
INI_13 = max(ANCORA, add_months(MES_ANT, -12))
MESES13 = []
_m = INI_13
while _m <= MES_ANT:
    _f = add_months(_m, 1) - timedelta(days=1)
    MESES13.append((_m.isoformat(), _f.isoformat(), f"{MES_AB[_m.month]}/{str(_m.year)[2:]}", f"{_m.year}-{_m.month:02d}"))
    _m = add_months(_m, 1)

print(f"período do comparativo: {MESES13[0][3]} a {MESES13[-1][3]}  · ref {REF}")

# ===== dados =====
# janela: do início do comparativo até o fim do mês da projeção (12 meses à frente)
_fim_proj = add_months(MES_COR, 12) - timedelta(days=1)
_tx = []
for y in sorted({INI_13.year, MES_ANT.year, MES_COR.year, _fim_proj.year}):
    _tx.extend(tx_list(f"{y}-01-01", f"{y}-12-31"))
_vistos, _ded = set(), []
for t in _tx:
    k = t.get("id_transactions_payments")
    if k is None:
        k = (t.get("id_transactions"), t.get("value_in_cent"), bdate(t), t.get("situation"))
    if k in _vistos:
        continue
    _vistos.add(k); _ded.append(t)
_tx = _ded
print(f"lançamentos: {len(_tx)}")


def txs_mes(mes_key, incluir_pendente=False):
    """Lançamentos de caixa do mês (dt_billing), sem transferências entre contas."""
    sit = (0, 1, 2) if incluir_pendente else (1, 2)
    return [t for t in _tx if bdate(t)[:7] == mes_key and t.get("situation") in sit and ok_caixa(t)]


def soma_por_categoria(txs):
    g = defaultdict(lambda: [0, 0])
    for t in txs:
        cats = [(a.get("ds_category") or "(sem categoria)") for a in (t.get("apportionments_plan_account") or [])]
        if not cats:
            cats = ["(sem categoria)"]
        # rateio: divide o valor entre as categorias na proporção informada
        app = t.get("apportionments_plan_account") or []
        v_tot = valor_efetivo(t)
        soma_vals = sum((a.get("value") or 0) for a in app)
        for a, c in zip(app or [{"value": v_tot}], cats):
            if soma_vals:
                v = round(v_tot * (a.get("value") or 0) / soma_vals)
            else:
                v = v_tot
            g[c][0] += v
            g[c][1] += 1
    return g


_CACHE_RM = {}


def resumo_mes(mes_key):
    """Todos os blocos de um mês em caixa, com as naturezas separadas."""
    if mes_key in _CACHE_RM:
        return _CACHE_RM[mes_key]
    tx = txs_mes(mes_key)
    g = soma_por_categoria(tx)
    r = dict(tx=tx, por_cat=g)
    r["receita_op"] = sum(v for c, (v, n) in g.items() if eh_receita(c))
    r["desp_op"] = sum(v for c, (v, n) in g.items() if eh_desp_op(c))
    r["capex"] = sum(v for c, (v, n) in g.items() if eh_capex(c))
    r["aportes"] = sum(v for c, (v, n) in g.items() if eh_aporte(c))
    r["juros"] = sum(v for c, (v, n) in g.items() if eh_juros(c))
    r["ent_empr"] = sum(v for c, (v, n) in g.items() if eh_ent_empr(c))
    r["sai_empr"] = sum(v for c, (v, n) in g.items() if eh_sai_empr(c))
    # (sem categoria)/Outros: entra na variação, mas não é operação
    r["outros"] = sum(v for c, (v, n) in g.items()
                      if not (eh_receita(c) or eh_desp_op(c) or eh_capex(c) or eh_aporte(c)
                              or eh_juros(c) or eh_ent_empr(c) or eh_sai_empr(c)))
    r["resultado_op"] = r["receita_op"] + r["desp_op"]
    r["resultado"] = r["resultado_op"] + r["juros"]
    r["variacao"] = (r["resultado"] + r["aportes"] + r["ent_empr"] + r["sai_empr"]
                     + r["capex"] + r["outros"])
    _CACHE_RM[mes_key] = r
    return r


# ===== TRAVAS =====
# 1) lista do mês == balances do mês (prova de que a paginação não perdeu linha e de que
#    a exclusão de transferência está correta); 2) caixa anda (saldo inicial + variação).
tot_saldo_contas = None
fluxo = []
_primeiro = MESES13[0][0]
_dia_antes = (date.fromisoformat(_primeiro) - timedelta(days=1)).isoformat()
# saldo de partida = saldo real das contas no dia anterior ao início do comparativo
s_ini = bal("2019-01-01", _dia_antes)["balanceDone"]
for _, fim, lab, key in MESES13:
    ini_m = fim[:8] + "01"
    b = bal(ini_m, fim)
    e = b.get("revenuesDone", 0) or 0
    x = b.get("expensesDone", 0) or 0
    sf = b["balanceDone"]
    rm = resumo_mes(key)
    # TRAVA 1: o resumo do mês tem de explicar exatamente o líquido do balances
    if rm["variacao"] != e + x:
        raise SystemExit(f"ERRO trava 1 ({lab}): resumo {rm['variacao']/100:,.2f} "
                         f"!= balances {(e + x)/100:,.2f}")
    # TRAVA 2: entradas + saídas explicam a variação real do saldo
    if s_ini + e + x != sf:
        raise SystemExit(f"ERRO trava 2 ({lab}): {s_ini} + {e} + {x} != {sf}")
    fluxo.append((lab, s_ini, e, x, sf))
    s_ini = sf
saldo_cc = fluxo[-1][4]
tot_saldo_contas = bal("2019-01-01", FIM_MES_ANT.isoformat())["balanceDone"]
if tot_saldo_contas != saldo_cc:
    raise SystemExit(f"ERRO trava 3: saldo pelo fluxo {saldo_cc/100:,.2f} != "
                     f"balanceDone da licença {tot_saldo_contas/100:,.2f}")
print(f"travas OK: lista == balances nos {len(MESES13)} meses; fluxo fecha; "
      f"saldo {FIM_MES_ANT_LABEL} = {saldo_cc/100:,.2f}")

D = resumo_mes(REF)

# comparativo 13 meses por categoria (caixa)
matriz = defaultdict(lambda: defaultdict(int))
for _, _, lab, key in MESES13:
    for c, (v, n) in soma_por_categoria(txs_mes(key)).items():
        if v:
            matriz[c][key] += v
meses_mov = [(fim, lab, key) for _, fim, lab, key in MESES13
             if any(v.get(key) for v in matriz.values())]

# despesas em aberto até o último dia do mês anterior (só despesa operacional e CAPEX)
aberto = [t for t in _tx if t.get("activity_type") == 0 and t.get("situation") == 0
          and bdate(t) <= FIM_MES_ANT.isoformat() and ok_caixa(t)]
aberto_op = [t for t in aberto if eh_desp_op(cat_nome(t)) or eh_capex(cat_nome(t))]
g_aberto = soma_por_categoria(aberto_op)

# receitas em aberto (inadimplência) até o último dia do mês anterior
aberto_rec = [t for t in _tx if t.get("activity_type") == 1 and t.get("situation") == 0
              and bdate(t) <= FIM_MES_ANT.isoformat() and ok_caixa(t)]
g_aberto_rec = soma_por_categoria(aberto_rec)

# previsão do mês corrente: pendente + agendado
prev = txs_mes(f"{MES_COR.year}-{MES_COR.month:02d}", incluir_pendente=True)
prev_pend = [t for t in prev if t.get("situation") == 0]
prev_rec = soma_por_categoria([t for t in prev_pend if t.get("activity_type") == 1])
prev_desp = soma_por_categoria([t for t in prev_pend if t.get("activity_type") == 0])

# empréstimos: por contraparte (quem tomou / quem devolveu), em caixa
def por_contraparte(txs):
    g = defaultdict(lambda: [0, 0, 0])  # saiu, voltou, n
    for t in txs:
        c = cat_nome(t)
        if not (eh_ent_empr(c) or eh_sai_empr(c)):
            continue
        nome = (t.get("name_contact") or "").strip() or "(sem contato)"
        v = valor_efetivo(t)
        if eh_sai_empr(c):
            g[nome][0] += v
        else:
            g[nome][1] += v
        g[nome][2] += 1
    return g


emp_13 = por_contraparte([t for t in _tx if t.get("situation") in (1, 2) and ok_caixa(t)
                          and MESES13[0][3] <= bdate(t)[:7] <= MESES13[-1][3]])
emp_mes = por_contraparte(D["tx"])

# lançamentos em "Outros"/sem categoria (a classificar) — o relatório mostra, não conserta
a_classificar = sorted([t for t in _tx if t.get("situation") in (1, 2) and ok_caixa(t)
                        and cat_nome(t) in (OUTROS, "(sem categoria)")
                        and MESES13[0][3] <= bdate(t)[:7] <= MESES13[-1][3]], key=bdate)

# projeção 12 meses (previstos/pendentes)
proj = []
for i in range(1, 13):
    ini_m = add_months(MES_COR, i - 1)
    fim_m = add_months(ini_m, 1) - timedelta(days=1)
    lab = f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"
    txs_m = [t for t in _tx if ini_m.isoformat() <= bdate(t) <= fim_m.isoformat() and ok_caixa(t)]
    ent = sum(valor_efetivo(t) for t in txs_m if t.get("activity_type") == 1)
    sai = sum(valor_efetivo(t) for t in txs_m if t.get("activity_type") == 0)
    proj.append((lab, ent, sai))
proj_ac, _ac = [], saldo_cc
for lab, ent, sai in proj:
    _ac += ent + sai
    proj_ac.append((lab, ent, sai, _ac))

# ===== hóspedes e ticket médio (regra de 12/11: contatos distintos que pagaram 01.01) =====
hosp_serie, ticket_serie = {}, {}
for _, _, lab, key in MESES13:
    contatos, orfaos, soma = set(), 0, 0
    for t in txs_mes(key):
        if cat_nome(t) != CAT_MENSAL:
            continue
        soma += valor_efetivo(t)
        if t.get("id_contacts"):
            contatos.add(t["id_contacts"])
        else:
            orfaos += 1
    h = len(contatos) + orfaos
    hosp_serie[key] = h or None
    ticket_serie[key] = round(soma / 100 / h, 2) if h else None

print(f"hóspedes {REF}: {hosp_serie.get(REF)} · ticket {ticket_serie.get(REF)}")
print("dados prontos")

# ===== PDF =====
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=PRETO, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=LARANJA, spaceBefore=14, spaceAfter=3)
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, textColor=PRETO, spaceBefore=10, spaceAfter=3)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5,
                     textColor=colors.HexColor("#777777"), spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold")
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cellb, alignment=2)
cellc = ParagraphStyle("cellc", parent=cell, alignment=1)
P = Paragraph


def P_val(cents, style):
    st = ParagraphStyle("v", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl(cents), st)


def P_val_int(cents, style):
    st = ParagraphStyle("vi", parent=style, textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
    return P(brl_int(cents), st)


def estilos_celula(fs):
    c = ParagraphStyle(f"cell_{fs}", parent=styles["Normal"], fontSize=fs, leading=fs + 1.5)
    cb = ParagraphStyle(f"cellb_{fs}", parent=c, fontName="Helvetica-Bold")
    cr = ParagraphStyle(f"cellr_{fs}", parent=c, alignment=2)
    crb = ParagraphStyle(f"cellrb_{fs}", parent=cb, alignment=2)
    return c, cb, cr, crb


def larguras_por_conteudo(celulas, fs, folga=1.5):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    n = max(len(r) for r in celulas)
    out = []
    for j in range(n):
        w = 0.0
        for r in celulas:
            if j >= len(r):
                continue
            txt = getattr(r[j], "text", str(r[j]))
            txt = str(txt).replace("<b>", "").replace("</b>", "")
            w = max(w, stringWidth(txt, "Helvetica-Bold", fs) if j == 0 else stringWidth(txt, "Helvetica", fs))
        out.append(w + 12 + folga)
    return out


def tabela(rows, widths, fs=7.5):
    t = Table(rows, colWidths=widths, repeatRows=1)
    style = [("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), fs),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("BACKGROUND", (0, 0), (-1, 0), LARANJA), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
             ("LINEBELOW", (0, -1), (-1, -1), 0.7, LARANJA)]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), CINZA))
    t.setStyle(TableStyle(style))
    return t


def tabela_cat(titulo, grupos, total_label="Total", vazio="Nenhum lançamento neste grupo."):
    if not any(v for v, _ in grupos.values()):
        return [P(f"<b>{titulo}</b>", h2), P(vazio, sub)]
    rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nome, (v, n) in sorted(grupos.items(), key=lambda x: x[1][0]):
        rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tot = sum(v for v, _ in grupos.values())
    rows.append([P(f"<b>{total_label}</b>", cellrb),
                 P(f"<b>{sum(n for _, n in grupos.values())}</b>", cellc), P_val(tot, cellrb)])
    t = tabela(rows, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), LARANJA_CLARO)]))
    return [P(f"<b>{titulo}</b>", h2), t]


ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_BracoDoNorte.pdf"
ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_BracoDoNorte.xlsx"


def rodape(canvas, doc_):
    if os.path.exists(SIMBOLO):
        alt = 1.1 * cm
        larg = alt * 372 / 553
        canvas.drawImage(SIMBOLO, canvas._pagesize[0] - 1.5 * cm - larg, 1.0 * cm,
                         width=larg, height=alt, mask="auto")
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawRightString(canvas._pagesize[0] - 1.5 * cm, 0.55 * cm, f"pág. {doc_.page}")


_ml, _mr, _mt, _mb = 1.5 * cm, 1.5 * cm, 1.3 * cm, 1.7 * cm
_marg = dict(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
fr_r = Frame(_ml, _mb, A4[0] - _ml - _mr, A4[1] - _mt - _mb, **dict(_marg, id="fr_r"))
fr_l = Frame(_ml, _mb, landscape(A4)[0] - _ml - _mr, landscape(A4)[1] - _mt - _mb, **dict(_marg, id="fr_l"))
LARG_PAIS = landscape(A4)[0] - _ml - _mr

doc = BaseDocTemplate(ARQ_PDF, pagesize=A4, leftMargin=_ml, rightMargin=_mr,
                      topMargin=_mt, bottomMargin=_mb,
                      title=f"Relatório Gerencial — {CLIENTE}")
doc.addPageTemplates([
    PageTemplate(id="paisagem", frames=[fr_l], onPage=rodape, pagesize=landscape(A4)),
    PageTemplate(id="retrato", frames=[fr_r], onPage=rodape, pagesize=A4),
])
E = []

h1c = ParagraphStyle("h1c", parent=h1, fontSize=13, alignment=1, spaceAfter=0)
h2c = ParagraphStyle("h2c", parent=h2, fontSize=10, alignment=1, spaceBefore=0, spaceAfter=1)
subc = ParagraphStyle("subc", parent=sub, fontSize=7.5, alignment=1, spaceAfter=0)


def capa():
    els = [NextPageTemplate("paisagem")]
    if os.path.exists(LOGO):
        img = RLImage(LOGO, width=2.6 * cm, height=2.6 * cm * 1501 / 2668)
        img.hAlign = "CENTER"
        els.append(img)
    els.append(Spacer(1, 3))
    els.append(P(f"<b>{CLIENTE}</b>", h1c))
    els.append(P("Relatório Gerencial Mensal", h2c))
    els.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · "
                 f"Ref.: {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} — regime de caixa", subc))
    els.append(Spacer(1, 2))
    return els


def bloco_comparativo():
    els = [P("<b>Comparativo por Categoria</b>", h2)]
    els.append(P(f"Últimos 13 Meses "
                 f"({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) "
                 f"— regime de caixa (baixado + agendado, mês da baixa); transferências entre contas fora", sub))
    meses = meses_mov
    n_col = len(meses)
    fs_cm = 6.5 if n_col <= 8 else 5.8
    _c, _cb, _cr, _crb = estilos_celula(fs_cm)

    def _v(cents, forte=False):
        st = _crb if forte else _cr
        st = ParagraphStyle(f"vc{fs_cm}", parent=st,
                            textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
        return P(brl_int(cents), st)

    cats = sorted({c for c in matriz}, key=lambda c: -sum(matriz[c].values()))
    rows = [[P("<b>Categoria</b>", _cb)] + [P(f"<b>{lab}</b>", _crb) for _, lab, _ in meses]
            + [P("<b>Média</b>", _crb), P("<b>Total</b>", _crb)]]
    for cat in cats:
        vals = [matriz[cat].get(k, 0) for _, _, k in meses]
        row = [P(cat, _c)] + [_v(v) if v else P("—", _cr) for v in vals]
        row += [_v(round(sum(vals) / len(vals)), True), _v(sum(vals), True)]
        rows.append(row)
    res = [sum(v[k] for v in matriz.values()) for _, _, k in meses]
    rows.append([P("<b>Variação do caixa no mês</b>", _cb)] + [_v(v, True) for v in res]
                + [_v(round(sum(res) / len(res)), True), _v(sum(res), True)])

    _ws = larguras_por_conteudo([[getattr(c, "text", str(c)) for c in r] for r in rows], fs_cm)
    _cat = _ws[0]
    _resto = LARG_PAIS - _cat
    _outs = sum(_ws[1:]) or 1
    _ws = [_cat] + [w * _resto / _outs for w in _ws[1:]]
    if sum(_ws) > LARG_PAIS:
        _cat = max(5.0 * cm, _ws[0] - (sum(_ws) - LARG_PAIS))
        _resto2 = LARG_PAIS - _cat
        _o2 = sum(_ws[1:]) or 1
        _ws = [_cat] + [w * _resto2 / _o2 for w in _ws[1:]]
    els.append(tabela(rows, _ws, fs=fs_cm))
    return els


def bloco_mes():
    """Receitas e Despesas do mês anterior, com cada natureza demonstrada à parte."""
    els = [NextPageTemplate("retrato"), PageBreak()]
    els.append(P(f"Receitas e Despesas — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de caixa)", h2))
    r = [[P("<b>Item</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]

    def _bloco(titulo, chaves, total_label, total_val, sinal=None):
        sub_rows = [(c, v, n) for c, (v, n) in D["por_cat"].items() if chaves(c) and v]
        if not sub_rows and not total_val:
            return
        r.append([P(f"<b>{titulo}</b>", cellb), P("", cellc), P("", cellr)])
        for c, v, n in sorted(sub_rows):
            r.append([P(c, cell), P(str(n), cellc), P_val(v, cellr)])
        r.append([P(f"<b>{total_label}</b>", cellrb),
                  P(f"<b>{sum(n for _, _, n in sub_rows)}</b>", cellc), P_val(total_val, cellrb)])

    _bloco("Receitas operacionais", eh_receita, "Total de Receitas Operacionais", D["receita_op"])
    _bloco("Despesas operacionais", eh_desp_op, "Total de Despesas Operacionais", D["desp_op"])
    if D["juros"]:
        _bloco("Juros de aplicação financeira", eh_juros, "Total de Juros", D["juros"])
    r.append([P("<b>Resultado operacional do mês</b>", cellrb), P("", cellc), P_val(D["resultado"], cellrb)])

    # naturezas que NÃO são resultado: demonstradas e subtraídas
    if D["aportes"] or D["ent_empr"]:
        _bloco("Aportes dos sócios", eh_aporte, "(−) Total de Aportes", D["aportes"])
    if D["ent_empr"]:
        _bloco("Entradas de empréstimo", eh_ent_empr, "(−) Total de Entradas de Empréstimo", D["ent_empr"])
    if D["sai_empr"]:
        _bloco("Saídas de empréstimo", eh_sai_empr, "(−) Total de Saídas de Empréstimo", D["sai_empr"])
    if D["capex"]:
        _bloco("Investimento na obra (CAPEX)", eh_capex, "(−) Total de Investimentos", D["capex"])
    if D["outros"]:
        r.append([P("Lançamentos em Outros (a classificar)", cell), P("", cellc), P_val(D["outros"], cellr)])
    r.append([P("<b>Variação do caixa no mês</b>", cellrb), P("", cellc), P_val(D["variacao"], cellrb)])

    t = tabela(r, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 2), (-1, len(r) - 1), LARANJA_CLARO)]))
    els.append(t)
    els.append(P("Resultado operacional = receitas operacionais menos despesas operacionais, mais juros de "
                 "aplicação. Aporte dos sócios, empréstimos e investimento na obra entram no caixa mas não "
                 "são resultado: aparecem demonstrados e subtraídos até a variação do caixa.", sub))
    return els


def bloco_indicadores():
    """Nº hóspedes e ticket médio (Controlle) + situação de empréstimos por contraparte."""
    els = [NextPageTemplate("paisagem"), PageBreak()]
    els.append(P("Hóspedes e Ticket Médio", h2))
    fs_i = 6.5 if len(meses_mov) > 10 else 7.5
    _c, _cb, _cr, _crb = estilos_celula(fs_i)

    def _cel(txt):
        return P(str(txt), _cr)

    rows = [[P("<b>Indicador</b>", _cb)] + [P(f"<b>{lab}</b>", _crb) for _, lab, _ in meses_mov]]
    rows.append([P("Nº Hóspedes", _c)] + [_cel(hosp_serie.get(k) or "—") for _, _, k in meses_mov])
    rows.append([P("Ticket Médio", _c)]
                + [_cel(_brl_sem_rs(ticket_serie.get(k)) if ticket_serie.get(k) else "—")
                   for _, _, k in meses_mov])
    _ws = larguras_por_conteudo([[getattr(c, "text", str(c)) for c in r] for r in rows], fs_i)
    _cat = max(8.0 * cm, _ws[0])
    _resto = LARG_PAIS - _cat
    _o = sum(_ws[1:]) or 1
    els.append(tabela(rows, [_cat] + [w * _resto / _o for w in _ws[1:]], fs=fs_i))
    els.append(P("Hóspede = contato distinto que pagou mensalidade (categoria 01.01) no mês de caixa; "
                 "contato com mais de um pagamento no mês conta uma vez. Ticket = soma das mensalidades "
                 "dividida pelo número de hóspedes.", sub))

    if emp_13:
        els.append(NextPageTemplate("retrato"))
        els.append(PageBreak())
        els.append(P("Empréstimos por contraparte (13 meses, caixa)", h2))
        rr = [[P("<b>Contraparte</b>", cell), P("<b>Lançamentos</b>", cellc),
               P("<b>Saiu</b>", cellr), P("<b>Voltou</b>", cellr), P("<b>Posição</b>", cellr)]]
        tot = [0, 0, 0]
        for nome, (saiu, voltou, n) in sorted(emp_13.items(), key=lambda x: x[1][2]):
            rr.append([P(nome, cell), P(str(n), cellc), P_val(saiu, cellr),
                       P_val(voltou, cellr) if voltou else P("—", cellr),
                       P_val(saiu + voltou, cellrb)])
            tot[0] += saiu; tot[1] += voltou; tot[2] += n
        rr.append([P("<b>Total</b>", cellrb), P(f"<b>{tot[2]}</b>", cellc), P_val(tot[0], cellrb),
                   P_val(tot[1], cellrb), P_val(tot[0] + tot[1], cellrb)])
        t = tabela(rr, [6.6 * cm, 2.4 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm], fs=7.5)
        t.setStyle(TableStyle([("BACKGROUND", (0, len(rr) - 1), (-1, len(rr) - 1), LARANJA_CLARO)]))
        els.append(t)
        els.append(P("Posição = saídas menos entradas no período: valor líquido a receber da contraparte. "
                     "Unidade independente: estes empréstimos são com terceiros, não movimento entre casas "
                     "do mesmo grupo.", sub))
    return els


def _brl_sem_rs(v):
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def bloco_aberto_previsao():
    els = [Spacer(1, 12)]
    els.append(P(f"Despesas em aberto até {FIM_MES_ANT_LABEL}", h2))
    els += tabela_cat("Resumo por categoria", g_aberto, total_label="Total em aberto",
                      vazio="Nenhuma despesa em aberto na data de referência.")
    if g_aberto_rec:
        els += tabela_cat("Receitas em aberto (inadimplência) até " + FIM_MES_ANT_LABEL,
                          g_aberto_rec, total_label="Total a receber")
    els.append(P("Em aberto = lançamento ainda não baixado com vencimento até a data de referência. "
                 "Não entra no caixa; aparece aqui como posição.", sub))
    els.append(Spacer(1, 12))
    els.append(P(f"Previsão de {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (ainda não baixado)", h2))
    pr = [[P("<b>Item</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    pr.append([P("<b>Receitas previstas</b>", cellb), P("", cellc), P("", cellr)])
    for nome, (v, n) in sorted(prev_rec.items(), key=lambda x: -x[1][0]):
        pr.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tr = sum(v for v, _ in prev_rec.values())
    pr.append([P("<b>Total previsto</b>", cellrb), P(f"<b>{sum(n for _, n in prev_rec.values())}</b>", cellc),
               P_val(tr, cellrb)])
    if prev_desp:
        pr.append([P("<b>Despesas previstas</b>", cellb), P("", cellc), P("", cellr)])
        for nome, (v, n) in sorted(prev_desp.items(), key=lambda x: x[1][0]):
            pr.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
        td = sum(v for v, _ in prev_desp.values())
        pr.append([P("<b>Total de Despesas Previstas</b>", cellrb),
                   P(f"<b>{sum(n for _, n in prev_desp.values())}</b>", cellc), P_val(td, cellrb)])
        pr.append([P("<b>Resultado previsto do mês</b>", cellrb), P("", cellc), P_val(tr + td, cellrb)])
    t = tabela(pr, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(pr) - 1), (-1, len(pr) - 1), LARANJA_CLARO)]))
    els.append(t)
    return els


def bloco_fluxo_proj():
    els = [PageBreak()]
    els.append(P(f"Fluxo de Caixa — Últimos 13 Meses "
                 f"({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) "
                 f"— realizado", h2))
    rows = [[P("<b>Mês</b>", cell), P("<b>Saldo inicial</b>", cellr), P("<b>Entradas</b>", cellr),
             P("<b>Saídas</b>", cellr), P("<b>Saldo final</b>", cellr)]]
    for lab, si, e, x, sf in fluxo:
        rows.append([P(lab, cell), P_val(si, cellr), P_val(e, cellr), P_val(x, cellr), P_val(sf, cellrb)])
    t = tabela(rows, [3.0 * cm, 3.6 * cm, 3.4 * cm, 3.4 * cm, 3.6 * cm], fs=7.5)
    els.append(t)
    els.append(P("Entradas e saídas realizadas nas contas da unidade, baixadas no período, sem transferências "
                 "entre contas. Saldo final conferido contra o saldo real das contas no Controlle.", sub))

    els.append(Spacer(1, 14))
    els.append(P(f"Projeção de Fluxo de Caixa — Próximos 12 Meses "
                 f"({MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} a "
                 f"{MES_PT[add_months(MES_COR, 11).month].capitalize()} de {add_months(MES_COR, 11).year})", h2))
    rows6 = [[P("<b>Mês</b>", cell), P("<b>Entradas previstas</b>", cellr),
              P("<b>Saídas previstas</b>", cellr), P("<b>Saldo previsto</b>", cellr)]]
    for lab, e, x, s in proj_ac:
        rows6.append([P(lab, cell), P_val(e, cellr), P_val(x, cellr), P_val(s, cellrb)])
    t = tabela(rows6, [3.2 * cm, 4.4 * cm, 4.4 * cm, 4.6 * cm], fs=7.5)
    els.append(t)
    els.append(P(f"Saldo de partida = saldo real em {FIM_MES_ANT_LABEL}; movimentos = lançamentos previstos e "
                 f"pendentes já registrados no Controlle.", sub))
    return els


def bloco_classificar():
    els = [PageBreak()]
    els.append(P("Lançamentos em Outros (a classificar)", h2))
    els.append(P(f"Lançamentos de caixa dos últimos 13 meses na categoria Outros ou sem categoria "
                 f"({len(a_classificar)} lançamentos). Entram na variação do caixa, mas não pertencem a "
                 f"nenhuma natureza do relatório enquanto não forem classificados na origem.", sub))
    if a_classificar:
        rows = [[P("<b>Data</b>", cell), P("<b>Descrição</b>", cell), P("<b>Conta</b>", cell),
                 P("<b>Valor</b>", cellr)]]
        for t_ in a_classificar:
            dt = bdate(t_)
            rows.append([P(f"{dt[8:10]}/{dt[5:7]}/{dt[:4]}", cell),
                         P((t_.get("ds_transaction") or "")[:60], cell),
                         P(t_.get("ds_account_main") or "", cell), P_val(valor_efetivo(t_), cellr)])
        rows.append([P("<b>Total</b>", cellrb), P(f"<b>{len(a_classificar)} lançamentos</b>", cellrb),
                     P("", cellc), P_val(sum(valor_efetivo(t_) for t_ in a_classificar), cellrb)])
        t = tabela(rows, [2.2 * cm, 8.2 * cm, 3.6 * cm, 3.0 * cm], fs=7.5)
        t.setStyle(TableStyle([("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), LARANJA_CLARO)]))
        els.append(t)
    else:
        els.append(P("Nenhum lançamento pendente de classificação.", sub))
    return els


# ---- documento ----
E += capa()
E += bloco_comparativo()
E += bloco_mes()
E += bloco_indicadores()
E += bloco_aberto_previsao()
E += bloco_fluxo_proj()
E += bloco_classificar()

doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== EXCEL =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

wb = Workbook()
ws0 = wb.active
ws0.title = "Resumo"
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
TOT = ("Total", "Resultado", "Variação", "Previsão", "Total de", "Total em", "Total previsto",
       "(−)", "Posição")
r_ = lambda v: v / 100


def aba(nome, linhas, larguras, titulo=None):
    ws = wb.create_sheet(nome[:31])
    desloc = 0
    if titulo:
        ws.append((titulo,))
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(1, len(larguras)))
        c = ws.cell(row=1, column=1)
        c.font = Font(bold=True, size=12, color="FF501C")
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 22
        desloc = 1
    for r in linhas:
        ws.append(list(r))
    hdr = desloc + 1
    headers = [str(ws.cell(row=hdr, column=j).value or "") for j in range(1, ws.max_column + 1)]
    for c in ws[hdr]:
        c.fill = FILL_H; c.font = FH
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=hdr + 1):
        label = str(row[0].value or "")
        is_tot = label.startswith(TOT)
        if is_tot:
            for c in row:
                c.fill = FILL_T
                c.alignment = Alignment(horizontal="center", vertical="center")
            row[0].font = FB
        for j, c in enumerate(row[1:], 2):
            if isinstance(c.value, (int, float)):
                h = headers[j - 1] if j - 1 < len(headers) else ""
                if "Lançamentos" in h:
                    c.number_format = "0"; c.font = Font(bold=is_tot)
                else:
                    c.number_format = '"R$" #,##0.00'
                    cor = VERDE_XL if c.value > 0 else (VERMELHO_XL if c.value < 0 else "1A1A1A")
                    c.font = Font(bold=is_tot, color=cor)
    for j, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=hdr + 1, column=1)
    return ws

# --- aba Resumo (índice) ---
ws0.append(("Relatório Gerencial — CENTROVITA BRAÇO DO NORTE",))
ws0.merge_cells("A1:D1")
ws0["A1"].font = Font(bold=True, size=13, color="FF501C")
ws0["A1"].alignment = Alignment(horizontal="center")
ws0.append((f"Unidade independente · regime de caixa · ref. {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year}",))
ws0.merge_cells("A2:D2")
ws0["A2"].alignment = Alignment(horizontal="center")
ws0["A2"].font = Font(italic=True, size=9, color="777777")
ws0.append(())
ws0.append(("Indicador", MES_PT[MES_ANT.month].capitalize(), "Acumulado 13 meses", "Observação"))
for c in ws0[4]:
    c.fill = FILL_H; c.font = FH; c.alignment = Alignment(horizontal="center")
acum = lambda f: sum(f(k) for _, _, _, k in MESES13)
resumo = [
    ("Receitas operacionais", r_(D["receita_op"]), r_(acum(lambda k: resumo_mes(k)["receita_op"]))),
    ("Despesas operacionais", r_(D["desp_op"]), r_(acum(lambda k: resumo_mes(k)["desp_op"]))),
    ("Resultado operacional", r_(D["resultado"]), r_(acum(lambda k: resumo_mes(k)["resultado"]))),
    ("Aportes dos sócios", r_(D["aportes"]), r_(acum(lambda k: resumo_mes(k)["aportes"]))),
    ("Entradas de empréstimo", r_(D["ent_empr"]), r_(acum(lambda k: resumo_mes(k)["ent_empr"]))),
    ("Saídas de empréstimo", r_(D["sai_empr"]), r_(acum(lambda k: resumo_mes(k)["sai_empr"]))),
    ("Investimento na obra (CAPEX)", r_(D["capex"]), r_(acum(lambda k: resumo_mes(k)["capex"]))),
    ("Variação do caixa", r_(D["variacao"]), r_(acum(lambda k: resumo_mes(k)["variacao"]))),
]
for label, v1, v2 in resumo:
    ws0.append((label, v1, v2, ""))
ws0.append(())
ws0.append(("Saldo em contas em " + FIM_MES_ANT_LABEL, r_(saldo_cc)))
ws0.append(("Nº hóspedes (ref.)", hosp_serie.get(REF)))
ws0.append(("Ticket médio (ref.)", ticket_serie.get(REF)))
for row in ws0.iter_rows(min_row=5):
    if isinstance(row[1].value, (int, float)):
        for c in row[1:3]:
            if isinstance(c.value, (int, float)):
                c.number_format = '"R$" #,##0.00'
                c.font = Font(color=(VERDE_XL if c.value > 0 else VERMELHO_XL if c.value < 0 else "1A1A1A"))
for j, w in enumerate([38, 20, 22, 40], 1):
    ws0.column_dimensions[get_column_letter(j)].width = w

# --- comparativo 13m ---
meses = meses_mov
cats = sorted({c for c in matriz}, key=lambda c: -sum(matriz[c].values()))
linhas = [("Categoria",) + tuple(lab for _, lab, _ in meses) + ("Média", "Total")]
for cat in cats:
    vals = [matriz[cat].get(k, 0) for _, _, k in meses]
    linhas.append((cat,) + tuple(r_(v) if v else None for v in vals)
                  + (r_(round(sum(vals) / len(vals))), r_(sum(vals))))
res = [sum(v[k] for v in matriz.values()) for _, _, k in meses]
linhas.append(("Variação do caixa no mês",) + tuple(r_(v) for v in res)
              + (r_(round(sum(res) / len(res))), r_(sum(res))))
aba("Comp 13m", linhas, [42] + [11] * len(meses) + [12, 14],
    titulo="CENTROVITA BRAÇO DO NORTE — Comparativo dos Últimos 13 Meses por Categoria (regime de caixa)")

# --- mês anterior ---
lm = [("Item", "Lançamentos", "Valor"), ("Receitas operacionais", None, None)]
for k, (v, n) in sorted(D["por_cat"].items()):
    if eh_receita(k) and v:
        lm.append((k, n, r_(v)))
lm.append(("Total de Receitas Operacionais", None, r_(D["receita_op"])))
lm.append(("Despesas operacionais", None, None))
for k, (v, n) in sorted(D["por_cat"].items()):
    if eh_desp_op(k) and v:
        lm.append((k, n, r_(v)))
lm.append(("Total de Despesas Operacionais", None, r_(D["desp_op"])))
if D["juros"]:
    lm.append(("Juros Aplicação Financeira", None, r_(D["juros"])))
lm.append(("Resultado operacional do mês", None, r_(D["resultado"])))
for rot, chave in (("Aportes dos sócios", "aportes"), ("Entradas de empréstimo", "ent_empr"),
                   ("Saídas de empréstimo", "sai_empr"), ("Investimento na obra (CAPEX)", "capex")):
    if D[chave]:
        lm.append((rot, None, None))
        fn = {"aportes": eh_aporte, "ent_empr": eh_ent_empr,
              "sai_empr": eh_sai_empr, "capex": eh_capex}[chave]
        for k, (v, n) in sorted(D["por_cat"].items()):
            if fn(k) and v:
                lm.append((k, n, r_(v)))
        lm.append((f"(−) Total de {rot}", None, r_(D[chave])))
if D["outros"]:
    lm.append(("Lançamentos em Outros (a classificar)", None, r_(D["outros"])))
lm.append(("Variação do caixa no mês", None, r_(D["variacao"])))
aba("Mes ant", lm, [52, 14, 16],
    titulo=f"CENTROVITA BRAÇO DO NORTE — Receitas e Despesas de {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (caixa)")

# --- hóspedes e ticket ---
lh = [("Mês", "Nº Hóspedes", "Ticket Médio")]
for _, lab, key in meses:
    lh.append((lab, hosp_serie.get(key), ticket_serie.get(key)))
ws_h = aba("Hospedes e Ticket", lh, [14, 16, 16],
           titulo="CENTROVITA BRAÇO DO NORTE — Hóspedes e Ticket Médio (mensalidades pagas, caixa)")
for row in ws_h.iter_rows(min_row=3):
    for c in row[1:]:
        if isinstance(c.value, (int, float)):
            c.number_format = "0" if row[0].value and c.column == 2 else "#,##0.00"

# --- despesas em aberto ---
la = [("Categoria", "Lançamentos", "Valor")]
for k, (v, n) in sorted(g_aberto.items()):
    la.append((k, n, r_(v)))
la.append(("Total em aberto", sum(n for _, n in g_aberto.values()), r_(sum(v for v, _ in g_aberto.values()))))
aba("Despesas em aberto", la, [46, 14, 16],
    titulo=f"CENTROVITA BRAÇO DO NORTE — Despesas em aberto até {FIM_MES_ANT_LABEL}")

# --- receitas em aberto ---
lr = [("Categoria", "Lançamentos", "Valor")]
for k, (v, n) in sorted(g_aberto_rec.items(), key=lambda x: -x[1][0]):
    lr.append((k, n, r_(v)))
lr.append(("Total a receber", sum(n for _, n in g_aberto_rec.values()),
           r_(sum(v for v, _ in g_aberto_rec.values()))))
aba("Receitas em aberto", lr, [46, 14, 16],
    titulo=f"CENTROVITA BRAÇO DO NORTE — Receitas em aberto (inadimplência) até {FIM_MES_ANT_LABEL}")

# --- previsão ---
lp = [("Item", "Lançamentos", "Valor"), ("Receitas previstas", None, None)]
for k, (v, n) in sorted(prev_rec.items(), key=lambda x: -x[1][0]):
    lp.append((k, n, r_(v)))
tr_ = sum(v for v, _ in prev_rec.values())
lp.append(("Total previsto", sum(n for _, n in prev_rec.values()), r_(tr_)))
if prev_desp:
    lp.append(("Despesas previstas", None, None))
    for k, (v, n) in sorted(prev_desp.items(), key=lambda x: x[1][0]):
        lp.append((k, n, r_(v)))
    td_ = sum(v for v, _ in prev_desp.values())
    lp.append(("Total de Despesas Previstas", sum(n for _, n in prev_desp.values()), r_(td_)))
    lp.append(("Resultado previsto do mês", None, r_(tr_ + td_)))
aba("Previsao mes", lp, [46, 14, 16],
    titulo=f"CENTROVITA BRAÇO DO NORTE — Previsão de {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (não baixado)")

# --- fluxo 13m ---
aba("Fluxo 13m",
    [("Mês", "Saldo inicial", "Entradas", "Saídas", "Saldo final")] +
    [(lab, r_(a), r_(b), r_(c), r_(e)) for lab, a, b, c, e in fluxo],
    [10, 16, 16, 16, 16],
    titulo="CENTROVITA BRAÇO DO NORTE — Fluxo de Caixa dos Últimos 13 Meses (realizado)")

# --- projeção 12m ---
aba("Proj 12m",
    [("Mês", "Entradas previstas", "Saídas previstas", "Saldo previsto")] +
    [(lab, r_(e), r_(x), r_(s)) for lab, e, x, s in proj_ac],
    [10, 18, 18, 18],
    titulo="CENTROVITA BRAÇO DO NORTE — Projeção de Fluxo de Caixa — Próximos 12 Meses")

# --- empréstimos ---
le = [("Contraparte", "Lançamentos", "Saiu", "Voltou", "Posição")]
for nome, (saiu, voltou, n) in sorted(emp_13.items(), key=lambda x: x[1][2]):
    le.append((nome, n, r_(saiu), r_(voltou) if voltou else None, r_(saiu + voltou)))
le.append(("Total", sum(v[2] for v in emp_13.values()),
           r_(sum(v[0] for v in emp_13.values())), r_(sum(v[1] for v in emp_13.values())),
           r_(sum(v[0] + v[1] for v in emp_13.values()))))
aba("Emprestimos", le, [40, 14, 16, 16, 16],
    titulo="CENTROVITA BRAÇO DO NORTE — Empréstimos por Contraparte (13 meses, caixa)")

# --- a classificar ---
lc = [("Data", "Descrição", "Conta", "Valor")]
for t_ in a_classificar:
    lc.append((bdate(t_), (t_.get("ds_transaction") or "")[:60], t_.get("ds_account_main") or "",
               r_(valor_efetivo(t_))))
lc.append(("Total", f"{len(a_classificar)} lançamentos", "", r_(sum(valor_efetivo(t_) for t_ in a_classificar))))
ws_c = aba("A classificar", lc, [12, 52, 26, 16],
           titulo="CENTROVITA BRAÇO DO NORTE — Lançamentos em Outros / sem categoria (13 meses, caixa)")
for row in ws_c.iter_rows(min_row=3):
    if isinstance(row[0].value, str) and len(row[0].value) == 10 and row[0].value[4] == "-":
        row[0].number_format = "DD/MM/YYYY"

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
