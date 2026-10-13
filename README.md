# Raízes do Nordeste - Backend

API REST desenvolvida em Python com FastAPI para representar operações
de uma rede de restaurantes, incluindo cadastro de usuários, unidades e
produtos, estoque por unidade, pedidos multicanal, pagamento mock e
programa de fidelidade.

## 1. Tecnologias

-   Python 3.11 ou superior
-   FastAPI
-   Uvicorn
-   SQLAlchemy
-   SQLite
-   Pydantic
-   email-validator
-   Passlib com `pbkdf2_sha256`
-   python-jose para JWT
-   python-multipart
-   python-dotenv

## 2. Estrutura do projeto

``` text
projeto/
├── auth/
│   └── auth.py
├── database/
│   └── database.py
├── models/
│   └── models.py
├── routes/
│   ├── auth.py
│   ├── estoque.py
│   ├── fidelidade.py
│   ├── pagamentos.py
│   ├── pedidos.py
│   ├── produtos.py
│   └── unidades.py
├── schemas/
│   └── schemas.py
├── security/
│   └── security.py
├── .envexample
├── .gitignore
├── main.py
├── README.md
└── requiriments.txt
```

### Responsabilidade dos módulos

-   `main.py`: cria a aplicação FastAPI, cria as tabelas e registra os
    routers.
-   `database/database.py`: configura SQLite, SQLAlchemy, `Base`,
    `SessionLocal` e `get_db`.
-   `models/models.py`: contém as entidades persistidas.
-   `schemas/schemas.py`: contém os modelos Pydantic usados nas
    entradas.
-   `auth/auth.py`: cadastro e login.
-   `security/security.py`: hash de senha, geração/validação de JWT e
    função de verificação de perfil.
-   `routes/`: endpoints de unidades, produtos, estoque, pedidos,
    pagamentos e fidelidade.

## 3. Instalação

Abra a pasta do projeto no VS Code e abra um terminal.

### Criar ambiente virtual

No Windows:

``` powershell
python -m venv venv
```

Ative:

``` powershell
venv\Scripts\activate
```

Se o PowerShell bloquear a ativação, também é possível executar os
comandos usando diretamente o Python instalado, desde que as
dependências estejam instaladas.

### Instalar dependências

O arquivo do projeto está nomeado `requiriments.txt`. Portanto, com o
nome atual:

``` powershell
pip install -r requiriments.txt
```

Dependências declaradas:

``` text
fastapi
uvicorn[standard]
sqlalchemy
pydantic
email-validator
passlib
python-jose[cryptography]
python-multipart
python-dotenv
```

## 4. Banco de dados

O projeto usa SQLite:

``` text
sqlite:///./raizes.db
```

As tabelas são criadas automaticamente na inicialização por:

``` python
Base.metadata.create_all(bind=engine)
```

Entidades existentes:

-   `Unidade`
-   `Produto`
-   `Usuario`
-   `Estoque`
-   `Pedido`
-   `ItemPedido`
-   `Pagamento`
-   `MovimentoFidelidade`

## 5. Executar a API

Na raiz do projeto:

``` powershell
python -m uvicorn main:app --reload
```

Alternativamente:

``` powershell
py -m uvicorn main:app --reload
```

Com a aplicação iniciada:

-   API local: `http://127.0.0.1:8000`
-   Swagger: `http://127.0.0.1:8000/docs`
-   ReDoc: `http://127.0.0.1:8000/redoc`

A rota raiz deve retornar:

``` json
{
  "status": "Raizes do Nordeste API online"
}
```

## 6. Autenticação

### Registrar usuário

`POST /auth/registrar`

Exemplo:

``` json
{
  "nome": "Bruno Andras",
  "email": "bruno@teste.com",
  "senha": "teste",
  "perfil": "CLIENTE",
  "consentimento_fidelidade": true
}
```

Perfis aceitos pelo cadastro:

-   `CLIENTE`
-   `ATENDENTE`
-   `COZINHA`
-   `ADMIN`

