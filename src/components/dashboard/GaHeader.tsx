import React from 'react'
import {
  Calendar as CalendarIcon,
  Check,
  ChevronDown,
  Download,
  Menu,
  RefreshCw,
  Search,
  Share2,
  SlidersHorizontal,
} from 'lucide-react'
import { DatePeriod, PERIOD_LABELS } from '@/lib/dashboard-data'

interface GaHeaderProps {
  period: DatePeriod
  onChangePeriod: (period: DatePeriod) => void
  compareEnabled: boolean
  onToggleCompare: () => void
  onOpenMobileMenu: () => void
  isRefreshing?: boolean
  onRefresh?: () => void
}

export const GaHeader: React.FC<GaHeaderProps> = ({
  period,
  onChangePeriod,
  compareEnabled,
  onToggleCompare,
  onOpenMobileMenu,
  isRefreshing,
  onRefresh,
}) => {
  const [dropdownOpen, setDropdownOpen] = React.useState(false)

  const periods: DatePeriod[] = ['today', '7d', '28d', '90d', '12m']

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
      {/* Top Bar: Brand, Search, Global Tools */}
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
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              Relatório
            </span>
            <h1 className="text-base sm:text-lg font-semibold text-slate-900 truncate">
              Relatório de visão geral
            </h1>
          </div>
        </div>

        {/* Search bar style GA4 */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              readOnly
              placeholder="Pesquisar relatórios, dimensões e métricas..."
              className="w-full bg-slate-50 hover:bg-slate-100 text-xs sm:text-sm text-slate-700 pl-9 pr-4 py-1.5 rounded-full border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer transition-colors"
            />
          </div>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-1 sm:gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              title="Atualizar dados agora"
              className={`p-2 rounded-md text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors ${
                isRefreshing ? 'animate-spin text-blue-600' : ''
              }`}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}

          <button
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Compartilhar este relatório"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Compartilhar</span>
          </button>

          <button
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
            title="Exportar dados"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* Sub Bar: Date period & Comparison controls (Identical to GA4) */}
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
                    Selecione o período
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

          {/* Comparison toggle button */}
          <button
            onClick={onToggleCompare}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-medium transition-all ${
              compareEnabled
                ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Comparar: Período anterior</span>
            <span
              className={`inline-block w-2 h-2 rounded-full ml-1 ${
                compareEnabled ? 'bg-blue-600' : 'bg-slate-300'
              }`}
            />
          </button>
        </div>

        {/* Realtime Pill Badge */}
        <div className="flex items-center gap-2 text-slate-500">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-medium text-slate-600">
            Dados sincronizados em tempo real (Simulado)
          </span>
        </div>
      </div>
    </header>
  )
}
