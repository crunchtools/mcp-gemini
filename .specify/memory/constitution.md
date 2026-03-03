# mcp-gemini-crunchtools Constitution

> **Version:** 1.0.0
> **Ratified:** 2026-03-02
> **Status:** Active
> **Inherits:** [crunchtools/constitution](https://github.com/crunchtools/constitution) v1.0.0
> **Profile:** MCP Server

This constitution establishes the core principles, constraints, and workflows that govern all development on mcp-gemini-crunchtools.

---

## I. Core Principles

### 1. Five-Layer Security Model

Every change MUST preserve all five security layers. No exceptions.

**Layer 1 — Token Protection:**
- API credentials stored as `SecretStr` (never logged or exposed)
- Environment-variable-only storage
- Automatic scrubbing from error messages

**Layer 2 — Input Validation:**
- Validation functions enforce strict data types
- Allowlists for permitted values (aspect ratios, image sizes, models)
- File paths validated against traversal patterns

**Layer 3 — API Hardening:**
- Auth via google-genai SDK (key never in URL)
- Request timeouts and response size limits
- File size validation before upload

**Layer 4 — Dangerous Operation Prevention:**
- No shell execution or code evaluation on the server
- No `eval()`/`exec()` functions
- Tools are pure API wrappers with no side effects beyond file output

**Layer 5 — Supply Chain Security:**
- Weekly automated CVE scanning via GitHub Actions
- Hummingbird container base images (minimal CVE surface)
- Gourmand AI slop detection gating all PRs

### 2. Two-Layer Tool Architecture

Tools follow a strict two-layer pattern:
- `server.py` — `@mcp.tool()` decorated functions that validate args and delegate
- `tools/*.py` — Pure async functions that call `client.py` SDK methods

Never put business logic in `server.py`. Never put MCP registration in `tools/*.py`.

### 3. Three Distribution Channels

Every release MUST be available through all three channels simultaneously:

| Channel | Command | Use Case |
|---------|---------|----------|
| uvx | `uvx mcp-gemini-crunchtools` | Zero-install, Claude Code |
| pip | `pip install mcp-gemini-crunchtools` | Virtual environments |
| Container | `podman run quay.io/crunchtools/mcp-gemini` | Isolated, systemd |

### 4. Three Transport Modes

The server MUST support all three MCP transports:
- **stdio** (default) — spawned per-session by Claude Code
- **SSE** — legacy HTTP transport
- **streamable-http** — production HTTP, systemd-managed containers

### 5. Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/) strictly.

**MAJOR** (breaking changes — consumers must update):
- Removed or renamed tools
- Changed tool parameter names or types
- Renamed environment variables
- Changed default behavior of existing tools

**MINOR** (new functionality — backwards compatible):
- New tools added
- New optional parameters on existing tools
- New tool groups

**PATCH** (fixes — no functional change):
- Bug fixes in existing tools
- Test additions or improvements
- Security patches (dependency updates)

**No version bump required** (infrastructure, not shipped):
- CI/CD changes (workflows, gourmand config)
- Documentation (README, CLAUDE.md, SECURITY.md)
- Issue templates, pre-commit config
- Governance files (.specify/)

**Version bump happens at release time, not per-commit.** Multiple commits can accumulate between releases. The version in `pyproject.toml` and `server.py` is bumped when cutting a release tag.

### 6. AI Code Quality

All code MUST pass Gourmand checks before merge. Zero violations required.

---

## II. Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.10+ |
| MCP Framework | FastMCP | Latest |
| AI SDK | google-genai | Latest |
| Validation | Pydantic | v2 |
| Image Processing | Pillow | Latest |
| Container Base | Hummingbird | Latest |
| Package Manager | uv | Latest |
| Build System | hatchling | Latest |
| Linter | ruff | Latest |
| Type Checker | mypy (strict) | Latest |
| Tests | pytest + pytest-asyncio | Latest |
| Slop Detector | gourmand | Latest |

---

## III. Testing Standards

### Mocked SDK Tests (MANDATORY)

Every tool MUST have a corresponding mocked test. Tests mock `GeminiClient` methods — no live API calls, no keys required in CI.

**Pattern:**
1. Patch `mcp_gemini_crunchtools.client.get_client` to return a mock
2. Configure mock methods (`generate_content`, `generate_images`, etc.)
3. Call the tool function directly (not the `_tool` wrapper)
4. Assert response structure and values

**Required test classes per tool group:**

| Tool Group | Test Class | Minimum Tests |
|------------|-----------|---------------|
| Each text tool | `TestQueryTools`, etc. | Verify response shape |
| Each image tool | `TestImageGenTools`, etc. | Verify image path handling |
| Each async tool | `TestVideoTools`, etc. | Verify operation tracking |
| Error cases | `TestErrorSafety` | API key sanitization |

**Singleton reset:** The `_reset_client_singleton` autouse fixture resets `client._client` and `config._config` between every test to prevent state leakage.

**Tool count assertion:** `test_tool_count` MUST be updated whenever tools are added or removed. This catches accidental regressions.

### Input Validation Tests

Every validation function in `models.py` MUST have tests in `test_validation.py`:
- Valid inputs accepted
- Invalid inputs rejected with proper errors

### Security Tests

- API key sanitization: `GeminiApiError` MUST scrub keys from messages
- Config safety: `repr()` and `str()` MUST never expose the key
- Config requires `GEMINI_API_KEY`

---

## IV. Gourmand (AI Slop Detection)

All code MUST pass `gourmand --full .` with **zero violations** before merge. Gourmand is a CI gate in GitHub Actions.

### Configuration

- `gourmand.toml` — Check settings, excluded paths
- `gourmand-exceptions.toml` — Documented exceptions with justifications
- `.gourmand-cache/` — Must be in `.gitignore`

### Checks That Apply

| Check | What it catches |
|-------|----------------|
| `linter_configuration` | Missing ruff rules, no pre-commit hooks |
| `lint_suppression` | `type: ignore` without fix |
| `generic_names` | Variables named `data`, `result`, `temp` |
| `verbose_comments` | Redundant comments restating code |
| `summary_litter` | AI status/summary files in project root |
| `prefer_match` | elif chains that should be match/case |
| `primitive_obsession` | Magic numbers without named constants |
| `copy_paste_detection` | Duplicated code blocks |
| `single_use_helpers` | Unnecessary abstractions |
| `speculative_generality` | YAGNI violations |

### Exception Policy

Exceptions MUST have documented justifications in `gourmand-exceptions.toml`. Acceptable reasons:
- Standard API patterns (HTTP status codes, pagination params)
- Test-specific patterns (intentional invalid input)
- Framework requirements (CLAUDE.md for Claude Code)

Unacceptable reasons:
- "The code is special"
- "The threshold is too strict"
- Rewording to avoid detection

---

## V. Code Quality Gates

Every code change must pass through these gates in order:

1. **Lint** — `uv run ruff check src tests`
2. **Type Check** — `uv run mypy src`
3. **Tests** — `uv run pytest -v` (all passing, mocked google-genai)
4. **Gourmand** — `gourmand --full .` (zero violations)
5. **Container Build** — `podman build -f Containerfile .`

### CI Pipeline (GitHub Actions)

| Job | What it does | Gates PRs |
|-----|-------------|-----------|
| test | Lint + mypy + pytest (Python 3.10-3.12) | Yes |
| gourmand | AI slop detection | Yes |
| build-container | Containerfile builds | Yes |
| security | Weekly CVE scan + CodeQL | Scheduled |
| publish | PyPI trusted publishing | On release tag |
| container | Quay.io push + Trivy | On release tag |

---

## VI. Naming Conventions

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-gemini` |
| PyPI package | `mcp-gemini-crunchtools` |
| CLI command | `mcp-gemini-crunchtools` |
| Python module | `mcp_gemini_crunchtools` |
| Container image | `quay.io/crunchtools/mcp-gemini` |
| systemd service | `mcp-gemini.service` |
| HTTP port | 8011 |
| License | AGPL-3.0-or-later |
| API Key env var | `GEMINI_API_KEY` |

---

## VII. Development Workflow

### Adding a New Tool

1. Add the async function to the appropriate `tools/*.py` file
2. Export it from `tools/__init__.py`
3. Import it in `server.py` and register with `@mcp.tool()`
4. Add a mocked test in `tests/test_tools.py`
5. Update the tool count in `test_tool_count`
6. Run all five quality gates
7. Update CLAUDE.md tool listing

### Adding a New Tool Group

1. Create `tools/new_group.py` with async functions
2. Add imports and `__all__` entries in `tools/__init__.py`
3. Add `@mcp.tool()` wrappers in `server.py`
4. Add a `TestNewGroupTools` class in `tests/test_tools.py`
5. Run all five quality gates

---

## VIII. Governance

### Amendment Process

1. Create a PR with proposed changes to this constitution
2. Document rationale in PR description
3. Require maintainer approval
4. Update version number upon merge

### Ratification History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-02 | Initial constitution |