Se o e-mail já existir, a API retorna `409`.

### Login

`POST /auth/login`

``` json
{
  "email": "bruno@teste.com",
  "senha": "teste"
}
```

O login retorna um JWT, o tipo `bearer`, o perfil e dados básicos do
usuário. O token tem expiração configurada para 8 horas.

## 7. Unidades

### Criar unidade

`POST /unidades/`

``` json
{
  "nome": "LipeFood",
  "cidade": "Campinas",
  "endereco": "Rua Jetiba, numero 0"
}
```

### Listar unidades

`GET /unidades/`

### Consultar unidade por ID

`GET /unidades/{unidade_id}`

Exemplo:

``` text
GET /unidades/1
```

Unidade inexistente retorna `404`.

## 8. Produtos

### Criar produto

`POST /produtos/`

``` json
{
  "nome": "Bolo de Mandioca com Chocolate",
  "preco": 45,
  "descricao": "Bolo delicioso de mandioca coberto com chocolate"
}
```

### Listar produtos

`GET /produtos/`

## 9. Estoque

### Adicionar estoque

`POST /estoque/`

``` json
{
  "produto_id": 1,
  "unidade_id": 1,
  "quantidade": 10
}
```

Se já existir um registro para a combinação produto/unidade, a
quantidade enviada é somada ao estoque atual.

### Consultar produto no estoque de uma unidade

`GET /estoque/{unidade_id}/produto/{produto_id}`

Exemplo:

``` text
GET /estoque/1/produto/1
```

A consulta valida unidade, produto e registro de estoque e pode retornar
`404`.

## 10. Pedidos

### Criar pedido

`POST /pedidos/`

Exemplo usado nos testes:

``` json
{
  "cliente_id": 1,
  "unidade_id": 1,
  "canal_pedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 1
    }
  ]
}
```

Ao criar um pedido, o código:

1.  valida o cliente;
2.  valida a unidade;
3.  verifica se existem itens;
4.  rejeita quantidade menor ou igual a zero;
5.  agrupa produtos repetidos;
6.  valida produto e estoque na unidade;
7.  rejeita estoque insuficiente;
8.  calcula o total;
9.  cria o pedido;
10. cria os itens;
11. baixa a quantidade do estoque;
12. gera pontos se o cliente tiver consentimento de fidelidade;
13. confirma a transação.

O pedido é criado com status `CRIADO`.

### Pontos gerados

No código atual:

``` python
pontos = int(total)
```

Portanto, quando há consentimento, a quantidade de pontos gerada
corresponde à parte inteira do valor total do pedido. Exemplo: total
`45.00` gera `45` pontos.

### Listar pedidos

`GET /pedidos/`

Filtros opcionais:

``` text
?canalPedido=APP
?status=PAGO
?unidade_id=1
```

Os filtros podem ser combinados.

### Consultar pedido por ID

`GET /pedidos/{pedido_id}`

### Atualizar status

`PATCH /pedidos/{pedido_id}/status`

O parâmetro `novo_status` é recebido como query parameter.

Valores aceitos:

-   `CRIADO`
-   `AGUARDANDO_PAGAMENTO`
-   `PAGO`
-   `EM_PREPARO`
-   `PRONTO`
-   `ENTREGUE`
-   `CANCELADO`

Exemplo:

``` text
PATCH /pedidos/1/status?novo_status=EM_PREPARO
```

## 11. Pagamento mock

`POST /pagamentos/{pedido_id}`

A forma de pagamento é enviada por query parameter.

Exemplo:

``` text
POST /pagamentos/1?forma_pagamento=CARTAO
```

Formas aceitas:

-   `PIX`
-   `CARTAO`
-   `DINHEIRO`

O mock utiliza uma simulação aleatória:

``` python
aprovado = random.randint(1, 5) != 5
```

Assim, cada chamada tem aproximadamente 80% de chance de aprovação e 20%
de chance de recusa.

Quando aprovado:

