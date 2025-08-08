from sqlalchemy import Column, Integer, String, Numeric
from .database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    codigo_sku = Column(String(64), unique=True, index=True, nullable=False)
    preco = Column(Numeric(10, 2), nullable=False, default=0)
    quantidade = Column(Integer, nullable=False, default=0)