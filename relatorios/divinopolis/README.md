# Divinópolis (F COSTA) Vistoria — Relatório Mensal (formato Uberlândia v1.2)

Cron **6a3e1a8f5c4cd4df** — dia 04 de cada mês, 14:00.

## Como rodar

```bash
bash scripts/6a3e1a8f5c4cd4df/run.sh
# = python3 scripts/relatorio_divinopolis/relatorio_divinopolis.py
# + python3 scripts/relatorio_divinopolis/enviar_divinopolis.py
```

- Token: `scripts/relatorio_divinopolis/.controlle_token_divinopolis` (fora do repo)
- Saída: `artifacts/<data>_Relatorio_Divinopolis.pdf` + `.xlsx`
- Destino: vinicius@terceirizou.com.br (Resend, idempotência por mtime dos arquivos)

## Execuções

| Data | Mês de ref. | Receitas | Despesas | Resultado | Saldo fim | Envio |
|---|---|---|---|---|---|---|
| 04/10/2026 | setembro/26 (competência) | 19.993,17 | −18.685,53 | **+1.307,64** | 10.065,40 | 01a107e8 |

Histórico anterior (formato aprovado): ago/26 competência 19.251,02 / −18.683,91 = +567,11 (após correção de lançamentos pelo cliente; 1º envio tinha −3.615,60).
