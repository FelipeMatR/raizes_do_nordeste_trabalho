from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario
from schemas.schemas import UsuarioCreate, UsuarioLogin
from security.security import gerar_hash, verificar_senha, criar_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/registrar", status_code=201)
def registrar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db)
):
    # 1. Verifica se o e-mail já está cadastrado
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado"
        )

    # 2. Valida perfil informado
    perfis_validos = [
        "CLIENTE",
        "ATENDENTE",
        "COZINHA",
        "ADMIN"
    ]

    perfil = dados.perfil.upper()

    if perfil not in perfis_validos:
        raise HTTPException(
            status_code=400,
            detail="Perfil inválido"
        )

    # 3. Cria usuário
    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash(dados.senha),
        perfil=perfil,
        consentimento_fidelidade=(
            dados.consentimento_fidelidade
        )
    )

    db.add(novo_usuario)

    try:
        db.commit()
        db.refresh(novo_usuario)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao registrar usuário"
        )

    # 4. Retorno sem senha e sem hash
    return {
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "email": novo_usuario.email,
        "perfil": novo_usuario.perfil,
        "consentimento_fidelidade":
            novo_usuario.consentimento_fidelidade
    }


@router.post("/login")
def login(
    dados: UsuarioLogin,
    db: Session = Depends(get_db)
):

    # 1. Procura usuário pelo e-mail
    usuario = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # 2. Verifica senha
    if not verificar_senha(
        dados.senha,
        usuario.senha_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # 3. Gera JWT
    token = criar_token({
        "sub": str(usuario.id),
        "perfil": usuario.perfil
    })

    # 4. Retorna informações da autenticação
    return {
        "access_token": token,
        "token_type": "bearer",
        "perfil": usuario.perfil,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "perfil": usuario.perfil
        }
    }