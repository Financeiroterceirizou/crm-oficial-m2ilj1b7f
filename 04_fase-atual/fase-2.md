# Fase 2 — Qualificação e roteamento de leads

**Fonte de verdade técnica:** projeto CRM Oficial no Skip, projectId 51268.
**Última sincronização:** 2026-09-04.
**Versão Skip validada:** v0.0.35 (`e4ae9f5`).
**Status:** 5/5 tasks concluídas e aprovadas pelo champion; aguardando apenas validação formal do consultor para encerramento administrativo.

## Tasks realizadas

| ID | Task | Evidência sincronizada | Status |
|---|---|---|---|
| F2-T01 | Definir e validar regra v1 de qualificação | Regra determinística: carteira de serviços, exclusões comércio/indústria, receita, cargo decisor, limiar 4, estados e SLA de revisão | ✅ CONCLUÍDA |
| F2-T02 | Adicionar campos de qualificação ao CRM | Migration `pocketbase/migrations/0006_add_qualificacao_fields.js`; 6 campos aditivos em `leads`; rollback limitado aos campos novos | ✅ CONCLUÍDA |
| F2-T03 | Automatizar classificação na criação e atualização | Hooks `qualificar_lead_create.js` e `qualificar_lead_update.js`; classificação determinística, score explicável e reclassificação somente quando `respostas` muda | ✅ CONCLUÍDA |
| F2-T04 | Criar fila de revisão e correção humana auditável | Hooks `fila_revisao.js` e `revisar_lead.js`; rotas `/backend/v1/fila-revisao` e `/backend/v1/revisar-lead`; histórico preservado | ✅ CONCLUÍDA |
| F2-T05 | Provar regressão, acesso, rollback e histórico | Regressão CA-2-001..004; acesso por papel CA-2-005 com 404; rollback preservando histórico; 2 eventos auditáveis; aceite do champion no commit `1fbf13b` | ✅ CONCLUÍDA |

## Regra v1

- Estados: `qualificado`, `nao_qualificado`, `pendente_revisao`, `excecao`.
- Peso de segmento na carteira: `+2`.
- Peso de receita/faturamento informado: `+2`.
- Peso de cargo decisor: `+1`.
- Segmento excluído (comércio/indústria): não qualificar.
- Prestador negativo: não qualificar.
- Limiar de qualificação: `score >= 4`.
- Dados incompletos ou conflito entre respostas: revisão humana.
- SLA de revisão: 24 horas úteis.
- Responsáveis: Henrique para leads de Meta Ads, Cora e manual; Vinícius para exceções.

## Campos adicionados em `leads`

- `estado_qualificacao`
- `score`
- `score_componentes`
- `regra_versao`
- `motivo_decisao`
- `proxima_acao`

## Limite da sincronização

A documentação da Fase 1 permanece preservada nos commits anteriores. Esta atualização sincroniza os artefatos técnicos e o registro da Fase 2; não altera a regra de negócio nem cria frontend novo da Fase 3.
