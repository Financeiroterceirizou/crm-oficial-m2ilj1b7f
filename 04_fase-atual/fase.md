# Fase 4 — Tarefas

<!-- fase-format:2 -->

Cada linha é uma tarefa da Jornada de Execução. **Tudo que cabe num card cabe nesta linha** — se um campo não estiver aqui, ele não tem como ser preenchido, porque é este arquivo que cria a tarefa.

```
- [ ] Título da tarefa @responsável !30/09/2026 #projeto [interno]   <!-- id:… -->
      > descrição da tarefa, uma ou mais linhas
  - [ ] subtarefa (basta indentar 2 espaços)                         <!-- id:… -->
    - [ ] sub-subtarefa (indente mais 2)                             <!-- id:… -->
```

| marcador                      | o que define                                                   | se você não escrever     |
| ----------------------------- | -------------------------------------------------------------- | ------------------------ |
| `- [ ]` / `- [/]` / `- [x]`   | a fazer / em andamento / concluída                             | a fazer                  |
| `@nome`                       | responsável (`@"Nome Composto"` com aspas)                     | fica **sem responsável** |
| `!dd/mm/aaaa`                 | prazo                                                          | fica **sem prazo**       |
| `#projeto` / `#aculturamento` | tipo                                                           | Projeto de IA            |
| `[interno]`                   | o cliente **não vê** esta tarefa                               | o cliente vê             |
| `> texto` na linha de baixo   | descrição (aparece ao abrir o card)                            | sem descrição            |
| indentar 2 espaços            | vira subtarefa da tarefa acima (vale em qualquer profundidade) | tarefa de topo           |

Os marcadores só valem **no fim da linha** — `Revisar #3 do contrato` continua sendo um título.
Um título que TERMINA na forma de um marcador sai escapado com `\\@joao`; a barra é só para o parser e nunca aparece no card. Você não precisa escrever isso à mão.
Marque `[x]` para concluir e adicione linhas novas à vontade: elas entram no quadro na próxima sincronização e voltam aqui com o `<!-- id:… -->` preenchido. **Não apague o marcador de id** das tarefas que já têm um.

- [x] Confirmar com o Cliente o acesso de leitura à conta do Meta e anexar a resposta @Izabel !22/09/2026 #aculturamento [interno] <!-- id:e4c77e80-e32f-4479-8f42-709d520aa28b -->
  > SPEC-4-001 · B4-101 · Solicitar a confirmação de conta, permissões e campos disponíveis. Se não houver acesso, registrar a decisão de usar uma exportação manual como alternativa. Pré-condição da prova técnica do conector.
- [x] Trazer para o CRM a origem, a campanha e o anúncio de cada lead @Cliente !24/09/2026 [interno] <!-- id:cd704a1c-72c3-48e2-85b3-369d9d25175d -->
  > SPEC-4-001 · CA-4-101/102/103/104 · B4-102/103/104 · Prova técnica timeboxed do Meta (RED: zero ingestão sem prova aprovada) e espelhamento com proveniência (fonte, período, data de carga). Lead sem correspondência exibe "sem dado Meta", nunca zero. Credencial somente em secret manager, fora de Git/log/tela. Se a prova falhar, registrar lacuna e usar exportação manual aprovada (fallback da SPEC-4-001). Demonstra leads com origem preenchida e informação ausente claramente identificada.
- [x] Criar uma tela que compare quantidade e qualidade de leads por campanha @Cliente !25/09/2026 [interno] <!-- id:b7c2faea-89da-40ea-a6cf-969a1cc557a9 -->
  > SPEC-4-002 · CA-4-201 · Exibir campanha/origem, período, leads recebidos, qualificados, agendados e convertidos. A tela mostra fonte, período e ausência como "Sem dado"; B4-203 aprovado em 23/09/2026. Aceite humano do champion no preview em 23/09/2026: "funcionou".
- [x] Criar uma lista de leads antigos que podem receber uma nova abordagem @Cliente !28/09/2026 [interno] <!-- id:5ef4b7cd-7240-4480-a420-c9dcfb2f2944 --> ✅ 2026-10-16
  > SPEC-4-002 · CA-4-202/203 · B4-201/202 · CONCLUÍDA em 16/10/2026: migrations 0013–0015, rotas fila-reativacao + aprovar, tela /reativacao; 9 provas PASSOU na revalidação do zero; teste humano aprovado pelo champion ("sim funcionou" 13:09); fixture de QA e lotes de teste removidos. Fase 4: 4/8.
- [ ] Configurar uma análise que sugira aprendizados sobre campanhas sem alterar orçamento ou público @Cliente !29/09/2026 [interno] <!-- id:1a38ea22-f8ba-4c9c-a7aa-985c9df0aa0a -->
  > SPEC-4-003 · CA-4-301/302/305 · B4-301/302/303 · Loop L4.1 configurado um por vez, com cadência definida (B4-301), prompt homologado, teto e pausa (B4-302/303). A análise gera fato observado, fonte, período, limitação e recomendação, com trilha de auditoria que reconstrói fonte e período (CA-4-305). Não pode publicar anúncio nem modificar campanha — bloqueio demonstrado por prova negativa. B4-301..303 aprovados em 16/10/2026: cadência semanal (segunda, antes da revisão de KPIs); teto 20 créditos; pausa em 3 gatilhos com retomada manual.
- [ ] Revisar dez recomendações de campanha e registrar quais serão usadas @"Felipe Navaar" !30/09/2026 #aculturamento [interno] <!-- id:82524cff-7200-4428-a3cb-ede0586a79f4 -->
  > SPEC-4-003 · CA-4-304 · Conferir com o Cliente se cada recomendação está sustentada pelos dados e registrar aceita, rejeitada ou precisa de mais informação, com autor e data.
- [ ] Exibir qualificação e follow-up na tela do lead @Cliente !25/09/2026 [interno]
  > SPEC-4-002 · CA-4-204/205 · Evolução aceita em 17/09 (painel visual do follow-up): colunas estado/score/motivo/próxima ação e linha do tempo do follow-up na tela do lead, consumindo os eventos da SPEC-3-002. RLS herdado com prova negativa de acesso cruzado.
- [ ] Monitorar queda de qualidade por origem com baseline @Cliente !30/09/2026 [interno] <!-- id:afe03044-121e-4c89-8990-c236f83396ec -->
  > SPEC-4-003 · CA-4-303 · B4-304 · Loop L4.2 configurado após o L4.1 (um loop por vez). Sinaliza queda ou diferença de qualificação por origem somente contra baseline registrado (B4-304); sem baseline, o sinal sai rotulado como hipótese. Não altera regras sozinho. SPEC-4-003 criada em 16/10/2026. B4-304 aprovado em 16/10/2026: queda ≥ 30% contra baseline, mínimo 10 leads da origem em 28 dias.
