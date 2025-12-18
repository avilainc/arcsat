import React, { useState, useEffect } from 'react';
import {
  getCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  getCNPJData,
  getCEPData,
  getCustomerNotes,
  createNote,
  deleteNote,
  togglePinNote,
  getCustomerInteractions,
  createInteraction,
  deleteInteraction,
  getCustomerAttachments,
  uploadAttachment,
  deleteAttachment
} from '../services/crmService';
import { Customer, CustomerCreate } from '../types';

const CustomersAdvanced: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [activeTab, setActiveTab] = useState('geral'); // geral, notas, historico, anexos
  const [loadingCNPJ, setLoadingCNPJ] = useState(false);
  const [loadingCEP, setLoadingCEP] = useState(false);
  
  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('todos');
  const [filterCategoria, setFilterCategoria] = useState('todos');
  
  // Estados para notas, interações e anexos
  const [notes, setNotes] = useState<any[]>([]);
  const [interactions, setInteractions] = useState<any[]>([]);
  const [attachments, setAttachments] = useState<any[]>([]);
  const [newNote, setNewNote] = useState('');
  const [newInteraction, setNewInteraction] = useState({
    tipo: 'email',
    titulo: '',
    descricao: '',
    data: new Date().toISOString(),
    responsavel: '',
    resultado: 'pendente'
  });

  const [formData, setFormData] = useState<CustomerCreate>({
    name: '',
    email: '',
    phone: '',
    company: '',
    status: 'lead',
    cnpj: '',
    cep: '',
    categoria: '',
    segmento: '',
    tags: [],
    origem: '',
    responsavel: '',
    observacoes: ''
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  useEffect(() => {
    filterCustomers();
  }, [customers, searchTerm, filterStatus, filterCategoria]);

  const loadCustomers = async () => {
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    }
  };

  const filterCustomers = () => {
    let filtered = customers;

    // Filtro por busca
    if (searchTerm) {
      filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.cnpj?.includes(searchTerm)
      );
    }

    // Filtro por status
    if (filterStatus !== 'todos') {
      filtered = filtered.filter(c => c.status === filterStatus);
    }

    // Filtro por categoria
    if (filterCategoria !== 'todos') {
      filtered = filtered.filter(c => c.categoria === filterCategoria);
    }

    setFilteredCustomers(filtered);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedCustomer) {
        await updateCustomer(selectedCustomer.id, formData);
      } else {
        await createCustomer(formData);
      }
      resetForm();
      loadCustomers();
    } catch (error) {
      console.error('Erro ao salvar cliente:', error);
      alert('Erro ao salvar cliente');
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Deseja realmente deletar este cliente?')) {
      try {
        await deleteCustomer(parseInt(id));
        loadCustomers();
      } catch (error) {
        console.error('Erro ao deletar cliente:', error);
      }
    }
  };

  const handleEdit = (customer: Customer) => {
    setSelectedCustomer(customer);
    setFormData(customer as any);
    setShowForm(true);
  };

  const handleViewDetails = async (customer: Customer) => {
    setSelectedCustomer(customer);
    setShowDetails(true);
    setActiveTab('geral');
    
    // Carregar dados adicionais
    try {
      const [notesData, interactionsData, attachmentsData] = await Promise.all([
        getCustomerNotes(customer.id),
        getCustomerInteractions(customer.id),
        getCustomerAttachments(customer.id)
      ]);
      setNotes(notesData);
      setInteractions(interactionsData);
      setAttachments(attachmentsData);
    } catch (error) {
      console.error('Erro ao carregar detalhes:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      company: '',
      status: 'lead',
      cnpj: '',
      cep: '',
      categoria: '',
      segmento: '',
      tags: [],
      origem: '',
      responsavel: '',
      observacoes: ''
    });
    setSelectedCustomer(null);
    setShowForm(false);
  };

  const handleCNPJChange = async (value: string) => {
    const cnpjClean = value.replace(/\D/g, '');
    setFormData({ ...formData, cnpj: value });

    if (cnpjClean.length === 14) {
      setLoadingCNPJ(true);
      try {
        const data = await getCNPJData(cnpjClean);
        setFormData(prev => ({
          ...prev,
          razao_social: data.razao_social,
          nome_fantasia: data.nome_fantasia,
          company: data.nome_fantasia || data.razao_social,
          name: data.nome_fantasia || data.razao_social,
          email: data.email || prev.email,
          phone: data.telefone || prev.phone,
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
        }));
      } catch (error) {
        console.error('Erro ao buscar CNPJ:', error);
        alert('CNPJ não encontrado');
      } finally {
        setLoadingCNPJ(false);
      }
    }
  };

  const handleCEPChange = async (value: string) => {
    const cepClean = value.replace(/\D/g, '');
    setFormData({ ...formData, cep: value });

    if (cepClean.length === 8) {
      setLoadingCEP(true);
      try {
        const data = await getCEPData(cepClean);
        setFormData(prev => ({
          ...prev,
          logradouro: data.logradouro,
          bairro: data.bairro,
          municipio: data.municipio,
          uf: data.uf
        }));
      } catch (error) {
        console.error('Erro ao buscar CEP:', error);
      } finally {
        setLoadingCEP(false);
      }
    }
  };

  const handleAddNote = async () => {
    if (!selectedCustomer || !newNote.trim()) return;
    
    try {
      await createNote({
        customer_id: selectedCustomer.id,
        content: newNote,
        author: 'Sistema'
      });
      setNewNote('');
      const notesData = await getCustomerNotes(selectedCustomer.id);
      setNotes(notesData);
    } catch (error) {
      console.error('Erro ao adicionar nota:', error);
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    try {
      await deleteNote(noteId);
      const notesData = await getCustomerNotes(selectedCustomer!.id);
      setNotes(notesData);
    } catch (error) {
      console.error('Erro ao deletar nota:', error);
    }
  };

  const handlePinNote = async (noteId: string) => {
    try {
      await togglePinNote(noteId);
      const notesData = await getCustomerNotes(selectedCustomer!.id);
      setNotes(notesData);
    } catch (error) {
      console.error('Erro ao fixar nota:', error);
    }
  };

  const handleAddInteraction = async () => {
    if (!selectedCustomer || !newInteraction.titulo.trim()) return;
    
    try {
      await createInteraction({
        ...newInteraction,
        customer_id: selectedCustomer.id
      });
      setNewInteraction({
        tipo: 'email',
        titulo: '',
        descricao: '',
        data: new Date().toISOString(),
        responsavel: '',
        resultado: 'pendente'
      });
      const interactionsData = await getCustomerInteractions(selectedCustomer.id);
      setInteractions(interactionsData);
    } catch (error) {
      console.error('Erro ao adicionar interação:', error);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedCustomer || !e.target.files?.[0]) return;
    
    try {
      const file = e.target.files[0];
      await uploadAttachment(selectedCustomer.id, file);
      const attachmentsData = await getCustomerAttachments(selectedCustomer.id);
      setAttachments(attachmentsData);
      alert('Arquivo enviado com sucesso!');
    } catch (error) {
      console.error('Erro ao enviar arquivo:', error);
      alert('Erro ao enviar arquivo');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors: any = {
      lead: 'bg-blue-100 text-blue-800',
      prospect: 'bg-yellow-100 text-yellow-800',
      cliente: 'bg-green-100 text-green-800',
      inativo: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors.lead;
  };

  const exportToCSV = () => {
    const headers = ['Nome', 'Email', 'Telefone', 'Empresa', 'Status', 'CNPJ', 'Cidade'];
    const data = filteredCustomers.map(c => [
      c.name,
      c.email || '',
      c.phone || '',
      c.company || '',
      c.status,
      c.cnpj || '',
      c.municipio || ''
    ]);
    
    const csv = [headers, ...data].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'clientes.csv';
    a.click();
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Clientes</h1>
        <div className="flex gap-2">
          <button
            onClick={exportToCSV}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            📊 Exportar CSV
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Novo Cliente
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="🔍 Buscar por nome, email, empresa..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="border rounded px-3 py-2"
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="todos">Todos os Status</option>
            <option value="lead">Lead</option>
            <option value="prospect">Prospect</option>
            <option value="cliente">Cliente</option>
            <option value="inativo">Inativo</option>
          </select>
          <select
            value={filterCategoria}
            onChange={(e) => setFilterCategoria(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="todos">Todas Categorias</option>
            <option value="pequeno">Pequeno</option>
            <option value="medio">Médio</option>
            <option value="grande">Grande</option>
          </select>
          <div className="text-sm text-gray-600 flex items-center">
            Total: <strong className="ml-2">{filteredCustomers.length}</strong> clientes
          </div>
        </div>
      </div>

      {/* Lista de Clientes */}
      <div className="grid grid-cols-1 gap-4">
        {filteredCustomers.map((customer) => (
          <div key={customer.id} className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold">{customer.name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(customer.status)}`}>
                    {customer.status.toUpperCase()}
                  </span>
                  {customer.categoria && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                      {customer.categoria}
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
                  <div>📧 {customer.email}</div>
                  <div>📱 {customer.phone || 'N/A'}</div>
                  <div>🏢 {customer.company || 'N/A'}</div>
                  <div>📍 {customer.municipio ? `${customer.municipio}/${customer.uf}` : 'N/A'}</div>
                </div>
                {customer.tags && customer.tags.length > 0 && (
                  <div className="flex gap-2 mt-2">
                    {customer.tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-50 text-blue-600 rounded text-xs">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleViewDetails(customer)}
                  className="text-blue-600 hover:text-blue-800 px-3 py-1 border border-blue-600 rounded"
                >
                  👁️ Ver
                </button>
                <button
                  onClick={() => handleEdit(customer)}
                  className="text-yellow-600 hover:text-yellow-800 px-3 py-1 border border-yellow-600 rounded"
                >
                  ✏️ Editar
                </button>
                <button
                  onClick={() => handleDelete(customer.id)}
                  className="text-red-600 hover:text-red-800 px-3 py-1 border border-red-600 rounded"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de Formulário */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {selectedCustomer ? 'Editar Cliente' : 'Novo Cliente'}
            </h2>
            <form onSubmit={handleSubmit}>
              {/* Seção: Dados Principais */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-blue-600">📋 Dados Principais</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">CNPJ *</label>
                    <input
                      type="text"
                      value={formData.cnpj || ''}
                      onChange={(e) => handleCNPJChange(e.target.value)}
                      className="w-full border rounded px-3 py-2"
                      placeholder="00.000.000/0000-00"
                      maxLength={18}
                    />
                    {loadingCNPJ && <p className="text-sm text-blue-600 mt-1">🔄 Buscando dados...</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Status *</label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    >
                      <option value="lead">Lead</option>
                      <option value="prospect">Prospect</option>
                      <option value="cliente">Cliente</option>
                      <option value="inativo">Inativo</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Razão Social *</label>
                    <input
                      type="text"
                      value={formData.razao_social || ''}
                      onChange={(e) => setFormData({ ...formData, razao_social: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="Razão Social"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Nome Fantasia</label>
                    <input
                      type="text"
                      value={formData.nome_fantasia || ''}
                      onChange={(e) => setFormData({ ...formData, nome_fantasia: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="Nome Fantasia"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Email *</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Telefone</label>
                    <input
                      type="text"
                      value={formData.phone || ''}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="(00) 00000-0000"
                    />
                  </div>
                </div>
              </div>

              {/* Seção: Endereço */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-green-600">📍 Endereço</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">CEP</label>
                    <input
                      type="text"
                      value={formData.cep || ''}
                      onChange={(e) => handleCEPChange(e.target.value)}
                      className="w-full border rounded px-3 py-2"
                      placeholder="00000-000"
                      maxLength={9}
                    />
                    {loadingCEP && <p className="text-sm text-blue-600 mt-1">🔄 Buscando CEP...</p>}
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-1">Logradouro</label>
                    <input
                      type="text"
                      value={formData.logradouro || ''}
                      onChange={(e) => setFormData({ ...formData, logradouro: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Número</label>
                    <input
                      type="text"
                      value={formData.numero || ''}
                      onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Bairro</label>
                    <input
                      type="text"
                      value={formData.bairro || ''}
                      onChange={(e) => setFormData({ ...formData, bairro: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Cidade</label>
                    <input
                      type="text"
                      value={formData.municipio || ''}
                      onChange={(e) => setFormData({ ...formData, municipio: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">UF</label>
                    <input
                      type="text"
                      value={formData.uf || ''}
                      onChange={(e) => setFormData({ ...formData, uf: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      maxLength={2}
                    />
                  </div>
                </div>
              </div>

              {/* Seção: Categorização */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-purple-600">🏷️ Categorização</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Categoria</label>
                    <select
                      value={formData.categoria || ''}
                      onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione...</option>
                      <option value="pequeno">Pequeno</option>
                      <option value="medio">Médio</option>
                      <option value="grande">Grande</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Segmento</label>
                    <input
                      type="text"
                      value={formData.segmento || ''}
                      onChange={(e) => setFormData({ ...formData, segmento: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      placeholder="Tecnologia, Saúde, Educação..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Origem</label>
                    <select
                      value={formData.origem || ''}
                      onChange={(e) => setFormData({ ...formData, origem: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione...</option>
                      <option value="site">Site</option>
                      <option value="indicacao">Indicação</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="evento">Evento</option>
                      <option value="cold_call">Cold Call</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Seção: Observações */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-orange-600">📝 Observações</h3>
                <textarea
                  value={formData.observacoes || ''}
                  onChange={(e) => setFormData({ ...formData, observacoes: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  rows={4}
                  placeholder="Observações gerais sobre o cliente..."
                />
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 border rounded hover:bg-gray-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {selectedCustomer ? 'Atualizar' : 'Criar'} Cliente
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Detalhes */}
      {showDetails && selectedCustomer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-5xl w-full max-h-screen overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold">{selectedCustomer.name}</h2>
                <p className="text-gray-600">{selectedCustomer.email}</p>
              </div>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-600 hover:text-gray-800"
              >
                ✖️
              </button>
            </div>

            {/* Tabs */}
            <div className="border-b mb-4">
              <div className="flex gap-4">
                {['geral', 'notas', 'historico', 'anexos'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`pb-2 px-4 ${
                      activeTab === tab
                        ? 'border-b-2 border-blue-600 text-blue-600 font-semibold'
                        : 'text-gray-600'
                    }`}
                  >
                    {tab === 'geral' && '📋 Geral'}
                    {tab === 'notas' && '📝 Notas'}
                    {tab === 'historico' && '📅 Histórico'}
                    {tab === 'anexos' && '📎 Anexos'}
                  </button>
                ))}
              </div>
            </div>

            {/* Conteúdo das Tabs */}
            <div>
              {activeTab === 'geral' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <strong>Status:</strong> {selectedCustomer.status}
                  </div>
                  <div>
                    <strong>CNPJ:</strong> {selectedCustomer.cnpj || 'N/A'}
                  </div>
                  <div>
                    <strong>Telefone:</strong> {selectedCustomer.phone || 'N/A'}
                  </div>
                  <div>
                    <strong>Empresa:</strong> {selectedCustomer.company || 'N/A'}
                  </div>
                  <div className="col-span-2">
                    <strong>Endereço:</strong> {selectedCustomer.logradouro || 'N/A'}
                  </div>
                </div>
              )}

              {activeTab === 'notas' && (
                <div>
                  <div className="mb-4">
                    <textarea
                      value={newNote}
                      onChange={(e) => setNewNote(e.target.value)}
                      className="w-full border rounded px-3 py-2"
                      rows={3}
                      placeholder="Escreva uma nota..."
                    />
                    <button
                      onClick={handleAddNote}
                      className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      ➕ Adicionar Nota
                    </button>
                  </div>
                  <div className="space-y-3">
                    {notes.map((note) => (
                      <div key={note.id} className="border rounded p-3 bg-gray-50">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            {note.pinned && <span className="text-yellow-500">📌 </span>}
                            <p className="text-sm">{note.content}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(note.created_at).toLocaleString('pt-BR')}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => handlePinNote(note.id)}
                              className="text-yellow-600 hover:text-yellow-800"
                            >
                              📌
                            </button>
                            <button
                              onClick={() => handleDeleteNote(note.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'historico' && (
                <div>
                  <div className="mb-4 bg-gray-50 p-4 rounded">
                    <h4 className="font-semibold mb-2">Nova Interação</h4>
                    <div className="grid grid-cols-2 gap-3">
                      <select
                        value={newInteraction.tipo}
                        onChange={(e) => setNewInteraction({ ...newInteraction, tipo: e.target.value })}
                        className="border rounded px-3 py-2"
                      >
                        <option value="email">Email</option>
                        <option value="telefone">Telefone</option>
                        <option value="reuniao">Reunião</option>
                        <option value="whatsapp">WhatsApp</option>
                        <option value="proposta">Proposta</option>
                      </select>
                      <input
                        type="text"
                        value={newInteraction.titulo}
                        onChange={(e) => setNewInteraction({ ...newInteraction, titulo: e.target.value })}
                        placeholder="Título da interação"
                        className="border rounded px-3 py-2"
                      />
                      <textarea
                        value={newInteraction.descricao}
                        onChange={(e) => setNewInteraction({ ...newInteraction, descricao: e.target.value })}
                        placeholder="Descrição"
                        className="border rounded px-3 py-2 col-span-2"
                        rows={2}
                      />
                      <select
                        value={newInteraction.resultado}
                        onChange={(e) => setNewInteraction({ ...newInteraction, resultado: e.target.value })}
                        className="border rounded px-3 py-2"
                      >
                        <option value="pendente">Pendente</option>
                        <option value="positivo">Positivo</option>
                        <option value="negativo">Negativo</option>
                        <option value="neutro">Neutro</option>
                      </select>
                      <button
                        onClick={handleAddInteraction}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                      >
                        ➕ Adicionar
                      </button>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {interactions.map((interaction) => (
                      <div key={interaction.id} className="border-l-4 border-blue-600 pl-4 py-2">
                        <div className="flex justify-between">
                          <div>
                            <strong>{interaction.titulo}</strong>
                            <span className="ml-2 text-xs bg-gray-200 px-2 py-1 rounded">
                              {interaction.tipo}
                            </span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {new Date(interaction.data).toLocaleDateString('pt-BR')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{interaction.descricao}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'anexos' && (
                <div>
                  <div className="mb-4">
                    <input
                      type="file"
                      onChange={handleFileUpload}
                      className="border rounded px-3 py-2"
                    />
                  </div>
                  <div className="space-y-2">
                    {attachments.map((attachment) => (
                      <div key={attachment.id} className="flex justify-between items-center border p-3 rounded">
                        <div>
                          <strong>{attachment.filename}</strong>
                          <p className="text-sm text-gray-600">
                            {(attachment.file_size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                        <button
                          onClick={() => deleteAttachment(attachment.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomersAdvanced;
