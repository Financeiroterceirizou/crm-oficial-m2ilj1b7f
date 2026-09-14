    # Carrega leads existentes do CRM (para dedup) — com paginação (fix 2026-09-14):
    # perPage=300 fixo deixava de enxergar leads além do primeiro lote; com ~320+
    # registros o dedup falhava e lead existente era RE-CRIADO (duplicado no CRM).
    leads_existentes = []
    page = 1
    while True:
        st, dados = api('GET', f'/api/collections/leads/records?perPage=200&page={page}')
        if st != 200:
            raise RuntimeError(f'Falha ao buscar leads (página {page}): {st} {dados}')
        leads_existentes.extend(dados['items'])
        if page * 200 >= dados.get('totalItems', 0) or not dados['items']:
            break
        page += 1