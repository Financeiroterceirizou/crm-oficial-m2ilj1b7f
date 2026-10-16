// pocketbase/migrations/0014_seed_fixture_reativacao.js
// F4 5ef4b7cd: fixture de QA para provar o caminho ELEGÍVEL da fila de reativação.
//
// Por que migration: o caminho elegível exige lead captado há >= 90 dias; `created`
// é autodate e não pode ser retroativo via API. Precedente: migration 0014 re-executa
// idempotente. A fixture é TEMPORÁRIA e claramente marcada — removida após o teste
// humano (ver changelog 16/10/2026). Rollback (down) remove a fixture.
//
// Condições da fixture: qualificado (prestador, regra F2), CNPJ nas respostas,
// captada 2026-07-01 (>= 90 dias em 16/10), última interação 2026-08-01 (>= 60 dias),
// sem descadastro/bounce/objeção.

migrate(
  (app) => {
    const existentes = app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
      dk: 'fixture-reativacao-qa-20261016',
    })
    if (existentes.length > 0) {
      console.log('Migration 0014: fixture ja existe, nada a fazer')
      return
    }
    const collection = app.findCollectionByNameOrId('leads')
    const rec = new Record(collection)
    rec.set('lead_id', 'LEAD-FIXTURE-REATIVACAO-QA')
    rec.set('opportunity_id', 'OPP-FIXTURE-REATIVACAO-QA')
    rec.set('nome', 'FIXTURE Reativação QA (remover após teste)')
    rec.set('email', 'fixture.reativacao@qa.local')
    rec.set('telefone', '5599000000000')
    rec.set('origem', 'manual')
    rec.set('campanha', 'fixture_qa')
    rec.set('estagio', 'capturado')
    rec.set('responsavel', 'fixture_qa')
    rec.set('dedup_key', 'fixture-reativacao-qa-20261016')
    rec.set('estado_qualificacao', 'qualificado')
    rec.set('score', 5)
    rec.set('motivo_decisao', 'fixture_qa_prestador_com_cnpj')
    rec.set('created', '2026-07-01 12:00:00.000Z')
    rec.set('ultima_interacao', '2026-08-01 12:00:00.000Z')
    rec.set(
      'respostas',
      JSON.stringify({
        segmento: 'consultorias_negocio',
        cargo: 'proprietario',
        cnpj: '00.000.000/0001-00',
      }),
    )
    app.save(rec)
    console.log('Migration 0014 aplicada: fixture de reativação criada (temporária)')
  },
  (app) => {
    const existentes = app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
      dk: 'fixture-reativacao-qa-20261016',
    })
    for (let i = 0; i < existentes.length; i++) {
      try {
        app.delete(existentes[i])
      } catch (_) {}
    }
    console.log('Migration 0014 revertida: fixture de reativação removida')
  },
)
