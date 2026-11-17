"""Reklama zapisów w wersji poziomej 16:9 (YouTube, strona zapisów, reklamy w filmach).

Te same ujęcia, kwestie, HeyGen i montaż co wersja pionowa (reklama_zapisy.py), tylko w poziomie.
Jeśli kadr pionowy ujęcia jest już zatwierdzony (output/reklama_zapisy/wybrane/<klucz>.png), idzie
jako ostatni obraz wzorcowy: wersja pozioma ma wtedy to samo światło, rekwizyty i pozę Mikołaja,
a model tylko rozszerza scenę na boki. Głos Mikołaja jest wspólny (output/reklama_zapisy/glos/).
"""

from __future__ import annotations

from pathlib import Path

from .. import config
from . import reklama_zapisy as pion

NAME = "reklama_zapisy_poziomo"
TITLE = "Reklama zapisów: Mikołaj mówi do rodziców (wersja pozioma 16:9)"
DOC = pion.DOC
PROMPTY = "scenariusze/reklama_zapisy_poziomo_prompty.md"
ASPECT = "16:9"

PLATEK_FROM = pion.PLATEK_FROM
# Kwestie nagrywamy raz: polecenie `kwestie` zapisuje je do output/reklama_zapisy/glos/.
GLOS_FROM = pion.NAME

SCENE_TITLES = pion.SCENE_TITLES
SHOTS = pion.SHOTS
KWESTIE = pion.KWESTIE
CHARACTERS: dict[str, dict] = {}
TEMPLATES: dict[str, dict] = {}
REUSED_TEMPLATES: dict[str, int] = {}

HORIZONTAL = (
    "wide horizontal 16:9 frame, the main subject slightly off-center, with calm, simple space "
    "on one side and in the bottom fifth of the frame"
)

VERTICAL_REFERENCE_NOTE = """\
The last attached image is the approved vertical version of this exact shot. Keep the same
setting, props, lighting, colors and mood{santa}, and recompose it as a wide horizontal frame,
extending the scene naturally to the left and right instead of stretching or cropping it."""


def vertical_frame(key: str) -> Path:
    """Zatwierdzony kadr pionowy tego samego ujęcia."""
    return config.OUTPUT_DIR / pion.NAME / "wybrane" / f"{key}.png"


def extra_references(key: str) -> list[Path]:
    """Dodatkowe obrazy wzorcowe po portretach: kadr pionowy, jeśli jest zatwierdzony."""
    path = vertical_frame(key)
    return [path] if path.exists() else []


def frame_prompt(key: str, with_platek_reference: bool = True, with_extra_references: bool = True) -> str:
    """Prompt kadru poziomego (Nano Banana Pro); with_extra_references: wysyłamy kadr pionowy."""
    prompt = pion.build_frame_prompt(key, HORIZONTAL, with_platek_reference)
    if with_extra_references:
        santa = ", and Santa's pose, gestures and expression" if SHOTS[key].get("santa", True) else ""
        prompt += "\n" + VERTICAL_REFERENCE_NOTE.format(santa=santa)
    return prompt


motion_prompt = pion.motion_prompt
needs_santa_reference = pion.needs_santa_reference
video_shots = pion.video_shots
new_frame_shots = pion.new_frame_shots
