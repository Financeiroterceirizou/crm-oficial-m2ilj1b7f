# Registro documental — Base legal alternativa para reativação de leads (B4-202)

**Projeto:** CRM Oficial — Terceirizou Terceirização Empresarial Ltda (BPO Financeiro, Florianópolis/SC)
**Data:** 16/10/2026 · **Versão:** 1.1 — **VALIDADA pelo champion em 16/10/2026**
**Trava que este documento resolve:** task `5ef4b7cd` (Fase 4 — fila de reativação), bloqueada pela ausência de registro da base legal alternativa decidida em 06/10/2026.
**Status jurídico:** documento operacional de compliance, não parecer jurídico. Recomenda-se revisão por advogado antes do primeiro lote (ver Pendências, item 2).

---

## 1. Decisões de origem (fatos, não hipóteses)

**06/10/2026** — o champion Vinícius decidiu (registrado no changelog do projeto):

- Consentimento explícito **não é requisito obrigatório** para incluir leads antigos na fila de reativação.
- Uma **base legal alternativa aplicável a cada lead** deve ser documentada e validada antes da inclusão na fila.
- Descadastro e `nao_contatar` ficam **permanentemente fora**.
- **Nenhum contato** parte do sistema sem aprovação humana de lote.

**16/10/2026** — o champion validou este registro respondendo as pendências prioritárias:

1. **"Não tenho interesse agora" conta como objeção** — invalida a base permanentemente.
2. **Canal de reativação: WhatsApp**; a mensagem padrão é **redigida e aprovada pelo SDR**.
3. **A validação da base por lead pode ser feita por qualquer usuário do sistema.**

Onde ainda falta decisão do champion, o item está listado como pendência aberta na seção 8 — nada foi decidido por inferência.

---

## 2. Base legal proposta (a)

### 2.1 Avaliação das alternativas (LGPD, art. 7º)

| Hipótese legal                      | Aplicável?     | Motivo                                                                                                                                                                      |
| ----------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I — Consentimento                   | **Descartada** | Decisão do champion de 06/10. Além disso, pedir consentimento a um lead antigo já é um contato — o requisito criaria paradoxo operacional.                                  |
| II — Obrigação legal                | Não            | Não existe obrigação legal de reativar leads.                                                                                                                               |
| III — Contratos (execução)          | Não            | Lead captado não é contratante; não há contrato em execução com o titular.                                                                                                  |
| IV — Pesquisa por órgão de pesquisa | Não            | Finalidade é comercial, não científica.                                                                                                                                     |
| VII — Proteção da vida              | Não            | Não se aplica.                                                                                                                                                              |
| VIII — Tutela da saúde              | Não            | A reativação é comercial. Atenção ao nicho ILPI: o contexto do lead pode tocar saúde, mas o tratamento em tela (contato comercial com o responsável) não é tutela de saúde. |
| IX — **Legítimo interesse**         | **Aplicável**  | Ver justificativa abaixo.                                                                                                                                                   |
| X — Proteção do crédito             | Não            | A Terceirizou não concede crédito (posicionamento da empresa).                                                                                                              |

### 2.2 Base escolhida: legítimo interesse (art. 7º, IX, c/c art. 10 da LGPD)

O tratamento em tela é o **uso dos dados de contato (nome, e-mail, telefone) de leads próprios para uma nova abordagem comercial** — reativação. Fundamentação:

1. **Interesse legítimo do controlador:** a Terceirizou tem interesse comercial concreto e compatível com o ordenamento jurídico em reaproximar leads que já manifestaram interesse no serviço — é o próprio funil comercial da empresa, com meta trimestral definida (200 reuniões de fechamento).
2. **Lastro em situação concreta:** os leads existem, foram captados em canais próprios (Meta Ads, Cora) e estão registrados no CRM com data e origem.
3. **Finalidade legítima, específica e explícita:** reativação comercial de lead próprio. Nenhuma outra finalidade é amparada por esta base — oferta de crédito, por exemplo, é incompatível com o posicionamento da empresa e invalidaria o registro.
4. **Expectativa do titular (art. 10, caput):** o titular forneceu nome, e-mail e telefone **voluntariamente em formulário de captação** para ser abordado sobre o serviço. É evidente que ele esperava receber comunicação comercial naquele contexto. A reabordagem após janela de inatividade (≥90 dias da captação, ≥60 dias sem interação) segue prática comercial usual de prospecção.
5. **Direito de oposição preservado (art. 10, caput, c/c art. 8º, §1º):** toda comunicação de reativação deve oferecer meio de oposição, e a oposição é permanente — ver seção 6.

**Limites normativos observados:**

- O legítimo interesse **não ampara dados pessoais sensíveis** (Guia Orientativo ANPD, fev/2024). Se o histórico do lead contiver dado sensível (ex.: informação de saúde de residentes de ILPI), esse dado **não pode ser usado** no tratamento de reativação — o contato usa apenas nome, e-mail, telefone e contexto comercial.
- O CNPJ é dado de pessoa jurídica e não é dado pessoal; o dado pessoal tratado é o **contato da pessoa física** que representa o prestador de serviço.

