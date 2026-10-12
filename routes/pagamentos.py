import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, Pagamento

router = APIRouter(
    prefix="/pagamentos",
    tags=["pagamentos"]
)

@router.post("/{pedido.id}")
def processarPagamento(
    pedido_id: int,
    forma_pagamento: str,
    db: Session = Depends(get_db)
):
    # 1. Verificar se o pedido existe
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    # 2. Validar forma de pagamento
    formasValidas = [
        "PIX",
        "CARTAO",
        "DINHEIRO"
    ]

    forma_pagamento = forma_pagamento.upper()

    if forma_pagamento not in formasValidas:
        raise HTTPException(
            status_code=400,
            detail="Forma de pagamento inválida"
        )

    # 3. Verificar pagamento existente
    pagamento = db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido_id
    ).first()

    # 4. Simulação do pagamento
    aprovado = random.randint(1, 5) != 5

    if aprovado:
        statusPagamento = "APROVADO"
        statusPedido = "PAGO"
    else:
        statusPagamento = "RECUSADO"
        statusPedido = "AGUARDANDO PAGAMENTO"

    # 5. Criar ou atualizar pagamento
    if pagamento is None:
        pagamento = Pagamento(
            pedido_id=pedido_id,
            status=statusPagamento,
            forma_pagamento=forma_pagamento,
            payload_mock=(
                f"Pagamento mock {statusPagamento}"
            )
        )

        db.add(pagamento)

    else:
        pagamento.status = statusPagamento
        pagamento.forma_pagamento = forma_pagamento
        pagamento.payload_mock = (
            f"Pagamento mock {statusPagamento}"
        )

    # 6. Atualizar status do pedido
    pedido.status = statusPedido

    # 7. Confirmar alterações
    try:
        db.commit()
        db.refresh(pagamento)
        db.refresh(pedido)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao processar pagamento"
        )

    return {
        "pedido.id": pedido.id,
        "pagamento.id": pagamento.id,
        "status.pagamento": pagamento.status,
        "status.pedido": pedido.status,
        "forma.pagamento": pagamento.forma_pagamento
    }