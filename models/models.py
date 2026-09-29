from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cidade = Column(String)
    endereco = Column(String)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    preco = Column(Float)
    descricao = Column(String, nullable=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha_hash = Column(String)
    perfil = Column(String, default="CLIENTE")
    consentimento_fidelidade = Column(Boolean, default=False)
    pontos = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Estoque(Base):
    __tablename__ = "estoques"
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    quantidade = Column(Integer, default=0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    unidade_id = Column(Integer, ForeignKey("unidades.id"))
    canal = Column(String)
    status = Column(String, default="CRIADO")
    total = Column(Float, default=0.0)
    pontos_gerados = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    itens = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    pedido = relationship("Pedido", back_populates="itens")

class MovimentoFidelidade(Base):
    __tablename__ = "movimentos_fidelidade"
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    tipo = Column(String)
    pontos = Column(Integer)
    descricao = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)