# Changelog — Projeto Terceirizou Terceirização Empresarial

> Registro de tudo que acontece no projeto, em ordem cronológica inversa.

## Registro

- 2026-09-14 · [Adapta/Ethos] · FIX polling F1-T05: cron 91e08561a5b65e5d disparou o run.sh sem a etapa de leitura MCP (tmp/polling/*.json ausentes) → rodada silenciosa com zero rows. Investigação revelou o CONTRATO DE FORMATO: os hashes do estado.json foram gerados sobre leituras FORMATTED_VALUE do Google Sheets (datas 'YYYY-MM-DD HH:MM' na Cora e 'DD/MM/YYYY HH:MM' nas abas Meta; números como string exibida — CPF com zero à esquerda, telefone com vírgulas), validado por hash-match (Sperka/Isamara/Fabiana). transform.py atualizado com o contrato documentado + GUARDA que aborta (exit 1) se receber serial UNFORMATTED (evita re-sync em massa ~114 linhas no CRM). Estado com merge-back das 38 chaves criptografadas da Cora (71/16/27 hashes) e 2 rodadas validadas 0/0/0. Commit anterior corrompido (b9b8fc8d) substituído por este.
- 2026-09-10 · [Adapta/Ethos] · FIX polling F1-T05: loop infinito de updates no lead dldr9dp92fj1tzd (colisão Cora Isamara×Sperka — mesmo telefone/e-mail, 2 linhas na planilha). Causa: `estado.json` guardava UM hash por chave de dedup; como as 2 linhas compartilham a chave, só o hash da ÚLTIMA linha (Sperka) sobrevivia e a 1ª (Isamara) era re-processada em toda rodada (update nome/respostas a cada ciclo). Correção em `scripts/captacao_leads/processar.py`: estado agora guarda LISTA de hashes por chave (legado string migrado na leitura). Validado: 2 rodadas consecutivas com 0 criados/0 atualizados.
- 2026-09-08 · [Adapta/Ethos] · FIX polling F1-T05: bug `UA` indefinido em `renovar_token()` (renovação de token JWT sempre falhava em silêncio desde 01/09); corrigido em `scripts/captacao_leads/processar.py`, token renovado e validado. Lead novo capturado (linha Cora 12/04, nome anonimizado pela Cora) — PATCH manual de correção do nome aplicado (updateRule exige role admin; responsavel='-' não atualiza pelo token comum).
- 2026-09-04 · [Adapta/Ethos] · Fase 2 sincronizada no GitHub a partir do Skip v0.0.35: F2-T01 a F2-T05, migration 0006, hooks de qualificação/fila/revisão, SPEC e status.
- 2026-09-03 · [Vinicius/Champion] · F2-T05 teste final aprovado; regressão CA-2-001..004, acesso CA-2-005, rollback e histórico comprovados; commit de referência `1fbf13b`.
- 2026-09-02 · [Vinicius/Champion] · F2-T04 concluída: fila de revisão, revisão humana e preservação de histórico.
- 2026-09-02 · [Vinicius/Champion] · F2-T03 concluída: classificação determinística na criação e atualização.
- 2026-09-02 · [Vinicius/Champion] · F2-T02 concluída: migration 0006 aplicada diretamente no Skip Cloud.
- 2026-09-01 · [Vinicius/Champion] · F2-T01 concluída: regra v1 de qualificação aprovada.
- 2026-09-01 · [Adapta/Ethos] · FIX automação de captação (F1-T05): token JWT renovado e auto-refresh no polling.
- 2026-08-25 · [Vinicius/Champion] · F1-T10 TESTE APROVADO: "Tudo certo.. Pode seguir."
- 2026-08-25 · [Adapta/Ethos] · F1-T10 FECHADA; Fase 1 encerrada com 10/10 tasks.
- 2026-08-21 · [Vinicius/Champion] · F1-T09 TESTE APROVADO.
- 2026-08-21 · [Vinicius/Champion] · F1-T08 TESTE APROVADO.
- 2026-08-21 · [Vinicius/Champion] · F1-T07 TESTE APROVADO.
- 2026-08-21 · [Vinicius/Champion] · F1-T06 TESTE APROVADO.
- 2026-08-20 · [Vinicius/Champion] · F1-T05 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T02 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T04 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T01 TESTE APROVADO.
