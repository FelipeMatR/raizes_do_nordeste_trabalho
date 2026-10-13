from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Unidade
from schemas.schemas import UnidadeCreate

router = APIRouter(prefix="/unidades", tags=["unidades"])

@router.post("/")
def criar(dados: UnidadeCreate, db: Session = Depends(get_db)):
    nova = Unidade(**dados.dict())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Unidade).all()

@router.get("/{unidade_id}")
def consultar_por_id(unidade_id: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()

    if unidade is None:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada"
        )

    return unidade