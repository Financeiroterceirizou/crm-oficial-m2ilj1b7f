/* Mock data generator for Google Analytics 4 style CRM Dashboard */

export type DatePeriod = 'today' | '7d' | '28d' | '90d' | '12m'

export interface KpiCardData {
  id: string
  title: string
  metricKey: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio'
  currentValueFormatted: string
  currentValueRaw: number
  previousValueFormatted: string
  deltaPercent: number
  isPositive: boolean
  sparkline: { val: number }[]
  benchmarkDesc: string
  recommended?: boolean
}

export interface TimeSeriesPoint {
  date: string
  vendas: number
  clientes: number
  vendasAnterior: number
  clientesAnterior: number
  conversao: number
}

export interface ChannelDimensionRow {
  id: string
  dimension: string // Canal / Origem
  vendas: number
  vendasFormatted: string
  clientes: number
  clientesFormatted: string
  conversao: number
  conversaoFormatted: string
  percentShare: number // 0 a 100
  badgeColor?: string
}

export interface RealtimeData {
  usersLast30Min: number
  vendasLast30Min: number
  activePages: { path: string; count: number }[]
  topCities: { city: string; active: number }[]
}

export const PERIOD_LABELS: Record<DatePeriod, string> = {
  today: 'Hoje',
  '7d': 'Últimos 7 dias',
  '28d': 'Últimos 28 dias',
  '90d': 'Últimos 90 dias',
  '12m': 'Últimos 12 meses',
}

export const COMPARISON_LABELS: Record<DatePeriod, string> = {
  today: 'vs. ontem',
  '7d': 'vs. 7 dias anteriores',
  '28d': 'vs. 28 dias anteriores',
  '90d': 'vs. 90 dias anteriores',
  '12m': 'vs. ano anterior',
}

// Sparklines pré-definidos para suavidade e beleza visual
const SPARKLINES: Record<
  DatePeriod,
  { vendas: number[]; clientes: number[]; conversao: number[]; ticket: number[] }
> = {
  today: {
    vendas: [1200, 1500, 1800, 1400, 2200, 2900, 3400, 4100, 3800, 4600, 5200, 5890],
    clientes: [3, 4, 2, 5, 8, 11, 14, 12, 16, 19, 21, 24],
    conversao: [2.1, 2.4, 2.3, 2.6, 2.8, 3.1, 3.4, 3.2, 3.5, 3.6, 3.8, 4.1],
    ticket: [400, 375, 450, 280, 275, 263, 242, 341, 237, 242, 247, 245],
  },
  '7d': {
    vendas: [22400, 24800, 23100, 28900, 31200, 36500, 38400],
    clientes: [95, 108, 102, 126, 134, 158, 162],
    conversao: [3.2, 3.4, 3.3, 3.6, 3.8, 4.0, 4.2],
    ticket: [235, 229, 226, 229, 232, 231, 237],
  },
  '28d': {
    vendas: [
      12000, 13400, 14200, 13800, 15600, 16200, 17100, 16800, 18200, 19400, 18900, 21000, 22400,
      23100, 22800, 24500, 25800, 26200, 27400, 28100, 29500, 30200, 31800, 32400, 34100, 35600,
      37200, 38900,
    ],
    clientes: [
      52, 58, 62, 59, 68, 71, 75, 72, 80, 85, 82, 92, 98, 102, 99, 107, 113, 115, 121, 125, 132,
      135, 142, 146, 154, 161, 168, 175,
    ],
    conversao: [
      2.8, 2.9, 3.0, 2.9, 3.1, 3.2, 3.3, 3.2, 3.4, 3.5, 3.4, 3.6, 3.7, 3.8, 3.7, 3.8, 3.9, 4.0, 4.0,
      4.1, 4.2, 4.2, 4.3, 4.3, 4.4, 4.5, 4.6, 4.7,
    ],
    ticket: [
      230, 231, 229, 233, 229, 228, 228, 233, 227, 228, 230, 228, 228, 226, 230, 228, 228, 227, 226,
      224, 223, 223, 223, 221, 221, 221, 221, 222,
    ],
  },
  '90d': {
    vendas: [
      78000, 82000, 86000, 91000, 97000, 104000, 112000, 118000, 126000, 134000, 142000, 156000,
    ],
    clientes: [340, 362, 380, 405, 432, 460, 498, 524, 560, 595, 630, 694],
    conversao: [3.1, 3.2, 3.3, 3.4, 3.6, 3.8, 4.0, 4.1, 4.2, 4.3, 4.4, 4.6],
    ticket: [229, 226, 226, 224, 224, 226, 224, 225, 225, 225, 225, 224],
  },
  '12m': {
    vendas: [
      320000, 340000, 365000, 390000, 420000, 450000, 490000, 530000, 580000, 620000, 690000,
      784000,
    ],
    clientes: [1420, 1510, 1630, 1740, 1870, 2010, 2190, 2370, 2590, 2770, 3080, 3498],
    conversao: [2.9, 3.0, 3.2, 3.3, 3.5, 3.6, 3.8, 3.9, 4.1, 4.2, 4.4, 4.6],
    ticket: [225, 225, 223, 224, 224, 223, 223, 223, 223, 223, 224, 224],
  },
}