-   pagamento: `APROVADO`
-   pedido: `PAGO`

Quando recusado:

-   pagamento: `RECUSADO`
-   pedido: `AGUARDANDO PAGAMENTO`

O pagamento possui relação 1:1 com o pedido por `pedido_id` único. Se já
houver pagamento para o pedido, o registro existente é atualizado.

## 12. Fidelidade

### Ativar participação

`POST /fidelidade/optin/{cliente_id}`

Registra `consentimento_fidelidade = true`.

### Consultar saldo

`GET /fidelidade/saldo/{cliente_id}`

### Resgatar pontos

`POST /fidelidade/resgatar/{cliente_id}`

O número de pontos é enviado no Body:

``` json
{
  "cliente_id": 1,
  "pontos": 10
}
```

O código valida:

-   existência do cliente;
-   consentimento;
-   pontos maiores que zero;
-   saldo suficiente.

## 13. Segurança e privacidade

O código fornecido contém:

-   hash de senha com `pbkdf2_sha256`;
-   JWT HS256;
-   expiração de token em 8 horas;
-   função de obtenção do usuário atual;
-   função `exigir_perfis`;
-   resposta de cadastro sem `senha_hash`;
-   campo de consentimento para fidelidade.

A chave JWT está definida diretamente em `security/security.py` e também
aparece no arquivo `.envexample`. O código de banco e segurança
fornecido não lê essas configurações do `.env`.

Não foi identificada, no código fornecido, implementação de logs de
auditoria, endpoint de revogação do consentimento ou rotina automática
de anonimização/retenção. Esses itens não devem ser apresentados como
implementados.

## 14. Testes no Postman - preparação

### 14.1 Criar Environment

Crie um Environment chamado `local`.

Variável:

``` text
baseUrl = http://127.0.0.1:8000
```

Assim, as requisições podem utilizar:

``` text
{{baseUrl}}
```

### 14.2 Ordem recomendada

Execute os testes nesta ordem, pois os IDs criados são utilizados nas
etapas seguintes:

1.  Registrar usuário.
2.  Fazer login.
3.  Criar produto.
4.  Criar unidade.
5.  Adicionar estoque.
6.  Criar pedido.
7.  Processar pagamento.
8.  Executar os quatro cenários negativos.

Se os IDs gerados não forem `1`, substitua os exemplos pelos IDs
realmente retornados pela sua API.

## 15. Testes positivos executados

### T-1 - Registrar usuário

**Método:** `POST`

``` text
{{baseUrl}}/auth/registrar
```

Body:

``` json
{
  "nome": "Bruno Andras",
  "email": "bruno@teste.com",
  "senha": "teste",
  "perfil": "CLIENTE",
  "consentimento_fidelidade": true
}
```

Resultado observado: `201 Created`.

### T-2 - Login

**Método:** `POST`

``` text
{{baseUrl}}/auth/login
```

Body:

``` json
{
  "email": "bruno@teste.com",
  "senha": "teste"
}
```

Resultado observado: `200 OK`, com `access_token`.

### T-3 - Criar produto

**Método:** `POST`

``` text
{{baseUrl}}/produtos/
```

Body:

``` json
{
  "nome": "Bolo de Mandioca com Chocolate",
  "preco": 45,
  "descricao": "Bolo delicioso de mandioca coberto com chocolate"
}
```

Resultado observado: `200 OK`.

### T-4 - Criar unidade

**Método:** `POST`

``` text
{{baseUrl}}/unidades/
```

Body:

``` json
{
  "nome": "LipeFood",
  "cidade": "Campinas",
  "endereco": "Rua Jetiba, numero 0"
}
```

Resultado observado: `200 OK`.

### T-5 - Adicionar estoque

**Método:** `POST`

``` text
{{baseUrl}}/estoque/
```

Body:

``` json
{
  "produto_id": 1,
  "unidade_id": 1,
  "quantidade": 10
}
```

Resultado observado: `200 OK`.

### T-6 - Criar pedido

**Método:** `POST`

