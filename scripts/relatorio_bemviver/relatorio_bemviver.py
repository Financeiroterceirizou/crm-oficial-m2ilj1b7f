#!/usr/bin/env python3
# Relatórios Semanais — BEM VIVER (ILPI) — v1.4, 2026-09-21
# Uso: python3 relatorio_bemviver.py [YYYY-MM-DD]  (default: hoje)
# Gera UM PDF + UM Excel com os 11 relatórios no padrão dos exemplos de 14/09
#   + Comparativo 13 meses em PDF PRÓPRIO PAISAGEM.
# Fonte: API Controlle v1 (token Bem Viver). Envio: segunda-feira 14:00 → financeirodabemviver@gmail.com
#
# v1.4 (feedback Vinícius 21/09 23:25 — ÚLTIMO AJUSTE):
#   - Comparativo PDF: série "Resultado do mês" (entradas+saídas) no lugar de Saldo realizado
#   - Inadimplência: dois somatórios — TOTAL e EXCLUINDO Negociação Judicial (01.97) e
#     Possível Perda de Receita (01.99)
#   - Layout: KeepTogether — relatório completo numa página (título + tabela juntos;
#     demonstrativos quebram por bloco de categoria, nunca no meio de um bloco)
#   - Excel: abas separadas "Detalhe Previsão mês corrente" e "Detalhe Previsão mês seguinte"
#
# v1.3 (feedback 21/09 22:35 e 23:04): Média no comparativo (PDF+Excel); Consolidado com
#   Total de Receitas/Despesas/Resultado; Despesas em aberto com demonstrativo; Saldo colorido;
#   Fluxo 12m sem gráfico; Excel com cores/negrito/centralizado; detalhes agrupados por categoria.
# v1.2 (feedback 21/09): comparativo inteiro sem R$ + verde/vermelho; ordem por categoria;
#   inadimplência com todos os lançamentos; títulos únicos.
# v1.1 (feedback 21/09): filtro centro de custo BEM VIVER + transferências fora; comparativo paisagem.
# v1.0 (2026-09-21): pacote original com 11 relatórios.
# v1.5 (2026-10-05): FIX retry — req() com retry (4 tentativas, backoff 5/10/15s) para 500/502/503
#   da API Controlle (mesmo padrão do fix aplicado ao v4 Terceirizou e Pouso Alegre). 1º run de
#   05/10 falhou com HTTP 502 na 1ª tentativa.
import json, os, sys, time, urllib.request, urllib.error
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

BASE = "https://api-v1.controlle.com"
_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".controlle_token_bemviver")
TOKEN = os.environ.get("CONTROLLE_TOKEN_BEMVIVER") or (open(_token).read().strip() if os.path.exists(_token) else "")
UA = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"}
LARANJA = colors.HexColor("#ff501c")
LARANJA_CLARO = colors.HexColor("#ffe3d6")
PRETO = colors.HexColor("#1a1a1a")
CINZA = colors.HexColor("#f5f5f5")

MES_PT = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
MES_AB = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
TAG_BOLETO = 130213  # "Boleto Emitido"

def req(url, _tent=0):
    r = urllib.request.Request(url)
    for k, v in UA.items():
        r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        # 500/502/503 = instabilidade da API Controlle — retry com backoff (4 tentativas)
        if e.code in (500, 502, 503) and _tent < 3:
            time.sleep(5 * (_tent + 1))
            return req(url, _tent + 1)
        raise