export function getKpisForPeriod(period: DatePeriod): KpiCardData[] {
  const spark = SPARKLINES[period]

  const metricsMap = {
    today: {
      vendas: { cur: 5890, prev: 4920, delta: 19.7, curFmt: 'R$ 5.890,00', prevFmt: 'R$ 4.920,00' },
      clientes: { cur: 24, prev: 18, delta: 33.3, curFmt: '24', prevFmt: '18' },
      conversao: { cur: 4.1, prev: 3.5, delta: 17.1, curFmt: '4,1%', prevFmt: '3,5%' },
      ticket: {
        cur: 245.41,
        prev: 273.33,
        delta: -10.2,
        curFmt: 'R$ 245,41',
        prevFmt: 'R$ 273,33',
      },
    },
    '7d': {
      vendas: {
        cur: 38400,
        prev: 32600,
        delta: 17.8,
        curFmt: 'R$ 38.400,00',
        prevFmt: 'R$ 32.600,00',
      },
      clientes: { cur: 162, prev: 139, delta: 16.5, curFmt: '162', prevFmt: '139' },
      conversao: { cur: 4.2, prev: 3.8, delta: 10.5, curFmt: '4,2%', prevFmt: '3,8%' },
      ticket: { cur: 237.03, prev: 234.53, delta: 1.1, curFmt: 'R$ 237,03', prevFmt: 'R$ 234,53' },
    },
    '28d': {
      vendas: {
        cur: 148920,
        prev: 122450,
        delta: 21.6,
        curFmt: 'R$ 148.920,00',
        prevFmt: 'R$ 122.450,00',
      },
      clientes: { cur: 672, prev: 548, delta: 22.6, curFmt: '672', prevFmt: '548' },
      conversao: { cur: 4.38, prev: 3.72, delta: 17.7, curFmt: '4,38%', prevFmt: '3,72%' },
      ticket: { cur: 221.6, prev: 223.44, delta: -0.8, curFmt: 'R$ 221,60', prevFmt: 'R$ 223,44' },
    },
    '90d': {
      vendas: {
        cur: 462800,
        prev: 389200,
        delta: 18.9,
        curFmt: 'R$ 462.800,00',
        prevFmt: 'R$ 389.200,00',
      },
      clientes: { cur: 2064, prev: 1730, delta: 19.3, curFmt: '2.064', prevFmt: '1.730' },
      conversao: { cur: 4.15, prev: 3.65, delta: 13.7, curFmt: '4,15%', prevFmt: '3,65%' },
      ticket: { cur: 224.22, prev: 224.97, delta: -0.3, curFmt: 'R$ 224,22', prevFmt: 'R$ 224,97' },
    },
    '12m': {
      vendas: {
        cur: 1890400,
        prev: 1540000,
        delta: 22.7,
        curFmt: 'R$ 1.890.400,00',
        prevFmt: 'R$ 1.540.000,00',
      },
      clientes: { cur: 8430, prev: 6920, delta: 21.8, curFmt: '8.430', prevFmt: '6.920' },
      conversao: { cur: 4.22, prev: 3.68, delta: 14.6, curFmt: '4,22%', prevFmt: '3,68%' },
      ticket: { cur: 224.24, prev: 222.54, delta: 0.8, curFmt: 'R$ 224,24', prevFmt: 'R$ 222,54' },
    },
  }[period]

  const compLabel = COMPARISON_LABELS[period]

  return [
    {
      id: 'kpi-vendas',
      title: 'Vendas totais',
      metricKey: 'vendas',
      currentValueFormatted: metricsMap.vendas.curFmt,
      currentValueRaw: metricsMap.vendas.cur,
      previousValueFormatted: metricsMap.vendas.prevFmt,
      deltaPercent: metricsMap.vendas.delta,
      isPositive: metricsMap.vendas.delta >= 0,
      sparkline: spark.vendas.map((val) => ({ val })),
      benchmarkDesc: `${compLabel}: ${metricsMap.vendas.prevFmt}`,
      recommended: true,
    },
    {
      id: 'kpi-clientes',
      title: 'Novos clientes',
      metricKey: 'clientes',
      currentValueFormatted: metricsMap.clientes.curFmt,
      currentValueRaw: metricsMap.clientes.cur,
      previousValueFormatted: metricsMap.clientes.prevFmt,
      deltaPercent: metricsMap.clientes.delta,
      isPositive: metricsMap.clientes.delta >= 0,
      sparkline: spark.clientes.map((val) => ({ val })),
      benchmarkDesc: `${compLabel}: ${metricsMap.clientes.prevFmt}`,
      recommended: true,
    },
    {
      id: 'kpi-conversao',
      title: 'Taxa de conversão de leads',
      metricKey: 'conversao',
      currentValueFormatted: metricsMap.conversao.curFmt,
      currentValueRaw: metricsMap.conversao.cur,
      previousValueFormatted: metricsMap.conversao.prevFmt,
      deltaPercent: metricsMap.conversao.delta,
      isPositive: metricsMap.conversao.delta >= 0,
      sparkline: spark.conversao.map((val) => ({ val })),
      benchmarkDesc: `${compLabel}: ${metricsMap.conversao.prevFmt}`,
      recommended: false,
    },
    {
      id: 'kpi-ticket',
      title: 'Ticket médio de fechamento',
      metricKey: 'ticketMedio',
      currentValueFormatted: metricsMap.ticket.curFmt,
      currentValueRaw: metricsMap.ticket.cur,
      previousValueFormatted: metricsMap.ticket.prevFmt,
      deltaPercent: metricsMap.ticket.delta,
      isPositive: metricsMap.ticket.delta >= 0,
      sparkline: spark.ticket.map((val) => ({ val })),
      benchmarkDesc: `${compLabel}: ${metricsMap.ticket.prevFmt}`,
      recommended: false,
    },
  ]
}

