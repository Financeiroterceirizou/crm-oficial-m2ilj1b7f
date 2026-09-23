# STATUS — Projeto Terceirizou Terceirização Empresarial

> **Atualizado em:** 2026-09-22 20:56 · **Fonte técnica:** Skip projectId 51268

## Onde estamos

- **Fase 1:** concluída — 10/10 tasks.
- **Fase 2:** concluída — 5/5 tasks.
- **Fase 3:** concluída — 7/7 tasks, aceite final do champion em 2026-09-16.
- **Fase 4:** em andamento — **2/8 tasks concluídas** (`e4c77e80`, `cd704a1c`); a correção de regressão foi concluída dentro da `cd704a1c`; prazo 30/09/2026.
- **Task `cd704a1c`:** concluída após QA técnico, correção de regressão, verificação no preview e aceite humano do champion em 22/09/2026 — "Aparece o formulário".
- **Skip:** CRM Oficial; correção funcional e fechamento documental aprovados com QA 5/5.
- **Preview:** https://crm-oficial-65bb8--preview.goskip.app
- **Produção:** https://crm-oficial-65bb8.goskip.app (não atualizada neste ciclo; aceite realizado no preview)
- **GitHub:** o frontend aceito permanece no Skip; o repositório ainda não está integralmente alinhado ao frontend novo. Resolver Skip → GitHub antes de iniciar `b7c2faea`.

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
- `src/pages/Index.tsx`
- `04-fase-atual/specs/spec-4-001-conector-meta-leitura.md`

## Bloqueio atual — `b7c2faea`

- **B4-203 aberto:** a SPEC-4-002 exige aprovação do champion para definição de qualificação, janela e fórmula da métrica de qualidade. Não vou inventar a fórmula.
- **Fonte documental:** a SPEC canônica existe no GitHub em `04-fase-atual/specs/spec-4-002-qualidade-origem-reativacao.md`, mas não está no working tree do Skip, que é a fonte técnica do frontend aceito.
- **Lacuna de dados:** o schema atual tem origem, campanha, qualificação e agendamento, mas não tem campo/collection de conversão. O painel não pode tratar conversão ausente como zero.
- **Estado:** nenhum código da `b7c2faea` foi alterado.

## Próximo passo

Resolver B4-203 e sincronizar a SPEC no Skip; depois disso, a implementação pode começar com nova confirmação do champion.
