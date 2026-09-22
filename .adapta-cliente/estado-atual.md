# Estado atual — Adapta Cliente

- task_id: cd704a1c (Fase 4 — espelhar origem/campanha/anúncio no CRM)
- champion: Vinicius (CEO)
- spec: 04_fase-atual/specs/spec-4-001-conector-meta-leitura.md
- etapa: em_correcao
- autorizacao_implementacao: confirmada + 2026-09-22T11:19 — "pode implementar este plano"
- teste*humano: pendente — interface nova não exibia os campos meta*\*; correção de UI em andamento
- verificacao_automatica: pendente — dashboard novo usava mocks em `src/lib/dashboard-data.ts`; backend tem 44 leads espelhados reais
- aprendizado: pendente
- ultima_acao: causa raiz reproduzida na interface publicada/preview: dashboard GA4 mockado não lia `leads`; escrita seção MetaLeadsRealCard para leitura real do CRM
- proxima_acao: rodar QA Skip e verificar preview com leads reais e proveniência Meta
- atualizado_em: 2026-09-22T12:05:00-03:00
