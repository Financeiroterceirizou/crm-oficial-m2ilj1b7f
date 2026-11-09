#!/usr/bin/env python3
# Relatório Gerencial — CENTROVITA SENIOR LIVING (MAURO RAMOS + BARRA DA LAGOA)
# REGIME DE CAIXA · separado por CENTRO DE CUSTO + CONSOLIDADO
# v1.0, 2026-11-09 — pedido do Vinícius: "relatórios da Centrovita Mauro Ramos por regime de
# caixa, separando por centro de custo e também fazendo um relatório unificado".
# Molde: relatorio_giane_zanelato / relatorio_revitalizy (regime de caixa).
#
# REGIME DE CAIXA: situation in (1,2) = pago + agendado, mês apurado por dt_billing.
# FONTE DO CAIXA POR CENTRO DE CUSTO: balances com id_cost_centers=<id> — descoberta desta
# rodada. Ele devolve revenuesDone/expensesDone/balanceDone DO CC e fecha exato, mês a mês,
# com a soma da lista (situation 1,2, sem transferências) do mesmo CC. A trava abaixo prova
# isso nos 13 meses antes de gerar qualquer página.
# TRAP: previousDayBalance NÃO respeita id_cost_centers (volta o total da licença). O saldo
# inicial de cada mês tem de ser o balanceDone do mês anterior, nunca o previousDayBalance.
# USO: python3 relatorio_centrovita_caixa.py [YYYY-MM-DD]   (default: hoje)
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
TOKEN = os.environ.get("CONTROLLE_TOKEN_CVMR") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}

LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")
VERDE = colors.HexColor("#1a7f37")
VERMELHO = colors.HexColor("#c0392b")
LOGO = os.path.join(_dir, "logo-centrovita.png")
LOGO_T = os.path.join(_dir, "logo-terceirizou.png")
SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")

CLIENTE = "CENTROVITA SENIOR LIVING"
UNIDADES = [("MAURO RAMOS", 157108), ("BARRA DA LAGOA", 157107)]

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}

# ---- classificação das categorias (regra Vinícius: aporte e dividendo FORA do resultado) ----
APORTE = "Aporte dos Socios"
JUROS = "Juros Aplicacao Financeira"
CAPEX = "Investimento na Obra (Projetos e Estrutura)"
TRANSF = "Transferencias entre Contas"
OUTROS = "Outros"

def eh_aporte(c):  return c == APORTE
def eh_juros(c):   return c == JUROS
def eh_capex(c):   return c == CAPEX
def eh_despesa_op(c):  return not (eh_aporte(c) or eh_juros(c) or eh_capex(c))


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
                time.sleep(3 * (i + 1)); continue
            raise
        except (http.client.IncompleteRead, OSError, ValueError):
            if i < tries - 1:
                time.sleep(5 * (i + 1)); continue
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


def bal(ini, fim, cid=None):
    u = f"{BASE}/transaction/v1/transactions/balances?start_date={ini}&end_date={fim}"
    if cid:
        u += f"&id_cost_centers={cid}"
    return req(u)["results"]


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
    return (a[0].get("ds_category") or "?") if a else "(sem categoria)"


def ccs(t):
    return {(a.get("ds_cost_center") or "").upper() for a in (t.get("apportionments_cost_center") or [])}


def ok_caixa(t):
    """Fora do relatório: transferência entre contas (type==1 é a marca canônica)."""
    if t.get("type") == 1:
        return False
    for c in (t.get("apportionments_plan_account") or []):
        d = (c.get("ds_category") or "")
        if d.startswith("99.01") or d.lower().startswith("transfer"):
            return False
    return True


def valor_efetivo(t):
    """O que de fato entrou/saiu: em pago com ajuste vale payment_in_cent (fecha com balances)."""
    if t.get("situation") in (1, 2) and t.get("payment_in_cent") is not None:
        return t["payment_in_cent"]
    return t["value_in_cent"]


def agrupa(txs, so_negativas=False, so_positivas=False, filtro=None):
    g = defaultdict(lambda: [0, 0])
    for t in txs:
        c = cat_nome(t)
        v = valor_efetivo(t)
        if filtro and not filtro(c):
            continue
        if so_negativas and v >= 0: continue
        if so_positivas and v <= 0: continue
        g[c][0] += v
        g[c][1] += 1
    return g


# ===== datas =====
HOJE = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
MES_ANT = add_months(HOJE.replace(day=1), -1)
FIM_MES_ANT = (MES_ANT.replace(day=28) + timedelta(days=4))
FIM_MES_ANT = FIM_MES_ANT - timedelta(days=FIM_MES_ANT.day)
MES_COR = HOJE.replace(day=1)
FIM_MES_COR = (MES_COR.replace(day=28) + timedelta(days=4))
FIM_MES_COR = FIM_MES_COR - timedelta(days=FIM_MES_COR.day)
REF = f"{MES_ANT.year}-{MES_ANT.month:02d}"
HOJE_LABEL = HOJE.strftime("%d/%m/%Y")
FIM_MES_ANT_LABEL = FIM_MES_ANT.strftime("%d/%m/%Y")

