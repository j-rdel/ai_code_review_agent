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

## T5 — `feat: add nodes` ✅
- [x] `nodes/__init__.py` (vazio — evita colisão entre nome de submódulo e função re-exportada)
- [x] `nodes/detect_changes.py` — usa `git_tools.list_changed_python_files` + `get_repo_name`
- [x] `nodes/load_files.py` — usa `git_tools.read_file_at_ref`
- [x] `nodes/review_file.py` — LLM + `.with_structured_output(FileReview)`, força `file_path` correto (anti-hallucination)
- [x] `nodes/aggregate_summary.py` — LLM + `.with_structured_output(RepoSummary)`
- [x] `nodes/generate_report.py` — usa `report_writer`, lê `output_dir` do state com fallback para `settings.default_output_dir`
- [x] `tests/test_nodes.py` cobrindo os 5 nós (git real nos determinísticos, LLM mockado nos LLM)
- Ajuste em `state.py`: adicionado campo opcional `output_dir` (input do CLI em T7)

## T6 — `feat: wire langgraph flow` ✅
- [x] `src/ai_code_review_agent/graph.py`
- [x] `build_graph() -> CompiledGraph`
- [x] Fan-out por arquivo via `Send` API (`route_files`)
- [x] Fan-in automático via reducer `operator.add` em `file_reviews`
- [x] Curto-circuito: se `file_contents` vazio, `route_files` retorna `"aggregate_summary"` (sem review)
- [x] `tests/test_graph.py` — smoke test end-to-end + caminho sem alterações

## T7 — `feat: add typer cli` ✅
- [x] `src/ai_code_review_agent/cli.py`
- [x] Opções: `--repo`, `--base`, `--head`, `--out`
- [x] Entrypoint `review` já registrado em `pyproject.toml` (T1)
- [x] Validado `uv run review --help`; teste `test_cli.py` executa a CLI fim-a-fim com LLM mockado

## T8 — `docs: add README with usage` ✅
- [x] Criar `README.md` com:
  - [x] Descrição do projeto
  - [x] Requisitos (Python 3.12+, Ollama com `qwen3:8b`)
  - [x] Instalação (`uv sync`)
  - [x] Uso (`uv run review --repo . --base main --head HEAD`)
  - [x] Exemplo de relatório
  - [x] Link para `docs/architecture.md`
