# mcp-gemini-crunchtools Constitution

> **Version:** 1.1.0
> **Ratified:** 2026-03-02
> **Amended:** 2026-10-02
> **Status:** Active
> **Inherits:** [crunchtools/constitution](https://github.com/crunchtools/constitution) v1.22.0
> **Profile:** MCP Server

This file holds what is specific to mcp-gemini. The fleet rules and the MCP
Server profile (five-layer security model, two-layer tools, distribution
channels, transports, quality gates, Gourmand) apply at the inherited version
and are checked against this repo's files by `constitution.yml`. They are not
restated here.

## Security Model Specifics

- **Credentials:** `GEMINI_API_KEY` (required), held as `SecretStr`, read
  from the environment only. `GeminiApiError` scrubs it from messages, and
  `Config.__repr__()`/`__str__()` never expose it.
- **Input limits:** allowlists for aspect ratios, image sizes (`1K`, `2K`,
  `4K`), Imagen models and text models; input images are capped at 20MB and
  documents at 100MB before upload.
- **API:** auth goes through the google-genai SDK, never the URL. The SDK's
  HTTP layer has no default timeout, so requests are bounded at 300s here;
  responses are capped at 100MB, sized for inline base64 images.
- **Surface:** tools are API wrappers whose only side effect is writing
  generated files to the output directory. No shell execution or code
  evaluation.

## Generated Output

Generated images, audio and video go to `GEMINI_OUTPUT_DIR` (default
`~/.config/mcp-gemini-crunchtools/output`, created on startup). In the
container, mount a shared volume and set `GEMINI_OUTPUT_DIR` to it so the
client can read the files.

## Mocked SDK Tests

Tests mock `GeminiClient` (patch `mcp_gemini_crunchtools.client.get_client`)
rather than HTTP, because the server talks to Gemini through the google-genai
SDK. Image tools assert image path handling, async tools (video) assert
operation tracking, and `TestErrorSafety` asserts API key scrubbing.

## Instance

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-gemini` |
| PyPI package | `mcp-gemini-crunchtools` |
| Container image | `quay.io/crunchtools/mcp-gemini` |
| systemd service | `mcp-gemini.service` |
| HTTP port | 8011 |

## History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-02 | Initial constitution |
| 1.0.1 | 2026-03-16 | Add Section VI (Container Conventions); renumber VI-VIII to VII-IX |
| 1.0.2 | 2026-09-25 | Inherit constitution v1.17.0 (Gatehouse gates) |
| 1.1.0 | 2026-10-02 | Manifest under constitution v1.18.0: profile restatement removed, mcp-gemini specifics kept; unimplemented path-traversal claim dropped |