export function getTimeSeriesForPeriod(period: DatePeriod): TimeSeriesPoint[] {
  if (period === 'today') {
    const hours = [
      '08:00',
      '09:00',
      '10:00',
      '11:00',
      '12:00',
      '13:00',
      '14:00',
      '15:00',
      '16:00',
      '17:00',
      '18:00',
      '19:00',
    ]
    const curVendas = [240, 480, 620, 850, 410, 520, 780, 910, 680, 820, 420, 160]
    const prevVendas = [190, 390, 510, 700, 380, 460, 650, 790, 580, 690, 350, 120]
    const curClientes = [1, 2, 2, 4, 2, 2, 3, 4, 3, 3, 2, 1]
    const prevClientes = [1, 1, 2, 3, 1, 2, 2, 3, 2, 3, 1, 1]

    return hours.map((hour, idx) => ({
      date: hour,
      vendas: curVendas[idx],
      clientes: curClientes[idx],
      vendasAnterior: prevVendas[idx],
      clientesAnterior: prevClientes[idx],
      conversao: Number((3.0 + (idx % 4) * 0.4).toFixed(2)),
    }))
  }

  if (period === '7d') {
    const days = ['Seg, 18', 'Ter, 19', 'Qua, 20', 'Qui, 21', 'Sex, 22', 'Sáb, 23', 'Dom, 24']
    const vCur = [4800, 5400, 5100, 6300, 6900, 4200, 5700]
    const vPrev = [4100, 4600, 4300, 5200, 5800, 3600, 5000]
    const cCur = [20, 23, 21, 27, 29, 18, 24]
    const cPrev = [17, 19, 18, 23, 25, 15, 22]

    return days.map((day, idx) => ({
      date: day,
      vendas: vCur[idx],
      clientes: cCur[idx],
      vendasAnterior: vPrev[idx],
      clientesAnterior: cPrev[idx],
      conversao: Number((3.6 + (idx % 3) * 0.3).toFixed(2)),
    }))
  }

  if (period === '28d') {
    const points: TimeSeriesPoint[] = []
    const baseDate = new Date()
    baseDate.setDate(baseDate.getDate() - 27)

    for (let i = 0; i < 28; i++) {
      const d = new Date(baseDate)
      d.setDate(baseDate.getDate() + i)
      const dayStr = `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`

      const trend = i * 65
      const wave = Math.sin(i / 2) * 450
      const vCur = Math.round(4200 + trend + wave + (i % 5) * 120)
      const vPrev = Math.round(3500 + i * 50 + Math.cos(i / 2) * 350)
      const cCur = Math.round(vCur / 225)
      const cPrev = Math.round(vPrev / 228)

      points.push({
        date: dayStr,
        vendas: vCur,
        clientes: cCur,
        vendasAnterior: vPrev,
        clientesAnterior: cPrev,
        conversao: Number((3.8 + (i % 6) * 0.15).toFixed(2)),
      })
    }
    return points
  }

  if (period === '90d') {
    const weeks = [
      'Sem 1',
      'Sem 2',
      'Sem 3',
      'Sem 4',
      'Sem 5',
      'Sem 6',
      'Sem 7',
      'Sem 8',
      'Sem 9',
      'Sem 10',
      'Sem 11',
      'Sem 12',
    ]
    return weeks.map((w, idx) => ({
      date: w,
      vendas: Math.round(32000 + idx * 1200 + (idx % 3) * 800),
      clientes: Math.round(145 + idx * 5 + (idx % 2) * 6),
      vendasAnterior: Math.round(27000 + idx * 1050),
      clientesAnterior: Math.round(120 + idx * 4),
      conversao: Number((3.9 + (idx % 4) * 0.2).toFixed(2)),
    }))
  }

  // 12m
  const months = [
    'Jan',
    'Fev',
    'Mar',
    'Abr',
    'Mai',
    'Jun',
    'Jul',
    'Ago',
    'Set',
    'Out',
    'Nov',
    'Dez',
  ]
  return months.map((m, idx) => ({
    date: m,
    vendas: Math.round(130000 + idx * 6200 + (idx % 4) * 3500),
    clientes: Math.round(580 + idx * 28 + (idx % 3) * 15),
    vendasAnterior: Math.round(108000 + idx * 5100),
    clientesAnterior: Math.round(480 + idx * 22),
    conversao: Number((3.7 + (idx % 4) * 0.25).toFixed(2)),
  }))
}

