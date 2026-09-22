import React, { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, CircleAlert, Database, RefreshCw, Search } from 'lucide-react'
import pb from '@/lib/pocketbase/client'

type MetaStatus = 'espelhado' | 'sem_dado_meta' | 'divergente' | string

type MetaLead = {
  id: string
  lead_id: string
  nome: string
  email: string
  origem: string
  campanha: string
  anuncio_criativo: string
  meta_status: MetaStatus
  meta_campanha_nome: string
  meta_anuncio_nome: string
  meta_proveniencia: {
    fonte?: string
    periodo?: string
    data_carga?: string
    tipo_match?: string
    match_por_prefixo?: boolean
  } | null
}

function parseProveniencia(value: unknown): MetaLead['meta_proveniencia'] {
  if (!value) return null
  if (typeof value === 'object') return value as MetaLead['meta_proveniencia']
  if (typeof value === 'string') {
    try {
      return JSON.parse(value) as MetaLead['meta_proveniencia']
    } catch {
      return null
    }
  }
  return null
}

function statusLabel(status: string) {
  if (status === 'espelhado') return 'Espelhado'
  if (status === 'sem_dado_meta') return 'Sem dado Meta'
  if (status === 'divergente') return 'Divergente'
  return status || 'Sem classificação'
}

function statusClass(status: string) {
  if (status === 'espelhado') return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  if (status === 'sem_dado_meta') return 'bg-slate-100 text-slate-600 border-slate-200'
  return 'bg-amber-50 text-amber-700 border-amber-200'
}

export const MetaLeadsRealCard: React.FC = () => {
  const [leads, setLeads] = useState<MetaLead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<
    'todos' | 'espelhado' | 'sem_dado_meta' | 'divergente'
  >('todos')

  const loadLeads = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await pb.collection('leads').getList(1, 200, {
        filter: 'origem = "meta_ads"',
        sort: '-updated',
      })
      setLeads(
        response.items.map((item) => ({
          id: item.id,
          lead_id: item.lead_id || item.id,
          nome: item.nome || 'Sem nome',
          email: item.email || '—',
          origem: item.origem || '—',
          campanha: item.campanha || '—',
          anuncio_criativo: item.anuncio_criativo || '—',
          meta_status: item.meta_status || 'sem_dado_meta',
          meta_campanha_nome: item.meta_campanha_nome || '—',
          meta_anuncio_nome: item.meta_anuncio_nome || '—',
          meta_proveniencia: parseProveniencia(item.meta_proveniencia),
        })),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível carregar os leads reais.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLeads()
  }, [])

  const counts = useMemo(
    () => ({
      total: leads.length,
      espelhado: leads.filter((lead) => lead.meta_status === 'espelhado').length,
      semDado: leads.filter((lead) => lead.meta_status === 'sem_dado_meta').length,
      divergente: leads.filter((lead) => lead.meta_status === 'divergente').length,
    }),
    [leads],
  )

  const filteredLeads = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    return leads.filter((lead) => {
      const matchesStatus = statusFilter === 'todos' || lead.meta_status === statusFilter
      const haystack = [lead.nome, lead.email, lead.meta_campanha_nome, lead.meta_anuncio_nome]
        .join(' ')
        .toLowerCase()
      return matchesStatus && (!term || haystack.includes(term))
    })
  }, [leads, searchTerm, statusFilter])

  return (
    <section
      aria-label="Leads reais do Meta"
      className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden"
    >
      <div className="p-4 sm:p-5 border-b border-slate-200/80">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-blue-600" />
              <h2 className="text-base font-semibold text-slate-900">Leads reais — espelho Meta</h2>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                CRM ao vivo
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Campanha e anúncio oficiais do Meta, sem sobrescrever os dados originais do lead.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void loadLeads()}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Atualizar leads reais
          </button>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mt-4">
          {[
            ['Total Meta', counts.total, 'todos'],
            ['Espelhados', counts.espelhado, 'espelhado'],
            ['Sem dado Meta', counts.semDado, 'sem_dado_meta'],
            ['Divergentes', counts.divergente, 'divergente'],
          ].map(([label, value, filter]) => (
            <button
              type="button"
              key={label as string}
              onClick={() => setStatusFilter(filter as typeof statusFilter)}
              className={`text-left rounded-lg border p-3 transition-colors ${statusFilter === filter ? 'border-blue-300 bg-blue-50' : 'border-slate-200 bg-slate-50/60 hover:bg-slate-50'}`}
            >
              <span className="block text-[10px] uppercase tracking-wide text-slate-500">
                {label}
              </span>
              <strong className="block mt-1 text-xl text-slate-900">{value}</strong>
            </button>
          ))}
        </div>

        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1 max-w-md">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Pesquisar lead, campanha ou anúncio..."
              className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-blue-500"
            />
          </div>
          <span className="self-center text-[11px] text-slate-500">
            Mostrando {filteredLeads.length} de {leads.length}
          </span>
        </div>
      </div>

      {error && (
        <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-xs text-red-700 flex items-center gap-2">
          <CircleAlert className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-semibold">
              <th className="py-3 px-4 min-w-[170px]">Lead</th>
              <th className="py-3 px-4 min-w-[260px]">Campanha no Meta</th>
              <th className="py-3 px-4 min-w-[320px]">Anúncio no Meta</th>
              <th className="py-3 px-4 min-w-[130px]">Status</th>
              <th className="py-3 px-4 min-w-[220px]">Proveniência</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={5} className="py-8 px-4 text-center text-slate-400">
                  Carregando dados reais do CRM...
                </td>
              </tr>
            )}
            {!loading && filteredLeads.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 px-4 text-center text-slate-400">
                  Nenhum lead Meta encontrado.
                </td>
              </tr>
            )}
            {!loading &&
              filteredLeads.slice(0, 50).map((lead) => {
                const provenance = lead.meta_proveniencia
                return (
                  <tr key={lead.id} className="hover:bg-blue-50/40 align-top">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{lead.nome}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">{lead.email}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-700">{lead.meta_campanha_nome}</td>
                    <td className="py-3 px-4">
                      <div className="text-slate-700">{lead.meta_anuncio_nome}</div>
                      <div className="text-[10px] text-slate-400 mt-1">
                        Original: {lead.anuncio_criativo}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[10px] font-semibold ${statusClass(lead.meta_status)}`}
                      >
                        {lead.meta_status === 'espelhado' && <CheckCircle2 className="w-3 h-3" />}
                        {statusLabel(lead.meta_status)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-[11px] text-slate-500">
                      <div>{provenance?.fonte || '—'}</div>
                      <div>{provenance?.periodo || 'Período não informado'}</div>
                      <div>
                        {provenance?.data_carga
                          ? new Date(provenance.data_carga).toLocaleString('pt-BR')
                          : '—'}
                      </div>
                      {provenance?.match_por_prefixo && (
                        <div className="text-blue-600">Match por prefixo</div>
                      )}
                    </td>
                  </tr>
                )
              })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
