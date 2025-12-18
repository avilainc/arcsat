from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
from bson import ObjectId
from ..database import customers_collection
import csv
import io
from pydantic import BaseModel, EmailStr

router = APIRouter()

class CustomerImport(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    company: str = ""
    cnpj: str = ""
    status: str = "lead"
    origem: str = "importacao"

@router.post("/import/customers/csv")
async def import_customers_csv(file: UploadFile = File(...)):
    """Importar clientes de arquivo CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        # Ler arquivo
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')
        csv_file = io.StringIO(decoded)
        reader = csv.DictReader(csv_file)
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Validar campos obrigatórios
                if not row.get('name') or not row.get('email'):
                    errors.append(f"Linha {row_num}: Nome e email são obrigatórios")
                    continue
                
                # Verificar se já existe
                existing = await customers_collection.find_one({"email": row['email']})
                if existing:
                    errors.append(f"Linha {row_num}: Cliente com email {row['email']} já existe")
                    continue
                
                # Criar cliente
                customer = {
                    "name": row.get('name', ''),
                    "email": row.get('email', ''),
                    "phone": row.get('phone', ''),
                    "company": row.get('company', ''),
                    "cnpj": row.get('cnpj', ''),
                    "status": row.get('status', 'lead'),
                    "origem": row.get('origem', 'importacao'),
                    "categoria": row.get('categoria', ''),
                    "segmento": row.get('segmento', ''),
                    "responsavel": row.get('responsavel', ''),
                    "cep": row.get('cep', ''),
                    "municipio": row.get('municipio', ''),
                    "uf": row.get('uf', ''),
                    "observacoes": row.get('observacoes', ''),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                await customers_collection.insert_one(customer)
                imported += 1
                
            except Exception as e:
                errors.append(f"Linha {row_num}: {str(e)}")
        
        return {
            "message": f"{imported} clientes importados com sucesso",
            "imported": imported,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


@router.post("/import/customers/bulk")
async def import_customers_bulk(customers: List[CustomerImport]):
    """Importar múltiplos clientes via JSON"""
    try:
        imported = 0
        errors = []
        
        for idx, customer_data in enumerate(customers):
            try:
                # Verificar se já existe
                existing = await customers_collection.find_one({"email": customer_data.email})
                if existing:
                    errors.append(f"Cliente {idx+1}: Email {customer_data.email} já existe")
                    continue
                
                customer_dict = customer_data.model_dump()
                customer_dict["created_at"] = datetime.now()
                customer_dict["updated_at"] = datetime.now()
                
                await customers_collection.insert_one(customer_dict)
                imported += 1
                
            except Exception as e:
                errors.append(f"Cliente {idx+1}: {str(e)}")
        
        return {
            "message": f"{imported} clientes importados com sucesso",
            "imported": imported,
            "total": len(customers),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


@router.get("/import/template/csv")
async def download_import_template():
    """Baixar template CSV para importação"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalhos
        headers = [
            'name', 'email', 'phone', 'company', 'cnpj', 'status',
            'categoria', 'segmento', 'origem', 'responsavel',
            'cep', 'municipio', 'uf', 'observacoes'
        ]
        writer.writerow(headers)
        
        # Exemplo
        example = [
            'João Silva',
            'joao@empresa.com.br',
            '(11) 99999-9999',
            'Empresa XYZ Ltda',
            '12.345.678/0001-90',
            'lead',
            'medio',
            'tecnologia',
            'site',
            'Vendedor A',
            '01310-100',
            'São Paulo',
            'SP',
            'Cliente potencial'
        ]
        writer.writerow(example)
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content.encode('utf-8-sig'),
            media_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=template_importacao_clientes.csv'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar template: {str(e)}")


@router.post("/import/validate/csv")
async def validate_csv_before_import(file: UploadFile = File(...)):
    """Validar CSV antes de importar"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')
        csv_file = io.StringIO(decoded)
        reader = csv.DictReader(csv_file)
        
        valid_rows = 0
        invalid_rows = []
        duplicate_emails = []
        
        required_fields = ['name', 'email']
        
        for row_num, row in enumerate(reader, start=2):
            # Verificar campos obrigatórios
            missing_fields = [field for field in required_fields if not row.get(field)]
            if missing_fields:
                invalid_rows.append({
                    "row": row_num,
                    "error": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"
                })
                continue
            
            # Verificar email duplicado no banco
            existing = await customers_collection.find_one({"email": row['email']})
            if existing:
                duplicate_emails.append({
                    "row": row_num,
                    "email": row['email']
                })
                continue
            
            valid_rows += 1
        
        return {
            "valid_rows": valid_rows,
            "invalid_rows": len(invalid_rows),
            "duplicate_emails": len(duplicate_emails),
            "details": {
                "invalid": invalid_rows[:10],  # Mostrar apenas os primeiros 10
                "duplicates": duplicate_emails[:10]
            },
            "can_import": len(invalid_rows) == 0 and len(duplicate_emails) == 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar: {str(e)}")
