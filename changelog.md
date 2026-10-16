# Changelog — Projeto Terceirizou Terceirização Empresarial

> Registro de tudo que acontece no projeto, em ordem cronológica inversa.

- 2026-10-16 · [Adapta/Ethos] · Plano CNPJ — partes 1 e 2 executadas (autorização explícita do champion): (1) pipeline da Cora agora grava o documento fornecido voluntariamente em `respostas.cnpj_cpf` (chave que os leads cora antigos já usavam; nunca sobrescreve; teste unitário PASSOU) — vale para os crons 91e0856 e a5b0, que compartilham o processar.py; (2) retroalimentação one-off dos leads cora existentes: 34/39 atualizados (33 CPF + 1 CNPJ, extraídos programaticamente da planilha canônica, match por email/telefone, PATCH só em campo vazio, log em log_acoes.jsonl), 5 sem match na origem ficam "Sem dado". Verificação pós-retro: 33 CPF + 1 CNPJ + 5 vazios, 0 malformados. Meta Ads segue sem CNPJ na origem (formulário não pergunta) — coleta via SDR/formulário opcional pendente de decisão do champion.
- 2026-10-16 · [Adapta/Ethos] · Migration 0016 aplicada (autorização explícita do champion): índices `idx_leads_estado_fila` e `idx_leads_ultima_interacao` em leads — item (d) do contrato de reativação que ficou de fora da 0013. Verificado ao vivo na collection (QA v0.0.121, 5/5); RLS da Fase 1 intacta.
- 2026-10-16 · [champion] · Bloqueios B4-301..304 da SPEC-4-003 aprovados: cadência do L4.1 semanal (toda segunda, antes da revisão de KPIs); teto de 20 créditos por execução; pausa automática em 3 gatilhos (teto estourado, divergência CRM × espelho Meta, tentativa de escrita no Meta) com retomada manual; "queda relevante" = queda ≥ 30% na taxa de qualificação da origem contra baseline com mínimo de 10 leads da origem em 28 dias. Task L4.1 (1a38ea22) desbloqueada.
- 2026-10-16 · [champion] · Task `5ef4b7cd` concluída: fila de reativação aprovada pelo champion após teste humano na tela /reativacao ("sim funcionou", 13:09). Verificação independente do zero: 9 provas PASSOU (401 sem token nas 2 rotas, 400 sem lote_id, fila 200 com fixture elegível, aprovação 201, idempotência HTTP 200, idempotência de lote 201 com 0 incluídos, lote persistido em reativacao_lote, preview renderizando). Limpeza pós-teste: fixture de QA (dedup_key fixture-reativacao-qa-20261016) e 5 lotes de teste removidos — collection reativacao_lote vazia e pronta para uso real. Fase 4: 4/8.
- 2026-10-16 · [Adapta/Ethos] · F4 `5ef4b7cd` IMPLEMENTADA: fila de reativação assistida. Migration 0013 (contrato de reativação no lead: motivo_perda, ultima_interacao, estado_fila, motivo_exclusao, reativacao_registro + collection reativacao_lote), 0014/0015 (fixture de QA com backdate SQL), rota GET /backend/v1/fila-reativacao (8 condições da base legal v1.1 + B4-201), rota POST /backend/v1/reativacao/aprovar (aprovação humana de lote, idempotente por lote_id, nenhum contato disparado), tela /reativacao (login, 3 contadores, tabela de elegíveis com base legal, aprovação de lote, excluídos/não elegíveis em detalhe). Verificação automática: 401 sem token (RN-4-205), 400 sem lote_id, 201 aprovação (1 incluído/130 excluídos), 200 idempotência HTTP, 201 novo lote com 0 incluídos (idempotência de lote), fila final com fixture elegível. Quirk documentado: campo JSON chega como array de bytes no JSVM (padrão de leitura copiado de qualificar_lead_create.js). Aguardando teste humano.
- 2026-10-16 · [Vinícius/Champion] · B4-202 F4 `5ef4b7cd` VALIDADO: registro documental da base legal alternativa concluído e validado pelo champion (`06_notas/registro-base-legal-b4-202.md` v1.1). Base: legítimo interesse (art. 7º, IX c/c art. 10 da LGPD), teste de balanceamento ANPD 3 fases aprovado. Decisões do champion: "não tenho interesse agora" = objeção (exclusão permanente); canal WhatsApp, mensagem padrão redigida e aprovada pelo SDR; validação da base por lead pode ser feita por qualquer usuário do sistema. Pendências abertas não bloqueiam o 1º lote: frequência máxima de reabordagem, revisão jurídica formal, política de retenção.
- 2026-10-16 · [Adapta/Ethos] · SPEC-4-002 realinhada à decisão de 06/10 e ao registro validado de 16/10: RN-4-202 e CA-4-202 atualizadas (consentimento → base legal + objeção), fixtures e caminhos de erro ajustados, task `5ef4b7cd` desbloqueada. Nenhum código alterado.
- 2026-10-16 · [Adapta/Ethos] · Auditoria de lacunas da Fase 4 entregue ao champion: SPEC-4-003 inexistente, 2 tasks sem UUID, contrato de reativação ausente no schema, CNPJ ausente nas respostas (41/41), produção atrás do HEAD, pastas de fase duplicadas, STATUS.md desatualizado. Prompts autocontidos gerados para cada item.
- 2026-10-06 · [Vinícius/Champion] · B4-201 F4 `5ef4b7cd` fechado: basta ter motivo de perda explícito, sem lista adicional de motivos permitidos; prestador de serviço com CNPJ; captação há pelo menos 90 dias; sem interação há pelo menos 60 dias. Descadastro/`nao_contatar`/bounce permanente continuam fora. Nenhum código alterado.
- 2026-10-06 · [Vinícius/Champion] · Decisão B4-202 F4 `5ef4b7cd`: consentimento explícito não será requisito obrigatório; uma base legal alternativa aplicável a cada lead deve ser documentada e validada antes da inclusão na fila. Descadastro/`nao_contatar` seguem excluídos e nenhum contato sai sem aprovação humana. A SPEC-4-002 ainda traz a regra anterior; a task permanece bloqueada até o consultor alinhar a SPEC e concluir a validação. Nenhum código alterado.

