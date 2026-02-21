"""Image generation tools including native Gemini and Imagen 4."""

from typing import Any

from google.genai import types
from PIL import Image

from .._image_utils import (
    extract_image_from_response,
    extract_text_from_response,
    save_generated_image,
)
from ..client import get_client
from ..errors import ImageGenerationError
from ..models import validate_file_exists


async def gemini_generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    style: str | None = None,
    use_google_search: bool = False,
) -> dict[str, Any]:
    """Generate an image from a text prompt using Gemini's native image model.

    Args:
        prompt: Description of the image to generate.
        aspect_ratio: Aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, etc).
        image_size: Output size (1K, 2K, 4K).
        style: Optional style modifier to append to the prompt.
        use_google_search: Ground the image with Google Search results.

    Returns:
        Path to the generated image and text description.
    """
    client = get_client()

    full_prompt = prompt
    if style:
        full_prompt = f"{prompt}. Style: {style}"

    config_kwargs: dict[str, Any] = {
        "response_modalities": ["TEXT", "IMAGE"],
    }

    if use_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    config = types.GenerateContentConfig(**config_kwargs)

    response = client.generate_content(
        model="gemini-2.5-flash-image",
        contents=[full_prompt],
        config=config,
    )

    image_data = extract_image_from_response(response)
    if image_data is None:
        raise ImageGenerationError("No image was generated. Try rephrasing your prompt.")

    output_path = save_generated_image(
        image_data[0], client.output_dir, prefix="gemini_gen",
    )
    text = extract_text_from_response(response)

    return {
        "image_path": str(output_path),
        "text": text,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
    }


async def gemini_generate_image_with_input(
    prompt: str,
    file_path: str,
    _aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    """Generate or edit an image using a local image file as input.

    Upload a local image and give Gemini instructions for how to modify it.
    Use cases: add watermarks, change styles, composite images, etc.

    Args:
        prompt: Instructions for what to do with the input image.
        file_path: Absolute path to a local image file.
        _aspect_ratio: Desired aspect ratio for the output (currently unused).

    Returns:
        Path to the generated image and text response.
    """
    file_path = validate_file_exists(file_path)
    client = get_client()

    input_image = Image.open(file_path)

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    )

    response = client.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, input_image],
        config=config,
    )

    image_data = extract_image_from_response(response)
    if image_data is None:
        raise ImageGenerationError(
            "No image was generated. Try rephrasing your prompt."
        )

    output_path = save_generated_image(
        image_data[0], client.output_dir, prefix="gemini_edit",
    )
    text = extract_text_from_response(response)

    return {
        "image_path": str(output_path),
        "text": text,
        "input_image": file_path,
        "prompt": prompt,
    }


async def gemini_image_prompt(
    description: str,
    style: str | None = None,
    mood: str | None = None,
    model: str = "flash",
) -> dict[str, Any]:
    """Help craft an effective image generation prompt.

    Args:
        description: What you want the image to show.
        style: Desired art style (photorealistic, cartoon, watercolor, etc).
        mood: Desired mood or atmosphere.
        model: Model to use for prompt crafting.

    Returns:
        A crafted image prompt ready to use.
    """
    from .query import _resolve_model

    client = get_client()
    model_name = _resolve_model(model)

    prompt = (
        "You are an expert at crafting image generation prompts. "
        "Create a detailed, effective prompt for generating an image based on:\n\n"
        f"Description: {description}"
    )
    if style:
        prompt += f"\nStyle: {style}"
    if mood:
        prompt += f"\nMood: {mood}"
    prompt += (
        "\n\nProvide a single, detailed prompt that would produce a high-quality image. "
        "Include details about composition, lighting, colors, and style."
    )

    response = client.generate_content(model=model_name, contents=[prompt])
    return {"prompt": response.text, "model": model_name}


async def gemini_imagen_generate(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
    number_of_images: int = 1,
    aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    """Generate images using Google Imagen 4 models.

    Dedicated high-quality image generation. Models:
    - imagen-4.0-generate-001 (standard, $0.04/image)
    - imagen-4.0-ultra-generate-001 (highest quality, $0.06/image)
    - imagen-4.0-fast-generate-001 (fastest, $0.02/image)

    Args:
        prompt: Description of the image to generate.
        model: Imagen model to use.
        number_of_images: Number of images to generate (1-4).
        aspect_ratio: Aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9).

    Returns:
        Paths to generated images.
    """
    client = get_client()

    config = types.GenerateImagesConfig(
        number_of_images=number_of_images,
        aspect_ratio=aspect_ratio,
    )

    response = client.generate_images(
        model=model, prompt=prompt, config=config,
    )

    saved_paths: list[str] = []
    if response and response.generated_images:
        for i, generated_image in enumerate(response.generated_images):
            path = save_generated_image(
                generated_image.image.image_bytes,
                client.output_dir,
                prefix=f"imagen4_{i}",
            )
            saved_paths.append(str(path))

    return {
        "image_paths": saved_paths,
        "model": model,
        "count": len(saved_paths),
        "prompt": prompt,
    }
