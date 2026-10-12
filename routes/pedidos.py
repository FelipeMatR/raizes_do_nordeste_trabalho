from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.models import Pedido, ItemPedido, Produto, Estoque, Usuario, Unidade, MovimentoFidelidade
from schemas.schemas import PedidoCreate
from security.security import exigir_perfis

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("/")
def criar_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db)
):
    
    # 1. Validar cliente
    cliente = db.query(Usuario).filter(
        Usuario.id == dados.cliente_id
    ).first()

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )

    # 2. Validar unidade
    unidade = db.query(Unidade).filter(
        Unidade.id == dados.unidade_id
    ).first()

    if unidade is None:
        raise HTTPException(
            status_code=404,
            detail="Unidade não encontrada"
        )

    # 3. Validar se existem itens no pedido
    if not dados.itens:
        raise HTTPException(
            status_code=400,
            detail="O pedido deve possuir pelo menos um item"
        )

    # 4. Agrupa os produtos por ID e soma as quantidades
    produtos_agrupados = {}

    for item in dados.itens:
        if item.quantidade <= 0:
            raise HTTPException(
                status_code=400,
                detail="A quantidade do produto deve ser maior que zero"
            )

        if item.produto_id in produtos_agrupados:
            produtos_agrupados[item.produto_id] += item.quantidade
        else:
            produtos_agrupados[item.produto_id] = item.quantidade

    # 5. Validar produtos e estoque
    itens_validados = []
    total = 0

    for produto_id, quantidade in produtos_agrupados.items():

        produto = db.query(Produto).filter(
            Produto.id == produto_id
        ).first()

        if produto is None:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {produto_id} não encontrado"
            )

        estoque = db.query(Estoque).filter(
            Estoque.produto_id == produto_id,
            Estoque.unidade_id == dados.unidade_id
        ).first()

        if estoque is None:
            raise HTTPException(
                status_code=409,
                detail=f"Produto {produto.nome} sem estoque nesta unidade"
            )

        if estoque.quantidade < quantidade:
            raise HTTPException(
                status_code=409,
                detail=f"Estoque insuficiente para o produto {produto.nome}"
            )

        subtotal = produto.preco * quantidade
        total += subtotal

        itens_validados.append({
            "produto": produto,
            "estoque": estoque,
            "quantidade": quantidade
        })

    # 6. Criar pedido
    novo_pedido = Pedido(
        cliente_id=dados.cliente_id,
        unidade_id=dados.unidade_id,
        canal_pedido=dados.canal_pedido,
        status="CRIADO",
        total=total,
        pontos_gerados=0
    )

    db.add(novo_pedido)

    # flush gera o ID
    db.flush()

    # 7. Criar itens e fazer baixa no estoque
    for item in itens_validados:

        produto = item["produto"]
        estoque = item["estoque"]
        quantidade = item["quantidade"]

        novo_item = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco
        )

        db.add(novo_item)

        estoque.quantidade -= quantidade

    # 8. Fidelidade
    if cliente.consentimento_fidelidade:
        pontos = int(total)

        if pontos > 0:
            cliente.pontos += pontos
            novo_pedido.pontos_gerados = pontos

            movimento = MovimentoFidelidade(
                cliente_id=cliente.id,
                tipo="CREDITO",
                pontos=pontos,
                descricao=f"Pontos gerados pelo pedido {novo_pedido.id}"
            )

            db.add(movimento)

    # 9. Confirmar alterações
    try:
        db.commit()
        db.refresh(novo_pedido)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao registrar o pedido"
        )

    return novo_pedido


@router.get("/")
def listar_pedidos(
    canalPedido: str = None,
    status: str = None,
    unidade_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Pedido)

    if canalPedido:
        query = query.filter(
            Pedido.canal_pedido == canalPedido
        )

    if status:
        query = query.filter(
            Pedido.status == status
        )

    if unidade_id:
        query = query.filter(
            Pedido.unidade_id == unidade_id
        )

    return query.all()


@router.get("/{pedido_id}")
def consultar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    return pedido


@router.patch("/{pedido_id}/status")
def atualizar_status(
    pedido_id: int,
    novo_status: str,
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    status_validos = [
        "CRIADO",
        "AGUARDANDO_PAGAMENTO",
        "PAGO",
        "EM_PREPARO",
        "PRONTO",
        "ENTREGUE",
        "CANCELADO"
    ]

    novo_status = novo_status.upper()

    if novo_status not in status_validos:
        raise HTTPException(
            status_code=400,
            detail="Status inválido"
        )

    pedido.status = novo_status

    db.commit()
    db.refresh(pedido)

    return pedido