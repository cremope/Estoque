from sqlalchemy.orm import Session
from .models import Produto


def criar_dados_iniciais(db: Session):
    # Insere somente se não houver nenhum registro
    if db.query(Produto).count() == 0:
        itens = [
            Produto(nome="Mouse Gamer", codigo_sku="SKU-001", preco=150.00, quantidade=25),
            Produto(nome="Teclado Mecânico", codigo_sku="SKU-002", preco=350.00, quantidade=15),
            Produto(nome="Monitor 24''", codigo_sku="SKU-003", preco=899.90, quantidade=10),
            Produto(nome="Headset USB", codigo_sku="SKU-004", preco=199.90, quantidade=20),
        ]
        db.add_all(itens)
        db.commit()