# STATUS — Projeto Terceirizou Terceirização Empresarial

> **Atualizado em:** 2026-10-06 · **Fonte técnica:** Skip projectId 51268

## Onde estamos

- **Fase 1:** concluída — 10/10 tasks.
- **Fase 2:** concluída — 5/5 tasks.
- **Fase 3:** concluída — 7/7 tasks, aceite final do champion em 2026-09-16.
- **Fase 4:** em andamento — **3/8 tasks concluídas** (`e4c77e80`, `cd704a1c`, `b7c2faea`); `5ef4b7cd` bloqueada por B4-201 e pela validação/alinhamento da decisão B4-202; prazo 30/09/2026.
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
- **Métrica aprovada B4-203:** qualificado = prestador de serviço + CNPJ; qualidade = qualificados ÷ recebidos × 100; conversão fora da task.
- **Proveniência:** mostra CRM, campanha declarada ou CRM + espelho Meta, além do período e das limitações.
- **Regra de segurança:** campo ausente/incompleto aparece como `Sem dado`; não é convertido em zero.
- **Evidência real:** preview carregado, atualização manual exercitada e champion confirmou "funcionou" em 23/09/2026.
- **Limitação observada:** no snapshot real do preview havia 41 leads no período e nenhum CNPJ nas respostas disponíveis; por isso qualidade/qualificados aparecem como `Sem dado`, enquanto recebidos e agendados seguem visíveis.
- **QA:** Skip v0.0.100 / `c53c171`; setup, análise estática, build, integrações e testes passaram.
- **Produção:** publicada em `https://crm-oficial-65bb8.goskip.app`; validação visual confirmou o painel e o período de 28 dias.

## `5ef4b7cd` — bloqueada por decisão de negócio

- **B4-201 — critério conservador aprovado pelo champion em 06/10/2026:** exigir motivo de perda explícito, lead prestador de serviço com CNPJ, captação há pelo menos 90 dias e pelo menos 60 dias sem interação.
- **Detalhe B4-201 ainda pendente:** confirmar se qualquer motivo de perda explicitamente registrado é elegível ou se haverá uma lista de motivos aceitos. Nenhuma regra foi implementada.
- **B4-202 decidido pelo champion em 06/10/2026:** consentimento explícito não será requisito obrigatório; uma base legal alternativa aplicável ao lead deve ser documentada e validada antes da inclusão na fila.
- **Alinhamento necessário:** a SPEC-4-002 ainda exclui leads sem consentimento. O consultor deve alinhar a SPEC à decisão e validar/documentar a base alternativa antes de retomar a análise.
- **Salvaguardas mantidas:** descadastro/`nao_contatar` excluídos; aprovação humana do lote obrigatória; nenhum contato automático.
- **Lacuna técnica:** a collection `leads` possui `respostas`, `historico`, `followup_parada` e datas, mas não tem contrato estruturado para os critérios nem collection de lote/aprovação.
- **Estado:** nenhum código da `5ef4b7cd` foi alterado.

## Próximo passo

Confirmar se qualquer motivo de perda explícito basta ou se será definida uma lista de motivos elegíveis; obter o alinhamento da SPEC e a validação consultiva de B4-202; depois disso, fazer nova análise/autorização de implementação.
