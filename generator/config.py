"""Ścieżki, modele i klucze API. Wszystko da się nadpisać zmiennymi środowiskowymi lub plikiem .env."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Minimalny parser .env (KLUCZ=wartość), bez zewnętrznych zależności."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()

OUTPUT_DIR = Path(os.environ.get("MIKOLAJ_OUTPUT_DIR", ROOT / "output"))
IMAGES_DIR = OUTPUT_DIR / "images"
VIDEOS_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio"
ORDERS_DIR = OUTPUT_DIR / "orders"
# Wybrane (zatwierdzone przez człowieka) warianty: portrait.png, dom.png, ...
SELECTED_DIR = OUTPUT_DIR / "selected"
VOICE_FILE = OUTPUT_DIR / "voice.json"

# Google (Gemini API): Nano Banana Pro, Gemini Omni Flash (wideo), model tekstowy.
IMAGE_MODEL = os.environ.get("MIKOLAJ_IMAGE_MODEL", "gemini-3-pro-image-preview")
# Veo 3.1 w Gemini API wyłączono 22.10.2026; następca to Gemini Omni Flash.
VIDEO_MODEL = os.environ.get("MIKOLAJ_VIDEO_MODEL", "gemini-omni-1.1-flash")
TEXT_MODEL = os.environ.get("MIKOLAJ_TEXT_MODEL", "gemini-3.8-flash")

# ElevenLabs.
ELEVEN_API_URL = os.environ.get("ELEVENLABS_API_URL", "https://api.elevenlabs.io")
ELEVEN_TTS_MODEL = os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2")
ELEVEN_VOICE_DESIGN_MODEL = os.environ.get("ELEVENLABS_VOICE_DESIGN_MODEL", "eleven_multilingual_ttv_v2")
ELEVEN_OUTPUT_FORMAT = os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")


def require_env(*names: str) -> str:
    """Zwraca pierwszą ustawioną zmienną z listy albo kończy program z czytelnym błędem."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    sys.exit(f"Brak klucza API: ustaw {' lub '.join(names)} w pliku .env albo w środowisku.")
