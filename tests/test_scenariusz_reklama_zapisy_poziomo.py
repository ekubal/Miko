"""Wersja pozioma reklamy zapisów: te same ujęcia i kwestie, kadry 16:9 z kadrem pionowym jako wzorem."""

from types import SimpleNamespace

from generator import config
from generator.scenariusze import __main__ as cli
from generator.scenariusze import reklama_zapisy as pion
from generator.scenariusze import reklama_zapisy_poziomo as sc
from generator.scenariusze.__main__ import prompts_doc_path, render_markdown


def test_same_shots_and_lines_as_vertical_version():
    assert sc.SHOTS is pion.SHOTS and sc.KWESTIE is pion.KWESTIE
    assert sc.ASPECT == "16:9" and pion.ASPECT == "9:16"


def test_frames_are_horizontal_and_follow_production_rules():
    for key in sc.SHOTS:
        frame = sc.frame_prompt(key)
        assert "horizontal 16:9" in frame and "vertical 9:16" not in frame, key
        assert "No children" in frame and "no text" in frame.lower(), key
        assert "approved vertical version" in frame, key
        assert "approved vertical version" not in sc.frame_prompt(key, with_extra_references=False), key


def test_prompts_document_is_up_to_date_and_separate():
    # Po zmianie promptów: python -m generator.scenariusze -s reklama_zapisy_poziomo opis
    assert prompts_doc_path(sc) != prompts_doc_path(pion)
    assert prompts_doc_path(sc).read_text(encoding="utf-8") == render_markdown(sc)


def fake_generation(monkeypatch, tmp_path):
    calls = []

    def fake_generate_image(client, prompt, references, aspect_ratio, size):
        calls.append({"refs": list(references), "aspect": aspect_ratio, "prompt": prompt})
        return b"png", "image/png", None

    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(config, "SELECTED_DIR", tmp_path / "selected")
    monkeypatch.setattr("generator.common.google_client", lambda: object())
    monkeypatch.setattr("generator.images.generate_image", fake_generate_image)
    portrait = tmp_path / "selected" / "portrait.png"
    portrait.parent.mkdir(parents=True)
    portrait.write_bytes(b"portret")
    return calls, portrait


def test_vertical_frame_is_sent_as_last_reference(monkeypatch, tmp_path):
    calls, portrait = fake_generation(monkeypatch, tmp_path)
    vertical = sc.vertical_frame("w1_mowi")
    vertical.parent.mkdir(parents=True)
    vertical.write_bytes(b"pion")
    cli.cmd_kadry(sc, SimpleNamespace(only=["w1_mowi"], count=1, size="1K"))
    assert calls[0]["refs"] == [portrait, vertical] and calls[0]["aspect"] == "16:9"
    assert "approved vertical version" in calls[0]["prompt"]


def test_without_vertical_frame_prompt_does_not_mention_it(monkeypatch, tmp_path):
    calls, portrait = fake_generation(monkeypatch, tmp_path)
    cli.cmd_kadry(sc, SimpleNamespace(only=["w1_mowi"], count=1, size="1K"))
    assert calls[0]["refs"] == [portrait]
    assert "approved vertical version" not in calls[0]["prompt"]


def test_voice_lines_are_shared_with_vertical_version(monkeypatch, tmp_path):
    recorded = []
    monkeypatch.setattr(config, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("generator.audio.speak", lambda text, out: recorded.append(out))
    cli.cmd_kwestie(sc, SimpleNamespace(only=["w1_2"], force=False))
    assert recorded == [tmp_path / pion.NAME / "glos" / "w1_2.mp3"]
