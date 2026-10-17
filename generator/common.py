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


def with_retry(fn: Callable[[], T], attempts: int = 3, delay: float = 5.0) -> T:
    """Ponawia wywołanie API przy błędach przejściowych (limit, sieć), z rosnącym odstępem."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # SDK-i rzucają różne typy wyjątków
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
