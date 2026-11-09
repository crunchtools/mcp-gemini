# MCP Gemini CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-gemini .
#
# Run:
#   podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini
#
# With the key as a mounted secret file (keeps it out of `podman inspect`):
#   podman run -i --rm \
#     -v ~/.config/mcp-gemini/api-key:/run/secrets/api-key:ro,z \
#     -e GEMINI_API_KEY_FILE=/run/secrets/api-key \
#     quay.io/crunchtools/mcp-gemini
#
# With shared volume (for generated images/audio and input files):
#   mkdir -p ~/.local/share/mcp-uploads-downloads
#   podman run -i --rm \
#     -v ~/.local/share/mcp-uploads-downloads:/output:z \
#     -e GEMINI_API_KEY \
#     -e GEMINI_OUTPUT_DIR=/output \
#     quay.io/crunchtools/mcp-gemini
#
# With Claude Code:
#   mkdir -p ~/.local/share/mcp-uploads-downloads
#   claude mcp add mcp-gemini-crunchtools \
#     --env GEMINI_API_KEY=your_key \
#     --env GEMINI_OUTPUT_DIR=/output \
#     -- podman run -i --rm \
#       -v ~/.local/share/mcp-uploads-downloads:/output:z \
#       -e GEMINI_API_KEY \
#       -e GEMINI_OUTPUT_DIR=/output \
#       quay.io/crunchtools/mcp-gemini

# Stage 1: Lock (turn uv.lock into the exact dependency set to install)
FROM quay.io/hummingbird/python:3.14-builder AS lock
USER 0
RUN pip install --no-cache-dir uv==0.13.7
WORKDIR /lock
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project \
      --format requirements-txt -o /requirements.txt

# Stage 2: Builder (has a shell, dnf and build tools)
FROM quay.io/hummingbird/python:3.14-builder AS builder
USER 0
WORKDIR /app
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
# Dependencies come from uv.lock, not from a fresh resolve. `pip install .`
# read only pyproject.toml, whose floors carry no upper bound, so the image
# shipped whatever had been released that morning -- a dependency set no test
# had ever run against. That is how google-genai 3.0, which inverted httpx and
# httpx2, reached production with CI green (trentina issue #79 is the same
# bug). --no-deps stops pip re-resolving what the lock already decided.
COPY --from=lock /requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-deps -r /tmp/requirements.txt
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps .

# Stage 3: Runtime (distroless -- no shell, no package manager)
FROM quay.io/hummingbird/python:3.14

# Labels for container metadata
LABEL name="mcp-gemini-crunchtools" \
      version="0.8.0" \
      summary="MCP server for Google Gemini AI" \
      description="A security-focused MCP server for Google Gemini AI built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-gemini" \
      io.k8s.display-name="MCP Gemini CrunchTools" \
      io.openshift.tags="mcp,gemini,ai,imagen" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-gemini" \
      org.opencontainers.image.description="MCP server for Google Gemini AI" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

WORKDIR /app

COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Verify the install. Exec form: this stage has no /bin/sh for RUN's shell form.
RUN ["python3", "-c", "from mcp_gemini_crunchtools import main; print('Installation verified')"]

# Default: stdio transport (use -i with podman run)
# HTTP:    --transport streamable-http (use -d -p 8000:8000 with podman run)
EXPOSE 8011
ENTRYPOINT ["python", "-m", "mcp_gemini_crunchtools"]
