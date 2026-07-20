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
- `e9039cf` docs: mark T2 done and register prompt 005

---

## 006 — Implementar T3 (git tools e report writer)

**Data:** 2026-07-20

**Prompt:**
> implemente T3

### Implementação
- Criado `src/ai_code_review_agent/tools/__init__.py`
- Criado `src/ai_code_review_agent/tools/git_tools.py`:
  - Helper interno `_run_git()` que encapsula `subprocess.run` (sem shell, sem escaping)
  - `list_changed_python_files()` usa `git diff --name-only --diff-filter=ACMRT base..head -- '*.py'` (exclui deleções)
  - `read_file_at_ref()` usa `git show ref:path`
  - `get_repo_name()` tenta `remote.origin.url` (strip `.git`, aceita HTTPS/SSH), fallback para nome do diretório
- Criado `src/ai_code_review_agent/tools/report_writer.py`:
  - `render_markdown(*, repo_name, base_ref, head_ref, file_reviews, repo_summary)` — assinatura com kwargs explícitos (desvio consciente do `state: GraphState` na arquitetura) para permitir teste isolado sem depender de T4
  - Seções renderizadas: header com metadados, Overall Assessment, tabela de severidade, Top priorities, Recommendations, per-file review (score, summary, issues formatados como `[SEVERITY] (category, line N)`, strengths). Seções opcionais são omitidas se vazias.
  - `write_report()` cria `out_dir` se preciso, grava `<repo>_<YYYYMMDD-HHMMSS>.md`, retorna path absoluto
- Testes:
  - `tests/test_git_tools.py` — usa `tmp_path` para criar repositórios git reais (init/config/commits) e valida os 3 helpers, incluindo exclusão de deleções, leitura de versões históricas e todas as formas de remote URL
  - `tests/test_report_writer.py` — valida seções renderizadas, formatação de severidade, omissão de seções vazias e escrita/criação de diretório
- `uv run pytest -v` → **30/30 verde**

### Commits
- `b724753` feat: add git and report tools
- `0c48da0` docs: mark T3 done and register prompt 006

---

## 007 — Implementar T4 (state, config, llm, prompts)

**Data:** 2026-07-20

**Prompt:**
> implemente t4

### Implementação
- `config.py`: `Settings` (dataclass frozen) com defaults do arquitetura (`qwen3:8b`, `http://localhost:11434`, temp `0.2`, refs default e output dir); `load_settings()` lê `OLLAMA_MODEL`/`OLLAMA_HOST`/`OLLAMA_TEMPERATURE` do ambiente; instância `settings` de módulo.
- `state.py`: `GraphState(TypedDict, total=False)` com todos os campos da arquitetura + `repo_name` (usado por `generate_report`); `file_reviews` anotado com `Annotated[list[FileReview], operator.add]` para fan-in seguro dos `Send`s paralelos.
- `llm.py`: `get_llm(temperature=None)` retorna `ChatOllama` configurado a partir de `settings`; `temperature` argumento sobrepõe o default.
- `prompts.py`: `FILE_REVIEW_PROMPT` e `AGGREGATE_PROMPT` como `ChatPromptTemplate` (system + human). Ambos os systems começam com `/no_think` para desligar CoT do Qwen3.
- Testes:
  - `test_config.py`: defaults e override via env
  - `test_state.py`: `total=False`, chaves esperadas, e — mais importante — smoke real com `StateGraph` compilado que fanea dois nós e confirma que o reducer concatena `file_reviews`
  - `test_llm.py`: `ChatOllama` instanciado com model/host/temperature corretos (settings mockado via `monkeypatch.setattr`)
  - `test_prompts.py`: presença de `/no_think`, formatação de placeholders (`file_path`/`content`/`reviews_json`), tipos das mensagens
- `uv run pytest -v` → **46/46 verde**

### Commits
- `dbb057a` feat: add graph state and llm factory
- `acd843b` docs: mark T4 done and register prompt 007

---

## 008 — Implementar T5 (nós do grafo)

**Data:** 2026-07-20

**Prompt:**
> implemente t5

### Implementação
- Criados os 5 nós em `src/ai_code_review_agent/nodes/`:
  - `detect_changes` — chama `list_changed_python_files` + `get_repo_name`; devolve `{changed_files, repo_name}`
  - `load_files` — mapeia `read_file_at_ref` sobre `changed_files`; devolve `{file_contents}`
  - `review_file` — worker do fan-out. Recebe `{"file_path", "content"}` (o `Send` de T6 injeta). Constrói `structured = get_llm().with_structured_output(FileReview)`, formata `FILE_REVIEW_PROMPT` e invoca. **Força `review.file_path = file_path`** para bloquear alucinação do modelo. Devolve `{"file_reviews": [review]}` — merge no state via reducer `operator.add`.
  - `aggregate_summary` — serializa `file_reviews` para JSON e envia via `AGGREGATE_PROMPT` para `RepoSummary`
  - `generate_report` — chama `render_markdown` + `write_report`; lê `state["output_dir"]` com fallback para `settings.default_output_dir`
