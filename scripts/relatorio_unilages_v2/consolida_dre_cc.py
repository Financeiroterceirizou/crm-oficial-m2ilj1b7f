#!/usr/bin/env python3
"""Consolida os pacotes DRE Unilages por CC de UM mês em 1 Excel (aba por CC: DRE + Detalhe).
Uso: python3 consolida_dre_cc.py YYYYMM
Gera artifacts/<yymmdd>_DRE_Unilages_Completo_YYYYMM.xlsx
Layout idêntico ao 261023_DRE_Unilages_Completo_202609.xlsx (14 abas, sem Resumo).
"""
import os
import sys
from copy import copy
from datetime import date

from openpyxl import Workbook, load_workbook

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))

PACOTES = [
    ("Geral", "GERAL"),
    ("correia_pinto", "Correia Pinto"),
    ("curitibanos", "Curitibanos"),
    ("lages_bm_adm", "Lages + BM ADM"),
    ("otacilio_costa", "Otacilio Costa"),
    ("sao_joaquim", "Sao Joaquim"),
    ("urubici", "Urubici"),
]


def copia_sheet(wb, orig, nome):
    d = wb.create_sheet(nome[:31])
    for row in orig.iter_rows():
        for cell in row:
            nc = d.cell(row=cell.row, column=cell.column, value=cell.value)
            if cell.has_style:
                nc.font = copy(cell.font)
                nc.fill = copy(cell.fill)
                nc.number_format = cell.number_format
                nc.alignment = copy(cell.alignment)
                nc.border = copy(cell.border)
    for k, dim in orig.column_dimensions.items():
        d.column_dimensions[k].width = dim.width
    for k, dim in orig.row_dimensions.items():
        d.row_dimensions[k].height = dim.height
    for rng in orig.merged_cells.ranges:
        d.merge_cells(str(rng))
    if orig.freeze_panes:
        d.freeze_panes = orig.freeze_panes
    return d


def main():
    if len(sys.argv) < 2:
        print("uso: consolida_dre_cc.py YYYYMM")
        return 2
    ref = sys.argv[1]                      # 202610
    mmyy = ref[4:6] + ref[2:4]             # 1026
    dia = date.today().strftime("%y%m%d")
    saida = os.path.join(RAIZ, "artifacts", f"{dia}_DRE_Unilages_Completo_{ref}.xlsx")

    wb = Workbook()
    wb.remove(wb.active)
    for tag, label in PACOTES:
        p = os.path.join(RAIZ, "artifacts", f"{dia}_DRE_Unilages_{tag}_{ref}.xlsx")
        if not os.path.exists(p):
            print(f"FALTA: {p}")
            return 1
        src = load_workbook(p)
        copia_sheet(wb, src.worksheets[0], f"{label} — DRE {mmyy}")
        if len(src.worksheets) > 1:
            copia_sheet(wb, src.worksheets[1], f"{label} — Detalhe Despesas {mmyy}")
        src.close()

    wb.save(saida)
    print(f"OK: {saida} — {len(wb.sheetnames)} abas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
