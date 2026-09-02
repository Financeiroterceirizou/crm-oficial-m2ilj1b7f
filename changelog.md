# Changelog — Projeto Terceirizou Terceirização Empregos

> Registro de tudo que acontece no projeto, em ordem cronológica inversa.

## Registro

- 2026-09-01 · [Adapta/Ethos] · FIX automação de captação (F1-T05): token JWT da automação expirado (20/08) causava falha silenciosa de UPDATE no polling (404 em PATCH). Renovado token; processar.py agora renova token automaticamente (auto-refresh com credenciais) e transform.py alinhado ao converter.py (chaves canônicas + descarte da coluna "É prestador de serviços?" da aba Jun). 4 leads pendentes atualizados (Luciana das Neves, Brenda dos passos da cruz, TESTE F1-T04, Vinícius Oliveira) e estado sincronizado.
- 2026-08-25 · [Vinicius/Champion] · F1-T10 TESTE APROVADO: "Tudo certo.. Pode seguir."
- 2026-08-25 · [Adapta/Ethos] · F1-T10 FECHADA: CA-1-009 a CA-1-012 comprovados; RLS do error_log corrigido pela migration 2026; Fase 1 encerrada com 10/10 tasks.
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