from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario

SECRET_KEY = "BolodeMandiocacomChocolate"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def gerar_hash(senha: str):
    return pbkdf2_sha256.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pbkdf2_sha256.verify(senha, senha_hash)

def criar_token(dados: dict):
    dados_token = dados.copy()

    expiracao = datetime.utcnow() + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )

    dados_token.update({
        "exp": expiracao
    })

    return jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    erro_credenciais = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise erro_credenciais

        usuario_id = int(usuario_id)

    except (JWTError, ValueError):
        raise erro_credenciais

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise erro_credenciais

    return usuario

def exigir_perfis(*perfis_permitidos):
    def verificar_perfil(
        usuario_atual: Usuario = Depends(obter_usuario_atual)
    ):
        if usuario_atual.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=403,
                detail="Usuário sem permissão para esta operação"
            )

        return usuario_atual

    return verificar_perfil