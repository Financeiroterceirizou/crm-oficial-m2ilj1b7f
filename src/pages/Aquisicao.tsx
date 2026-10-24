/* CRM Oficial — Página de Aquisição: Pipeline de Vendas Estilo Kanban (GA4)
   Conectado em tempo real ao PocketBase (Skip Cloud) com persistência completa.
*/
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { GaSidebar } from '@/components/dashboard/GaSidebar'
import { GaPipelineHeader } from '@/components/pipeline/GaPipelineHeader'
import { PipelineSummary } from '@/components/pipeline/PipelineSummary'
import { PipelineKanbanBoard } from '@/components/pipeline/PipelineKanbanBoard'
import { NewDealDialog } from '@/components/pipeline/DealModal'
import { PipelineDeal } from '@/lib/pipeline-data'
import { DatePeriod } from '@/lib/dashboard-data'
import { DealsService } from '@/services/deals'
import {
  AlertCircle,
  ChevronRight,
  Database,
  Filter,
  Kanban,
  Loader2,
  Plus,
  RefreshCw,
} from 'lucide-react'

export const Aquisicao: React.FC = () => {
  const [period, setPeriod] = useState<DatePeriod>('28d')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [channelFilter, setChannelFilter] = useState<string>('all')
  const [deals, setDeals] = useState<PipelineDeal[]>([])
  const [newDealOpen, setNewDealOpen] = useState(false)

  // Carrega os dados reais da collection 'deals'
  const fetchDeals = useCallback(async (showRefreshingSpinner = false) => {
    try {
      if (showRefreshingSpinner) {
        setIsRefreshing(true)
      } else {
        setIsLoading(true)
      }
      setLoadError(null)

      const fetched = await DealsService.list()
      setDeals(fetched)
    } catch (err: unknown) {
      console.error('Falha ao carregar deals do PocketBase:', err)
      const message =
        err instanceof Error ? err.message : 'Não foi possível carregar os negócios do CRM.'
      setLoadError(message)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchDeals()
  }, [fetchDeals])

  // Extrai lista única de canais disponíveis para o filtro
  const channelsList = useMemo(() => {
    const set = new Set<string>()
    deals.forEach((d) => {
      if (d.channel) set.add(d.channel)
    })
    return Array.from(set).sort()
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
    fetchDeals(true)
  }

  const handleAddNewDeal = (newDeal: PipelineDeal) => {
    setDeals((prev) => [newDeal, ...prev])
  }

  const handleDealUpdated = (updatedDeal: PipelineDeal) => {
    setDeals((prev) => prev.map((d) => (d.id === updatedDeal.id ? updatedDeal : d)))
  }

  const handleDealDeleted = (dealId: string) => {
    setDeals((prev) => prev.filter((d) => d.id !== dealId))
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
                  <span className="text-[10px] bg-emerald-100 text-emerald-900 px-1.5 py-0.5 rounded font-semibold uppercase flex items-center gap-1">
                    <Database className="w-3 h-3" />
                    Skip Cloud Conectado
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  Pipeline sincronizado com a base PocketBase. Arraste cartões para atualizar etapas
                  com rollback automático se houver perda de conexão.
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

          {/* Resumo do Pipeline (KPIs no topo estilo GA4 calculados dos dados reais) */}
          <PipelineSummary deals={filteredDeals} period={period} />

          {/* Kanban Board Container */}
          <section className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm space-y-4 flex-1 flex flex-col">
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

            {/* Loading State estilo GA4 */}
            {isLoading ? (
              <div className="py-20 flex flex-col items-center justify-center text-center space-y-3">
                <div className="p-3 rounded-full bg-blue-50 text-blue-600 border border-blue-100 animate-spin">
                  <Loader2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-800">
                    Sincronizando pipeline de aquisição...
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Consultando oportunidades comerciais no PocketBase
                  </p>
                </div>
              </div>
            ) : loadError ? (
              /* Error State estilo GA4 */
              <div className="py-16 px-4 flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-3">
                <div className="p-3 rounded-full bg-red-50 text-red-600 border border-red-100">
                  <AlertCircle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Falha ao carregar oportunidades
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">{loadError}</p>
                </div>
                <button
                  onClick={() => fetchDeals()}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium shadow-sm transition-colors"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Tentar novamente</span>
                </button>
              </div>
            ) : deals.length === 0 ? (
              /* Empty State Total estilo GA4 */
              <div className="py-20 px-4 flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-3">
                <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center border border-slate-200">
                  <Kanban className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Nenhum negócio no pipeline
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Crie a primeira oportunidade para começar a acompanhar seu funil de conversão e
                    faturamento.
                  </p>
                </div>
                <button
                  onClick={() => setNewDealOpen(true)}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-sm transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Cadastrar primeiro negócio</span>
                </button>
              </div>
            ) : filteredDeals.length === 0 ? (
              /* Empty State de Filtro estilo GA4 */
              <div className="py-16 px-4 flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-2">
                <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-200">
                  <Filter className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Nenhum resultado para os filtros atuais
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Tente ajustar a busca por texto ou redefinir a origem de canal.
                  </p>
                </div>
                <button
                  onClick={() => {
                    setSearchQuery('')
                    setChannelFilter('all')
                  }}
                  className="px-3 py-1.5 text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Limpar filtros
                </button>
              </div>
            ) : (
              <PipelineKanbanBoard
                deals={filteredDeals}
                onUpdateDeals={setDeals}
                onDealCreated={handleAddNewDeal}
                onDealUpdated={handleDealUpdated}
                onDealDeleted={handleDealDeleted}
              />
            )}
          </section>

          {/* Dicas e Rodapé GA4 */}
          <footer className="pt-4 pb-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2 mt-auto">
            <div className="flex items-center gap-2">
              <span>Google Analytics 4 — Módulo de Aquisição</span>
              <span>•</span>
              <span>CRM Terceirizou (Skip Cloud Deals)</span>
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
        onDealCreated={handleAddNewDeal}
      />
    </div>
  )
}

export default Aquisicao
