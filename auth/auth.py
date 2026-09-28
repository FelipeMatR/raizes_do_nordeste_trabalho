from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Usuario
from security.security import verificar_senha, criar_token, hash_senha
from schemas.schemas import UsuarioLogin, UsuarioCreate

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/registrar")
def registrar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    novo = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        perfil=dados.perfil,
        consentimento_fidelidade=dados.consentimento_fidelidade
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"ok": True, "id": novo.id}

@router.post("/login")
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not user or not verificar_senha(dados.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    token = criar_token({"sub": str(user.id), "perfil": user.perfil})
    return {"access_token": token, "perfil": user.perfil}