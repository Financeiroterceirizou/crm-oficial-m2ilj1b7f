/* CRM Oficial — Página de Vendas: Análise de Receita e Fechamentos (Estilo GA4)
   Conectada aos DADOS REAIS da collection `deals` do PocketBase (Skip Cloud).
   Responsáveis comerciais reais: Henrique Tavano Sammartino e Vinícius Oliveira da Costa.
*/
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { GaSidebar } from '@/components/dashboard/GaSidebar'
import { VendasHeader } from '@/components/vendas/VendasHeader'
import { VendasKpiCardsGrid } from '@/components/vendas/VendasKpiCardsGrid'
import { VendasChartCard } from '@/components/vendas/VendasChartCard'
import { VendasDimensionTable } from '@/components/vendas/VendasDimensionTable'
import { VendasDealsTable } from '@/components/vendas/VendasDealsTable'
import { DealRecord } from '@/services/deals'
import { DatePeriod } from '@/lib/dashboard-data'
import { VendasService, VendasReportData, VendasFilterOptions } from '@/services/vendas-service'
import {
  AlertCircle,
  BadgePercent,
  CheckCircle2,
  ChevronRight,
  Database,
  DollarSign,
  Kanban,
  RefreshCw,
  ShoppingBag,
  Sparkles,
  TrendingUp,
  UserCheck,
} from 'lucide-react'

export const Vendas: React.FC = () => {
  const [period, setPeriod] = useState<DatePeriod>('28d')
  const [compareEnabled, setCompareEnabled] = useState(true)
  const [responsavelFilter, setResponsavelFilter] = useState<string>('all')
  const [canalFilter, setCanalFilter] = useState<string>('all')
  const [stageView, setStageView] = useState<'won_only' | 'all'>('won_only')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Deals brutos do PocketBase
  const [rawDeals, setRawDeals] = useState<DealRecord[]>([])

  // Busca deals da collection `deals`
  const fetchDeals = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setIsRefreshing(true)
      } else {
        setIsLoading(true)
      }
      setLoadError(null)

      const fetched = await VendasService.fetchAllDeals()
      setRawDeals(fetched)
    } catch (err: unknown) {
      console.error('Falha ao carregar vendas do PocketBase:', err)
      const msg =
        err instanceof Error ? err.message : 'Não foi possível carregar os dados de vendas do CRM.'
      setLoadError(msg)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [])

  useEffect(() => {
    void fetchDeals()
  }, [fetchDeals])

  const handleRefresh = () => {
    void fetchDeals(true)
  }

  // Agrega e calcula os relatórios reativamente
  const filterOptions: VendasFilterOptions = useMemo(
    () => ({
      period,
      compareEnabled,
      responsavelFilter,
      canalFilter,
      stageView,
    }),
    [period, compareEnabled, responsavelFilter, canalFilter, stageView],
  )

  const reportData: VendasReportData = useMemo(() => {
    return VendasService.calculateReport(rawDeals, filterOptions)
  }, [rawDeals, filterOptions])

  const kpisList = [
    reportData.kpis.receitaTotal,
    reportData.kpis.vendasFechadas,
    reportData.kpis.ticketMedio,
    reportData.kpis.taxaConversao,
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col lg:flex-row font-sans text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
      <GaSidebar
        activeTab="sales"
        isOpenMobile={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <VendasHeader
          period={period}
          onChangePeriod={setPeriod}
          compareEnabled={compareEnabled}
          onToggleCompare={() => setCompareEnabled(!compareEnabled)}
          responsavelFilter={responsavelFilter}
          onChangeResponsavelFilter={setResponsavelFilter}
          canalFilter={canalFilter}
          onChangeCanalFilter={setCanalFilter}
          canaisDisponiveis={reportData.canaisDisponiveis}
          responsaveisDisponiveis={reportData.responsaveisDisponiveis}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />

        <main className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto w-full flex-1 flex flex-col">
          {/* Header Banner estilo GA4 */}
          <div className="bg-white rounded-xl border border-emerald-200/80 p-3.5 sm:p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-emerald-50/40 via-white to-white">
            <div className="flex items-start sm:items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm">
                <DollarSign className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-950">
                    Módulo de Vendas — Análise de Receita Fechada
                  </span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-900 px-1.5 py-0.5 rounded font-semibold uppercase flex items-center gap-1 border border-emerald-200">
                    <Database className="w-3 h-3 text-emerald-700" />
                    PocketBase Conectado
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  Dados calculados das oportunidades da collection <code>deals</code>. Responsáveis
                  reais: <strong className="text-blue-700">Henrique Tavano Sammartino (HT)</strong>{' '}
                  e <strong className="text-emerald-700">Vinícius Oliveira da Costa (VO)</strong>.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-500 self-start sm:self-auto">
              <Link
                to="/aquisicao"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition-colors"
              >
                <Kanban className="w-3.5 h-3.5 text-slate-600" />
                <span>Ver Pipeline (Kanban)</span>
              </Link>
            </div>
          </div>

          {/* Banner de Erro caso ocorra falha */}
          {loadError && (
            <div className="rounded-xl border border-rose-200 bg-rose-50/90 p-4 text-xs text-rose-800 flex items-center justify-between gap-3 shadow-sm">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>
                  <strong>Aviso de sincronização:</strong> {loadError}
                </span>
              </div>
              <button
                onClick={() => void fetchDeals()}
                className="inline-flex items-center gap-1 font-semibold text-rose-700 hover:text-rose-900 underline shrink-0"
              >
                <RefreshCw className="w-3 h-3" />
                Tentar novamente
              </button>
            </div>
          )}

          {/* 1. KPIs no Topo */}
          <section aria-label="Métricas Principais de Vendas">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-600" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Desempenho Comercial & Variação vs. Período Anterior
                </h2>
              </div>
              <span className="text-xs text-slate-400">
                {rawDeals.length} oportunidades registradas
              </span>
            </div>
            <VendasKpiCardsGrid
              cards={kpisList}
              compareEnabled={compareEnabled}
              isLoading={isLoading}
            />
          </section>

          {/* 2. Gráfico de Linhas: Evolução da Receita */}
          <section aria-label="Evolução da Receita">
            <VendasChartCard
              data={reportData.timeSeries}
              compareEnabled={compareEnabled}
              isLoading={isLoading}
              responsavelFilter={responsavelFilter}
            />
          </section>

          {/* 3. Tabela de Relatórios Estilo GA4: Dimensões (Responsável / Canal) */}
          <section aria-label="Vendas por Dimensão">
            <VendasDimensionTable
              responsavelData={reportData.vendasPorResponsavel}
              canalData={reportData.vendasPorCanal}
              isLoading={isLoading}
            />
          </section>

          {/* 4. Tabela Detalhada dos Negócios Ganhos */}
          <section aria-label="Lista Detalhada de Negócios">
            <VendasDealsTable
              deals={reportData.dealsList}
              isLoading={isLoading}
              stageView={stageView}
              onStageViewChange={setStageView}
            />
          </section>

          {/* Dicas e Rodapé GA4 */}
          <footer className="pt-4 pb-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2 mt-auto">
            <div className="flex items-center gap-2">
              <span>Google Analytics 4 — Módulo de Vendas</span>
              <span>•</span>
              <span>CRM Terceirizou (Skip Cloud Deals)</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/" className="text-slate-500 hover:text-blue-600 flex items-center gap-1">
                <span>Voltar para Relatórios Gerais</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default Vendas
