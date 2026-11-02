"""Wspólne pomocniki: klient Google, ponawianie wywołań, nazwy plików wariantów."""

import re
import time
from pathlib import Path
from typing import Callable, TypeVar

from . import config

T = TypeVar("T")


def google_client():
    from google import genai

    return genai.Client(api_key=config.require_env("GEMINI_API_KEY", "GOOGLE_API_KEY"))


def permanent_error_hint(exc: Exception) -> str | None:
    """Podpowiedź dla błędów, których ponawianie nie naprawi, albo None dla przejściowych."""
    text = str(exc)
    if "RESOURCE_EXHAUSTED" in text and ("free_tier" in text or "limit: 0" in text):
        return (
            "Projekt Google jest na darmowym planie (Free Tier), na którym ten model ma limit 0.\n"
            "Włącz płatności dla projektu klucza w Google AI Studio (https://aistudio.google.com/apikey)\n"
            "i uruchom polecenie ponownie. Ten sam klucz zacznie działać po włączeniu płatności."
        )
    if "NOT_FOUND" in text and "model" in text.lower():
        return (
            "Model nie istnieje albo został wyłączony. Komunikat Google:\n"
            f"{text[:400]}\n"
            "Wpisz aktualną nazwę modelu w .env (MIKOLAJ_IMAGE_MODEL, MIKOLAJ_VIDEO_MODEL albo MIKOLAJ_TEXT_MODEL)."
        )
    if "API_KEY_INVALID" in text or "API key not valid" in text:
        return "Klucz API jest nieprawidłowy. Sprawdź GEMINI_API_KEY w pliku .env."
    return None


def with_retry(fn: Callable[[], T], attempts: int = 3, delay: float = 5.0) -> T:
    """Ponawia wywołanie API przy błędach przejściowych (limit, sieć), z rosnącym odstępem.

    Błędy, których ponawianie nie naprawi (brak płatności, zły klucz), kończą program
    od razu z podpowiedzią, zamiast powtarzać się przy każdym wariancie.
    """
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # SDK-i rzucają różne typy wyjątków
            hint = permanent_error_hint(exc)
            if hint:
                raise SystemExit(f"\nBłąd API, którego nie da się ponowić:\n{hint}") from exc
            if attempt == attempts:
                raise
            wait = delay * 2 ** (attempt - 1)
            print(f"  ! błąd ({exc}); ponawiam za {wait:.0f} s ({attempt}/{attempts})")
            time.sleep(wait)
    raise AssertionError("unreachable")


def variant_paths(directory: Path, stem: str, suffix: str, count: int) -> list[Path]:
    """Zwraca `count` kolejnych wolnych nazw: stem_01.png, stem_02.png, ...

    Numeracja jest kontynuowana, więc ponowne uruchomienie dokłada nowe warianty
    zamiast nadpisywać te, które już obejrzałeś. Liczą się pliki z dowolnym
    rozszerzeniem, bo model może zwrócić np. JPEG zamiast zamówionego PNG.
    """
    directory.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"{re.escape(stem)}_(\d+)\.[^.]+")
    existing = [int(m.group(1)) for p in directory.iterdir() if (m := pattern.fullmatch(p.name))]
    start = max(existing, default=0) + 1
    return [directory / f"{stem}_{n:02d}{suffix}" for n in range(start, start + count)]


def selected_path(name: str, suffix: str = ".png") -> Path:
    return config.SELECTED_DIR / f"{name}{suffix}"
