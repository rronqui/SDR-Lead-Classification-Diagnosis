# AGENTS.MD

## Stack
- **API:** FastAPI 0.115.x + Uvicorn
- **ORM:** SQLAlchemy 2.0.x + Alembic
- **Database:** PostgreSQL 16
- **LLM:** OpenRouter (configurável via OPENROUTER_MODEL, default: openai/gpt-4o-mini)
- **Search:** SerpAPI
- **WhatsApp:** Z-API
- **CRM:** HubSpot
- **Observabilidade:** LangSmith

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Database
createdb sdr && alembic upgrade head

# Run
uvicorn src.api.main:app --reload

# Test
# Os testes NÃO são versionados (estão no .gitignore)
# Execute localmente: pytest tests/ -v

# Lint
ruff check src/
```

## Releases (SemVer via release-please)
- Branch `master` protegida: mudanças entram via issue → branch (`fix/#N`, `feat/#N`) → PR (`Closes #N`) → CI `quality` verde → squash merge.
- Commits: Conventional Commits (`fix:` patch, `feat:` minor, `!` major) — validados pelo hook `.githooks/commit-msg` (instalar: `sh scripts/install-hooks.sh`); `.githooks/pre-push` bloqueia push direto na master (bypass: `--no-verify`).
- `release-please` abre PR de release (changelog + versão). NUNCA edite a versão manualmente (fonte única: `pyproject.toml`); o PR de release é mergado manualmente (cadência humana).
- Versão servida em `GET /version` e no OpenAPI.

## Structure

```
src/
├── api/                  # FastAPI (config.py, routes.py, main.py)
├── agents/                # LangChain agents (individual files per agent)
│   ├── __init__.py        # Agent exports
│   ├── base.py           # BaseAgent parent class
│   ├── prompts.py        # System prompts
│   ├── schemas.py       # Input/Output schemas
│   ├── buscar_empresa.py
│   ├── buscar_linkedin.py
│   ├── classifica_lead.py
│   ├── gerar_diagnostico.py
│   ├── gerar_perguntas.py
│   ├── msg_fechamento.py
│   └── validar_resposta.py
├── graph/                # LangGraph (NewLeadGraph, MainChatGraph)
│   ├── __init__.py
│   ├── nodes.py         # Graph nodes
│   ├── states.py       # State definitions
│   ├── new_lead.py
│   └── main_chat.py
├── models/               # SQLAlchemy (6 tables)
├── schemas/              # Pydantic
└── services/           # (database.py, zapi.py, hubspot.py)
```

## 7 Agents Pipeline

| # | Agent | Trigger |
|---|-------|---------|
| 1 | ValidarResposta | Every lead message |
| 2 | GerarPerguntas | After valid response |
| 3 | BuscarEmpresa | posicao=0 |
| 4 | BuscarLinkedIn | posicao=0 |
| 5 | ClassificaLead | posicao >= MAX_PERGUNTAS |
| 6 | GerarDiagnostico | After ClassificaLead |
| 7 | MsgFechamento | After GerarDiagnostico |

## Env Variables Required
- `DATABASE_URL`
- `ZAPI_INSTANCE_ID`, `ZAPI_INSTANCE_TOKEN`, `ZAPI_SECURITY_TOKEN`
- `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` (default: https://openrouter.ai/api/v1), `OPENROUTER_MODEL` (default: openai/gpt-4o-mini)
- `SERPAPI_API_KEY`
- `HUBSPOT_ACCESS_TOKEN`, `HUBSPOT_OWNER_ID`
- `MAX_PERGUNTAS` (default: 6)
- `LOG_LEVEL`, `APP_ENV`
- `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` (default: SDR-Lead-Classification-Diagnosis)

## Key Files
- Base agent class: `src/agents/base.py`
- Prompt templates: `src/agents/prompts.py`
- Input/Output schemas: `src/agents/schemas.py`
- Graph nodes: `src/graph/nodes.py`

## 8 Agents (from src/agents/__init__.py)
1. ValidarRespostaAgent
2. GerarPerguntasAgent
3. BuscarEmpresaAgent
4. BuscarLinkedInAgent
5. ClassificaLeadAgent
6. GerarDiagnosticoAgent
7. MsgFechamentoAgent
8. BaseAgent (parent class)

## 9 Instruções de Revisão de códigos e arquivos do projeto
1. Ao final de qualquer alteração de código, SEMPRE rode os testes relacionados ao código alterado e corrija os problemas identificados nos testes
2. Ao final de qualquer alteração em qualquer arquivo, SEMPRE revise TODOS os arquivos ".MD" do projeto para verificar se necessitam ser atualizados e em caso positivo, atualize-os.
3. Antes de realizar qualquer alteração de código SEMPRE verifique se possui alguma Skill ou MCP relacionado ao tema e em caso positivo, utilize a(s) SKILLS e/ou MCP's disponíveis
4. SEMPRE crie uma branch nova para realizar qualquer alteração em qualquer arquivo do projeto
5. SEMPRE execute o lint e corrija os erros após qualquer alteração ou criação de código no projeto, SEMPRE corrija TODOS, mesmo que sejam pré-existentes e/ou de outra sessão
6. Ao encontrar erros na execução de testes SEMPRE corrija TODOS, mesmo que sejam pré-existentes e/ou de outra sessão
7. Ao criar novas fetatures, SEMPRE crie novos casos de testes para estas novas features, execute-os e corrija os erros encontrados
8. Ao realizar alterações/mudanças de código SEMPRE atualize e execute os testes relativos ao código alterado.
9. Após a realização merge de outras branchs com a branch MASTER, SEMPRE apague as outras branchs MANTENDO SOMENTE A BRANCH MASTER