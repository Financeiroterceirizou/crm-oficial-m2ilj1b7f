// pocketbase/migrations/0015_backdate_fixture_reativacao.js
// F4 5ef4b7cd: backdate da fixture de QA (0014 criou a fixture em 16/10; o caminho
// elegível exige created >= 90 dias). SQL direto porque autodate não retroage via API/ORM.
// Idempotente: UPDATE restrito à linha da fixture.

migrate(
  (app) => {
    app
      .db()
      .newQuery(
        "UPDATE leads SET created = '2026-07-01 12:00:00.000Z', updated = '2026-08-01 12:00:00.000Z' WHERE dedup_key = 'fixture-reativacao-qa-20261016'",
      )
      .execute()
    console.log('Migration 0015 aplicada: backdate da fixture de reativação')
  },
  (app) => {
    app
      .db()
      .newQuery(
        "UPDATE leads SET created = '2026-10-16 15:01:35.665Z', updated = '2026-10-16 15:01:35.665Z' WHERE dedup_key = 'fixture-reativacao-qa-20261016'",
      )
      .execute()
    console.log('Migration 0015 revertida: datas da fixture restauradas')
  },
)
