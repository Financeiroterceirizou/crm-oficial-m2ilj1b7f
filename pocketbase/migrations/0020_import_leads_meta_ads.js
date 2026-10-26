// pocketbase/migrations/0020_import_leads_meta_ads.js
// Migração para importar os 18 leads reais da planilha "Leads Meta Ads - Jun.26"
// Fonte: https://docs.google.com/spreadsheets/d/1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk
// Linhas de teste sintético (TESTE e TESTE 2) foram descartadas.
// Idempotente: checa existência por dedup_key antes de inserir.

migrate(
  (app) => {
    const leadsCollection = app.findCollectionByNameOrId('leads')

    const rawLeads = [
      {
        data_hora_planilha: '20/06/2026 18:06',
        iso_created: '2026-06-20 18:06:00.000Z',
        nome: 'Fabiana Muniz',
        email: 'jasmimrosacaferestaurante@gmail.com',
        telefone: '(11) 98177-8097',
        prestador_servicos: '',
        segmento: 'comércio_/_loja_/_varejo',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'falta_de_relatórios_para_tomada_de_decisão',
        motivacao: 'Apoio especializado',
        anuncio_criativo:
          'AD 15 - VID IG 28/05 - Você não tem problema de faturamento, você tem problema de controle',
        conjunto_anuncio:
          '02 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [ABERTO] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '21/06/2026 19:45',
        iso_created: '2026-06-21 19:45:00.000Z',
        nome: 'Rossana Zambelli',
        email: 'rossana.zambelli@soteplas.com.br',
        telefone: '(31) 98524-6084',
        prestador_servicos: '',
        segmento: 'indústria_/_agro_/_produção',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'outro',
        motivacao:
          'O sistema de gestão financeira não funciona, precisaria ser reimplatado, e não temho tempo para isto.',
        anuncio_criativo:
          'AD 15 - VID IG 28/05 - Você não tem problema de faturamento, você tem problema de controle',
        conjunto_anuncio:
          '02 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [ABERTO] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '22/06/2026 16:41',
        iso_created: '2026-06-22 16:41:00.000Z',
        nome: 'Graci Julião',
        email: 'juliaograci@gmail.com',
        telefone: '(47) 99111-0559',
        prestador_servicos: '',
        segmento: 'Construção Civil - Piso industrial',
        cargo: 'administrativo_/_financeiro',
        quem_faz_gestao: 'não_temos_uma_rotina_financeira_definida',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        motivacao: 'Não quero voltar da onde sai quero mudar',
        anuncio_criativo:
          'AD 15 - VID IG 28/05 - Você não tem problema de faturamento, você tem problema de controle',
        conjunto_anuncio:
          '02 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [ABERTO] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: 'Henrique entrou em contato',
        reuniao_agendada: 'Reunião agendada',
      },
      {
        data_hora_planilha: '12/07/2026 11:00',
        iso_created: '2026-07-12 11:00:00.000Z',
        nome: 'Rodrigo Vendramini',
        email: 'rodrigovendramini@hotmail.com',
        telefone: '(47) 99984-4078',
        prestador_servicos: '',
        segmento: 'saúde_/_estética_/_clínicas',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'financeiro_interno_estruturado',
        maior_problema: 'inadimplência_/_dificuldade_com_cobranças',
        motivacao:
          'Minha empresa fatura 2.3k mês e gasta mais que fatura.\nA muito tempo não consigo colocar gastos dentro do recebimento.\nBancos me apertam, honorários, funcionários e tributos consomem.\nFaturo muito bem mas a conta explode todo mês!',
        anuncio_criativo:
          'AD 15 - VID IG 28/05 - Você não tem problema de faturamento, você tem problema de controle',
        conjunto_anuncio:
          '02 - [FB/IG] [GEO: Floripa, BC, BH, Curitiba, SP] [30-55] [H-M] [ABERTO] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '12/08/2026 05:36',
        iso_created: '2026-08-12 05:36:00.000Z',
        nome: 'Henrique T. Sammartino',
        email: 'henrique.tavano@gmail.com',
        telefone: '(48) 99167-7077',
        prestador_servicos: '',
        segmento: 'consultoria_/_assessoria',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'alguém_interno,_mas_sem_processo_claro',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        motivacao: 'Teste de funcionalidade',
        anuncio_criativo: 'AD 01 - Post IG 11/12 - Controle financeiro',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '13/08/2026 08:53',
        iso_created: '2026-08-13 08:53:00.000Z',
        nome: 'Victor Vanzella',
        email: 'victorl.vanzella@hotmail.com',
        telefone: '(11) 95300-2417',
        prestador_servicos: '',
        segmento: 'saúde_/_estética_/_clínicas',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'contas_a_pagar/receber_desorganizadas',
        motivacao: 'Organizar as finanças',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '15/08/2026 16:08',
        iso_created: '2026-08-15 16:08:00.000Z',
        nome: 'Vinícius Oliveira',
        email: 'oliveiradacosta.vinicius@gmail.com',
        telefone: '(48) 99122-6496',
        prestador_servicos: '',
        segmento: 'consultoria_/_assessoria',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        motivacao: 'Organizar as finanças',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '16/08/2026 07:30',
        iso_created: '2026-08-16 07:30:00.000Z',
        nome: 'Jailson Araujo',
        email: 'araujo.jailson71@gmail.com',
        telefone: '(11) 97161-2090',
        prestador_servicos: '',
        segmento: 'comércio_/_loja_/_varejo',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'alguém_interno,_mas_sem_processo_claro',
        maior_problema: 'contas_a_pagar/receber_desorganizadas',
        motivacao: 'quero entender como funciona a terceirização',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '16/08/2026 14:07',
        iso_created: '2026-08-16 14:07:00.000Z',
        nome: 'Wallysson Eder Almeida',
        email: 'whjabo@gmail.com',
        telefone: '(31) 99603-9946',
        prestador_servicos: '',
        segmento: 'comércio_/_loja_/_varejo',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        motivacao: 'Sofrimento',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '18/08/2026 17:35',
        iso_created: '2026-08-18 17:35:00.000Z',
        nome: 'Cinthya Santos',
        email: 'diego.santana01@yahoo.com.br',
        telefone: '(31) 99264-0370',
        prestador_servicos: 'sim',
        segmento: 'locação_/_manutenção_/_operação_de_serviços',
        cargo: 'outro',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        motivacao: 'Queda de trabalho',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '26/08/2026 09:38',
        iso_created: '2026-08-26 09:38:00.000Z',
        nome: 'Poli Cristal Estética Automotiva',
        email: 'policristallavacar@gmail.com',
        telefone: '(11) 97307-6205',
        prestador_servicos: 'sim',
        segmento: 'outros_segmentos_de_prestação_de_serviço',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        motivacao: 'Organizar a financeira',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '07/09/2026 19:24',
        iso_created: '2026-09-07 19:24:00.000Z',
        nome: 'Guilherme Assad',
        email: 'guilherme.assad.10@gmail.com',
        telefone: '(12) 99674-2451',
        prestador_servicos: 'sim',
        segmento: 'locação_/_manutenção_/_operação_de_serviços',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'alguém_interno,_mas_sem_processo_claro',
        maior_problema: 'falta_de_tempo_para_cuidar_do_financeiro',
        motivacao: 'Falta de tempo',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '08/09/2026 03:11',
        iso_created: '2026-09-08 03:11:00.000Z',
        nome: 'Group Lift Brasil',
        email: 'comercial@groupliftbrasil.com',
        telefone: '(48) 99208-7519',
        prestador_servicos: 'sim',
        segmento: 'outros_segmentos_de_prestação_de_serviço',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'outro',
        motivacao: 'Crescimento da empresa',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '13/09/2026 11:43',
        iso_created: '2026-09-13 11:43:00.000Z',
        nome: 'PODOBELLO BARREIRO',
        email: 'podobelo@gmail.com',
        telefone: '(31) 97308-7152',
        prestador_servicos: 'sim',
        segmento: 'consultoria_/_assessoria',
        cargo: 'outro',
        quem_faz_gestao: 'contador',
        maior_problema: 'mistura_finanças_pessoais_e_da_empresa',
        motivacao:
          'O motivo maior e falta de dinheiro Desorganizao tôtal teve vc arios Roubos.tinhas duas secretaria Hoje nao tem mais trabalho Sozinha? Nossa tá muito difícil?',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '19/09/2026 14:12',
        iso_created: '2026-09-19 14:12:00.000Z',
        nome: 'Sidnei Bispo Dos Santos',
        email: 'sidneibispo.moveis@gmail.com',
        telefone: '(12) 98155-8510',
        prestador_servicos: 'sim',
        segmento: 'outros_segmentos_de_prestação_de_serviço',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'não_temos_uma_rotina_financeira_definida',
        maior_problema: 'não_sei_exatamente_onde_o_dinheiro_se_perde',
        motivacao: 'cansado da bagunça',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '23/09/2026 20:44',
        iso_created: '2026-09-23 20:44:00.000Z',
        nome: 'Ana Maria Viriato',
        email: 'anamariaviriato65@gmail.com',
        telefone: '(31) 99798-3813',
        prestador_servicos: 'sim',
        segmento: 'educação_/_cursos_/_treinamentos',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'inadimplência_/_dificuldade_com_cobranças',
        motivacao: 'Desorganização financeira',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '25/09/2026 18:43',
        iso_created: '2026-09-25 18:43:00.000Z',
        nome: 'erick Francisco de moura',
        email: 'luisrensch33@gmail.com',
        telefone: '(47) 93383-9681',
        prestador_servicos: 'sim',
        segmento: 'educação_/_cursos_/_treinamentos',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        motivacao: 'organização',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '29/09/2026 19:06',
        iso_created: '2026-09-29 19:06:00.000Z',
        nome: 'Vania Battistini',
        email: 'vision.clean@hotmail.com',
        telefone: '(11) 94036-4346',
        prestador_servicos: 'sim',
        segmento: 'outros_segmentos_de_prestação_de_serviço',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'não_sei_exatamente_onde_o_dinheiro_se_perde',
        motivacao: 'Não saber fazer gestão financeira do meu negócio',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
      },
      {
        data_hora_planilha: '01/10/2026 17:09',
        iso_created: '2026-10-01 17:09:00.000Z',
        nome: 'Ricardo Mesquita',
        email: 'mesquitaricardoaliiance@gmail.com',
        telefone: '(11) 94037-7395',
        prestador_servicos: 'sim',
        segmento: 'outros_segmentos_de_prestação_de_serviço',
        cargo: 'sócio_/_proprietário',
        quem_faz_gestao: 'eu_mesmo_/_sócio_da_empresa',
        maior_problema: 'falta_de_previsibilidade_de_caixa',
        motivacao: 'Organização',
        anuncio_criativo: 'AD 03 - VID Dormir tranquilo',
        conjunto_anuncio:
          '00 - [AUTO] [GEO: Cidades Novas] [30-55] [H-M] [Cargos, comportamentos, interesses] [ADV+]',
        campanha: '[LEADS] [FORM INSTANT] [POS. AUTO] [NOVO WPP] - 06.08.2026',
        henrique_contato: '',
        reuniao_agendada: '',
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
      // Ex: "20/06/2026 18:06" -> "20062026"
      const datePart = dateStr.split(' ')[0]
      return datePart.replace(/\D/g, '')
    }

    let insertedCount = 0

    for (let i = 0; i < rawLeads.length; i++) {
      const item = rawLeads[i]
      const dedupKey = item.email.toLowerCase().trim()

      // Verificar se já existe (idempotência por dedup_key)
      const existing = app.findRecordsByFilter('leads', "dedup_key = '" + dedupKey + "'", '', 1, 0)
      if (existing && existing.length > 0) {
        console.log('[0020_import_leads_meta_ads] Lead ja existente (' + dedupKey + '), pulando.')
        continue
      }

      const slug = slugify(item.nome)
      const ddmmaaaa = extractDateDigits(item.data_hora_planilha)
      const leadId = 'metaads-' + slug + '-' + ddmmaaaa

      const respostas = {
        data_hora_planilha: item.data_hora_planilha,
        prestador_servicos: item.prestador_servicos || null,
        segmento: item.segmento || null,
        cargo: item.cargo || null,
        quem_faz_gestao: item.quem_faz_gestao || null,
        maior_problema: item.maior_problema || null,
        motivacao: item.motivacao || null,
        conjunto_anuncio: item.conjunto_anuncio || null,
      }

      if (item.henrique_contato) {
        respostas.henrique_contato = item.henrique_contato
      }
      if (item.reuniao_agendada) {
        respostas.reuniao_agendada = item.reuniao_agendada
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

      // Preservar a Data/Hora original da planilha atualizando created e updated via SQL
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
          '[0020_import_leads_meta_ads] Aviso: nao foi possivel ajustar created para ' +
            record.id +
            ': ' +
            err,
        )
      }

      insertedCount++
    }

    console.log(
      '[0020_import_leads_meta_ads] Migracao concluida. Inseridos: ' + insertedCount + ' leads.',
    )
  },
  (app) => {
    // Reverter importação dos 18 leads criados por esta migração
    const dedupKeys = [
      'jasmimrosacaferestaurante@gmail.com',
      'rossana.zambelli@soteplas.com.br',
      'juliaograci@gmail.com',
      'rodrigovendramini@hotmail.com',
      'henrique.tavano@gmail.com',
      'victorl.vanzella@hotmail.com',
      'oliveiradacosta.vinicius@gmail.com',
      'araujo.jailson71@gmail.com',
      'whjabo@gmail.com',
      'diego.santana01@yahoo.com.br',
      'policristallavacar@gmail.com',
      'guilherme.assad.10@gmail.com',
      'comercial@groupliftbrasil.com',
      'podobelo@gmail.com',
      'sidneibispo.moveis@gmail.com',
      'anamariaviriato65@gmail.com',
      'luisrensch33@gmail.com',
      'vision.clean@hotmail.com',
      'mesquitaricardoaliiance@gmail.com',
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
