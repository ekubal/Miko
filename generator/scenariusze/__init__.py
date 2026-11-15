"""Prompty scenariuszy długiej wersji filmu: jeden moduł na scenariusz.

Wersja krótka korzysta z generator/prompts.py (SCENES, TEMPLATES). Długie scenariusze mają
własne ujęcia, postacie i szablony w tym katalogu, a obsługuje je polecenie:

    python -m generator.scenariusze --help
"""

from . import od_listu_do_san

SCENARIUSZE = {od_listu_do_san.NAME: od_listu_do_san}


def get(name: str):
    return SCENARIUSZE[name]