- **Ajuste em `state.py`** (T4 touchup): adicionado `output_dir: str` como input opcional para o CLI (T7) injetar por invocação, mantendo consistência com o padrão dos outros inputs
- **`nodes/__init__.py` intencionalmente vazio**: uma primeira versão fazia `from ai_code_review_agent.nodes.review_file import review_file`, mas isso reatribui o atributo `review_file` do pacote (que apontava para o submódulo) para a função, quebrando `import ai_code_review_agent.nodes.review_file as module` (o CPython usa `IMPORT_FROM` que resolve pelo atributo). Solução: sem re-exports; consumidores importam do submódulo diretamente
- Testes em `tests/test_nodes.py`:
  - `detect_changes` e `load_files` — usam repositórios git reais em `tmp_path` (sem mock)
  - `review_file` — mocka `get_llm()` retornando `MagicMock` cujo `.with_structured_output(FileReview).invoke(...)` retorna um `FileReview`; valida (1) que schema correto é solicitado, (2) que `file_path` é sobrescrito mesmo quando o LLM devolve outro nome, (3) que as mensagens formatadas contêm `file_path` e `content`
  - `aggregate_summary` — mocka LLM; valida que `RepoSummary` é o schema pedido e que a human message carrega JSON parseável dos reviews
  - `generate_report` — sem LLM; escreve no `tmp_path` e valida saída + fallback para settings
- `uv run pytest -v` → **55/55 verde**

### Commits
- `f4fba63` feat: add nodes
- `9483cb2` docs: mark T5 done and register prompt 008

---

## 009 — Implementar T6, T7 e T8 (graph, CLI, README)

**Data:** 2026-07-20

**Prompt:**
> implemente t6, t7 e t8

### Implementação

**T6 — `graph.py`:**
- `route_files(state)` como conditional edge: retorna `list[Send]` (um por arquivo) OU string `"aggregate_summary"` quando não há arquivos (curto-circuito p/ evitar deadlock em `add_conditional_edges` com lista vazia).
- `build_graph()` monta o `StateGraph` com edges: `START → detect_changes → load_files → (fan-out) → review_file → aggregate_summary → generate_report → END`. `add_conditional_edges("load_files", route_files, ["review_file", "aggregate_summary"])` declara ambos destinos.
- Ajuste secundário em `aggregate_summary.py`: `state.get("file_reviews") or []` (tolera caminho sem arquivos, onde `file_reviews` nunca é preenchido).
- Migrado `from langgraph.constants import Send` → `from langgraph.types import Send` (V1 depreca o primeiro).
- `tests/test_graph.py`: (1) `route_files` unit tests, (2) end-to-end com git real + LLMs mockados (fanout de 2 arquivos, checa reducer), (3) end-to-end sem alterações Python (checa curto-circuito).

**T7 — `cli.py`:**
- Typer app com `@app.callback(invoke_without_command=True)` — permite `review --repo . ...` sem exigir subcomando.
- Opções: `--repo`/`-r` (default `.`), `--base`/`-b`, `--head`/`-H`, `--out`/`-o` — defaults dos options vêm de `settings`. `--repo` valida existência de diretório via `exists=True, file_okay=False`.
- Entrypoint `review = "ai_code_review_agent.cli:app"` já registrado em T1.
- Imprime `Reviewing X — base..head`, `Reviewed N file(s).`, `Report written: <path>`.
- `tests/test_cli.py`: (1) `--help` lista todas as opções, (2) execução real via `CliRunner` com LLMs mockados, valida exit code, mensagens e arquivo gerado.
- Validado manualmente: `uv run review --help` funciona.
- Não executado com Ollama real (não disponível neste ambiente); wiring validado pelos testes.

**T8 — `README.md`:**
- Descrição, requisitos (Python 3.12+, Ollama + `qwen3:8b`), tabela de env vars, instalação (`uv sync`), uso (`uv run review ...`), tabela de opções, explicação passo-a-passo do fluxo, exemplo de relatório em Markdown, seção Development (`uv run pytest`), links para `docs/architecture.md`, `docs/prompts.md`, `docs/tasks.md`.

- `uv run pytest -v` → **61/61 verde** (55 anteriores + 4 de graph + 2 de cli)

### Commits
- _a preencher após commit_

---
