# Claude Code Instructions

## Project

td — AI-native Todoist CLI. Python, Click, Rich. See README.md for details.

## Development Workflow

### Before starting work
1. `git checkout main && git pull`
2. `make check` to verify clean state
3. Review open issues: `gh issue list --state open`

### During a feature sprint
1. Create feature branch: `git checkout -b feat/description`
2. Implement with tests
3. `make check` must pass (lint + 85% coverage gate)
4. Conventional commit: `feat(scope):`, `fix:`, `docs:`, `chore:`, etc.
5. Push and PR: `git push -u origin feat/... && gh pr create`
6. Wait for CI, then merge: `gh pr merge <n> --merge`
7. `git checkout main && git pull`

### After shipping features (EVERY sprint, not optional)
1. **Update docs**: README.md commands table, AGENTS.md command list, quick start examples
2. **Regenerate examples**: `make examples`
3. **Update CHANGELOG.md**: add entries under [Unreleased]
4. **Bump version**: update `td/__init__.py`
5. **Release PR**: branch, commit, push, merge
6. **Tag**: `git tag -a vX.Y.Z-alpha -m "vX.Y.Z-alpha" && git push origin vX.Y.Z-alpha`
7. **Release notes**: `gh release edit vX.Y.Z-alpha --notes "..."`

### Commands
```
make check      # lint + test (the one command you need)
make fmt        # auto-format
make test       # tests only
make lint       # lint only
make examples   # regenerate docs/examples.md
make release    # VERSION=x.y.z — bump, changelog, tag, push
```

## Code Conventions

- **Architecture**: `td/core/` is pure business logic (no CLI). `td/cli/` is the Click frontend.
- **Output**: All commands use `OutputFormatter` for Rich/JSON/Plain modes.
- **Errors**: Structured `TdError` subclasses with codes and suggestions.
- **Task refs**: All task commands accept row number, content match, or task ID via `_resolve_task()`.
- **Caching**: Name cache (5-min TTL) in `td/core/cache.py`. Result cache (10-min TTL) for row numbers.
- **Types**: `mypy --strict` must pass. Use `Any` sparingly.
- **Sorting**: List commands support `--sort` and `--reverse` via `sort_tasks()`.

## What NOT to do

- Don't push directly to main (branch protection enforced)
- Don't skip `make check` before committing
- Don't ship features without updating docs and releasing
- Don't use `lambda` assignments (ruff E731)
- Don't use `try/except pass` (use `contextlib.suppress`)
