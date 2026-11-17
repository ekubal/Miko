"""Cienki klient REST ElevenLabs: Voice Design, zapis głosu, TTS, zamiana głosu (STS) i muzyka."""

import json
import mimetypes
import os
import sys
from pathlib import Path

import requests

from . import config

TIMEOUT = 300


def _headers() -> dict:
    return {"xi-api-key": config.require_env("ELEVENLABS_API_KEY"), "Content-Type": "application/json"}


def _post(path: str, payload: dict, params: dict | None = None) -> requests.Response:
    response = requests.post(
        f"{config.ELEVEN_API_URL}{path}", headers=_headers(), json=payload, params=params, timeout=TIMEOUT
    )
    if not response.ok:
        raise RuntimeError(f"ElevenLabs {path}: HTTP {response.status_code}: {response.text[:500]}")
    return response


def _post_form(path: str, data: dict, files: dict, params: dict | None = None) -> requests.Response:
    # Wysyłka pliku (multipart): bez nagłówka JSON, requests sam ustawia granice formularza.
    headers = {"xi-api-key": config.require_env("ELEVENLABS_API_KEY")}
    response = requests.post(
        f"{config.ELEVEN_API_URL}{path}", headers=headers, data=data, files=files, params=params, timeout=TIMEOUT
    )
    if not response.ok:
        raise RuntimeError(f"ElevenLabs {path}: HTTP {response.status_code}: {response.text[:500]}")
    return response


def design_voice(description: str, sample_text: str) -> list[dict]:
    """Zwraca listę podglądów: {generated_voice_id, audio_base_64, ...}."""
    payload = {"voice_description": description, "model_id": config.ELEVEN_VOICE_DESIGN_MODEL, "text": sample_text}
    return _post("/v1/text-to-voice/design", payload).json()["previews"]


def create_voice(name: str, description: str, generated_voice_id: str) -> str:
    payload = {"voice_name": name, "voice_description": description, "generated_voice_id": generated_voice_id}
    return _post("/v1/text-to-voice", payload).json()["voice_id"]


def text_to_speech(text: str, voice_id: str, settings: dict, model: str | None = None,
                   language_code: str | None = None) -> bytes:
    """Tekst na mowę. language_code (np. "pl") wymusza język; obsługują go tylko niektóre modele."""
    payload = {"text": text, "model_id": model or config.ELEVEN_TTS_MODEL, "voice_settings": settings}
    if language_code:
        payload["language_code"] = language_code
    return _post(
        f"/v1/text-to-speech/{voice_id}", payload, params={"output_format": config.ELEVEN_OUTPUT_FORMAT}
    ).content


def speech_to_speech(audio: Path, voice_id: str, settings: dict, model: str,
                     remove_background_noise: bool = False) -> bytes:
    """Zamiana głosu: nagranie człowieka -> ten sam tekst i intonacja, głosem `voice_id`."""
    mime = mimetypes.guess_type(audio.name)[0] or "audio/mpeg"
    data = {
        "model_id": model,
        "voice_settings": json.dumps(settings),
        "remove_background_noise": "true" if remove_background_noise else "false",
    }
    files = {"audio": (audio.name, audio.read_bytes(), mime)}
    return _post_form(
        f"/v1/speech-to-speech/{voice_id}", data, files, params={"output_format": config.ELEVEN_OUTPUT_FORMAT}
    ).content


def compose_music(prompt: str, length_ms: int) -> bytes:
    payload = {"prompt": prompt, "music_length_ms": length_ms, "force_instrumental": True}
    return _post("/v1/music", payload, params={"output_format": config.ELEVEN_OUTPUT_FORMAT}).content


def saved_voice_id() -> str:
    """Głos Mikołaja: ELEVENLABS_VOICE_ID albo id zapisane przez `audio save-voice`."""
    if os.environ.get("ELEVENLABS_VOICE_ID"):
        return os.environ["ELEVENLABS_VOICE_ID"]
    if config.VOICE_FILE.exists():
        return json.loads(config.VOICE_FILE.read_text(encoding="utf-8"))["voice_id"]
    sys.exit(
        "Brak głosu Mikołaja. Uruchom: python -m generator.audio design, "
        "potem: python -m generator.audio save-voice <generated_voice_id>, "
        "albo ustaw ELEVENLABS_VOICE_ID."
    )
