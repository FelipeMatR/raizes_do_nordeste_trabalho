# Raízes do Nordeste_Backend

API para gestão de rede de restaurantes regionais com multicanalidade (APP, TOTEM, BALCAO, PICKUP, WEB), estoque por unidade, fidelidade com consentimento LGPD e pagamento mock.

## 1. Stack
- Python 3.11+
- FastAPI
- SQLAlchemy + SQLite (pode trocar por Postgres via .env)
- Pydantic, python-jose (JWT), passlib pbkdf2_sha256
- Uvicorn
- python-dotenv

## 2. Arquitetura em Camadas
- **Domain**: `models/models.py` - Entidades: Unidade, Produto, Usuario, Estoque, Pedido, ItemPedido, Pagamento, MovimentoFidelidade. Regras: 1 ponto a cada R$10, estoque por unidade, pagamento 1:1 com unique=True.
- **Application**: `routes/` - Casos de uso: criar pedido, baixar estoque, gerar pontos, solicitar pagamento mock, atualizar status.
- **Infrastructure**: `database/database.py` - ORM, Base, SessionLocal, engine.
- **API**: `auth/auth.py` + `main.py` - Controllers, contratos request/response, Swagger/OpenAPI, JWT e autorização por perfil.

## 3. Requisitos
- Python 3.11 ou 3.12
- pip 24+
- Git

## 4. Variáveis de Ambiente
Crie um arquivo `.env` na raiz baseado no `.env.example`:

DATABASE_URL=sqlite:///./raizes.db
SECRET_KEY=BolodeMandiocacomChocolate
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8

## 5. Instalação

python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt


## 6. Banco e Migrations
Usa `Base.metadata.create_all` para criar as tabelas automaticamente.

Seed opcional: criar unidade e produtos via rotas `/unidades` e `/produtos` no Swagger.

## 7. Iniciar API

uvicorn main:app --reload

API: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs
Redoc: http://127.0.0.1:8000/redoc

## 8. Endpoints Principais
- POST /auth/registrar - criar usuário
- POST /auth/login - retorna JWT
- GET /unidades, POST /unidades
- GET /produtos, POST /produtos
- POST /estoque/ - adicionar estoque por unidade
- GET /estoque/{unidade_id} - cardápio por unidade
- POST /pedidos/ - criar pedido multicanal (canal_pedido obrigatório: APP, TOTEM, BALCAO, PICKUP, WEB)
- GET /pedidos?canalPedido=APP&status=AGUARDANDO_PAGAMENTO - filtro obrigatório roteiro p.8
- PATCH /pedidos/{pedido_id}/status?status=PREPARANDO
- POST /pagamentos/{pedido_id}?forma_pagamento=MOCK - mock 80% APROVADO / 20% RECUSADO, retorna payload_mock
- POST /fidelidade/optin/{cliente_id}
- GET /fidelidade/saldo/{cliente_id}
- POST /fidelidade/resgatar/{cliente_id}?pontos=10

## 9. Regra de Fidelidade
1 ponto a cada R$10 em compras, apenas se consentimento_fidelidade=true. Histórico salvo em movimentos_fidelidade com tipo ACUMULO e RESGATE.

## 10. LGPD, Privacidade e Segurança (Obrigatório roteiro p.8)
-Dados pessoais coletados: nome, email, senha (armazenada como hash), pontos, consentimento_fidelidade.
-Finalidade: Autenticação, gestão de pedidos e programa de fidelidade.
-Base legal: Consentimento Art.7º I LGPD para fidelidade; Execução de contrato para pedidos.
-Como consentimento é registrado:** Campo Boolean consentimento_fidelidade em usuarios + created_at + rota POST /fidelidade/optin/{id} que seta True. Revogação via PATCH setando False.
-Controles mínimos implementados:
- Hash de senha: passlib pbkdf2_sha256 em security/security.py
- Autenticação por token: JWT criar_token com exp 8h
- Autorização por perfil: perfil = CLIENTE, ATENDENTE, GERENTE
- Logs de acesso: log de login e resgate de pontos
- Retenção/Anonimização: created_at para auditoria; estratégia futura anonimizar email após 5 anos
- Respostas seguras: nunca retorna senha_hash nos responses

## 11. Pagamento Mock - Fluxo Crítico
Pedido criado como AGUARDANDO_PAGAMENTO -> POST /pagamentos/{id} -> cria registro em pagamentos com payload_mock JSON -> se APROVADO status vira PAGO, se RECUSADO mantém AGUARDANDO_PAGAMENTO. Pagamento desacoplado 1:1 (pedido_id unique=True) conforme DER exigido.

## 12. Plano de Testes e Como Rodar
Importe `Raizes_do_Nordeste.postman_collection.json` no Postman.
Cenários: 6 positivos e 4 negativos cobrindo 401, 400, 409, pagamento RECUSADO.
