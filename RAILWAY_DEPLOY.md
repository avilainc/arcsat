# CRM Arcsat - Guia de Deploy Railway

## Estrutura do Projeto

- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Vite + TypeScript

## Passo 1: Preparar MongoDB no Railway

1. Acesse [Railway.app](https://railway.app) e faça login
2. Crie um novo projeto
3. Clique em "New" → "Database" → "Add MongoDB"
4. Após criar, copie a **MONGO_URL** nas variáveis do MongoDB

## Passo 2: Deploy do Backend

1. No mesmo projeto Railway, clique em "New" → "GitHub Repo"
2. Selecione o repositório `arcsat`
3. Configure o serviço:
   - **Root Directory**: `/backend`
   - **Build Command**: (deixe em branco, será detectado automaticamente)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Adicione as variáveis de ambiente:
   ```
   MONGODB_URL=<copie a URL do MongoDB criado no Railway>
   DATABASE_NAME=arcsat_crm
   ENVIRONMENT=production
   CORS_ORIGINS=https://seu-frontend.railway.app,http://arcsat.com.br,https://arcsat.com.br
   ```

5. Salve e aguarde o deploy

## Passo 3: Deploy do Frontend

1. No mesmo projeto, clique em "New" → "GitHub Repo" (mesmo repo)
2. Configure o serviço:
   - **Root Directory**: `/frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

3. Adicione as variáveis de ambiente:
   ```
   VITE_API_URL=https://seu-backend.railway.app/api
   ```

4. Salve e aguarde o deploy

## Passo 4: Configurar Domínio (arcsat.com.br)

### No Railway:

1. Vá ao serviço Frontend
2. Clique em "Settings" → "Domains"
3. Adicione um domínio customizado: `arcsat.com.br`
4. Railway fornecerá um registro CNAME

### No seu provedor de domínio:

1. Acesse o painel de DNS do seu domínio
2. Adicione um registro CNAME:
   - **Nome/Host**: `@` ou deixe em branco
   - **Valor/Destino**: O valor fornecido pelo Railway
   - **TTL**: 3600 (1 hora)

3. Para www, adicione outro CNAME:
   - **Nome/Host**: `www`
   - **Valor/Destino**: O mesmo valor do Railway
   - **TTL**: 3600

### Atualizar CORS no Backend:

Após configurar o domínio, adicione à variável `CORS_ORIGINS`:
```
CORS_ORIGINS=https://seu-frontend.railway.app,http://arcsat.com.br,https://arcsat.com.br,http://www.arcsat.com.br,https://www.arcsat.com.br
```

## Passo 5: Verificar o Deploy

1. **Backend Health Check**: `https://seu-backend.railway.app/health`
2. **Frontend**: `https://seu-frontend.railway.app` ou `https://arcsat.com.br`

## Variáveis de Ambiente Completas

### Backend:
```env
MONGODB_URL=mongodb+srv://...
DATABASE_NAME=arcsat_crm
ENVIRONMENT=production
CORS_ORIGINS=https://frontend.railway.app,https://arcsat.com.br
PORT=8000
```

### Frontend:
```env
VITE_API_URL=https://backend.railway.app/api
PORT=3000
```

## Comandos Úteis

### Testar localmente com MongoDB:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Troubleshooting

1. **Erro de conexão MongoDB**: Verifique se a MONGODB_URL está correta
2. **CORS Error**: Adicione a URL do frontend no CORS_ORIGINS do backend
3. **502 Bad Gateway**: Verifique os logs do serviço no Railway
4. **Domínio não funciona**: Aguarde propagação DNS (até 48h, geralmente 1-2h)

## Estrutura de Dados MongoDB

Coleções criadas automaticamente:
- `customers`: Clientes
- `deals`: Negócios/Oportunidades
- `activities`: Atividades
- `contacts`: Contatos

## Segurança

- ✅ CORS configurado
- ✅ HTTPS automático no Railway
- ✅ Variáveis de ambiente seguras
- ✅ MongoDB com autenticação

## Suporte

Em caso de problemas:
1. Verifique os logs no Railway Dashboard
2. Teste as URLs de health check
3. Verifique as variáveis de ambiente
