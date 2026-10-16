# STATUS — Projeto Terceirizou Terceirização Empresarial

> **Atualizado em:** 2026-10-06 · **Fonte técnica:** Skip projectId 51268

## Onde estamos

- **Fase 1:** concluída — 10/10 tasks.
- **Fase 2:** concluída — 5/5 tasks.
- **Fase 3:** concluída — 7/7 tasks, aceite final do champion em 2026-09-16.
- **Fase 4:** em andamento — **4/8 tasks concluídas** (`e4c77e80`, `cd704a1c`, `b7c2faea`, `5ef4b7cd`); `5ef4b7cd` concluída em 16/10/2026 com teste humano aprovado pelo champion; prazo 30/09/2026 vencido — reprogramação pendente de decisão do champion.
- **Task `cd704a1c`:** concluída após QA técnico, correção de regressão, verificação no preview e aceite humano do champion em 22/09/2026 — "Aparece o formulário".
- **Skip:** CRM Oficial; correção funcional e fechamento documental aprovados com QA 5/5.
- **Preview:** https://crm-oficial-65bb8--preview.goskip.app
- **Produção:** https://crm-oficial-65bb8.goskip.app — publicada em 23/09/2026, ref `c53c171` (v0.0.100); URL oficial respondendo e painel de qualidade visível.
- **GitHub:** o frontend aceito permanece no Skip; o repositório ainda não está integralmente alinhado ao frontend novo. Resolver Skip → GitHub antes de iniciar a próxima task.

## Resultado da Fase 4 até aqui

- `e4c77e80`: conta Meta confirmada e credencial mantida no secret manager, fora do Git.
- `cd704a1c`: espelho Meta de leitura implementado sem escrita no Meta.
- Prova técnica: 76 anúncios, 12 conjuntos e 6 campanhas lidos; espelhamento idempotente validado.
- Dados no CRM: 50 leads Meta avaliados, 44 espelhados, 6 sem dado Meta e 0 divergentes.
- Interface nova: seção `Leads reais — espelho Meta` lê a collection real `leads` via PocketBase e exibe campanha, anúncio, status, busca, filtros e proveniência; seção `Leads e agendamento` recupera lista real, detalhe e formulário de reunião autenticado.
- Ausência preservada como `sem dado Meta`; dados originais do lead não são sobrescritos.
- Teste humano do champion: espelho Meta aprovado no preview — “testei no preview e funcionou”; correção de acesso a leads/agendamento aprovada — “Aparece o formulário”.

## Inventário Fase 4

- `pocketbase/migrations/0012_add_meta_espelho_fields.js`
- `pocketbase/hooks/meta_espelho.js`
- `src/components/dashboard/MetaLeadsRealCard.tsx`
- `src/components/dashboard/LeadQualityCard.tsx`
- `src/pages/Index.tsx`
- `04-fase-atual/specs/spec-4-001-conector-meta-leitura.md`
- `04-fase-atual/specs/spec-4-002-qualidade-origem-reativacao.md`

## `b7c2faea` — concluída

- **Entrega:** `LeadQualityCard` lê a collection real `leads` e compara origem/campanha nos últimos 28 dias.
- **Métrica aprovada B4-203:** qualificado = prestador de serviço + CNPJ; qualidade = qualificados ÷ recebidos × 100; conversão fora desta task.
- **Proveniência:** mostra CRM, campanha declarada ou CRM + espelho Meta, além do período e das limitações.
- **Regra de segurança:** campo ausente/incompleto aparece como `Sem dado`; não é convertido em zero.
- **Evidência real:** preview carregado, atualização manual exercitada e champion confirmou "funcionou" em 23/09/2026.
- **Limitação observada:** no snapshot real do preview havia 41 leads no período e nenhum CNPJ nas respostas disponíveis; por isso qualidade/qualificados aparecem como `Sem dado`, enquanto recebidos e agendados seguem visíveis.
- **QA:** Skip v0.0.100 / `c53c171`; setup, análise estática, build, integrações e testes passaram.
- **Produção:** publicada em `https://crm-oficial-65bb8.goskip.app`; validação visual confirmou o painel e o período de 28 dias.

## `5ef4b7cd` — concluída (16/10/2026)

- **B4-201 fechado pelo champion em 06/10/2026:** basta ter motivo de perda explícito, sem lista adicional de motivos permitidos; o lead deve ser prestador de serviço com CNPJ, ter sido captado há pelo menos 90 dias e estar sem interação há pelo menos 60 dias. Descadastro/`nao_contatar` e bounce permanente ficam excluídos.
- **B4-202 fechado em 16/10/2026:** registro documental da base legal validado (`06_notas/registro-base-legal-b4-202.md` v1.1 — legítimo interesse, art. 7º IX c/c art. 10 LGPD). Decisões: "não tenho interesse agora" = objeção; WhatsApp com mensagem padrão do SDR; validação por lead por qualquer usuário.
- **Implementação (16/10/2026):** migration 0013 (contrato de reativação + collection `reativacao_lote`), 0014/0015 (fixture de QA com backdate SQL), rota GET `/backend/v1/fila-reativacao` (8 condições da base legal v1.1 + B4-201), rota POST `/backend/v1/reativacao/aprovar` (aprovação humana idempotente, nenhum contato disparado), tela `/reativacao`.
- **Verificação automática:** 401 sem token (RN-4-205); 400 sem lote_id; 201 aprovação (1 incluído/130 excluídos); 200 idempotência HTTP; 201 novo lote com 0 incluídos (idempotência de lote); QA Skip 5/5 (v0.0.115/c4a51cd).
- **Achado de baseline:** 0 de 130 leads com CNPJ nas respostas — a fila nasce vazia até o CNPJ entrar na captura (pendência do prompt 5); fixture de QA prova o caminho elegível.
- **Estado:** CONCLUÍDA — teste humano aprovado pelo champion ("sim funcionou", 13:09 de 16/10). Revalidação independente do zero: 9 provas PASSOU. Limpeza pós-teste: fixture de QA e 5 lotes de teste removidos; collection `reativacao_lote` vazia e pronta para uso real.

## Próximo passo

Fase 4 em 4/8. Próxima task candidata: SPEC-4-003 (loops L4.1/L4.2 — monitor de qualidade por origem e baseline) — SPEC ainda inexistente, precisa ser escrita antes da análise. Pendências abertas que não bloqueiam o uso da fila: frequência máxima de reabordagem, revisão jurídica formal, política de retenção e CNPJ na captura (prompt 5). Estado do projeto: sem_task — próxima task exige novo pedido do champion.
