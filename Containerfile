# MCP Gemini CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-gemini .
#
# Run:
#   podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini
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

# Stage 1: Builder (has a shell, dnf and build tools)
FROM quay.io/hummingbird/python:latest-builder AS builder
USER 0
WORKDIR /app
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

# Stage 2: Runtime (distroless -- no shell, no package manager)
FROM quay.io/hummingbird/python:latest

# Labels for container metadata
LABEL name="mcp-gemini-crunchtools" \
      version="0.3.0" \
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
