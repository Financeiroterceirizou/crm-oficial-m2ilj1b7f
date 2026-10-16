# AP-2026-10-16-1315 — Quirk JSVM: campo JSON chega como bytes e corrompe leitura por chave

- Status: candidato
- Escopo: projeto do cliente
- Task/SPEC: 5ef4b7cd / SPEC-4-002
- Sinal: hooks JS do PocketBase no runtime do Skip recebem campos JSON às vezes como array de bytes (Uint8Array), não como string/objeto; JSON.stringify nesse valor produz índices numéricos e a busca por chave ("cnpj") falha silenciosamente, sem erro aparente.
- Evidência: rota GET /backend/v1/fila-reativacao retornava cnpj_presente=nao para registro com respostas.cnpj preenchido (verificação 16/10 ~12:00); corrigido copiando o padrão de leitura byte a byte de qualificar_lead_create.js; após o fix a mesma rota retornou a fixture como elegível (prova E4 PASSOU).
- Regra reutilizável: ao ler campo JSON em hook do PocketBase, aplicar sempre o normalizador de bytes (typeof raw === 'object' && typeof raw.length === 'number' && typeof raw[0] === 'number' → converter com String.fromCharCode) antes de JSON.parse.
- Quando aplicar: qualquer hook/rota que leia campos JSON (respostas, historico, score_componentes, reativacao_registro) no runtime JSVM do Skip.
- Quando não aplicar: código que já usa o normalizador (qualificar_lead_create.js, qualificar_lead_update.js, fila_reativacao.js, reativacao_aprovar.js) e leituras via API REST (fora do JSVM).
- Confiança: alta — comportamento reproduzido e corrigido com prova A/B na mesma rota.
- Privacidade: sem segredo, dado pessoal ou conteúdo bruto
