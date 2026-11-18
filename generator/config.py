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

# Cennik Nano Banana Pro (gemini-3-pro-image-preview) w USD za 1 mln tokenów, stan XI 2026
# (ai.google.dev/gemini-api/docs/pricing). Służy tylko do podglądu kosztu; prawdziwe
# rozliczenie jest w Google Cloud Billing. Przy zmianie modelu nadpisz zmiennymi.
IMAGE_PRICE_INPUT = float(os.environ.get("MIKOLAJ_IMAGE_PRICE_INPUT", "2.0"))  # prompt i referencje
IMAGE_PRICE_OUTPUT_IMAGE = float(os.environ.get("MIKOLAJ_IMAGE_PRICE_OUTPUT_IMAGE", "120.0"))
IMAGE_PRICE_OUTPUT_TEXT = float(os.environ.get("MIKOLAJ_IMAGE_PRICE_OUTPUT_TEXT", "12.0"))  # tekst i myślenie
# Tokeny do szacunku przed wysłaniem (--na-sucho): obraz wynikowy wg rozmiaru i jedna referencja.
IMAGE_OUTPUT_TOKENS = {"1K": 1120, "2K": 1120, "4K": 2000}
IMAGE_INPUT_TOKENS_PER_REFERENCE = 560

# ElevenLabs.
ELEVEN_API_URL = os.environ.get("ELEVENLABS_API_URL", "https://api.elevenlabs.io")
# Eleven v4 (wrzesień 2026): najnowszy model mowy; obsługuje polski i wskazówki w nawiasach ([pause]…).
ELEVEN_TTS_MODEL = os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_v4")
ELEVEN_VOICE_DESIGN_MODEL = os.environ.get("ELEVENLABS_VOICE_DESIGN_MODEL", "eleven_ttv_v3")
ELEVEN_OUTPUT_FORMAT = os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")
# Zestaw ustawień głosu (model, stabilność, tempo…) z generator/audio.py PRESETS; porównanie: `audio probki`.
ELEVEN_PRESET = os.environ.get("ELEVENLABS_PRESET", "v4")
# Model zamiany głosu (speech-to-speech): nagranie człowieka czytane głosem Mikołaja.
ELEVEN_STS_MODEL = os.environ.get("ELEVENLABS_STS_MODEL", "eleven_multilingual_sts_v2")


def require_env(*names: str) -> str:
    """Zwraca pierwszą ustawioną zmienną z listy albo kończy program z czytelnym błędem."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    sys.exit(f"Brak klucza API: ustaw {' lub '.join(names)} w pliku .env albo w środowisku.")