export function getChannelsForPeriod(period: DatePeriod): ChannelDimensionRow[] {
  // Ajuste proporcional baseado no período
  const scale =
    period === 'today'
      ? 0.04
      : period === '7d'
        ? 0.26
        : period === '28d'
          ? 1
          : period === '90d'
            ? 3.1
            : 12.7

  const baseChannels = [
    {
      name: 'Meta Ads (Instagram & Facebook)',
      baseVendas: 58900,
      baseClientes: 268,
      conv: 4.82,
      share: 39.5,
      badgeColor: 'bg-purple-100 text-purple-800',
    },
    {
      name: 'Google Search Orgânico (SEO)',
      baseVendas: 34200,
      baseClientes: 154,
      conv: 5.14,
      share: 23.0,
      badgeColor: 'bg-emerald-100 text-emerald-800',
    },
    {
      name: 'Google Ads (Search & Performance Max)',
      baseVendas: 26800,
      baseClientes: 122,
      conv: 4.25,
      share: 18.0,
      badgeColor: 'bg-blue-100 text-blue-800',
    },
    {
      name: 'Indicações de Clientes & Parcerias',
      baseVendas: 17820,
      baseClientes: 81,
      conv: 6.9,
      share: 12.0,
      badgeColor: 'bg-amber-100 text-amber-800',
    },
    {
      name: 'Email Marketing & CRM Nurturing',
      baseVendas: 7200,
      baseClientes: 32,
      conv: 3.4,
      share: 4.8,
      badgeColor: 'bg-indigo-100 text-indigo-800',
    },
    {
      name: 'Tráfego Direto & Outros',
      baseVendas: 4000,
      baseClientes: 15,
      conv: 2.1,
      share: 2.7,
      badgeColor: 'bg-gray-100 text-gray-800',
    },
  ]

  return baseChannels.map((c, i) => {
    const vendas = Math.round(c.baseVendas * scale)
    const clientes = Math.round(c.baseClientes * scale)
    return {
      id: `chan-${i + 1}`,
      dimension: c.name,
      vendas,
      vendasFormatted: `R$ ${vendas.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      clientes,
      clientesFormatted: clientes.toLocaleString('pt-BR'),
      conversao: c.conv,
      conversaoFormatted: `${c.conv.toFixed(2)}%`,
      percentShare: c.share,
      badgeColor: c.badgeColor,
    }
  })
}

export function getProductDimensionForPeriod(period: DatePeriod): ChannelDimensionRow[] {
  const scale =
    period === 'today'
      ? 0.04
      : period === '7d'
        ? 0.26
        : period === '28d'
          ? 1
          : period === '90d'
            ? 3.1
            : 12.7

  const baseProducts = [
    {
      name: 'BPO Financeiro Completo (Mensal)',
      baseVendas: 68400,
      baseClientes: 285,
      conv: 5.6,
      share: 45.9,
    },
    {
      name: 'Conciliação Bancária & Fiscal',
      baseVendas: 37200,
      baseClientes: 177,
      conv: 4.3,
      share: 25.0,
    },
    {
      name: 'Gestão de Contas a Pagar/Receber',
      baseVendas: 24600,
      baseClientes: 123,
      conv: 3.9,
      share: 16.5,
    },
    {
      name: 'Consultoria Financeira Estratégica',
      baseVendas: 13200,
      baseClientes: 55,
      conv: 3.1,
      share: 8.9,
    },
    {
      name: 'Auditoria & Diagnóstico Financeiro',
      baseVendas: 5520,
      baseClientes: 32,
      conv: 2.5,
      share: 3.7,
    },
  ]

  return baseProducts.map((p, i) => {
    const vendas = Math.round(p.baseVendas * scale)
    const clientes = Math.round(p.baseClientes * scale)
    return {
      id: `prod-${i + 1}`,
      dimension: p.name,
      vendas,
      vendasFormatted: `R$ ${vendas.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      clientes,
      clientesFormatted: clientes.toLocaleString('pt-BR'),
      conversao: p.conv,
      conversaoFormatted: `${p.conv.toFixed(2)}%`,
      percentShare: p.share,
    }
  })
}

export const MOCK_REALTIME: RealtimeData = {
  usersLast30Min: 47,
  vendasLast30Min: 3,
  activePages: [
    { path: '/planos-bpo-financeiro', count: 18 },
    { path: '/agendamento-consultoria', count: 14 },
    { path: '/calculadora-roi-financeiro', count: 9 },
    { path: '/depoimentos-cases', count: 6 },
  ],
  topCities: [
    { city: 'São Paulo (SP)', active: 22 },
    { city: 'Rio de Janeiro (RJ)', active: 11 },
    { city: 'Belo Horizonte (MG)', active: 7 },
    { city: 'Curitiba (PR)', active: 4 },
    { city: 'Porto Alegre (RS)', active: 3 },
  ],
}
