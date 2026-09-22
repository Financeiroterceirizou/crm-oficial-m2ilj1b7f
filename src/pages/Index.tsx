/* CRM Oficial — Página Inicial: Dashboard no estilo visual do Google Analytics 4
   Dados fictícios / mockados com foco prioritário em Vendas e Clientes
*/
import React, { useState } from 'react'
import {
  DatePeriod,
  getKpisForPeriod,
  getTimeSeriesForPeriod,
  getChannelsForPeriod,
  getProductDimensionForPeriod,
  MOCK_REALTIME,
} from '@/lib/dashboard-data'
import { GaSidebar, NavTab } from '@/components/dashboard/GaSidebar'
import { GaHeader } from '@/components/dashboard/GaHeader'
import { GaKpiCardsGrid } from '@/components/dashboard/GaKpiCardsGrid'
import { GaMainChartCard } from '@/components/dashboard/GaMainChartCard'
import { GaDataTableCard } from '@/components/dashboard/GaDataTableCard'
import { GaRealtimeCard } from '@/components/dashboard/GaRealtimeCard'
import {
  TrendingUp,
  Target,
  Sparkles,
  Info,
  Clock,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react'

const Index: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview')
  const [period, setPeriod] = useState<DatePeriod>('28d')
  const [compareEnabled, setCompareEnabled] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState<
    'vendas' | 'clientes' | 'conversao' | 'ticketMedio'
  >('vendas')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Reactive data computed from current period selection
  const kpiCards = getKpisForPeriod(period)
  const timeSeries = getTimeSeriesForPeriod(period)
  const channelData = getChannelsForPeriod(period)
  const productData = getProductDimensionForPeriod(period)

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => {
      setIsRefreshing(false)
    }, 600)
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col lg:flex-row font-sans text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
      {/* Google Analytics Dark Left Sidebar */}
      <GaSidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isOpenMobile={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Sticky GA4 Top Header with Date Selectors */}
        <GaHeader
          period={period}
          onChangePeriod={setPeriod}
          compareEnabled={compareEnabled}
          onToggleCompare={() => setCompareEnabled(!compareEnabled)}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />

        {/* Dashboard Body */}
        <main className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto w-full">
          {/* Quick Notice Banner: Pure GA4 Interface Info */}
          <div className="bg-white rounded-xl border border-blue-200/80 p-3.5 sm:p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-blue-50/50 via-white to-white">
            <div className="flex items-start sm:items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-blue-900">
                    Painel Executivo — Estilo Google Analytics 4
                  </span>
                  <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded font-semibold uppercase">
                    Modo Simulação
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  Métricas em destaque: <strong>Vendas e Clientes</strong> (conforme recomendação).
                  Todos os seletores e gráficos reagem dinamicamente à navegação.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs text-slate-500 font-mono hidden sm:inline">
                Fuso: America/Sao_Paulo (GMT-3)
              </span>
            </div>
          </div>

          {/* 1. TOP CARDS GRID: Vendas e Clientes em destaque absoluto */}
          <section aria-label="Cartões de Métricas Principais">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-600" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  KPIs Principais & Variação do Período
                </h2>
              </div>
              <span className="text-xs text-slate-400">
                Clique em um cartão para projetar no gráfico
              </span>
            </div>

            <GaKpiCardsGrid
              cards={kpiCards}
              selectedMetric={selectedMetric}
              onSelectMetric={setSelectedMetric}
              compareEnabled={compareEnabled}
            />
          </section>

          {/* 2. MAIN TIME SERIES LINE CHART + REALTIME SIDEBAR WIDGET */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Main Area / Line Chart (spans 2 columns on desktop) */}
            <div className="lg:col-span-2">
              <GaMainChartCard
                data={timeSeries}
                selectedMetric={selectedMetric}
                compareEnabled={compareEnabled}
              />
            </div>

            {/* Realtime Snapshot Widget (GA4 real-time panel) */}
            <div className="lg:col-span-1">
              <GaRealtimeCard realtime={MOCK_REALTIME} />
            </div>
          </section>

          {/* 3. GA4 DATA TABLE: Dimension Breakdown (Acquisition Channels & Services) */}
          <section aria-label="Relatório de Dimensões e Conversões">
            <GaDataTableCard channelData={channelData} productData={productData} />
          </section>

          {/* 4. Secondary Analytics Insight Cards */}
          <section className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            {/* Insight 1 */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600 shrink-0">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900">Melhor canal em taxa de conversão</h4>
                <p className="text-slate-500 mt-1 leading-relaxed">
                  <strong>Indicações e Parcerias</strong> atingiram <strong>6,90%</strong> de taxa
                  de conversão neste período, gerando o maior ticket médio unitário.
                </p>
              </div>
            </div>

            {/* Insight 2 */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600 shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900">
                  Produto mais vendido: BPO Financeiro
                </h4>
                <p className="text-slate-500 mt-1 leading-relaxed">
                  O plano completo de BPO representa <strong>45,9%</strong> do faturamento total
                  recorrente, com retenção superior a 94%.
                </p>
              </div>
            </div>

            {/* Insight 3 */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start gap-3">
              <div className="p-2 rounded-lg bg-amber-50 text-amber-600 shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900">Horário de pico de fechamentos</h4>
                <p className="text-slate-500 mt-1 leading-relaxed">
                  Terças e quintas-feiras entre as <strong>10h00 e 15h30</strong> concentram 58% dos
                  contratos assinados pela equipe comercial.
                </p>
              </div>
            </div>
          </section>

          {/* Footer note GA4 style */}
          <footer className="pt-6 pb-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
            <div className="flex items-center gap-2">
              <span>Google Analytics 4 — Interface de Demonstração</span>
              <span>•</span>
              <span>Propriedade: CRM Oficial Terceirizou</span>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="/fila"
                className="text-slate-500 hover:text-blue-600 flex items-center gap-1"
              >
                <span>Acessar Fila de Recuperação</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default Index
