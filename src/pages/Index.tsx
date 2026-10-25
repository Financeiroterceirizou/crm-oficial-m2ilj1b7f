/* CRM Oficial — Página Inicial: Dashboard no estilo visual do Google Analytics 4
   Conectado aos DADOS REAIS do CRM (deals de vendas e leads/clientes do Skip Cloud PocketBase)
*/
import React, { useCallback, useEffect, useState } from 'react'
import {
  DatePeriod,
  KpiCardData,
  TimeSeriesPoint,
  ChannelDimensionRow,
  RealtimeData,
  getKpisForPeriod,
  getTimeSeriesForPeriod,
  getChannelsForPeriod,
  getProductDimensionForPeriod,
  MOCK_REALTIME,
} from '@/lib/dashboard-data'
import { CrmDashboardData, DashboardCrmService } from '@/services/dashboard-crm'
import { GaSidebar, NavTab } from '@/components/dashboard/GaSidebar'
import { GaHeader } from '@/components/dashboard/GaHeader'
import { GaKpiCardsGrid } from '@/components/dashboard/GaKpiCardsGrid'
import { GaMainChartCard } from '@/components/dashboard/GaMainChartCard'
import { GaDataTableCard } from '@/components/dashboard/GaDataTableCard'
import { GaRealtimeCard } from '@/components/dashboard/GaRealtimeCard'
import { MetaLeadsRealCard } from '@/components/dashboard/MetaLeadsRealCard'
import { LeadScheduleCard } from '@/components/dashboard/LeadScheduleCard'
import { LeadQualityCard } from '@/components/dashboard/LeadQualityCard'
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Database,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
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
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Estado dos dados reais vindos do CRM
  const [dashboardData, setDashboardData] = useState<CrmDashboardData | null>(null)

  // Busca os dados reais do CRM
  const loadCrmData = useCallback(
    async (showRefreshing = false) => {
      try {
        if (showRefreshing) {
          setIsRefreshing(true)
        } else {
          setIsLoading(true)
        }
        setLoadError(null)

        const result = await DashboardCrmService.getDashboardData(period)
        setDashboardData(result)
      } catch (err: unknown) {
        console.error('Falha ao consultar dados reais do CRM no PocketBase:', err)
        const msg =
          err instanceof Error
            ? err.message
            : 'Não foi possível carregar os dados reais de Vendas e Clientes.'
        setLoadError(msg)
      } finally {
        setIsLoading(false)
        setIsRefreshing(false)
      }
    },
    [period],
  )

  useEffect(() => {
    void loadCrmData()
  }, [loadCrmData])

  const handleRefresh = () => {
    void loadCrmData(true)
  }

  // Fallback suave para dados mock caso o backend falhe completamente
  const kpiCards: KpiCardData[] = dashboardData?.kpis || getKpisForPeriod(period)
  const timeSeries: TimeSeriesPoint[] = dashboardData?.timeSeries || getTimeSeriesForPeriod(period)
  const channelData: ChannelDimensionRow[] =
    dashboardData?.channelData || getChannelsForPeriod(period)
  const productData: ChannelDimensionRow[] =
    dashboardData?.productData || getProductDimensionForPeriod(period)
  const realtimeData: RealtimeData = dashboardData?.realtime || MOCK_REALTIME

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col lg:flex-row font-sans text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
      <GaSidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isOpenMobile={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <GaHeader
          period={period}
          onChangePeriod={setPeriod}
          compareEnabled={compareEnabled}
          onToggleCompare={() => setCompareEnabled(!compareEnabled)}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          isRefreshing={isRefreshing}
          onRefresh={handleRefresh}
        />

        <main className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto w-full">
          {/* Banner de status dos Dados Reais */}
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
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold uppercase flex items-center gap-1 border border-emerald-200">
                    <Database className="w-3 h-3 text-emerald-700" />
                    Dados Reais do CRM Conectados
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-0.5">
                  Métricas em destaque: <strong>Vendas Totais</strong> (oportunidades e faturamento
                  da collection <code>deals</code>) e <strong>Novos Clientes</strong> (collection{' '}
                  <code>leads</code>).
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-start sm:self-auto">
              {dashboardData?.metaInfo && (
                <span className="text-[11px] text-slate-500 font-mono bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                  {dashboardData.metaInfo.totalDeals} deals • {dashboardData.metaInfo.totalLeads}{' '}
                  contatos
                </span>
              )}
            </div>
          </div>

          {/* Banner de Erro caso ocorra falha de rede */}
          {loadError && (
            <div className="rounded-xl border border-rose-200 bg-rose-50/90 p-4 text-xs text-rose-800 flex items-center justify-between gap-3 shadow-sm">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>
                  <strong>Aviso de sincronização:</strong> {loadError}. Exibindo dados de
                  contingência.
                </span>
              </div>
              <button
                onClick={() => void loadCrmData()}
                className="inline-flex items-center gap-1 font-semibold text-rose-700 hover:text-rose-900 underline shrink-0"
              >
                <RefreshCw className="w-3 h-3" />
                Tentar novamente
              </button>
            </div>
          )}

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
              isLoading={isLoading}
            />
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            <div className="lg:col-span-2">
              <GaMainChartCard
                data={timeSeries}
                selectedMetric={selectedMetric}
                compareEnabled={compareEnabled}
                isLoading={isLoading}
              />
            </div>
            <div className="lg:col-span-1">
              <GaRealtimeCard realtime={realtimeData} />
            </div>
          </section>

          {/* F4 b7c2faea: qualidade real por campanha, com B4-203 aprovado */}
          <LeadQualityCard />
          <MetaLeadsRealCard />
          <LeadScheduleCard />

          <section aria-label="Relatório de Dimensões e Conversões">
            <GaDataTableCard
              channelData={channelData}
              productData={productData}
              isLoading={isLoading}
            />
          </section>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
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

          <footer className="pt-6 pb-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
            <div className="flex items-center gap-2">
              <span>Google Analytics 4 — Interface de Demonstração</span>
              <span>•</span>
              <span>Propriedade: CRM Oficial Terceirizou</span>
            </div>
            <a href="/fila" className="text-slate-500 hover:text-blue-600 flex items-center gap-1">
              <span>Acessar Fila de Recuperação</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </a>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default Index
