from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "segredo-raizes-2026"

def criar_token(dados: dict):
    exp = datetime.utcnow() + timedelta(minutes=60)
    dados.update({"exp": exp})
    return jwt.encode(dados, SECRET_KEY, algorithm="HS256")

def verificar_senha(senha: str, hash_salvo: str):
    return pwd_context.verify(senha, hash_salvo)

def hash_senha(senha: str):
    return pwd_context.hash(senha)