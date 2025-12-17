from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/arcsat_crm")
DATABASE_NAME = os.getenv("DATABASE_NAME", "arcsat_crm")

# Cliente MongoDB assíncrono para FastAPI
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Coleções
customers_collection = database.get_collection("customers")
deals_collection = database.get_collection("deals")
activities_collection = database.get_collection("activities")
contacts_collection = database.get_collection("contacts")

# Dependência para obter o database
async def get_database():
    return database
