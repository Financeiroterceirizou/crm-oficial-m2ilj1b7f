// pocketbase/hooks/fila_reativacao.js
// F4 5ef4b7cd: fila de reativação assistida (SPEC-4-002 realinhada 16/10/2026).
// GET /backend/v1/fila-reativacao
//
// Aplica as 8 condições da base legal (registro v1.1) + critério B4-201:
//   1. contato fornecido voluntariamente (origem registrada)
//   2. prestador de serviço com CNPJ (B4-201)
//   3. captação >= 90 dias E sem interação >= 60 dias (B4-201)
//   4. sem descadastro/nao_contatar (permanente)
//   5. sem bounce permanente (followup_parada = 'bounce' — migration 0011)
//   6. sem objeção (incl. "não tenho interesse agora" — decisão 16/10)
//   7. sem dado sensível no tratamento (fila usa nome/email/telefone apenas)
//   8. registro de base legal gerado na montagem (reativacao_registro)
// Exclusões: estado_fila = 'excluido' (RN-4-202) sai da fila com motivo registrado.
// RLS herdada: exige autenticação (401 sem) — RN-4-205.
// Vazio ≠ zero: lead sem dado exibe estado explícito (RN-4-204).

routerAdd(
  'GET',
  '/backend/v1/fila-reativacao',
  (e) => {
    const limitRaw = Number(e.request.url.query().get('perPage') || 200)
    const limit = Number.isFinite(limitRaw) ? Math.min(Math.max(Math.trunc(limitRaw), 1), 500) : 200

    const registros = $app.findRecordsByFilter('leads', '', '-created', limit, 0)
    const agora = new Date()
    const noventaDias = 90 * 24 * 60 * 60 * 1000
    const sessentaDias = 60 * 24 * 60 * 60 * 1000

    const temCnpj = (rec) => {
      let resp = rec.get('respostas')
      try {
        // Normaliza qualquer formato do JSVM (objeto goja, Map, string) para dict puro.
        if (typeof resp !== 'string') resp = JSON.stringify(resp)
        resp = JSON.parse(resp)
      } catch (_) {
        return false
      }
      if (!resp || typeof resp !== 'object') return false
      const chaves = Object.keys(resp)
      for (let c = 0; c < chaves.length; c++) {
        if (String(chaves[c]).toLowerCase().indexOf('cnpj') !== -1) {
          const valor = String(resp[chaves[c]] || '').trim()
          if (valor !== '' && valor !== '-' && valor !== 'null') return true
        }
      }
      return false
    }

    const temObjecao = (rec) => {
      // Descadastro/nao_contatar (F3) e bounce (0011) são paradas permanentes.
      const parada = String(rec.get('followup_parada') || '')
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') return true
      // Objeção registrada no motivo de perda (decisão 16/10: "não tenho interesse agora").
      const motivo = String(rec.get('motivo_perda') || '').toLowerCase()
      if (
        motivo.indexOf('nao tenho interesse') !== -1 ||
        motivo.indexOf('não tenho interesse') !== -1 ||
        motivo.indexOf('objecao') !== -1 ||
        motivo.indexOf('objeção') !== -1
      ) {
        return true
      }
      return false
    }

    const elegiveis = []
    const excluidos = []
    const semDado = []

    for (let i = 0; i < registros.length; i++) {
      const rec = registros[i]
      const criado = rec.getDateTime('created')
      const ultima = rec.get('ultima_interacao')
        ? rec.getDateTime('ultima_interacao')
        : rec.getDateTime('updated')

      const captadoMs = criado ? new Date(criado.string()).getTime() : 0
      const interacaoMs = ultima ? new Date(ultima.string()).getTime() : 0
      const captadoHa90 = captadoMs > 0 && agora.getTime() - captadoMs >= noventaDias
      const semInteracao60 = interacaoMs > 0 && agora.getTime() - interacaoMs >= sessentaDias

      const cnpj = temCnpj(rec)
      const qualificado = String(rec.get('estado_qualificacao') || '') === 'qualificado'
      const parada = String(rec.get('followup_parada') || '')
      const estadoFila = String(rec.get('estado_fila') || '')

      // Condição 4/6: exclusões permanentes — sai da fila com motivo (RN-4-202).
      if (estadoFila === 'excluido') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: rec.get('motivo_exclusao') || 'excluido_da_fila',
        })
        continue
      }
      // Já aprovado em lote anterior — não reentra (idempotência de lote).
      if (estadoFila === 'aprovado') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'aprovado_em_lote',
        })
        continue
      }
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'parada_permanente_' + parada,
        })
        continue
      }
      if (temObjecao(rec)) {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'objecao_do_titular',
        })
        continue
      }

      // Condições 2 e 3: sem CNPJ ou janelas não cumpridas — não elegível ainda.
      if (!cnpj || !qualificado || !captadoHa90 || !semInteracao60) {
        semDado.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          origem: rec.get('origem'),
          estado_qualificacao: rec.get('estado_qualificacao') || 'sem_dado',
          cnpj_presente: cnpj ? 'sim' : 'nao',
          captado_ha_90d: captadoHa90 ? 'sim' : 'nao',
          sem_interacao_60d: semInteracao60 ? 'sim' : 'nao',
        })
        continue
      }

      // Todas as condições atendidas — elegível com registro de base legal (condição 8).
      elegiveis.push({
        id: rec.get('id'),
        lead_id: rec.get('lead_id'),
        nome: rec.get('nome'),
        email: rec.get('email'),
        telefone: rec.get('telefone'),
        origem: rec.get('origem'),
        motivo_perda: rec.get('motivo_perda') || 'sem_motivo_registrado',
        ultima_interacao: ultima ? ultima.string() : '',
        captado_em: criado ? criado.string() : '',
        base_legal: 'legitimo_interesse',
        finalidade: 'reativacao_comercial',
        registro_versao: '1.1',
      })
    }

    return e.json(200, {
      total_elegiveis: elegiveis.length,
      total_excluidos: excluidos.length,
      total_nao_elegiveis: semDado.length,
      criterio: {
        b4_201:
          'prestador_com_cnpj + captado_90d + sem_interacao_60d + motivo_perda_explcito_ou_ausente',
        b4_202: 'base_legal_legitimo_interesse_v1.1',
        fonte: 'SPEC-4-002 realinhada 16/10/2026 + 06_notas/registro-base-legal-b4-202.md v1.1',
      },
      elegiveis,
      excluidos,
      nao_elegiveis: semDado,
    })
  },
  $apis.requireAuth(),
)
