# Claude Code Instructions

This is a secure MCP server for Google Gemini AI - text, image, video, research, and more.

## Quick Start

### Option 1: Using uvx (Recommended)

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    -- uvx mcp-gemini-crunchtools
```

### Option 2: Using Container

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    -- podman run -i --rm -e GEMINI_API_KEY quay.io/crunchtools/mcp-gemini
```

### Option 3: With Output Directory (for generated files)

```bash
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    --env GEMINI_OUTPUT_DIR=$HOME/.config/mcp-gemini-crunchtools/output \
    -- uvx mcp-gemini-crunchtools
```

### Option 4: Local Development

```bash
cd ~/Projects/crunchtools/mcp-gemini
claude mcp add mcp-gemini-crunchtools \
    --env GEMINI_API_KEY=your_api_key_here \
    -- uv run mcp-gemini-crunchtools
```

## Creating a Google Gemini API Key

### Step-by-Step Instructions

1. **Navigate to Google AI Studio**
   - Go to https://aistudio.google.com/apikey
   - Sign in with your Google account

2. **Create API Key**
   - Click "Get API key" or "Create API key"
   - Select a Google Cloud project or create a new one
   - Click "Create API key in new project" (or select existing project)

3. **Copy Your API Key**
   - **IMPORTANT: Copy the API key immediately** - store it securely!
   - The key starts with `AI...` (e.g., `AIzaSy...`)
   - Store it in a password manager or secure location

4. **Add to Claude Code**
   ```bash
   claude mcp add mcp-gemini-crunchtools \
       --env GEMINI_API_KEY=your_copied_api_key \
       -- uvx mcp-gemini-crunchtools
   ```

### Security Best Practices

- **Never commit API keys**: Don't put keys in code or config files in git
- **Use environment variables**: Always pass keys via `--env` flag
- **Monitor usage**: Check https://aistudio.google.com/apikey for API usage
- **Set billing alerts**: Detect unusual usage patterns in Google Cloud Console
- **Rotate keys**: Periodically create new keys and revoke old ones

## Available Tools (39 total)

### Query Tools (5)
- `gemini_query` - Query Gemini with optional Google Search grounding
- `gemini_brainstorm` - Generate creative ideas on a topic
- `gemini_analyze_code` - Analyze code for security, performance, bugs
- `gemini_analyze_text` - Analyze text for sentiment, tone, content
- `gemini_summarize` - Summarize content in various formats

### Image Generation (4)
- `gemini_generate_image` - Generate images from text prompts (native Gemini)
- `gemini_generate_image_with_input` - Edit/modify existing images
- `gemini_image_prompt` - Craft effective image generation prompts
- `gemini_imagen_generate` - Generate images using Google Imagen 4 models

### Image Editing (4)
- `gemini_start_image_edit` - Start a multi-turn image editing session
- `gemini_continue_image_edit` - Continue editing in an active session
- `gemini_end_image_edit` - End an image editing session
- `gemini_list_image_sessions` - List all active editing sessions

### Image Analysis (1)
- `gemini_analyze_image` - Analyze and describe local image files

### Search (1)
- `gemini_search` - Web search using Gemini with Google Search grounding

### Document (3)
- `gemini_analyze_document` - Analyze PDFs, DOCX, TXT, etc.
- `gemini_summarize_pdf` - Summarize PDF documents
- `gemini_extract_tables` - Extract tables from documents

### URL (3)
- `gemini_analyze_url` - Analyze one or more URLs
- `gemini_compare_urls` - Compare two URLs
- `gemini_extract_from_url` - Extract specific data from a URL

### Video (2)
- `gemini_generate_video` - Generate videos using Veo
- `gemini_check_video` - Check video generation status

### YouTube (2)
- `gemini_youtube` - Analyze YouTube videos
- `gemini_youtube_summary` - Summarize YouTube videos

