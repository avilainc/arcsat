from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import customers, deals, activities, contacts

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRM API",
    description="Sistema de CRM completo",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(deals.router, prefix="/api/deals", tags=["deals"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])

@app.get("/")
def read_root():
    return {"message": "CRM API está rodando!", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
