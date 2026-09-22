# AP-2026-09-22-2002 — Interface deve validar a fonte real do CRM

- Status: candidato
- Escopo: projeto do cliente
- Task/SPEC: `cd704a1c` / `04_fase-atual/specs/spec-4-001-conector-meta-leitura.md`
- Sinal: a nova interface compilava e carregava, mas inicialmente usava dados mockados enquanto o backend já tinha os dados reais do espelho Meta.
- Evidência: `MetaLeadsRealCard.tsx`, Skip v0.0.79 com QA 5/5 e preview validado com 50 leads Meta, 44 espelhados, 6 sem dado Meta e 0 divergentes.
- Regra reutilizável: em qualquer redesenho de interface, o teste de aceite deve conferir a leitura da fonte real, a contagem de registros e pelo menos um conjunto de campos críticos; compilação e aparência não provam integração.
- Quando aplicar: após alterar uma tela que consome dados de uma collection ou conector existente.
- Quando não aplicar: telas explicitamente estáticas ou protótipos declarados como mock, fora de um critério de integração.
- Confiança: alta — causa reproduzida, correção aplicada e preview aprovado pelo champion.
- Privacidade: sem segredo, credencial, PII ou payload bruto.
