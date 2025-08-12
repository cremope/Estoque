
**Estoque**

API REST para gerenciamento de produtos em estoque, construída com FastAPI, SQLAlchemy e PostgreSQL. Inclui documentação automática (Swagger e ReDoc), paginação, validações e retornos de erro padronizados em português.

Produção: https://estoque-6ldl.onrender.com
Swagger: https://estoque-6ldl.onrender.com/docs
ReDoc: https://estoque-6ldl.onrender.com/redoc

---

**Dependências**
- Python 3.12
- FastAPI – framework web
- Uvicorn – servidor ASGI
- SQLAlchemy 2 – ORM
- Pydantic 2 – validação de dados
- psycopg – driver PostgreSQL
- python-dotenv – variáveis de ambiente
- Render – deploy da API e do banco PostgreSQL

**Estrutura (resumo)**
```bash
app/
 ├─ config.py    # Leitura de env (DATABASE_URL, CORS, etc.)       
 ├─ crud.py      # Operações (camada de repositório)
 ├─ database.py  # Engine, sessão e Base (SQLAlchemy)
 ├─ main.py      # Controllers e endpoints
 ├─ models.py    # Tabela Produto
 ├─ schemas.py   # Schemas Pydantic (entrada/saída + ErroResposta)
 ├─ seed.py      # Seed de dados
.env             # Variáveis de ambiente
Readme.md        # Readme
```


**Padrões de resposta**

**Sucesso:**
```bash
{
  "id": 1,
  "nome": "Teclado Mecânico",
  "codigo_sku": "SKU-100",
  "preco": 259.90,
  "quantidade": 10
}
```

**Obs:** SKU é a sigla para Stock Keeping Unit (Unidade de Manutenção de Estoque).

**Erro (padronizado em pt-BR):**
```bash
- 422 → { "codigo": 422, "mensagem": "O campo 'preco' não é um número válido" }
- 404 → { "codigo": 404, "mensagem": "Produto não encontrado" }
- 409 → { "codigo": 409, "mensagem": "SKU já existente" }
- 401 → { "codigo": 401, "mensagem": "Não autorizado" }
- 500 → { "codigo": 500, "mensagem": "Erro interno no servidor." }
```
**Endpoints**

Base URL (produção): https://estoque-6ldl.onrender.com

**Controller saude**
```bash
GET / → redireciona para /docs - Health da aplicação
```

**Controller produtos**
```bash
POST /produtos → cria produto
GET /produtos?pular=0&limite=50 → lista produtos (paginação)
GET /produtos/{produto_id} → busca por ID
PATCH /produtos/{produto_id} → atualiza parcialmente
DELETE /produtos/{produto_id} → remove produto
POST /produtos/{produto_id}/ajustar?quantidade=5 → ajusta estoque
```
**Controller teste**
```bash
POST /teste/resetar → limpa base (apenas testes)
```

**Render**

[Render](https://render.com/) é uma plataforma de nuvem para publicar APIs, web apps e bancos de dados sem complicação. 

Neste projeto:
- Web Service (API FastAPI)
- PostgreSQL (Render Managed DB)
- Internal Database URL → uso no Render
- External Database URL → uso local
- Integração com o GitHub


**Importante:** Todo deploy ocorre automaticamente quando a branch main é alterada. Portanto, caso ocorra alguma alteração de código na branch main, é iniciada uma nova build.

**Modelo de dados**

Tabela produtos no PostgreSQL:
```bash
- id (int, PK)
- nome (str)
- codigo_sku (str único)
- preco (decimal ≥ 0)
- quantidade (int ≥ 0)
```

**Rodando localmente**

```bash
git clone https://github.com/cremope/Estoque.git
cd Estoque
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts ctivate no Windows
pip install -r requirements.txt
```
Utilize esses valores no arquivo .env:
**DATABASE_URL**=postgresql://estoque_az2q_user:yPuE0M335JBdObC1u7ibqNL60vr5XJok@dpg-d2b75uje5dus73ca5l20-a.oregon-postgres.render.com/estoque_az2q
**TEST_API_KEY**=e25256b2e50ccfcb9baa5d80f3077bb6
**CORS_ORIGINS**=https://cremope.github.io/RCremonez

Execute o comando abaixo para subir a API:
```bash
uvicorn app.main:aplicacao --reload
```
o comando Uvicorn não abre o navegador automaticamente. Ele só mostra a URL onde está rodando. Veja qual a URL que mostra nos logs do terminal após rodar o comando, abaixo segue exemplo:

-   **Base URL**: `http://127.0.0.1:8000`
-   **Swagger**: `http://127.0.0.1:8000/docs`
-   **ReDoc**: `http://127.0.0.1:8000/redoc`

**Obs:** A Base URL pode ser usada no Postman, navegador para executar os endpoints.

## ScreenShots

**Render Dashboard:**

<img src="https://github.com/cremope/Estoque/blob/main/ScreenShots/Dashboard_Render.png" width="400" /> 

**Render deploy/buid:**

<img src="https://github.com/cremope/Estoque/blob/main/ScreenShots/Deploy_Render.png" width="400" /> 

**Documentação Swagger:**

<img src="https://github.com/cremope/web-java-playwright-cucumber/blob/main/ScreenShots/Documentacao_Swagger.png" width="400" />

**Documentação Redoc:**

<img src="https://github.com/cremope/web-java-playwright-cucumber/blob/main/ScreenShots/Documentacao_Redoc.png" width="400" /> 