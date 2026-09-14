# Changelog — pipeline Captação de Leads

## 2026-09-14
- **commit 78b55d0** — Fix corrida de arquivos entre os dois crons (a5b0 e 91e0856): ambos gravavam saves MCP no mesmo `tmp/polling/`; rodadas simultâneas truncavam `cora.json` (JSONDecodeError no transform) e apagavam os `meta_ads_*.json` do outro job. `transform.py` agora aceita `POLLING_TMP` (default mantém `tmp/polling`); `run.sh` do a5b0 exporta `POLLING_TMP=$PWD/tmp/polling_a5b0`. Cuidado operacional: se o cora.json não é salvo na rodada, o estado de cora sai como `{}` no salvamento — salvar as 3 fontes sempre.
- **Fix paginação no dedup** — `processar.py` carregava apenas o primeiro lote (`perPage=300`, sem `page`); com ~320+ leads no CRM, leads fora do lote não entravam no dedup e linhas antigas eram re-criadas. Agora carrega todas as páginas (`perPage=200` + loop até `totalItems`). Efeito observado: 1 rodada com 17 updates (re-sincronização única dos leads fora da janela), rodadas seguintes 0/0 — estável.
- Validação: run.sh completo com as 3 fontes → 0 criados / 0 atualizados / 38 ignorados (esperado: criptografados Cora + linhas de teste); 2 rodadas consecutivas sem updates.

## 2026-09-10
- FIX ping-pong infinito Isamara×Sperka (hashes em lista por chave), FIX briga de pipelines (a5b0 usa pipeline live), FIX corrida no leads_input.json (LEADS_INPUT_PATH por job), FIX linha sem nome.

## 2026-09-08
- Fix UA na renovar_token() (renovação falhava em silêncio desde 01/09). Commits 9428922 + f1c23cd.

## 2026-09-01
- renovar_token() automático em 401/403; transform.py alinhado ao converter.py. Commit 1cf94e0.