INI_13 = add_months(MES_ANT, -12)
MESES13 = []
_m = INI_13
while _m <= MES_ANT:
    _f = add_months(_m, 1) - timedelta(days=1)
    MESES13.append((_m.isoformat(), _f.isoformat(), f"{MES_AB[_m.month]}/{str(_m.year)[2:]}", f"{_m.year}-{_m.month:02d}"))
    _m = add_months(_m, 1)

print(f"período do comparativo: {MESES13[0][3]} a {MESES13[-1][3]}  · ref {REF}")

# ===== dados =====
_tx = []
for y in sorted({INI_13.year, MES_ANT.year, MES_COR.year, add_months(MES_COR, 12).year}):
    _tx.extend(tx_list(f"{y}-01-01", f"{y}-12-31"))
_vistos, _ded = set(), []
for t in _tx:
    k = t.get("id_transactions_payments")
    if k is None:
        k = (t.get("id_transactions"), t.get("value_in_cent"), bdate(t), t.get("situation"))
    if k in _vistos: continue
    _vistos.add(k); _ded.append(t)
_tx = _ded
print(f"lançamentos: {len(_tx)}")


def dados_cc(nome, cid):
    def do_cc(t):
        return nome in ccs(t)

    # 1. comparativo 13m em CAIXA (mês por dt_billing)
    matriz = defaultdict(lambda: defaultdict(int))
    for t in _tx:
        if not ok_caixa(t) or t.get("situation") not in (1, 2) or not do_cc(t):
            continue
        mes = bdate(t)[:7]
        if mes < MESES13[0][3] or mes > MESES13[-1][3]:
            continue
        matriz[cat_nome(t)][mes] += valor_efetivo(t)

    meses_mov = [(fim, lab, key) for _, fim, lab, key in MESES13
                 if any(v[key] for v in matriz.values())]

    # 2. mês anterior em caixa
    tx_ant = [t for t in _tx if bdate(t)[:7] == REF and t.get("situation") in (1, 2)
              and ok_caixa(t) and do_cc(t)]
    ant_rec = agrupa(tx_ant, so_positivas=True)
    ant_desp = agrupa(tx_ant, so_negativas=True, filtro=eh_despesa_op)
    ant_capex = agrupa(tx_ant, filtro=eh_capex)
    ant_entradas = sum(v for v, _ in ant_rec.values())
    ant_saidas = sum(v for v, _ in ant_desp.values())
    ant_capex_tot = sum(v for v, _ in ant_capex.values())
    ant_aportes = sum(v for c, (v, _) in ant_rec.items() if eh_aporte(c))
    ant_juros = sum(v for c, (v, _) in ant_rec.items() if eh_juros(c))
    ant_resultado = ant_juros + ant_saidas          # resultado sem aporte e sem capex
    ant_variacao = ant_entradas + ant_saidas + ant_capex_tot

    # 3. despesas em aberto até o último dia do mês anterior
    aberto = [t for t in _tx if t.get("activity_type") == 0 and t.get("situation") == 0
              and bdate(t) <= FIM_MES_ANT.isoformat() and ok_caixa(t) and do_cc(t)]
    g_aberto = agrupa(aberto, filtro=eh_despesa_op)

    # 4. previsão do mês corrente (pago + pendente)
    prev = [t for t in _tx if MES_COR.isoformat() <= bdate(t) <= FIM_MES_COR.isoformat()
            and ok_caixa(t) and do_cc(t)]
    prev_rec = agrupa(prev, so_positivas=True)
    prev_desp = agrupa(prev, so_negativas=True, filtro=eh_despesa_op)
    prev_capex = agrupa(prev, filtro=eh_capex)

    # 5. fluxo 13m REALIZADO — fonte canônica: balances por CC
    fluxo = []
    primeiro = MESES13[0][0]
    dia_antes = (date.fromisoformat(primeiro) - timedelta(days=1)).isoformat()
    s_ini = bal("2017-01-01", dia_antes, cid)["balanceDone"]
    for _, fim, lab, _ in MESES13:
        ini_m = fim[:8] + "01"
        b = bal(ini_m, fim, cid)
        e = b.get("revenuesDone", 0) or 0
        x = b.get("expensesDone", 0) or 0
        sf = b["balanceDone"]
        # TRAVA 1: entradas + saídas explicam a variação real do saldo
        if s_ini + e + x != sf:
            raise SystemExit(f"ERRO fluxo {nome} {lab}: {s_ini} + {e} + {x} != {sf}")
        # TRAVA 2: balances == lista do mesmo mês (prova de que a paginação não perdeu linha)
        lt = [t for t in _tx if bdate(t)[:7] == fim[:7] and t.get("situation") in (1, 2)
              and ok_caixa(t) and do_cc(t)]
        le = sum(valor_efetivo(t) for t in lt if t["activity_type"] == 1)
        lx = sum(valor_efetivo(t) for t in lt if t["activity_type"] == 0)
        if le != e or lx != x:
            raise SystemExit(f"ERRO lista x balances {nome} {lab}: lista {le}/{lx} bal {e}/{x}")
        fluxo.append((lab, s_ini, e, x, sf))
        s_ini = sf
    saldo_cc = fluxo[-1][4]

    # 6. projeção 12m (lançamentos previstos)
    proj = []
    for i in range(1, 13):
        ini_m = add_months(MES_COR, i - 1)
        fim_m = add_months(ini_m, 1) - timedelta(days=1)
        lab = f"{MES_AB[ini_m.month]}/{str(ini_m.year)[2:]}"
        txs_m = [t for t in _tx if ini_m.isoformat() <= bdate(t) <= fim_m.isoformat() and ok_caixa(t) and do_cc(t)]
        ent = sum(valor_efetivo(t) for t in txs_m if t["activity_type"] == 1)
        sai = sum(valor_efetivo(t) for t in txs_m if t["activity_type"] == 0)
        proj.append((lab, ent, sai))

    return dict(nome=nome, cid=cid, matriz=matriz, meses_mov=meses_mov,
                tx_ant=tx_ant, ant_rec=ant_rec, ant_desp=ant_desp, ant_capex=ant_capex,
                ant_entradas=ant_entradas, ant_saidas=ant_saidas, ant_capex_tot=ant_capex_tot,
                ant_aportes=ant_aportes, ant_juros=ant_juros, ant_resultado=ant_resultado,
                ant_variacao=ant_variacao, aberto=aberto, g_aberto=g_aberto,
                prev_rec=prev_rec, prev_desp=prev_desp, prev_capex=prev_capex,
                fluxo=fluxo, saldo_cc=saldo_cc, proj=proj)


