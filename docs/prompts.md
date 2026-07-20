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
- _a preencher após commit_

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
- _a preencher após commit_

---
