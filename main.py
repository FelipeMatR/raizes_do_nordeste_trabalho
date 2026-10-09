from fastapi import FastAPI
from database.database import Base, engine
from models import models
from routes import unidades, produtos, estoque, pedidos, fidelidade, pagamentos
from auth.auth import router as auth_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Raizes do Nordeste API")
app.include_router(auth_router)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(fidelidade.router)
app.include_router(pagamentos.router)

@app.get("/")
def root(): return {"status": "Raizes do Nordeste API online"}