print("buscando dados por centro de custo...")
D = {n: dados_cc(n, c) for n, c in UNIDADES}

# consolidado
tot_saldo_contas = bal("2017-01-01", FIM_MES_ANT.isoformat())["balanceDone"]

# ===== TRAVA DE CLASSIFICAÇÃO (regra do Vinícius, 09/11) =====
# TODOS os lançamentos precisam ter centro de custo. A ÚNICA exceção são as
# transferências entre contas, que não pertencem a unidade nenhuma e se anulam.
# Se aparecer lançamento que não é transferência e está sem centro de custo, o
# relatório NÃO é gerado: aborta com a lista, para o lançamento ser classificado
# na origem. Nenhum ajuste automático, nenhuma atribuição por conta própria —
# o número do relatório é sempre o número real do Controlle.
def _sem_cc_relevantes():
    """Lançamentos sem centro de custo que NÃO são transferência entre contas."""
    out = []
    for t in _tx:
        if ccs(t) or not t.get("value_in_cent"):
            continue
        d = (t.get("ds_transaction") or "").upper()
        cats = [(a.get("ds_category") or "") for a in (t.get("apportionments_plan_account") or [])]
        if d.startswith("TRANSFERÊNCIA") or d.startswith("TRANSFERENCIA"):
            continue
        if any(c.startswith("Transferencias") or c.startswith("99.01") for c in cats):
            continue
        out.append(t)
    return out

SEM_CC = _sem_cc_relevantes()
if SEM_CC:
    print("ERRO: lançamento sem centro de custo (só transferência pode ficar sem).")
    print("      Classifique na origem no Controlle e rode de novo. Nada foi gerado, nada será enviado.")
    for t in sorted(SEM_CC, key=bdate):
        print(f"  {bdate(t)}  {(t.get('ds_transaction') or '')[:56]:56s} "
              f"{t['value_in_cent']/100:>12,.2f}  conta={t.get('ds_account_main')}  "
              f"cat={(t.get('apportionments_plan_account') or [{}])[0].get('ds_category')}")
    raise SystemExit(11)

# sem lançamento pendente de classificação: a soma dos CCs tem de fechar com as contas.
_sobra = tot_saldo_contas - sum(D[n]["saldo_cc"] for n, _ in UNIDADES)
if _sobra:
    print(f"ERRO: soma dos centros de custo ({sum(D[n]['saldo_cc'] for n, _ in UNIDADES)/100:,.2f}) "
          f"não fecha com o total das contas ({tot_saldo_contas/100:,.2f}): diferença {_sobra/100:,.2f}.")
    print("      Todos os lançamentos já têm centro de custo, então a diferença é de transferência.")
    print("      Verifique no Controlle antes de gerar. Nada foi gerado, nada será enviado.")
    raise SystemExit(11)
