from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, ItemPedido, Produto, Estoque, Usuario, TransacaoPontos
from schemas.schemas import PedidoCreate
from datetime import datetime

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("/")
def criar(dados: PedidoCreate, db: Session = Depends(get_db)):
    total = 0.0
    itens_db = []
    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} nao encontrado")
        est = db.query(Estoque).filter(Estoque.produto_id==item.produto_id, Estoque.unidade_id==dados.unidade_id).first()
        if not est or est.quantidade < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para {produto.nome}")
        est.quantidade -= item.quantidade
        total += float(produto.preco) * item.quantidade
        itens_db.append(ItemPedido(produto_id=item.produto_id, quantidade=item.quantidade, preco_unitario=produto.preco))
    pedido = Pedido(cliente_id=dados.cliente_id, unidade_id=dados.unidade_id, canal_pedido=dados.canal_pedido, total=total, data=datetime.utcnow())
    db.add(pedido); db.flush()
    for it in itens_db:
        it.pedido_id = pedido.id
        db.add(it)
    cliente = db.query(Usuario).filter(Usuario.id==dados.cliente_id).first()
    if cliente and cliente.consentimento_fidelidade:
        pontos = int(total // 10)
        if pontos > 0:
            cliente.saldo_pontos += pontos
            db.add(TransacaoPontos(cliente_id=cliente.id, pontos=pontos, motivo="compra", data=datetime.utcnow()))
    db.commit()
    return {"ok": True, "pedido_id": pedido.id, "total": total}