# SPEC-4-001 — Conector Meta Ads de leitura e origem do lead

**Fase:** 4 — Sistema de inteligência de campanhas e operação assistida  
**Status:** concluída para `cd704a1c` após correção de regressão, prova técnica e aceite humano em 22/09/2026  
**Dono:** administrador armazena credencial e prova acesso; responsável técnico implementa; marketing consome  
**Origem no escopo:** `02-Escopo-Definitivo.md`, Fase 4, seção "Sistema de inteligência de campanhas e operação assistida"; decisão Navaar de 17/09/2026 (formulário de transição): incluir Meta Ads com prova técnica timeboxed.  
**Degrau da solução:** conector compartilhado de leitura — espelha dados de campanha/anúncio/origem do Meta para dentro do CRM; nenhuma escrita no Meta, nenhuma alteração de campanha, orçamento ou público.

## Contexto e decisões fechadas

- **Estado atual:** a Fase 1 captura a origem declarada pelo lead no formulário; a Fase 2 classifica e a Fase 3 faz follow-up.
- **Estado desejado:** relacionar dados do Meta (campanha, anúncio/criativo, origem) com a qualidade e conversão dos leads já registrados; ausência de acesso vira lacuna visível, nunca inferência.
- **B4-101..104:** conta correta confirmada; credencial mantida no secret manager; escopos de leitura e amostra/período comprovados na prova técnica.

## Resultado observável

Um lead do CRM exibe, quando existir correspondência, a campanha/anúncio/origem vindos do Meta com fonte e período declarados; leads sem correspondência ficam marcados como "sem dado Meta", nunca como zero. A prova técnica documenta acesso, escopos, limites e fallback.

## Limites e dependências

- **Inclui:** prova técnica timeboxed de acesso; contrato mínimo de leitura; espelhamento idempotente; marcação explícita de ausência; log sanitizado.
- **Fora de escopo:** publicação/edição de anúncios, alteração de orçamento/público, benchmark externo, enriquecimento por LinkedIn e métricas de performance além do necessário para relacionar origem.
- **Saídas:** registro de origem/campanha/anúncio por lead com proveniência (fonte, período, data de carga); relatório da prova; lacunas visíveis.
- **Nenhuma persona escreve no Meta.**

## Dados e integrações

| Origem/destino         | Fonte de verdade                           | Campos/contrato                                                              | Autenticação/permissão                                          | Timeout/retry/idempotência                                    | Tratamento de erro                               |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------ |
| Meta → CRM             | Meta para dados de campanha; CRM para lead | `lead_id`, `campanha`, `anuncio/criativo`, `origem`, `periodo`, `data_carga` | token de leitura somente em secret manager; escopos homologados | chave `lead_id + campanha + periodo`; reprocessar não duplica | falha registra lacuna visível; sem falso sucesso |
| CRM → painel de origem | CRM                                        | proveniência por registro                                                    | acesso por papel já existente                                   | leitura pura                                                  | campo vazio ≠ zero; exibir "sem dado Meta"       |

| Regra    | Condição                                         | Ação/resultado                                           |
| -------- | ------------------------------------------------ | -------------------------------------------------------- |
| RN-4-101 | sem prova técnica aprovada ou credencial válida  | zero ingestão; pendência visível                         |
| RN-4-102 | lead sem correspondência no Meta                 | marcar "sem dado Meta"; nunca zero                       |
| RN-4-103 | dado inconsistente entre origem declarada e Meta | registrar divergência; não sobrescrever original         |
| RN-4-104 | falha de API/timeout                             | pausar espelhamento; sem retry infinito ou falso sucesso |

## Fluxo e regras

1. Administrador confirma conta e armazena credencial no cofre.
2. Prova técnica timeboxed autentica, lista escopos, lê amostra aprovada e registra limites/fallback.
3. Se a prova falhar, registrar lacuna e fallback manual aprovado; não improvisar.
4. Se aprovada, espelhar campanha/anúncio/origem por lead com proveniência completa e idempotente.
5. Expor divergências e ausências como lacuna visível.

## Critérios de aceite

- [x] **CA-4-101:** sem prova técnica aprovada, nenhuma ingestão acontece e a pendência fica visível. RED com credencial inválida/ausente comprovou zero ingestão.
- [x] **CA-4-102:** com prova aprovada, cada lead espelhado exibe campanha/anúncio/origem com fonte, período e data de carga. Prova: 50 leads avaliados, 44 espelhados com proveniência.
- [x] **CA-4-103:** lead sem correspondência exibe "sem dado Meta"; divergência fica registrada sem sobrescrever o original. Prova: 6 sem dado Meta e 0 divergentes.
- [x] **CA-4-104:** credencial não aparece em Git, log ou tela; falha de API não cria falso sucesso nem duplicidade. Prova: segredo fora do Git/tela, falha RED e duas rodadas idempotentes.

## TDD da SPEC

| Etapa     | Prova                                  | Resultado observado                                   | Evidência                        |
| --------- | -------------------------------------- | ----------------------------------------------------- | -------------------------------- |
| RED       | credencial inválida/ausente            | zero ingestão, lacuna visível                         | prova técnica B4-103             |
| GREEN     | prova aprovada + amostra               | 44 espelhados, 6 lacunas, sem duplicidade             | registros CRM + commit `e37b38d` |
| REGRESSÃO | ausência, divergência e falha simulada | "sem dado Meta", divergência explícita e pausa segura | roteiro sanitizado + estado CRM  |

## Evidência e aceite

- Leitura técnica: 76 anúncios, 12 conjuntos e 6 campanhas.
- Espelhamento: 50 leads Meta avaliados; 44 espelhados; 6 sem dado Meta; 0 divergentes.
- Idempotência: duas rodadas idênticas sem duplicidade.
- Interface: `MetaLeadsRealCard` lê a collection real `leads` via PocketBase e exibe campanha, anúncio, status, filtros e proveniência.
- Correção de regressão: `LeadScheduleCard` recupera lista real, detalhe e formulário autenticado de agendamento; aceite humano no preview em 22/09/2026 — "Aparece o formulário"; nenhum evento real enviado ao Calendar.
- QA Skip: 5/5 nas versões do ciclo; fechamento documental final no Skip após o aceite humano.
- Aceite do champion: espelho Meta em 22/09/2026 — "testei no preview e funcionou"; correção de acesso a leads/agendamento em 22/09/2026 — "Aparece o formulário".

## Tasks vinculadas

| ID       | Task                                         | Status                    |
| -------- | -------------------------------------------- | ------------------------- |
| e4c77e80 | Confirmar acesso de leitura à conta Meta     | ✅ CONCLUÍDA (22/09/2026) |
| cd704a1c | Trazer origem, campanha e anúncio para o CRM | ✅ CONCLUÍDA (22/09/2026) |
