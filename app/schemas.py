from pydantic import BaseModel, Field, field_validator, ConfigDict, condecimal
import re
from typing import Optional

SKU_REGEX = re.compile(r"^[A-Za-z0-9._\-]{1,64}$")

class ProdutoCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200, description="Nome do produto")
    codigo_sku: str = Field(..., min_length=1, max_length=64, description="SKU único (A–Z, 0–9, ., -, _)")
    preco: condecimal(max_digits=10, decimal_places=2) = Field(..., ge=0, description="Preço (ex.: 199.90)")
    quantidade: int = Field(..., ge=0, description="Quantidade em estoque (>= 0)")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("nome")
    @classmethod
    def _nome_trim(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("não pode ser vazio")
        return v

    @field_validator("codigo_sku")
    @classmethod
    def _sku_normaliza_valida(cls, v: str) -> str:
        v = v.strip().upper()
        if not SKU_REGEX.match(v):
            raise ValueError("formato inválido (permitido: letras, números, ponto, hífen e underscore)")
        return v

class ProdutoAtualizar(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    codigo_sku: Optional[str] = Field(None, min_length=1, max_length=64)
    preco: Optional[condecimal(max_digits=10, decimal_places=2)] = Field(None, ge=0)
    quantidade: Optional[int] = Field(None, ge=0)

    @field_validator("nome")
    @classmethod
    def _nome_trim(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

    @field_validator("codigo_sku")
    @classmethod
    def _sku_normaliza_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().upper()
        if not SKU_REGEX.match(v):
            raise ValueError("formato inválido (permitido: letras, números, ponto, hífen e underscore)")
        return v


class ProdutoResposta(BaseModel):
    id: int
    nome: str
    codigo_sku: str
    preco: condecimal(max_digits=10, decimal_places=2)
    quantidade: int

    model_config = ConfigDict(from_attributes=True)

class ErroResposta(BaseModel):
    codigo: int = Field(..., description="Código de erro")
    mensagem: str = Field(..., description="Mensagem de erro")