import React, { useState } from 'react'
import {
  ArrowUpDown,
  Calendar,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  DollarSign,
  Filter,
  Search,
  Tag,
} from 'lucide-react'
import { DealRecord, getOwnerDetails } from '@/services/deals'
import { getChannelBadgeStyle } from '@/lib/pipeline-data'

interface VendasDealsTableProps {
  deals: DealRecord[]
  isLoading?: boolean
  stageView: 'won_only' | 'all'
  onStageViewChange: (view: 'won_only' | 'all') => void
}

type SortField = 'valor' | 'data' | 'nome' | 'cliente'

export const VendasDealsTable: React.FC<VendasDealsTableProps> = ({
  deals,
  isLoading = false,
  stageView,
  onStageViewChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('valor')
  const [sortAsc, setSortAsc] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(false)
    }
  }

  const getDateValue = (d: DealRecord): number => {
    const raw = d.data_fechamento || d.updated || d.created
    if (!raw) return 0
    return new Date(raw).getTime()
  }

  const filteredDeals = deals
    .filter((d) => {
      const q = searchTerm.toLowerCase().trim()
      if (!q) return true
      return (
        d.nome?.toLowerCase().includes(q) ||
        d.cliente?.toLowerCase().includes(q) ||
        d.responsavel?.toLowerCase().includes(q) ||
        d.canal?.toLowerCase().includes(q)
      )
    })
    .sort((a, b) => {
      const mult = sortAsc ? 1 : -1
      if (sortField === 'valor') {
        return ((a.valor || 0) - (b.valor || 0)) * mult
      }
      if (sortField === 'data') {
        return (getDateValue(a) - getDateValue(b)) * mult
      }
      if (sortField === 'nome') {
        return (a.nome || '').localeCompare(b.nome || '') * mult
      }
      if (sortField === 'cliente') {
        return (a.cliente || '').localeCompare(b.cliente || '') * mult
      }
      return 0
    })

  const totalPages = Math.max(1, Math.ceil(filteredDeals.length / pageSize))
  const paginatedDeals = filteredDeals.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const formatCurrency = (val?: number) =>
    `R$ ${(val || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  const formatDate = (raw?: string) => {
    if (!raw) return '—'
    const d = new Date(raw)
    return isNaN(d.getTime())
      ? '—'
      : d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  const parseTags = (raw?: string[] | string): string[] => {
    if (Array.isArray(raw)) return raw
    if (typeof raw === 'string' && raw.trim()) {
      try {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) return parsed
      } catch {
        return [raw]
      }
    }
    return []
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Table Header */}
      <div className="p-4 sm:p-5 border-b border-slate-200/80 bg-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                Detalhamento dos Negócios
              </span>
              <h2 className="text-base font-semibold text-slate-900">
                Lista de Vendas & Oportunidades
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Negócios cadastrados com valores, responsáveis comerciais e canais de atração
            </p>
          </div>

          {/* Toggle entre Fechados (Ganhos) e Todas as Etapas */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-medium self-start md:self-auto">
            <button
              onClick={() => {
                onStageViewChange('won_only')
                setCurrentPage(1)
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                stageView === 'won_only'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Apenas Fechados (Ganhos)</span>
            </button>
            <button
              onClick={() => {
                onStageViewChange('all')
                setCurrentPage(1)
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                stageView === 'all'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>Todas as etapas ({deals.length})</span>
            </button>
          </div>
        </div>

        {/* Filter / Search Row */}
        <div className="mt-4 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
              placeholder="Pesquisar por negócio, cliente, responsável..."
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="text-[11px]">
              Exibindo {paginatedDeals.length} de {filteredDeals.length} negócios
            </span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-semibold select-none">
              <th className="py-3 px-4 w-12 text-slate-400">#</th>
              <th
                onClick={() => handleSort('nome')}
                className="py-3 px-4 min-w-[200px] cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 font-semibold text-slate-700">
                  <span>Negócio / Empresa</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('cliente')}
                className="py-3 px-4 min-w-[160px] cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 font-semibold text-slate-700">
                  <span>Cliente / Contato</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('valor')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Valor do Contrato</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 min-w-[170px]">Responsável</th>
              <th className="py-3 px-4 min-w-[130px]">Canal</th>
              <th className="py-3 px-4 min-w-[110px]">Etapa</th>
              <th
                onClick={() => handleSort('data')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Fechamento / Data</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {paginatedDeals.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-10 text-slate-400">
                  Nenhum negócio encontrado com os filtros selecionados.
                </td>
              </tr>
            ) : (
              paginatedDeals.map((deal, idx) => {
                const owner = getOwnerDetails(deal.responsavel)
                const tags = parseTags(deal.tags)
                const isWon = deal.etapa === 'Fechado (ganho)'
                const indexNum = (currentPage - 1) * pageSize + idx + 1

                return (
                  <tr key={deal.id} className="hover:bg-blue-50/40 transition-colors group">
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{indexNum}</td>

                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{deal.nome}</div>
                      {tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {tags.slice(0, 2).map((tag, tIdx) => (
                            <span
                              key={tIdx}
                              className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded border border-slate-200"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>

                    <td className="py-3 px-4 text-slate-700 font-medium">{deal.cliente || '—'}</td>

                    <td className="py-3 px-4 text-right font-semibold text-slate-900 font-mono">
                      {formatCurrency(deal.valor)}
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold shrink-0 ${owner.avatarBg}`}
                        >
                          {owner.initials}
                        </div>
                        <span className="text-xs text-slate-800 truncate max-w-[130px]">
                          {owner.name}
                        </span>
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${getChannelBadgeStyle(
                          deal.canal || 'Meta Ads',
                        )}`}
                      >
                        {deal.canal || 'Meta Ads'}
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold ${
                          isWon
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                            : 'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}
                      >
                        {isWon && <CheckCircle2 className="w-3 h-3 text-emerald-700" />}
                        <span>{deal.etapa}</span>
                      </span>
                    </td>

                    <td className="py-3 px-4 text-right text-slate-600 font-mono text-[11px]">
                      {formatDate(deal.data_fechamento || deal.updated || deal.created)}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="p-3 border-t border-slate-200/80 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
          <div>
            Página <span className="font-semibold text-slate-900">{currentPage}</span> de{' '}
            <span className="font-semibold text-slate-900">{totalPages}</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
