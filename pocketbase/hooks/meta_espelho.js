// F4 cd704a1c - Espelho Meta: origem/campanha/anúncio do Meta no CRM (SPEC-4-001 CA-4-101..104).
// POST /backend/v1/meta-espelho
// Body: { modo: 'prova'|'espelhar', janela_dias (default 30), operador }
// - modo 'prova': só valida acesso/conta/amostra (zero ingestão).
// - modo 'espelhar': lê anúncios da conta aprovada, cruza com leads por PREFIXO do nome
//   declarado (formulário trunca ~70 chars), grava meta_* com proveniência.
// - Idempotente: repetir não duplica (mesma proveniência = re-grava igual, sem efeito colateral).
// - Sem correspondência -> meta_status=sem_dado_meta (nunca zero). Divergência -> registra, não sobrescreve.
// - Falha de API -> pausa e registra lacuna (RN-4-104). Somente leitura no Meta.
// NOTA runtime Skip: tudo DENTRO do callback (escopo de módulo não visível ao handler).

routerAdd(
  'POST',
  '/backend/v1/meta-espelho',
  (e) => {
    const CONTA_APROVADA = 'act_629165959070277' // B4-101
    const body = e.requestInfo().body || {}
    const modo = String(body.modo || 'prova').trim()
    const operador = String(body.operador || 'sistema').trim()
    const janelaDias = Number(body.janela_dias || 30)

    const apiKeyBruta = $secrets.get('COMPOSIO_API')
    const apiKey = apiKeyBruta
      ? String(apiKeyBruta)
          .trim()
          .replace(/^["']+/g, '')
          .replace(/["']+$/g, '')
      : ''
    if (!apiKey) {
      return e.json(503, {
        status: 'pendente_configuracao',
        motivo: 'composio_api_key_ausente',
        prova_aprovada: false,
      })
    }
    const H = {
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'User-Agent': 'terceirizou-crm-fase4/1.0',
    }

    function executar(toolSlug, args, connectedAccountId, userId) {
      const payload = { arguments: args, connectedAccountId: connectedAccountId, user_id: userId }
      let r = null
      try {
        r = $http.send({
          url: 'https://backend.composio.dev/api/v3.1/tools/execute/' + toolSlug,
          method: 'POST',
          headers: H,
          body: JSON.stringify(payload),
          timeout: 25,
        })
      } catch (_) {
        r = null
      }
      if (!r || r.statusCode < 200 || r.statusCode >= 300 || !r.json) {
        return { ok: false, http: r ? r.statusCode : 'transport_error', data: null }
      }
      if (r.json.successful === false) {
        return { ok: false, http: r.statusCode, data: r.json.error || 'tool_failed' }
      }
      return {
        ok: true,
        http: r.statusCode,
        data: r.json.data !== undefined ? r.json.data : r.json,
      }
    }

    // --- conexão ativa ---
    let contas = null
    try {
      contas = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/connected_accounts?toolkit_slug=metaads',
        method: 'GET',
        headers: H,
        timeout: 20,
      })
    } catch (_) {
      contas = null
    }
    let conta = null
    if (contas && contas.json && contas.json.items) {
      for (let i = 0; i < contas.json.items.length; i++) {
        if (contas.json.items[i].status === 'ACTIVE') {
          conta = contas.json.items[i]
          break
        }
      }
    }
    if (!conta) {
      return e.json(502, {
        status: 'falha',
        etapa: 'connected_accounts',
        prova_aprovada: false,
        lacuna: 'nenhuma conta metaads ACTIVE no Composio',
      })
    }
    const connectedAccountId = conta.id

    // --- userId do dono (obrigatório no execute) ---
    let detalhe = null
    try {
      detalhe = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/connected_accounts/' + connectedAccountId,
        method: 'GET',
        headers: H,
        timeout: 20,
      })
    } catch (_) {
      detalhe = null
    }
    const userId = detalhe && detalhe.json ? detalhe.json.userId || detalhe.json.user_id : null
    if (!userId) {
      return e.json(502, {
        status: 'falha',
        etapa: 'user_id',
        prova_aprovada: false,
        lacuna: 'userId da conexão Composio indisponível',
      })
    }

    // --- conta aprovada acessível (B4-101) ---
    const provaContas = executar('METAADS_GET_AD_ACCOUNTS', {}, connectedAccountId, userId)
    let contaOk = false
    if (provaContas.ok && provaContas.data) {
      contaOk = JSON.stringify(provaContas.data).indexOf(CONTA_APROVADA) !== -1
    }
    if (!contaOk) {
      return e.json(502, {
        status: 'falha',
        etapa: 'conta_aprovada',
        prova_aprovada: false,
        lacuna: 'conta ' + CONTA_APROVADA + ' não acessível (RN-4-101: zero ingestão)',
      })
    }

    // --- anúncios da conta (leitura) ---
    const adsResp = executar(
      'METAADS_LIST_ADS',
      {
        ad_account_id: CONTA_APROVADA,
        limit: 100,
      },
      connectedAccountId,
      userId,
    )
    if (!adsResp.ok || !adsResp.data || !adsResp.data.data) {
      return e.json(502, {
        status: 'falha',
        etapa: 'list_ads',
        http: adsResp.http,
        prova_aprovada: false,
        lacuna: 'falha ao ler anúncios do Meta (pausa espelhamento — RN-4-104)',
      })
    }
    const ads = adsResp.data.data

    // --- adsets -> campanha (para proveniência completa) ---
    const adsetCampanha = {}
    const vistos = {}
    for (let i = 0; i < ads.length; i++) {
      const adsetId = ads[i].adset_id
      if (adsetId && !vistos[adsetId]) {
        vistos[adsetId] = true
        const r = executar(
          'METAADS_GET_OBJECT',
          {
            object_id: adsetId,
            fields: ['id', 'campaign_id'],
          },
          connectedAccountId,
          userId,
        )
        adsetCampanha[adsetId] = r.ok && r.data ? r.data.campaign_id : null
      }
    }

    // --- campanhas (nomes oficiais) ---
    const camsResp = executar(
      'METAADS_LIST_CAMPAIGNS',
      {
        ad_account_id: CONTA_APROVADA,
        limit: 50,
        fields: ['id', 'name', 'status'],
      },
      connectedAccountId,
      userId,
    )
    const campanhaNome = {}
    if (camsResp.ok && camsResp.data && camsResp.data.data) {
      for (let i = 0; i < camsResp.data.data.length; i++) {
        campanhaNome[camsResp.data.data[i].id] = camsResp.data.data[i].name
      }
    }

    const agora = new Date().toISOString()
    const hoje = new Date()
    const ini = new Date(hoje.getTime() - janelaDias * 24 * 3600 * 1000)
    const fmt = (d) => d.toISOString().slice(0, 10)
    const provenienciaBase = {
      fonte: 'meta_ads_via_composio',
      conta: CONTA_APROVADA,
      periodo: fmt(ini) + ' a ' + fmt(hoje),
      data_carga: agora,
      operador: operador,
      tipo_match: 'prefixo_nome_anuncio',
    }

    // --- modo PROVA: zero ingestão, só diagnóstico ---
    if (modo === 'prova') {
      return e.json(200, {
        status: 'prova_aprovada',
        connected_account_id: connectedAccountId,
        conta_aprovada: CONTA_APROVADA,
        anuncios_lidos: ads.length,
        adsets_mapeados: Object.keys(adsetCampanha).length,
        campanhas_conhecidas: Object.keys(campanhaNome).length,
        janela_dias: janelaDias,
        prova_aprovada: true,
        nota: 'acesso e amostra OK; nenhuma ingestão no modo prova',
      })
    }

    if (modo !== 'espelhar') {
      return e.json(400, { error: 'modo inválido. Valores: prova, espelhar' })
    }

    // --- modo ESPELHAR: cruza leads x anúncios por prefixo ---
    // índice: prefixo normalizado "ad NN - " -> anúncio do Meta
    function normalizar(s) {
      return String(s).trim().toLowerCase().replace(/\s+/g, ' ')
    }
    const indiceAds = []
    for (let i = 0; i < ads.length; i++) {
      const nome = normalizar(ads[i].name)
      const m = nome.match(/^ad\s*(\d{1,2})\s*-\s*/)
      if (m) {
        indiceAds.push({ prefixo: 'ad ' + m[1] + ' - ', ad: ads[i] })
      }
    }

    // leads alvo: leitura DIRETA do banco (sem self-call HTTP — sem dependência de header/token)
    const leadsAlvo = $app.findRecordsByFilter('leads', "origem = 'meta_ads'", '-created', 500, 0)

    let espelhados = 0
    let semDado = 0
    let divergentes = 0
    const detalhes = []

    for (let i = 0; i < leadsAlvo.length; i++) {
      const lead = leadsAlvo[i]
      const declarado = String(lead.get('anuncio_criativo') || '').trim()
      const registro = {
        lead_id: lead.get('lead_id'),
        declarado: declarado || null,
      }
      if (!declarado) {
        // lead meta_ads sem anúncio declarado: lacuna visível
        if (lead.get('meta_status') !== 'sem_dado_meta') {
          lead.set('meta_status', 'sem_dado_meta')
          lead.set(
            'meta_proveniencia',
            JSON.stringify(
              Object.assign({}, provenienciaBase, { nota: 'sem anúncio declarado no formulário' }),
            ),
          )
          $app.save(lead)
        }
        semDado++
        registro.resultado = 'sem_dado_meta'
        detalhes.push(registro)
        continue
      }
      const dec = normalizar(declarado)
      const m = dec.match(/^ad\s*(\d{1,2})\s*-\s*/)
      let achado = null
      if (m) {
        const pref = 'ad ' + m[1] + ' - '
        for (let j = 0; j < indiceAds.length; j++) {
          if (indiceAds[j].prefixo === pref && dec.indexOf(indiceAds[j].prefixo) === 0) {
            // match: declarado é prefixo (ou igual) do nome real do anúncio
            const nomeReal = normalizar(indiceAds[j].ad.name)
            if (nomeReal.indexOf(dec) === 0 || dec.indexOf(nomeReal) === 0) {
              achado = indiceAds[j].ad
              break
            }
          }
        }
      }
      if (!achado) {
        if (lead.get('meta_status') !== 'sem_dado_meta') {
          lead.set('meta_status', 'sem_dado_meta')
          lead.set(
            'meta_proveniencia',
            JSON.stringify(
              Object.assign({}, provenienciaBase, {
                nota: 'anúncio declarado não encontrado no Meta',
              }),
            ),
          )
          $app.save(lead)
        }
        semDado++
        registro.resultado = 'sem_dado_meta'
        detalhes.push(registro)
        continue
      }

      const adsetId = achado.adset_id
      const campanhaId = adsetCampanha[adsetId] || null
      const nomeCampanha = campanhaId ? campanhaNome[campanhaId] || null : null
      const truncado = normalizar(declarado) !== normalizar(achado.name)

      // divergência: campanha declarada difere da campanha real do anúncio (RN-4-103)
      const campDeclarada = normalizar(String(lead.get('campanha') || ''))
      let divergente = false
      if (campDeclarada && nomeCampanha) {
        const campReal = normalizar(nomeCampanha)
        // declarada truncada também: match por prefixo
        if (!(campReal.indexOf(campDeclarada) === 0 || campDeclarada.indexOf(campReal) === 0)) {
          divergente = true
        }
      }

      lead.set('meta_anuncio_id', achado.id)
      lead.set('meta_anuncio_nome', achado.name)
      lead.set('meta_campanha_id', campanhaId || '')
      lead.set('meta_campanha_nome', nomeCampanha || '')
      lead.set('meta_status', divergente ? 'divergente' : 'espelhado')
      lead.set(
        'meta_proveniencia',
        JSON.stringify(
          Object.assign({}, provenienciaBase, {
            match_por_prefixo: truncado,
            divergencia_campanha: divergente
              ? { declarada: lead.get('campanha'), real: nomeCampanha }
              : null,
          }),
        ),
      )
      $app.save(lead)

      if (divergente) divergentes++
      else espelhados++
      registro.resultado = divergente ? 'divergente' : 'espelhado'
      registro.meta_anuncio = achado.name
      registro.meta_campanha = nomeCampanha
      detalhes.push(registro)
    }

    return e.json(200, {
      status: 'espelhado',
      janela_dias: janelaDias,
      anuncios_no_meta: ads.length,
      leads_avaliados: leadsAlvo.length,
      espelhados: espelhados,
      sem_dado_meta: semDado,
      divergentes: divergentes,
      amostra_detalhes: detalhes.slice(0, 10),
    })
  },
  $apis.requireAuth(),
)
