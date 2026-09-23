# AP-2026-09-23-1858 — Não transformar dado incompleto em zero no painel de qualidade

- Status: candidato
- Escopo: projeto do cliente
- Task/SPEC: `b7c2faea` / `04-fase-atual/specs/spec-4-002-qualidade-origem-reativacao.md`
- Sinal: a métrica de qualidade tinha denominador conhecido, mas os leads reais não traziam CNPJ suficiente para avaliar o critério aprovado.
- Evidência: `src/components/dashboard/LeadQualityCard.tsx`; preview aprovado pelo champion; QA Skip v0.0.97 / `bf15fcb`; painel exibiu recebidos e a limitação como `Sem dado`, sem falso zero.
- Regra reutilizável: quando uma métrica depende de campo obrigatório ausente ou incompleto, manter a contagem de entrada, exibir `Sem dado` e explicar a lacuna; nunca inferir zero.
- Quando aplicar: painéis de qualidade, conversão ou elegibilidade com campos opcionais, históricos ou incompletos.
- Quando não aplicar: quando a fonte declarar explicitamente o valor zero e a completude do campo estiver validada.
- Confiança: alta — regra aplicada no código, observada no preview e aprovada no teste humano.
- Privacidade: sem segredo, credencial, dado pessoal ou payload bruto.
