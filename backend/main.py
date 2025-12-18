from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import customers, deals, activities, contacts, cnpj
from database import client
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Lifespan para gerenciar conexão MongoDB
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: conectar ao MongoDB
    print("Conectando ao MongoDB...")
    yield
    # Shutdown: fechar conexão
    print("Fechando conexão MongoDB...")
    client.close()

app = FastAPI(
    title="CRM API",
    description="Sistema de CRM completo com MongoDB",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS dinamicamente
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
cors_origins.extend([
    "http://arcsat.com.br",
    "https://arcsat.com.br",
    "http://www.arcsat.com.br",
    "https://www.arcsat.com.br"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(deals.router, prefix="/api/deals", tags=["deals"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(cnpj.router, prefix="/api", tags=["cnpj"])

@app.get("/")
async def read_root():
    return {
        "message": "CRM API Arcsat está rodando com MongoDB!",
        "version": "2.0.0",
        "database": "MongoDB"
    }

@app.get("/health")
async def health_check():
    try:
        # Testar conexão com MongoDB
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
