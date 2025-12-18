from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

@router.get("/cep/{cep}")
async def buscar_cep(cep: str):
    """Busca dados de endereço pelo CEP usando ViaCEP"""
    # Remove caracteres não numéricos
    cep_limpo = "".join(filter(str.isdigit, cep))

    if len(cep_limpo) != 8:
        raise HTTPException(status_code=400, detail="CEP deve ter 8 dígitos")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="CEP não encontrado")

            data = response.json()

            if "erro" in data:
                raise HTTPException(status_code=404, detail="CEP não encontrado")

            return {
                "cep": data.get("cep"),
                "logradouro": data.get("logradouro"),
                "complemento": data.get("complemento"),
                "bairro": data.get("bairro"),
                "municipio": data.get("localidade"),
                "uf": data.get("uf"),
                "ibge": data.get("ibge"),
                "ddd": data.get("ddd")
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar CEP: {str(e)}")
