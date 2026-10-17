"""Testy offline: bez kluczy API i bez połączeń sieciowych."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from generator import audio, common, config, images, order, prompts

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

KASIA_TEXT = (
    "Ho, ho, ho! Kasiu, mam dla ciebie wspaniałe wieści! Moje elfy przez cały rok sprawdzały, "
    "jak sobie radzisz. I wiesz, co mi powiedziały? Że nauczyłaś się jeździć na rowerze bez "
    "bocznych kółek! To było bardzo odważne. Jestem z ciebie ogromnie dumny, Kasiu. Słyszałem "
    "też, że uwielbiasz dinozaury i pięknie rysujesz. Pewnie twoje dinozaury są groźniejsze niż "
    "moje renifery! Pamiętaj, że każdy rysunek zrobiony z uśmiechem sprawia mi wielką radość. "
    "Zapisałem też twoje marzenie o zestawie do rysowania z dinozaurami. Elfy już go starannie "
    "pakują. A teraz zajrzyjmy razem do mojej magicznej księgi!"
)


@pytest.fixture
def tmp_output(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "IMAGES_DIR", tmp_path / "images")
    monkeypatch.setattr(config, "SELECTED_DIR", tmp_path / "selected")
    monkeypatch.setattr(config, "AUDIO_DIR", tmp_path / "audio")
    monkeypatch.setattr(config, "ORDERS_DIR", tmp_path / "orders")
    return tmp_path


def test_scene_and_motion_prompts_have_no_placeholders_left():
    for scene in prompts.SCENES.values():
        assert "{" not in prompts.SCENE_PROMPT.format(scene=scene["scene"])
        assert "{" not in prompts.MOTION_PROMPT.format(motion=scene["motion"])


def test_voice_sample_text_fits_voice_design_limits():
    assert 100 <= len(prompts.VOICE_SAMPLE_TEXT) <= 1000


def test_general_lines_have_both_variants():
    for lines in prompts.GENERAL_LINES.values():
        assert lines["single"] and lines["plural"] and lines["single"] != lines["plural"]


def test_build_prompt_single_child():
    data = order.load_order(EXAMPLES / "zamowienie_jas.json")
    text = order.build_prompt(data)
    assert "Jasiu" in text and "chłopiec" in text
    assert "Czy prezent jest już kupiony: NIE" in text
    assert "90–110 słów" in text
    assert "{" not in text


def test_build_prompt_siblings():
    data = order.load_order(EXAMPLES / "zamowienie_zosia_antek.json")
    text = order.build_prompt(data)
    assert "Dziecko 1:" in text and "Dziecko 2:" in text
    assert "Zosiu" in text and "Antku" in text
    assert "110–130 słów" in text


def test_check_speech_accepts_example_from_mvp():
    data = order.load_order(EXAMPLES / "zamowienie_kasia.json")
    assert order.check_speech(KASIA_TEXT, data) == []


def test_check_speech_flags_problems():
    data = order.load_order(EXAMPLES / "zamowienie_jas.json")
    issues = order.check_speech("Ho, ho, ho! Elfy już go pakują.", data)
    assert any("słów" in i for i in issues)
    assert any("Jasiu" in i for i in issues)
    assert any("nie jest kupiony" in i for i in issues)
    assert order.check_speech(prompts.NEEDS_REVIEW, data)[0].startswith("Model zwrócił")


def test_apply_pronunciation():
    data = {"wymowa": {"Jessico": "Dzesiko"}}
    assert order.apply_pronunciation("Jessico, Jessico!", data) == "Dzesiko, Dzesiko!"


def test_variant_paths_continue_numbering(tmp_path):
    (tmp_path / "dom_01.png").write_bytes(b"x")
    (tmp_path / "dom_02.png").write_bytes(b"x")
    paths = common.variant_paths(tmp_path, "dom", ".png", 2)
    assert [p.name for p in paths] == ["dom_03.png", "dom_04.png"]


def test_portrait_and_select(tmp_output, monkeypatch):
    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", lambda *a, **k: (b"PNGDATA", "image/png"))
    images.main(["portrait", "-n", "2"])
    assert sorted(p.name for p in (tmp_output / "images" / "portrait").iterdir()) == [
        "portrait_01.png",
        "portrait_02.png",
    ]
    images.main(["select", "portrait", "2"])
    assert (tmp_output / "selected" / "portrait.png").read_bytes() == b"PNGDATA"


def test_scenes_use_selected_portrait_as_reference(tmp_output, monkeypatch):
    (tmp_output / "selected").mkdir()
    (tmp_output / "selected" / "portrait.png").write_bytes(b"REF")
    seen = []

    def fake_generate(client, prompt, reference, aspect, size):
        seen.append((reference.read_bytes(), prompt))
        return b"IMG", "image/png"

    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", fake_generate)
    images.main(["scenes", "-n", "1", "--only", "dom", "sanie"])
    assert [ref for ref, _ in seen] == [b"REF", b"REF"]
    assert "sleigh" in seen[1][1]


def test_scenes_without_portrait_exit(tmp_output):
    with pytest.raises(SystemExit):
        images.main(["scenes"])


def test_generate_image_extracts_inline_data(monkeypatch):
    part = SimpleNamespace(inline_data=SimpleNamespace(data=b"IMG", mime_type="image/png"))
    response = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: response))
    assert images.generate_image(client, "prompt", None, "16:9", "2K") == (b"IMG", "image/png")


def test_lines_records_single_and_plural(tmp_output, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice123")
    calls = []
    monkeypatch.setattr(
        audio.elevenlabs, "text_to_speech", lambda text, vid, s: calls.append((text, vid)) or b"MP3"
    )
    audio.main(["lines", "--only", "scena5_lista"])
    files = sorted(p.name for p in (tmp_output / "audio" / "lines").iterdir())
    assert files == ["scena5_lista.mp3", "scena5_lista_rodzenstwo.mp3"]
    assert {vid for _, vid in calls} == {"voice123"}
    assert any("Wasze imiona" in text for text, _ in calls)


def test_order_voice_requires_approval(tmp_output):
    with pytest.raises(SystemExit):
        order.main(["voice", str(EXAMPLES / "zamowienie_kasia.json")])


def test_order_voice_applies_pronunciation(tmp_output, tmp_path, monkeypatch):
    data = json.loads((EXAMPLES / "zamowienie_kasia.json").read_text(encoding="utf-8"))
    data["wymowa"] = {"Kasiu": "Kasju"}
    order_file = tmp_path / "order.json"
    order_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    directory = tmp_output / "orders" / data["id"]
    directory.mkdir(parents=True)
    (directory / "tekst.txt").write_text(KASIA_TEXT, encoding="utf-8")

    spoken = []
    monkeypatch.setattr(order, "speak", lambda text, out: spoken.append((text, out)))
    order.main(["voice", str(order_file), "--approved"])
    assert "Kasju" in spoken[0][0] and "Kasiu" not in spoken[0][0]
    assert spoken[0][1] == directory / "glos.mp3"
