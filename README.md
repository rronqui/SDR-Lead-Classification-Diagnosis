# SDR Lead Classification System

Sistema de classificação e diagnóstico de leads B2B via WhatsApp utilizando LangChain, LangGraph, LangSmith, FastAPI e PostgreSQL.

![CI](https://github.com/rronqui/SDR-Lead-Classification-Diagnosis/actions/workflows/ci.yml/badge.svg)

## Estrutura do Projeto

```
SDR/
├── pyproject.toml            # Dependências Python (fonte única de versão)
├── .env.example              # Variáveis de ambiente (copiar para .env)
├── alembic.ini               # Configuração Alembic
├── alembic/                  # Migrations do banco de dados
├── src/
│   ├── api/
│   │   ├── config.py         # Configurações (inclui LangChain/LangSmith)
│   │   ├── routes.py         # Endpoints
│   │   └── main.py           # App
│   ├── agents/               # Agentes LangChain (rastreados via LangSmith)
│   │   ├── base.py           # BaseAgent com tracing LangSmith
│   │   ├── prompts.py        # System prompts
│   │   ├── schemas.py        # Input/Output schemas
│   │   ├── validar_resposta.py
│   │   ├── gerar_perguntas.py
│   │   ├── buscar_empresa.py
│   │   ├── buscar_linkedin.py
│   │   ├── classifica_lead.py
│   │   ├── gerar_diagnostico.py
│   │   └── msg_fechamento.py
│   ├── graph/                # LangGraph (rastreado via LangSmith)
│   │   ├── nodes.py          # Nós do grafo
│   │   ├── states.py         # Definições de estado
│   │   ├── new_lead.py
│   │   └── main_chat.py
│   ├── models/               # SQLAlchemy (6 tabelas)
│   ├── schemas/              # Pydantic API
│   └── services/             # Serviços externos (database, zapi, hubspot)
├── .github/                  # CI, release-please, templates
├── .githooks/                # Hooks git locais (commit-msg, pre-push)
└── scripts/                  # Scripts auxiliares (install-hooks.sh)
```

## Quick Start

### 1. Configuração do Ambiente

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate      # Windows

# Instalar dependências
pip install -e ".[dev]"

# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves API

# Instalar hooks git (Conventional Commits + proteção da master)
sh scripts/install-hooks.sh
```

### 2. Banco de Dados

```bash
# Criar banco
createdb sdr

# Executar migrations
alembic upgrade head
```

### 3. Executar API

```bash
uvicorn src.api.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

### 4. Documentação Interativa

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `DATABASE_URL` | Connection string PostgreSQL | Sim |
| `ZAPI_INSTANCE_ID` | ID da instância Z-API | Sim |
| `ZAPI_INSTANCE_TOKEN` | Token da instância Z-API | Sim |
| `ZAPI_SECURITY_TOKEN` | Security Token Z-API (Client-Token header) | Sim |
| `OPENROUTER_API_KEY` | Chave OpenRouter | Sim |
| `OPENROUTER_BASE_URL` | URL OpenRouter (padrão: https://openrouter.ai/api/v1) | Não |
| `OPENROUTER_MODEL` | Modelo LLM (padrão: openai/gpt-4o-mini) | Não |
| `SERPAPI_API_KEY` | Chave SerpAPI | Sim |
| `HUBSPOT_ACCESS_TOKEN` | Token HubSpot | Sim |
| `HUBSPOT_OWNER_ID` | ID do owner HubSpot | Sim |
| `MAX_PERGUNTAS` | Máx. perguntas diagnóstico (padrão: 6) | Não |
| `APP_ENV` | Ambiente (dev/test/prod) | Não |
| `LOG_LEVEL` | Nível de log (padrão: INFO) | Não |
| `LANGCHAIN_API_KEY` | Chave LangSmith para observabilidade | Não |
| `LANGCHAIN_PROJECT` | Nome do projeto no LangSmith (padrão: SDR-Lead-Classification-Diagnosis) | Não |

---

## Endpoints API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/webhooks/zapi` | Recebe mensagens do WhatsApp |
| POST | `/leads` | Cria novo lead |
| GET | `/leads/{id}` | Retorna lead específico |
| GET | `/leads` | Lista leads com filtros |
| GET | `/health` | Health check |
| GET | `/version` | Versão da aplicação (fonte: pyproject.toml) |

---

## Arquitetura

### Fluxo NewLead
1. Recebe trigger → cria lead
2. Pesquisa empresa (SerpAPI)
3. Valida LinkedIn (com pesquisa SerpAPI)
4. Gera primeira pergunta
5. Envia mensagem boas-vindas via Z-API

### Fluxo MainChat
1. Recebe resposta do lead
2. Valida pertinência (ValidarResposta)
3. Gera próxima pergunta (GerarPerguntas)
4. Repete até MAX_PERGUNTAS
5. Classifica lead (ClassificaLead)
6. Gera diagnóstico (GerarDiagnostico)
7. Cria msg fechamento (MsgFechamento)
8. Envia para HubSpot + WhatsApp

> **Nota:** Todas as execuções de agentes e chains são rastreadas via LangSmith.

---

## 7 Agentes LangChain

| # | Agente | Função |
|---|--------|-------|
| 1 | ValidarResposta | Valida se resposta é pertinente |
| 2 | GerarPerguntas | Gera roteiro de qualificação |
| 3 | BuscarEmpresa | Pesquisa dados via SerpAPI |
| 4 | BuscarLinkedIn | Valida perfil LinkedIn (com pesquisa SerpAPI) |
| 5 | ClassificaLead | Classifica A/B/C + score |
| 6 | GerarDiagnostico | Gera relatório técnico |
| 7 | MsgFechamento | Cria mensagem de fechamento |

---

## Stack

| Componente | Tecnologia |
|------------|------------|
| API | FastAPI 0.115.x |
| ORM | SQLAlchemy 2.0.x |
| Database | PostgreSQL 16 |
| Migrations | Alembic 1.13.x |
| Agentes | LangChain 0.3.x |
| Orquestração | LangGraph 0.2.x |
| LLM | OpenRouter (openai/gpt-4o-mini) |
| Search | SerpAPI |
| CRM | HubSpot |
| WhatsApp | Z-API |
| Observabilidade | LangSmith |

---

## Versionamento e Releases (SemVer)

O projeto segue [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- A versão vive em **um único lugar**: `pyproject.toml`. A API a expõe via
  `GET /version` e no OpenAPI (`importlib.metadata`).
- Commits seguem [Conventional Commits](https://www.conventionalcommits.org/),
  validados pelo hook local `commit-msg` (instale com `sh scripts/install-hooks.sh`):
  - `fix:` → bump PATCH | `feat:` → bump MINOR | `!` / `BREAKING CHANGE:` → bump MAJOR
- O [release-please](https://github.com/googleapis/release-please) roda no push da
  `master` e abre um PR de release (changelog + bump de versão). **Ninguém edita a
  versão manualmente**; o merge do PR de release gera a tag e o GitHub Release.
- O workflow usa o secret `RELEASE_PLEASE_TOKEN` (PAT): PRs criados com o
  `GITHUB_TOKEN` padrão não disparam outros workflows, e o PR de release precisa
  passar pelo CI obrigatório.
- Cadência de release é decisão humana: o PR de release é mergado manualmente.

### Atualizando uma instalação local após release

```bash
git checkout master && git pull --rebase
pip install -e ".[dev]"     # ou: docker-compose up -d --build
curl -s http://localhost:8000/version
```

---

## Como contribuir (fluxo protegido)

A branch `master` é protegida por ruleset: não aceita push direto nem
fast-forward, exige PR e o check `quality` do CI verde.

1. Abra uma issue (bug ou feature).
2. Crie uma branch: `fix/#N-<slug>` ou `feat/#N-<slug>`.
3. Commite com Conventional Commits.
4. Abra o PR com `Closes #N` no corpo.
5. CI (`quality`: ruff) deve passar; o merge é squash.

---

## Docker

### Executar com Docker

```bash
cp .env.example .env   # editar com suas chaves
docker-compose up --build
docker-compose logs -f app
docker-compose down
```

### Estrutura Docker

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `postgres` | 5432 (interno) | Banco de dados PostgreSQL |
| `app` | 8001 → 8000 | API FastAPI |
| `ngrok` | — | Túnel para webhooks (opcional) |

---

## Privacidade

O sistema processa mensagens de WhatsApp de leads (texto livre, potencialmente
com dados pessoais) e as sincroniza com o HubSpot. Para operar:

- Mantenha as credenciais apenas no `.env` (fora do versionamento); use
  `.env.example` só com nomes de variáveis.
- Os traces do LangSmith podem conter conteúdo das conversas — restrinja o
  acesso ao projeto no LangSmith.
- Não commite dados de leads, conversas ou credenciais reais.

---

## Licença

[MIT](LICENSE)
