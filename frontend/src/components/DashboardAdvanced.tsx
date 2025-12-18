import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface DashboardStats {
  customers: {
    total: number;
    leads: number;
    prospects: number;
    clientes: number;
    inativos: number;
    new_this_month: number;
    conversion_rate: number;
  };
  deals: {
    total: number;
    open: number;
    won: number;
    lost: number;
    total_open_value: number;
    won_this_month: number;
  };
  activities: {
    pending: number;
  };
  interactions: {
    this_week: number;
  };
  top_customers: Array<{
    id: string;
    name: string;
    email: string;
    valor_contrato: number;
  }>;
}

interface Alert {
  type: string;
  priority: string;
  message: string;
  customer_id?: string;
  activity_id?: string;
}

const DashboardAdvanced: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [statsRes, alertsRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/dashboard/alerts')
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const runAutomation = async (type: string) => {
    try {
      let endpoint = '';
      switch (type) {
        case 'score':
          endpoint = '/automation/score-leads';
          break;
        case 'convert':
          endpoint = '/automation/convert-hot-leads';
          break;
        case 'inactive':
          endpoint = '/automation/inactive-customer-alert';
          break;
        case 'renewal':
          endpoint = '/automation/contract-renewal-reminder';
          break;
      }
      
      const res = await api.post(endpoint);
      alert(res.data.message);
      loadDashboard();
    } catch (error) {
      console.error('Erro ao executar automação:', error);
      alert('Erro ao executar automação');
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: any = {
      high: 'bg-red-100 text-red-800 border-red-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-blue-100 text-blue-800 border-blue-300'
    };
    return colors[priority] || colors.low;
  };

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Carregando dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard Avançado</h1>
        <p className="text-gray-600">Visão geral do seu CRM</p>
      </div>

      {/* KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Total de Clientes</p>
              <h3 className="text-3xl font-bold text-gray-800">{stats.customers.total}</h3>
              <p className="text-sm text-green-600 mt-1">
                +{stats.customers.new_this_month} este mês
              </p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Deals Abertos</p>
              <h3 className="text-3xl font-bold text-gray-800">{stats.deals.open}</h3>
              <p className="text-sm text-gray-600 mt-1">
                R$ {stats.deals.total_open_value.toLocaleString('pt-BR')}
              </p>
            </div>
            <div className="text-4xl">💼</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Taxa de Conversão</p>
              <h3 className="text-3xl font-bold text-gray-800">
                {stats.customers.conversion_rate.toFixed(1)}%
              </h3>
              <p className="text-sm text-gray-600 mt-1">Lead → Cliente</p>
            </div>
            <div className="text-4xl">📈</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Ganho Este Mês</p>
              <h3 className="text-3xl font-bold text-green-600">
                R$ {stats.deals.won_this_month.toLocaleString('pt-BR')}
              </h3>
              <p className="text-sm text-gray-600 mt-1">{stats.deals.won} deals</p>
            </div>
            <div className="text-4xl">💰</div>
          </div>
        </div>
      </div>

      {/* Distribuição de Clientes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Distribuição de Clientes</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Leads</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-gray-200 rounded">
                  <div 
                    className="h-full bg-blue-500 rounded" 
                    style={{width: `${(stats.customers.leads/stats.customers.total)*100}%`}}
                  ></div>
                </div>
                <span className="font-semibold w-12 text-right">{stats.customers.leads}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Prospects</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-gray-200 rounded">
                  <div 
                    className="h-full bg-yellow-500 rounded" 
                    style={{width: `${(stats.customers.prospects/stats.customers.total)*100}%`}}
                  ></div>
                </div>
                <span className="font-semibold w-12 text-right">{stats.customers.prospects}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Clientes</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-gray-200 rounded">
                  <div 
                    className="h-full bg-green-500 rounded" 
                    style={{width: `${(stats.customers.clientes/stats.customers.total)*100}%`}}
                  ></div>
                </div>
                <span className="font-semibold w-12 text-right">{stats.customers.clientes}</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Inativos</span>
              <div className="flex items-center gap-2">
                <div className="w-32 h-2 bg-gray-200 rounded">
                  <div 
                    className="h-full bg-gray-400 rounded" 
                    style={{width: `${(stats.customers.inativos/stats.customers.total)*100}%`}}
                  ></div>
                </div>
                <span className="font-semibold w-12 text-right">{stats.customers.inativos}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Atividades Recentes</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded">
              <div>
                <p className="font-semibold text-gray-800">Atividades Pendentes</p>
                <p className="text-sm text-gray-600">Tarefas aguardando conclusão</p>
              </div>
              <span className="text-2xl font-bold text-yellow-600">{stats.activities.pending}</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
              <div>
                <p className="font-semibold text-gray-800">Interações Esta Semana</p>
                <p className="text-sm text-gray-600">Contatos realizados</p>
              </div>
              <span className="text-2xl font-bold text-blue-600">{stats.interactions.this_week}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Automações */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h3 className="text-lg font-semibold mb-4">🤖 Automações</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button
            onClick={() => runAutomation('score')}
            className="p-4 border-2 border-blue-300 rounded-lg hover:bg-blue-50 transition"
          >
            <div className="text-3xl mb-2">📊</div>
            <p className="font-semibold">Calcular Scores</p>
            <p className="text-sm text-gray-600">Avaliar todos os leads</p>
          </button>
          
          <button
            onClick={() => runAutomation('convert')}
            className="p-4 border-2 border-green-300 rounded-lg hover:bg-green-50 transition"
          >
            <div className="text-3xl mb-2">🚀</div>
            <p className="font-semibold">Converter Hot Leads</p>
            <p className="text-sm text-gray-600">Score >= 70</p>
          </button>
          
          <button
            onClick={() => runAutomation('inactive')}
            className="p-4 border-2 border-yellow-300 rounded-lg hover:bg-yellow-50 transition"
          >
            <div className="text-3xl mb-2">⚠️</div>
            <p className="font-semibold">Alertar Inativos</p>
            <p className="text-sm text-gray-600">30+ dias sem contato</p>
          </button>
          
          <button
            onClick={() => runAutomation('renewal')}
            className="p-4 border-2 border-purple-300 rounded-lg hover:bg-purple-50 transition"
          >
            <div className="text-3xl mb-2">📅</div>
            <p className="font-semibold">Renovação</p>
            <p className="text-sm text-gray-600">Contratos expirando</p>
          </button>
        </div>
      </div>

      {/* Alertas */}
      {alerts.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h3 className="text-lg font-semibold mb-4">🔔 Alertas e Lembretes</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {alerts.map((alert, idx) => (
              <div 
                key={idx} 
                className={`p-3 border-l-4 rounded ${getPriorityColor(alert.priority)}`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{alert.message}</p>
                    <p className="text-xs text-gray-600 mt-1">
                      {alert.type.replace('_', ' ').toUpperCase()}
                    </p>
                  </div>
                  {alert.priority === 'high' && (
                    <span className="text-red-600 font-bold">!</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Clientes */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">🏆 Top Clientes por Contrato</h3>
        <div className="space-y-3">
          {stats.top_customers.map((customer, idx) => (
            <div key={customer.id} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded">
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                <div>
                  <p className="font-semibold">{customer.name}</p>
                  <p className="text-sm text-gray-600">{customer.email}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-green-600">
                  R$ {customer.valor_contrato.toLocaleString('pt-BR')}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardAdvanced;
