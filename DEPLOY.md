# 🚀 Deploy Railway - CRM System

Sistema CRM completo com backend Python (FastAPI) e frontend TypeScript (React).

## 📦 Deploy Automático via GitHub

### 1. 🐳 Docker / Docker Compose (Recomendado)

**Vantagens:** Funciona em qualquer lugar, isolamento completo, fácil de gerenciar

```bash
# Build e iniciar todos os serviços
docker-compose up -d

# Ou build separado
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

Acesse: <http://localhost>

---

### 2. ☁️ Railway (Deploy Gratuito)

**Vantagens:** Deploy automático via Git, gratuito, banco PostgreSQL incluído

#### Backend

1. Crie conta em [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Selecione o repositório
4. Configure:
   - **Root Directory**: `backend`
   - Railway detecta Python automaticamente
5. Adicione variáveis de ambiente se necessário

#### Frontend

1. No mesmo projeto, click "+ New"
2. Selecione "GitHub Repo" novamente
3. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Start Command**: `npx serve -s dist -l $PORT`

---

### 3. 🎨 Render (Deploy Gratuito)

**Vantagens:** Interface simples, SSL gratuito, domínio próprio

#### Backend

1. Crie conta em [Render.com](https://render.com)
2. "New +" → "Web Service"
3. Conecte seu repositório
4. Configurações:
   - **Name**: crm-backend
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && pip install email-validator`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

#### Frontend

1. "New +" → "Static Site"
2. Selecione o repositório
3. Configurações:
   - **Name**: crm-frontend
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

---

### 4. ▲ Vercel (Frontend) + Render/Railway (Backend)

**Vantagens:** Deploy super rápido para frontend, domínio .vercel.app gratuito

#### Frontend no Vercel

```bash
cd frontend
npm install -g vercel
vercel
```

Ou via dashboard:

1. [Vercel.com](https://vercel.com) → "New Project"
2. Importe repositório
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### Backend: Use Railway ou Render (instruções acima)

---

### 5. 🌐 Heroku

**Vantagens:** Clássico, confiável, fácil de usar

#### Backend

```bash
cd backend
heroku login
heroku create crm-backend-app
git subtree push --prefix backend heroku main

# Ou via dashboard do Heroku
```

#### Frontend

```bash
cd frontend
heroku create crm-frontend-app
# Adicionar buildpack
heroku buildpacks:set heroku/nodejs
git subtree push --prefix frontend heroku main
```

---

### 6. 📦 VPS (DigitalOcean, Linode, AWS EC2)

**Para servidores VPS:**

#### 1. Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

#### 2. Clone o projeto

```bash
git clone <seu-repositorio>
cd Arcsat
```

#### 3. Configure domínio (opcional)

Edite `frontend/nginx.conf` e adicione seu domínio

#### 4. Deploy

```bash
docker-compose up -d
```

#### 5. SSL com Let's Encrypt (opcional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com
```

---

## 🔧 Configurações Importantes

### Variáveis de Ambiente (Backend)

Crie um arquivo `.env` se necessário:

```env
DATABASE_URL=sqlite:///./crm.db
# Para PostgreSQL em produção:
# DATABASE_URL=postgresql://user:password@host:port/database
```

### Atualizar URL da API (Frontend)

Em `frontend/src/services/api.ts`, atualize:

```typescript
const api = axios.create({
  baseURL: 'https://seu-backend-url.com/api', // URL do seu backend em produção
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## 📊 Banco de Dados

### SQLite (Desenvolvimento)

- Já configurado, arquivo `crm.db` criado automaticamente

### PostgreSQL (Produção Recomendada)

1. Instale psycopg2:

```bash
pip install psycopg2-binary
```

2. Atualize `backend/database.py`:

```python
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/crm_db"
)
```

3. No Railway/Render, adicione banco PostgreSQL automaticamente

---

## 🔒 Segurança para Produção

1. **Adicione autenticação** (JWT tokens)
2. **Configure CORS** adequadamente em `main.py`
3. **Use HTTPS** (SSL/TLS)
4. **Variáveis de ambiente** para senhas
5. **Rate limiting** para APIs
6. **Validação de entrada** robusta

---

## 📈 Monitoramento

- **Logs**: `docker-compose logs -f`
- **Railway**: Dashboard com logs em tempo real
- **Render**: Logs na dashboard
- **Sentry** (opcional): Para tracking de erros

---

## 🆘 Troubleshooting

### Backend não conecta ao banco

```bash
# Verifique permissões do arquivo crm.db
chmod 666 backend/crm.db
```

### CORS errors

Atualize `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend não encontra API

Verifique `frontend/src/services/api.ts` - URL da API deve estar correta

---

## 📞 Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Rebuild após mudanças
docker-compose up -d --build

# Parar tudo
docker-compose down

# Ver logs de serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Acessar shell do container
docker-compose exec backend bash
```

---

## ✅ Checklist de Deploy

- [ ] Backend rodando e acessível
- [ ] Frontend rodando e acessível
- [ ] Banco de dados funcionando
- [ ] CORS configurado
- [ ] URL da API atualizada no frontend
- [ ] SSL/HTTPS configurado
- [ ] Domínio apontando corretamente (se aplicável)
- [ ] Backup do banco de dados configurado
- [ ] Monitoramento ativo

---

**Boa sorte com o deploy! 🚀**
