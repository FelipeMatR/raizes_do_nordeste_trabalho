from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "raizes-do-nordeste-secret-2026"
ALGORITHM = "HS256"

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)

def criar_token(dados: dict):
    exp = datetime.utcnow() + timedelta(hours=8)
    dados.update({"exp": exp})
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)