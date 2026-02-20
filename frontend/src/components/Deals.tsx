import React, { useState, useEffect } from 'react';
import { getDeals, createDeal, deleteDeal, getCustomers } from '../services/crmService';
import { Deal, DealCreate, Customer } from '../types';

const Deals: React.FC = () => {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<DealCreate>({
    title: '',
    description: '',
    value: 0,
    stage: 'prospect',
    customer_id: 0,
    probability: 50,
  });

  useEffect(() => {
    loadDeals();
    loadCustomers();
  }, []);

  const loadDeals = async () => {
    try {
      const data = await getDeals();
      setDeals(data);
    } catch (error) {
      console.error('Erro ao carregar negócios:', error);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createDeal(formData);
      setFormData({
        title: '',
        description: '',
        value: 0,
        stage: 'prospect',
        customer_id: 0,
        probability: 50,
      });
      setShowForm(false);
      loadDeals();
    } catch (error) {
      console.error('Erro ao criar negócio:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Deseja realmente deletar este negócio?')) {
      try {
        await deleteDeal(id);
        loadDeals();
      } catch (error) {
        console.error('Erro ao deletar negócio:', error);
      }
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="deals-page">
      <div className="page-header">
        <h1>Negócios</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : '+ Novo Negócio'}
        </button>
      </div>

      {showForm && (
        <form className="deal-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Título *</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Valor *</label>
            <input
              type="number"
              required
              step="0.01"
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: parseFloat(e.target.value) })}
            />
          </div>
          <div className="form-group">
            <label>Cliente *</label>
            <select
              required
              value={formData.customer_id}
              onChange={(e) => setFormData({ ...formData, customer_id: parseInt(e.target.value) })}
            >
              <option value="">Selecione um cliente</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Estágio</label>
            <select
              value={formData.stage}
              onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
            >
              <option value="prospect">Prospecção</option>
              <option value="qualified">Qualificado</option>
              <option value="proposal">Proposta</option>
              <option value="negotiation">Negociação</option>
              <option value="closed-won">Ganho</option>
              <option value="closed-lost">Perdido</option>
            </select>
          </div>
          <div className="form-group">
            <label>Probabilidade (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.probability}
              onChange={(e) => setFormData({ ...formData, probability: parseInt(e.target.value) })}
            />
          </div>
          <button type="submit" className="btn-primary">Salvar</button>
        </form>
      )}

      <div className="deals-list">
        {deals.map((deal) => (
          <div key={deal.id} className="deal-card">
            <div className="deal-info">
              <h3>{deal.title}</h3>
              <p className="deal-value">{formatCurrency(deal.value)}</p>
              {deal.description && <p>{deal.description}</p>}
              <div className="deal-meta">
                <span className={`stage-badge ${deal.stage}`}>{deal.stage}</span>
                <span className="probability">{deal.probability}% de chance</span>
              </div>
            </div>
            <div className="deal-actions">
              <button className="btn-danger" onClick={() => handleDelete(deal.id)}>
                Deletar
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Deals;
