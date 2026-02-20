from fastapi import APIRouter, HTTPException
import httpx
from schemas import CNPJData

router = APIRouter()

@router.get("/cnpj/{cnpj}", response_model=CNPJData)
async def get_cnpj_data(cnpj: str):
    """
    Busca dados de CNPJ na API da Receita Federal
    API pública: https://brasilapi.com.br/docs
    """
    # Remove caracteres não numéricos
    cnpj_clean = ''.join(filter(str.isdigit, cnpj))

    if len(cnpj_clean) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Usando Brasil API (gratuita e confiável)
            response = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_clean}")

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="CNPJ não encontrado")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro ao consultar CNPJ")

            data = response.json()

            # Mapear dados da Brasil API para nosso schema
            cnpj_data = {
                "cnpj": data.get("cnpj", cnpj_clean),
                "razao_social": data.get("razao_social", ""),
                "nome_fantasia": data.get("nome_fantasia"),
                "porte": data.get("porte"),
                "natureza_juridica": data.get("natureza_juridica"),
                "capital_social": data.get("capital_social"),
                "cep": data.get("cep"),
                "logradouro": data.get("logradouro"),
                "numero": data.get("numero"),
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "municipio": data.get("municipio"),
                "uf": data.get("uf"),
                "email": data.get("email"),
                "telefone": data.get("ddd_telefone_1"),
                "data_abertura": data.get("data_inicio_atividade"),
                "situacao": data.get("descricao_situacao_cadastral"),
            }

            # Atividade principal
            if data.get("cnae_fiscal_descricao"):
                cnpj_data["atividade_principal"] = data.get("cnae_fiscal_descricao")
            elif data.get("cnaes_secundarios") and len(data.get("cnaes_secundarios", [])) > 0:
                cnpj_data["atividade_principal"] = data["cnaes_secundarios"][0].get("descricao")

            return CNPJData(**cnpj_data)

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout ao consultar CNPJ")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Erro na requisição: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {str(e)}")
