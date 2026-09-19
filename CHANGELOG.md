# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

## [0.3.0] - 2026-03-02

v2 best practices upgrade.

### Added
- `.specify/` governance framework (constitution, baseline spec, templates).
- 78 mocked tests covering all 39 tools (test_tools, test_validation, test_errors).
- Gourmand AI slop detection config — zero violations across 31 checks.
- Pre-commit hooks (ruff check + ruff format).
- GitHub issue templates (bug report, feature request).
- `gourmand-exceptions.toml` for documented exceptions.

### Changed
- Version bumped from 0.1.1 to 0.3.0.
- CI workflow: added gourmand quality gate job.
- CI workflow: container build uses plain `docker build` instead of
  docker/build-push-action.
- Default HTTP port changed from 8000 to 8011.
- Removed verbose comments flagged by gourmand across source files.

### Fixed
- Unused `_mime_type` parameter in `save_generated_image`.

## [0.1.0] - 2026-02-20

First release of the MCP server for Google Gemini AI.

### Added
- 39 Gemini AI tools across 7 categories.
- Query, brainstorm, code analysis, text analysis.
- Image generation (Gemini native + Imagen 4) and multi-turn image editing
  sessions.
- Document analysis (PDF, DOCX, TXT).
- YouTube video analysis and summarization.
- Video generation with Veo.
- Text-to-speech and multi-voice dialogue.
- Deep research with multi-step web search.
- Content caching for efficient repeated queries.
- Structured JSON output and data extraction.
- Python code execution via Gemini.
