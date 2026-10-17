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

# Google (Gemini API): Nano Banana Pro, Veo 3.1, model tekstowy.
IMAGE_MODEL = os.environ.get("MIKOLAJ_IMAGE_MODEL", "gemini-3-pro-image-preview")
VIDEO_MODEL_FAST = os.environ.get("MIKOLAJ_VIDEO_MODEL_FAST", "veo-3.1-fast-generate-preview")
VIDEO_MODEL_QUALITY = os.environ.get("MIKOLAJ_VIDEO_MODEL_QUALITY", "veo-3.1-generate-preview")
TEXT_MODEL = os.environ.get("MIKOLAJ_TEXT_MODEL", "gemini-2.5-flash")

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
