// pocketbase/migrations/0022_import_leads_anuncios_cadastro_real.js
// Migração para importar os leads REAIS da aba "Leads Anúncios de Cadastro" (gid=0)
// Fonte: https://docs.google.com/spreadsheets/d/1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk (gid=0)
//
// A aba "Leads Anúncios de Cadastro" possui 25 linhas totais de leads.
// 1 linha interna descartada:
// - Vinícius Oliveira da Costa (vinicius@terceirizou.com.br / oliveiradacosta.vinicius@gmail.com - sócio / teste de marketing)
// (A linha de teste de Henrique T. Sammartino está na primeira aba "Leads Meta Ads - Jun.26", não nesta aba).
// Restam 24 leads reais a importar.
//
// Idempotente: checa existência por dedup_key antes de inserir (deduplicação por email normalizado).
// Preserva datas originais em created e updated via SQLite.

migrate(
  (app) => {
    const leadsCollection = app.findCollectionByNameOrId('leads')

    const rawLeads = [
      {
        data_hora_planilha: '25/12/2025 08:06',
        iso_created: '2025-12-25 08:06:00.000Z',
        nome: 'Sinval de Lima Filho',
        email: 'sinval.glp@gmail.com',
        telefone: '(11) 98147-3707',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'acima_de_r$_200_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Ter mais clareza no meu caixa',
        anuncio_criativo: 'AD 05 - Post IG 11/12 - Controle financeiro',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '27/12/2025 19:01',
        iso_created: '2025-12-27 19:01:00.000Z',
        nome: 'Érica Barbosa',
        email: 'erica.bbsilva@gmail.com',
        telefone: '(11) 94939-0925',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao:
          'Quero crescer e ter uma visão clara organizada e objetiva do financeiro. E sozinha não consigo.',
        anuncio_criativo: 'AD 05 - Post IG 11/12 - Controle financeiro',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '05/01/2026 08:06',
        iso_created: '2026-01-05 08:06:00.000Z',
        nome: 'Debora',
        email: 'residencialsennior@gmail.comr',
        telefone: '(48) 99968-0707',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'margem_baixa_/_não_sabe_onde_perde_dinheiro',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'preciso muito colocar tudonem.ordem saber como estaca empresa no geral',
        anuncio_criativo: 'AD 05 - Post IG 11/12 - Controle financeiro',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '20/02/2026 20:38',
        iso_created: '2026-02-20 20:38:00.000Z',
        nome: 'Alessandra José',
        email: 'alessandrajose6372@gmail.com',
        telefone: '(11) 95063-8160',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_80_mil_a_r$_200_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Busco mudança',
        anuncio_criativo: 'AD 05 - Post IG 11/12 - Controle financeiro',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Mercearia (não faz sentido)',
      },
      {
        data_hora_planilha: '04/03/2026 07:54',
        iso_created: '2026-03-04 07:54:00.000Z',
        nome: 'Marcia Perdigão Gontijo',
        email: 'marciatalentos@hotmail.com',
        telefone: 'p:+553791314181',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'contador_faz_tudo',
        maior_problema: 'margem_baixa_/_não_sabe_onde_perde_dinheiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Necessidade',
        anuncio_criativo: 'AD 10 - VID Não é empréstimo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '11/03/2026 06:39',
        iso_created: '2026-03-11 06:39:00.000Z',
        nome: 'Joao Luiz Romantini',
        email: 'jromantini@gmail.com',
        telefone: 'p:+5511999804398',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'acima_de_r$_200_mil',
        quem_faz_gestao: 'tenho_financeiro_interno_estruturado',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'descontentamento com financeiro interno',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: 'Reunião 16/03 às 10:00',
        observacoes: 'Enviado apresentação dia 16/03 | Enviado mensagem dia 23/03',
      },
      {
        data_hora_planilha: '13/03/2026 20:21',
        iso_created: '2026-03-13 20:21:00.000Z',
        nome: 'Hilceu Geraldo da Silva',
        email: 'hilceuibia@gmail.com',
        telefone: '3498205269',
        cargo: 'diretor',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'margem_baixa_/_não_sabe_onde_perde_dinheiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'sim',
        motivacao: 'buscar lucro',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: 'Reunião 16/03 às 14:00',
        observacoes: 'Enviado apresentação dia 16/03 | Enviado mensagem dia 23/03',
      },
      {
        data_hora_planilha: '14/03/2026 18:02',
        iso_created: '2026-03-14 18:02:00.000Z',
        nome: 'Ramon passos',
        email: 'pescadosbluefish@gmail.com',
        telefone: '(47) 99161-3383',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'acima_de_r$_200_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Desorganização',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes:
          'Vinícius entrou em contato e cliente não respondeu | Enviado mensagem dia 23/03',
      },
      {
        data_hora_planilha: '15/03/2026 00:01',
        iso_created: '2026-03-15 00:01:00.000Z',
        nome: 'Adriana Maia',
        email: 'refrimaia@refrimaia.com.br',
        telefone: '(11) 97483-3932',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'acima_de_r$_200_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao:
          'Preciso de uma direção financeira, nao sobra dinheiro e as dívidas somente aumentam...',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '19/03/2026 00:38',
        iso_created: '2026-03-19 00:38:00.000Z',
        nome: 'Daniela Carvalho',
        email: 'luivafinanceiro@gmail.com',
        telefone: '(11) 97829-8802',
        cargo: 'gerente',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_80_mil_a_r$_200_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'sim',
        motivacao: 'Organização',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '23/03/2026 07:15',
        iso_created: '2026-03-23 07:15:00.000Z',
        nome: 'Tabata',
        email: 'tabata@winovarh.com.br',
        telefone: '(12) 99255-0592',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'sim',
        motivacao: 'Quero alguém para arrumar vida pessoal e profissional',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: 'Evoluindo pra reunião',
        observacoes: 'Tabata ja interagiu no whatsapp',
      },
      {
        data_hora_planilha: '13/04/2026 13:32',
        iso_created: '2026-04-13 13:32:00.000Z',
        nome: 'Andressa',
        email: 'bertolo.andressa@gmail.com',
        telefone: '(48) 99817-4605',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'sim',
        motivacao:
          'Nosso financeiro está bagunçado, assim não temos previsão nem controle dos recebimentos e pagamentos',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: 'Reunião feita',
        observacoes: 'Deu feedback e disse que fechou com outro BPO',
      },
      {
        data_hora_planilha: '15/04/2026 00:10',
        iso_created: '2026-04-15 00:10:00.000Z',
        nome: 'David Coutinho',
        email: 'davidacoutinho@hotmail.com',
        telefone: '3899986875',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_80_mil_a_r$_200_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'A falta de organização do meu sistema financeiro',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '20/04/2026 23:41',
        iso_created: '2026-04-20 23:41:00.000Z',
        nome: 'Anime-se sp',
        email: 'mohamadams1977@gmail.com',
        telefone: '119328046000',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'sim',
        motivacao: 'Falta de sossego',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '21/04/2026 19:22',
        iso_created: '2026-04-21 19:22:00.000Z',
        nome: 'Edson Souza',
        email: 'souzaedson2202@gmail.com',
        telefone: '(31) 98477-7264',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'outro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Ganhar tempo e organização',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Vinícius entrou em contato',
      },
      {
        data_hora_planilha: '27/04/2026 20:51',
        iso_created: '2026-04-27 20:51:00.000Z',
        nome: 'Fabiula da silva pinto',
        email: 'retificawetofraga@gmail.com',
        telefone: '(93) 7533-5265',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'ter aplique cuide do financeiro sem ter que contratar mais um funcionário',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Vinícius entrou em contato por e-mail.',
      },
      {
        data_hora_planilha: '29/04/2026 17:58',
        iso_created: '2026-04-29 17:58:00.000Z',
        nome: 'Silvani Silva Souza',
        email: 'silvanisilvasouza@hotmail.com',
        telefone: '(31) 99371-5895',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Preciso melhorar',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Vinícius entrou em contato',
      },
      {
        data_hora_planilha: '01/05/2026 10:06',
        iso_created: '2026-05-01 10:06:00.000Z',
        nome: 'Carol Carvalho | Ginecologia Natural',
        email: 'mama_meteoro_9r@icloud.com',
        telefone: '(11) 99533-4022',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'tenho_alguém_interno,_mas_sem_processo_estruturado',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao:
          'Estou avaliando ainda para contratar no futuro e ter mais previsibilidade e organização',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Vinícius entrou em contato',
      },
      {
        data_hora_planilha: '02/05/2026 10:01',
        iso_created: '2026-05-02 10:01:00.000Z',
        nome: 'Sérgio Antônio',
        email: 'sergio@designpisos.com.br',
        telefone: '(11) 99143-8377',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '6_a_15',
        faturamento_medio: 'acima_de_r$_200_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'organização',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: 'Vinícius entrou em contato',
      },
      {
        data_hora_planilha: '09/05/2026 16:35',
        iso_created: '2026-05-09 16:35:00.000Z',
        nome: 'nando Montana',
        email: 'chefnandomontana@hotmail.com',
        telefone: '(34) 99107-3348',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'sim',
        motivacao: 'tempo livre',
        anuncio_criativo:
          'AD 13 - VID Mai.26 - Sua empresa fatura mais de 200 mil, mas parece que o dinheiro evapora',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '13/05/2026 15:56',
        iso_created: '2026-05-13 15:56:00.000Z',
        nome: 'Vitor Oliveira | Lojista Líder',
        email: 'doidaodotrembala157@gmail.com',
        telefone: '(11) 94305-8869',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'sim,_estou_avaliando_contratar',
        disposto_investir: 'sim',
        motivacao: 'Falta de controle',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
        observacoes: '',
      },
      {
        data_hora_planilha: '26/05/2026 19:23',
        iso_created: '2026-05-26 19:23:00.000Z',
        nome: 'roberto moreno',
        email: 'kayallami@gmail.com',
        telefone: '(11) 94744-9887',
        cargo: 'gerente',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        interesse_contratar: 'apenas_buscando_informações',
        disposto_investir: 'sim',
        motivacao: 'quero crescer mais estruturado',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: 'Reunião agendada paa 28/05 as 10h',
        observacoes:
          'Proposta enviada de terceirizou + hold | Por fone disse que tem chance de fechar com a agente',
      },
      {
        data_hora_planilha: '27/05/2026 09:39',
        iso_created: '2026-05-27 09:39:00.000Z',
        nome: 'João Eduardo',
        email: 'varelajoao658@gmail.com',
        telefone: '(47) 99642-6039',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_30_mil_a_r$_80_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'outro',
        interesse_contratar: 'sim,_mas_quero_entender_melhor_antes',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Organizar as finanças',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: 'Não responde',
      },
      {
        data_hora_planilha: '27/05/2026 21:29',
        iso_created: '2026-05-27 21:29:00.000Z',
        nome: 'Aldenora',
        email: 'aldenora_utikava@hotmail.com',
        telefone: '(11) 94769-4785',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_controle_financeiro',
        interesse_contratar: 'apenas_buscando_informações',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Ter ajudar e normalizar o problema',
        anuncio_criativo: 'AD 09 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: 'Telefone inexistente',
      },
      {
        data_hora_planilha: '31/05/2026 08:34',
        iso_created: '2026-05-31 08:34:00.000Z',
        nome: 'Sérgio Silva',
        email: 'eletrovoltseng@terra.com.br',
        telefone: '(11) 94028-4555',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'até_r$_30_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        interesse_contratar: 'apenas_buscando_informações',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Organizar as finanças',
        anuncio_criativo:
          'AD 14 - VID IG 07/05 - O dinheiro entra, mas no fim do mês parece que nunca sobra',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: 'Reuniao agendada',
        observacoes: '',
      },
      {
        data_hora_planilha: '05/06/2026 21:10',
        iso_created: '2026-06-05 21:10:00.000Z',
        nome: 'Michelle Borges',
        email: 'borgesmichelle2020@gmail.com',
        telefone: '3193986892',
        cargo: 'sócio_/_proprietário',
        quantos_funcionarios: '1_a_5',
        faturamento_medio: 'r$_80_mil_a_r$_200_mil',
        quem_faz_gestao: 'eu_mesmo_faço,_de_forma_simples',
        maior_problema: 'margem_baixa_/_não_sabe_onde_perde_dinheiro',
        interesse_contratar: 'apenas_buscando_informações',
        disposto_investir: 'depende_da_proposta',
        motivacao: 'Reduzir custos',
        anuncio_criativo:
          'AD 14 - VID IG 07/05 - O dinheiro entra, mas no fim do mês parece que nunca sobra',
        conjunto_anuncio:
          '00 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [CARGOS E EMPREGADORES] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
        observacoes: '',
      },
    ]

    function slugify(text) {
      return text
        .toString()
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
    }

    function extractDateDigits(dateStr) {
      // Ex: "25/12/2025 08:06" -> "25122025"
      const datePart = dateStr.split(' ')[0]
      return datePart.replace(/\D/g, '')
    }

    let insertedCount = 0
    let skippedCount = 0

    for (let i = 0; i < rawLeads.length; i++) {
      const item = rawLeads[i]
      const dedupKey = item.email.toLowerCase().trim()

      // Idempotência por dedup_key: pula se já existir no banco
      const existing = app.findRecordsByFilter('leads', "dedup_key = '" + dedupKey + "'", '', 1, 0)
      if (existing && existing.length > 0) {
        console.log(
          '[0022_import_leads_anuncios_cadastro_real] Lead ja existente (' +
            dedupKey +
            '), pulando.',
        )
        skippedCount++
        continue
      }

      const slug = slugify(item.nome)
      const ddmmaaaa = extractDateDigits(item.data_hora_planilha)
      const leadId = 'metaads-' + slug + '-' + ddmmaaaa

      // Tratar eventuais <br> ou <br/> como \n na motivação
      const motivacaoClean = item.motivacao ? item.motivacao.replace(/<br\s*\/?>/gi, '\n') : null

      const respostas = {
        data_hora_planilha: item.data_hora_planilha,
        cargo: item.cargo || null,
        quantos_funcionarios: item.quantos_funcionarios || null,
        faturamento_medio: item.faturamento_medio || null,
        quem_faz_gestao: item.quem_faz_gestao || null,
        maior_problema: item.maior_problema || null,
        interesse_contratar: item.interesse_contratar || null,
        disposto_investir: item.disposto_investir || null,
        motivacao: motivacaoClean,
        anuncio: item.anuncio_criativo || null,
        conjunto_anuncio: item.conjunto_anuncio || null,
        campanha: item.campanha || null,
      }

      if (item.henrique_contato) {
        respostas.henrique_contato = item.henrique_contato
      }
      if (item.reuniao_agendada) {
        respostas.reuniao_agendada = item.reuniao_agendada
      }
      if (item.observacoes) {
        respostas.observacoes = item.observacoes
      }

      const record = new Record(leadsCollection)
      record.set('lead_id', leadId)
      record.set('opportunity_id', 'nao_vinculado')
      record.set('nome', item.nome)
      record.set('email', item.email)
      record.set('telefone', item.telefone)
      record.set('origem', 'meta_ads')
      record.set('campanha', item.campanha)
      record.set('anuncio_criativo', item.anuncio_criativo)
      record.set('meta_campanha_nome', item.campanha)
      record.set('meta_anuncio_nome', item.anuncio_criativo)
      record.set('respostas', respostas)
      record.set('estagio', 'capturado')
      record.set('responsavel', 'Nao atribuido')
      record.set('dedup_key', dedupKey)

      app.save(record)

      // Preservar a Data/Hora original da planilha atualizando created e updated via SQLite
      try {
        app
          .db()
          .newQuery('UPDATE leads SET created = {:created}, updated = {:updated} WHERE id = {:id}')
          .bind({
            created: item.iso_created,
            updated: item.iso_created,
            id: record.id,
          })
          .execute()
      } catch (err) {
        console.log(
          '[0022_import_leads_anuncios_cadastro_real] Aviso: nao foi possivel ajustar created para ' +
            record.id +
            ': ' +
            err,
        )
      }

      insertedCount++
    }

    console.log(
      '[0022_import_leads_anuncios_cadastro_real] Migracao concluida. Inseridos: ' +
        insertedCount +
        ', ja existentes/pulados: ' +
        skippedCount,
    )
  },
  (app) => {
    // Reverter registros inseridos por esta migração
    const dedupKeys = [
      'sinval.glp@gmail.com',
      'erica.bbsilva@gmail.com',
      'residencialsennior@gmail.comr',
      'alessandrajose6372@gmail.com',
      'marciatalentos@hotmail.com',
      'jromantini@gmail.com',
      'hilceuibia@gmail.com',
      'pescadosbluefish@gmail.com',
      'refrimaia@refrimaia.com.br',
      'luivafinanceiro@gmail.com',
      'tabata@winovarh.com.br',
      'bertolo.andressa@gmail.com',
      'davidacoutinho@hotmail.com',
      'mohamadams1977@gmail.com',
      'souzaedson2202@gmail.com',
      'retificawetofraga@gmail.com',
      'silvanisilvasouza@hotmail.com',
      'mama_meteoro_9r@icloud.com',
      'sergio@designpisos.com.br',
      'chefnandomontana@hotmail.com',
      'doidaodotrembala157@gmail.com',
      'kayallami@gmail.com',
      'varelajoao658@gmail.com',
      'aldenora_utikava@hotmail.com',
      'eletrovoltseng@terra.com.br',
      'borgesmichelle2020@gmail.com',
    ]

    for (let i = 0; i < dedupKeys.length; i++) {
      try {
        const records = app.findRecordsByFilter(
          'leads',
          "dedup_key = '" + dedupKeys[i] + "'",
          '',
          1,
          0,
        )
        if (records && records.length > 0) {
          app.delete(records[0])
        }
      } catch (_) {}
    }
  },
)
