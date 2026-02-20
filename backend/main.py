from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import customers, deals, activities, contacts, cnpj, cep, customer_extras, analytics, automation, pipeline, reports, import_data, email, notifications, tasks, whatsapp, custom_dashboards, business_intelligence
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
app.include_router(cep.router, prefix="/api", tags=["cep"])
app.include_router(customer_extras.router, prefix="/api", tags=["customer-extras"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(automation.router, prefix="/api", tags=["automation"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(import_data.router, prefix="/api", tags=["import"])
app.include_router(email.router, prefix="/api", tags=["email"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(whatsapp.router, prefix="/api", tags=["whatsapp"])
app.include_router(custom_dashboards.router, prefix="/api", tags=["dashboards"])
app.include_router(business_intelligence.router, prefix="/api", tags=["bi"])

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
