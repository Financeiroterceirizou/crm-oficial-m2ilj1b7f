# Debug Summary — Regressão de acesso a leads/agendamento

- Task: `cd704a1c`
- Sintoma: champion não conseguia acessar leads para fazer agendamento na interface nova.
- Reprodução: preview `crm-oficial-65bb8--preview.goskip.app` mostrava dashboard Meta, mas nenhum cabeçalho `Leads`, botão `Abrir`, detalhe ou formulário de agendamento. Produção antiga mostrava os 126 leads e o botão `Abrir`.
- Causa raiz: a correção visual da task substituiu a tela operacional antiga por um dashboard, mas não incorporou o fluxo de lista/detalhe/agendamento da F3-T02. O backend `agendar_lead.js` e as migrations 0007/0008 permanecem presentes.
- Correção: adicionado `LeadScheduleCard`, que lê a collection real `leads`, permite busca, abre detalhe, mostra qualificação e solicita agendamento via `/backend/v1/agendar-lead` após login PocketBase. O espelho Meta foi preservado.
- Verificação: Skip QA 5/5 em v0.0.87 (`f5b8af0`); preview mostrou lista real, login liberado, botão `Abrir` e formulário `Solicitar agendamento` para lead qualificado. Nenhum evento real foi enviado ao Calendar.
