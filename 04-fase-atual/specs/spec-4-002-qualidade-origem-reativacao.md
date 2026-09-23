# SPEC-4-002 — Qualidade por origem, reativação assistida e painel do follow-up

**Fase:** 4 — Sistema de inteligência de campanhas e operação assistida
**Status:** planejada
**Dono:** responsável comercial valida qualidade; champion aprova lista de reativação; marketing consulta
**Origem no escopo:** `02-Escopo-Definitivo.md`, Fase 4 (painel de qualidade por origem; classificação de leads históricos para reativação; fila de reativação com preservação de histórico); evolução aceita por Navaar em 17/09/2026: painel visual do follow-up na tela do lead (`06_notas/F3-candidata-frontend-leads.md`).
**Degrau da solução:** consulta e fila assistidas — leitura e organização para decisão humana; nenhum contato parte sem aprovação humana; nenhuma alteração automática de regra.

## Contexto e decisões fechadas

- **Estado atual:** a Fase 2 classifica leads (estado, score, motivo, próxima ação) e a Fase 3 registra follow-up e paradas, mas o painel atual (`src/pages/Index.tsx`) não exibe os campos de qualificação nem o follow-up; leads perdidos não têm fila de reativação; a qualidade por origem só é respondível exportando dados manualmente.
- **Estado desejado:** uma tela compara quantidade e qualidade por origem/campanha; uma fila de reativação organiza leads históricos elegíveis com histórico preservado; a tela do lead mostra qualificação e follow-up para a revisão humana trabalhar; nenhuma ação de contato parte do sistema sem aprovação humana.
- **Decisões fechadas:** Navaar aceitou em 17/09/2026 o painel visual do follow-up como evolução da F4; scheduler da cadência e webhook de bounce foram **rejeitados** nesta onda (registrados como adiados); reativação permanece com aprovação humana obrigatória (escopo: "nenhum contato deve ser enviado antes da aprovação humana").
- **Bloqueios (B4-201..203):** (B4-201) critério de elegibilidade da reativação (motivos de perda, janela de última interação, exclusões) definido pelo champion antes de qualquer contato; (B4-202) consentimento/base legal por lead checados antes de incluir alguém na fila — leads com descadastro (nao_contatar da F3) ficam permanentemente fora; (B4-203) métrica de comparação (definição de "qualificado", janela, fórmula) aprovada pelo champion antes de a tela comparar. **B4-203 foi aprovado pelo champion em 23/09/2026: qualificado = prestador de serviço e CNPJ presentes; janela = últimos 28 dias; qualidade = leads qualificados / leads recebidos × 100; conversão não será usada nesta task.**

## Resultado observável

O responsável comercial abre uma tela que compara origens/campanhas por leads recebidos, qualificados, agendados e convertidos, com fonte e período declarados e vazio ≠ zero. Filtra leads históricos por motivo de perda e última interação, monta uma fila de reativação e a aprova; cada lead da fila preserva o histórico completo e o consentimento. O operador vê, na tela do lead, estado/score/motivo/próxima ação e a linha do tempo do follow-up.

## Limites e dependências

- **Inclui:** consulta de qualidade por origem (com dados Meta quando a SPEC-4-001 estiver ativa; só dados internos caso contrário); classificação de leads históricos para reativação; fila com aprovação humana e preservação de histórico; colunas de qualificação + timeline do follow-up na tela do lead.
- **Fora de escopo:** envio automático de qualquer contato de reativação (mesmo por e-mail); alteração automática de regras de qualificação; métricas de performance de anúncio além da origem; benchmark externo.
- **Entradas:** leads e eventos das fases 1–3; dados Meta espelhados (quando disponíveis); critérios do champion (B4-201/203).
- **Saídas:** painel de qualidade com fonte/período; fila de reativação aprovada; tela do lead com qualificação + follow-up visíveis.
- **Atores/permissões:** marketing consulta e propõe; responsável comercial valida qualidade e aprova fila; champion define critérios; RLS da F1 permanece (papel não vê lead de outro responsável).
- **Risco/plano B:** dado incompleto pode induzir decisão errada → mostrar fonte, amostra, período e limitações; recomendação pode ser retirada; consentimento ausente ou descadastro exclui o lead da fila.
- **Rollback:** desativar fila e painel sem apagar histórico; nenhum estado de lead é destruído pela consulta.

## Dados e integrações

