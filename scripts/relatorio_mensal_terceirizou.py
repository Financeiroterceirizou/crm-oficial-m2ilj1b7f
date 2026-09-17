#!/usr/bin/env python3
# Relatório gerencial mensal — TERCEIRIZOU (piloto de automação)
# v2 (2026-09-17): pacote final definido pelo Vinícius — envio dia 05 do mês seguinte.
# Seções: Resumo · Fluxo de Caixa (realizado + projeção 12m) · Entradas vs Saídas por
# Categoria · DRE Gerencial · Inadimplência (receitas em aberto até fim do mês) ·
# Saldo nas contas no último dia do mês.
# Dados de agosto/2026: painel Controlle (relatórios Fluxo de Caixa realizado e
# Entradas vs Saídas por categorias, período ago/2026).
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

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

def build(mes_label, fonte_label, resumo_rows, entradas_rows, saidas_rows, dre_rows,
          saldo_rows, projecao_texto, inad_rows, saida_pdf):
    doc = SimpleDocTemplate(saida_pdf, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
    E = []
    E.append(Paragraph("Relatório Gerencial — Terceirizou", h1))
    E.append(Paragraph(f"{mes_label} · Fechamento mensal · Fonte: Controlle ({fonte_label})", sub))

    E.append(Paragraph("Resumo do mês", h2))
    E.append(tabela(resumo_rows, [6*cm, 4.5*cm, 5.5*cm]))

    E.append(Paragraph("Fluxo de caixa — realizado", h2))
    E.append(Paragraph(
        "Movimentações realizadas no mês, por categoria (sem transferências entre contas próprias):", body))
    E.append(Spacer(1, 4))
    fc = [[Paragraph("<b>Categoria</b>", cell), Paragraph("<b>Entradas</b>", cell), Paragraph("<b>Saídas</b>", cell)]]
    cats = ["RECEITAS", "RECEITAS FINANCEIRAS", "CUSTOS OPERACIONAIS", "DESPESAS DE RH",
            "DESPESAS ADMINISTRATIVAS E COMERCIAS", "IMPOSTOS SOBRE FATURAMENTO", "DESPESAS FINANCEIRAS"]
    for cat in cats:
        e_row = next((r for r in entradas_rows[1:-1] if r[0].text == cat), None)
        s_row = next((r for r in saidas_rows[1:-1] if r[0].text == cat), None)
        fc.append([Paragraph(cat, cell),
                   e_row[2] if e_row else Paragraph("—", cell),
                   s_row[2] if s_row else Paragraph("—", cell)])
    fc.append([Paragraph("<b>Total</b>", cellb),
               entradas_rows[-1][2] if entradas_rows else Paragraph("—", cell),
               saidas_rows[-1][2] if saidas_rows else Paragraph("—", cell)])
    E.append(tabela(fc, [7*cm, 4.5*cm, 4.5*cm]))

    E.append(Paragraph("Entradas vs Saídas por categoria", h2))
    E.append(tabela(entradas_rows, [8*cm, 3*cm, 5*cm]))
    E.append(Spacer(1, 4))
    E.append(tabela(saidas_rows, [8*cm, 3*cm, 5*cm]))

    E.append(Paragraph("DRE Gerencial (regime caixa)", h2))
    E.append(tabela(dre_rows, [9*cm, 3.5*cm, 3.5*cm]))

    E.append(Paragraph("Inadimplência — receitas em aberto até o fim do mês", h2))
    E.append(tabela(inad_rows, [8*cm, 4*cm, 4*cm]))

    E.append(Paragraph("Saldo nas contas — último dia do mês", h2))
    E.append(tabela(saldo_rows, [8*cm, 4*cm, 4*cm]))

    E.append(Paragraph("Projeção de fluxo de caixa — 12 meses", h2))
    E.append(Paragraph(projecao_texto, body))

    E.append(Spacer(1, 14))
    E.append(Paragraph("Gerado automaticamente pela Terceirizou · dados do Controlle",
                       ParagraphStyle("foot", parent=sub, fontSize=8)))
    doc.build(E)


if __name__ == "__main__":
    # ===== Agosto/2026 (dados reais extraídos do painel Controlle em 17/09) =====
    entradas_rows = [
        [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>%</b>", cell), Paragraph("<b>Valor</b>", cell)],
        [Paragraph("RECEITAS", cell), Paragraph("99,27%", cell), Paragraph("R$ 69.357,67", cell)],
        [Paragraph("RECEITAS FINANCEIRAS", cell), Paragraph("0,73%", cell), Paragraph("R$ 508,63", cell)],
        [Paragraph("<b>Total</b>", cellb), Paragraph("<b>100,00%</b>", cellb), Paragraph("<b>R$ 69.866,30</b>", cellb)],
    ]
    saidas_rows = [
        [Paragraph("<b>Categoria</b>", cell), Paragraph("<b>%</b>", cell), Paragraph("<b>Valor</b>", cell)],
        [Paragraph("CUSTOS OPERACIONAIS", cell), Paragraph("61,14%", cell), Paragraph("-R$ 47.314,32", cell)],
        [Paragraph("DESPESAS DE RH", cell), Paragraph("17,09%", cell), Paragraph("-R$ 13.222,58", cell)],
        [Paragraph("DESPESAS ADMINISTRATIVAS E COMERCIAS", cell), Paragraph("16,89%", cell), Paragraph("-R$ 13.067,27", cell)],
        [Paragraph("IMPOSTOS SOBRE FATURAMENTO", cell), Paragraph("4,78%", cell), Paragraph("-R$ 3.700,92", cell)],
        [Paragraph("DESPESAS FINANCEIRAS", cell), Paragraph("0,10%", cell), Paragraph("-R$ 80,50", cell)],
        [Paragraph("<b>Total</b>", cellb), Paragraph("<b>100,00%</b>", cellb), Paragraph("<b>-R$ 77.385,59</b>", cellb)],
    ]
    resumo_rows = [
        [Paragraph("<b>Indicador</b>", cell), Paragraph("<b>Agosto/2026</b>", cell), Paragraph("<b>Julho/2026</b>", cell)],
        [Paragraph("Entradas", cell), Paragraph("R$ 69.866,30", cell), Paragraph("R$ 74.402,22", cell)],
        [Paragraph("Saídas", cell), Paragraph("R$ 77.385,59", cell), Paragraph("R$ 69.491,43", cell)],
        [Paragraph("<b>Resultado</b>", cellb), Paragraph("<b>-R$ 7.519,29</b>", cellb), Paragraph("<b>+R$ 4.910,79</b>", cellb)],
        [Paragraph("Saldo em 31/08 (total)", cell), Paragraph("R$ 31.315,62", cell), Paragraph("R$ 38.834,91", cell)],
    ]
    dre_rows = [
        [Paragraph("<b>DRE (regime caixa)</b>", cell), Paragraph("<b>Agosto/2026</b>", cell), Paragraph("<b>% receita</b>", cell)],
        [Paragraph("Receita total", cell), Paragraph("R$ 69.866,30", cell), Paragraph("100,0%", cell)],
        [Paragraph("(-) Custos Operacionais", cell), Paragraph("R$ 47.314,32", cell), Paragraph("67,7%", cell)],
        [Paragraph("(-) Despesas de RH", cell), Paragraph("R$ 13.222,58", cell), Paragraph("18,9%", cell)],
        [Paragraph("(-) Despesas Administrativas e Comerciais", cell), Paragraph("R$ 13.067,27", cell), Paragraph("18,7%", cell)],
        [Paragraph("(-) Impostos sobre Faturamento", cell), Paragraph("R$ 3.700,92", cell), Paragraph("5,3%", cell)],
        [Paragraph("(-) Despesas Financeiras", cell), Paragraph("R$ 80,50", cell), Paragraph("0,1%", cell)],
        [Paragraph("<b>Resultado do mês</b>", cellb), Paragraph("<b>-R$ 7.519,29</b>", cellb), Paragraph("<b>-10,8%</b>", cellb)],
    ]
    saldo_rows = [
        [Paragraph("<b>Conta</b>", cell), Paragraph("<b>Saldo em 31/08</b>", cell), Paragraph("<b>Saldo em 31/07</b>", cell)],
        [Paragraph("Detalhamento por conta", cell), Paragraph("populado pelo pipeline automático", cell), Paragraph("—", cell)],
        [Paragraph("<b>Total</b>", cellb), Paragraph("<b>R$ 31.315,62</b>", cellb), Paragraph("<b>R$ 38.834,91</b>", cellb)],
    ]
    inad_rows = [
        [Paragraph("<b>Cliente</b>", cell), Paragraph("<b>Valor em aberto</b>", cell), Paragraph("<b>Vencimento</b>", cell)],
        [Paragraph("Extração via Contas a Receber em aberto em 31/08", cell), Paragraph("—", cell), Paragraph("—", cell)],
        [Paragraph("(seção populada pelo pipeline automático)", cell), Paragraph("—", cell), Paragraph("—", cell)],
    ]
    projecao_texto = (
        "Projeção gerada em 14/08 (base ago/26 a jul/27, a partir do Controlle): entradas médias de ~R$ 69 mil/mês "
        "contra saídas de ~R$ 70,7 mil/mês — acumulado de -R$ 20,5 mil no período. O saldo atual de R$ 31,3 mil dá folga, "
        "mas a diferença estrutural entre entrada e saída exige revisão dos custos operacionais nos próximos ciclos."
    )
    build("Agosto de 2026", "Terceirização Empresarial LTDA", resumo_rows, entradas_rows, saidas_rows,
          dre_rows, saldo_rows, projecao_texto, inad_rows,
          "artifacts/relatorio-terceirizou-agosto-2026.pdf")
    print("OK v2")
