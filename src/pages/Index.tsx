/* CRM Oficial — Página inicial: lista de leads do PocketBase */
import { useEffect, useState } from 'react'
import pb from '@/lib/pocketbase/client'

interface Lead {
  id: string
  lead_id: string
  opportunity_id: string
  nome: string
  email: string
  telefone: string
  origem: string
  campanha: string
  estagio: string
  responsavel: string
  created: string
  updated: string
}

const estagioColors: Record<string, string> = {
  capturado: 'bg-blue-100 text-blue-800',
  aguardando_dados: 'bg-yellow-100 text-yellow-800',
  encerrado_entrada_invalida: 'bg-red-100 text-red-800',
}

const origemColors: Record<string, string> = {
  meta_ads: 'bg-purple-100 text-purple-800',
  cora: 'bg-green-100 text-green-800',
  indicacao: 'bg-orange-100 text-orange-800',
  manual: 'bg-gray-100 text-gray-800',
}

const Index = () => {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Verificar se há usuário logado
    const currentUser = pb.authStore.model
    if (currentUser) {
      setUser(currentUser)
    }

    // Buscar leads
    fetchLeads()
  }, [])

  const fetchLeads = async () => {
    try {
      setLoading(true)
      const records = await pb.collection('leads').getFullList({
        sort: '-created',
      })
      setLeads(records as unknown as Lead[])
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar leads')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    try {
      await pb
        .collection('users')
        .authWithPassword('vinicius@terceirizou.com.br', 'Terceirizou@2026')
      setUser(pb.authStore.model)
      fetchLeads()
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer login')
    }
  }

  const handleLogout = () => {
    pb.authStore.clear()
    setUser(null)
    setLeads([])
  }

  // Tela de login
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">CRM Oficial</h1>
            <p className="mt-2 text-gray-600">Terceirizou — BPO Financeiro</p>
          </div>
          <div className="mt-8 space-y-4">
            <button
              onClick={handleLogin}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Entrar como Administrador
            </button>
            {error && <div className="text-red-600 text-sm text-center">{error}</div>}
          </div>
        </div>
      </div>
    )
  }

  // Tela principal — lista de leads
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">CRM Oficial</h1>
            <p className="text-sm text-gray-500">Terceirizou — BPO Financeiro</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user.name || user.email}</span>
            <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-800">
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Conteúdo */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Resumo */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Total de Leads</div>
            <div className="text-2xl font-bold text-gray-900">{leads.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Capturados</div>
            <div className="text-2xl font-bold text-blue-600">
              {leads.filter((l) => l.estagio === 'capturado').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Aguardando Dados</div>
            <div className="text-2xl font-bold text-yellow-600">
              {leads.filter((l) => l.estagio === 'aguardando_dados').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Encerrados</div>
            <div className="text-2xl font-bold text-red-600">
              {leads.filter((l) => l.estagio === 'encerrado_entrada_invalida').length}
            </div>
          </div>
        </div>

        {/* Tabela de leads */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Leads</h2>
            <button onClick={fetchLeads} className="text-sm text-indigo-600 hover:text-indigo-800">
              Atualizar
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center text-gray-500">Carregando...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">{error}</div>
          ) : leads.length === 0 ? (
            <div className="p-8 text-center text-gray-500">Nenhum lead encontrado</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nome
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Telefone
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Origem
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estágio
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Responsável
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Criado em
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {lead.nome}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.email || '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.telefone || '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${origemColors[lead.origem] || 'bg-gray-100 text-gray-800'}`}
                        >
                          {lead.origem}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estagioColors[lead.estagio] || 'bg-gray-100 text-gray-800'}`}
                        >
                          {lead.estagio}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.responsavel}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lead.created).toLocaleDateString('pt-BR')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default Index
