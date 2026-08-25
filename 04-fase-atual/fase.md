# Fase 1 — Tarefas gerais

**Fonte de verdade técnica:** projeto CRM Oficial no Skip, projectId 51268.  
**Última auditoria:** 2026-08-25.  
**Regra:** o status abaixo reflete somente o que está comprovado no código, nas migrations aplicadas e nos testes observáveis do Skip.

## Estado consolidado

- **Fase:** 1 — Sistema central de captura, dados e pipeline
- **Tasks com implementação/evidência:** F1-T01, F1-T02, F1-T03, F1-T04, F1-T05, F1-T06, F1-T07, F1-T08 e F1-T09
- **F1-T10:** em correção — CA-1-009, CA-1-010 e CA-1-011 passaram; CA-1-012 falhou
- **Produção:** não publicada
- **Preview:** https://crm-oficial-65bb8--preview.goskip.app

## Tasks

| ID     | Task                                              | Resultado auditado                                            | Status         |
| ------ | ------------------------------------------------- | ------------------------------------------------------------- | -------------- |
| F1-T01 | Confirmar plataforma, conta, papéis, campos e RLS | Decisão registrada; Skip projectId 51268 confirmado           | ✅ EXECUTADA   |
| F1-T02 | Configurar modelo, pipeline, RLS e histórico      | migrations 0001–0003; `leads`; frontend                       | ✅ EXECUTADA   |
| F1-T03 | Provar modelo, RLS, histórico e bordas            | Provas registradas no handoff                                 | ✅ EXECUTADA   |
| F1-T04 | Confirmar formulário, conector e idempotência     | Contrato registrado                                           | ✅ EXECUTADA   |
| F1-T05 | Configurar captura e upsert                       | `webhook_lead.js`                                             | ✅ EXECUTADA   |
| F1-T06 | Provar criação e replay                           | Criação 201; replay 200; mesmo lead_id                        | ✅ EXECUTADA   |
| F1-T07 | Provar ausências e erros                          | Validações 400 sem falso sucesso                              | ✅ EXECUTADA   |
| F1-T08 | Confirmar recuperação                             | `error_log` e política registrados                            | ✅ EXECUTADA   |
| F1-T09 | Configurar fila e replay manual                   | `replay_lead.js` e frontend `/fila`                           | ✅ EXECUTADA   |
| F1-T10 | Provar falha, replay, reconciliação e RLS         | 3 critérios passaram; acesso anônimo à fila retornou HTTP 200 | 🔧 EM CORREÇÃO |

## Prova F1-T10

Relatório: `04-fase-atual/teste-f1-t10.md`

- CA-1-009: ✅ passou
- CA-1-010: ✅ passou
- CA-1-011: ✅ passou
- CA-1-012: ❌ falhou — `error_log` permite leitura sem autenticação

## Próxima ação única

Corrigir o RLS de `error_log` para impedir leitura anônima e repetir CA-1-012. A F1-T10 e a Fase 1 permanecem abertas até aprovação.
