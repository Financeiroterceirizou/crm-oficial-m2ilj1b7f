# Changelog — Projeto Terceirizou Terceirização Empresarial

> Registro de tudo que acontece no projeto, em ordem cronológica inversa.

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
