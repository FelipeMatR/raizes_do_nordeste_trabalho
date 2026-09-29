from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, ItemPedido, Produto, Estoque, Usuario, MovimentoFidelidade
from schemas.schemas import PedidoCreate

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("/")
def criar_pedido(dados: PedidoCreate, db: Session = Depends(get_db)):
    total = 0
    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id==item.produto_id).first()
        total += produto.preco * item.quantidade
        est = db.query(Estoque).filter(Estoque.produto_id==item.produto_id, Estoque.unidade_id==dados.unidade_id).first()
        est.quantidade -= item.quantidade

    pedido = Pedido(cliente_id=dados.cliente_id, unidade_id=dados.unidade_id, canal=dados.canal_pedido, total=total)
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id==item.produto_id).first()
        db.add(ItemPedido(pedido_id=pedido.id, produto_id=item.produto_id, quantidade=item.quantidade, preco_unitario=produto.preco))

    cliente = db.query(Usuario).filter(Usuario.id==dados.cliente_id).first()
    pontos = int(total // 10)
    if cliente.consentimento_fidelidade:
        cliente.pontos += pontos
        pedido.pontos_gerados = pontos
        mov = MovimentoFidelidade(cliente_id=cliente.id, tipo="ACUMULO", pontos=pontos, descricao=f"Pedido {pedido.id}")
        db.add(mov)

    db.commit()
    return {"pedido_id": pedido.id, "total": total, "pontos_gerados": pontos}