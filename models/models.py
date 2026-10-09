from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    endereco = Column(String, nullable=False)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    descricao = Column(String, nullable=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(String, default="CLIENTE") # Cliente, Atendente, Gerente
    consentimento_fidelidade = Column(Boolean, default=False)
    pontos = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Estoque(Base):
    __tablename__ = "estoques"
    id = Column(Integer, primary_key=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    quantidade = Column(Integer, default=0)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido = Column(String, nullable=False) # APP, TOTEM, BALCAO, PICKUP, WEB
    status = Column(String, default="AGUARDANDO_PAGAMENTO") # Aguardando_Pagamento, Pago, Preparando, Pronto, Entregue, Cancelado
    total = Column(Float, default=0.0)
    pontos_gerados = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    pedido = relationship("Pedido", back_populates="itens")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True, nullable=False)
    status = Column(String, default="PENDENTE") # Pendente, Aprovado, Recusado
    forma_pagamento = Column(String, nullable=False) # Mock, PIX, Cartao
    payload_mock = Column(String)
    pedido = relationship("Pedido", back_populates="pagamento")

class MovimentoFidelidade(Base):
    __tablename__ = "movimentos_fidelidade"
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String, nullable=False) # Acumulo, Resgate
    pontos = Column(Integer, nullable=False)
    descricao = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)