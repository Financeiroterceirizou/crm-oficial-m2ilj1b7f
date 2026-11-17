/* CRM Oficial — Relatório de Leads por Situação
   Responde à pergunta do champion (28/10/2026): dos leads que entraram, quantos estão
   qualificados, quantos aguardam aprovação, quantos estão sem segmento e quantos não
   qualificam — com o destino de cada um no Kanban.

   Regra v1.2:
     qualificado        -> entra no Kanban (deal criado automaticamente)
     pendente_revisao   -> fora do Kanban até aprovação humana
     nao_qualificado    -> nunca entra no Kanban; fica no histórico de leads
*/
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AlertCircle,
  CalendarDays,
  CheckCircle2,
  Clock,
  RefreshCw,
  Search,
  ShieldQuestion,
  XCircle,
} from 'lucide-react'
import pb from '@/lib/pocketbase/client'

type Lead = {
  id: string
  nome: string
  email: string
  telefone: string
  origem: string
  created: string
  estado_qualificacao: string
  motivo_decisao: string
  proxima_acao: string
  respostas: unknown
}

type Filtro = 'todos' | 'qualificado' | 'sem_segmento' | 'aguardando_aprovacao' | 'nao_qualificado'

function parseRespostas(value: unknown): Record<string, unknown> {
  if (!value) return {}
  if (typeof value === 'string') {
    try {
      const p = JSON.parse(value)
      return p && typeof p === 'object' ? (p as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  if (Array.isArray(value) && value.every((i) => typeof i === 'number')) {
    try {
      const txt = new TextDecoder('utf-8').decode(new Uint8Array(value as number[]))
      const p = JSON.parse(txt)
      return p && typeof p === 'object' ? (p as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  return typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function categoria(lead: Lead): Exclude<Filtro, 'todos'> {
  if (lead.estado_qualificacao === 'qualificado') return 'qualificado'
  if (lead.estado_qualificacao === 'nao_qualificado') return 'nao_qualificado'
  if (lead.proxima_acao === 'aprovar_segmento') return 'aguardando_aprovacao'
  return 'sem_segmento'
}

function formatDate(v: string) {
  if (!v) return '—'
  const d = new Date(v)
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString('pt-BR')
}

const RelatorioLeads = () => {
  const navigate = useNavigate()
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filtro, setFiltro] = useState<Filtro>('todos')
  const [busca, setBusca] = useState('')

  const carregar = async () => {
    setLoading(true)
    setError('')
    try {
      const lista = await pb.collection('leads').getFullList<Lead>({ sort: '-created' })
      setLeads(lista)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível carregar os leads.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void carregar()
  }, [])

  const totais = useMemo(() => {
    const base = { qualificado: 0, sem_segmento: 0, aguardando_aprovacao: 0, nao_qualificado: 0 }
    for (const l of leads) base[categoria(l)] += 1
    return base
  }, [leads])

  const listaFiltrada = useMemo(() => {
    const termo = busca.trim().toLowerCase()
    return leads.filter((l) => {
      if (filtro !== 'todos' && categoria(l) !== filtro) return false
      if (!termo) return true
      return [l.nome, l.email, l.telefone].join(' ').toLowerCase().includes(termo)
    })
  }, [leads, filtro, busca])

  const noMes = useMemo(() => {
    const agora = new Date()
    return leads.filter((l) => {
      const d = new Date(l.created)
      return (
        !Number.isNaN(d.getTime()) &&
        d.getMonth() === agora.getMonth() &&
        d.getFullYear() === agora.getFullYear()
      )
    })
  }, [leads])

  const cards: {
    id: Filtro
    titulo: string
    valor: number
    cor: string
    icone: React.ReactNode
    nota: string
  }[] = [
    {
      id: 'qualificado',
      titulo: 'Qualificados',
      valor: totais.qualificado,
      cor: 'text-emerald-600',
      icone: <CheckCircle2 className="w-4 h-4" />,
      nota: 'No Kanban (Novos leads)',
    },
    {
      id: 'aguardando_aprovacao',
      titulo: 'Aguardando aprovação',
      valor: totais.aguardando_aprovacao,
      cor: 'text-amber-600',
      icone: <ShieldQuestion className="w-4 h-4" />,
      nota: 'Fora do Kanban — depende de você',
    },
    {
      id: 'sem_segmento',
      titulo: 'Sem segmento',
      valor: totais.sem_segmento,
      cor: 'text-blue-600',
      icone: <Clock className="w-4 h-4" />,
      nota: 'Contato manual p/ descobrir',
    },
    {
      id: 'nao_qualificado',
      titulo: 'Não qualificam',
      valor: totais.nao_qualificado,
      cor: 'text-red-600',
      icone: <XCircle className="w-4 h-4" />,
      nota: 'Fora do Kanban — histórico mantido',
    },
  ]

  const rotulo = (l: Lead) => {
    const c = categoria(l)
    if (c === 'qualificado') return { txt: 'Qualificado', cls: 'bg-emerald-100 text-emerald-800' }
    if (c === 'nao_qualificado') return { txt: 'Não qualifica', cls: 'bg-red-100 text-red-800' }
    if (c === 'aguardando_aprovacao')
      return { txt: 'Aguardando aprovação', cls: 'bg-amber-100 text-amber-800' }
    return { txt: 'Sem segmento', cls: 'bg-blue-100 text-blue-800' }
  }

  return (
    <div className="space-y-6 p-4 sm:p-6 bg-[#f8fafc] min-h-screen">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Relatório de Leads</h1>
          <p className="text-sm text-slate-500 mt-1 max-w-3xl">
            Situação de cada lead que entrou, e o destino dele no Kanban. Regra v1.2: qualificado
            entra direto no quadro; sem segmento e aguardando aprovação ficam fora até decisão
            humana; não qualificado nunca entra, mas o histórico fica guardado.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => void carregar()}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md border border-slate-200 bg-white text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
          <button
            type="button"
            onClick={() => navigate('/segmentos')}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md bg-blue-600 text-white text-xs font-semibold"
          >
            Aprovar segmentos
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 text-red-800 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {cards.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setFiltro(filtro === c.id ? 'todos' : c.id)}
            className={`text-left bg-white rounded-xl border p-4 transition-colors ${
              filtro === c.id ? 'border-blue-500 ring-1 ring-blue-200' : 'border-slate-200'
            } hover:border-slate-300`}
          >
            <div className={`flex items-center gap-2 text-xs font-medium text-slate-500 ${c.cor}`}>
              {c.icone}
              <span className="text-slate-600">{c.titulo}</span>
            </div>
            <div className={`text-2xl font-bold mt-1 ${c.cor}`}>{c.valor}</div>
            <div className="text-[11px] text-slate-500 mt-0.5 leading-tight">{c.nota}</div>
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-2 sm:items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <CalendarDays className="w-4 h-4 text-slate-400" />
            {filtro === 'todos' ? 'Todos os leads' : cards.find((c) => c.id === filtro)?.titulo}
            <span className="text-xs font-normal text-slate-500">
              ({listaFiltrada.length} de {leads.length}) · {noMes.length} entraram neste mês
            </span>
          </div>
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              placeholder="Buscar nome, e-mail ou telefone"
              className="pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-md w-64"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Carregando...</div>
        ) : listaFiltrada.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">Nenhum lead neste filtro.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wide">
                <tr>
                  <th className="text-left px-4 py-2 font-semibold">Lead</th>
                  <th className="text-left px-4 py-2 font-semibold">Contato</th>
                  <th className="text-left px-4 py-2 font-semibold">Segmento declarado</th>
                  <th className="text-left px-4 py-2 font-semibold">Situação</th>
                  <th className="text-left px-4 py-2 font-semibold">Kanban</th>
                  <th className="text-left px-4 py-2 font-semibold">Captado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {listaFiltrada.map((l) => {
                  const r = rotulo(l)
                  const seg = String(parseRespostas(l.respostas).segmento || '').trim()
                  const c = categoria(l)
                  return (
                    <tr key={l.id} className="hover:bg-slate-50">
                      <td className="px-4 py-2 font-medium text-slate-800">{l.nome || '—'}</td>
                      <td className="px-4 py-2 text-slate-600">
                        {l.telefone || '—'}
                        <div className="text-[10px] text-slate-400">{l.email || ''}</div>
                      </td>
                      <td className="px-4 py-2 text-slate-600">
                        {seg || <span className="text-slate-400">não informado</span>}
                      </td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-0.5 rounded-full font-semibold ${r.cls}`}>
                          {r.txt}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        {c === 'qualificado' ? (
                          <span className="text-emerald-700 font-medium">Sim — Novos leads</span>
                        ) : (
                          <span className="text-slate-400">Fora do quadro</span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-slate-500">{formatDate(l.created)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default RelatorioLeads
