from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, ItemPedido, Produto, Estoque, Usuario, MovimentoFidelidade
from schemas.schemas import PedidoCreate
from typing import Optional

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("/")
def criar_pedido(dados: PedidoCreate, db: Session = Depends(get_db)):
    total = 0
    # Valida estoque
    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id==item.produto_id).first()
        if not produto:
            raise HTTPException(404, f"Produto {item.produto_id} não encontrado")
        est = db.query(Estoque).filter(Estoque.produto_id==item.produto_id, Estoque.unidade_id==dados.unidade_id).first()
        if not est or est.quantidade < item.quantidade:
            raise HTTPException(409, f"Estoque insuficiente para produto {produto.nome}")
        total += produto.preco * item.quantidade

    # Baixa estoque
    for item in dados.itens:
        est = db.query(Estoque).filter(Estoque.produto_id==item.produto_id, Estoque.unidade_id==dados.unidade_id).first()
        est.quantidade -= item.quantidade

    pedido = Pedido(cliente_id=dados.cliente_id, unidade_id=dados.unidade_id, canal_pedido=dados.canal_pedido, total=total, status="AGUARDANDO_PAGAMENTO")
    db.add(pedido); db.commit(); db.refresh(pedido)

    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id==item.produto_id).first()
        db.add(ItemPedido(pedido_id=pedido.id, produto_id=item.produto_id, quantidade=item.quantidade, preco_unitario=produto.preco))

    cliente = db.query(Usuario).filter(Usuario.id==dados.cliente_id).first()
    pontos = int(total // 10)
    if cliente.consentimento_fidelidade:
        cliente.pontos += pontos
        pedido.pontos_gerados = pontos
        db.add(MovimentoFidelidade(cliente_id=cliente.id, tipo="ACUMULO", pontos=pontos, descricao=f"Pedido {pedido.id}"))
    db.commit()
    return {"pedido_id": pedido.id, "total": total, "pontos_gerados": pontos, "status": pedido.status}

@router.get("/")
def listar_pedidos(canalPedido: Optional[str] = Query(None), status: Optional[str] = Query(None), unidade_id: Optional[int] = None, db: Session = Depends(get_db)):
    # Filtro por canal e status
    q = db.query(Pedido)
    if canalPedido: q = q.filter(Pedido.canal_pedido==canalPedido)
    if status: q = q.filter(Pedido.status==status)
    if unidade_id: q = q.filter(Pedido.unidade_id==unidade_id)
    return q.all()

@router.patch("/{pedido_id}/status")
def atualizar_status(pedido_id: int, novo_status: str, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id==pedido_id).first()
    if not pedido: raise HTTPException(404, "Pedido não encontrado")
    pedido.status = novo_status
    db.commit()
    return {"msg": f"Status atualizado para {novo_status}"}