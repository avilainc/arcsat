import React, { useState, useEffect } from 'react';
import { getActivities, createActivity, deleteActivity, getCustomers, getDeals } from '../services/crmService';
import { Activity, ActivityCreate, Customer, Deal } from '../types';

const Activities: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<ActivityCreate>({
    title: '',
    description: '',
    activity_type: 'task',
    status: 'pending',
    customer_id: 0,
  });

  useEffect(() => {
    loadActivities();
    loadCustomers();
    loadDeals();
  }, []);

  const loadActivities = async () => {
    try {
      const data = await getActivities();
      setActivities(data);
    } catch (error) {
      console.error('Erro ao carregar atividades:', error);
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

  const loadDeals = async () => {
    try {
      const data = await getDeals();
      setDeals(data);
    } catch (error) {
      console.error('Erro ao carregar negócios:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createActivity(formData);
      setFormData({
        title: '',
        description: '',
        activity_type: 'task',
        status: 'pending',
        customer_id: 0,
      });
      setShowForm(false);
      loadActivities();
    } catch (error) {
      console.error('Erro ao criar atividade:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Deseja realmente deletar esta atividade?')) {
      try {
        await deleteActivity(id);
        loadActivities();
      } catch (error) {
        console.error('Erro ao deletar atividade:', error);
      }
    }
  };

  return (
    <div className="activities-page">
      <div className="page-header">
        <h1>Atividades</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : '+ Nova Atividade'}
        </button>
      </div>

      {showForm && (
        <form className="activity-form" onSubmit={handleSubmit}>
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
            <label>Tipo *</label>
            <select
              value={formData.activity_type}
              onChange={(e) => setFormData({ ...formData, activity_type: e.target.value })}
            >
              <option value="call">Ligação</option>
              <option value="meeting">Reunião</option>
              <option value="email">Email</option>
              <option value="task">Tarefa</option>
              <option value="note">Nota</option>
            </select>
          </div>
          <div className="form-group">
            <label>Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <option value="pending">Pendente</option>
              <option value="completed">Completa</option>
              <option value="cancelled">Cancelada</option>
            </select>
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
            <label>Negócio (opcional)</label>
            <select
              value={formData.deal_id || ''}
              onChange={(e) => setFormData({ ...formData, deal_id: e.target.value ? parseInt(e.target.value) : undefined })}
            >
              <option value="">Nenhum</option>
              {deals.map((deal) => (
                <option key={deal.id} value={deal.id}>
                  {deal.title}
                </option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn-primary">Salvar</button>
        </form>
      )}

      <div className="activities-list">
        {activities.map((activity) => (
          <div key={activity.id} className="activity-card">
            <div className="activity-info">
              <h3>{activity.title}</h3>
              {activity.description && <p>{activity.description}</p>}
              <div className="activity-meta">
                <span className={`type-badge ${activity.activity_type}`}>{activity.activity_type}</span>
                <span className={`status-badge ${activity.status}`}>{activity.status}</span>
              </div>
            </div>
            <div className="activity-actions">
              <button className="btn-danger" onClick={() => handleDelete(activity.id)}>
                Deletar
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Activities;
