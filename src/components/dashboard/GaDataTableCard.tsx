import React, { useState } from 'react'
import { ArrowUpDown, ChevronDown, Download, Filter, Search } from 'lucide-react'
import { ChannelDimensionRow } from '@/lib/dashboard-data'

interface GaDataTableCardProps {
  channelData: ChannelDimensionRow[]
  productData: ChannelDimensionRow[]
}

type TabType = 'channels' | 'products'
type SortField = 'vendas' | 'clientes' | 'conversao' | 'percentShare'

export const GaDataTableCard: React.FC<GaDataTableCardProps> = ({ channelData, productData }) => {
  const [activeTab, setActiveTab] = useState<TabType>('channels')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('vendas')
  const [sortAsc, setSortAsc] = useState(false)

  const currentDataset = activeTab === 'channels' ? channelData : productData

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

  // Totals
  const totalVendas = currentDataset.reduce((sum, r) => sum + r.vendas, 0)
  const totalClientes = currentDataset.reduce((sum, r) => sum + r.clientes, 0)

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Table Header & Tabs */}
      <div className="p-4 sm:p-5 border-b border-slate-200/80 bg-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Detalhamento
              </span>
              <h2 className="text-base font-semibold text-slate-900">
                Relatório de Dimensão e Métricas do Funil
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Desempenho cruzado por canal de aquisição e por linha de produto de BPO
            </p>
          </div>

          {/* Dimension Tabs (Google Analytics style switcher) */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-medium self-start md:self-auto">
            <button
              onClick={() => setActiveTab('channels')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'channels'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Primeiro grupo de canais do usuário
            </button>
            <button
              onClick={() => setActiveTab('products')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'products'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Linha de Produto & Serviço
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
              placeholder="Pesquisar dimensão..."
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
              <th className="py-3 px-4 min-w-[200px]">
                <div className="flex items-center gap-1.5">
                  <span>
                    {activeTab === 'channels' ? 'Origem / Canal padrão' : 'Nome do Serviço'}
                  </span>
                </div>
              </th>
              <th
                onClick={() => handleSort('vendas')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Vendas Totais</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('clientes')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Clientes</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('conversao')}
                className="py-3 px-4 text-right cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 justify-end font-semibold text-slate-700">
                  <span>Taxa de Conversão</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('percentShare')}
                className="py-3 px-4 text-left min-w-[170px] cursor-pointer hover:bg-slate-100 transition-colors"
              >
                <div className="inline-flex items-center gap-1 font-semibold text-slate-700">
                  <span>% do Total (Share)</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-slate-400">
                  Nenhuma dimensão encontrada para o termo "{searchTerm}".
                </td>
              </tr>
            ) : (
              filteredData.map((row, idx) => (
                <tr key={row.id} className="hover:bg-blue-50/40 transition-colors group">
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{idx + 1}</td>
                  <td className="py-3 px-4 font-medium text-slate-900">
                    <div className="flex items-center gap-2">
                      <span>{row.dimension}</span>
                      {row.badgeColor && (
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-normal ${row.badgeColor}`}
                        >
                          Ativo
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-slate-900 font-mono">
                    {row.vendasFormatted}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-700 font-mono">
                    {row.clientesFormatted}
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-blue-600 font-mono">
                    {row.conversaoFormatted}
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
                Total ({activeTab === 'channels' ? 'Canais' : 'Serviços'})
              </td>
              <td className="py-3 px-4 text-right font-mono text-blue-700">
                R${' '}
                {totalVendas.toLocaleString('pt-BR', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </td>
              <td className="py-3 px-4 text-right font-mono">
                {totalClientes.toLocaleString('pt-BR')}
              </td>
              <td className="py-3 px-4 text-right font-mono text-blue-700">
                {((totalClientes / (currentDataset.length ? totalClientes * 23 : 1)) * 100).toFixed(
                  2,
                )}
                %
              </td>
              <td className="py-3 px-4 text-slate-500 text-[11px] font-mono">100,0% do volume</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  )
}
