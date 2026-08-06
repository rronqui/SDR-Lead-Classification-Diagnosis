# PRD - Sistema SDR: Lead Classification & Diagnosis

## 1. Visão Geral do Projeto

**Nome:** SDR Lead Classification & Diagnosis System  
**Tipo:** Backend API + Agentes IA  
**Resumo:** Sistema automatizado de classificação e diagnóstico de leads B2B via WhatsApp, integrando múltiplos agentes de IA para qualificação, pesquisa e geração de relatórios técnicos.  
**Público-alvo:** Equipes de Vendas B2B que utilizam WhatsApp como canal principal de comunicação.

---

## 2. Escopo do Projeto

### 2.1 Escopo Incluído
- API REST para integração com Z-API (WhatsApp)
- Sistema de 7 agentes LangChain para automação de vendas
- Orquestração via LangGraph (NewLeadGraph + MainChatGraph)
- Observabilidade e tracing via LangSmith
- Integração com SerpAPI para pesquisa de empresas
- Integração com HubSpot CRM
- Banco de dados PostgreSQL com 6 tabelas
- Migration Alembic

### 2.2 Escopo Excluído
- Frontend/Web interface (futuro)
- Tabela `parametros` (configurações via .env)
- Histórico de mensagens em detalhe (simplificado)

---

## 3. Funcionalidades Principais

### 3.1 Fluxo New Lead
1. Recebe webhook de novo lead (Z-API)
2. Cria registro em `lead` com status "novo"
3. Executa pesquisa de empresa (SerpAPI)
4. Executa validação LinkedIn
5. Envia mensagem de boas-vindas com botão "SIM"
6. Armazena interação inicial

### 3.2 Fluxo Main Chat
1. Recebe resposta do lead
2. Valida pertinência da resposta (ValidarResposta)
3. Gera próxima pergunta de qualificação (GerarPerguntas)
4. Repete até MAX_PERGUNTAS (Qtd. Máxima de perguntas configurada em .env)
5. Classifica lead (ClassificaLead)
6. Gera diagnóstico técnico (GerarDiagnostico)
7. Cria mensagem de fechamento (MsgFechamento)
8. Envia para HubSpot (criar/atualizar contact + deal)
9. Envia mensagem final via WhatsApp

### 3.3 Agentes LangChain
| # | Agente | Função |
|---|--------|-------|
| 1 | ValidarResposta | Valida se resposta é pertinente |
| 2 | GerarPerguntas | Gera próxima pergunta de qualificação |
| 3 | BuscarEmpresa | Pesquisa dados da empresa |
| 4 | BuscarLinkedIn | Valida perfil LinkedIn do lead (com pesquisa SerpAPI) |
| 5 | ClassificaLead | Classifica lead A/B/C + score |
| 6 | GerarDiagnostico | Gera relatório técnico |
| 7 | MsgFechamento | Cria mensagem de fechamento |

> **Nota:** Todas as execuções de agentes são rastreadas via **LangSmith** para debugging, análise de performance e otimização de prompts.

---

## 4. Requisitos Funcionais

### RF-001: Recebimento de Novos Leads
- Sistema deve receber webhook de novo lead contendo número WhatsApp e nome
- Deve criar registro em banco de dados
- Deve iniciar fluxo de qualificação automaticamente

### RF-002: Pesquisa de Empresas
- Sistema deve buscar dados da empresa via SerpAPI usando nome + domínio
- Deve extrair: setor, tamanho, descrição, informações relevantes
- Deve armazenar em `info_internet_empresa`

### RF-003: Validação LinkedIn
- Sistema deve buscar perfil LinkedIn do lead usando nome + cargo + empresa
- Deve validar se informações conferem
- Deve armazenar URL e status em `info_internet_contato`

### RF-004: Qualificação de Leads
- Sistema deve conducir entrevista com até 6 perguntas
- Cada pergunta deve ter objetivo e indicador jelas
- Históricos deve ser armazenado em `perguntas_diagnostico`

### RF-005: Validação de Respostas
- Sistema deve validar se resposta é semanticamente pertinente
- Deve permitir reenvio de pergunta se inválida
- Deve analisar tom e adequação

### RF-006: Classificação de Leads
- Sistema deve classificar leads em A (hot), B (warm), C (cold)
- Deve calcular score de 0-100
- Deve armazenar classificação em `lead`

### RF-007: Geração de Diagnóstico
- Sistema deve gerar relatório técnico em Markdown
- Deve incluir: Panorama, Dores, Solução, Validação BANT
- Deve armazenar em `diagnostico`

