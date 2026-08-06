# SDR Lead Classification System

Sistema de classificação e diagnóstico de leads B2B via WhatsApp utilizando LangChain, LangGraph, LangSmith, FastAPI e PostgreSQL.

## Estrutura do Projeto

```
SDR/
├── pyproject.toml            # Dependências Python
├── .env.example              # Variáveis de ambiente (copiar para .env)
├── alembic.ini               # Configuração Alembic
├── alembic/                  # Migrations do banco de dados
│   ├── env.py
│   └── versions/
│       ├── 001_initial.py
│       ├── 002_add_missing_fk_constraints.py
│       ├── 003_alter_objetivo_indicador_to_text.py
│       └── 004_remove_unused_diagnostico_fields.py
├── src/
│   ├── api/
│   │   ├── config.py         # Configurações (inclui LangChain/LangSmith)
│   │   ├── routes.py         # Endpoints
│   │   └── main.py           # App
│   ├── agents/               # Agentes LangChain (rastreados via LangSmith)
│   │   ├── __init__.py       # 7 agentes exportados
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
│   │   ├── __init__.py       # NewLeadGraph + MainChatGraph
│   │   ├── nodes.py          # Nós do grafo
│   │   ├── states.py         # Definições de estado
│   │   ├── new_lead.py
│   │   └── main_chat.py
│   ├── models/               # SQLAlchemy
│   │   ├── base.py
│   │   └── models.py         # 6 tabelas
│   ├── schemas/              # Pydantic API
│   │   └── __init__.py
│   └── services/             # Serviços externos
│       ├── database.py
│       ├── zapi.py
│       └── hubspot.py
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

---

## Arquitetura

### Fluxo NewLead
1. Recebe trigger → cria lead
2. Pesquisa empresa (SerpAPI)
3. Valida LinkedIn (com pesquisa SerpAPI)
4. Gera primeira pergunta
5. Envia mensagem boas-vindas via Z-API

> **Nota:** Todas as execuções de agentes são rastreadas via LangSmith.

### Fluxo MainChat
1. Recebe resposta do lead
2. Valida pertinência (ValidarResposta)
3. Gera próxima pergunta (GerarPerguntas)
4. Repete até MAX_PERGUNTAS
5. Classifica lead (ClassificaLead)
6. Gera diagnóstico (GerarDiagnostico)
7. Cria msg fechamento (MsgFechamento)
8. Envia para HubSpot + WhatsApp

> **Nota:** Cada agente executado envia traces para LangSmith, permitindo debug detalhado de cada etapa.

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

> **Nota:** Todas as execuções de agentes são rastreadas via **LangSmith** para debugging, análise de performance e otimização de prompts. |

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

### LangSmith (Observabilidade)

O projeto utiliza **LangSmith** para rastreamento completo das execuções de agentes e chains:

- **Tracing:** Todas as chamadas aos agentes LangChain e execuções do LangGraph são automaticamente rastreadas
- **Debugging:** Visualização detalhada de prompts, respostas e tokens utilizados
- **Métricas:** Latência por agente, contagem de tokens, custos
- **Projeto:** `SDR-Lead-Classification-Diagnosis` (configurável via `LANGCHAIN_PROJECT`)

Configure em `.env`:
```bash
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=SDR-Lead-Classification-Diagnosis
```

Acesse o dashboard em: https://smith.langchain.com/

---

## Licença

MIT

---

## Docker

### Preparação

```bash
# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves API
```

### Executar com Docker

```bash
# Build e start dos containers
docker-compose up --build

# Ver logs
docker-compose logs -f app

# Parar containers
docker-compose down
```

### Estrutura Docker

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| `postgres` | 5432 (interno) | Banco de dados PostgreSQL |
| `app` | 8000 | API FastAPI |

### Scripts Úteis

```bash
# Recriar banco de dados
docker-compose down -v
docker-compose up --build

# Acessar shell do container
docker-compose exec app sh
```