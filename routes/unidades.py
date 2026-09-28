from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Unidade
from schemas.schemas import UnidadeCreate

router = APIRouter(prefix="/unidades", tags=["unidades"])

@router.post("/")
def criar(dados: UnidadeCreate, db: Session = Depends(get_db)):
    nova = Unidade(**dados.dict())
    db.add(nova); db.commit(); db.refresh(nova)
    return nova

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Unidade).all()