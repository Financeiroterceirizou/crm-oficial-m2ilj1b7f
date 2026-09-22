# Debug Summary — Regressão de acesso a leads/agendamento

- Task: `cd704a1c`
- Sintoma: champion não conseguia acessar leads para fazer agendamento na interface nova.
- Reprodução: preview `crm-oficial-65bb8--preview.goskip.app` mostrava dashboard Meta, mas nenhum cabeçalho `Leads`, botão `Abrir`, detalhe ou formulário de agendamento. Produção antiga mostrava os 126 leads e o botão `Abrir`.
- Causa raiz: a correção visual da task substituiu a tela operacional antiga por um dashboard, mas não incorporou o fluxo de lista/detalhe/agendamento da F3-T02. O backend `agendar_lead.js` e as migrations 0007/0008 permanecem presentes.
- Correção: adicionado `LeadScheduleCard` com leitura real da collection `leads`, busca, detalhe, qualificação, login PocketBase e solicitação para `/backend/v1/agendar-lead`; adicionado ao `Index.tsx` sem remover o espelho Meta.
- Limite: o teste desta correção deve validar acesso, abertura do lead, bloqueio de não qualificado e formulário; não disparar evento real no Calendar sem horário aprovado.
