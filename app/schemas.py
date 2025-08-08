from pydantic import BaseModel, Field, condecimal
from typing import Optional

class ProdutoCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    codigo_sku: str = Field(..., min_length=1, max_length=64)
    preco: condecimal(max_digits=10, decimal_places=2) = 0
    quantidade: int = 0

class ProdutoAtualizar(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    codigo_sku: Optional[str] = Field(None, min_length=1, max_length=64)
    preco: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    quantidade: Optional[int] = None

class ProdutoResposta(BaseModel):
    id: int
    nome: str
    codigo_sku: str
    preco: condecimal(max_digits=10, decimal_places=2)
    quantidade: int

    model_config = {
        "from_attributes": True
    }