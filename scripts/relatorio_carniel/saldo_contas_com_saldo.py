#!/usr/bin/env python3
# Saldo nas Contas — CARNIEL EMPREENDIMENTO LTDA — variante "somente contas com saldo" (pedido Vinícius 11/11).
# Fonte canônica: GET /transaction/v1/transactions/balances por conta (regime de caixa, balanceDone na data).
#   NÃO somar lançamentos da `list` para chegar em saldo: transferências entre contas e rateios
#   fazem a soma por ds_account_main divergir; o balances é o que fecha com o Controlle.
# Uso: python3 saldo_contas.py [YYYY-MM-DD]  (default: 2026-10-31)
import json, os, sys, time, urllib.request, urllib.error
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage

BASE = "https://api-v1.controlle.com"
_dir = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("CONTROLLE_TOKEN_CARNIEL") or open(os.path.join(_dir, ".controlle_token")).read().strip()
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}


def req(url, tries=5):
    """Retry em falha de REDE (IncompleteRead/URLError/SSL/timeout) e em 500/502/503."""
    for i in range(tries):
        try:
            r = urllib.request.Request(url)
            for k, v in UA.items():
                r.add_header(k, v)
            with urllib.request.urlopen(r, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and i < tries - 1:
                time.sleep(5 * (i + 1))
                continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(5 * (i + 1))
                continue
            raise


def brl(cents):
    v = cents / 100
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-" if v < 0 else "") + "R$ " + s


DATA = sys.argv[1] if len(sys.argv) > 1 else "2026-10-31"
DATA_LABEL = f"{DATA[8:10]}/{DATA[5:7]}/{DATA[:4]}"

contas = [c for c in req(f"{BASE}/account/v1/accounts").get("results", []) if c.get("status") == 1]
saldos, tot = [], 0
for c in contas:
    b = req(f"{BASE}/transaction/v1/transactions/balances?start_date=2017-01-01&end_date={DATA}"
            f"&id_account_main={c['id']}")["results"]
    saldos.append((c.get("ds_account"), b["balanceDone"]))
    tot += b["balanceDone"]

# Pedido 11/11: apresentar APENAS as contas com saldo (as zeradas ficam fora do PDF).
zeradas = [n for n, v in saldos if v == 0]
saldos = [(n, v) for n, v in saldos if v != 0]

LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=PRETO, alignment=1, spaceAfter=2)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8,
                     textColor=colors.HexColor("#777777"), alignment=1, spaceAfter=10)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=9)
cellr = ParagraphStyle("cellr", parent=cell, alignment=2)
cellrb = ParagraphStyle("cellrb", parent=cell, fontName="Helvetica-Bold", alignment=2)
P = Paragraph

os.makedirs("artifacts", exist_ok=True)
ARQ = f"artifacts/{time.strftime('%y%m%d')}_Saldo_Contas_Carniel_{DATA[8:10]}{DATA[5:7]}{DATA[:4]}.pdf"
doc = SimpleDocTemplate(ARQ, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                        topMargin=1.3 * cm, bottomMargin=1.6 * cm,
                        title=f"Saldo nas Contas — Carniel — {DATA_LABEL}")
E = []
img = RLImage(os.path.join(_dir, "logo-terceirizou.png"), width=5 * cm, height=5 * cm * 561 / 1600)
img.hAlign = "CENTER"
E.append(img)
E.append(Spacer(1, 8))
E.append(P("<b>CARNIEL EMPREENDIMENTO LTDA — Saldo nas Contas</b>", h1))
E.append(P(f"Posição em {DATA_LABEL} · Fonte: Controlle · Regime de caixa", sub))

rows = [[P("<b>Conta</b>", cell), P(f"<b>Saldo em {DATA_LABEL}</b>", cellr)]]
for nome, v in saldos:
    rows.append([P(nome, cell), P(brl(v), cellr)])
rows.append([P("<b>TOTAL</b>", cellrb), P(brl(tot), cellrb)])

t = Table(rows, colWidths=[9 * cm, 6 * cm])
st = [("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9),
      ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
      ("BACKGROUND", (0, 0), (-1, 0), LARANJA), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
      ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
      ("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), LARANJA_CLARO),
      ("LINEBELOW", (0, -1), (-1, -1), 0.7, LARANJA)]
for i in range(1, len(rows) - 1):
    if i % 2 == 0:
        st.append(("BACKGROUND", (0, i), (-1, i), CINZA))
t.setStyle(TableStyle(st))
E.append(t)
E.append(Spacer(1, 10))
nota = "Contas com saldo apresentadas nesta posição." 
if zeradas:
    nota += f" {len(zeradas)} contas sem saldo não integram o relatório."
E.append(P(nota + " Gerado automaticamente pela Terceirizou.", sub))

SIMBOLO = os.path.join(_dir, "simbolo-terceirizou.png")


def rodape(canvas, doc):
    if os.path.exists(SIMBOLO):
        alt = 1.1 * cm
        canvas.drawImage(SIMBOLO, 1.6 * cm, 1.0 * cm, width=alt * 372 / 553, height=alt, mask="auto")


doc.build(E, onFirstPage=rodape, onLaterPages=rodape)

print(f"OK: {ARQ}")
print(f"DATA: {DATA}")
print(f"TOTAL: {brl(tot)}")