- 2026-09-23 · [Adapta/Ethos] · DÚVIDA/BLOQUEIO F4 `5ef4b7cd`: B4-201 sem motivos/janela/exclusões; B4-202 sem consentimento/base legal estruturados; CRM sem contrato de lote/aprovação. Nenhum código alterado.

- 2026-09-23 · [Adapta/Ethos] · Produção publicada: `https://crm-oficial-65bb8.goskip.app`, ref `c53c171` / v0.0.100; QA 5/5 e painel de qualidade visível na URL oficial.
- 2026-09-23 · [Vinicius/Champion] · Task `b7c2faea` concluída: "funcionou" no preview; painel de qualidade por campanha aprovado após QA 5/5 e validação do critério B4-203.
- 2026-09-23 · [Adapta/Ethos] · Task `b7c2faea` fechada: 3/8 da Fase 4; Skip v0.0.98 / `84e9323`; recebidos, qualificação, qualidade, agendados, fonte e ausência sem falso zero verificados.

- 2026-09-23 · [Adapta/Ethos] · F4 `b7c2faea` IMPLEMENTADA: painel real de qualidade por origem/campanha nos últimos 28 dias; B4-203 aplicado (prestador de serviço + CNPJ; qualificados ÷ recebidos × 100); conversão fora da task; campo ausente/incompleto exibido como "Sem dado".
- 2026-09-23 · [Adapta/Ethos] · F4 `b7c2faea` QA PASSOU no Skip v0.0.96 / `ea7a91c`: setup, análise estática, build, integrações e testes; preview carregado e atualização manual exercitada. Observação real: 41 leads no período e nenhum CNPJ disponível nas respostas, então qualidade permanece "Sem dado" sem falso zero. Aguardando teste humano.
- 2026-09-23 · [Adapta/Ethos] · DÚVIDA/BLOQUEIO F4 `b7c2faea`: B4-203 ainda não define métrica, janela e fórmula de qualidade; SPEC-4-002 está no GitHub, mas ausente no working tree do Skip; schema não possui fonte de conversão. Nenhum código alterado.