---

## 3. Teste de balanceamento (modelo ANPD, 3 fases)

O Guia Orientativo da ANPD sobre legítimo interesse (publicado em 02/02/2024) recomenda teste em três fases. Resultado aplicado ao caso:

**Fase 1 — Finalidade.** Reativação comercial de leads próprios captados por canais da Terceirizou. Finalidade legítima, específica e explícita, com lastro em situação concreta (funil e meta trimestrais registrados). **Aprovada.**

**Fase 2 — Necessidade.** Reabordar um lead exige usar seus dados de contato — não existe alternativa menos invasiva que atinja a finalidade (reativá-lo sem contato é impossível). Usam-se apenas os dados mínimos: nome, e-mail, telefone. Nenhum outro campo do histórico entra na comunicação. **Aprovada.**

**Fase 3 — Balanceamento e salvaguardas.** Do lado do titular: dados comuns (não sensíveis) fornecidos voluntariamente para ser abordado; expectativa razoável de comunicação comercial; direito de oposição garantido e permanente. Do lado do controlador: interesse comercial legítimo e documentado. Salvaguardas que pesam no balanceamento: aprovação humana de lote obrigatória, nenhum disparo automático, opt-out em toda mensagem de WhatsApp, descadastro permanente, histórico preservado, sem compartilhamento com terceiros. **Conclusão: os direitos e liberdades fundamentais do titular não prevalecem sobre o tratamento quando as salvaguardas estão ativas — a base se sustenta.**

---

## 4. Argumento por cenário de uso (b)

| Cenário                                                                                     | Base aplicável?                         | Argumento                                                                                                                                                     |
| ------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lead Meta Ads captado há ≥90 dias, sem interação há ≥60 dias, sem motivo de perda explícito | **Sim**                                 | Fornecer contato em anúncio de captação cria expectativa evidente de comunicação comercial; reabordagem é prática usual.                                      |
| Lead Cora (indicação/curadoria) nas mesmas janelas                                          | **Sim**                                 | Mesma expectativa — o contato chegou pela Cora para ser apresentado à Terceirizou.                                                                            |
| Lead com motivo de perda explícito (ex.: "fechou com concorrente", "sem verba agora")       | **Sim, com cuidado**                    | Motivo de perda comercial não é objeção ao tratamento. A reabordagem é permitida, mas o motivo deve constar na mensagem para não soar ignorante do histórico. |
| Lead que respondeu "não tenho interesse agora"                                              | **Não — objeção (decidido 16/10/2026)** | O champion definiu que essa resposta conta como objeção: invalida a base permanentemente e exclui o lead da fila.                                             |
| Lead de ILPI (contato é pessoa física responsável pela unidade)                             | **Sim**                                 | Dados comuns; LI aplicável. Se o histórico contém dado sensível (saúde de residentes), esse dado fica fora do tratamento.                                     |
| Lead em `encerrado_entrada_invalida`                                                        | **Não aplicável**                       | Dado de contato inválido — não há como contatar; é limitação técnica, não jurídica. O lead pode reentrar se dados válidos forem obtidos.                      |
| Lead com descadastro / `nao_contatar`                                                       | **Nunca**                               | Exclusão permanente, já decidida pelo champion.                                                                                                               |
| Lead com bounce permanente                                                                  | **Não**                                 | Sem canal válido não há tratamento possível; ver seção 6.                                                                                                     |

---

## 5. Condições de aplicação por lead (c)

Um lead só entra na fila de reativação quando **todas** as condições abaixo são verdadeiras. A checagem é por lead, não por lote, e pode ser feita por **qualquer usuário do sistema** (decisão do champion em 16/10/2026).

1. **Contato fornecido voluntariamente pelo titular** no ato da captação, com origem registrada (`meta_ads`, `cora`, `indicacao`, `manual`).
2. **Prestador de serviço com CNPJ** (critério B4-201 fechado em 06/10).
3. **Captação há pelo menos 90 dias** e **sem interação há pelo menos 60 dias** (critério B4-201).
4. **Sem descadastro e sem `nao_contatar`** — exclusão permanente (decisão de 06/10).
5. **Sem bounce permanente registrado** (migration 0011).
6. **Sem objeção do titular** — incluindo "não tenho interesse agora", que conta como objeção (decisão de 16/10/2026).
7. **Sem dado sensível no tratamento** — a comunicação usa apenas nome, e-mail, telefone e contexto comercial.
8. **Registro de comprovação da base preenchido** (seção 7) — lead sem registro não entra na fila.

---

## 6. O que invalida a base (d)

A base legal do lead é invalidada quando qualquer evento abaixo ocorre. A invalidação é **permanente e irreversível** nos itens 1 e 2.

