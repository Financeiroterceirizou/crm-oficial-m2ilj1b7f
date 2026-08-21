# Contrato de Campos — F1-T004

**Data:** 2026-08-21
**Status:** APROVADO pelo champion

## Fontes de dados

| Fonte    | ID                                             | Abas                       | Colunas    |
| -------- | ---------------------------------------------- | -------------------------- | ---------- |
| Cora     | `1TYe2__HmgLUhqOoudmxm-I2fL94wKSJ8ThmXmbCUXfY` | Principal                  | 14 colunas |
| Meta Ads | `1I5F4-NMzkkaStAyVKrO89Dulfi-1POXZHVPZNLRv02A` | Leads Meta Ads - Jun.26    | 13 colunas |
| Meta Ads | `1I5F4-NMzkkaStAyVKrO89Dulfi-1POXZHVPZNLRv02A` | Leads Anúncios de Cadastro | 15 colunas |

## Mapeamento de campos

### Cora → CRM

| Campo Planilha          | Campo CRM                         | Tipo   | Observação            |
| ----------------------- | --------------------------------- | ------ | --------------------- |
| data_envio              | source_event_id                   | text   | Timestamp do evento   |
| nome                    | nome                              | text   | Nome do lead          |
| cnpj_ou_cpf             | respostas.cnpj_ou_cpf             | json   | Dados adicionais      |
| tipo_empresa            | respostas.tipo_empresa            | json   | Dados adicionais      |
| email                   | email                             | text   | Email primário        |
| telefone                | telefone                          | text   | Telefone fallback     |
| servico_desejado        | respostas.servico_desejado        | json   | Dados adicionais      |
| ramo_atividade          | respostas.ramo_atividade          | json   | Dados adicionais      |
| segmento                | respostas.segmento                | json   | Dados adicionais      |
| estado                  | respostas.estado                  | json   | Dados adicionais      |
| cidade                  | respostas.cidade                  | json   | Dados adicionais      |
| preferencia_atendimento | respostas.preferencia_atendimento | json   | Dados adicionais      |
| status_atendimento      | respostas.status_atendimento      | json   | Dados adicionais      |
| observação/comentários  | respostas.observacao              | json   | Dados adicionais      |
| (fixo)                  | origem                            | select | `cora`                |
| (fixo)                  | estagio                           | select | `capturado`           |
| (auto)                  | lead_id                           | text   | UUID gerado           |
| (auto)                  | opportunity_id                    | text   | UUID gerado           |
| (auto)                  | dedup_key                         | text   | email + telefone      |
| (auto)                  | responsavel                       | text   | Padrão ou round-robin |

### Meta Ads (Jun.26) → CRM

| Campo Planilha                                             | Campo CRM                    | Tipo   | Observação            |
| ---------------------------------------------------------- | ---------------------------- | ------ | --------------------- |
| Data/Hora                                                  | source_event_id              | text   | Timestamp do evento   |
| Nome completo                                              | nome                         | text   | Nome do lead          |
| Email                                                      | email                        | text   | Email primário        |
| Telefone                                                   | telefone                     | text   | Telefone fallback     |
| É prestador de serviços?                                   | respostas.prestador_servicos | json   | Dados adicionais      |
| Qual o segmento de atuação da empresa?                     | respostas.segmento           | json   | Dados adicionais      |
| Qual seu cargo na empresa?                                 | respostas.cargo              | json   | Dados adicionais      |
| Quem faz a gestão financeira hoje?                         | respostas.gestao_financeira  | json   | Dados adicionais      |
| Qual o maior problema na gestão financeira?                | resproblema_gestao           | json   | Dados adicionais      |
| O que te motivou a buscar a terceirização financeira agora | respostas.motivacao          | json   | Dados adicionais      |
| Nome do Anúncio                                            | anuncio_criativo             | text   | Nome do anúncio       |
| Conjunto de Anúncio                                        | respostas.conjunto_anuncio   | json   | Dados adicionais      |
| Campanha                                                   | campanha                     | text   | Nome da campanha      |
| (fixo)                                                     | origem                       | select | `meta_ads`            |
| (fixo)                                                     | estagio                      | select | `capturado`           |
| (auto)                                                     | lead_id                      | text   | UUID gerado           |
| (auto)                                                     | opportunity_id               | text   | UUID gerado           |
| (auto)                                                     | dedup_key                    | text   | email + telefone      |
| (auto)                                                     | responsavel                  | text   | Padrão ou round-robin |

### Meta Ads (Anúncios de Cadastro) → CRM

