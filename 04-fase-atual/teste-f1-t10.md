# Relatório de Prova — F1-T10

> **Data:** 2026-08-25 · **Projeto:** CRM Oficial · **Skip projectId:** 51268
> **Versão auditada:** v0.0.22 / 3734b8a

## Resultado

| Critério                                                                         | Resultado | Evidência                                                                                                                            |
| -------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| CA-1-009 — falha visível com referência, categoria, horário, dono e próxima ação | ✅ PASSOU | Evento `t10-falha-001` criou item `error_log` categoria `validacao`, estado `pendente`, dono Henrique Tavano e próxima ação definida |
| CA-1-010 — replay controlado sem duplicidade, com operador e motivo              | ✅ PASSOU | Lead `cTjUNsQTmvnf`, replay `200`, mesma referência, operador Vinicius e motivo registrado                                           |
| CA-1-011 — reconciliação sem alterar fonte                                       | ✅ PASSOU | Amostra sintética: 5/5 campos correspondentes; divergências=0; fonte_modificada=false                                                |
| CA-1-012 — acesso negativo e proteção de fila/log                                | ❌ FALHOU | Consulta sem autenticação à collection `error_log` retornou HTTP 200 e dados; `listRule`/`viewRule` estão vazias                     |

## Evidências técnicas

- Falha sintética: `POST /backend/v1/webhook/lead` sem `nome` → HTTP 400
- Item criado na fila: `error_id=7mr8HYYGOveL`, `source_event_id=t10-falha-001`
- Replay: `lead_id=cTjUNsQTmvnf`, `status=replayed`
- Reconciliação: `source_event_id`, nome, email, telefone e origem correspondentes
- Acesso sem autenticação à fila: HTTP 200 — exposição confirmada

## Conclusão

A F1-T10 **não pode ser concluída**. Três critérios passaram, mas CA-1-012 falhou. A SPEC exige parar diante de qualquer falha e corrigir o RLS antes de nova prova. A fonte histórica não foi alterada.

## Próxima ação

Corrigir o RLS de `error_log` para negar leitura sem autenticação e repetir a prova negativa. Não marcar F1-T10 como concluída até CA-1-012 passar.