### RF-008: Integração HubSpot
- Sistema deve criar/atualizar contato no HubSpot
- Deve criar deal opportunity asociado
- Deve enviar propriedades personalizadas

### RF-009: Envio de Mensagens WhatsApp
- Sistema deve enviar mensagens via Z-API
- Deve suportar texto e botões
- Deve trackingar em `interacoes_chatboot`

---

## 5. Requisitos Não-Funcionais

### RNF-001: Latência
- Resposta de webhook deve ser < 500ms
- Pesquisa SerpAPI deve completar em < 10s
- Geração de diagnóstico deve completar em < 15s

### RNF-002: Disponibilidade
- API deve estar disponível 99.5% do tempo
- Fallback para erros de API externo

### RNF-003: Segurança
- Todas as chaves de API em variáveis de ambiente
- Validação de input em todos os endpoints
- Rate limiting implementado

### RNF-004: Monitoramento
- Logs estruturados em formato JSON
- Métricas de utilização de agentes
- Rastreamento de erros com stack trace
- Observabilidade via LangSmith (tracing de LLMs e LangGraph)

---

## 6. Stack Tecnológico

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Framework API | FastAPI | 0.115.x |
| ORM | SQLAlchemy | 2.0.x |
| Database | PostgreSQL | 16.x |
| Migrations | Alembic | 1.13.x |
| Agentes IA | LangChain | 0.3.x |
| Orquestração | LangGraph | 0.2.x |
| LLM Client | LangChain OpenRouter | - |
| Web Search | SerpAPI | - |
| CRM | HubSpot | - |
| WhatsApp | Z-API | - |
| Validacao | Pydantic | 2.10.x |
| Observabilidade | LangSmith | - |

---

## 7. Arquitetura do Sistema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Z-API      │───▶|  FastAPI    │────▶│  LangGraph  │
│  (Webhook)  │     │  (Router)   │     │Orchestration│
└─────────────┘     └─────────────┘     └─────┬───────┘
                                               │
           ┌─────────────┬─────────────┬───────┴───────┬─────────────┐
           ▼             ▼             ▼               ▼             ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
     │Validar   │ │Gerar     │ │Buscar    │ │Buscar    │ │Classifica│ │Gerar     │ │Msg       │
     │Resposta  │ │Perguntas │ │Empresa   │ │LinkedIn  │ │Lead      │ │Diagnost. │ │Fechamento│
     └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
           │             │             │               │             │             │
           └─────────────┴─────────────┴───────────────┴─────────────┴─────────────┘
                                           │
                           ┌───────────────┼───────────────┐
                           ▼               ▼               ▼
                     ┌──────────┐   ┌──────────┐    ┌──────────┐
                     │PostgreSQL│   │ HubSpot  │    │  Z-API   │
                     └──────────┘   └──────────┘    └──────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      LangSmith (Observabilidade)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Tracing  │  │ Debug    │  │ Métricas │  │ Avaliação│         │
│  │ Agentes  │  │ Prompts  │  │ Tokens   │  │ Chains   │         │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│  Coleta traces de todos os agentes + LangGraph                  │
│  Dashboard: https://smith.langchain.com/                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Modelo de Dados

### 8.1 Tabela: lead
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| numero_whatsapp | VARCHAR(20) | Telepone com DDI |
| nome | VARCHAR(255) | Nome do lead |
| email | VARCHAR(255) | Email (opcional) |
| empresa | VARCHAR(255) | Nome da empresa |
| dominio_empresa | VARCHAR(255) | Domínio web |
| cargo | VARCHAR(100) | Cargo do lead |
| classificacao | VARCHAR(20) | A, B ou C |
| score | INTEGER | 0-100 |
| status | VARCHAR(20) | novo, em_progresso, classificado |
| posicao_pergunta | INTEGER | 0-6 |
| created_at | TIMESTAMP | Data criação |
| updated_at | TIMESTAMP | Data atualização |

### 8.2 Tabela: perguntas_diagnostico
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| lead_id | UUID | FK lead |
| posicao | INTEGER | 0-6 |
| pergunta | TEXT | Texto da pergunta |
| objetivo | TEXT | O que busca descobrir |
| indicador | TEXT | Métrica/indicador |
| resposta | TEXT | Resposta do lead |
| validada | BOOLEAN | Se resposta foi validada |
| created_at | TIMESTAMP | Data criação |

