import React, { useState, useEffect } from 'react';
import { getCustomers, createCustomer, deleteCustomer, getCNPJData } from '../services/crmService';
import { Customer, CustomerCreate } from '../types';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loadingCNPJ, setLoadingCNPJ] = useState(false);
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

  const formatCNPJ = (value: string) => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length <= 14) {
      return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return value;
  };

  const handleCNPJChange = async (value: string) => {
    const cnpjClean = value.replace(/\D/g, '');
    setFormData({ ...formData, cnpj: formatCNPJ(value) });

    // Se CNPJ tiver 14 dígitos, buscar dados
    if (cnpjClean.length === 14) {
      setLoadingCNPJ(true);
      try {
        const data = await getCNPJData(cnpjClean);
        setFormData({
          ...formData,
          cnpj: formatCNPJ(data.cnpj),
          razao_social: data.razao_social,
          nome_fantasia: data.nome_fantasia || '',
          company: data.nome_fantasia || data.razao_social,
          name: data.nome_fantasia || data.razao_social,
          email: data.email || formData.email,
          phone: data.telefone || formData.phone,
          porte: data.porte,
          natureza_juridica: data.natureza_juridica,
          capital_social: data.capital_social,
          cep: data.cep,
          logradouro: data.logradouro,
          numero: data.numero,
          complemento: data.complemento,
          bairro: data.bairro,
          municipio: data.municipio,
          uf: data.uf,
          atividade_principal: data.atividade_principal,
          data_abertura: data.data_abertura,
          situacao: data.situacao,
        });
      } catch (error) {
        console.error('Erro ao buscar CNPJ:', error);
        alert('CNPJ não encontrado ou erro na consulta');
      } finally {
        setLoadingCNPJ(false);
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
            <label>CNPJ {loadingCNPJ && '(Buscando...)'}</label>
            <input
              type="text"
              placeholder="00.000.000/0000-00"
              maxLength={18}
              value={formData.cnpj || ''}
              onChange={(e) => handleCNPJChange(e.target.value)}
            />
          </div>
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

          {formData.razao_social && (
            <>
              <div className="form-group">
                <label>Razão Social</label>
                <input type="text" value={formData.razao_social} readOnly />
              </div>
              <div className="form-group">
                <label>Nome Fantasia</label>
                <input type="text" value={formData.nome_fantasia || ''} readOnly />
              </div>
              <div className="form-group">
                <label>Endereço</label>
                <input
                  type="text"
                  value={`${formData.logradouro || ''}, ${formData.numero || ''} - ${formData.bairro || ''}, ${formData.municipio || ''}/${formData.uf || ''}`}
                  readOnly
                />
              </div>
              <div className="form-group">
                <label>CEP</label>
                <input type="text" value={formData.cep || ''} readOnly />
              </div>
              <div className="form-group">
                <label>Atividade Principal</label>
                <input type="text" value={formData.atividade_principal || ''} readOnly />
              </div>
              <div className="form-group">
                <label>Porte</label>
                <input type="text" value={formData.porte || ''} readOnly />
              </div>
              <div className="form-group">
                <label>Situação Cadastral</label>
                <input type="text" value={formData.situacao || ''} readOnly />
              </div>
            </>
          )}

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
          <button type="submit" className="btn-primary" disabled={loadingCNPJ}>
            {loadingCNPJ ? 'Aguarde...' : 'Salvar'}
          </button>
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
