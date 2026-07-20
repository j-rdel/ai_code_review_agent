# Registro de Prompts

Todo prompt do usuário é registrado aqui, na ordem cronológica.

---

## 001 — Setup inicial do Git

**Data:** 2026-07-20

**Prompt:**
> Faça o setup inicial do git com o repositorio https://github.com/j-rdel/ai_code_review_agent.git

### Implementação
- `git init` no diretório do projeto
- Branch renomeada de `master` para `main`
- Remote `origin` adicionado apontando para `https://github.com/j-rdel/ai_code_review_agent.git`
- Verificado que o remoto está vazio (sem refs)

### Commits
- _sem commits nesta etapa (apenas configuração local de git)_

---

## 002 — Proposta de arquitetura

**Data:** 2026-07-20

**Prompt:**
> Quero desenvolver um agente utilizando LangGraph. O objetivo é criar um AI Code Review Agent que analisa alterações em um projeto Python e gera um relatório técnico. Quero que a arquitetura siga boas práticas de LangGraph, separando claramente estado compartilhado, nós, ferramentas e fluxo. Antes de escrever qualquer código, proponha a arquitetura completa do projeto, incluindo estrutura de diretórios, responsabilidades de cada componente e o diagrama do fluxo e salve em `docs/architecture.md`.
>
> Stack e decisões técnicas:
>   - Python 3.12+
>   - Orquestração: LangGraph
>   - LLM: Ollama Qwen 3 8B** (`qwen3:8b`)
>   - Integração: `langchain-ollama` (`ChatOllama`)
>   - Structured output via `.with_structured_output(SchemaPydantic)`
>   - Considere usar `/no_think` no prompt para desativar o modo "thinking" do Qwen3 (evita chain-of-thought verboso que gasta tokens/tempo)
>   - Gerência de dependências: uv
>   - Relatório: Markdown, gravado em `reports/<repo>_<timestamp>.md`
>   - Escopo do review: arquivo inteiro (não só o diff)
>
> Convenções do projeto (obrigatórias):
>   - Registrar todo prompt em `/docs/prompts.md`. Cada entrada deve conter:
>     - O prompt na íntegra
>     - Data
>     - Seção Implementação (resumo do que foi entregue)
>     - Seção Commits (hash curto + subject)
>   - Mensagens de commit:
>     - Curtas, em inglês
>     - Prefixo convencional: `feat:`, `chore:`, `fix:`, `docs:`
>     - Nunca incluir `Co-Authored-By: Claude` nem qualquer assinatura de IA
>     - Exemplo: `chore: add prompts.md on /docs`
>   - Commits granulares por camada (models → tools → nodes → graph → cli) para o histórico contar a história.

### Implementação
- Criado `docs/architecture.md` com:
  - Objetivo e stack
  - Estrutura de diretórios completa (`src/ai_code_review_agent/{nodes,tools}`, `docs/`, `reports/`, `tests/`)
  - Descrição de cada componente: `state`, `models`, `tools`, `nodes`, `graph`, `llm`, `prompts`, `cli`, `config`
  - Diagrama Mermaid do fluxo com fan-out via `Send` API por arquivo e fan-in via reducer
  - Decisões técnicas justificadas (arquivo inteiro vs diff, structured output, `Send` vs loop, `/no_think`)
  - Roadmap de implementação em 8 commits granulares por camada
- Criado este `docs/prompts.md` com o histórico de prompts (001 e 002).

### Commits
- `b84c841` docs: add architecture, prompts registry and tasks roadmap

---

## 003 — Roadmap como tasks

**Data:** 2026-07-20

**Prompt:**
> Crie um tasks.md em /docs e adicione os commit propostos @docs/architecture.md forma de tarefa
>
> ## 8. Roadmap de implementação (ordem de commits)
>
> 1. `chore: bootstrap uv project` — `pyproject.toml`, deps (`langgraph`, `langchain-ollama`, `pydantic`, `typer`), `.gitignore`, `.python-version`.
> 2. `feat: add pydantic schemas for review output` — `models.py`.
> 3. `feat: add git and report tools` — `tools/git_tools.py`, `tools/report_writer.py`.
> 4. `feat: add graph state and llm factory` — `state.py`, `llm.py`, `config.py`, `prompts.py`.
> 5. `feat: add nodes` — `nodes/*.py`.
> 6. `feat: wire langgraph flow` — `graph.py`.
> 7. `feat: add typer cli` — `cli.py`.
> 8. `docs: add README with usage` — instruções finais.
>
> Após isso commite e de o push

### Implementação
- Criado `docs/tasks.md` desdobrando os 8 commits do roadmap em checklists acionáveis
- Cada task lista arquivos, funções e verificações esperadas para o commit correspondente
- Prompt registrado aqui em `docs/prompts.md`
- Commit e push da estrutura inicial de docs

### Commits
- `b84c841` docs: add architecture, prompts registry and tasks roadmap
- `343d414` docs: backfill commit hashes in prompts registry

---

## 004 — Implementar T1 (bootstrap uv)

**Data:** 2026-07-20

**Prompt:**
> Implemente T1 de @docs/tasks.md

### Implementação
- `uv init --package --name ai-code-review-agent --python 3.12` (gerou `pyproject.toml`, `.python-version`, `src/ai_code_review_agent/`, `README.md`)
- Adicionadas deps de runtime: `langgraph`, `langchain-ollama`, `pydantic`, `typer`
- Adicionadas deps de dev: `pytest`, `pytest-mock` (via `uv add --dev`)
- Ajustado `pyproject.toml`: descrição real do projeto e entrypoint `review = "ai_code_review_agent.cli:app"` (módulo será criado em T7)
- `src/ai_code_review_agent/__init__.py` reduzido a `__version__` (removido `main()` placeholder do `uv init`)
- Criado `.gitignore` (Python, `.venv`, caches, `reports/`)
- `.python-version` = `3.12` (gerado pelo `uv init`)
- `uv sync` executado; `uv.lock` gerado; smoke-test de imports OK
- T1 marcada como `[x]` em `docs/tasks.md`

### Commits
- `ee3e7c4` chore: bootstrap uv project
- `538198a` docs: mark T1 done and register prompt 004

---

## 005 — Implementar T2 (schemas Pydantic)

**Data:** 2026-07-20

**Prompt:**
> implemente T2

### Implementação
- Criado `src/ai_code_review_agent/models.py` com:
  - Aliases `IssueCategory` e `Severity` como `Literal` (dão enum claro no JSON schema para structured output)
  - `Issue` — `category`, `severity`, `line` (opcional, `ge=1`), `description`, `suggestion`; todos os campos com `Field(description=...)` para orientar o LLM
  - `FileReview` — `file_path`, `overall_score` (`ge=0, le=10`), `summary`, `issues`, `strengths`
  - `SeverityCounts` — sub-modelo com contadores `low/medium/high/critical` (não-negativos)
  - `RepoSummary` — `overall_assessment`, `total_issues_by_severity: SeverityCounts`, `top_priorities`, `recommendations`
- Criado `tests/__init__.py` e `tests/test_models.py` cobrindo:
  - `Issue`: validação de category/severity, `line` opcional e positivo
  - `FileReview`: defaults de lista, limites de score
  - `SeverityCounts`: defaults e rejeição de negativos
  - `RepoSummary`: defaults e campos populados
- `uv run pytest -v` → 13/13 verde
- T2 marcada como `[x]` em `docs/tasks.md`

### Commits
- `9501bf1` feat: add pydantic schemas for review output
- _hash do commit de docs preenchido no próximo commit_

---
