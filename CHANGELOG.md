# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

## [0.8.1] - 2026-11-11

### Changed

- No functional change. First release on the build-once container pipeline (RT#1550): `:latest` now names a digest that passed the release gates.

## [0.8.0] - 2026-11-09

### Added

- **The client says what it is.** Requests carry
  `User-Agent: mcp-gemini-crunchtools/<version> (+<repo url>)`, with the
  version read from installed package metadata, alongside the
  `Accept-Encoding: identity` already set there.

  Worth recording why this needed doing by hand: `google-genai` owns the
  transport, so `check_http_client` from constitution v1.36.0 skips this repo
  entirely — it finds no HTTP import under `src/`. The check cannot catch a
  missing agent string here, which is precisely why the header is set
  deliberately and asserted by a test (RT #1601).

### Fixed

- A malformed `Content-Length` is no longer an unhandled `ValueError`. The
  header is whatever the far end sent, and an unguarded `int()` on it escaped
  as itself rather than as a `GeminiApiError`. The message now also says what
  was declared and what the limit is.

### Changed

- Inherits constitution v1.36.0. This repo's response guard — a response hook
  that bounds the stream before the body is read, with compression refused so
  the counted bytes are the bytes the SDK reads — is what the profile's
  "measuring at the transport counts wire bytes" note is drawn from.

## [0.7.1] - 2026-11-07

### Fixed

- Every tool failed with `Gemini API error: Attempted to call a sync close on
  an async stream`. Nothing in this project is async there: google-genai 3.0
  swapped its required HTTP library from `httpx` to `httpx2`, which is a
  separate distribution with its own `SyncByteStream`. The response-size guard
  wrapped the body stream in a class built on `httpx`'s base, so httpx2's
  `isinstance` check rejected it when closing the response, and reported that
  as an async-stream error. The wrapper is now built from whichever flavour
  produced the response, so the guard works under either library.
- An HTTP library offering no `SyncByteStream` at all now fails the call with
  a clear message instead of passing the body through uncapped. The
  constitution caps responses at 100MB and an uncountable body cannot honour
  that.
- The container installs its dependencies from `uv.lock` instead of resolving
  them fresh from `pyproject.toml`. `pip install .` read only the floor pins,
  so the image shipped whatever had been released that morning -- a dependency
  set no test had ever run against. That is how the google-genai 3.0 break
  above reached production with CI green: CI tested the locked versions and the
  container shipped different ones. Same bug as trentina issue #79.
- `google-genai` carries an upper bound at the next major, so a release that
  changes its HTTP layer again arrives as a Dependabot pull request that has to
  pass the suite rather than as a silent change inside a container build.

### Added

- Tests for the response-size guard against real `httpx` and `httpx2` response
  objects, parametrised over every flavour installed. The rest of the suite
  mocks the SDK, so the guard and its stream wrapper were never executed by any
  test and a break in them could not fail CI -- which is why this one did not.

## [0.7.0] - 2026-11-06

### Added

- `GEMINI_API_KEY_FILE` reads the API key from a file when `GEMINI_API_KEY` is
  unset, keeping the key out of MCP config and `podman inspect`.

### Security

- `GeminiApiError` now redacts the resolved key from `Config`, so a key loaded
  from a file is scrubbed from upstream error messages.

## [0.6.1] - 2026-10-31

### Security

- Upgraded locked dependencies within their declared ranges to clear the
  advisories the fleet dependency audit found (anyio, authlib, certifi, cryptography, dnspython, fastmcp, joserfc, opentelemetry-api, pillow, pyasn1, pydantic-settings, pygments, pyjwt, python-dotenv, requests, urllib3).

## [0.6.0] - 2026-10-20

### Changed

- Container base images pinned to `quay.io/hummingbird/python:3.14*` instead of
  `latest`, which moved to Python 3.15.0 on 2026-10-20 (crunchtools/constitution#66).

## [0.5.0] - 2026-10-16

### Added

- `gemini_check_video_tool` and `gemini_check_research_tool` publish
  `readOnlyHint: true`.

### Changed

- The YouTube tools attach the video as a `file_data` part (`file_uri` is the
  URL) instead of passing the URL as prompt text with search grounding.
- `gemini_deep_research_tool` documents that it completes in a single call.

### Fixed

- `gemini_deep_research_tool` IDs use `uuid4`, so two calls in the same second
  no longer collide.
- `gemini_generate_image_tool` passes `aspect_ratio` and `image_size` to the
  image config instead of ignoring them.

## [0.4.0] - 2026-10-10

### Added

- The 20 tools that only read publish `readOnlyHint: true`. A gateway uses it
  to decide whether an invalid optional argument may be dropped or must refuse
  the call (crunchtools/constitution#35). Every tool here is a paid model
  call, so the line is drawn at one `generateContent`, `countTokens` or list
  request that writes nothing to the output directory and stores nothing with
  Google. Tools that generate images, audio or video, upload through the Files
  API, create or delete a cache, run code, or start or poll a long-running
  operation stay unannotated.
- Tests pin every registered tool into `READ_ONLY` or `WRITES`, and check with
  a mocked client that each read-only tool makes at most one such request,
  uses no upload, cache or code execution, and creates no file.

### Changed

- Inherits constitution v1.22.0; the workflow pins and the pre-commit hook rev
  move with it.
- Constitution is now a v1.18.0 manifest: it holds only what is specific to
  this repo; fleet and profile rules apply by reference.
- Constitution validation is pinned to the inherited release via
  `.github/workflows/constitution.yml`.
- Dependabot auto-merges GitHub Actions minor and patch updates.

## [0.3.1] - 2026-09-28

### Fixed

- A slow Gemini call no longer freezes the server for every other caller.
  Tools called the synchronous google-genai SDK from async handlers, so one
  long generation blocked the event loop until it returned; on 2026-09-28 the
  server stopped answering even `initialize` and had to be restarted. SDK
  calls now run in a worker thread, and requests carry a 300-second HTTP
  timeout so a stalled one ends as an error.
- Turns within one image-edit session are serialized, so two concurrent
  edits cannot interleave the chat history.
- Responses larger than 100 MB are refused, chunked ones included, and
  `gemini_create_cache` enforces the same upload size limit as the document
  tools.

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
