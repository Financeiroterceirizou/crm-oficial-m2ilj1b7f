/* CRM Oficial — Página de Aquisição: Pipeline de Vendas Estilo Kanban (GA4)
   Dados fictícios / mockados com drag & drop client-side (sem chamadas a backend)
*/
import React, { useMemo, useState } from 'react'
import { GaSidebar } from '@/components/dashboard/GaSidebar'
import { GaPipelineHeader } from '@/components/pipeline/GaPipelineHeader'
import { PipelineSummary } from '@/components/pipeline/PipelineSummary'
import { PipelineKanbanBoard } from '@/components/pipeline/PipelineKanbanBoard'
import { NewDealDialog } from '@/components/pipeline/DealModal'
import { INITIAL_PIPELINE_DEALS, PipelineDeal } from '@/lib/pipeline-data'
import { DatePeriod } from '@/lib/dashboard-data'
import { ChevronRight, Filter, HelpCircle, Info, Kanban, Sparkles } from 'lucide-react'

export const Aquisicao: React.FC = () => {
  const [period, setPeriod] = useState<DatePeriod>('28d')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [channelFilter, setChannelFilter] = useState<string>('all')
  const [deals, setDeals] = useState<PipelineDeal[]>(INITIAL_PIPELINE_DEALS)
  const [newDealOpen, setNewDealOpen] = useState(false)

  // Extrai lista única de canais disponíveis para o filtro
  const channelsList = useMemo(() => {
    const set = new Set<string>()
    deals.forEach((d) => set.add(d.channel))
    return Array.from(set)
  }, [deals])

  // Filtra deals por busca textual e canal de origem
  const filteredDeals = useMemo(() => {
    return deals.filter((deal) => {
      const matchChannel = channelFilter === 'all' || deal.channel === channelFilter

      const q = searchQuery.toLowerCase().trim()
      const matchSearch =
        !q ||
        deal.title.toLowerCase().includes(q) ||
        deal.contactName.toLowerCase().includes(q) ||
        deal.owner.name.toLowerCase().includes(q) ||
        deal.channel.toLowerCase().includes(q) ||
        deal.tags?.some((t) => t.toLowerCase().includes(q))

      return matchChannel && matchSearch
    })
  }, [deals, searchQuery, channelFilter])

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => {
      setIsRefreshing(false)
    }, 500)
  }

  const handleAddNewDeal = (newDeal: PipelineDeal) => {
    setDeals((prev) => [newDeal, ...prev])
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col lg:flex-row font-sans text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
      <GaSidebar
        activeTab="acquisition"
        isOpenMobile={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <GaPipelineHeader
          period={period}
          onChangePeriod={setPeriod}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          channelFilter={channelFilter}
          onChannelFilterChange={setChannelFilter}
          channelsList={channelsList}
          onNewDealClick={() => setNewDealOpen(true)}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />

        <main className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto w-full flex-1 flex flex-col">
          {/* Header Banner estilo GA4 */}
          <div className="bg-white rounded-xl border border-amber-200/80 p-3.5 sm:p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-amber-50/40 via-white to-white">
            <div className="flex items-start sm:items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 shadow-sm">
                <Kanban className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-950">
                    Aquisição de Clientes — Funil de Vendas Comercial
                  </span>
                  <span className="text-[10px] bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded font-semibold uppercase">
                    Pipeline Dinâmico
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  Arraste os cartões entre as etapas para atualizar contagens e valores em tempo
                  real. Origens de tráfego atribuídas por campanha.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="hidden sm:inline">Visualização:</span>
              <span className="font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                Kanban de Oportunidades
              </span>
            </div>
          </div>

          {/* Resumo do Pipeline (KPIs no topo estilo GA4) */}
          <PipelineSummary deals={filteredDeals} period={period} />

          {/* Kanban Board Container */}
          <section className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-600" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Etapas do Funil de Aquisição
                </h2>
                <span className="text-xs text-slate-400 font-normal">
                  ({filteredDeals.length} de {deals.length} oportunidades exibidas)
                </span>
              </div>

              {channelFilter !== 'all' && (
                <div className="flex items-center gap-1.5 text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded-md border border-blue-200 self-start sm:self-auto">
                  <Filter className="w-3 h-3" />
                  <span>Filtrado por: {channelFilter}</span>
                  <button
                    onClick={() => setChannelFilter('all')}
                    className="ml-1 text-blue-500 hover:text-blue-900 font-bold"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>

            <PipelineKanbanBoard deals={filteredDeals} onUpdateDeals={setDeals} />
          </section>

          {/* Dicas e Rodapé GA4 */}
          <footer className="pt-4 pb-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2 mt-auto">
            <div className="flex items-center gap-2">
              <span>Google Analytics 4 — Módulo de Aquisição</span>
              <span>•</span>
              <span>CRM Terceirizou</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="/" className="text-slate-500 hover:text-blue-600 flex items-center gap-1">
                <span>Voltar para Relatórios (Visão geral)</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </footer>
        </main>
      </div>

      {/* New Deal dialog at page level */}
      <NewDealDialog
        isOpen={newDealOpen}
        onClose={() => setNewDealOpen(false)}
        onAddDeal={handleAddNewDeal}
      />
    </div>
  )
}

export default Aquisicao
