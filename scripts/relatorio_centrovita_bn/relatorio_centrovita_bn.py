#!/usr/bin/env python3
# Relatórios Semanais — BEM VIVER (ILPI) — v1, 2026-09-21
# Uso: python3 relatorio_bemviver.py [YYYY-MM-DD]  (default: hoje)
# Gera UM PDF + UM Excel com os 11 relatórios no padrão dos exemplos de 14/09.
# Fonte: API Controlle v1 (token Centrovita). Envio: segunda-feira 14:00 → raulroliveira@hotmail.com
import json, os, sys, time, urllib.request
from collections import defaultdict
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

BASE = "https://api-v1.controlle.com"
_token = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".controlle_token_centrovita_bn")
