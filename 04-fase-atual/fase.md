# Fase 1 — Tarefas gerais

**Fonte de verdade técnica:** projeto CRM Oficial no Skip, projectId 51268.  
**Última auditoria:** 2026-08-25.  
**Regra:** o status abaixo reflete somente o que está comprovado no código, nas migrations aplicadas e nos testes observáveis do Skip.

## Estado consolidado

- **Fase:** 1 — Sistema central de captura, dados e pipeline
- **Tasks com implementação/evidência no Skip:** F1-T01, F1-T02, F1-T03, F1-T04, F1-T05, F1-T06, F1-T07, F1-T08 e F1-T09
- **Task ainda não comprovada no Skip:** F1-T10
- **Contagem operacional:** 9/10 tasks com execução registrada; F1-T10 permanece pendente de prova final
- **Produção:** não publicada
- **Preview:** https://crm-oficial-65bb8--preview.goskip.app

## Tasks

| ID     | Task                                                              | Evidência real no Skip                                                           | Status auditado                             |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------- |
| F1-T01 | Confirmar plataforma, conta, papéis, campos e RLS                 | Decisão registrada no handoff GitHub; Skip projectId 51268 confirmado            | ✅ EXECUTADA — documentação fora do Skip    |
| F1-T02 | Configurar modelo de lead/oportunidade, pipeline, RLS e histórico | migrations 0001, 0002 e 0003 aplicadas; collection `leads`; frontend Index       | ✅ EXECUTADA                                |
| F1-T03 | Provar modelo, RLS, histórico e bordas                            | testes de API registrados no handoff GitHub; código/estrutura presentes no Skip  | ✅ EXECUTADA — evidência de teste no GitHub |
| F1-T04 | Confirmar formulário, conector, campos e idempotência             | contrato registrado no handoff GitHub; não há Apps Script dentro do projeto Skip | ✅ EXECUTADA — documentação fora do Skip    |
| F1-T05 | Configurar captura, validação e upsert idempotente                | hook `pocketbase/hooks/webhook_lead.js`; webhook POST `/backend/v1/webhook/lead` | ✅ EXECUTADA                                |
| F1-T06 | Provar criação e replay idempotente                               | webhook testado: criação `201`, replay `200`, mesmo `lead_id`                    | ✅ EXECUTADA — teste de API                 |
| F1-T07 | Provar ausências, schema inválido e permissão                     | webhook valida nome/origem/body e retorna `400` sem falso sucesso                | ✅ EXECUTADA — teste de API                 |
| F1-T08 | Confirmar fila, retenção, retry, alerta e pausa                   | migration 0004, collection `error_log` e política registrada no handoff          | ✅ EXECUTADA                                |
| F1-T09 | Configurar fila de recuperação e replay manual                    | hook `replay_lead.js`, rota `/backend/v1/replay/lead`, página `/fila`            | ✅ EXECUTADA                                |
| F1-T10 | Provar falha, replay, reconciliação e RLS da recuperação          | nenhum artefato ou relatório de F1-T10 encontrado no Skip                        | 🟡 PENDENTE — não marcar como concluída     |

## Inventário técnico confirmado no Skip

### Migrations aplicadas

- `0001_create_leads`
- `0002_seed_admin_and_test_lead`
- `0003_fix_rls_and_role`
- `0004_create_error_log`

### Collections ativas

- `users` (auth)
- `leads` (base)
- `error_log` (base)

### Hooks ativos

- `webhook_lead.js` — captura, validação, upsert e logging
- `replay_lead.js` — replay manual com motivo, operador e dedup_key

### Frontend presente

- `src/pages/Index.tsx` — login, tabela de leads e cards de resumo
- `src/pages/FilaRecuperacao.tsx` — fila de erros e modal de replay
- `src/App.tsx` — rotas `/` e `/fila`

## Próxima ação única

Executar e comprovar F1-T10: falha sintética, replay controlado, reconciliação de amostra, teste de acesso negativo e relatório final. Até essa prova, a Fase 1 não está encerrada.
