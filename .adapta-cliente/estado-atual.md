# Estado atual — Adapta Cliente

- task_id: cd704a1c (Fase 4 — espelhar origem/campanha/anúncio no CRM; correção de regressão de agendamento)
- champion: Vinicius (CEO)
- spec: 04-fase-atual/specs/spec-4-001-conector-meta-leitura.md
- etapa: em_correcao
- autorizacao_implementacao: confirmada + 2026-09-22T11:19 — "pode implementar este plano"
- teste_humano: pendente após correção — verificar acesso à lista, abertura de lead qualificado e formulário de agendamento no preview
- verificacao_automatica: pendente — componente `LeadScheduleCard` adicionado; precisa QA Skip e verificação de preview
- aprendizado: capturado:06_notas/aprendizado-continuo/AP-2026-09-22-2002-ui-fonte-real.md
- ultima_acao: regressão corrigida no working tree: interface nova agora renderiza lista real de leads, detalhe e solicitação de agendamento autenticada; espelho Meta preservado
- proxima_acao: rodar QA Skip e verificar preview sem disparar evento real no Calendar
- atualizado_em: 2026-09-22T20:50:00-03:00