| Origem/destino                    | Fonte de verdade | Campos/contrato                                                             | Autenticação/permissão               | Timeout/retry/idempotência                | Tratamento de erro                                         |
| --------------------------------- | ---------------- | --------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------- | ---------------------------------------------------------- |
| CRM (F1–F3) → painel de qualidade | CRM              | origem, estado, score, motivo, agenda, conversão, período                   | RLS existente; acesso por papel      | leitura pura                              | vazio ≠ zero; fonte/período visíveis                       |
| CRM → fila de reativação          | CRM              | `lead_id`, motivo de perda, última interação, consentimento, estado da fila | aprovação humana registrada por lote | lote idempotente; reprocessar não duplica | lead com descadastro/sem consentimento excluído com motivo |
| CRM → tela do lead                | CRM              | colunas de qualificação + eventos de follow-up                              | RLS (não atribuído não vê PII)       | leitura                                   | sem dado exibe estado explícito                            |

| Regra    | Condição                                               | Ação/resultado                         | Exceção                       |
| -------- | ------------------------------------------------------ | -------------------------------------- | ----------------------------- |
| RN-4-201 | critério de reativação não aprovado (B4-201)           | fila não é gerada                      | pendência visível ao champion |
| RN-4-202 | lead com descadastro/nao_contatar ou sem consentimento | excluído da fila permanentemente       | histórico preservado          |
| RN-4-203 | lote de reativação sem aprovação humana                | nenhum contato, nenhuma tarefa criada  | fila fica aguardando          |
| RN-4-204 | campo de qualidade ausente para a origem               | exibe "sem dado" com fonte/período     | nunca vira zero               |
| RN-4-205 | papel sem permissão sobre o lead                       | não vê dado na tela/fila (RLS herdado) | prova negativa obrigatória    |

## Fluxo e regras

1. Champion aprova critério de reativação e métrica de comparação (B4-201/203).
2. Sistema monta consulta de qualidade por origem com fonte, período e limitações declaradas.
3. Sistema propõe fila de reativação conforme critério; leads com descadastro ficam fora.
4. Responsável comercial revisa e aprova a fila; só então cada lead vira tarefa humana de reabordagem.
5. Tela do lead passa a exibir qualificação + follow-up; operador trabalha revisão humana por ali.

| Cenário   | Dado/condição                                  | Resultado esperado                    | Recuperação |
| --------- | ---------------------------------------------- | ------------------------------------- | ----------- |
| Principal | critério aprovado + leads históricos elegíveis | fila montada e aprovada com histórico | —           |
| Limite    | lead com descadastro na base                   | excluído da fila com motivo           | —           |
| Falha     | origem sem dado de qualidade                   | "sem dado" com fonte/período          | —           |

## Instruções de execução para o Ethos

1. Ler esta SPEC, SPEC-2-001 (estados de qualificação) e SPEC-3-002 (eventos de follow-up/parada).
2. Construir apenas consulta, fila e exibição; nenhum disparo, nenhum envio, nenhuma alteração de regra.
3. Não criar critério de reativação nem fórmula de qualidade por inferência — parar se B4-201/203 estiverem abertos.
4. Respeitar RLS existente em toda tela/fila nova; prova negativa de acesso cruzado é obrigatória.
5. Estado válido ao parar: fila aguardando aprovação humana; nenhuma tarefa de contato criada sem aceite.

## Checklist de execução

- [ ] critério de reativação aprovado pelo champion (B4-201)
- [x] consentimento/descadastro tratados como exclusão permanente (B4-202)
- [x] métrica de qualidade aprovada (B4-203) — aprovação registrada em 23/09/2026
- [ ] prova negativa de RLS nas novas telas
- [x] lote aprovado não gerou contato automático — esta task não cria lote nem contato

## Critérios de aceite

- [x] **CA-4-201:** a tela de qualidade compara origens/campanhas com fonte, período e vazio ≠ zero — validada no preview e aprovada pelo champion em 23/09/2026.
- [ ] **CA-4-202:** fila de reativação só contém leads elegíveis pelo critério aprovado; descadastro/nao_contatar ficam permanentemente fora.
- [ ] **CA-4-203:** nenhum contato/tarefa de reabordagem existe sem aprovação humana registrada no lote.
- [ ] **CA-4-204:** a tela do lead exibe estado, score, motivo, próxima ação e a linha do tempo do follow-up.
- [ ] **CA-4-205:** papel sem atribuição não vê lead de outro responsável nas novas telas/filas (RLS herdado).

## TDD da SPEC

| Etapa              | Prova                                                                                                      | Ação                       | Resultado esperado                                              | Evidência            |
| ------------------ | ---------------------------------------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------------------- | -------------------- |
| RED                | critério de reativação ausente (B4-201)                                                                    | tentar montar fila         | zero fila, pendência visível                                    | estado do sistema    |
| GREEN              | critério aprovado + fixtures sintéticas (elegível, descadastrado, sem consentimento, de outro responsável) | montar fila e abrir telas  | fila correta, exclusões com motivo, qualidade com fonte/período | roteiro + registros  |
| REFACTOR/REGRESSÃO | aprovar lote e tentar contato; acessar lead alheio; origem sem dado                                        | exercitar provas negativas | nenhum contato automático; acesso negado; "sem dado" explícito  | logs + aceite humano |

