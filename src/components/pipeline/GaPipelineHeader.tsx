import React, { useState } from 'react'
import {
  Calendar as CalendarIcon,
  Check,
  ChevronDown,
  Download,
  Filter,
  Kanban,
  Menu,
  Plus,
  RefreshCw,
  Search,
  Share2,
} from 'lucide-react'
import { DatePeriod, PERIOD_LABELS } from '@/lib/dashboard-data'

interface GaPipelineHeaderProps {
  period: DatePeriod
  onChangePeriod: (period: DatePeriod) => void
  onOpenMobileMenu: () => void
  searchQuery: string
  onSearchChange: (q: string) => void
  channelFilter: string
  onChannelFilterChange: (channel: string) => void
  channelsList: string[]
  onNewDealClick?: () => void
  isRefreshing?: boolean
  onRefresh?: () => void
}

export const GaPipelineHeader: React.FC<GaPipelineHeaderProps> = ({
  period,
  onChangePeriod,
  onOpenMobileMenu,
  searchQuery,
  onSearchChange,
  channelFilter,
  onChannelFilterChange,
  channelsList,
  onNewDealClick,
  isRefreshing,
  onRefresh,
}) => {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [filterOpen, setFilterOpen] = useState(false)

  const periods: DatePeriod[] = ['today', '7d', '28d', '90d', '12m']

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      {/* Top Bar */}
      <div className="px-4 sm:px-6 py-2.5 flex items-center justify-between gap-3 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileMenu}
            className="lg:hidden p-1.5 -ml-1 text-slate-600 hover:text-slate-900 rounded-md hover:bg-slate-100"
            aria-label="Abrir menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
              <Kanban className="w-3 h-3 text-amber-700" />
              <span>Aquisição</span>
            </span>
            <h1 className="text-base sm:text-lg font-semibold text-slate-900 truncate">
              Aquisição — Pipeline
            </h1>
          </div>
        </div>

        {/* Global Search styled like GA4 */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Buscar por prospect, responsável ou tags..."
              className="w-full bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-xs sm:text-sm text-slate-700 pl-9 pr-4 py-1.5 rounded-full border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-1 sm:gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              title="Atualizar dados do pipeline"
              className={`p-2 rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors ${
                isRefreshing ? 'animate-spin text-blue-600' : ''
              }`}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}

          {onNewDealClick && (
            <button
              onClick={onNewDealClick}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Novo negócio</span>
            </button>
          )}

          <button
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Compartilhar visualização"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Compartilhar</span>
          </button>

          <button
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Exportar pipeline CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* Sub Bar: Date period & Canal filter (estilo GA4) */}
      <div className="px-4 sm:px-6 py-2 bg-slate-50/70 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center flex-wrap gap-2">
          {/* Period selector dropdown */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-300 rounded-md shadow-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <CalendarIcon className="w-3.5 h-3.5 text-blue-600" />
              <span>{PERIOD_LABELS[period]}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {dropdownOpen && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
                <div className="absolute left-0 mt-1 w-56 bg-white rounded-lg shadow-xl border border-slate-200 py-1.5 z-40 text-xs animate-in fade-in slide-in-from-top-2">
                  <div className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Período de Aquisição
                  </div>
                  {periods.map((p) => (
                    <button
                      key={p}
                      onClick={() => {
                        onChangePeriod(p)
                        setDropdownOpen(false)
                      }}
                      className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-blue-50/60 transition-colors text-slate-700"
                    >
                      <span className={period === p ? 'font-semibold text-blue-600' : ''}>
                        {PERIOD_LABELS[p]}
                      </span>
                      {period === p && <Check className="w-4 h-4 text-blue-600" />}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Channel dimension filter */}
          <div className="relative">
            <button
              onClick={() => setFilterOpen(!filterOpen)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-medium transition-colors ${
                channelFilter !== 'all'
                  ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Filter className="w-3.5 h-3.5 text-slate-500" />
              <span>Canal: {channelFilter === 'all' ? 'Todos os canais' : channelFilter}</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {filterOpen && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setFilterOpen(false)} />
                <div className="absolute left-0 mt-1 w-64 bg-white rounded-lg shadow-xl border border-slate-200 py-1.5 z-40 text-xs animate-in fade-in slide-in-from-top-2">
                  <div className="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Dimensão: Origem de Tráfego
                  </div>
                  <button
                    onClick={() => {
                      onChannelFilterChange('all')
                      setFilterOpen(false)
                    }}
                    className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50 transition-colors text-slate-700"
                  >
                    <span className={channelFilter === 'all' ? 'font-semibold text-blue-600' : ''}>
                      Todos os canais ({channelsList.length})
                    </span>
                    {channelFilter === 'all' && <Check className="w-4 h-4 text-blue-600" />}
                  </button>
                  {channelsList.map((ch) => (
                    <button
                      key={ch}
                      onClick={() => {
                        onChannelFilterChange(ch)
                        setFilterOpen(false)
                      }}
                      className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-blue-50/60 transition-colors text-slate-700"
                    >
                      <span className={channelFilter === ch ? 'font-semibold text-blue-600' : ''}>
                        {ch}
                      </span>
                      {channelFilter === ch && <Check className="w-4 h-4 text-blue-600" />}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Realtime live tag */}
        <div className="flex items-center gap-2 text-slate-500">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-medium text-slate-600">
            Funil sincronizado com campanhas
          </span>
        </div>
      </div>

      {/* Mobile search bar if on small screen */}
      <div className="md:hidden px-4 py-2 border-t border-slate-100 bg-white">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Buscar por cliente, tags ou vendedor..."
            className="w-full bg-slate-50 text-xs text-slate-700 pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>
    </header>
  )
}
