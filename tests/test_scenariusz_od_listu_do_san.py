"""Prompty scenariusza 4 „Od listu do sań”: zasady produkcji i zgodność pliku z promptami."""

from generator import prompts
from generator.scenariusze import od_listu_do_san as sc
from generator.scenariusze.__main__ import prompts_doc_path, render_markdown


def test_every_scene_has_shots():
    assert {s["scena"] for s in sc.SHOTS.values()} == set(range(1, 12))


def test_reused_shots_exist_in_short_version():
    for key, shot in sc.SHOTS.items():
        if "reuse" in shot:
            assert shot["reuse"] in prompts.SCENES, key


def test_new_shots_are_complete():
    for key, shot in sc.SHOTS.items():
        if "reuse" in shot:
            continue
        assert shot.get("scene"), key
        if shot.get("wideo", True):
            assert shot.get("motion"), key


def test_prompts_follow_production_rules():
    for key in sc.SHOTS:
        frame = sc.frame_prompt(key)
        assert "{" not in frame and "}" not in frame, key
        assert "No children" in frame, key
        assert "no text" in frame.lower(), key
        if sc.SHOTS[key].get("wideo", True):
            motion = sc.motion_prompt(key, 8)
            assert "{" not in motion and "No dialogue" in motion, key
    for key, item in {**sc.CHARACTERS, **sc.TEMPLATES}.items():
        assert "no text" in item["prompt"].lower(), key


def test_character_and_elf_flags_match_scene_text():
    for key, shot in sc.SHOTS.items():
        if "reuse" in shot:
            continue
        text = shot["scene"].lower()
        assert ("young reindeer" in text) == bool(shot.get("platek")), key
        assert ("elves" in text or "elf " in text) == bool(shot.get("elves")), key
        if shot.get("santa", True):
            assert "reference character" in sc.frame_prompt(key), key
        else:
            assert "reference character" not in sc.frame_prompt(key), key
            assert "santa is not" in text or "santa does not" in text, key


def test_platek_is_not_a_famous_reindeer():
    assert "not red and does not glow" in sc.PLATEK_DESCRIPTION
    for key, shot in sc.SHOTS.items():
        if shot.get("platek"):
            assert sc.PLATEK_DESCRIPTION in sc.frame_prompt(key), key


def test_globe_shot_keeps_santa_in_frame():
    motion = sc.motion_prompt("kula", 8)
    assert "Static camera" in motion and "stays in the frame" in motion


def test_prompts_document_is_up_to_date():
    # Po zmianie promptów: python -m generator.scenariusze opis
    assert prompts_doc_path(sc).read_text(encoding="utf-8") == render_markdown(sc)