**Dados/fixtures:** leads sintéticos por estado/motivo/consentimento/atribuição; janela de última interação variada.
**Caminhos de erro obrigatórios:** critério ausente, descadastro, consentimento ausente, acesso cruzado, origem sem dado.
**Evidência exigida:** recibo do critério aprovado, roteiro de provas, registros de fila, aceite humano.

## Configuração no Ethos

- **Tipo:** automação de apoio (consulta + fila assistida)
- **Sistemas das fases 1–3 usados:** F1 (leads, RLS), F2 (qualificação: SPEC-2-001), F3 (eventos de follow-up/parada: SPEC-3-002)
- **Agente responsável:** assistente principal do cliente; veredito sempre humano

### Meta

- **Nome curto:** Qualidade e reativação
- **O que atingir:** decisão de reativação e leitura de qualidade apoiadas em dados com proveniência
- **Prazo do ciclo:** definido na Jornada F4
- **Valor estimado:** [opcional e com fonte]

### Validação

- **Como saber que foi atingido:** painel exibindo qualidade com fonte/período; fila aprovada sem contato automático; tela do lead completa
- **Modo:** assistente mede | humano valida
- **Fonte independente:** registros do CRM × roteiro de provas
- **Baseline / alvo / unidade:** 100% das exibições com fonte/período; 0 contato sem aprovação
- **Cadência:** consulta sob demanda; fila por lote aprovado
- **Responsável pelo veredito:** responsável comercial (fila) e champion (critério)

### Conectores e skills

| Item                             | Tipo     | Uso                                | Permissão/entrada     | Saída               | Plano B           |
| -------------------------------- | -------- | ---------------------------------- | --------------------- | ------------------- | ----------------- |
| Dados internos CRM               | fonte    | qualidade e reativação             | RLS por papel         | painel/fila         | exportação manual |
| Dados Meta (se SPEC-4-001 ativa) | conector | enriquecer comparação por campanha | proveniência da 4-001 | colunas de campanha | só dados internos |

### Arranque

- **Instruções permanentes:** vazio ≠ zero; nenhum contato sem aprovação humana; descadastro é permanente; RLS em toda tela nova.
- **Primeiras tarefas:** aprovar critério (B4-201) e métrica (B4-203) com o champion; montar consulta de qualidade.
- **Autonomia:** não
- **Limites e aprovações:** B4-201..203; veredito de reativação sempre humano.
- **Teto de créditos:** definido no setup
- **Condição de pausa/recuperação:** divergência de dados ou acesso cruzado detectado pausa a fila e abre exceção.

## Prova específica

Ciclo controlado: baseline (leads históricos conhecidos), montagem da fila, aprovação humana, conferência de que nenhum contato partiu do sistema, veredito e aprendizado. Provar falha de acesso cruzado, lead com descadastro e origem sem dado.

## Handoff e operação

- **Como demonstrar:** abrir a tela de qualidade, montar a fila, aprovar um lote e mostrar a tela do lead com qualificação + follow-up.
- **Como operar:** responsável comercial valida qualidade e aprova lotes; marketing consulta; champion revisa critério.
- **Como monitorar:** lotes aguardando aprovação, acessos negados, origens sem dado.
- **Pendência conhecida:** critério de reativação e métrica dependem do champion (B4-201/203); painel do follow-up consome eventos da SPEC-3-002 já em produção.

## Tasks vinculadas

| ID          | Task                                                                    | Dono    | SPEC  | Critério     | Recorte da prova                             | Evidência esperada | Pré-condições                | Status                   |
| ----------- | ----------------------------------------------------------------------- | ------- | ----- | ------------ | -------------------------------------------- | ------------------ | ---------------------------- | ------------------------ |
| b7c2faea    | Criar uma tela que compare quantidade e qualidade de leads por campanha | Cliente | 4-002 | CA-4-201     | GREEN qualidade com fonte/período            | tela + registros   | cd704a1c ou fallback interno | CONCLUÍDA 23/09/2026     |
| 5ef4b7cd    | Criar uma lista de leads antigos que podem receber uma nova abordagem   | Cliente | 4-002 | CA-4-202/203 | RED sem critério + fila aprovada sem contato | fila + aceites     | b7c2faea                     | BLOQUEADA                |
| id pendente | Exibir qualificação e follow-up na tela do lead                         | Cliente | 4-002 | CA-4-204/205 | GREEN tela + prova negativa RLS              | tela + logs        | b7c2faea                     | BLOQUEADA · aguarda UUID |
