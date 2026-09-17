#!/usr/bin/env python3
# Amostra do relatório gerencial mensal — TERCEIRIZOU (agosto/2026) — V2
# Dados: painel Controlle (Entradas vs Saídas por categorias, Fluxo de Caixa realizado,
# Lançamentos com filtro status=pending para inadimplência).
# Seções: resumo, entradas/saídas por categoria, leitura gerencial, inadimplência,
# saldos, resultado 12m por categoria, comparativo mensal.
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

AZUL = colors.HexColor("#1a3a5c")
CINZA = colors.HexColor("#f2f4f7")

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

E.append(Paragraph("Entradas por categoria", h2))
ent = [
    [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>%</b>", cell), Paragraph("<b>Valor</b>", cell)],
    [Paragraph("RECEITAS", cell), Paragraph("99,27%", cell), Paragraph("R$ 69.357,67", cell)],
    [Paragraph("RECEITAS FINANCEIRAS", cell), Paragraph("0,73%", cell), Paragraph("R$ 508,63", cell)],
    [Paragraph("<b>Total</b>", cellb), Paragraph("<b>100,00%</b>", cellb), Paragraph("<b>R$ 69.866,30</b>", cellb)],
]
E.append(tabela(ent, [8*cm, 3*cm, 5*cm]))

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

doc.build(E)

# ===== V2: seções adicionais =====
doc2 = SimpleDocTemplate("artifacts/relatorio-terceirizou-agosto-2026-v2.pdf", pagesize=A4,
                        leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
E2 = []
E2.append(Paragraph("Relatório Gerencial — Terceirizou (complemento)", h1))
E2.append(Paragraph("Agosto de 2026 · Seções: Inadimplência, Saldos, Resultado 12m e Comparativo mensal", sub))

E2.append(Paragraph("Inadimplência — receitas em aberto até 31/08", h2))
inad = [
    [Paragraph("<b>Item</b>", cell), Paragraph("<b>Valor</b>", cell)],
    [Paragraph("Receitas em aberto (vencidas até 31/08/2026)", cell), Paragraph("R$ 353.110,50", cell)],
    [Paragraph("Despesas em aberto (parcelas pendentes)", cell), Paragraph("-R$ 283.978,52", cell)],
    [Paragraph("<b>Saldo líquido em aberto</b>", cellb), Paragraph("<b>-R$ 3.458,84</b>", cellb)],
]
E2.append(tabela(inad, [10*cm, 6*cm]))
E2.append(Spacer(1, 6))
E2.append(Paragraph(
    "Principais receitas em aberto (recorrência mensal de R$ 400,00, vencidas desde set/2025): VISTORIA PARACATU, "
    "VISTORIA CURVELO, VISTORIA PORTEIRINHA, VISTORIA TEOFILO OTONI - FURTADO, VISTORIA CORONEL FABRICIANO - MCS, "
    "VISTORIA JUIZ DE FORA 2 - AGUIAR, VISTORIA GUAXUPÉ, VISTORIA ARAGUARI - DN, VISTORIA UBERABA II - APN e VISTORIA LAVRAS. "
    "Atenção: parte desse valor pode ser receita já recebida mas não conciliada no sistema — recomendo conferência antes de cobrança.",
    body))

E2.append(Paragraph("Saldo nas contas em 31/08/2026", h2))
saldos = [
    [Paragraph("<b>Conta</b>", cell), Paragraph("<b>Saldo em 31/08</b>", cell)],
    [Paragraph("Cora - 2482761-1 + Inter Investimentos (consolidado)", cell), Paragraph("R$ 31.315,62", cell)],
    [Paragraph("Saldo atual (17/09/2026)", cell), Paragraph("R$ 32.988,26", cell)],
]
E2.append(tabela(saldos, [10*cm, 6*cm]))

E2.append(Paragraph("Resultado dos últimos 12 meses por categoria (jan–set/2026 realizado)", h2))
res12 = [
    [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>Entradas</b>", cell), Paragraph("<b>Saídas</b>", cell)],
    [Paragraph("RECEITAS", cell), Paragraph("R$ 292.324,61", cell), Paragraph("—", cell)],
    [Paragraph("RECEITAS FINANCEIRAS", cell), Paragraph("R$ 2.001,67", cell), Paragraph("—", cell)],
    [Paragraph("CUSTOS OPERACIONAIS", cell), Paragraph("—", cell), Paragraph("-R$ 192.836,42", cell)],
    [Paragraph("DESPESAS DE RH", cell), Paragraph("—", cell), Paragraph("-R$ 54.268,81", cell)],
    [Paragraph("DESPESAS ADMINISTRATIVAS E COMERCIAS", cell), Paragraph("—", cell), Paragraph("-R$ 30.702,01", cell)],
    [Paragraph("IMPOSTOS SOBRE FATURAMENTO", cell), Paragraph("—", cell), Paragraph("-R$ 14.525,12", cell)],
    [Paragraph("DESPESAS FINANCEIRAS", cell), Paragraph("—", cell), Paragraph("-R$ 318,70", cell)],
    [Paragraph("<b>Total</b>", cellb), Paragraph("<b>R$ 294.326,28</b>", cellb), Paragraph("<b>-R$ 292.651,06</b>", cellb)],
    [Paragraph("<b>Resultado acumulado</b>", cellb), Paragraph("<b>+R$ 1.675,22</b>", cellb), Paragraph("", cell)],
]
E2.append(tabela(res12, [8*cm, 4*cm, 4*cm]))

E2.append(Paragraph("Comparativo mensal 2026 (entradas × saídas × saldo)", h2))
comp = [
    [Paragraph("<b>Mês</b>", cell), Paragraph("<b>Entradas</b>", cell), Paragraph("<b>Saídas</b>", cell), Paragraph("<b>Saldo final</b>", cell)],
    [Paragraph("Março", cell), Paragraph("R$ 0,00", cell), Paragraph("R$ 0,00", cell), Paragraph("R$ 400,00", cell)],
    [Paragraph("Abril", cell), Paragraph("R$ 31.313,04", cell), Paragraph("R$ 0,00", cell), Paragraph("R$ 36.934,93", cell)],
    [Paragraph("Maio", cell), Paragraph("R$ 0,00", cell), Paragraph("-R$ 68.250,21", cell), Paragraph("R$ 33.718,54", cell)],
    [Paragraph("Junho", cell), Paragraph("R$ 5.221,89", cell), Paragraph("-R$ 69.491,43", cell), Paragraph("R$ 28.980,54", cell)],
    [Paragraph("Julho", cell), Paragraph("R$ 65.033,82", cell), Paragraph("-R$ 64.547,85", cell), Paragraph("R$ 38.834,91", cell)],
    [Paragraph("Agosto", cell), Paragraph("R$ 74.402,22", cell), Paragraph("-R$ 77.385,59", cell), Paragraph("R$ 31.315,62", cell)],
    [Paragraph("Setembro (até 17/09)", cell), Paragraph("R$ 69.866,30", cell), Paragraph("-R$ 12.975,98", cell), Paragraph("R$ 32.988,26", cell)],
]
E2.append(tabela(comp, [4.5*cm, 3.8*cm, 3.8*cm, 3.9*cm]))
E2.append(Spacer(1, 6))
E2.append(Paragraph(
    "Nota: o comparativo mensal completo de 13 meses (set/2025 → set/2026) por categoria e o resultado consolidado "
    "dos 12 meses anteriores saem integralmente quando o token de API do Controlle for configurado — a interface "
    "exibe a matriz completa, mas a extração automática mensal depende do token.", body))

E2.append(Spacer(1, 14))
E2.append(Paragraph("Gerado automaticamente pela Terceirizou · dados do Controlle · 17/09/2026",
                   ParagraphStyle("foot2", parent=sub, fontSize=8)))
doc2.build(E2)
print("OK V2")
