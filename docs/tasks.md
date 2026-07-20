# Tasks — Roadmap de Implementação

Cada task equivale a um commit granular por camada, conforme convenção do projeto.
Marque como concluída (`[x]`) após o commit correspondente.

Fonte: [architecture.md § 8](./architecture.md#8-roadmap-de-implementação-ordem-de-commits).

---

## T1 — `chore: bootstrap uv project` ✅
- [x] Inicializar projeto com `uv init`
- [x] Configurar `pyproject.toml` (nome, Python 3.12+, entrypoint `review`)
- [x] Adicionar dependências: `langgraph`, `langchain-ollama`, `pydantic`, `typer`
- [x] Adicionar dev deps: `pytest`, `pytest-mock`
- [x] Criar `.gitignore` (Python, `reports/`, `.venv`, caches)
- [x] Criar `.python-version`
- [x] Rodar `uv sync` e verificar `uv.lock`

## T2 — `feat: add pydantic schemas for review output` ✅
- [x] Criar `src/ai_code_review_agent/models.py`
- [x] Definir `Issue` (category, severity, line?, description, suggestion)
- [x] Definir `FileReview` (file_path, overall_score, summary, issues, strengths)
- [x] Definir `RepoSummary` (overall_assessment, total_issues_by_severity, top_priorities, recommendations)
- [x] Adicionar `tests/test_models.py` cobrindo validações essenciais

## T3 — `feat: add git and report tools` ✅
- [x] Criar `src/ai_code_review_agent/tools/__init__.py`
- [x] `tools/git_tools.py`:
  - [x] `list_changed_python_files(repo_path, base_ref, head_ref)`
  - [x] `read_file_at_ref(repo_path, path, ref)`
  - [x] `get_repo_name(repo_path)`
- [x] `tools/report_writer.py`:
  - [x] `render_markdown(...)` — assinatura com kwargs explícitos (`repo_name`, `base_ref`, `head_ref`, `file_reviews`, `repo_summary`) em vez de `GraphState` para permitir teste isolado; o nó `generate_report` (T5) faz o destructuring
  - [x] `write_report(markdown, repo_name, out_dir)`
- [x] `tests/test_git_tools.py` e `tests/test_report_writer.py`

## T4 — `feat: add graph state and llm factory` ✅
- [x] `src/ai_code_review_agent/config.py` — settings (modelo, host Ollama, defaults)
- [x] `src/ai_code_review_agent/state.py` — `GraphState` (TypedDict + reducers)
- [x] `src/ai_code_review_agent/llm.py` — factory `get_llm()` com `ChatOllama`
- [x] `src/ai_code_review_agent/prompts.py` — templates com prefixo `/no_think`
  - [x] `FILE_REVIEW_PROMPT`
  - [x] `AGGREGATE_PROMPT`

## T5 — `feat: add nodes`
- [ ] `nodes/__init__.py`
- [ ] `nodes/detect_changes.py` — usa `git_tools.list_changed_python_files`
- [ ] `nodes/load_files.py` — usa `git_tools.read_file_at_ref`
- [ ] `nodes/review_file.py` — LLM + `.with_structured_output(FileReview)`
- [ ] `nodes/aggregate_summary.py` — LLM + `.with_structured_output(RepoSummary)`
- [ ] `nodes/generate_report.py` — usa `report_writer`
- [ ] `tests/test_nodes.py` com LLM mockado

## T6 — `feat: wire langgraph flow`
- [ ] `src/ai_code_review_agent/graph.py`
- [ ] `build_graph() -> CompiledGraph`
- [ ] Fan-out por arquivo via `Send` API (`route_files`)
- [ ] Fan-in automático via reducer `operator.add` em `file_reviews`
- [ ] `tests/test_graph.py` — smoke test end-to-end com LLM mockado

## T7 — `feat: add typer cli`
- [ ] `src/ai_code_review_agent/cli.py`
- [ ] Opções: `--repo`, `--base`, `--head`, `--out`
- [ ] Registrar entrypoint `review` no `pyproject.toml`
- [ ] Executar `uv run review` de ponta a ponta em um repo real

## T8 — `docs: add README with usage`
- [ ] Criar `README.md` com:
  - [ ] Descrição do projeto
  - [ ] Requisitos (Python 3.12+, Ollama com `qwen3:8b`)
  - [ ] Instalação (`uv sync`)
  - [ ] Uso (`uv run review --repo . --base main --head HEAD`)
  - [ ] Exemplo de relatório
  - [ ] Link para `docs/architecture.md`
