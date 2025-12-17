# 🚀 CRM Arcsat - MongoDB & Railway Setup

## ✅ O que foi feito

### 1. Backend migrado para MongoDB
- ✅ Removido SQLAlchemy e SQLite
- ✅ Instalado pymongo, motor (async MongoDB driver)
- ✅ Atualizado database.py com configuração MongoDB
- ✅ Convertido todos os models para MongoDB
- ✅ Atualizado todos os schemas para usar ObjectId
- ✅ Convertido todos os routers para operações assíncronas
- ✅ Configurado variáveis de ambiente (.env)

### 2. Frontend preparado para Railway
- ✅ Configurado VITE_API_URL dinâmico
- ✅ Adicionado interceptors para logging
- ✅ Criado arquivos .env para diferentes ambientes
- ✅ Adicionado tipos TypeScript para variáveis Vite

### 3. Railway Deploy Files
- ✅ Criado railway.toml para backend e frontend
- ✅ Documentação completa de deploy (RAILWAY_DEPLOY.md)

## 📝 Próximos Passos

### Passo 1: Testar Localmente com MongoDB

1. **Instalar MongoDB localmente** (se ainda não tiver):
   - Windows: Baixe em https://www.mongodb.com/try/download/community
   - Ou use MongoDB Atlas (cloud gratuito)

2. **Configurar .env do backend**:
   ```bash
   cd D:\Arcsat\backend
   # Edite o .env e ajuste a MONGODB_URL se necessário
   ```

3. **Iniciar o backend**:
   ```bash
   cd D:\Arcsat\backend
   uvicorn main:app --reload
   ```

4. **Testar health check**:
   - Acesse: http://localhost:8000/health
   - Deve retornar: `{"status": "healthy", "database": "connected"}`

5. **Iniciar o frontend**:
   ```bash
   cd D:\Arcsat\frontend
   npm run dev
   ```

### Passo 2: Deploy no Railway

Siga o guia completo em: **RAILWAY_DEPLOY.md**

Resumo rápido:
1. Criar projeto no Railway
2. Adicionar MongoDB database
3. Deploy do backend (com MONGODB_URL)
4. Deploy do frontend (com VITE_API_URL)
5. Configurar domínio arcsat.com.br

## 🔧 Configuração de Variáveis

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017/arcsat_crm
DATABASE_NAME=arcsat_crm
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

## 🗄️ Estrutura MongoDB

### Coleções criadas automaticamente:
- **customers**: Clientes do CRM
- **deals**: Negócios/Oportunidades
- **activities**: Atividades e tarefas
- **contacts**: Contatos dos clientes

### Schemas convertidos para ObjectId:
- Todos os IDs agora são strings (ObjectId)
- Relacionamentos mantidos via referências
- Timestamps automáticos (created_at, updated_at)

## 🧪 Testando a API

### Health Check
```bash
curl http://localhost:8000/health
```

### Criar um cliente
```bash
curl -X POST http://localhost:8000/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Empresa Teste",
    "email": "contato@teste.com",
    "phone": "11999999999",
    "company": "Teste LTDA",
    "status": "active"
  }'
```

### Listar clientes
```bash
curl http://localhost:8000/api/customers
```

## 🔥 Comandos Úteis

### Backend
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn main:app --reload

# Iniciar em uma porta específica
uvicorn main:app --port 8080 --reload
```

### Frontend
```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview
```

## 📊 Diferenças SQLite → MongoDB

| Aspecto | SQLite (Antes) | MongoDB (Agora) |
|---------|----------------|-----------------|
| IDs | Integer auto-increment | ObjectId (string) |
| Queries | Síncrono (SQLAlchemy) | Assíncrono (Motor) |
| Relacionamentos | Foreign Keys | Referências (ObjectId) |
| Schemas | Rígidos (SQL) | Flexíveis (JSON) |
| Deploy | Arquivo local | Cloud/Railway |

## ⚠️ Importantes

1. **MongoDB é case-sensitive** nos nomes de coleções
2. **ObjectId** deve ser validado antes de queries
3. **Operações assíncronas** requerem `async/await`
4. **Índices** podem ser adicionados para melhor performance
5. **Backup** configure backups automáticos no Railway

## 🐛 Troubleshooting

### Erro: "MONGODB_URL not found"
- Verifique se o .env existe e está correto
- Certifique-se que o arquivo .env está no diretório backend/

### Erro: "Connection refused"
- Verifique se o MongoDB está rodando
- Teste a conexão: `mongo mongodb://localhost:27017`

### Erro: "Invalid ObjectId"
- Certifique-se que está passando um ID válido do MongoDB
- Use ObjectId.is_valid() antes de queries

### CORS Error no frontend
- Adicione a URL do frontend no CORS_ORIGINS do backend
- Verifique se o backend está rodando

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Motor Docs](https://motor.readthedocs.io/)
- [MongoDB Docs](https://www.mongodb.com/docs/)
- [Railway Docs](https://docs.railway.app/)
- [Vite Docs](https://vitejs.dev/)

## 🎉 Pronto!

Seu CRM Arcsat está agora configurado com:
- ✅ MongoDB como database
- ✅ Backend assíncrono com FastAPI
- ✅ Frontend React + TypeScript
- ✅ Pronto para deploy no Railway
- ✅ Configurado para domínio arcsat.com.br

Bom trabalho! 🚀
