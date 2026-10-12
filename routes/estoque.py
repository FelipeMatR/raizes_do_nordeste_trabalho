from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Estoque, Produto, Unidade
from schemas.schemas import EstoqueCreate
from security.security import exigir_perfis

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

@router.get("/{unidade_id}/produto/{produto_id}")
def consultar_estoque(
    unidade_id: int,
    produto_id: int,
    db: Session = Depends(get_db)
):
    unidade = db.query(Unidade).filter(
        Unidade.id == unidade_id
    ).first()

    if unidade is None:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada"
        )

    produto = db.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    estoque = db.query(Estoque).filter(
        Estoque.unidade_id == unidade_id,
        Estoque.produto_id == produto_id
    ).first()

    if estoque is None:
        raise HTTPException(
            status_code=404,
            detail="Estoque não encontrado para este produto e unidade"
        )

    return estoque