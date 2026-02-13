# AGENTS.md

Read [CLAUDE.md](./CLAUDE.md) first for project context.

## Agent Instructions

### code-planner
- Check CLAUDE.md for project structure before planning.
- Plans must be concise, actionable, with small steps.
- End every plan with unresolved questions (or "No unresolved questions.").

### code-executioner
- Read CLAUDE.md before making changes.
- Backend uses FastAPI + samgis_core + samgis_web packages.
- Frontend is Vue.js SPA in `static/` — see `static/CLAUDE.md`.
- SAM models in `sam-quantized/` submodule must be initialized.

### code-testing-planner
- Tests in `tests/` using pytest with coverage.
- Run: `python -m pytest --cov=samgis --cov-report=term-missing`
- Test payloads in `tests/events/`.

### commit-name-creator
- Use Conventional Commits format: `feat(scope):`, `fix:`, `docs:`, etc.
- Keep messages concise, focus on "why" not "what".
