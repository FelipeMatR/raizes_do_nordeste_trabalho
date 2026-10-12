from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario, MovimentoFidelidade
from schemas.schemas import ResgatePontos
from security.security import exigir_perfis


router = APIRouter(
    prefix="/fidelidade",
    tags=["fidelidade"]
)


@router.post("/optin/{cliente_id}")
def ativar_fidelidade(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    # 1. Verificar se o cliente existe
    cliente = db.query(Usuario).filter(
        Usuario.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    # 2. Verificar se já existe consentimento
    if cliente.consentimento_fidelidade:
        return {
            "cliente_id": cliente.id,
            "consentimento_fidelidade": True,
            "message": "Cliente já participa do programa de fidelidade"
        }

    # 3. Registrar consentimento
    cliente.consentimento_fidelidade = True

    try:
        db.commit()
        db.refresh(cliente)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao registrar consentimento"
        )

    return {
        "cliente_id": cliente.id,
        "consentimento_fidelidade": True,
        "message": "Consentimento registrado com sucesso"
    }


@router.get("/saldo/{cliente_id}")
def consultar_saldo(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    
    # 1. Verificar se o cliente existe
    cliente = db.query(Usuario).filter(
        Usuario.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    # 2. Retornar saldo
    return {
        "cliente_id": cliente.id,
        "pontos": cliente.pontos,
        "consentimento_fidelidade":
            cliente.consentimento_fidelidade
    }


@router.post("/resgatar/{cliente_id}")
def resgatar_pontos(
    cliente_id: int,
    dados: ResgatePontos,
    db: Session = Depends(get_db)
):
    # 1. Verificar se o cliente existe
    cliente = db.query(Usuario).filter(
        Usuario.id == cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    # 2. Verificar consentimento
    if not cliente.consentimento_fidelidade:
        raise HTTPException(
            status_code=403,
            detail="Cliente não participa do programa de fidelidade"
        )

    # 3. Validar quantidade de pontos
    if dados.pontos <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade de pontos deve ser maior que zero"
        )

    # 4. Verificar saldo
    if cliente.pontos < dados.pontos:
        raise HTTPException(
            status_code=409,
            detail="Saldo de pontos insuficiente"
        )

    # 5. Realizar resgate
    cliente.pontos -= dados.pontos

    movimento = MovimentoFidelidade(
        cliente_id=cliente.id,
        tipo="DEBITO",
        pontos=dados.pontos,
        descricao="Resgate de pontos"
    )

    db.add(movimento)

    # 6. Confirmar alterações
    try:
        db.commit()
        db.refresh(cliente)
        db.refresh(movimento)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao realizar resgate de pontos"
        )

    return {
        "cliente_id": cliente.id,
        "pontos_resgatados": dados.pontos,
        "saldo_atual": cliente.pontos,
        "message": "Pontos resgatados com sucesso"
    }