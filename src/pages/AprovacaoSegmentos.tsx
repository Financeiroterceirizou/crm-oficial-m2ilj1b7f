/* CRM Oficial — Aprovação de Segmento (regra v1.2, decisão do champion 28/10/2026)
   Uma tela para resolver os dois casos que dependem de humano:
     1. segmento fora da carteira -> aprovar ou não qualificar;
     2. lead sem segmento -> preencher o segmento oficial (contato manual).
   Nada aqui dispara contato automático: o contato é humano, a tela só registra. */
import { useEffect, useMemo, useState } from 'react'
import {
  AlertCircle,
  CheckCircle2,
  Filter,
  HelpCircle,
  Phone,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import pb from '@/lib/pocketbase/client'

// O app funciona sem login (mesmo padrão de pipeline/vendas); as decisões desta
// tela ficam registradas no histórico do lead com este operador fixo.
const OPERADOR_PADRAO = 'equipe-comercial (sem login)'

type Lead = {
  id: string
  lead_id: string
  nome: string
  email: string
  telefone: string
  origem: string
  created: string
  estado_qualificacao: string
  motivo_decisao: string
  proxima_acao: string
  score: number | null
  respostas: unknown
}

const SEGMENTOS = [
  'Escritório de Arquitetura',
  'Escritório de Advocacia',
  'Clínica de Saúde e Estética',
  'Agência de Marketing',
  'Casa de Repouso (ILPI)',
  'Associação de Proteção Veicular',
  'Vistoria Veicular',
  'Consultoria em Geral',
  'Outro Segmento de Prestação de Serviço',
  'Segmento que não atendemos',
]

function parseRespostas(value: unknown): Record<string, unknown> {
  if (!value) return {}
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  if (Array.isArray(value) && value.every((item) => typeof item === 'number')) {
    try {
      const texto = new TextDecoder('utf-8').decode(new Uint8Array(value as number[]))
      const parsed = JSON.parse(texto)
      return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  return typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function formatDate(value: string) {
  if (!value) return '—'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString('pt-BR')
}

type Aba = 'sem_segmento' | 'fora_carteira'

const AprovacaoSegmentos = () => {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [aba, setAba] = useState<Aba>('sem_segmento')
  const [busca, setBusca] = useState('')
  const [salvando, setSalvando] = useState<string | null>(null)
  const [escolhas, setEscolhas] = useState<Record<string, string>>({})
  const [observacoes, setObservacoes] = useState<Record<string, string>>({})

  const carregar = async () => {
    setLoading(true)
    setError('')
    try {
      const lista = await pb.collection('leads').getFullList<Lead>({
        filter:
          'proxima_acao = "solicitar_complemento_segmento" || proxima_acao = "aprovar_segmento"',
        sort: '-created',
      })
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

  const porAba = useMemo(() => {
    const semSegmento = leads.filter((l) => l.proxima_acao === 'solicitar_complemento_segmento')
    const foraCarteira = leads.filter((l) => l.proxima_acao === 'aprovar_segmento')
    const termo = busca.trim().toLowerCase()
    const filtrar = (arr: Lead[]) =>
      !termo
        ? arr
        : arr.filter((l) => [l.nome, l.email, l.telefone].join(' ').toLowerCase().includes(termo))
    return { sem_segmento: filtrar(semSegmento), fora_carteira: filtrar(foraCarteira) }
  }, [leads, busca])

  const lista = porAba[aba]

  const executar = async (lead: Lead, acao: string) => {
    const segmento = escolhas[lead.id] || ''
    if (acao === 'definir_segmento' && !segmento) {
      setMessage(`Escolha o segmento de ${lead.nome} antes de salvar.`)
      return
    }
    setSalvando(lead.id)
    setMessage('')
    try {
      const resp = await fetch(`${pb.baseUrl}/backend/v1/segmentos/definir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_id: lead.id,
          acao,
          segmento,
          operador: OPERADOR_PADRAO,
          observacao: observacoes[lead.id] || '',
        }),
      })
      const resultado = await resp.json()
      if (!resp.ok) {
        setMessage(resultado.error || `Falha ao registrar (${resp.status}).`)
        return
      }
      setMessage(`${lead.nome}: ${resultado.estado} — ${resultado.motivo || ''}`.trim())
      // o lead só sai da fila quando deixou de estar pendente; se continuar
      // pendente (ex.: salvou "outro segmento"), ele fica com o estado novo.
      const continuaPendente =
        resultado.proxima_acao === 'solicitar_complemento_segmento' ||
        resultado.proxima_acao === 'aprovar_segmento'
      setLeads((prev) =>
        continuaPendente
          ? prev.map((l) =>
              l.id === lead.id
                ? {
                    ...l,
                    estado_qualificacao: resultado.estado,
                    motivo_decisao: resultado.motivo,
                    proxima_acao: resultado.proxima_acao,
                  }
                : l,
            )
          : prev.filter((l) => l.id !== lead.id),
      )
      setEscolhas((prev) => {
        const copia = { ...prev }
        delete copia[lead.id]
        return copia
      })
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Erro de conexão.')
    } finally {
      setSalvando(null)
    }
  }

  const totalSemSegmento = leads.filter(
    (l) => l.proxima_acao === 'solicitar_complemento_segmento',
  ).length
  const totalFora = leads.filter((l) => l.proxima_acao === 'aprovar_segmento').length

  return (
    <div className="space-y-6 p-4 sm:p-6 bg-[#f8fafc] min-h-screen">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Aprovação de Segmento</h1>
          <p className="text-sm text-slate-500 mt-1 max-w-3xl">
            Regra v1.2: oito segmentos oficiais qualificam direto. Aqui ficam os dois casos que
            dependem de decisão humana — o lead sem segmento (o formulário não perguntava) e o lead
            com segmento fora da carteira. Nenhum contato parte do sistema: você fala com o lead e
            registra o segmento.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void carregar()}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-md border border-slate-200 bg-white text-xs font-medium text-slate-600 hover:bg-slate-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 text-red-800 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}
      {message && (
        <div className="p-3 rounded-lg bg-green-50 text-green-800 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" /> {message}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          type="button"
          onClick={() => setAba('sem_segmento')}
          className={`text-left bg-white rounded-lg shadow p-4 border-2 transition-colors ${
            aba === 'sem_segmento' ? 'border-blue-500' : 'border-transparent'
          }`}
        >
          <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
            <HelpCircle className="w-4 h-4" /> Sem segmento — pedir complemento
          </div>
          <div className="text-2xl font-bold text-blue-600 mt-1">{totalSemSegmento}</div>
          <div className="text-[11px] text-slate-500 mt-1">
            O formulário de Cadastro não pergunta o segmento.
          </div>
        </button>
        <button
          type="button"
          onClick={() => setAba('fora_carteira')}
          className={`text-left bg-white rounded-lg shadow p-4 border-2 transition-colors ${
            aba === 'fora_carteira' ? 'border-amber-500' : 'border-transparent'
          }`}
        >
          <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
            <ShieldCheck className="w-4 h-4" /> Fora da carteira — aguardando aval
          </div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{totalFora}</div>
          <div className="text-[11px] text-slate-500 mt-1">
            Declarou outro segmento ou um valor não reconhecido.
          </div>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-2 sm:items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <Filter className="w-4 h-4 text-slate-400" />
            {aba === 'sem_segmento' ? 'Leads sem segmento' : 'Leads fora da carteira'}
            <span className="text-xs font-normal text-slate-500">({lista.length})</span>
          </div>
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={busca}
              onChange={(event) => setBusca(event.target.value)}
              placeholder="Buscar nome, e-mail ou telefone"
              className="pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-md w-64"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Carregando leads...</div>
        ) : lista.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">Nada pendente nesta aba.</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {lista.map((lead) => {
              const respostas = parseRespostas(lead.respostas)
              const declarado = String(respostas.segmento || '').trim()
              const ocupado = salvando === lead.id
              return (
                <div key={lead.id} className="p-4">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-semibold text-sm text-slate-900 truncate">
                        {lead.nome || '(sem nome)'}
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                        <span className="inline-flex items-center gap-1">
                          <Phone className="w-3 h-3" /> {lead.telefone || '—'}
                        </span>
                        <span>{lead.email || '—'}</span>
                        <span>origem: {lead.origem || '—'}</span>
                        <span>captado: {formatDate(lead.created)}</span>
                      </div>
                      <div className="mt-1.5 text-[11px]">
                        {declarado ? (
                          <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-medium">
                            declarou: {declarado}
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                            sem segmento informado
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-2 shrink-0 w-full lg:w-auto">
                      <select
                        value={escolhas[lead.id] || ''}
                        onChange={(event) =>
                          setEscolhas((prev) => ({ ...prev, [lead.id]: event.target.value }))
                        }
                        className="px-2 py-2 text-xs bg-white border border-slate-200 rounded-md sm:w-64"
                      >
                        <option value="">Segmento oficial…</option>
                        {SEGMENTOS.map((s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        onClick={() => void executar(lead, 'definir_segmento')}
                        disabled={ocupado}
                        className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-md bg-blue-600 text-white text-xs font-semibold disabled:opacity-50"
                      >
                        <Save className="w-3.5 h-3.5" />
                        Salvar segmento
                      </button>
                      {aba === 'fora_carteira' && (
                        <button
                          type="button"
                          onClick={() => void executar(lead, 'aprovar')}
                          disabled={ocupado}
                          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-md bg-emerald-600 text-white text-xs font-semibold disabled:opacity-50"
                          title="Aprova o lead sem trocar o segmento declarado"
                        >
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Aprovar
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => void executar(lead, 'nao_qualificar')}
                        disabled={ocupado}
                        className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-md border border-slate-200 text-slate-600 text-xs font-semibold disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        Não qualifica
                      </button>
                    </div>
                  </div>

                  <input
                    value={observacoes[lead.id] || ''}
                    onChange={(event) =>
                      setObservacoes((prev) => ({ ...prev, [lead.id]: event.target.value }))
                    }
                    placeholder="Observação do contato (opcional) — ex: cliente informou por WhatsApp em 28/10"
                    className="mt-2 w-full px-3 py-1.5 text-[11px] bg-slate-50 border border-slate-200 rounded-md"
                  />
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default AprovacaoSegmentos
