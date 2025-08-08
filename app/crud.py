from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import Produto
from .schemas import ProdutoCriar, ProdutoAtualizar


def criar_produto(db: Session, dados: ProdutoCriar) -> Produto:
    produto = Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def listar_produtos(db: Session, pular: int = 0, limite: int = 50):
    consulta = select(Produto).offset(pular).limit(limite)
    return db.execute(consulta).scalars().all()


def buscar_produto(db: Session, produto_id: int):
    return db.get(Produto, produto_id)


def buscar_produto_por_sku(db: Session, codigo_sku: str):
    consulta = select(Produto).where(Produto.codigo_sku == codigo_sku)
    return db.execute(consulta).scalar_one_or_none()


def atualizar_produto(db: Session, produto: Produto, dados: ProdutoAtualizar) -> Produto:
    atualizacoes = dados.model_dump(exclude_unset=True)
    for campo, valor in atualizacoes.items():
        setattr(produto, campo, valor)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def deletar_produto(db: Session, produto: Produto):
    db.delete(produto)
    db.commit()


def ajustar_quantidade(db: Session, produto: Produto, delta: int) -> Produto:
    produto.quantidade = (produto.quantidade or 0) + delta
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def resetar_base(db: Session):
    db.query(Produto).delete()
    db.commit()