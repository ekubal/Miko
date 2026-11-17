"""Prompty scenariuszy długiej wersji filmu: jeden moduł na scenariusz.

Wersja krótka korzysta z generator/prompts.py (SCENES, TEMPLATES). Długie scenariusze mają
własne ujęcia, postacie i szablony w tym katalogu. Tu jest też film reklamowy zapisów
(reklama_zapisy_poziomo: 16:9, trzy warianty). Wszystkie obsługuje polecenie:

    python -m generator.scenariusze --help
"""

from . import od_listu_do_san, reklama_zapisy_poziomo

SCENARIUSZE = {module.NAME: module for module in (od_listu_do_san, reklama_zapisy_poziomo)}


def get(name: str):
    return SCENARIUSZE[name]