print(f"trava de classificação OK: nenhum lançamento não-transferência sem centro de custo; "
      f"soma dos CCs = total das contas ({tot_saldo_contas/100:,.2f})")

C = {}
for campo in ("ant_rec", "ant_desp", "ant_capex", "g_aberto", "prev_rec", "prev_desp", "prev_capex"):
    g = defaultdict(lambda: [0, 0])
    for n, _ in UNIDADES:
        for k, (v, q) in D[n][campo].items():
            g[k][0] += v; g[k][1] += q
    C[campo] = g
for campo in ("ant_entradas", "ant_saidas", "ant_capex_tot", "ant_aportes", "ant_juros",
              "ant_resultado", "ant_variacao"):
    C[campo] = sum(D[n][campo] for n, _ in UNIDADES)
C["saldo_cc"] = sum(D[n]["saldo_cc"] for n, _ in UNIDADES)
C["aberto"] = [t for n, _ in UNIDADES for t in D[n]["aberto"]]
# matriz consolidada (mesma janela e mesmos meses com movimento das unidades)
C["matriz"] = defaultdict(lambda: defaultdict(int))
for n, _ in UNIDADES:
    for cat, serie in D[n]["matriz"].items():
        for k, v in serie.items():
            C["matriz"][cat][k] += v
C["fluxo"] = []
for i in range(len(MESES13)):
    lab = D[UNIDADES[0][0]]["fluxo"][i][0]
    si = D[UNIDADES[0][0]]["fluxo"][i][1] + D[UNIDADES[1][0]]["fluxo"][i][1]
    e = D[UNIDADES[0][0]]["fluxo"][i][2] + D[UNIDADES[1][0]]["fluxo"][i][2]
    x = D[UNIDADES[0][0]]["fluxo"][i][3] + D[UNIDADES[1][0]]["fluxo"][i][3]
    sf = D[UNIDADES[0][0]]["fluxo"][i][4] + D[UNIDADES[1][0]]["fluxo"][i][4]
    C["fluxo"].append((lab, si, e, x, sf))
C["proj_ac"], C["meses_mov"] = [], D[UNIDADES[0][0]]["meses_mov"]
_ac = C["saldo_cc"]
for i in range(12):
    ent = sum(D[n]["proj"][i][1] for n, _ in UNIDADES)
    sai = sum(D[n]["proj"][i][2] for n, _ in UNIDADES)
    lab = D[UNIDADES[0][0]]["proj"][i][0]
    _ac += ent + sai
    C["proj_ac"].append((lab, ent, sai, _ac))
for n, _ in UNIDADES:
    _ac = D[n]["saldo_cc"]
    pac = []
    for lab, ent, sai in D[n]["proj"]:
        _ac += ent + sai
        pac.append((lab, ent, sai, _ac))
    D[n]["proj_ac"] = pac

print(f"saldos por CC: " + " · ".join(f"{n} {D[n]['saldo_cc']/100:,.2f}" for n, _ in UNIDADES))
print(f"soma CC {C['saldo_cc']/100:,.2f} · total em contas {tot_saldo_contas/100:,.2f} · resíduo {(tot_saldo_contas - C['saldo_cc'])/100:,.2f}")

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


def tabela_cat(titulo, grupos, total_label="Total"):
    rows = [[P("<b>Categoria</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    for nome, (v, n) in sorted(grupos.items()):
        rows.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tot = sum(v for v, _ in grupos.values())
    rows.append([P(f"<b>{total_label}</b>", cellrb),
                 P(f"<b>{sum(n for _, n in grupos.values())}</b>", cellc), P_val(tot, cellrb)])
    t = tabela(rows, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), LARANJA_CLARO)]))
    return [P(f"<b>{titulo}</b>", h2), t]


ARQ_PDF = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_Caixa.pdf"


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
                      title="Relatório Gerencial — Centrovita Senior Living (Mauro Ramos + Barra da Lagoa)")
doc.addPageTemplates([
    PageTemplate(id="paisagem", frames=[fr_l], onPage=rodape, pagesize=landscape(A4)),
    PageTemplate(id="retrato", frames=[fr_r], onPage=rodape, pagesize=A4),
])
E = []

h1c = ParagraphStyle("h1c", parent=h1, fontSize=13, alignment=1, spaceAfter=0)
h2c = ParagraphStyle("h2c", parent=h2, fontSize=10, alignment=1, spaceBefore=0, spaceAfter=1)
subc = ParagraphStyle("subc", parent=sub, fontSize=7.5, alignment=1, spaceAfter=0)


