# STATUS — Projeto Terceirizou Terceirização Empresarial

> **Atualizado em:** 2026-10-16 · **Fonte técnica:** Skip projectId 51268

## Onde estamos

- **Fase 1:** concluída — 10/10 tasks.
- **Fase 2:** concluída — 5/5 tasks.
- **Fase 3:** concluída — 7/7 tasks, aceite final do champion em 2026-09-16.
- **Fase 4:** em andamento — **4/8 tasks concluídas** (`e4c77e80`, `cd704a1c`, `b7c2faea`, `5ef4b7cd`). `5ef4b7cd` (fila de reativação) concluída em 16/10/2026 com teste humano aprovado pelo champion às 13:09. Próxima task: análise L4.1 (`1a38ea22`), desbloqueada com a criação da SPEC-4-003 e a aprovação dos bloqueios B4-301..304 em 16/10/2026.
- **Skip:** CRM Oficial — versão atual v0.0.126 / `8f8d27a` (QA verde: setup, análise estática, build, integrações).
- **Preview:** https://crm-oficial-65bb8--preview.goskip.app
- **Produção:** https://crm-oficial-65bb8.goskip.app — **publicada em 16/10/2026, ref `8f8d27a` (v0.0.126)**. URL oficial conferida no navegador em 16/10: painel carregando com os cards da F4 (Qualidade de leads por campanha; Leads reais — espelho Meta, 54 total / 44 espelhados / 10 sem dado / 0 divergentes; Leads e agendamento com login e qualificação).
- **GitHub × Skip:** divergência **RESOLVIDA** — `Index.tsx` verificado idêntico nos dois lados em 16/10/2026; o repositório é sincronizado pelo polling do pipeline de leads. Não há pendência de alinhamento.
- **Pastas de fase consolidadas em 16/10/2026:** a pasta antiga `04-fase-atual/` foi arquivada em `04_fase-atual/arquivo-fase-1/` (fase.md e teste-f1-t10.md da F1); as specs ativas vivem em `04_fase-atual/specs/` (SPEC-2-001, SPEC-4-001, SPEC-4-002, SPEC-4-003). A pasta duplicada não existe mais.

## Resultado da Fase 4 até aqui

- `e4c77e80`: conta Meta confirmada e credencial mantida no secret manager, fora do Git.
- `cd704a1c`: espelho Meta de leitura implementado sem escrita no Meta.
- Prova técnica: 76 anúncios, 12 conjuntos e 6 campanhas lidos; espelhamento idempotente validado.
- Dados no CRM: 50 leads Meta avaliados, 44 espelhados, 6 sem dado Meta e 0 divergentes.
- Interface nova: seção `Leads reais — espelho Meta` lê a collection real `leads` via PocketBase e exibe campanha, anúncio, status, busca, filtros e proveniência; seção `Leads e agendamento` recupera lista real, detalhe e formulário de reunião autenticado.
- Ausência preservada como `sem dado Meta`; dados originais do lead não são sobrescritos.
- Teste humano do champion: espelho Meta aprovado no preview — "testei no preview e funcionou"; correção de acesso a leads/agendamento aprovada — "Aparece o formulário".

## Inventário Fase 4

- `pocketbase/migrations/0012_add_meta_espelho_fields.js`
- `pocketbase/migrations/0013_add_reativacao_fields.js` (+ collection `reativacao_lote`)
- `pocketbase/migrations/0014_seed_fixture_reativacao.js` e `0015_backdate_fixture_reativacao.js` (fixture de QA — removida da base após o teste)
- `pocketbase/migrations/0016_add_leads_reativacao_indexes.js` (índices `idx_leads_estado_fila` e `idx_leads_ultima_interacao`)
- `pocketbase/hooks/meta_espelho.js`, `meta_prova.js`, `fila_reativacao.js`, `reativacao_aprovar.js`
- `src/components/dashboard/MetaLeadsRealCard.tsx`
- `src/components/dashboard/LeadQualityCard.tsx`
- `src/pages/Index.tsx`
- `src/pages/Reativacao.tsx` (fila de reativação)
- `04_fase-atual/specs/spec-4-001-conector-meta-leitura.md`
- `04_fase-atual/specs/spec-4-002-qualidade-origem-reativacao.md`
- `04_fase-atual/specs/spec-4-003-loops-l41-l42.md`

## `b7c2faea` — concluída

