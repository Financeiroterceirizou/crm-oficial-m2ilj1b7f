# SPEC-4-003 — Loops assistidos: análise de aprendizados (L4.1) e monitor de qualidade por origem (L4.2)

**Fase:** 4 — Sistema de inteligência de campanhas e operação assistida
**Status:** planejada — criada em 16/10/2026 para destravar as tasks `1a38ea22` (L4.1) e a task de monitor de qualidade (L4.2) do fase.md
**Dono:** champion define cadência, teto, pausa e limiar; responsável comercial valida recomendações; assistente executa e audita
**Origem no escopo:** `02-Escopo-Definitivo.md`, Fase 4 (loops de análise e monitor de qualidade); tasks `1a38ea22`, `82524cff` e a task "Monitorar queda de qualidade por origem com baseline" do fase.md
**Degrau da solução:** análise e monitor assistidos — nenhum toque em campanha, orçamento ou público; recomendação sempre com trilha de auditoria; veredito sempre humano

## Contexto e decisões fechadas

- **Estado atual:** a Fase 4 tem espelho Meta (SPEC-4-001), painel de qualidade por campanha (CA-4-201) e fila de reativação concluída (`5ef4b7cd`). Não existe loop de análise nem monitor de queda de qualidade: as duas tasks estão no fase.md sem SPEC e bloqueadas.
- **Estado desejado:** dois loops assistidos, **um por vez** — L4.1 primeiro; L4.2 só depois do L4.1 concluído. L4.1 gera aprendizados de campanha (fato observado, fonte, período, limitação, recomendação) com trilha de auditoria que reconstrói fonte e período. L4.2 sinaliza queda ou diferença de qualificação por origem **somente contra baseline registrado**; sem baseline, o sinal sai rotulado como hipótese.
- **Decisões fechadas:** um loop por vez; loop não publica anúncio nem modifica campanha (bloqueio demonstrado por prova negativa); loop não altera regras de qualificação sozinho; sem baseline o sinal é hipótese, nunca fato.
- **Bloqueios (B4-301..304) — a aprovar pelo champion, sem inferência:** (B4-301) cadência do L4.1; (B4-302) teto de custo por execução; (B4-303) gatilho e comportamento de pausa do loop; (B4-304) definição operacional de "queda relevante" para o L4.2 (limiar contra baseline). Nenhum loop entra em produção com bloqueio aberto.

## Resultado observável

O champion recebe, na cadência aprovada, uma análise com fato observado, fonte, período, limitação e recomendação — cada item reconstrutível pela trilha de auditoria (fonte + período). O responsável comercial revisa as recomendações (task `82524cff`) e registra aceita/rejeitada/precisa de mais informação, com autor e data. O L4.2, depois de ativado, sinaliza queda ou diferença de qualificação por origem somente contra baseline registrado; sem baseline, o sinal sai rotulado como hipótese. Em nenhum momento um anúncio é publicado ou uma campanha é modificada.

## Limites e dependências

- **Inclui:** loop L4.1 (análise com trilha de auditoria); loop L4.2 (monitor contra baseline); registro de baseline por origem; rotulagem sinal × hipótese; trilha de auditoria consultável; prova negativa de escrita no Meta.
- **Fora de escopo:** publicar/editar anúncio, orçamento, público ou qualquer objeto do Meta; alteração automática de regras de qualificação; envio de contato; decisão automática de campanha; benchmark externo.
- **Entradas:** dados Meta espelhados (SPEC-4-001); leads e qualificação (F2); painel de qualidade (SPEC-4-002); baseline registrado; bloqueios B4-301..304 aprovados.
- **Saídas:** análise com fato/fonte/período/limitação/recomendação; sinais de queda rotulados; trilha de auditoria; registros de pausa e bloqueio.
- **Atores/permissões:** assistente executa e registra; responsável comercial valida recomendações; champion define cadência/teto/pausa/limiar e aprova a ativação de cada loop; RLS da F1 permanece.
- **Risco/plano B:** análise sem dado suficiente → registra limitação e não inventa fato; custo acima do teto → pausa automática com registro; baseline ausente → sinal sai como hipótese, nunca como fato.
- **Rollback:** pausar loop sem apagar histórico; baseline e análises ficam preservados.

## Dados e integrações

| Origem/destino                           | Fonte de verdade           | Campos/contrato                                                   | Autenticação/permissão    | Timeout/retry/idempotência               | Tratamento de erro                                 |
| ---------------------------------------- | -------------------------- | ----------------------------------------------------------------- | ------------------------- | ---------------------------------------- | -------------------------------------------------- |
| CRM + Meta espelhado (4-001) → loop L4.1 | CRM e espelho              | origem, campanha, anúncio, leads, qualificação, período declarado | leitura pura; RLS herdada | rodada única e idempotente               | sem dado → limitação declarada, sem fato inventado |
| loop L4.1 → registro de análise          | CRM (registro append-only) | fato, fonte, período, limitação, recomendação, trilha             | registro por rodada       | idempotente por rodada                   | rodada sem dado válido → "sem sinal" registrado    |
| loop L4.2 → baseline + sinal             | CRM                        | baseline por origem (período, valores), sinal rotulado            | leitura + registro        | comparação só contra baseline registrado | sem baseline → hipótese rotulada                   |

