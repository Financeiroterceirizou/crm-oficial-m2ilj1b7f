// pocketbase/migrations/0012_add_meta_espelho_fields.js
// F4 cd704a1c: campos do espelho Meta (SPEC-4-001 CA-4-102/103).
//   meta_campanha_id     text  (id da campanha no Meta)
//   meta_campanha_nome   text  (nome oficial da campanha no Meta)
//   meta_anuncio_id      text  (id do anúncio no Meta)
//   meta_anuncio_nome    text  (nome oficial do anúncio no Meta)
//   meta_status          text  (espelhado | sem_dado_meta | nao_aplicavel | divergente)
//   meta_proveniencia    json  (fonte, período, data_carga, tipo de match)
// ADITIVA; rollback remove apenas estes campos. NÃO sobrescreve campanha/anuncio_criativo originais (RN-4-103).

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    const novos = [
      new TextField({ name: 'meta_campanha_id', required: false }),
      new TextField({ name: 'meta_campanha_nome', required: false }),
      new TextField({ name: 'meta_anuncio_id', required: false }),
      new TextField({ name: 'meta_anuncio_nome', required: false }),
      new TextField({ name: 'meta_status', required: false }),
      new JSONField({ name: 'meta_proveniencia', required: false }),
    ]
    for (const f of novos) {
      if (!nomes.has(f.name)) collection.fields.add(f)
    }
    app.save(collection)
    console.log('Migration 0012 aplicada: campos do espelho Meta adicionados a leads')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    for (const nome of [
      'meta_campanha_id',
      'meta_campanha_nome',
      'meta_anuncio_id',
      'meta_anuncio_nome',
      'meta_status',
      'meta_proveniencia',
    ]) {
      try {
        collection.fields.removeByName(nome)
      } catch (_) {}
    }
    app.save(collection)
    console.log('Migration 0012 revertida: campos do espelho Meta removidos')
  },
)
