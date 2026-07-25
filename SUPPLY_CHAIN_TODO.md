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

## Python `.pth` injection + runtime-exec hardening

Defense-in-depth against a compromised dependency planting a malicious `.pth` file in
site-packages — it executes arbitrary Python at every interpreter startup, a stealthy persistence
vector that `pip-audit`/Trivy/Syft do **not** detect (they treat packages as files, not as
executable code). Mirrors the `.pth` sentinel added to `devcontainer-guard` (MIASMA-3/MIASMA-5,
2026-07-02).

- [ ] **Dockerfile env hardening** (this repo): set `PYTHONNOUSERSITE=1` + `PYTHONPATH=` (empty) in
      the samgis-be Dockerfile. Cheap, no runtime cost, independent of the base image.
- [ ] **Startup/healthcheck `.pth` sentinel** (design corrected 2026-07-02 after adversarial review).
      site.py exec's any `.pth` line starting with `import `/`import\t` (single line; `from`-imports
      inert). **Detection = an `import`-line that makes a call `(` or chains `;` is suspicious UNLESS
      it matches a small safe-pattern allowlist.** Do NOT use a raw marker substring blocklist
      (`os.system(`…) — trivially evaded by `import os as o; o.system(...)`, getattr/importlib
      indirection, string-concat, `sys.path` manipulation; keep markers only as a secondary
      escalator. Severity: unexpected name in system root → CRIT, in workspace/user venv → WARN;
      suspicious content → CRIT; `.pth` > 4 KB → CRIT (weak size heuristic). Scan top-level of each
      site dir only (site.py doesn't recurse).
  - **⚠ MANDATORY content-pattern allowlist**: `distutils-precedence.pth` ships with setuptools in
      nearly every image (`import os; ...__import__('_distutils_hack').add_shim();`) and a naive scan
      FAILs it. Allowlist by content pattern: (1) `distutils-precedence.pth`, (2) editable finders
      `^import __editable___\w+_finder; __editable___\w+_finder\.install\(\)$` (regex, keep tight),
      (3) `declare_namespace` lines.
  - **Also scan (same pass)**: unexpected `sitecustomize.py`/`usercustomize.py` and
      **`/etc/ld.so.preload`** (native LD_PRELOAD persistence; any content = CRIT). Note most
      site-packages come from the `gis-prediction` base image — the sentinel scanning the *running*
      image covers them regardless of install origin. Reference impl: `devcontainer-guard`
      `scripts/_shared/pth_sentinel.py` once shipped (copy the inverted predicate + allowlist).
- [ ] **Base-image note**: most site-packages come from `gis-prediction` — the sentinel scanning
      the *running* image covers those regardless of where they were installed. The env hardening
      above is the only part that must live in this repo's Dockerfile.
- **Defer until**: pre-production hardening pass, or sooner if a dep audit flags a suspicious
      package. HF Space is private / low public attack surface (see Notes) — not blocking.

## Deferred — base image owns the real risk

The dependency installation surface for samgis-be lives in the **base image build pipeline**, not in this repo. The Dockerfile here only imports the prebuilt image and runs smoke tests.

- [ ] **Audit `gis-prediction` base image build** for supply chain hardening: how are deps installed? Is `uv sync --frozen` used? Is the base image build reproducible? Are pin hashes verified? — Out of scope for this repo, file under `gis-prediction` (or wherever the base image Dockerfile lives) when triaging.
- [ ] **Set `production: true`** in samgis-be `CLAUDE.md` once strict enforcement is wanted.
- [ ] **Vendor untrusted-input parsers** (rasterio, geopandas, onnxruntime model loading) — these are the real attack surface for a GIS service. Currently bundled in the base image. Out of scope until base image audit is done.

## Notes

- HF Space deployment exists but threat model identical to tradingbot: private, single deploy path, low public attack surface for now.