### Voice (3)
- `gemini_speak` - Convert text to speech
- `gemini_dialogue` - Generate multi-voice dialogue audio
- `gemini_list_voices` - List available voices

### Research (3)
- `gemini_deep_research` - Perform multi-step web research
- `gemini_check_research` - Check research operation status
- `gemini_research_followup` - Ask follow-up questions

### Cache (4)
- `gemini_create_cache` - Create content cache for repeated queries
- `gemini_query_cache` - Query cached content
- `gemini_list_caches` - List all active caches
- `gemini_delete_cache` - Delete a cache

### Structured Output (2)
- `gemini_structured` - Get structured JSON output
- `gemini_extract` - Extract structured data from text

### Token (1)
- `gemini_count_tokens` - Count tokens in content

### Code Execution (1)
- `gemini_run_code` - Execute Python code via Gemini

## Example Usage

### Basic Query
```
User: What are the latest developments in quantum computing?
Assistant: [calls gemini_query with use_google_search=true]
```

### Generate Image
```
User: Generate a photorealistic image of a sunset over mountains
Assistant: [calls gemini_generate_image with prompt and style]
```

### Analyze Document
```
User: Analyze this research paper at /path/to/paper.pdf
Assistant: [calls gemini_analyze_document]
```

### Summarize YouTube Video
```
User: Summarize this video: https://youtube.com/watch?v=...
Assistant: [calls gemini_youtube_summary]
```

### Deep Research
```
User: Research the environmental impact of electric vehicles
Assistant: [calls gemini_deep_research then checks status]
```

### Code Analysis
```
User: Analyze this Python code for security issues
Assistant: [calls gemini_analyze_code with focus="security"]
```

### Multi-turn Image Editing
```
User: Create an image of a beach, then make the sky more dramatic
Assistant: [calls gemini_start_image_edit, then gemini_continue_image_edit]
```

### Extract Structured Data
```
User: Extract contact information from this text
Assistant: [calls gemini_extract with extract_type="contacts"]
```

## Model Selection

Most tools accept a `model` parameter:

- `flash` - Gemini 2.0 Flash (default) - Fast, cost-effective
- `pro` - Gemini 2.0 Pro - Higher quality, better reasoning

### Image Models

- `imagen-4.0-fast-generate-001` - $0.02/image, fastest
- `imagen-4.0-generate-001` - $0.04/image, standard (default)
- `imagen-4.0-ultra-generate-001` - $0.06/image, highest quality

## Output Files

Generated files (images, audio, video) are saved to:

- Default: `~/.config/mcp-gemini-crunchtools/output`
- Custom: Set `GEMINI_OUTPUT_DIR` environment variable

Files are named with UUIDs: `image_<uuid>.png`, `audio_<uuid>.mp3`, etc.

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Lint
uv run ruff check src tests

# Type check
uv run mypy src

# Build container
podman build -t mcp-gemini .
```

## Troubleshooting

### API Key Not Found

If you see "GEMINI_API_KEY required":

1. Ensure you passed `--env GEMINI_API_KEY=...` when adding the server
2. Restart Claude Code after adding the server
3. Verify the API key is correct (starts with `AI...`)

### Quota Exceeded

If you see quota errors:

1. Check your API usage at https://aistudio.google.com/apikey
2. Verify billing is enabled in Google Cloud Console
3. Wait for quota to reset (usually per-minute or per-day limits)

### Generated Files Not Found

If generated files aren't appearing:

1. Check `GEMINI_OUTPUT_DIR` is set correctly
2. Ensure the directory exists and is writable
3. Check tool output for the actual file path

## Privacy Considerations

When using Gemini, the following data is sent to Google:

- User prompts and queries
- Uploaded files (images, documents, videos)
- URLs for analysis

Review [Google's Gemini API Terms](https://ai.google.dev/terms) for data handling policies.

**Recommendations:**
- Don't send sensitive personal information
- Don't upload documents with secrets or credentials
- Review data retention policies for your use case
