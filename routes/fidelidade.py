from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario, TransacaoPontos
from schemas.schemas import ResgatePontos
from datetime import datetime

router = APIRouter(prefix="/fidelidade", tags=["fidelidade"])

@router.post("/resgatar")
def resgatar(dados: ResgatePontos, db: Session = Depends(get_db)):
    cliente = db.query(Usuario).filter(Usuario.id == dados.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    if not cliente.consentimento_fidelidade:
        raise HTTPException(status_code=403, detail="Cliente nao optou pelo programa de fidelidade (LGPD)")
    if cliente.saldo_pontos < dados.pontos:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    cliente.saldo_pontos -= dados.pontos
    t = TransacaoPontos(cliente_id=cliente.id, pontos=-dados.pontos, motivo="resgate", data=datetime.utcnow())
    db.add(t); db.commit()
    return {"ok": True, "saldo_atual": cliente.saldo_pontos}