- **Entrega:** `LeadQualityCard` lê a collection real `leads` e compara origem/campanha nos últimos 28 dias.
- **Métrica aprovada B4-203:** qualificado = prestador de serviço + CNPJ; qualidade = qualificados ÷ recebidos × 100; conversão fora desta task.
- **Proveniência:** mostra CRM, campanha declarada ou CRM + espelho Meta, além do período e das limitações.
- **Regra de segurança:** campo ausente/incompleto aparece como `Sem dado`; não é convertido em zero.
- **Evidência real:** preview carregado, atualização manual exercitada e champion confirmou "funcionou" em 23/09/2026.
- **Limitação observada:** no snapshot real do preview havia 41 leads no período e nenhum CNPJ nas respostas disponíveis; por isso qualidade/qualificados aparecem como `Sem dado`, enquanto recebidos e agendados seguem visíveis. Pendência de coleta segue no CNPJ (ver Próximo passo).
- **QA:** Skip v0.0.100 / `c53c171`; setup, análise estática, build, integrações e testes passaram.
- **Produção:** publicada em `https://crm-oficial-65bb8.goskip.app`; validação visual confirmou o painel e o período de 28 dias.

## `5ef4b7cd` — concluída (16/10/2026)

- **B4-201 fechado pelo champion em 06/10/2026:** basta ter motivo de perda explícito, sem lista adicional de motivos permitidos; o lead deve ser prestador de serviço com CNPJ, ter sido captado há pelo menos 90 dias e estar sem interação há pelo menos 60 dias. Descadastro/`nao_contatar` e bounce permanente ficam excluídos.
- **B4-202 fechado em 16/10/2026:** registro documental da base legal validado (`06_notas/registro-base-legal-b4-202.md` v1.1 — legítimo interesse, art. 7º IX c/c art. 10 LGPD). Decisões: "não tenho interesse agora" = objeção; WhatsApp com mensagem padrão do SDR; validação por lead por qualquer usuário.
- **Implementação (16/10/2026):** migration 0013 (contrato de reativação + collection `reativacao_lote`), 0014/0015 (fixture de QA com backdate SQL), rota GET `/backend/v1/fila-reativacao` (8 condições da base legal v1.1 + B4-201), rota POST `/backend/v1/reativacao/aprovar` (aprovação humana idempotente, nenhum contato disparado), tela `/reativacao`.
- **Verificação automática:** 401 sem token (RN-4-205); 400 sem lote_id; 201 aprovação (1 incluído/130 excluídos); 200 idempotência HTTP; 201 novo lote com 0 incluídos (idempotência de lote); QA Skip 5/5 (v0.0.115/c4a51cd).
- **Achado de baseline:** 0 de 130 leads com CNPJ nas respostas — a fila nasce vazia até o CNPJ entrar na captura. Plano CNPJ partes 1 e 2 executado em 16/10: pipeline da Cora grava o documento em `respostas.cnpj_cpf` e 34/39 leads cora existentes foram retroalimentados (33 CPF + 1 CNPJ; 5 sem match). Meta Ads segue sem CNPJ na origem — coleta via SDR/formulário opcional pendente de decisão do champion.
- **Estado:** CONCLUÍDA — teste humano aprovado pelo champion ("sim funcionou", 13:09 de 16/10). Revalidação independente do zero: 9 provas PASSOU. Limpeza pós-teste: fixture de QA e 5 lotes de teste removidos; collection `reativacao_lote` vazia e pronta para uso real. Primeiro lead real entra na fila em 18/11/2026 (90 dias captação + 60 sem interação).

## Próximo passo

Fase 4 em 4/8. Próxima task: **análise da L4.1 (`1a38ea22`)** — SPEC-4-003 criada em 16/10 (`04_fase-atual/specs/spec-4-003-loops-l41-l42.md`) e bloqueios B4-301..304 aprovados pelo champion no mesmo dia (cadência semanal na segunda; teto 20 créditos/execução; pausa automática em 3 gatilhos; queda relevante = ≥30% com n≥10 em 28 dias). A task de revisão das 10 recomendações (`82524cff`, dono Felipe Navaar) e o monitor L4.2 (`afe03044`) dependem do L4.1 rodando. Proposta de renegociação dos prazos da F4 (todos os prazos de setembro vencidos) entregue ao champion em `artifacts/proposta-cronograma-f4.md` — o fase.md só é alterado após aprovação. Pendências abertas que não bloqueiam o uso da fila: frequência máxima de reabordagem, revisão jurídica formal, política de retenção e CNPJ na captura Meta (decisão champion + Henrique). Estado do projeto: sem_task — próxima task exige novo pedido do champion.
