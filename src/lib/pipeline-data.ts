/* Mock data e tipos para a Pipeline de Vendas na área de Aquisição (estilo GA4) */

export type PipelineStageId = 'new_leads' | 'contacted' | 'proposal_sent' | 'negotiation' | 'won'

export interface PipelineStageConfig {
  id: PipelineStageId
  title: string
  color: string
  badgeBg: string
  badgeText: string
  accentBorder: string
}

export interface PipelineDeal {
  id: string
  title: string // Nome do cliente ou prospect / empresa
  contactName: string
  value: number // Valor em R$
  channel: string // Meta Ads, Google Orgânico, Google Ads, Indicação, Email Marketing, Tráfego Direto
  stageId: PipelineStageId
  owner: {
    name: string
    initials: string
    avatarBg: string
  }
  daysInStage: number
  probability: number // %
  createdAt: string
  tags?: string[]
}

export const PIPELINE_STAGES: PipelineStageConfig[] = [
  {
    id: 'new_leads',
    title: 'Novos leads',
    color: 'bg-blue-500',
    badgeBg: 'bg-blue-50',
    badgeText: 'text-blue-700 border-blue-200',
    accentBorder: 'border-t-blue-500',
  },
  {
    id: 'contacted',
    title: 'Contato feito',
    color: 'bg-amber-500',
    badgeBg: 'bg-amber-50',
    badgeText: 'text-amber-700 border-amber-200',
    accentBorder: 'border-t-amber-500',
  },
  {
    id: 'proposal_sent',
    title: 'Proposta enviada',
    color: 'bg-purple-500',
    badgeBg: 'bg-purple-50',
    badgeText: 'text-purple-700 border-purple-200',
    accentBorder: 'border-t-purple-500',
  },
  {
    id: 'negotiation',
    title: 'Negociação',
    color: 'bg-indigo-500',
    badgeBg: 'bg-indigo-50',
    badgeText: 'text-indigo-700 border-indigo-200',
    accentBorder: 'border-t-indigo-500',
  },
  {
    id: 'won',
    title: 'Fechado (ganho)',
    color: 'bg-emerald-500',
    badgeBg: 'bg-emerald-50',
    badgeText: 'text-emerald-700 border-emerald-200',
    accentBorder: 'border-t-emerald-500',
  },
]

