from pydantic import BaseModel, Field
from typing import Optional


class PratoInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    preco_promocional: Optional[float] = Field(default=None, gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True


class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    preco_promocional: Optional[float]
    descricao: Optional[str]
    disponivel: bool
    criado_em: str
