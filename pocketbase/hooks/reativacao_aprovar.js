// pocketbase/hooks/reativacao_aprovar.js
// F4 5ef4b7cd: aprovação humana de lote (RN-4-203). POST /backend/v1/reativacao/aprovar
// Nenhum contato é disparado — a fila só organiza; reabordagem é tarefa humana no
// WhatsApp (decisão 16/10). Idempotente por lote_id. Autenticação obrigatória (RN-4-205).

routerAdd(
  'POST',
  '/backend/v1/reativacao/aprovar',
  (e) => {
    const body = e.requestInfo().body || {}
    const loteId = String(body.lote_id || '').trim()
    const operador = String(body.operador || 'admin').trim()
    const observacao = String(body.observacao || '').trim()
    if (!loteId) return e.json(400, { error: 'Campos obrigatórios: lote_id' })

    // Idempotência: mesmo lote_id retorna o estado atual, sem duplicar.
    const existentes = $app.findRecordsByFilter(
      'reativacao_lote',
      'lote_id = {:lid}',
      '-created',
      1,
      0,
      { lid: loteId },
    )
    if (existentes.length > 0) {
      const rec = existentes[0]
      return e.json(200, {
        status: 'already_exists',
        lote_id: rec.get('lote_id'),
        estado: rec.get('estado'),
        aprovado_por: rec.get('aprovado_por'),
        total_incluidos: rec.get('total_incluidos'),
        total_excluidos: rec.get('total_excluidos'),
      })
    }

    // Recalcula a fila no momento da aprovação — nunca reutiliza lista envelhecida.
    const registros = $app.findRecordsByFilter('leads', '', '-created', 500, 0)
    const agora = new Date().getTime()
    const noventa = 90 * 24 * 60 * 60 * 1000
    const sessenta = 60 * 24 * 60 * 60 * 1000

    const temCnpj = (rec) => {
      let resp = rec.get('respostas')
      if (typeof resp === 'string') {
        try {
          resp = JSON.parse(resp)
        } catch (_) {
          resp = null
        }
      }
      if (!resp || typeof resp !== 'object') return false
      for (const chave in resp) {
        if (String(chave).toLowerCase().indexOf('cnpj') !== -1) {
          const valor = String(resp[chave] || '').trim()
          if (valor !== '' && valor !== '-' && valor !== 'null') return true
        }
      }
      return false
    }

    const elegiveis = []
    const excluidos = []

    for (let i = 0; i < registros.length; i++) {
      const rec = registros[i]
      const criadoMs = rec.getDateTime('created').string()
      const ultimaRaw = rec.get('ultima_interacao')
      const ultimaMs = ultimaRaw
        ? rec.getDateTime('ultima_interacao').string()
        : rec.getDateTime('updated').string()
      const captadoHa90 = criadoMs ? agora - new Date(criadoMs).getTime() >= noventa : false
      const semInteracao60 = ultimaMs ? agora - new Date(ultimaMs).getTime() >= sessenta : false

      const parada = String(rec.get('followup_parada') || '')
      const estadoFila = String(rec.get('estado_fila') || '')
      const motivoPerda = String(rec.get('motivo_perda') || '').toLowerCase()

      if (estadoFila === 'excluido') {
        excluidos.push({
          lead_id: rec.get('lead_id'),
          motivo: rec.get('motivo_exclusao') || 'excluido_da_fila',
        })
        continue
      }
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'parada_permanente_' + parada })
        continue
      }
      if (
        motivoPerda.indexOf('nao tenho interesse') !== -1 ||
        motivoPerda.indexOf('não tenho interesse') !== -1 ||
        motivoPerda.indexOf('objecao') !== -1 ||
        motivoPerda.indexOf('objeção') !== -1
      ) {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'objecao_do_titular' })
        continue
      }
      if (
        !temCnpj(rec) ||
        String(rec.get('estado_qualificacao') || '') !== 'qualificado' ||
        !captadoHa90 ||
        !semInteracao60
      ) {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'nao_elegivel_no_momento' })
        continue
      }
      elegiveis.push(rec.get('lead_id'))
    }

    // Marca os elegíveis como aprovados e registra a comprovação da base (v1.1).
    const agoraIso = new Date().toISOString()
    for (let i = 0; i < registros.length; i++) {
      const rec = registros[i]
      if (elegiveis.indexOf(String(rec.get('lead_id'))) === -1) continue
      let registro = rec.get('reativacao_registro')
      if (typeof registro === 'string') {
        try {
          registro = JSON.parse(registro)
        } catch (_) {
          registro = null
        }
      }
      if (!registro || typeof registro !== 'object') registro = {}
      registro.base = 'legitimo_interesse'
      registro.finalidade = 'reativacao_comercial'
      registro.versao = '1.1'
      registro.data_avaliacao = agoraIso
      registro.avaliado_por = operador
      rec.set('reativacao_registro', JSON.stringify(registro))
      rec.set('estado_fila', 'aprovado')
      $app.save(rec)
    }

    const lote = new Record($app.findCollectionByNameOrId('reativacao_lote'))
    lote.set('lote_id', loteId)
    lote.set('regra_versao', '1.1')
    lote.set(
      'criterio_aplicado',
      JSON.stringify({
        b4_201: 'prestador_com_cnpj + captado_90d + sem_interacao_60d',
        b4_202: 'base_legal_legitimo_interesse_v1.1',
      }),
    )
    lote.set('leads_incluidos', JSON.stringify(elegiveis))
    lote.set('leads_excluidos', JSON.stringify(excluidos))
    lote.set('total_incluidos', elegiveis.length)
    lote.set('total_excluidos', excluidos.length)
    lote.set('aprovado_por', operador)
    lote.set('aprovado_em', agoraIso)
    lote.set('estado', 'aprovado')
    lote.set('observacao', observacao)
    $app.save(lote)

    return e.json(201, {
      status: 'lote_aprovado',
      lote_id: loteId,
      total_incluidos: elegiveis.length,
      total_excluidos: excluidos.length,
      contato_disparado: false,
    })
  },
  $apis.requireAuth(),
)
