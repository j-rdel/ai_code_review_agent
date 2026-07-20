# AI Code Review Agent

LangGraph-based agent that reviews Python code changes between two git refs
and produces a Markdown report. Runs entirely locally via Ollama — no API
key, no data leaves the machine.

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) running locally, with the `qwen3:8b` model
  pulled:

  ```sh
  ollama pull qwen3:8b
  ```

  Optional environment overrides:

  | Variable             | Default                  |
  | -------------------- | ------------------------ |
  | `OLLAMA_MODEL`       | `qwen3:8b`               |
  | `OLLAMA_HOST`        | `http://localhost:11434` |
  | `OLLAMA_TEMPERATURE` | `0.2`                    |

## Installation

```sh
uv sync
```

## Usage

```sh
uv run review --repo . --base main --head HEAD --out ./reports
```

Options:

| Option         | Default   | Description                                     |
| -------------- | --------- | ----------------------------------------------- |
| `--repo`, `-r` | `.`       | Path to the git repository to review.           |
| `--base`, `-b` | `main`    | Base git ref to diff from.                      |
| `--head`, `-H` | `HEAD`    | Head git ref to diff to.                        |
| `--out`, `-o`  | `reports` | Directory where the Markdown report is written. |

The report file name is `<repo>_<YYYYMMDD-HHMMSS>.md`.

## What it does

1. **detect_changes** — runs `git diff --name-only base..head` and keeps
   only `.py` files (deletions excluded).
2. **load_files** — reads the full content of each changed file at `head`
   (scope: whole file, not just the diff).
3. **review_file** — fanned out one-per-file via LangGraph's `Send` API;
   asks the LLM for a `FileReview` via structured output.
4. **aggregate_summary** — synthesizes all `FileReview`s into a single
   `RepoSummary`.
5. **generate_report** — renders Markdown and writes it to `--out`.

Prompts are prefixed with `/no_think` to disable Qwen3's chain-of-thought.

## Example output (excerpt)

```markdown
# AI Code Review — myrepo

**Generated:** 2026-07-20T10:15:32
**Base:** `main` → **Head:** `HEAD`
**Files reviewed:** 3

---

## Overall Assessment

Solid change set; a couple of high-severity bugs to address before merging.

### Issues by severity

| Critical | High | Medium | Low |
| -------- | ---- | ------ | --- |
| 0        | 2    | 5      | 3   |

### Top priorities

- Fix off-by-one in `pipeline.chunk()` (data loss on the last batch).
- Escape user input in `search.query()` before interpolation.

---

## Per-file reviews

### `src/pipeline.py` — score **6.5/10**

Chunking logic is clear but drops the tail when `len % size != 0`.

**Issues (2):**

- **[HIGH]** _(bug, line 47)_ Off-by-one drops the last chunk.
  _Suggestion:_ Use `range(0, len(items), size)` and slice inclusively.
- **[LOW]** _(style, line 12)_ Missing type hint on `chunk()`.
  _Suggestion:_ Annotate as `list[list[T]]`.
```

## Development

Run the test suite:

```sh
uv run pytest
```

## Architecture

See [`docs/architecture.md`](./docs/architecture.md) for the full design:
directory layout, per-component responsibilities, and the LangGraph flow
diagram.

## Project conventions

- Every user prompt is registered in [`docs/prompts.md`](./docs/prompts.md).
- Commit messages: short, English, conventional prefix (`feat:`, `chore:`,
  `fix:`, `docs:`).
- Implementation progress is tracked in [`docs/tasks.md`](./docs/tasks.md).
