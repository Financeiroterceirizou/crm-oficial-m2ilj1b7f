import React, { useState } from 'react'
import { ArrowUpDown, Search, User, Compass } from 'lucide-react'
import { DimensionVendaRow } from '@/services/vendas-service'

interface VendasDimensionTableProps {
  responsavelData: DimensionVendaRow[]
  canalData: DimensionVendaRow[]
  isLoading?: boolean
}

type TabType = 'responsavel' | 'canal'
type SortField = 'vendasValor' | 'vendasCount' | 'ticketMedio' | 'percentShare'

export const VendasDimensionTable: React.FC<VendasDimensionTableProps> = ({
  responsavelData,
  canalData,
  isLoading = false,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('responsavel')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('vendasValor')
  const [sortAsc, setSortAsc] = useState(false)

  const currentDataset = activeTab === 'responsavel' ? responsavelData : canalData

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(false)
    }
  }

  const filteredData = currentDataset
    .filter((row) => row.dimension.toLowerCase().includes(searchTerm.toLowerCase().trim()))
    .sort((a, b) => {
      const mult = sortAsc ? 1 : -1
      return (a[sortField] - b[sortField]) * mult
    })

  // Totais
  const totalValor = currentDataset.reduce((sum, r) => sum + r.vendasValor, 0)
  const totalCount = currentDataset.reduce((sum, r) => sum + r.vendasCount, 0)
  const totalTicket = totalCount > 0 ? Math.round(totalValor / totalCount) : 0

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Table Header & Tabs */}
      <div className="p-4 sm:p-5 border-b border-slate-200/80 bg-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                Relatório de Dimensão
              </span>
              <h2 className="text-base font-semibold text-slate-900">
                Vendas por Dimensão (Estilo GA4)
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Desempenho de receita consolidada por responsável comercial e por canal de aquisição
            </p>
          </div>

          {/* Dimension Tabs (Google Analytics style switcher) */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-medium self-start md:self-auto">
            <button
              onClick={() => setActiveTab('responsavel')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'responsavel'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <User className="w-3.5 h-3.5 text-blue-600" />
              <span>Por Responsável</span>
            </button>
            <button
              onClick={() => setActiveTab('canal')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'canal'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Compass className="w-3.5 h-3.5 text-amber-600" />
              <span>Por Canal de Origem</span>
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
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={`Pesquisar ${activeTab === 'responsavel' ? 'responsável...' : 'canal...'}`}
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="text-[11px]">
              Mostrando {filteredData.length} de {currentDataset.length} linhas
            </span>
          </div>
        </div>
      </div>

      {/* GA4 style Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-semibold select-none">
              <th className="py-3 px-4 w-12 text-slate-400">#</th>
              <th className="py-3 px-4 min-w-[220px]">
                <span>
                  {activeTab === 'responsavel' ? 'Responsável Comercial' : 'Canal de Origem'}
                </span>
              </th>
              <th
                onClick={() => handleSort('vendasValor')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Receita Fechada</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('vendasCount')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Vendas (Qtd)</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('ticketMedio')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Ticket Médio</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('percentShare')}
                className="py-3 px-4 text-left min-w-[180px] cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 font-semibold text-slate-700">
                  <span>% da Receita (Share)</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-slate-400">
                  Nenhum registro encontrado para "{searchTerm}".
                </td>
              </tr>
            ) : (
              filteredData.map((row, idx) => (
                <tr key={row.id} className="hover:bg-blue-50/40 transition-colors group">
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{idx + 1}</td>
                  <td className="py-3 px-4 font-medium text-slate-900">
                    <div className="flex items-center gap-2.5">
                      {/* Avatar para responsável */}
                      {activeTab === 'responsavel' && (
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold shrink-0 ${
                            row.avatarBg || 'bg-blue-600'
                          }`}
                        >
                          {row.initials || 'CO'}
                        </div>
                      )}
                      <div>
                        <div className="leading-tight">{row.dimension}</div>
                        {row.subdimension && (
                          <div className="text-[10px] text-slate-400 leading-tight mt-0.5">
                            {row.subdimension}
                          </div>
                        )}
                      </div>
                      {row.badgeColor && (
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-normal border ${row.badgeColor}`}
                        >
                          Ativo
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-slate-900 font-mono">
                    {row.vendasValorFormatted}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-700 font-mono">
                    {row.vendasCount}
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-slate-700 font-mono">
                    {row.ticketMedioFormatted}
                  </td>
                  <td className="py-3 px-4">
                    {/* Inline progress bar style GA4 table share */}
                    <div className="flex items-center gap-2.5">
                      <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200/50">
                        <div
                          className="bg-blue-600 h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(row.percentShare, 100)}%` }}
                        />
                      </div>
                      <span className="w-12 text-right font-mono text-[11px] font-medium text-slate-600">
                        {row.percentShare.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>

          {/* Table Totals Row */}
          <tfoot>
            <tr className="bg-slate-50 border-t-2 border-slate-200 font-semibold text-slate-900 text-xs">
              <td className="py-3 px-4 text-slate-400">—</td>
              <td className="py-3 px-4 uppercase tracking-wider text-[11px]">
                Total ({activeTab === 'responsavel' ? 'Equipe Comercial' : 'Canais'})
              </td>
              <td className="py-3 px-4 text-right font-mono text-blue-700">
                R${' '}
                {totalValor.toLocaleString('pt-BR', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </td>
              <td className="py-3 px-4 text-right font-mono">{totalCount}</td>
              <td className="py-3 px-4 text-right font-mono">
                R${' '}
                {totalTicket.toLocaleString('pt-BR', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </td>
              <td className="py-3 px-4 text-slate-500 text-[11px] font-mono">100,0% da receita</td>
            </tr>
          </tfoot>
        </table>
        {isLoading && (
          <div className="py-6 text-center text-xs text-slate-400 bg-white/70 backdrop-blur-xs flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
            <span>Atualizando métricas de vendas com dados reais...</span>
          </div>
        )}
      </div>
    </div>
  )
}
