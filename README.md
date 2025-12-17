# 🚀 CRM Arcsat - Sistema Completo

Sistema completo de CRM (Customer Relationship Management) desenvolvido com **FastAPI + MongoDB** no backend e **React + TypeScript** no frontend.

## 📋 Stack Tecnológica

### Backend
- **FastAPI** - Framework web moderno e rápido
- **MongoDB** - Banco de dados NoSQL (migrado de SQLite)
- **Motor** - Driver assíncrono para MongoDB
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

### Frontend
- **React** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool ultrarrápido
- **Axios** - Cliente HTTP

## 🚀 Funcionalidades

- **Gestão de Clientes**: Cadastro, edição, visualização e exclusão de clientes
- **Gestão de Negócios**: Acompanhamento de oportunidades de vendas com pipeline
- **Gestão de Contatos**: Múltiplos contatos por cliente
- **Gestão de Atividades**: Tarefas, ligações, reuniões, emails e notas
- **API RESTful**: Documentação automática com Swagger
- **MongoDB**: Escalável e flexível para produção
- **Dashboard**: Visão geral do sistema

## 📋 Tecnologias

### Backend

- Python 3.8+
- FastAPI
- SQLAlchemy (ORM)
- SQLite (banco de dados)
- Pydantic (validação de dados)
- Uvicorn (servidor ASGI)

### Frontend

- TypeScript
- React 18
- React Router DOM
- Axios
- Vite
- CSS3

## 🛠️ Instalação e Configuração

### Backend (Python)

1. Navegue até a pasta do backend:

```bash
cd backend
```

2. Crie um ambiente virtual (recomendado):

```bash
python -m venv venv
```

3. Ative o ambiente virtual:

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Inicie o servidor:

```bash
uvicorn main:app --reload
```

O backend estará rodando em: `http://localhost:8000`
Documentação da API: `http://localhost:8000/docs`

### Frontend (TypeScript/React)

1. Navegue até a pasta do frontend:

```bash
cd frontend
```

2. Instale as dependências:

```bash
npm install
```

3. Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

O frontend estará rodando em: `http://localhost:3000`

## 📁 Estrutura do Projeto

```
Arcsat/
├── backend/
│   ├── main.py              # Aplicação principal FastAPI
│   ├── database.py          # Configuração do banco de dados
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── requirements.txt     # Dependências Python
│   └── routers/
│       ├── customers.py     # Rotas de clientes
│       ├── deals.py         # Rotas de negócios
│       ├── contacts.py      # Rotas de contatos
│       └── activities.py    # Rotas de atividades
│
└── frontend/
    ├── src/
    │   ├── components/      # Componentes React
    │   │   ├── Dashboard.tsx
    │   │   ├── Customers.tsx
    │   │   ├── Deals.tsx
    │   │   └── Activities.tsx
    │   ├── services/        # Serviços de API
    │   │   ├── api.ts
    │   │   └── crmService.ts
    │   ├── types/           # Definições TypeScript
    │   │   └── index.ts
    │   ├── App.tsx          # Componente principal
    │   ├── main.tsx         # Ponto de entrada
    │   └── App.css          # Estilos
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## 🔌 API Endpoints

### Clientes

- `GET /api/customers` - Listar todos os clientes
- `GET /api/customers/{id}` - Obter cliente específico
- `POST /api/customers` - Criar novo cliente
- `PUT /api/customers/{id}` - Atualizar cliente
- `DELETE /api/customers/{id}` - Deletar cliente

### Negócios

- `GET /api/deals` - Listar todos os negócios
- `GET /api/deals/{id}` - Obter negócio específico
- `POST /api/deals` - Criar novo negócio
- `PUT /api/deals/{id}` - Atualizar negócio
- `DELETE /api/deals/{id}` - Deletar negócio

### Contatos

- `GET /api/contacts` - Listar todos os contatos
- `GET /api/contacts/{id}` - Obter contato específico
- `POST /api/contacts` - Criar novo contato
- `PUT /api/contacts/{id}` - Atualizar contato
- `DELETE /api/contacts/{id}` - Deletar contato

### Atividades

- `GET /api/activities` - Listar todas as atividades
- `GET /api/activities/{id}` - Obter atividade específica
- `POST /api/activities` - Criar nova atividade
- `PUT /api/activities/{id}` - Atualizar atividade
- `DELETE /api/activities/{id}` - Deletar atividade

## 💡 Uso

1. Inicie o backend (porta 8000)
2. Inicie o frontend (porta 3000)
3. Acesse `http://localhost:3000` no navegador
4. Navegue pelas diferentes seções usando o menu superior
5. Crie, visualize, edite e delete registros conforme necessário

## 🔄 Fluxo de Trabalho

1. **Adicionar Clientes**: Comece cadastrando seus clientes
2. **Criar Negócios**: Registre oportunidades de venda vinculadas aos clientes
3. **Adicionar Contatos**: Cadastre pessoas de contato para cada cliente
4. **Registrar Atividades**: Acompanhe todas as interações e tarefas

## 📝 Licença

Este projeto está sob a licença MIT.
