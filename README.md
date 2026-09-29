# Raízes do Nordeste - Backend

API para gestão de pedidos, estoque e fidelidade.

## Stack
FastAPI + SQLAlchemy + SQLite

## Rodar
pip install -r requirements.txt
uvicorn main:app --reload
Acesse: http://127.0.0.1:8000/docs

## Endpoints
- POST /auth/registrar - criar usuário
- POST /pedidos/ - criar pedido
- GET /fidelidade/saldo/{cliente_id} - ver pontos
- POST /fidelidade/resgatar/{cliente_id}?pontos=X - resgatar pontos

## Regra fidelidade
1 ponto a cada R$10, apenas com consentimento_fidelidade=true