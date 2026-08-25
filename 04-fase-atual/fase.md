# Fase 1 — Tarefas gerais

**Fonte de verdade técnica:** projeto CRM Oficial no Skip, projectId 51268.  
**Última atualização:** 2026-08-25.  
**Status:** Fase 1 concluída — 10/10 tasks.

## Tasks

| ID     | Task                                              | Evidência real no Skip                                | Status       |
| ------ | ------------------------------------------------- | ----------------------------------------------------- | ------------ |
| F1-T01 | Confirmar plataforma, conta, papéis, campos e RLS | Decisão registrada; Skip projectId 51268 confirmado   | ✅ CONCLUÍDA |
| F1-T02 | Configurar modelo, pipeline, RLS e histórico      | Migrations 0001–0003; collection `leads`; frontend    | ✅ CONCLUÍDA |
| F1-T03 | Provar modelo, RLS, histórico e bordas            | Relatório e testes de API                             | ✅ CONCLUÍDA |
| F1-T04 | Confirmar formulário, conector e idempotência     | Contrato de captura registrado                        | ✅ CONCLUÍDA |
| F1-T05 | Configurar captura, validação e upsert            | Hook `webhook_lead.js`                                | ✅ CONCLUÍDA |
| F1-T06 | Provar criação e replay idempotente               | Criação `201`; replay `200`; mesmo `lead_id`          | ✅ CONCLUÍDA |
| F1-T07 | Provar ausências, schema inválido e permissão     | Validações `400` sem falso sucesso                    | ✅ CONCLUÍDA |
| F1-T08 | Confirmar fila, retenção, retry, alerta e pausa   | Collection `error_log` e política                     | ✅ CONCLUÍDA |
| F1-T09 | Configurar fila e replay manual                   | Hook `replay_lead.js`, rota e página `/fila`          | ✅ CONCLUÍDA |
| F1-T10 | Provar falha, replay, reconciliação e RLS         | Relatório final; migration 0005; quatro CAs aprovados | ✅ CONCLUÍDA |

## Resultado da Fase 1

- **Tasks:** 10/10 concluídas
- **CA-1-001 a CA-1-012:** evidências registradas conforme as SPECs
- **RLS da fila:** leitura anônima bloqueada; usuário autenticado autorizado
- **Fonte histórica:** preservada
- **Produção:** publicada após QA final

## Inventário técnico

### Migrations aplicadas

- `0001_create_leads`
- `0002_seed_admin_and_test_lead`
- `0003_fix_rls_and_role`
- `0004_create_error_log`
- `0005_fix_error_log_rls`

### Collections

- `users` (auth)
- `leads` (base)
- `error_log` (base)

### Hooks

- `webhook_lead.js` — captura, validação, upsert e logging
- `replay_lead.js` — replay manual com motivo, operador e `dedup_key`

### Frontend

- `src/pages/Index.tsx` — login, tabela de leads e resumo
- `src/pages/FilaRecuperacao.tsx` — fila de erros e replay
- `src/App.tsx` — rotas `/` e `/fila`

## Encerramento

A Fase 1 foi concluída após a aprovação humana do champion em 2026-08-25. Nenhuma task da próxima fase foi iniciada.