| Campo Planilha                                                                                              | Campo CRM                     | Tipo   | Observação            |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------- | ------ | --------------------- |
| Data/Hora                                                                                                   | source_event_id               | text   | Timestamp do evento   |
| Nome completo                                                                                               | nome                          | text   | Nome do lead          |
| Email                                                                                                       | email                         | text   | Email primário        |
| Telefone                                                                                                    | telefone                      | text   | Telefone fallback     |
| Qual é o seu cargo na empresa?                                                                              | respostas.cargo               | json   | Dados adicionais      |
| Quantos funcionários a empresa possui hoje?                                                                 | respostas.funcionarios        | json   | Dados adicionais      |
| Qual é o faturamento médio mensal da empresa?                                                               | respostas.faturamento         | json   | Dados adicionais      |
| Hoje, como é feita a gestão financeira da empresa?                                                          | respostas.gestao_financeira   | json   | Dados adicionais      |
| Qual é o MAIOR problema financeiro da sua empresa hoje?                                                     | respostas.problema_financeiro | json   | Dados adicionais      |
| Você tem interesse em contratar uma empresa para cuidar da gestão financeira do seu negócio?                | respostas.interesse           | json   | Dados adicionais      |
| Se fizer sentido, você estaria disposto a investir mensalmente para ter uma gestão financeira profissional? | respostas.investimento        | json   | Dados adicionais      |
| O que te motivou a buscar terceirização financeira agora?                                                   | respostas.motivacao           | json   | Dados adicionais      |
| Nome do Anúncio                                                                                             | anuncio_criativo              | text   | Nome do anúncio       |
| Conjunto de Anúncio                                                                                         | respostas.conjunto_anuncio    | json   | Dados adicionais      |
| Campanha                                                                                                    | campanha                      | text   | Nome da campanha      |
| (fixo)                                                                                                      | origem                        | select | `meta_ads`            |
| (fixo)                                                                                                      | estagio                       | select | `capturado`           |
| (auto)                                                                                                      | lead_id                       | text   | UUID gerado           |
| (auto)                                                                                                      | opportunity_id                | text   | UUID gerado           |
| (auto)                                                                                                      | dedup_key                     | text   | email + telefone      |
| (auto)                                                                                                      | responsavel                   | text   | Padrão ou round-robin |

## Chave de idempotência

**dedup_key** = `email` (primário) + `telefone` (fallback)

- Se email existe: `email`
- Se email não existe mas telefone existe: `telefone`
- Se ambos não existem: evento vai para `aguardando_dados`

## Regras de negócio

| Regra    | Condição                                 | Ação                                                    |
| -------- | ---------------------------------------- | ------------------------------------------------------- |
| RN-1.005 | Evento com chave idempotente válida      | Processar uma vez; repetição não cria nova oportunidade |
| RN-1.006 | E-mail ou telefone presente              | Criar/atualizar conforme chave aprovada                 |
| RN-1.007 | Ambos e-mail e telefone ausentes         | Encaminhar para `aguardando_dados`                      |
| RN-1.008 | Origem/campanha/criativo não fornecido   | Persistir como ausente (nunca inventar)                 |
| RN-1.009 | Evento inválido ou conector indisponível | Registrar erro seguro e manter recuperação              |

## Fixture sintética para teste

```json
{
  "nome": "TESTE F1-T04 Lead Sintético",
  "email": "teste.f1t04@example.com",
  "telefone": "(48) 99999-0000",
  "origem": "meta_ads",
  "campanha": "Campanha de Teste F1-T04",
  "anuncio_criativo": "Anúncio de Teste",
  "respostas": {
    "prestador_servicos": "sim",
    "segmento": "serviços",
    "cargo": "sócio/proprietário",
    "motivacao": "Teste de integração F1-T04"
  },
  "estagio": "capturado",
  "responsavel": "Vinicius",
  "source_event_id": "2026-08-21T11:00:00-03:00",
  "dedup_key": "teste.f1t04@example.com"
}
```

## Conector

**Tipo:** Polling periódico via Google Sheets MCP
**Intervalo:** A cada 10 minutos
**Fluxo:** Cron → Google Sheets MCP → ler planilhas → upsert no CRM Skip

## Aprovações

| Item               | Status      | Data       |
| ------------------ | ----------- | ---------- |
| Formulário         | ✅ Aprovado | 2026-08-21 |
| Conector           | ✅ Aprovado | 2026-08-21 |
| Destino            | ✅ Aprovado | 2026-08-21 |
| Chave idempotência | ✅ Aprovada | 2026-08-21 |
| Mapa de campos     | ✅ Aprovado | 2026-08-21 |
| Fixture sintética  | ✅ Aprovada | 2026-08-21 |