def capa(titulo_unidade=None):
    els = [NextPageTemplate("paisagem")]
    if os.path.exists(LOGO):
        img = RLImage(LOGO, width=2.6 * cm, height=2.6 * cm * 1501 / 2668)
        img.hAlign = "CENTER"
        els.append(img)
    els.append(Spacer(1, 3))
    els.append(P(f"<b>{CLIENTE}</b>", h1c))
    if titulo_unidade:
        els.append(P(f"<b>{titulo_unidade}</b>", h2c))
    els.append(P("Relatório Gerencial Mensal", h2c))
    els.append(P(f"Gerado em {HOJE_LABEL} · Fonte: Controlle · "
                 f"Ref.: {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} — regime de caixa", subc))
    els.append(Spacer(1, 2))
    return els


def bloco_comparativo(d, titulo):
    """Comparativo 13m (caixa) + resumo do mês em duas colunas, na mesma página paisagem."""
    els = [P(f"<b>{titulo}</b>", h2)]
    els.append(P(f"Comparativo dos Últimos 13 Meses por Categoria "
                 f"({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) "
                 f"— regime de caixa (pago + agendado, mês da baixa)", sub))
    meses = d["meses_mov"]
    n_col = len(meses)
    fs_cm = 6.5 if n_col <= 8 else 5.8
    _c, _cb, _cr, _crb = estilos_celula(fs_cm)

    def _v(cents, forte=False):
        st = _crb if forte else _cr
        st = ParagraphStyle(f"vc{fs_cm}", parent=st,
                            textColor=(VERDE if cents > 0 else VERMELHO if cents < 0 else PRETO))
        return P(brl_int(cents), st)

    cats = sorted({c for c in d["matriz"]}, key=lambda c: -sum(d["matriz"][c].values()))
    rows = [[P("<b>Categoria</b>", _cb)] + [P(f"<b>{lab}</b>", _crb) for _, lab, _ in meses]
            + [P("<b>Média</b>", _crb), P("<b>Total</b>", _crb)]]
    for cat in cats:
        vals = [d["matriz"][cat].get(k, 0) for _, _, k in meses]
        row = [P(cat, _c)] + [_v(v) if v else P("—", _cr) for v in vals]
        row += [_v(round(sum(vals) / len(vals)), True), _v(sum(vals), True)]
        rows.append(row)
    res = [sum(v[k] for v in d["matriz"].values()) for _, _, k in meses]
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


def bloco_mes(d, titulo_unidade):
    """Receitas e Despesas do mês anterior: receita, despesa operacional, CAPEX, caixa."""
    els = [NextPageTemplate("retrato"), PageBreak()]
    els.append(P(f"Receitas e Despesas — {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de caixa)", h2))
    r = [[P("<b>Item</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    r.append([P("<b>Receitas</b>", cellb), P("", cellc), P("", cellr)])
    for nome, (v, n) in sorted(d["ant_rec"].items()):
        r.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    r.append([P("<b>Total de Receitas</b>", cellrb),
              P(f"<b>{sum(n for _, n in d['ant_rec'].values())}</b>", cellc), P_val(d["ant_entradas"], cellrb)])
    if d["ant_aportes"]:
        r.append([P("(−) Aportes dos sócios", cell), P("", cellc), P_val(-d["ant_aportes"], cellr)])
        r.append([P("<b>(=) Receita operacional (juros + outras)</b>", cellrb), P("", cellc),
                  P_val(d["ant_entradas"] - d["ant_aportes"], cellrb)])
    r.append([P("<b>Despesas operacionais</b>", cellb), P("", cellc), P("", cellr)])
    for nome, (v, n) in sorted(d["ant_desp"].items()):
        r.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    r.append([P("<b>Total de Despesas Operacionais</b>", cellrb),
              P(f"<b>{sum(n for _, n in d['ant_desp'].values())}</b>", cellc), P_val(d["ant_saidas"], cellrb)])
    if d["ant_capex"]:
        r.append([P("<b>Investimento na Obra (CAPEX)</b>", cellb), P("", cellc), P("", cellr)])
        for nome, (v, n) in sorted(d["ant_capex"].items()):
            r.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
        r.append([P("<b>Total de Investimentos</b>", cellrb),
                  P(f"<b>{sum(n for _, n in d['ant_capex'].values())}</b>", cellc), P_val(d["ant_capex_tot"], cellrb)])
    r.append([P("<b>Resultado do mês (juros − despesas operacionais)</b>", cellrb), P("", cellc),
              P_val(d["ant_resultado"], cellrb)])
    r.append([P("<b>Variação do caixa no mês</b>", cellrb), P("", cellc), P_val(d["ant_variacao"], cellrb)])
    t = tabela(r, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(r) - 2), (-1, len(r) - 1), LARANJA_CLARO)]))
    els.append(t)
    els.append(P("Aporte dos sócios entra no caixa mas não é receita da operação. "
                 "Investimento na Obra é CAPEX, não despesa operacional. "
                 "Resultado do mês = juros de aplicação menos despesas operacionais.", sub))
    return els