``` text
{{baseUrl}}/pedidos/
```

Body:

``` json
{
  "cliente_id": 1,
  "unidade_id": 1,
  "canal_pedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 1
    }
  ]
}
```

Resultado: `200 OK`. No teste apresentado, o pedido foi criado
com total `45.0`, status `CRIADO` e `45` pontos gerados.

### T-7 - Pagamento

**Método:** `POST`

``` text
{{baseUrl}}/pagamentos/1
```

Em `Params`:

``` text
forma_pagamento = CARTAO
```

A URL final fica:

``` text
{{baseUrl}}/pagamentos/1?forma_pagamento=CARTAO
```

Resultado observado no teste apresentado: `200 OK`, pagamento `APROVADO`
e pedido `PAGO`.

## 16. Quatro testes negativos executados

### T-1E - Pagamento de pedido inexistente

**Método:** `POST`

``` text
{{baseUrl}}/pagamentos/9999?forma_pagamento=CARTAO
```

Resultado observado:

``` text
404 Not Found
```

``` json
{
  "detail": "Pedido não encontrado"
}
```

### T-2E - Forma de pagamento inválida

**Método:** `POST`

``` text
{{baseUrl}}/pagamentos/1?forma_pagamento=BOLETO
```

Resultado observado:

``` text
400 Bad Request
```

``` json
{
  "detail": "Forma de pagamento inválida"
}
```

### T-3E - Produto inexistente

**Método:** `POST`

``` text
{{baseUrl}}/pedidos/
```

Body:

``` json
{
  "cliente_id": 1,
  "unidade_id": 1,
  "canal_pedido": "APP",
  "itens": [
    {
      "produto_id": 53,
      "quantidade": 1
    }
  ]
}
```

Resultado observado:

``` text
404 Not Found
```

``` json
{
  "detail": "Produto 53 não encontrado"
}
```

### T-4E - Estoque insuficiente

**Método:** `POST`

``` text
{{baseUrl}}/pedidos/
```

Body:

``` json
{
  "cliente_id": 1,
  "unidade_id": 1,
  "canal_pedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 5000
    }
  ]
}
```

Resultado observado:

``` text
409 Conflict
```

``` json
{
  "detail": "Estoque insuficiente para o produto Bolo de Mandioca com Chocolate"
}
```

## 17. Evidências dos testes

Para o relatório acadêmico, mantenha capturas que mostrem, sempre que
possível:

-   nome do teste;
-   método HTTP;
-   URL;
-   Body ou Params;
-   código HTTP retornado;
-   JSON de resposta.

As capturas já realizadas no Postman devem ser usadas como evidência dos
resultados efetivamente obtidos.

## 18. Exportar a coleção do Postman

No Postman:

1.  Localize a coleção que contém os testes do projeto.
2.  Clique nos três pontos ao lado do nome.
3.  Clique em `Export`.
4.  Escolha o formato de coleção oferecido pelo Postman,
    preferencialmente Collection v2.1.
5.  Salve o JSON junto aos arquivos de entrega.

Se a coleção usa `{{baseUrl}}`, exporte também o Environment `local` ou
documente que a variável deve possuir:

``` text
http://127.0.0.1:8000
```


## 19. Observações de conformidade documental

Este README descreve apenas recursos identificados no código e
resultados mostrados nos testes. Ele não declara como implementados
recursos que não aparecem na versão fornecida.

Pontos que devem ser tratados no relatório como limitações, caso
permaneçam assim na versão entregue:

-   não há paginação nas listagens;
-   os erros usam `{"detail": ...}` e não um envelope de erro
    padronizado completo;
-   não foi identificada aplicação efetiva de autorização por perfil nas
    rotas;
-   não foram identificados logs de auditoria;
-   não foi identificada revogação de consentimento;
-   não foram identificadas migrations formais;
-   a configuração de banco e JWT está fixa no código, sem leitura
    efetiva do `.env`;
-   o nome do arquivo de dependências fornecido é `requiriments.txt`.

