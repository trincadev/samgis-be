# samgis-be — Supply Chain TODO

Triggered 2026-04-06 by tomshw "code resurrection" article. Cross-cutting work tracked in `~/workspace/agents_writer/TODO.md` § Supply Chain Hardening Rollout.

## Current state (good baseline)

- ✅ `uv.lock` committed
- ✅ `pyproject.toml` ranges are **upper-capped** (`>=0.27.2,<1.0.0` style) — already follows the rule
- ✅ Dockerfile inherits from prebuilt base image `registry.gitlab.com/aletrn/gis-prediction:1.12.7` — runtime deps frozen in the image, not installed at app build time
- ✅ `pip-audit` declared in `[dependency-groups] dev`

## Active

- [ ] **Wire `pip-audit` into CI gate** — currently declared in dev group but not run on every build. Add to post-production / CI step.
- [ ] **Lockfile-diff guard** in pre-commit (one-line bash check via `/supply-chain` skill once shipped).

## Deferred — base image owns the real risk

The dependency installation surface for samgis-be lives in the **base image build pipeline**, not in this repo. The Dockerfile here only imports the prebuilt image and runs smoke tests.

- [ ] **Audit `gis-prediction` base image build** for supply chain hardening: how are deps installed? Is `uv sync --frozen` used? Is the base image build reproducible? Are pin hashes verified? — Out of scope for this repo, file under `gis-prediction` (or wherever the base image Dockerfile lives) when triaging.
- [ ] **Set `production: true`** in samgis-be `CLAUDE.md` once strict enforcement is wanted.
- [ ] **Vendor untrusted-input parsers** (rasterio, geopandas, onnxruntime model loading) — these are the real attack surface for a GIS service. Currently bundled in the base image. Out of scope until base image audit is done.

## Notes

- HF Space deployment exists but threat model identical to tradingbot: private, single deploy path, low public attack surface for now.