- 2026-09-22 · [Vinicius/Champion] · F4 `cd704a1c` TESTE HUMANO DA CORREÇÃO APROVADO: "Aparece o formulário"; confirmou acesso à lista, abertura de lead qualificado e exibição do formulário de agendamento no preview; nenhum evento real enviado.
- 2026-09-22 · [Adapta/Ethos] · F4 `cd704a1c` CORREÇÃO CONCLUÍDA: restaurada a lista real de leads, detalhe e formulário de agendamento autenticado na interface nova; espelho Meta preservado; correção funcional e fechamento documental com QA 5/5; produção não publicada.
- 2026-09-22 · [Vinicius/Champion] · F4 `cd704a1c` TESTE HUMANO APROVADO: "testei no preview e funcionou".
- 2026-09-22 · [Adapta/Ethos] · F4 `cd704a1c` CONCLUÍDA: interface nova passou a ler leads reais via PocketBase e exibir campanha/anúncio Meta, status e proveniência; 50 leads avaliados, 44 espelhados, 6 sem dado Meta, 0 divergentes; implementação Skip v0.0.79 (`b2e260c`), fechamento documental final v0.0.84 (`0ef865c`), todos QA 5/5; commit de implementação `91f36b3`.
- 2026-09-22 · [Adapta/Ethos] · F4 `cd704a1c` espelho Meta técnico validado: leitura de 76 anúncios, 12 conjuntos e 6 campanhas; idempotência confirmada e zero escrita no Meta.
- 2026-09-17 · [Adapta/Ethos] · F3-T05-CORREÇÃO RESEND implementada no hook `followup_lead.js`: remetente Terceirizou preservado; adicionados `User-Agent`, `Idempotency-Key` estável por lead/cadência/tentativa e tratamento sanitizado de erro de transporte. QA aprovado no Skip v0.0.62 / 7a3d748; aguardando teste humano.

## Registro

- 2026-08-25 · [Vinicius/Champion] · F1-T10 TESTE APROVADO: "Tudo certo.. Pode seguir."
- 2026-08-25 · [Adapta/Ethos] · F1-T10 FECHADA: CA-1-009 a CA-1-012 comprovados; RLS do error_log corrigido pela migration 0005; Fase 1 encerrada com 10/10 tasks.
- 2026-08-25 · [Adapta/Ethos] · QA final Skip aprovado na versão v0.0.26 / 94fe26d.
- 2026-08-25 · [Adapta/Ethos] · F1-T10 corrigida: leitura anônima da fila bloqueada; relatório final registrado.
- 2026-08-25 · [Adapta/Ethos] · Auditoria Skip/GitHub: F1-T10 não possuía evidência; status corrigido para pendente.
- 2026-08-21 · [Vinicius/Champion] · F1-T09 TESTE APROVADO.
- 2026-08-21 · [Adapta/Ethos] · F1-T09 FECHADA: replay manual e fila de recuperação.
- 2026-08-21 · [Vinicius/Champion] · F1-T08 TESTE APROVADO.
- 2026-08-21 · [Adapta/Ethos] · F1-T08 FECHADA: error_log, logging e política de recuperação.
- 2026-08-21 · [Vinicius/Champion] · F1-T07 TESTE APROVADO.
- 2026-08-21 · [Adapta/Ethos] · F1-T07 FECHADA: validação e ausência de falso sucesso.
- 2026-08-21 · [Vinicius/Champion] · F1-T06 TESTE APROVADO.
- 2026-08-20 · [Vinicius/Champion] · F1-T05 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T02 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T04 TESTE APROVADO.
- 2026-08-19 · [Vinicius/Champion] · F1-T01 TESTE APROVADO.
