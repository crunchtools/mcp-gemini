"""Video generation tools."""

from typing import Any

from ..client import get_client


async def gemini_generate_video(
    prompt: str,
    _aspect_ratio: str = "16:9",
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    """Generate a video using Veo.

    This starts an async video generation operation.
    Use gemini_check_video to poll for completion.

    Args:
        prompt: Description of the video to generate.
        _aspect_ratio: Video aspect ratio (currently unused).
        negative_prompt: What to avoid in the video.

    Returns:
        Operation name/ID for status checking.
    """
    client = get_client()

    full_prompt = prompt
    if negative_prompt:
        full_prompt = f"{prompt}. Avoid: {negative_prompt}"

    response = client.client.models.generate_videos(
        model="veo-2.0-generate-001",
        prompt=full_prompt,
    )

    return {
        "operation_name": response.name if response else None,
        "status": "started",
        "prompt": prompt,
    }


async def gemini_check_video(
    operation_name: str,
) -> dict[str, Any]:
    """Check the status of a video generation operation.

    Args:
        operation_name: The operation name from gemini_generate_video.

    Returns:
        Status and video details if complete.
    """
    client = get_client()

    operations: Any = client.client.operations
    operation = operations.get_videos_operation(name=operation_name)

    if operation.done:
        video_path = None
        if hasattr(operation, "response") and operation.response:
            generated_videos = operation.response.generated_videos
            if generated_videos:
                video = generated_videos[0].video
                if video and video.uri:
                    video_path = video.uri

        return {
            "operation_name": operation_name,
            "status": "complete",
            "video_uri": video_path,
        }

    return {
        "operation_name": operation_name,
        "status": "in_progress",
    }
