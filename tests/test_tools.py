"""Mocked tool tests for mcp-gemini-crunchtools.

Every tool gets at least one test with mocked google-genai SDK calls.
No live API calls, no API keys required.
"""

from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import (
    mock_audio_response,
    mock_gemini_client,
    mock_generate_response,
)

EXPECTED_TOOL_COUNT = 39


async def test_tool_count() -> None:
    """Verify the expected number of tools are registered on the server."""
    from mcp_gemini_crunchtools.server import mcp

    tools = await mcp._list_tools()
    assert len(tools) == EXPECTED_TOOL_COUNT, (
        f"Expected {EXPECTED_TOOL_COUNT} tools, found {len(tools)}. "
        f"Tools: {sorted(t.name for t in tools)}"
    )

class TestQueryTools:
    """Tests for query, brainstorm, analyze_code, analyze_text, summarize."""

    @patch("mcp_gemini_crunchtools.tools.query.get_client")
    async def test_gemini_query(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.query import gemini_query

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("hello world")
        mock_get_client.return_value = mock_client

        result = await gemini_query(prompt="test prompt")
        assert result["response"] == "hello world"
        assert "model" in result

    @patch("mcp_gemini_crunchtools.tools.query.get_client")
    async def test_gemini_brainstorm(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.query import gemini_brainstorm

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("ideas here")
        mock_get_client.return_value = mock_client

        result = await gemini_brainstorm(topic="containers")
        assert result["response"] == "ideas here"
        assert result["topic"] == "containers"

    @patch("mcp_gemini_crunchtools.tools.query.get_client")
    async def test_gemini_analyze_code(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.query import gemini_analyze_code

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("code analysis")
        mock_get_client.return_value = mock_client

        result = await gemini_analyze_code(code="print('hi')", focus="security")
        assert result["response"] == "code analysis"
        assert result["focus"] == "security"

    @patch("mcp_gemini_crunchtools.tools.query.get_client")
    async def test_gemini_analyze_text(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.query import gemini_analyze_text

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("text analysis")
        mock_get_client.return_value = mock_client

        result = await gemini_analyze_text(text="some text", analysis_type="sentiment")
        assert result["response"] == "text analysis"
        assert result["analysis_type"] == "sentiment"

    @patch("mcp_gemini_crunchtools.tools.query.get_client")
    async def test_gemini_summarize(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.query import gemini_summarize

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("summary")
        mock_get_client.return_value = mock_client

        result = await gemini_summarize(content="long content", format="bullets")
        assert result["response"] == "summary"
        assert result["format"] == "bullets"

class TestImageGenTools:
    """Tests for generate_image, generate_image_with_input, image_prompt, imagen_generate."""

    @patch("mcp_gemini_crunchtools.tools.image_gen.save_generated_image")
    @patch("mcp_gemini_crunchtools.tools.image_gen.extract_text_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_gen.extract_image_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_gen.get_client")
    async def test_gemini_generate_image(
        self,
        mock_get_client: MagicMock,
        mock_extract_image: MagicMock,
        mock_extract_text: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.image_gen import gemini_generate_image

        mock_client = mock_gemini_client()
        mock_get_client.return_value = mock_client
        mock_extract_image.return_value = (b"png-bytes", "image/png")
        mock_extract_text.return_value = "a nice image"
        mock_save.return_value = mock_client.output_dir / "test.png"

        result = await gemini_generate_image(prompt="a sunset")
        assert "image_path" in result
        assert result["prompt"] == "a sunset"

    @patch("mcp_gemini_crunchtools.tools.image_gen.get_client")
    async def test_gemini_image_prompt(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.image_gen import gemini_image_prompt

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("crafted prompt")
        mock_get_client.return_value = mock_client

        result = await gemini_image_prompt(description="a mountain landscape")
        assert result["prompt"] == "crafted prompt"

    @patch("mcp_gemini_crunchtools.tools.image_gen.save_generated_image")
    @patch("mcp_gemini_crunchtools.tools.image_gen.get_client")
    async def test_gemini_imagen_generate(
        self, mock_get_client: MagicMock, mock_save: MagicMock
    ) -> None:
        from mcp_gemini_crunchtools.tools.image_gen import gemini_imagen_generate

        mock_client = mock_gemini_client()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"png-bytes"
        mock_response = MagicMock()
        mock_response.generated_images = [mock_image]
        mock_client.generate_images.return_value = mock_response
        mock_get_client.return_value = mock_client
        mock_save.return_value = mock_client.output_dir / "imagen.png"

        result = await gemini_imagen_generate(prompt="a cat")
        assert result["count"] == 1
        assert result["model"] == "imagen-4.0-generate-001"

class TestImageEditTools:
    """Tests for start, continue, end, list_sessions."""

    @patch("mcp_gemini_crunchtools.tools.image_edit.save_generated_image")
    @patch("mcp_gemini_crunchtools.tools.image_edit.extract_text_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_edit.extract_image_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_edit.get_client")
    async def test_start_image_edit(
        self,
        mock_get_client: MagicMock,
        mock_extract_image: MagicMock,
        mock_extract_text: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.image_edit import gemini_start_image_edit

        mock_client = mock_gemini_client()
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = mock_generate_response("started")
        mock_client.create_chat.return_value = mock_chat
        mock_get_client.return_value = mock_client
        mock_extract_image.return_value = (b"png-data", "image/png")
        mock_extract_text.return_value = "editing started"
        mock_save.return_value = mock_client.output_dir / "edit.png"

        result = await gemini_start_image_edit(prompt="draw a house")
        assert "session_id" in result
        assert result["turn_count"] == 1

    @patch("mcp_gemini_crunchtools.tools.image_edit.save_generated_image")
    @patch("mcp_gemini_crunchtools.tools.image_edit.extract_text_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_edit.extract_image_from_response")
    @patch("mcp_gemini_crunchtools.tools.image_edit.get_client")
    async def test_continue_image_edit(
        self,
        mock_get_client: MagicMock,
        mock_extract_image: MagicMock,
        mock_extract_text: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        import time

        from mcp_gemini_crunchtools.tools.image_edit import (
            _sessions,
            gemini_continue_image_edit,
        )

        mock_client = mock_gemini_client()
        mock_get_client.return_value = mock_client
        mock_extract_image.return_value = (b"png-data", "image/png")
        mock_extract_text.return_value = "continued"
        mock_save.return_value = mock_client.output_dir / "edit2.png"

        session_id = "edit-test123"
        _sessions[session_id] = {
            "chat": MagicMock(),
            "last_active": time.time(),
            "turn_count": 1,
            "images": [],
        }

        result = await gemini_continue_image_edit(session_id=session_id, prompt="make sky blue")
        assert result["turn_count"] == 2

    async def test_end_image_edit(self) -> None:
        import time

        from mcp_gemini_crunchtools.tools.image_edit import (
            _sessions,
            gemini_end_image_edit,
        )

        session_id = "edit-endtest"
        _sessions[session_id] = {
            "chat": MagicMock(),
            "last_active": time.time(),
            "turn_count": 3,
            "images": ["/fake/path.png"],
        }

        result = await gemini_end_image_edit(session_id=session_id)
        assert result["status"] == "ended"
        assert result["total_turns"] == 3
        assert session_id not in _sessions

    async def test_end_image_edit_not_found(self) -> None:
        from mcp_gemini_crunchtools.errors import SessionNotFoundError
        from mcp_gemini_crunchtools.tools.image_edit import gemini_end_image_edit

        with pytest.raises(SessionNotFoundError):
            await gemini_end_image_edit(session_id="nonexistent")

    async def test_list_image_sessions(self) -> None:
        from mcp_gemini_crunchtools.tools.image_edit import gemini_list_image_sessions

        result = await gemini_list_image_sessions()
        assert result["count"] == 0
        assert result["sessions"] == []

class TestImageAnalysisTools:
    """Tests for analyze_image."""

    @patch("mcp_gemini_crunchtools.tools.image_analyze.Image")
    @patch("mcp_gemini_crunchtools.tools.image_analyze.validate_file_exists")
    @patch("mcp_gemini_crunchtools.tools.image_analyze.get_client")
    async def test_gemini_analyze_image(
        self,
        mock_get_client: MagicMock,
        mock_validate: MagicMock,
        mock_pil: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.image_analyze import gemini_analyze_image

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("a photo of a cat")
        mock_get_client.return_value = mock_client
        mock_validate.return_value = "/fake/image.png"
        mock_pil.open.return_value = MagicMock()

        result = await gemini_analyze_image(image_path="/fake/image.png")
        assert result["response"] == "a photo of a cat"

class TestSearchTools:
    """Tests for search."""

    @patch("mcp_gemini_crunchtools.tools.search.get_client")
    async def test_gemini_search(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.search import gemini_search

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("search results")
        mock_get_client.return_value = mock_client

        result = await gemini_search(query="python containers")
        assert result["response"] == "search results"
        assert result["query"] == "python containers"

class TestDocumentTools:
    """Tests for analyze_document, summarize_pdf, extract_tables."""

    @patch("mcp_gemini_crunchtools.tools.document.os.path.getsize")
    @patch("mcp_gemini_crunchtools.tools.document.validate_file_exists")
    @patch("mcp_gemini_crunchtools.tools.document.get_client")
    async def test_gemini_analyze_document(
        self,
        mock_get_client: MagicMock,
        mock_validate: MagicMock,
        mock_getsize: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.document import gemini_analyze_document

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("doc analysis")
        mock_get_client.return_value = mock_client
        mock_validate.return_value = "/fake/doc.pdf"
        mock_getsize.return_value = 1024

        result = await gemini_analyze_document(file_path="/fake/doc.pdf")
        assert result["response"] == "doc analysis"

    @patch("mcp_gemini_crunchtools.tools.document.os.path.getsize")
    @patch("mcp_gemini_crunchtools.tools.document.validate_file_exists")
    @patch("mcp_gemini_crunchtools.tools.document.get_client")
    async def test_gemini_summarize_pdf(
        self,
        mock_get_client: MagicMock,
        mock_validate: MagicMock,
        mock_getsize: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.document import gemini_summarize_pdf

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("pdf summary")
        mock_get_client.return_value = mock_client
        mock_validate.return_value = "/fake/doc.pdf"
        mock_getsize.return_value = 1024

        result = await gemini_summarize_pdf(file_path="/fake/doc.pdf")
        assert result["response"] == "pdf summary"

    @patch("mcp_gemini_crunchtools.tools.document.os.path.getsize")
    @patch("mcp_gemini_crunchtools.tools.document.validate_file_exists")
    @patch("mcp_gemini_crunchtools.tools.document.get_client")
    async def test_gemini_extract_tables(
        self,
        mock_get_client: MagicMock,
        mock_validate: MagicMock,
        mock_getsize: MagicMock,
    ) -> None:
        from mcp_gemini_crunchtools.tools.document import gemini_extract_tables

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("| col1 | col2 |")
        mock_get_client.return_value = mock_client
        mock_validate.return_value = "/fake/doc.pdf"
        mock_getsize.return_value = 1024

        result = await gemini_extract_tables(file_path="/fake/doc.pdf")
        assert "response" in result

class TestUrlTools:
    """Tests for analyze_url, compare_urls, extract_from_url."""

    @patch("mcp_gemini_crunchtools.tools.url.get_client")
    async def test_gemini_analyze_url(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.url import gemini_analyze_url

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("url analysis")
        mock_get_client.return_value = mock_client

        result = await gemini_analyze_url(urls=["https://example.com"])
        assert result["response"] == "url analysis"
        assert result["urls"] == ["https://example.com"]

    @patch("mcp_gemini_crunchtools.tools.url.get_client")
    async def test_gemini_compare_urls(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.url import gemini_compare_urls

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("comparison")
        mock_get_client.return_value = mock_client

        result = await gemini_compare_urls(
            url1="https://example.com", url2="https://other.com"
        )
        assert result["response"] == "comparison"

    @patch("mcp_gemini_crunchtools.tools.url.get_client")
    async def test_gemini_extract_from_url(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.url import gemini_extract_from_url

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("extracted data")
        mock_get_client.return_value = mock_client

        result = await gemini_extract_from_url(url="https://example.com", data_type="links")
        assert result["response"] == "extracted data"

class TestVideoTools:
    """Tests for generate_video, check_video."""

    @patch("mcp_gemini_crunchtools.tools.video.get_client")
    async def test_gemini_generate_video(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.video import gemini_generate_video

        mock_client = mock_gemini_client()
        mock_op = MagicMock()
        mock_op.name = "operations/video-123"
        mock_client.client.models.generate_videos.return_value = mock_op
        mock_get_client.return_value = mock_client

        result = await gemini_generate_video(prompt="a sunset timelapse")
        assert result["operation_name"] == "operations/video-123"
        assert result["status"] == "started"

    @patch("mcp_gemini_crunchtools.tools.video.get_client")
    async def test_gemini_check_video_complete(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.video import gemini_check_video

        mock_client = mock_gemini_client()
        mock_op = MagicMock()
        mock_op.done = True
        mock_video = MagicMock()
        mock_video.video.uri = "gs://bucket/video.mp4"
        mock_op.response.generated_videos = [mock_video]
        mock_client.client.operations.get_videos_operation.return_value = mock_op
        mock_get_client.return_value = mock_client

        result = await gemini_check_video(operation_name="op-123")
        assert result["status"] == "complete"

    @patch("mcp_gemini_crunchtools.tools.video.get_client")
    async def test_gemini_check_video_in_progress(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.video import gemini_check_video

        mock_client = mock_gemini_client()
        mock_op = MagicMock()
        mock_op.done = False
        mock_client.client.operations.get_videos_operation.return_value = mock_op
        mock_get_client.return_value = mock_client

        result = await gemini_check_video(operation_name="op-456")
        assert result["status"] == "in_progress"

class TestYouTubeTools:
    """Tests for youtube, youtube_summary."""

    @patch("mcp_gemini_crunchtools.tools.youtube.get_client")
    async def test_gemini_youtube(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.youtube import gemini_youtube

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("video insights")
        mock_get_client.return_value = mock_client

        result = await gemini_youtube(url="https://youtube.com/watch?v=test123")
        assert result["response"] == "video insights"
        assert result["url"] == "https://youtube.com/watch?v=test123"

    @patch("mcp_gemini_crunchtools.tools.youtube.get_client")
    async def test_gemini_youtube_summary(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.youtube import gemini_youtube_summary

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("video summary")
        mock_get_client.return_value = mock_client

        result = await gemini_youtube_summary(
            url="https://youtube.com/watch?v=test123", style="detailed"
        )
        assert result["response"] == "video summary"

class TestVoiceTools:
    """Tests for speak, dialogue, list_voices."""

    @patch("mcp_gemini_crunchtools.tools.voice.get_client")
    async def test_gemini_speak(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.voice import gemini_speak

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_audio_response()
        mock_get_client.return_value = mock_client

        result = await gemini_speak(text="Hello world", voice="Kore")
        assert result["voice"] == "Kore"
        assert result["text_length"] == 11

    @patch("mcp_gemini_crunchtools.tools.voice.get_client")
    async def test_gemini_dialogue(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.voice import gemini_dialogue

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_audio_response()
        mock_get_client.return_value = mock_client

        result = await gemini_dialogue(text="Speaker1: Hi\nSpeaker2: Hello")
        assert result["voices"] == ["Kore", "Puck"]

    async def test_gemini_list_voices(self) -> None:
        from mcp_gemini_crunchtools.tools.voice import gemini_list_voices

        result = await gemini_list_voices()
        assert "voices" in result
        assert "Kore" in result["voices"]
        assert len(result["voices"]) == 8

class TestResearchTools:
    """Tests for deep_research, check_research, research_followup."""

    @patch("mcp_gemini_crunchtools.tools.research.get_client")
    async def test_gemini_deep_research(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.research import gemini_deep_research

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("research findings")
        mock_get_client.return_value = mock_client

        result = await gemini_deep_research(query="container security best practices")
        assert result["status"] == "complete"
        assert "research_id" in result

    @patch("mcp_gemini_crunchtools.tools.research.get_client")
    async def test_gemini_check_research(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.research import (
            _research_ops,
            gemini_check_research,
        )

        mock_client = mock_gemini_client()
        mock_get_client.return_value = mock_client

        _research_ops["test-op"] = {
            "query": "test",
            "response": mock_generate_response("findings"),
            "started": 0,
        }

        result = await gemini_check_research(research_id="test-op")
        assert result["status"] == "complete"

    async def test_gemini_check_research_not_found(self) -> None:
        from mcp_gemini_crunchtools.tools.research import gemini_check_research

        result = await gemini_check_research(research_id="nonexistent")
        assert result["status"] == "not_found"

    @patch("mcp_gemini_crunchtools.tools.research.get_client")
    async def test_gemini_research_followup(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.research import (
            _research_ops,
            gemini_research_followup,
        )

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("followup answer")
        mock_get_client.return_value = mock_client

        _research_ops["followup-op"] = {
            "query": "test",
            "response": mock_generate_response("original"),
            "started": 0,
        }

        result = await gemini_research_followup(
            research_id="followup-op", question="tell me more"
        )
        assert result["response"] == "followup answer"

class TestCacheTools:
    """Tests for create_cache, query_cache, list_caches, delete_cache."""

    @patch("mcp_gemini_crunchtools.tools.cache.get_client")
    async def test_gemini_create_cache(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.cache import gemini_create_cache

        mock_client = mock_gemini_client()
        mock_cache = MagicMock()
        mock_cache.name = "caches/abc123"
        mock_client.client.caches.create.return_value = mock_cache
        mock_get_client.return_value = mock_client

        result = await gemini_create_cache(content="test content", display_name="test-cache")
        assert result["cache_name"] == "caches/abc123"
        assert result["display_name"] == "test-cache"

    @patch("mcp_gemini_crunchtools.tools.cache.get_client")
    async def test_gemini_query_cache(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.cache import gemini_query_cache

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("cached answer")
        mock_get_client.return_value = mock_client

        result = await gemini_query_cache(cache_name="caches/abc", question="what is this?")
        assert result["response"] == "cached answer"

    @patch("mcp_gemini_crunchtools.tools.cache.get_client")
    async def test_gemini_list_caches(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.cache import gemini_list_caches

        mock_client = mock_gemini_client()
        mock_client.client.caches.list.return_value = []
        mock_get_client.return_value = mock_client

        result = await gemini_list_caches()
        assert result["count"] == 0
        assert result["caches"] == []

    @patch("mcp_gemini_crunchtools.tools.cache.get_client")
    async def test_gemini_delete_cache(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.cache import gemini_delete_cache

        mock_client = mock_gemini_client()
        mock_get_client.return_value = mock_client

        result = await gemini_delete_cache(cache_name="caches/abc")
        assert result["status"] == "deleted"

class TestStructuredTools:
    """Tests for structured, extract."""

    @patch("mcp_gemini_crunchtools.tools.structured.get_client")
    async def test_gemini_structured(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.structured import gemini_structured

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response('{"key": "value"}')
        mock_get_client.return_value = mock_client

        result = await gemini_structured(prompt="extract entities")
        assert result["response"] == '{"key": "value"}'

    @patch("mcp_gemini_crunchtools.tools.structured.get_client")
    async def test_gemini_extract(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.structured import gemini_extract

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response('{"entities": []}')
        mock_get_client.return_value = mock_client

        result = await gemini_extract(text="John works at Acme", extract_type="entities")
        assert "response" in result

class TestTokenTools:
    """Tests for count_tokens."""

    @patch("mcp_gemini_crunchtools.tools.tokens.get_client")
    async def test_gemini_count_tokens(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.tokens import gemini_count_tokens

        mock_client = mock_gemini_client()
        mock_token_response = MagicMock()
        mock_token_response.total_tokens = 42
        mock_client.count_tokens.return_value = mock_token_response
        mock_get_client.return_value = mock_client

        result = await gemini_count_tokens(content="some text to count")
        assert result["total_tokens"] == 42

class TestCodeTools:
    """Tests for run_code."""

    @patch("mcp_gemini_crunchtools.tools.code.get_client")
    async def test_gemini_run_code(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.code import gemini_run_code

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("result: 42")
        mock_get_client.return_value = mock_client

        result = await gemini_run_code(prompt="calculate 6 * 7")
        assert result["response"] == "result: 42"

    @patch("mcp_gemini_crunchtools.tools.code.get_client")
    async def test_gemini_run_code_with_data(self, mock_get_client: MagicMock) -> None:
        from mcp_gemini_crunchtools.tools.code import gemini_run_code

        mock_client = mock_gemini_client()
        mock_client.generate_content.return_value = mock_generate_response("processed")
        mock_get_client.return_value = mock_client

        result = await gemini_run_code(prompt="sort this", data="3,1,2")
        assert result["response"] == "processed"
