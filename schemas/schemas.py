from typing import Optional, List
from pydantic import BaseModel, EmailStr

class ResgatePontos(BaseModel):
    cliente_id: int
    pontos: int

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    cliente_id: int
    unidade_id: int
    canal_pedido: str
    itens: List[ItemPedidoCreate]

class EstoqueCreate(BaseModel):
    produto_id: int
    unidade_id: int
    quantidade: int

class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    descricao: Optional[str] = None

class UnidadeCreate(BaseModel):
    nome: str
    cidade: str
    endereco: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "CLIENTE"
    consentimento_fidelidade: bool = False