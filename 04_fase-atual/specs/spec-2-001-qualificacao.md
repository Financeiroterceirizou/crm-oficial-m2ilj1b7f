# SPEC-2-001 — Qualificação e roteamento de leads

## Objetivo

Classificar leads capturados no CRM de forma determinística, explicável e auditável, sem substituir a revisão humana nos casos incompletos ou conflitantes.

## Estados

- `qualificado`
- `nao_qualificado`
- `pendente_revisao`
- `excecao`

## Regra v1

1. Prestador negativo explícito: `nao_qualificado`.
2. Comércio ou indústria: `nao_qualificado`.
3. Segmento ou cargo ausente: `pendente_revisao`.
4. Segmento não mapeado: `excecao`.
5. Segmento na carteira vale `+2`.
6. Receita/faturamento informado vale `+2`.
7. Cargo decisor vale `+1`.
8. Score igual ou superior a 4: `qualificado`.
9. Score inferior a 4: `pendente_revisao`.

## Campos de decisão

A collection `leads` registra o estado, score, componentes do score, versão da regra, motivo legível e próxima ação.

## Revisão humana

A fila retorna apenas leads `pendente_revisao` ou `excecao` e exige autenticação. A revisão exige operador, decisão e motivo. Toda alteração acrescenta um evento ao campo `historico`; o histórico anterior não é apagado.

## Critérios comprovados

- CA-2-001..004: classificação, atualização, fila e revisão auditável.
- CA-2-005: acesso sem autenticação negado com 404.
- Rollback: remove somente os seis campos adicionados pela migration 0006.
- Teste final: regressão aprovada pelo champion; aceite registrado no commit `1fbf13b`.
