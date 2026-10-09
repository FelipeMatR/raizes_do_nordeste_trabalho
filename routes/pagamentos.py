from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, Pagamento
import json, random

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])

@router.post("/{pedido_id}")
def solicitar_pagamento(pedido_id: int, forma_pagamento: str = "MOCK", db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id==pedido_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")

    # Mock
    aprovado = random.choice([True, True, True, True, False])
    status = "APROVADO" if aprovado else "RECUSADO"
    payload = {"gateway": "MOCK", "pedido_id": pedido_id, "valor": pedido.total, "status": status}

    pag = db.query(Pagamento).filter(Pagamento.pedido_id==pedido_id).first()
    if pag:
        pag.status = status
        pag.forma_pagamento = forma_pagamento
        pag.payload_mock = json.dumps(payload)
    else:
        pag = Pagamento(pedido_id=pedido_id, status=status, forma_pagamento=forma_pagamento, payload_mock=json.dumps(payload))
        db.add(pag)

    if aprovado:
        pedido.status = "PAGO"
    else:
        pedido.status = "AGUARDANDO_PAGAMENTO"

    db.commit()
    return {"pedido_id": pedido_id, "pagamento_status": status, "payload": payload}