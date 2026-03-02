"""Voice and text-to-speech tools."""

import uuid
from datetime import datetime, timezone
from typing import Any

from google.genai import types

from ..client import get_client

AVAILABLE_VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir",
    "Leda", "Orus", "Aoede",
]


async def gemini_speak(
    text: str,
    voice: str = "Kore",
) -> dict[str, Any]:
    """Convert text to speech.

    Args:
        text: Text to convert to speech.
        voice: Voice name to use.

    Returns:
        Path to the generated audio file.
    """
    client = get_client()

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice,
                ),
            ),
        ),
    )

    response = client.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=[text],
        config=config,
    )

    audio_path = None
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
                unique_id = uuid.uuid4().hex[:8]
                filename = f"tts_{timestamp}_{unique_id}.wav"
                audio_path = client.output_dir / filename
                audio_path.write_bytes(part.inline_data.data)
                break

    return {
        "audio_path": str(audio_path) if audio_path else None,
        "voice": voice,
        "text_length": len(text),
    }


async def gemini_dialogue(
    text: str,
    voice1: str = "Kore",
    voice2: str = "Puck",
) -> dict[str, Any]:
    """Generate multi-voice dialogue audio.

    Args:
        text: Dialogue text with speaker labels.
        voice1: First voice name.
        voice2: Second voice name.

    Returns:
        Path to the generated audio file.
    """
    client = get_client()

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice1,
                            ),
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice2,
                            ),
                        ),
                    ),
                ],
            ),
        ),
    )

    response = client.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=[text],
        config=config,
    )

    audio_path = None
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
                unique_id = uuid.uuid4().hex[:8]
                filename = f"dialogue_{timestamp}_{unique_id}.wav"
                audio_path = client.output_dir / filename
                audio_path.write_bytes(part.inline_data.data)
                break

    return {
        "audio_path": str(audio_path) if audio_path else None,
        "voices": [voice1, voice2],
    }


async def gemini_list_voices() -> dict[str, Any]:
    """List available voices for text-to-speech.

    Returns:
        List of available voice names.
    """
    return {"voices": AVAILABLE_VOICES}
