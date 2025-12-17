import React, { useState, useEffect } from 'react';
import { getCustomers, createCustomer, deleteCustomer } from '../services/crmService';
import { Customer, CustomerCreate } from '../types';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<CustomerCreate>({
    name: '',
    email: '',
    phone: '',
    company: '',
    status: 'active'
  });

  useEffect(() => {
    loadCustomers();
  }, []);

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
      await createCustomer(formData);
      setFormData({ name: '', email: '', phone: '', company: '', status: 'active' });
      setShowForm(false);
      loadCustomers();
    } catch (error) {
      console.error('Erro ao criar cliente:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Deseja realmente deletar este cliente?')) {
      try {
        await deleteCustomer(id);
        loadCustomers();
      } catch (error) {
        console.error('Erro ao deletar cliente:', error);
      }
    }
  };

  return (
    <div className="customers-page">
      <div className="page-header">
        <h1>Clientes</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : '+ Novo Cliente'}
        </button>
      </div>

      {showForm && (
        <form className="customer-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nome *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Telefone</label>
            <input
              type="text"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Empresa</label>
            <input
              type="text"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <option value="active">Ativo</option>
              <option value="inactive">Inativo</option>
              <option value="lead">Lead</option>
            </select>
          </div>
          <button type="submit" className="btn-primary">Salvar</button>
        </form>
      )}

      <div className="customers-list">
        {customers.map((customer) => (
          <div key={customer.id} className="customer-card">
            <div className="customer-info">
              <h3>{customer.name}</h3>
              <p>Email: {customer.email}</p>
              {customer.phone && <p>Telefone: {customer.phone}</p>}
              {customer.company && <p>Empresa: {customer.company}</p>}
              <span className={`status-badge ${customer.status}`}>{customer.status}</span>
            </div>
            <div className="customer-actions">
              <button className="btn-danger" onClick={() => handleDelete(customer.id)}>
                Deletar
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Customers;
