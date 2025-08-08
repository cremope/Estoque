from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido. Configure no .env ou em variáveis de ambiente.")

# Se vier como 'postgresql://', força psycopg3:
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    
# pool_pre_ping evita conexões zumbis em hospedagens gratuitas
motor = create_engine(DATABASE_URL, pool_pre_ping=True)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
Base = declarative_base()

# Dependência para injetar sessão do banco no FastAPI

def obter_sessao():
    db = SessaoLocal()
    try:
        yield db
    finally:
        db.close()