1. **Objeção do titular (art. 18 da LGPD):** pedido de não receber mais contato, revogação de autorização ou pedido de eliminação dos dados de contato — **incluindo a resposta "não tenho interesse agora", que o champion definiu como objeção em 16/10/2026**. Invalida imediatamente e para sempre. O lead sai da fila com motivo registrado.
2. **Descadastro / `nao_contatar`:** exclusão permanente, já decidida em 06/10. Qualquer meio pelo qual o titular sinalize o descadastro (resposta à mensagem de WhatsApp, canal comercial, terceiro) produz o mesmo efeito do item 1.
3. **Bounce permanente:** o e-mail deixa de ser canal válido. Invalida a aplicação prática da base (não há como contatar) e sinaliza dado desatualizado — o lead só reentra com dado de contato válido obtido legitimamente.
4. **Mudança de finalidade:** usar o contato para finalidade diversa da documentada (ex.: oferta de crédito, parceria, pesquisa) **não é amparado** por este registro — exigiria novo teste de balanceamento e nova base.
5. **Entrada de dado sensível no tratamento:** se a comunicação passar a usar dado sensível, a base cai — legítimo interesse não ampara dado sensível.
6. **Ausência do registro de comprovação:** lead sem o campo da seção 7 preenchido não tem base demonstrável e não entra na fila.

---

## 7. Campo de registro por lead (e)

Cada lead precisa carregar um registro que comprove a base no momento da inclusão na fila. Conteúdo mínimo documental (os nomes técnicos dos campos e a migration são definidos na task de contrato de reativação — aqui se define o que o registro deve conter):

| Componente              | Conteúdo                                                                                         | Exemplo                        |
| ----------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------ |
| **Base aplicada**       | Valor fixo: legítimo interesse                                                                   | `legitimo_interesse`           |
| **Finalidade**          | Valor fixo: reativação comercial de lead próprio                                                 | `reativacao_comercial`         |
| **Versão do documento** | Versão deste registro vigente na avaliação                                                       | `1.1`                          |
| **Data da avaliação**   | Quando a base foi aplicada ao lead                                                               | `2026-10-20`                   |
| **Avaliado por**        | Qualquer usuário do sistema que validou as condições da seção 5 (decisão de 16/10/2026)          | nome do avaliador              |
| **Evidência**           | Referência às condições checadas (janelas de 90/60 dias, ausência de descadastro/bounce/objeção) | lista das 8 condições          |
| **Invalidação**         | Motivo + data quando a base cair (seção 6)                                                       | `objecao_titular · 2026-11-05` |

**Regra de integridade:** o registro é aditivo — a invalidação é registrada, nunca apagada. O histórico completo do lead é preservado (decisão estrutural do projeto: nenhum estado de lead é destruído).

---

## 8. Decisões registradas e pendências

### 8.1 Decididas pelo champion em 16/10/2026

1. **"Não tenho interesse agora" = objeção.** Invalida a base permanentemente; o lead fica fora da fila para sempre, com motivo registrado.
2. **Canal e mensagem:** reativação por **WhatsApp**; a mensagem padrão é **redigida e aprovada pelo SDR**. O opt-out deve estar presente na mensagem padrão (art. 10 exige oposição respeitável na prática).
3. **Validação por lead:** pode ser feita por **qualquer usuário do sistema** — não exige o champion nem cargo específico.
4. **Validação deste documento:** feita pelo champion em 16/10/2026, respondendo os itens acima (registrada no changelog do projeto).

### 8.2 Pendências abertas (não bloqueiam o primeiro lote; precisam de decisão antes do segundo lote / política de retenção)

1. **Frequência máxima de reabordagem por lead:** quantas vezes um lead pode reentrar em lotes (ex.: 1 tentativa por lote, máximo 2 por semestre). Sem limite definido, a prática comercial usual que sustenta o art. 10 se desgasta.
2. **Validação jurídica formal:** este documento é operacional. Recomenda-se revisão por advogado antes do primeiro lote (custo e prazo a decidir).
3. **Política de retenção:** por quanto tempo um lead sem conversão permanece na base após tentativas esgotadas. A LGPD exige eliminação quando os dados deixam de ser necessários à finalidade.

---

## 9. Referências

- **LGPD (Lei 13.709/2018), art. 7º, IX** — hipótese do legítimo interesse; **art. 10, caput e parágrafo único** — condições específicas do legítimo interesse em comunicações (expectativa do titular, práticas comerciais usuais, direito de oposição); **art. 18** — direitos do titular, incluindo oposição e eliminação.
- **ANPD, Guia Orientativo das Hipóteses Legais de Tratamento de Dados Pessoais — Legítimo Interesse** (publicado 02/02/2024, atualizado 23/01/2025): teste de balanceamento em 3 fases (finalidade, necessidade, balanceamento e salvaguardas); legítimo interesse não ampara dados sensíveis; legítima expectativa do titular deve ser demonstrável. Fonte: gov.br/anpd — guia_legitimo_interesse.pdf.
- **Decisões do champion registradas no changelog do projeto:** 06/10/2026 (B4-201 e B4-202) e 16/10/2026 (validação deste registro).

---

_Próximo passo documental: SPEC-4-002 realinhada a este registro em 16/10/2026 (RN-4-202 e CA-4-202). Task `5ef4b7cd` desbloqueada — aguarda nova análise e autorização de implementação._
