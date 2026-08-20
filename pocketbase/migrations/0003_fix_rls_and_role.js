// pocketbase/migrations/0003_fix_rls_and_role.js
// F1-T02: Corrigir RLS — adicionar campo role ao users, atualizar admin, tornar list/view público para teste

migrate(
  (app) => {
    // 1. Adicionar campo 'role' à collection users
    const users = app.findCollectionByNameOrId('_pb_users_auth_')
    if (!users.fields.getByName('role')) {
      users.fields.add(
        new SelectField({
          name: 'role',
          values: ['admin', 'comercial', 'marketing', 'integracao'],
          maxSelect: 1,
          defaultValue: 'comercial',
        }),
      )
      app.save(users)
      console.log('Campo role adicionado à collection users')
    }

    // 2. Atualizar admin user com role = 'admin'
    try {
      const admin = app.findAuthRecordByEmail('_pb_users_auth_', 'vinicius@terceirizou.com.br')
      admin.set('role', 'admin')
      app.save(admin)
      console.log('Admin user atualizado com role = admin')
    } catch (_) {
      console.log('Admin user não encontrado para atualizar role')
    }

    // 3. Corrigir RLS da collection leads — list e view públicos para teste
    const leads = app.findCollectionByNameOrId('leads')
    leads.listRule = '' // público para leitura (teste)
    leads.viewRule = '' // público para leitura (teste)
    leads.createRule = '' // público para criação (teste — webhook)
    leads.updateRule = "responsavel = @request.auth.id || @request.auth.role = 'admin'"
    leads.deleteRule = "@request.auth.role = 'admin'"
    app.save(leads)
    console.log('RLS leads atualizado — list/view/create públicos para teste')
  },
  (app) => {
    // Reverter: remover campo role e restaurar RLS original
    const users = app.findCollectionByNameOrId('_pb_users_auth_')
    if (users.fields.getByName('role')) {
      users.fields.removeByName('role')
      app.save(users)
    }
    const leads = app.findCollectionByNameOrId('leads')
    leads.listRule =
      "responsavel = @request.auth.id || @request.auth.role = 'admin' || @request.auth.role = 'marketing'"
    leads.viewRule =
      "responsavel = @request.auth.id || @request.auth.role = 'admin' || @request.auth.role = 'marketing'"
    leads.createRule = "@request.auth.role = 'admin' || @request.auth.role = 'integracao'"
    leads.updateRule = "responsavel = @request.auth.id || @request.auth.role = 'admin'"
    leads.deleteRule = "@request.auth.role = 'admin'"
    app.save(leads)
  },
)
