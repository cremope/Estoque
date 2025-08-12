from fastapi import FastAPI, Depends, HTTPException, Header, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import uuid

from .database import Base, motor, obter_sessao, SessaoLocal
from .models import Produto
from .schemas import ProdutoCriar, ProdutoAtualizar, ProdutoResposta, ErroResposta
from . import crud as operacoes
from .config import CORS_ORIGINS, TEST_API_KEY
from .seed import criar_dados_iniciais

aplicacao = FastAPI(
    title="API de Estoque",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description="API para gerenciamento de produtos (retornos e erros padronizados em português)."
)

# CORS
aplicacao.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request-ID para rastreabilidade (útil em testes)
@aplicacao.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# Handlers em português
@aplicacao.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"codigo": exc.status_code, "mensagem": str(exc.detail)},
    )

@aplicacao.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = exc.errors()
    mensagens = []
    for e in erros:
        # loc ex.: ['body','campo'] | ['query','pular']
        loc = e.get("loc", [])
        campo = loc[-1] if loc else "dados"
        msg = e.get("msg", "")
        # pequenas traduções
        msg = (
            msg.replace("Field required", "é obrigatório")
               .replace("Input should be a valid number", "não é um número válido")
               .replace("String should have at least 1 character", "não pode ser vazio")
        )
        mensagens.append(f"O campo '{campo}' {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"codigo": 422, "mensagem": " | ".join(mensagens) or "Dados inválidos."},
    )

@aplicacao.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"codigo": 500, "mensagem": "Erro interno no servidor."},
    )

@aplicacao.get("/", tags=["saude"])
def raiz():
    return RedirectResponse(url="/docs", status_code=302)

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

# CREATE
@aplicacao.post(
    "/produtos",
    response_model=ProdutoResposta,
    status_code=201,
    tags=["produtos"],
    responses={
        201: {"description": "Criado com sucesso"},
        409: {"model": ErroResposta, "description": "Conflito (SKU já existe)"},
        422: {"model": ErroResposta, "description": "Dados inválidos"}
    }
)
def criar_produto_endpoint(
    dados: ProdutoCriar,
    response: Response,
    db: Session = Depends(obter_sessao)
):
    existente = operacoes.buscar_produto_por_sku(db, dados.codigo_sku)
    if existente:
        raise HTTPException(status_code=409, detail="SKU já existente")
    produto = operacoes.criar_produto(db, dados)
    # Location para testes de API
    response.headers["Location"] = f"/produtos/{produto.id}"
    return produto

# LIST + paginação documentada
@aplicacao.get(
    "/produtos",
    response_model=list[ProdutoResposta],
    tags=["produtos"],
    responses={
        200: {"description": "Lista paginada de produtos"},
        422: {"model": ErroResposta}
    }
)
def listar_produtos_endpoint(
    pular: int = Query(
        0, ge=0,
        description="Quantidade de registros a **pular** antes de começar a retornar (offset). Ex.: pular=50 começa a partir do 51º."
    ),
    limite: int = Query(
        50, ge=1, le=200,
        description="Quantidade **máxima** de registros a retornar (limit). Ex.: limite=20 retorna no máximo 20 itens."
    ),
    db: Session = Depends(obter_sessao)
):
    return operacoes.listar_produtos(db, pular, limite)

# GET by id
@aplicacao.get(
    "/produtos/{produto_id}",
    response_model=ProdutoResposta,
    tags=["produtos"],
    responses={404: {"model": ErroResposta}}
)
def buscar_produto_endpoint(produto_id: int, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

# PATCH
@aplicacao.patch(
    "/produtos/{produto_id}",
    response_model=ProdutoResposta,
    tags=["produtos"],
    responses={
        404: {"model": ErroResposta},
        409: {"model": ErroResposta},
        422: {"model": ErroResposta},
    }
)
def atualizar_produto_endpoint(produto_id: int, dados: ProdutoAtualizar, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if dados.codigo_sku:
        existente = operacoes.buscar_produto_por_sku(db, dados.codigo_sku)
        if existente and existente.id != produto_id:
            raise HTTPException(status_code=409, detail="SKU já existente")
    return operacoes.atualizar_produto(db, produto, dados)

# DELETE
@aplicacao.delete(
    "/produtos/{produto_id}",
    status_code=204,
    tags=["produtos"],
    responses={404: {"model": ErroResposta}}
)
def deletar_produto_endpoint(produto_id: int, db: Session = Depends(obter_sessao)):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    operacoes.deletar_produto(db, produto)
    return

# Ajuste de quantidade
@aplicacao.post(
    "/produtos/{produto_id}/ajustar",
    response_model=ProdutoResposta,
    tags=["produtos"],
    responses={404: {"model": ErroResposta}, 422: {"model": ErroResposta}}
)
def ajustar_quantidade_endpoint(
    produto_id: int,
    quantidade: int = Query(..., description="Delta de quantidade (ex.: 5 ou -3)"),
    db: Session = Depends(obter_sessao)
):
    produto = operacoes.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if produto.quantidade + quantidade < 0:
        raise HTTPException(status_code=422, detail="Resultado ficaria negativo")
    return operacoes.ajustar_quantidade(db, produto, quantidade)

# Limpeza de base para testes
@aplicacao.post(
    "/teste/resetar",
    tags=["teste"],
    responses={401: {"model": ErroResposta}}
)
def resetar_base_endpoint(
    db: Session = Depends(obter_sessao),
    x_api_key: str | None = Header(None)
):
    if not CHAVE_API_TESTE or x_api_key != CHAVE_API_TESTE:
        raise HTTPException(status_code=401, detail="Não autorizado")
    operacoes.resetar_base(db)
    return {"mensagem": "Base limpa"}