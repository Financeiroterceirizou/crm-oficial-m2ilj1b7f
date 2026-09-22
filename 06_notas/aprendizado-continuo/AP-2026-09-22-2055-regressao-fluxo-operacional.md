# AP-2026-09-22-2055 — Preservar fluxos operacionais ao trocar a interface

- Status: candidato
- Escopo: projeto do cliente
- Task/SPEC: `cd704a1c` / `04-fase-atual/specs/spec-4-001-conector-meta-leitura.md`; dependência operacional F3-T02
- Sinal: a tela nova validou o espelho Meta, mas removeu a lista de leads, o detalhe e o acesso ao agendamento que existiam na tela anterior.
- Evidência: produção antiga com 126 leads e botões `Abrir`; preview novo inicialmente sem lista/detalhe; após `LeadScheduleCard`, preview com lista real, login, detalhe e formulário de agendamento.
- Regra reutilizável: toda troca de interface deve ter uma matriz de regressão dos fluxos operacionais existentes; adicionar uma nova seção de dados não pode remover ações críticas já aceitas.
- Quando aplicar: em qualquer redesign de tela que já tenha fluxos de operação, especialmente agendamento, aprovação, replay ou contato.
- Quando não aplicar: protótipos isolados sem fluxo operacional anterior.
- Confiança: alta — regressão reproduzida em dois ambientes, causa confirmada e correção verificada no preview.
- Privacidade: sem segredo, credencial, PII ou payload bruto.