| Regra    | Condição                                 | Ação/resultado                       | Exceção                       |
| -------- | ---------------------------------------- | ------------------------------------ | ----------------------------- |
| RN-4-301 | bloqueio B4-301/302/303 aberto           | loop L4.1 não entra em produção      | pendência visível ao champion |
| RN-4-302 | execução acima do teto de custo (B4-302) | pausa automática + registro          | champion decide a retomada    |
| RN-4-303 | análise sem fato verificável no período  | registra limitação, não publica fato | sem invenção de dado          |
| RN-4-304 | sinal sem baseline registrado (B4-304)   | sai rotulado como hipótese           | nunca como fato               |
| RN-4-305 | tentativa de publicar/modificar campanha | bloqueada e registrada               | prova negativa obrigatória    |
| RN-4-306 | L4.2 ativado com L4.1 ainda ativo        | ativação recusada — um loop por vez  | pendência visível ao champion |

## Fluxo e regras

1. Champion aprova B4-301/302/303 (cadência, teto, pausa).
2. Prompt do L4.1 é homologado e versionado antes da primeira rodada.
3. Cada rodada do L4.1: lê dados do período declarado → gera fato/fonte/período/limitação/recomendação → registra com trilha de auditoria → para. Nada toca o Meta.
4. Responsável comercial revisa as recomendações (task `82524cff`) e registra decisão com autor e data.
5. Após o L4.1 concluído, champion aprova B4-304 e ativa o L4.2: baseline por origem registrado → sinaliza queda/diferença somente contra baseline → sem baseline, hipótese.
6. Prova negativa permanente: tentativa de escrita no Meta é bloqueada e registrada.

| Cenário   | Dado/condição                            | Resultado esperado                           | Recuperação     |
| --------- | ---------------------------------------- | -------------------------------------------- | --------------- |
| Principal | B4-301..303 aprovados + dados do período | análise registrada com trilha reconstrutível | —               |
| Limite    | sinal de queda sem baseline              | sai rotulado como hipótese                   | —               |
| Falha     | execução acima do teto                   | pausa automática + pendência                 | champion decide |

## Instruções de execução para o Ethos

1. Ler esta SPEC, SPEC-4-001 (espelho Meta) e SPEC-4-002 (qualidade).
2. Não ativar loop com B4-301..304 abertos — parar e registrar pendência.
3. Implementar bloqueio duro: nenhuma chamada de escrita ao Meta no código do loop; prova negativa obrigatória.
4. Toda análise registra fato, fonte, período, limitação e recomendação com trilha reconstrutível.
5. L4.2 só depois do L4.1 concluído; baseline registrado antes do primeiro sinal.

## Checklist de execução

- [ ] cadência do L4.1 aprovada pelo champion (B4-301)
- [ ] teto de custo por execução aprovado (B4-302)
- [ ] gatilho e comportamento de pausa aprovados (B4-303)
- [ ] definição operacional de "queda relevante" aprovada (B4-304)
- [ ] prompt do L4.1 homologado e versionado
- [ ] prova negativa de escrita no Meta executada e registrada
- [ ] baseline do L4.2 registrado antes do primeiro sinal

## Critérios de aceite

- [ ] **CA-4-301:** loop L4.1 configurado um por vez, com cadência aprovada (B4-301), prompt homologado e versionado; bloqueio de escrita no Meta demonstrado por prova negativa.
- [ ] **CA-4-302:** toda execução respeita o teto de custo (B4-302); acima do teto → pausa automática com registro (B4-303).
- [ ] **CA-4-303:** L4.2 sinaliza queda/diferença de qualificação por origem somente contra baseline registrado; sem baseline sai rotulado como hipótese; não altera regras sozinho.
- [ ] **CA-4-304:** recomendações revisadas pelo responsável comercial com registro aceita/rejeitada/precisa de mais informação, com autor e data (task `82524cff`).
- [ ] **CA-4-305:** cada análise tem fato observado, fonte, período, limitação e recomendação, com trilha de auditoria que reconstrói fonte e período.

## TDD da SPEC

| Etapa              | Prova                                                                                              | Ação                       | Resultado esperado                                                         | Evidência            |
| ------------------ | -------------------------------------------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------------- | -------------------- |
| RED                | bloqueio B4-301..304 aberto                                                                        | tentar ativar loop         | zero loop em produção, pendência visível                                   | estado do sistema    |
| GREEN              | bloqueios aprovados + fixtures (rodada com dado, sem dado, sinal com baseline, sinal sem baseline) | rodar L4.1 e L4.2          | análise completa com trilha; hipótese rotulada sem baseline; pausa no teto | roteiro + registros  |
| REFACTOR/REGRESSÃO | tentar publicar anúncio/modificar campanha; ativar L4.2 com L4.1 ativo                             | exercitar provas negativas | bloqueio registrado; ativação recusada                                     | logs + aceite humano |

