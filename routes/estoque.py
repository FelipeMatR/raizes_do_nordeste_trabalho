from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Estoque
from schemas.schemas import EstoqueCreate

router = APIRouter(prefix="/estoque", tags=["estoque"])

@router.post("/")
def adicionar(dados: EstoqueCreate, db: Session = Depends(get_db)):
    existente = db.query(Estoque).filter(Estoque.produto_id==dados.produto_id, Estoque.unidade_id==dados.unidade_id).first()
    if existente:
        existente.quantidade += dados.quantidade
    else:
        existente = Estoque(**dados.dict())
        db.add(existente)
    db.commit()
    return {"ok": True}

@router.get("/{unidade_id}")
def listar(unidade_id: int, db: Session = Depends(get_db)):
    return db.query(Estoque).filter(Estoque.unidade_id==unidade_id).all()