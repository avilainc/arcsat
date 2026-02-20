# Configuração Railway - Backend

Acesse: <https://railway.app/project/523c34a7-290a-4d1f-8700-9282cbff5a2e>

## Backend Service

### Variables

```bash
MONGODB_URL=mongodb+srv://nicolasrosaab_db_user:Gio4EAQhbEdQMISl@cluster0.npuhras.mongodb.net/arcsat_crm?retryWrites=true&w=majority
DATABASE_NAME=arcsat_crm
ENVIRONMENT=production
CORS_ORIGINS=https://frontend-production-5ae9.up.railway.app,https://arcsat.com.br
PORT=8000
```

## Frontend Service

### Variables

```bash
VITE_API_URL=https://backend-production-7566.up.railway.app/api
```

---

## Passo a Passo

1. **Backend:**
   - Clique no serviço `backend`
   - Vá em `Variables`
   - Adicione as 5 variáveis acima

2. **Frontend:**
   - Clique no serviço `frontend`
   - Vá em `Variables`
   - Adicione a variável `VITE_API_URL`

3. **Deploy:**
   - Os serviços farão redeploy automaticamente
   - Aguarde ~2-3 minutos

4. **Teste:**
   - <https://backend-production-7566.up.railway.app/health>
   - <https://frontend-production-5ae9.up.railway.app>

---

**Alternativa:** Use o CLI Railway

```bash
railway login
railway link 523c34a7-290a-4d1f-8700-9282cbff5a2e
railway variables set MONGODB_URL="mongodb+srv://nicolasrosaab_db_user:Gio4EAQhbEdQMISl@cluster0.npuhras.mongodb.net/arcsat_crm?retryWrites=true&w=majority"
```