### 8.3 Tabela: diagnostico
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| lead_id | UUID | FK lead |
| markdown | TEXT | Relatório completo |
| created_at | TIMESTAMP | Data criação |

### 8.4 Tabela: interacoes_chatboot
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| lead_id | UUID | FK lead |
| tipo | VARCHAR(20) | entrada, saida |
| mensagem | TEXT | Conteúdo |
| posicao | INTEGER | Posição no fluxo |
| created_at | TIMESTAMP | Data criação |

### 8.5 Tabela: info_internet_empresa
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| lead_id | UUID | FK lead |
| razao_social | VARCHAR(255) | Razão social |
| nome_fantasia | VARCHAR(255) | Nome fantasia |
| setor | VARCHAR(100) | Setor de atuação |
| tamanho | VARCHAR(50) | Porte |
| descricao | TEXT | Descrição |
| fonte | VARCHAR(50) | Fonte (serpapi, manual) |
| dados_json | JSONB | Dados raw |
| created_at | TIMESTAMP | Data criação |

### 8.6 Tabela: info_internet_contato
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | PK |
| lead_id | UUID | FK lead |
| linkedin_url | VARCHAR(500) | URL LinkedIn |
| cargo_confirmado | BOOLEAN | Se cargo confere |
| empresa_confirmada | BOOLEAN | Se empresa confere |
| status_validacao | VARCHAR(20) | validado, pendente, invalido |
| dados_json | JSONB | Dados raw |
| created_at | TIMESTAMP | Data criação |

---

## 9. Integrações

### 9.1 Z-API (WhatsApp)
- Endpoint: `POST /send-message`
- Autenticação: Instance Token + Authorization
- Recursos: Texto, botões, templates

### 9.2 OpenRouter (LLM)
- Provider: `openai/gpt-4o-mini`
- Temperatura: 0.2
- Tamanho: 350-3500 tokens (variável por agente)

### 9.3 SerpAPI (Web Search)
- Busca por nome + domínio da empresa
- Retorna: setor, descrição, notícias

### 9.4 HubSpot (CRM)
- Criar/atualizar contact
- Criar deal opportunity
- Enviar propriedades personalizadas

### 9.5 LangSmith (Observabilidade)
- **Rastreamento:** Todas as execuções de agentes LangChain e chains do LangGraph
- **Visualização:** Dashboard com traces, chains, nós e execuções
- **Debugging:** Análise de prompts, respostas, tokens e latência
- **Projeto:** `SDR-Lead-Classification-Diagnosis` (configurável via `LANGCHAIN_PROJECT`)
- **Configuração:**
  - `LANGCHAIN_API_KEY`: Chave da API LangSmith
  - `LANGCHAIN_TRACING_V2=true`: Ativa tracing v2
  - `LANGCHAIN_PROJECT`: Nome do projeto para agrupar traces
- **Dashboard:** https://smith.langchain.com/

---

## 10. API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /webhooks/zapi | Recebe eventos Z-API |
| POST | /leads | Cria novo lead manualmente |
| GET | /leads/{id} | Retorna lead com diagnóstico |
| GET | /leads | Lista leads com filtros |

---

## 11. Variáveis de Ambiente

```env
# Database
DATABASE_URL=

# Z-API
ZAPI_INSTANCE_ID=
ZAPI_INSTANCE_TOKEN=
ZAPI_SECURITY_TOKEN=

# OpenRouter
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini

# SerpAPI
SERPAPI_API_KEY=

# HubSpot
HUBSPOT_ACCESS_TOKEN=
HUBSPOT_OWNER_ID=

# App
APP_ENV=dev
LOG_LEVEL=INFO
MAX_PERGUNTAS=6

# LangSmith (Observabilidade)
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=SDR-Lead-Classification-Diagnosis
```

---

## 12. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| Taxa de classificação | > 80% dos leads |
| Classificações categoria A | > 20% |
| Latência média diagnóstico | < 15s |
| Taxa de traces LangSmith | 100% das execuções de agentes |
| Latência média agentes | < 5s |
| Disponibilidade API | 99.5% |

---

## 13. Riscos e Mitigações

| Risco | Mitigação |
|-------|----------|
| LLM fora do ar | Retry com exponential backoff |
| API Z-API lenta | Timeout de 30s + fila async |
| Dados HubSpot inválidos | Validação antes de envio |
| Rate limit APIs externas | Circuit breaker pattern |
| Falha em agente IA | Debug via LangSmith + retry automático |