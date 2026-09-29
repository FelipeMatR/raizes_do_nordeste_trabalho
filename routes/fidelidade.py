from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario, MovimentoFidelidade

router = APIRouter(prefix="/fidelidade", tags=["fidelidade"])

@router.post("/optin/{cliente_id}")
def optin(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(Usuario).filter(Usuario.id==cliente_id).first()
    c.consentimento_fidelidade = True
    db.commit()
    return {"msg": "opt-in realizado"}

@router.get("/saldo/{cliente_id}")
def saldo(cliente_id: int, db: Session = Depends(get_db)):
    c = db.query(Usuario).filter(Usuario.id==cliente_id).first()
    return {"pontos": c.pontos, "consentimento": c.consentimento_fidelidade}

@router.post("/resgatar/{cliente_id}")
def resgatar(cliente_id: int, pontos: int, db: Session = Depends(get_db)):
    c = db.query(Usuario).filter(Usuario.id==cliente_id).first()
    if not c.consentimento_fidelidade:
        raise HTTPException(400, "Cliente não deu opt-in LGPD")
    if c.pontos < pontos:
        raise HTTPException(400, "Saldo insuficiente")
    c.pontos -= pontos
    mov = MovimentoFidelidade(cliente_id=cliente_id, tipo="RESGATE", pontos=-pontos, descricao="Resgate")
    db.add(mov)
    db.commit()
    return {"novo_saldo": c.pontos}