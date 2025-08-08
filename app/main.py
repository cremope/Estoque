from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, motor, obter_sessao, SessaoLocal
from .models import Produto
from .schemas import ProdutoCriar, ProdutoAtualizar, ProdutoResposta
from . import crud as operacoes
from .config import CORS_ORIGINS, TEST_API_KEY
from .seed import criar_dados_iniciais

aplicacao = FastAPI(
    title="API de Estoque",
    version="1.0.0",
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json"
)

# CORS
aplicacao.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@aplicacao.on_event("startup")
def ao_iniciar():
    # Cria tabelas e popula seed se necessário
    Base.metadata.create_all(bind=motor)
    db = SessaoLocal()
    try:
        criar_dados_iniciais(db)
    finally:
        db.close()


@aplicacao.get("/", tags=["saude"])
def saude():
    return {"status": "ok"}


# CRUD de Produtos
@aplicacao.post("/produtos", response_model=ProdutoResposta, status_code=201, tags=["produtos"])
def criar_produto_endpoint(dados: ProdutoCriar, db: Session = Depends(obter_sessao)):
    if operacoes.buscar_produto_por_sku(db, dados.codigo_sku):
        raise HTTPException(status_code=409, detail="SKU já existe")
    return operacoes.criar_produto(db, dados)


@aplicacao.get("/produtos", response_model=list[ProdutoResposta], tags=["produtos"])
def listar_produtos_endpoint(pular: int = 0, limite: int = 50, db: Session = Depends(obter_sessao)):
    return operacoes.listar_produtos(db, pular, limite)


@aplicacao.get("/produtos/{produto_id}", response_model=ProdutoResposta, tags=["produtos"])
def buscar_produto_endpoint(produto_id: int, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@aplicacao.patch("/produtos/{produto_id}", response_model=ProdutoResposta, tags=["produtos"])
def atualizar_produto_endpoint(produto_id: int, dados: ProdutoAtualizar, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if dados.codigo_sku:
        existente = operacoes.buscar_produto_por_sku(db, dados.codigo_sku)
        if existente and existente.id != produto_id:
            raise HTTPException(status_code=409, detail="SKU já existe")
    return operacoes.atualizar_produto(db, produto, dados)


@aplicacao.delete("/produtos/{produto_id}", status_code=204, tags=["produtos"])
def deletar_produto_endpoint(produto_id: int, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    operacoes.deletar_produto(db, produto)
    return


@aplicacao.post("/produtos/{produto_id}/ajustar", response_model=ProdutoResposta, tags=["produtos"])
def ajustar_quantidade_endpoint(produto_id: int, quantidade: int, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return operacoes.ajustar_quantidade(db, produto, quantidade)


@aplicacao.post("/teste/resetar", tags=["teste"])
def resetar_base_endpoint(db: Session = Depends(obter_sessao), x_api_key: str | None = Header(None)):
    if not TEST_API_KEY or x_api_key != TEST_API_KEY:
        raise HTTPException(status_code=401, detail="Não autorizado")
    operacoes.resetar_base(db)
    return {"mensagem": "Base limpa"}