**Dados/fixtures:** rodada com dado completo; rodada sem dado no período; sinal com baseline; sinal sem baseline; tentativa de escrita no Meta.
**Caminhos de erro obrigatórios:** bloqueio aberto, teto estourado, sem dado no período, sinal sem baseline, tentativa de escrita.
**Evidência exigida:** recibo dos B4-301..304, prompt homologado versionado, registros de rodada com trilha, prova negativa, aceite humano.

## Configuração no Ethos

- **Tipo:** automação de apoio (loops assistidos de análise e monitor)
- **Sistemas das fases usados:** F1 (leads, RLS), F2 (qualificação: SPEC-2-001), F4-001 (espelho Meta), F4-002 (painel de qualidade)
- **Agente responsável:** assistente principal do cliente; veredito sempre humano

### Meta

- **Nome curto:** Loops L4.1 e L4.2
- **O que atingir:** aprendizados de campanha e alerta de qualidade com proveniência, custo controlado e zero escrita no Meta
- **Prazo do ciclo:** definido na Jornada F4
- **Valor estimado:** [opcional e com fonte]

### Validação

- **Como saber que foi atingido:** análises com trilha reconstrutível; sinais rotulados corretamente; 0 escrita no Meta; 0 execução acima do teto
- **Modo:** assistente mede | humano valida
- **Fonte independente:** registros de rodada × trilha de auditoria
- **Baseline / alvo / unidade:** 100% das análises com trilha; 0 tentativa de escrita bem-sucedida; 0 sinal sem rotulagem
- **Cadência:** definida pelo champion (B4-301)
- **Responsável pelo veredito:** responsável comercial (recomendações) e champion (bloqueios e ativação)

### Conectores e skills

| Item                               | Tipo     | Uso                             | Permissão/entrada     | Saída               | Plano B           |
| ---------------------------------- | -------- | ------------------------------- | --------------------- | ------------------- | ----------------- |
| Dados internos CRM                 | fonte    | análise e monitor               | RLS por papel         | registros de rodada | exportação manual |
| Dados Meta espelhados (SPEC-4-001) | conector | enriquecer análise por campanha | proveniência da 4-001 | colunas de campanha | só dados internos |

### Arranque

- **Instruções permanentes:** um loop por vez; nada toca o Meta; sem baseline é hipótese; trilha sempre; teto sempre.
- **Primeiras tarefas:** aprovar B4-301..304 com o champion; homologar prompt; executar prova negativa.
- **Autonomia:** não
- **Limites e aprovações:** B4-301..304; ativação de cada loop pelo champion.
- **Teto de créditos:** definido no setup (B4-302)
- **Condição de pausa/recuperação:** teto estourado, divergência de dados ou tentativa de escrita → pausa + registro.

## Prova específica

Ciclo controlado: baseline conhecido, rodada do L4.1 com trilha reconstruída passo a passo, prova negativa de escrita no Meta, rodada do L4.2 com e sem baseline, veredito humano e aprendizado.

## Handoff e operação

- **Como demonstrar:** rodar uma rodada do L4.1, reconstruir a trilha, tentar escrita no Meta (bloqueio registrado), rodar sinal do L4.2 com e sem baseline.
- **Como operar:** responsável comercial revisa recomendações; champion mantém cadência/teto/limiar; assistente executa e registra.
- **Como monitorar:** rodadas executadas, custo por execução, pausas, sinais rotulados, tentativas bloqueadas.
- **Pendência conhecida:** B4-301..304 dependem do champion; L4.2 só após L4.1 concluído.

## Tasks vinculadas

| ID                                   | Task                                                                                            | Dono          | SPEC  | Critério         | Recorte da prova                          | Evidência esperada | Pré-condições                        | Status                            |
| ------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------- | ----- | ---------------- | ----------------------------------------- | ------------------ | ------------------------------------ | --------------------------------- |
| 1a38ea22                             | Configurar uma análise que sugira aprendizados sobre campanhas sem alterar orçamento ou público | Cliente       | 4-003 | CA-4-301/302/305 | GREEN análise com trilha + prova negativa | registros + logs   | B4-301/302/303 aprovados             | BLOQUEADA — aguarda B4-301..303   |
| 82524cff                             | Revisar dez recomendações de campanha e registrar quais serão usadas                            | Felipe Navaar | 4-003 | CA-4-304         | revisão registrada com autor e data       | registros          | 1a38ea22 concluída                   | AGUARDANDO L4.1                   |
| afe03044-121e-4c89-8990-c236f83396ec | Monitorar queda de qualidade por origem com baseline                                            | Cliente       | 4-003 | CA-4-303         | sinal com/sem baseline rotulado           | registros          | 1a38ea22 concluída + B4-304 aprovado | BLOQUEADA — aguarda L4.1 + B4-304 |
