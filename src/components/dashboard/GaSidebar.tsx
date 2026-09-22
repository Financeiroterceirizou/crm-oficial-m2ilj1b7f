import React from 'react'
import {
  BarChart3,
  Compass,
  FileSpreadsheet,
  Globe,
  HelpCircle,
  Layers,
  PieChart,
  Radio,
  Settings,
  Users,
  X,
} from 'lucide-react'

export type NavTab = 'overview' | 'realtime' | 'acquisition' | 'retention' | 'explore'

interface GaSidebarProps {
  activeTab: NavTab
  onSelectTab: (tab: NavTab) => void
  isOpenMobile: boolean
  onCloseMobile: () => void
}

export const GaSidebar: React.FC<GaSidebarProps> = ({
  activeTab,
  onSelectTab,
  isOpenMobile,
  onCloseMobile,
}) => {
  const mainNavItems = [
    {
      id: 'overview' as NavTab,
      label: 'Relatórios',
      sublabel: 'Visão geral',
      icon: BarChart3,
    },
    {
      id: 'realtime' as NavTab,
      label: 'Tempo real',
      sublabel: 'Últimos 30 min',
      icon: Radio,
      badge: 'Ao vivo',
    },
    {
      id: 'explore' as NavTab,
      label: 'Explorar',
      sublabel: 'Análise livre',
      icon: Compass,
    },
    {
      id: 'acquisition' as NavTab,
      label: 'Aquisição',
      sublabel: 'Tráfego e canais',
      icon: Users,
    },
    {
      id: 'retention' as NavTab,
      label: 'Rentabilidade',
      sublabel: 'Produtos e BPO',
      icon: PieChart,
    },
  ]

  const bottomItems = [
    { label: 'Biblioteca', icon: Layers },
    { label: 'Administrador', icon: Settings },
    { label: 'Ajuda e feedback', icon: HelpCircle },
  ]

  const content = (
    <div className="flex flex-col h-full bg-[#1e293b] text-slate-300 w-64 select-none border-r border-slate-700/60 shadow-xl">
      {/* Brand Header */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-slate-700/60 bg-[#162032]">
        <div className="flex items-center gap-2.5">
          {/* GA4 style colored icon */}
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 via-orange-500 to-amber-600 flex items-center justify-center shadow-md">
            <span className="text-white font-extrabold text-sm tracking-tight">GA</span>
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">
              Analytics 4
            </span>
            <span className="text-sm font-medium text-white truncate max-w-[140px]">
              CRM Terceirizou
            </span>
          </div>
        </div>

        {/* Mobile close button */}
        <button
          onClick={onCloseMobile}
          className="lg:hidden p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-700/50"
          aria-label="Fechar navegação"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Property Selector Simulator */}
      <div className="px-3 py-2.5 bg-[#1a2333] border-b border-slate-700/40 text-xs flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <Globe className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="truncate text-slate-300">terceirizou.com.br</span>
        </div>
        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30">
          GA4-PROD
        </span>
      </div>

      {/* Navigation List */}
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-1">
        <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Ciclo de Vida
        </div>

        {mainNavItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectTab(item.id)
                onCloseMobile()
              }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <div className="text-left">
                  <div className="leading-tight">{item.label}</div>
                  <div
                    className={`text-[11px] ${
                      isActive ? 'text-blue-100' : 'text-slate-400'
                    } leading-tight`}
                  >
                    {item.sublabel}
                  </div>
                </div>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse font-semibold">
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}

        <div className="pt-4 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Configuração & Hub
        </div>

        <a
          href="/fila"
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <FileSpreadsheet className="w-4 h-4 text-slate-400" />
          <span>Fila de Recuperação (Replay)</span>
        </a>
      </div>

      {/* Footer controls */}
      <div className="p-3 border-t border-slate-700/60 bg-[#162032] space-y-1">
        {bottomItems.map((item, idx) => {
          const Icon = item.icon
          return (
            <button
              key={idx}
              className="w-full flex items-center gap-2.5 px-3 py-1.5 rounded-md text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop static sidebar */}
      <aside className="hidden lg:block h-screen sticky top-0 shrink-0 z-30">{content}</aside>

      {/* Mobile drawer overlay */}
      {isOpenMobile && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
          />
          <div className="relative z-10">{content}</div>
        </div>
      )}
    </>
  )
}
