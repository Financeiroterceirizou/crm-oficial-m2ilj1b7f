#!/bin/bash
# Cron mensal DARKE ESTRATEGIA — dia 03 14:00
cd /home/ethos/.assistant/workspace
python3 scripts/relatorio_darke/relatorio_darke.py > tmp/darke_gera.log 2>&1
python3 scripts/relatorio_darke/enviar_darke.py
