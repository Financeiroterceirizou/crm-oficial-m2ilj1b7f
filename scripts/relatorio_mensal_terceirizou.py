#!/usr/bin/env python3
# Amostra do relatório gerencial mensal — TERCEIRIZOU (agosto/2026)
# Dados: Entradas vs Saídas por categorias (painel Controlle, período Agosto 2026)
# + saldo do dashboard (17/09) + projeção 12m do fluxo gerado em 14/08.
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

AZUL = colors.HexColor("#1a3a5c")
CINZA = colors.HexColor("#f2f4f7")
VERDE = colors.HexColor("#1e7d3e")
VERMELHO = colors.HexColor("#b02a2a")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=AZUL, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=AZUL, spaceBefore=14, spaceAfter=6)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#666666"), spaceAfter=10)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5, leading=13)
cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=9)
cellb = ParagraphStyle("cellb", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold")

def tabela(rows, widths, header=True):
    t = Table(rows, colWidths=widths)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), CINZA))
    t.setStyle(TableStyle(style))
    return t

doc = SimpleDocTemplate("artifacts/relatorio-terceirizou-agosto-2026.pdf", pagesize=A4,
                        leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
E = []

E.append(Paragraph("Relatório Gerencial — Terceirizou", h1))
E.append(Paragraph("Agosto de 2026 · Fechamento mensal · Fonte: Controlle (Terceirização Empresarial LTDA)", sub))

# Resumo
E.append(Paragraph("Resumo do mês", h2))
resumo = [
    [Paragraph("<b>Indicador</b>", cell), Paragraph("<b>Agosto/2026</b>", cell), Paragraph("<b>Setembro (até 17/09)</b>", cell)],
    [Paragraph("Entradas", cell), Paragraph("R$ 69.866,30", cell), Paragraph("R$ 80.813,97", cell)],
    [Paragraph("Saídas", cell), Paragraph("R$ 77.385,59", cell), Paragraph("R$ 78.205,08", cell)],
    [Paragraph("<b>Resultado</b>", cellb), Paragraph("<b><font color='#b02a2a'>-R$ 7.519,29</font></b>", cellb),
     Paragraph("<b><font color='#1e7d3e'>+R$ 2.608,89</font></b>", cellb)],
    [Paragraph("Saldo em caixa (17/09)", cell), Paragraph("R$ 32.988,26", cell), Paragraph("Inter Investimentos + PERMUTA", cell)],
]
E.append(tabela(resumo, [6*cm, 4.5*cm, 5.5*cm]))

# Entradas
E.append(Paragraph("Entradas por categoria", h2))
ent = [
    [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>%</b>", cell), Paragraph("<b>Valor</b>", cell)],
    [Paragraph("RECEITAS", cell), Paragraph("99,27%", cell), Paragraph("R$ 69.357,67", cell)],
    [Paragraph("RECEITAS FINANCEIRAS", cell), Paragraph("0,73%", cell), Paragraph("R$ 508,63", cell)],
    [Paragraph("<b>Total</b>", cellb), Paragraph("<b>100,00%</b>", cellb), Paragraph("<b>R$ 69.866,30</b>", cellb)],
]
E.append(tabela(ent, [8*cm, 3*cm, 5*cm]))

# Saídas
E.append(Paragraph("Saídas por categoria", h2))
sai = [
    [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>%</b>", cell), Paragraph("<b>Valor</b>", cell)],
    [Paragraph("CUSTOS OPERACIONAIS", cell), Paragraph("61,14%", cell), Paragraph("-R$ 47.314,32", cell)],
    [Paragraph("DESPESAS DE RH", cell), Paragraph("17,09%", cell), Paragraph("-R$ 13.222,58", cell)],
    [Paragraph("DESPESAS ADMINISTRATIVAS E COMERCIAS", cell), Paragraph("16,89%", cell), Paragraph("-R$ 13.067,27", cell)],
    [Paragraph("IMPOSTOS SOBRE FATURAMENTO", cell), Paragraph("4,78%", cell), Paragraph("-R$ 3.700,92", cell)],
    [Paragraph("DESPESAS FINANCEIRAS", cell), Paragraph("0,10%", cell), Paragraph("-R$ 80,50", cell)],
    [Paragraph("<b>Total</b>", cellb), Paragraph("<b>100,00%</b>", cellb), Paragraph("<b>-R$ 77.385,59</b>", cellb)],
]
E.append(tabela(sai, [8*cm, 3*cm, 5*cm]))

# Leitura gerencial
E.append(Paragraph("Leitura gerencial", h2))
E.append(Paragraph(
    "Agosto fechou com resultado negativo de R$ 7,5 mil: as saídas superaram as entradas em 10,8%. "
    "O peso está em Custos Operacionais (61% das saídas), seguido de RH (17%) e Despesas Administrativas (17%). "
    "Setembro começou melhor — no parcial, o resultado está positivo em R$ 2,6 mil, com entradas de R$ 80,8 mil já superando "
    "todo o mês de agosto.", body))
E.append(Spacer(1, 6))
E.append(Paragraph(
    "Na projeção de 12 meses (ago/26 a jul/27), o caixa tem tendência de queda de R$ 20,5 mil no acumulado: "
    "entradas médias de ~R$ 69 mil/mês contra saídas de ~R$ 70,7 mil/mês. O saldo atual de R$ 33 mil dá folga, "
    "mas o ponto de atenção é a diferença estrutural entre entrada e saída — vale revisar os custos operacionais "
    "nos próximos ciclos.", body))

E.append(Spacer(1, 14))
E.append(Paragraph("Gerado automaticamente pela Terceirizou · dados do Controlle · 17/09/2026",
                   ParagraphStyle("foot", parent=sub, fontSize=8)))

doc.build(E)
print("OK")