def bloco_aberto_previsao(d, titulo_unidade):
    els = [Spacer(1, 12)]
    els.append(P(f"Despesas em aberto até {FIM_MES_ANT_LABEL}", h2))
    els += tabela_cat("Resumo por categoria", d["g_aberto"], total_label="Total em aberto")
    if d["aberto"]:
        por_cat = defaultdict(list)
        for t_ in d["aberto"]:
            por_cat[cat_nome(t_)].append(t_)
        els.append(P("<b>Demonstrativo dos lançamentos</b>", h3))
        for cat in sorted(por_cat):
            txs_cat = sorted(por_cat[cat], key=bdate)
            rows = [[P("<b>Vencimento</b>", cell), P("<b>Descrição</b>", cell),
                     P("<b>Conta</b>", cell), P("<b>Valor</b>", cellr)]]
            for t_ in txs_cat:
                dt = bdate(t_)
                rows.append([P(f"{dt[8:10]}/{dt[5:7]}/{dt[:4]}", cell),
                             P((t_.get("ds_transaction") or "")[:60], cell),
                             P(t_.get("ds_account_main") or "", cell), P_val(valor_efetivo(t_), cellr)])
            rows.append([P("<b>Total</b>", cellrb), P(f"<b>{cat}</b>", cellrb), P(f"<b>{len(txs_cat)}</b>", cellc),
                         P_val(sum(valor_efetivo(t_) for t_ in txs_cat), cellrb)])
            tt = tabela(rows, [2.2 * cm, 7.0 * cm, 3.4 * cm, 2.9 * cm])
            tt.setStyle(TableStyle([("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), LARANJA_CLARO)]))
            els.append(tt)
            els.append(Spacer(1, 4))
    else:
        els.append(P("Nenhuma despesa em aberto no período.", sub))
    els.append(Spacer(1, 12))
    els.append(P(f"Previsão de Receitas e Despesas — {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)", h2))
    pr = [[P("<b>Item</b>", cell), P("<b>Lançamentos</b>", cellc), P("<b>Valor</b>", cellr)]]
    pr.append([P("<b>Receitas previstas</b>", cellb), P("", cellc), P("", cellr)])
    for nome, (v, n) in sorted(d["prev_rec"].items()):
        pr.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
    tot_rec = sum(v for v, _ in d["prev_rec"].values())
    pr.append([P("<b>Total previsto</b>", cellrb), P(f"<b>{sum(n for _, n in d['prev_rec'].values())}</b>", cellc),
               P_val(tot_rec, cellrb)])
    if d["prev_desp"]:
        pr.append([P("<b>Despesas previstas</b>", cellb), P("", cellc), P("", cellr)])
        for nome, (v, n) in sorted(d["prev_desp"].items()):
            pr.append([P(nome, cell), P(str(n), cellc), P_val(v, cellr)])
        tot_desp = sum(v for v, _ in d["prev_desp"].values())
        pr.append([P("<b>Total de Despesas Previstas</b>", cellrb),
                   P(f"<b>{sum(n for _, n in d['prev_desp'].values())}</b>", cellc), P_val(tot_desp, cellrb)])
        pr.append([P("<b>Resultado previsto do mês</b>", cellrb), P("", cellc), P_val(tot_rec + tot_desp, cellrb)])
    if d["prev_capex"]:
        for nome, (v, n) in sorted(d["prev_capex"].items()):
            pr.append([P(f"CAPEX — {nome}", cell), P(str(n), cellc), P_val(v, cellr)])
    t = tabela(pr, [11 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, len(pr) - 1), (-1, len(pr) - 1), LARANJA_CLARO)]))
    els.append(t)
    return els


def bloco_fluxo_proj(d, titulo_unidade, resíduo=None):
    els = [PageBreak()]
    els.append(P(f"Fluxo de Caixa — Últimos 13 Meses "
                 f"({MES_AB[INI_13.month]}/{str(INI_13.year)[2:]} a {MES_AB[MES_ANT.month]}/{str(MES_ANT.year)[2:]}) "
                 f"— realizado", h2))
    rows = [[P("<b>Mês</b>", cell), P("<b>Saldo inicial</b>", cellr), P("<b>Entradas</b>", cellr),
             P("<b>Saídas</b>", cellr), P("<b>Saldo final</b>", cellr)]]
    for lab, si, e, x, sf in d["fluxo"]:
        rows.append([P(lab, cell), P_val(si, cellr), P_val(e, cellr), P_val(x, cellr), P_val(sf, cellrb)])
    t = tabela(rows, [3.0 * cm, 3.6 * cm, 3.4 * cm, 3.4 * cm, 3.6 * cm], fs=7.5)
    els.append(t)
    nota = ("Nota: entradas e saídas realizadas das contas do centro de custo (baixas do período), "
            "sem transferências entre contas. Saldo final conferido contra o saldo real do centro de custo.")
    if resíduo:
        nota += f" {resíduo}"
    els.append(P(nota, sub))

    els.append(Spacer(1, 14))
    els.append(P(f"Projeção de Fluxo de Caixa — Próximos 12 Meses "
                 f"({MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} a "
                 f"{MES_PT[add_months(MES_COR, 11).month].capitalize()} de {add_months(MES_COR, 11).year})", h2))
    rows6 = [[P("<b>Mês</b>", cell), P("<b>Entradas previstas</b>", cellr),
              P("<b>Saídas previstas</b>", cellr), P("<b>Saldo previsto</b>", cellr)]]
    for lab, e, x, s in d["proj_ac"]:
        rows6.append([P(lab, cell), P_val(e, cellr), P_val(x, cellr), P_val(s, cellrb)])
    t = tabela(rows6, [3.2 * cm, 4.4 * cm, 4.4 * cm, 4.6 * cm], fs=7.5)
    els.append(t)
    els.append(P(f"Nota: saldo de partida = saldo real em {FIM_MES_ANT_LABEL}; movimentos = lançamentos "
                 f"previstos e pendentes do Controlle para o centro de custo.", sub))
    return els


# ---- páginas ----
E += capa()
for i, (nome, _) in enumerate(UNIDADES):
    d = D[nome]
    if i > 0:
        E.append(NextPageTemplate("paisagem"))
        E.append(PageBreak())
        E += capa(nome)
    E += bloco_comparativo(d, f"Comparativo — {nome}")
    E += bloco_mes(d, nome)
    E += bloco_aberto_previsao(d, nome)
    E += bloco_fluxo_proj(d, nome)

# CONSOLIDADO
E.append(NextPageTemplate("paisagem"))
E.append(PageBreak())
E += capa("UNIFICADO — MAURO RAMOS + BARRA DA LAGOA")
Cv = dict(C)
Cv["nome"] = "UNIFICADO"
Cv["ant_aportes"] = C["ant_aportes"]
E += bloco_comparativo(Cv, "Comparativo consolidado")
E += bloco_mes(Cv, "UNIFICADO")
E += bloco_aberto_previsao(Cv, "UNIFICADO")
_res = (f"Soma dos dois centros de custo = {brl(C['saldo_cc'])} = total nas contas da licença em "
        f"{FIM_MES_ANT_LABEL} ({brl(tot_saldo_contas)}).")
E += bloco_fluxo_proj(Cv, "UNIFICADO", resíduo=_res)

E.append(Spacer(1, 10))
E.append(P("Gerado automaticamente pela terceirizou · dados do Controlle", sub))

doc.build(E)
print(f"OK: {ARQ_PDF}")

# ===== EXCEL =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ARQ_XLSX = f"artifacts/{HOJE.strftime('%y%m%d')}_Relatorio_Centrovita_Caixa.xlsx"
wb = Workbook(); wb.remove(wb.active)
FILL_H = PatternFill("solid", fgColor="FF501C")
FILL_T = PatternFill("solid", fgColor="FFE3D6")
FH = Font(bold=True, color="FFFFFF")
FB = Font(bold=True)
VERDE_XL = "1A7F37"; VERMELHO_XL = "C0392B"
TOT = ("Total", "Resultado", "Variação", "Previsão", "Total de", "Total em", "Total previsto", "(−)")

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


for nome, _ in UNIDADES + [("UNIFICADO", None)]:
    d = D[nome] if nome != "UNIFICADO" else C
    tag = "MR" if nome == "MAURO RAMOS" else ("BL" if nome == "BARRA DA LAGOA" else "UNIF")
    rotulo = nome
    # comparativo 13m
    meses = d["meses_mov"]
    cats = sorted({c for c in d["matriz"]}, key=lambda c: -sum(d["matriz"][c].values()))
    linhas = [("Categoria",) + tuple(lab for _, lab, _ in meses) + ("Média", "Total")]
    for cat in cats:
        vals = [d["matriz"][cat].get(k, 0) for _, _, k in meses]
        linhas.append((cat,) + tuple(r_(v) if v else None for v in vals)
                      + (r_(round(sum(vals) / len(vals))), r_(sum(vals))))
    res = [sum(v[k] for v in d["matriz"].values()) for _, _, k in meses]
    linhas.append(("Variação do caixa no mês",) + tuple(r_(v) for v in res)
                  + (r_(round(sum(res) / len(res))), r_(sum(res))))
    aba(f"Comp 13m {tag}", linhas, [42] + [11] * len(meses) + [12, 14],
        titulo=f"{rotulo} — Comparativo dos Últimos 13 Meses por Categoria (regime de caixa)")

    # mês anterior
    lm = [("Item", "Lançamentos", "Valor"), ("Receitas", None, None)]
    for k, (v, n) in sorted(d["ant_rec"].items()):
        lm.append((k, n, r_(v)))
    lm.append(("Total de Receitas", sum(n for _, n in d["ant_rec"].values()), r_(d["ant_entradas"])))
    if d["ant_aportes"]:
        lm.append(("(−) Aportes dos sócios", None, r_(-d["ant_aportes"])))
        lm.append(("(=) Receita operacional (juros + outras)", None, r_(d["ant_entradas"] - d["ant_aportes"])))
    lm.append(("Despesas operacionais", None, None))
    for k, (v, n) in sorted(d["ant_desp"].items()):
        lm.append((k, n, r_(v)))
    lm.append(("Total de Despesas Operacionais", sum(n for _, n in d["ant_desp"].values()), r_(d["ant_saidas"])))
    if d["ant_capex"]:
        lm.append(("Investimento na Obra (CAPEX)", None, None))
        for k, (v, n) in sorted(d["ant_capex"].items()):
            lm.append((k, n, r_(v)))
        lm.append(("Total de Investimentos", sum(n for _, n in d["ant_capex"].values()), r_(d["ant_capex_tot"])))
    lm.append(("Resultado do mês (juros − despesas operacionais)", None, r_(d["ant_resultado"])))
    lm.append(("Variação do caixa no mês", None, r_(d["ant_variacao"])))
    aba(f"Mes ant {tag}", lm, [46, 14, 16],
        titulo=f"{rotulo} — Receitas e Despesas de {MES_PT[MES_ANT.month].capitalize()} de {MES_ANT.year} (regime de caixa)")

    # despesas em aberto
    la = [("Categoria", "Lançamentos", "Valor")]
    for k, (v, n) in sorted(d["g_aberto"].items()):
        la.append((k, n, r_(v)))
    la.append(("Total em aberto", sum(n for _, n in d["g_aberto"].values()),
               r_(sum(v for v, _ in d["g_aberto"].values()))))
    aba(f"Aberto {tag}", la, [46, 14, 16],
        titulo=f"{rotulo} — Despesas em aberto até {FIM_MES_ANT_LABEL}")

    # previsão
    lp = [("Item", "Lançamentos", "Valor"), ("Receitas previstas", None, None)]
    for k, (v, n) in sorted(d["prev_rec"].items()):
        lp.append((k, n, r_(v)))
    tr = sum(v for v, _ in d["prev_rec"].values())
    lp.append(("Total previsto", sum(n for _, n in d["prev_rec"].values()), r_(tr)))
    if d["prev_desp"]:
        lp.append(("Despesas previstas", None, None))
        for k, (v, n) in sorted(d["prev_desp"].items()):
            lp.append((k, n, r_(v)))
        td = sum(v for v, _ in d["prev_desp"].values())
        lp.append(("Total de Despesas Previstas", sum(n for _, n in d["prev_desp"].values()), r_(td)))
        lp.append(("Resultado previsto do mês", None, r_(tr + td)))
    for k, (v, n) in sorted(d["prev_capex"].items()):
        lp.append((f"CAPEX — {k}", n, r_(v)))
    aba(f"Previsao {tag}", lp, [46, 14, 16],
        titulo=f"{rotulo} — Previsão de {MES_PT[MES_COR.month].capitalize()} de {MES_COR.year} (pago + pendente)")

    # fluxo 13m
    aba(f"Fluxo 13m {tag}",
        [("Mês", "Saldo inicial", "Entradas", "Saídas", "Saldo final")] +
        [(lab, r_(a), r_(b), r_(c), r_(e)) for lab, a, b, c, e in d["fluxo"]],
        [10, 16, 16, 16, 16],
        titulo=f"{rotulo} — Fluxo de Caixa dos Últimos 13 Meses (realizado)")

    # projeção 12m
    aba(f"Proj 12m {tag}",
        [("Mês", "Entradas previstas", "Saídas previstas", "Saldo previsto", "Saldo final")] and
        [("Mês", "Entradas previstas", "Saídas previstas", "Saldo previsto")] +
        [(lab, r_(e), r_(x), r_(s)) for lab, e, x, s in d["proj_ac"]],
        [10, 18, 18, 18],
        titulo=f"{rotulo} — Projeção de Fluxo de Caixa — Próximos 12 Meses")

# saldos
ls = [("Centro de custo / conta", f"Saldo em {FIM_MES_ANT_LABEL}")]
for nome, _ in UNIDADES:
    ls.append((nome, r_(D[nome]["saldo_cc"])))
ls.append(("Soma dos centros de custo", r_(C["saldo_cc"])))
ls.append(("Total nas contas (licença)", r_(tot_saldo_contas)))
ls.append(("Diferença", r_(tot_saldo_contas - C["saldo_cc"])))
aba("Saldos", ls, [56, 20], titulo=f"Saldos em {FIM_MES_ANT_LABEL}")

wb.save(ARQ_XLSX)
print(f"OK: {ARQ_XLSX}")
