# Relatório de Prova — F1-T10

> **Data:** 2026-08-25 · **Projeto:** CRM Oficial · **Skip projectId:** 51268
> **Versão:** v0.0.25 / 939d4eb

## Resultado consolidado

| Critério                                                                         | Resultado | Evidência                                                                                                                                         |
| -------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| CA-1-009 — falha visível com referência, categoria, horário, dono e próxima ação | ✅ PASSOU | Evento sintético criou item no `error_log` com categoria `validacao`, estado `pendente`, dono Henrique Tavano e próxima ação definida             |
| CA-1-010 — replay controlado sem duplicidade, com operador e motivo              | ✅ PASSOU | Replay manual retornou `200`, preservou o mesmo `lead_id`/`dedup_key` e registrou operador e motivo no histórico                                  |
| CA-1-011 — reconciliação sem alterar fonte                                       | ✅ PASSOU | Amostra sintética com 5/5 campos correspondentes; divergências=0; fonte histórica preservada                                                      |
| CA-1-012 — acesso negativo e proteção da fila/log                                | ✅ PASSOU | Após migration 0005, consulta anônima retornou HTTP 200 com `items=[]` e `totalItems=0`; consulta autenticada retornou HTTP 200 com itens da fila |

## Evidências técnicas

### CA-1-009

- Falha sintética: `POST /backend/v1/webhook/lead` sem `nome` → HTTP 400
- Item de recuperação criado com referência segura, categoria, horário, dono e próxima ação
- Payload completo/segredo não foi gravado no log

### CA-1-010

- Replay manual exige `dedup_key`, `motivo` e `operador`
- Replay executado → HTTP 200
- Mesmo `lead_id` e mesma `dedup_key` preservados
- Histórico registra a ação do operador

### CA-1-011

- Reconciliação de amostra sintética executada
- 5/5 campos correspondentes
- Divergências: 0
- Fonte anterior: não modificada

### CA-1-012

- Antes da correção: `error_log` permitia leitura anônima — falha registrada
- Migration `0005_fix_error_log_rls` aplicada no Skip
- `listRule`: `@request.auth.id != ''`
- `viewRule`: `@request.auth.id != ''`
- Consulta sem autenticação: HTTP 200, `items=[]`, `totalItems=0`
- Consulta autenticada como administrador: HTTP 200, fila acessível
- Nenhum segredo foi incluído nas evidências

## Conclusão

Os quatro critérios da F1-T10 estão tecnicamente comprovados no Skip.

A F1-T10 permanece em `aguardando_teste_humano` até o champion confirmar a prova final. Após a aprovação, atualizar estado, STATUS, fase e changelog para conclusão da F1-T10 e encerramento da Fase 1.
