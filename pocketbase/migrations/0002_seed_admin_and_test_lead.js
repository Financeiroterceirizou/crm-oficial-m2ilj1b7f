// pocketbase/migrations/0002_seed_admin_and_test_lead.js
// F1-T02: Criar usuário admin e lead sintético de teste

migrate(
  (app) => {
    // 1. Criar usuário admin (idempotente)
    const users = app.findCollectionByNameOrId('_pb_users_auth_')
    let adminUser
    try {
      adminUser = app.findAuthRecordByEmail('_pb_users_auth_', 'vinicius@terceirizou.com.br')
    } catch (_) {}
    if (!adminUser) {
      adminUser = new Record(users)
      adminUser.setEmail('vinicius@terceirizou.com.br')
      adminUser.setPassword('Terceirizou@2026')
      adminUser.setVerified(true)
      adminUser.set('name', 'Vinicius')
      app.save(adminUser)
      console.log('Admin user criado: vinicius@terceirizou.com.br')
    } else {
      console.log('Admin user já existe')
    }

    // 2. Criar lead sintético de teste (idempotente)
    const leads = app.findCollectionByNameOrId('leads')
    const testEmail = 'maria.teste@email.com'
    const dedupKey = $security.sha256(testEmail + '2026-08-19T18:10:00')
    try {
      app.findFirstRecordByData('leads', 'dedup_key', dedupKey)
      console.log('Lead de teste já existe')
      return
    } catch (_) {}

    const lead = new Record(leads)
    lead.set('lead_id', $security.randomString(12))
    lead.set('opportunity_id', $security.randomString(12))
    lead.set('nome', 'Maria Silva Teste')
    lead.set('email', testEmail)
    lead.set('telefone', '(48) 99999-0000')
    lead.set('origem', 'meta_ads')
    lead.set('campanha', '[LEADS] [FORM INSTANT] [FB/IG] - 19.12.2025')
    lead.set('anuncio_criativo', 'AD 15 - VID IG 28/05 - Você não tem problema de faturamento')
    lead.set('respostas', {
      prestador: 'sim',
      segmento: 'servicos',
      cargo: 'socio_proprietario',
      gestao_financeira: 'eu_mesmo',
      maior_problema: 'falta_de_relatórios',
      motivacao: 'apoio_especializado',
    })
    lead.set('estagio', 'capturado')
    lead.set('responsavel', 'Henrique Tavano')
    lead.set('dedup_key', dedupKey)
    lead.set('source_event_id', $security.randomString(16))
    lead.set('historico', [
      {
        acao: 'criacao',
        ator: 'sistema',
        data: '2026-08-19T18:10:00',
        detalhes: 'Lead criado via teste F1-T02',
      },
    ])
    app.save(lead)
    console.log('Lead de teste criado: Maria Silva Teste (' + testEmail + ')')
  },
  (app) => {
    // Down: remover lead de teste e admin
    try {
      const dedupKey = $security.sha256('maria.teste@email.com' + '2026-08-19T18:10:00')
      const lead = app.findFirstRecordByData('leads', 'dedup_key', dedupKey)
      app.delete(lead)
    } catch (_) {}
    try {
      const admin = app.findAuthRecordByEmail('_pb_users_auth_', 'vinicius@terceirizou.com.br')
      app.delete(admin)
    } catch (_) {}
  },
)
