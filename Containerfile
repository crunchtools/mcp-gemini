# MCP Gemini CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-gemini .
#
# Run:
#   podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini
#
# With output directory (for generated images/audio):
#   podman run -i --rm \
#     -v ~/.config/mcp-gemini-crunchtools/output:/output:Z \
#     -e GEMINI_API_KEY \
#     -e GEMINI_OUTPUT_DIR=/output \
#     quay.io/crunchtools/mcp-gemini
#
# With Claude Code:
#   claude mcp add mcp-gemini-crunchtools \
#     --env GEMINI_API_KEY=your_key \
#     -- podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini

# Use Hummingbird Python image (Red Hat UBI-based with Python pre-installed)
FROM quay.io/hummingbird/python:latest

# Labels for container metadata
LABEL name="mcp-gemini-crunchtools" \
      version="0.1.0" \
      summary="MCP server for Google Gemini AI" \
      description="A security-focused MCP server for Google Gemini AI built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-gemini" \
      io.k8s.display-name="MCP Gemini CrunchTools" \
      io.openshift.tags="mcp,gemini,ai,imagen"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and dependencies
RUN pip install --no-cache-dir .

# Verify installation
RUN python -c "from mcp_gemini_crunchtools import main; print('Installation verified')"

# MCP servers run via stdio, so we need interactive mode
# The entrypoint runs the MCP server
ENTRYPOINT ["python", "-m", "mcp_gemini_crunchtools"]

# No CMD needed - the server reads from stdin and writes to stdout
