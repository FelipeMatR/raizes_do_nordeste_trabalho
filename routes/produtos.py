from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Produto
from schemas.schemas import ProdutoCreate

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.post("/")
def criar(dados: ProdutoCreate, db: Session = Depends(get_db)):
    novo = Produto(**dados.dict())
    db.add(novo); db.commit(); db.refresh(novo)
    return novo

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Produto).all()