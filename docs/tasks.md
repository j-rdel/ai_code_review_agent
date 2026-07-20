# Tasks — Roadmap de Implementação

Cada task equivale a um commit granular por camada, conforme convenção do projeto.
Marque como concluída (`[x]`) após o commit correspondente.

Fonte: [architecture.md § 8](./architecture.md#8-roadmap-de-implementação-ordem-de-commits).

---

## T1 — `chore: bootstrap uv project`
- [ ] Inicializar projeto com `uv init`
- [ ] Configurar `pyproject.toml` (nome, Python 3.12+, entrypoint `review`)
- [ ] Adicionar dependências: `langgraph`, `langchain-ollama`, `pydantic`, `typer`
- [ ] Adicionar dev deps: `pytest`, `pytest-mock`
- [ ] Criar `.gitignore` (Python, `reports/`, `.venv`, caches)
- [ ] Criar `.python-version`
- [ ] Rodar `uv sync` e verificar `uv.lock`

## T2 — `feat: add pydantic schemas for review output`
- [ ] Criar `src/ai_code_review_agent/models.py`
- [ ] Definir `Issue` (category, severity, line?, description, suggestion)
- [ ] Definir `FileReview` (file_path, overall_score, summary, issues, strengths)
- [ ] Definir `RepoSummary` (overall_assessment, total_issues_by_severity, top_priorities, recommendations)
- [ ] Adicionar `tests/test_models.py` cobrindo validações essenciais

## T3 — `feat: add git and report tools`
- [ ] Criar `src/ai_code_review_agent/tools/__init__.py`
- [ ] `tools/git_tools.py`:
  - [ ] `list_changed_python_files(repo_path, base_ref, head_ref)`
  - [ ] `read_file_at_ref(repo_path, path, ref)`
  - [ ] `get_repo_name(repo_path)`
- [ ] `tools/report_writer.py`:
  - [ ] `render_markdown(state)`
  - [ ] `write_report(markdown, repo_name, out_dir)`
- [ ] `tests/test_git_tools.py` e `tests/test_report_writer.py`

## T4 — `feat: add graph state and llm factory`
- [ ] `src/ai_code_review_agent/config.py` — settings (modelo, host Ollama, defaults)
- [ ] `src/ai_code_review_agent/state.py` — `GraphState` (TypedDict + reducers)
- [ ] `src/ai_code_review_agent/llm.py` — factory `get_llm()` com `ChatOllama`
- [ ] `src/ai_code_review_agent/prompts.py` — templates com prefixo `/no_think`
  - [ ] `FILE_REVIEW_PROMPT`
  - [ ] `AGGREGATE_PROMPT`

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
