#!/bin/bash
# RELATÓRIO MENSAL POUSO ALEGRE 1 (MD) VISTORIA — dia 04, 14:00
# Gera PDF+Excel do mês anterior (relatórios 1 e 2 em competência) e envia para vinicius@terceirizou.com.br
set -e
cd "$(dirname "$0")/../.."
python3 scripts/relatorio_pouso_alegre/relatorio_pouso_alegre.py
python3 scripts/relatorio_pouso_alegre/enviar_pouso_alegre.py
