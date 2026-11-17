"""Reklama zapisów (scenariusze/reklama_zapisy.md): zasady produkcji, kwestie i zgodność plików."""

import re
from types import SimpleNamespace

from generator import config
from generator.scenariusze import reklama_zapisy as sc
from generator.scenariusze import __main__ as cli
from generator.scenariusze.__main__ import prompts_doc_path, render_markdown

VARIANTS = ["W1", "W2", "W3"]
FORBIDDEN = ["sztuczn", " ai", "fikcyj", "aktor", "generowan", "przebrany"]


def variant_lines(variant: str) -> list[str]:
    return [line["tekst"] for key, line in sc.KWESTIE.items() if key.startswith(variant.lower())]


def test_every_shot_has_a_titled_scene_and_each_variant_exists():
    assert {s["scena"] for s in sc.SHOTS.values()} == set(sc.SCENE_TITLES)
    for variant in VARIANTS:
        assert variant_lines(variant), variant


def test_frames_are_vertical_and_follow_production_rules():
    for key, shot in sc.SHOTS.items():
        frame = sc.frame_prompt(key)
        assert "16:9" not in frame and "vertical 9:16" in frame, key
        assert "{" not in frame and "}" not in frame, key
        assert "No children" in frame and "no text" in frame.lower(), key
        if shot.get("wideo", True):
            assert "No dialogue" in sc.motion_prompt(key, shot.get("sekundy", 8)), key
        else:
            assert shot.get("heygen"), key


def test_character_flags_match_scene_text():
    for key, shot in sc.SHOTS.items():
        text = shot["scene"].lower()
        assert ("young reindeer" in text) == bool(shot.get("platek")), key
        # Słowo „elf” albo „elves” (nie „bookshelves”).
        assert bool(re.search(r"\belf\b|\belves\b", text)) == bool(shot.get("elves")), key
        if not shot.get("santa", True):
            assert "santa is not in this shot" in text, key
        if shot.get("platek"):
            assert sc.od_listu_do_san.PLATEK_DESCRIPTION in sc.frame_prompt(key), key


def test_lines_point_to_existing_shots():
    for key, line in sc.KWESTIE.items():
        for shot in line["ujecie"].split(", "):
            assert shot in sc.SHOTS, (key, shot)


def test_each_variant_explains_the_offer_and_asks_to_sign_up():
    for variant in VARIANTS:
        text = " ".join(variant_lines(variant))
        assert "dwudziestego piątego listopada" in text, variant
        assert "minus dwadzieścia pięć procent" in text, variant
        assert "po imieniu" in text and "księdze" in text, variant
        assert "Zapiszcie się" in text, variant


def test_lines_keep_santa_real_and_have_no_digits():
    for key, line in sc.KWESTIE.items():
        text = " " + line["tekst"].lower()
        for word in FORBIDDEN:
            assert word not in text, (key, word)
        # Głos czyta liczby słownie; cyfry bywają czytane źle.
        assert not re.search(r"\d", line["tekst"]), key


def test_scenario_document_contains_every_line():
    document = (config.ROOT / sc.DOC).read_text(encoding="utf-8")
    for key, line in sc.KWESTIE.items():
        assert line["tekst"] in document, key


def test_prompts_document_is_up_to_date():
    # Po zmianie promptów: python -m generator.scenariusze -s reklama_zapisy opis
    assert prompts_doc_path(sc).read_text(encoding="utf-8") == render_markdown(sc)


def test_generate_passes_reference_list_and_aspect(monkeypatch, tmp_path):
    # Regresja: generate_image zwraca (bajty, mime, koszt), a brak referencji to pusta lista.
    calls = []

    def fake_generate_image(client, prompt, references, aspect_ratio, size):
        calls.append((references, aspect_ratio))
        return b"png", "image/png", 0.1

    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("generator.common.google_client", lambda: object())
    monkeypatch.setattr("generator.images.generate_image", fake_generate_image)
    cli.generate(sc, "w1_elf", sc.frame_prompt("w1_elf"), "kadry", [], SimpleNamespace(count=1, size="1K"))
    assert calls == [([], "9:16")]
    assert (tmp_path / sc.NAME / "kadry" / "w1_elf_01.png").read_bytes() == b"png"