export const INITIAL_PIPELINE_DEALS: PipelineDeal[] = [
  // Novos leads
  {
    id: 'deal-1',
    title: 'Clínica Odonto Prime',
    contactName: 'Dra. Camila Albuquerque',
    value: 3800,
    channel: 'Meta Ads',
    stageId: 'new_leads',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 1,
    probability: 20,
    createdAt: 'Hoje às 09:15',
    tags: ['BPO Completo', 'Urgente'],
  },
  {
    id: 'deal-2',
    title: 'Grupo Alpha Logística',
    contactName: 'Marcos Vinícius',
    value: 7500,
    channel: 'Google Orgânico',
    stageId: 'new_leads',
    owner: { name: 'Vinícius Oliveira da Costa', initials: 'VO', avatarBg: 'bg-emerald-600' },
    daysInStage: 2,
    probability: 25,
    createdAt: 'Ontem',
    tags: ['Conciliação', 'Grande Porte'],
  },
  {
    id: 'deal-3',
    title: 'TechWave Soluções Digitais',
    contactName: 'Fernanda Rocha',
    value: 4900,
    channel: 'Indicação',
    stageId: 'new_leads',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 1,
    probability: 30,
    createdAt: 'Hoje às 11:30',
    tags: ['Consultoria'],
  },
  {
    id: 'deal-4',
    title: 'Restaurante Sabor & Arte',
    contactName: 'Antônio Ferreira',
    value: 2600,
    channel: 'Meta Ads',
    stageId: 'new_leads',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 3,
    probability: 15,
    createdAt: '2 dias atrás',
    tags: ['Contas a Pagar'],
  },

  // Contato feito
  {
    id: 'deal-5',
    title: 'Vanguard Engenharia Civil',
    contactName: 'Eng. Roberto Dias',
    value: 9200,
    channel: 'Google Ads',
    stageId: 'contacted',
    owner: { name: 'Vinícius Oliveira da Costa', initials: 'VO', avatarBg: 'bg-emerald-600' },
    daysInStage: 3,
    probability: 40,
    createdAt: '3 dias atrás',
    tags: ['BPO + Fiscal', 'Reunião Agendada'],
  },
  {
    id: 'deal-6',
    title: 'BioSaúde Distribuidora',
    contactName: 'Patrícia Nogueira',
    value: 5800,
    channel: 'Meta Ads',
    stageId: 'contacted',
    owner: { name: 'Vinícius Oliveira da Costa', initials: 'VO', avatarBg: 'bg-emerald-600' },
    daysInStage: 2,
    probability: 35,
    createdAt: '3 dias atrás',
    tags: ['Diagnóstico'],
  },
  {
    id: 'deal-7',
    title: 'Escola Aquarela Kids',
    contactName: 'Beatriz Vasconcelos',
    value: 3200,
    channel: 'Indicação',
    stageId: 'contacted',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 4,
    probability: 45,
    createdAt: '4 dias atrás',
    tags: ['Mensalidade'],
  },

  // Proposta enviada
  {
    id: 'deal-8',
    title: 'Nexus Hub Coworking',
    contactName: 'Diego Brandão',
    value: 6400,
    channel: 'Google Orgânico',
    stageId: 'proposal_sent',
    owner: { name: 'Vinícius Oliveira da Costa', initials: 'VO', avatarBg: 'bg-emerald-600' },
    daysInStage: 5,
    probability: 60,
    createdAt: '5 dias atrás',
    tags: ['Proposta v2', 'Decisor Envolvido'],
  },
  {
    id: 'deal-9',
    title: 'Nova Era Auto Peças',
    contactName: 'Sérgio Ramos',
    value: 8100,
    channel: 'Google Ads',
    stageId: 'proposal_sent',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 4,
    probability: 65,
    createdAt: '6 dias atrás',
    tags: ['Plano Anual'],
  },
  {
    id: 'deal-10',
    title: 'Solaris Energia Renovável',
    contactName: 'Gustavo Mendonça',
    value: 11500,
    channel: 'Indicação',
    stageId: 'proposal_sent',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 2,
    probability: 70,
    createdAt: '2 dias atrás',
    tags: ['Enterprise', 'Prioridade Alta'],
  },

  // Negociação
  {
    id: 'deal-11',
    title: 'Rede Farma Popular (3 lojas)',
    contactName: 'Juliana Pires',
    value: 14200,
    channel: 'Meta Ads',
    stageId: 'negotiation',
    owner: { name: 'Vinícius Oliveira da Costa', initials: 'VO', avatarBg: 'bg-emerald-600' },
    daysInStage: 6,
    probability: 85,
    createdAt: '7 dias atrás',
    tags: ['Ajuste Jurídico', 'Fechamento Próximo'],
  },
  {
    id: 'deal-12',
    title: 'Studio Pilates Vida & Equilíbrio',
    contactName: 'Larissa Moura',
    value: 2900,
    channel: 'Google Orgânico',
    stageId: 'negotiation',
    owner: { name: 'Henrique Tavano Sammartino', initials: 'HT', avatarBg: 'bg-blue-600' },
    daysInStage: 3,
    probability: 80,
    createdAt: '4 dias atrás',
    tags: ['Desconto Pontualidade'],
  },
]

export function formatCurrencyBRL(value: number): string {
  return `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function formatCompactCurrencyBRL(value: number): string {
  if (value >= 1_000_000) {
    return `R$ ${(value / 1_000_000).toFixed(1).replace('.', ',')}M`
  }
  if (value >= 1_000) {
    return `R$ ${(value / 1_000).toFixed(1).replace('.', ',')} mil`
  }
  return formatCurrencyBRL(value)
}

export function getChannelBadgeStyle(channel: string): {
  bg: string
  text: string
  border: string
} {
  switch (channel) {
    case 'Meta Ads':
      return { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' }
    case 'Google Orgânico':
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' }
    case 'Google Ads':
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' }
    case 'Indicação':
      return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' }
    case 'Email Marketing':
      return { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' }
    default:
      return { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' }
  }
}
