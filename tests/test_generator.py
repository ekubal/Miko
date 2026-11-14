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
    for key, scene in prompts.SCENES.items():
        assert "{" not in prompts.scene_prompt(key), key
        assert "{" not in prompts.motion_prompt(scene["motion"], 8, scene.get("camera")), key


def test_scene_prompts_keep_image_rules():
    for key in prompts.SCENES:
        prompt = prompts.scene_prompt(key)
        assert "No children appear in the image" in prompt, key
        assert "no text, no letters" in prompt, key
        if "portrait" in prompts.scene_references(key):
            assert "mouth stays covered by hair" in prompt, key


def test_templates_have_no_text():
    for key, template in prompts.TEMPLATES.items():
        assert "No text, no letters" in template, key


def test_scene_references_default_to_santa_portrait():
    assert prompts.scene_references("dom") == ["portrait"]
    assert prompts.scene_prompt("dom") == prompts.SCENE_PROMPT.format(scene=prompts.SCENES["dom"]["scene"])
    assert prompts.scene_references("koperta") == []
    assert "attached image" not in prompts.scene_prompt("koperta")


def test_scene_prompt_numbers_references_in_order():
    prompt = prompts.scene_prompt("stajnia")
    assert prompts.scene_references("stajnia") == ["portrait", "platek"]
    assert "Santa: attached image 1" in prompt
    assert "attached image 2 is his reference" in prompt
    assert "snowflake-shaped" in prompt


def test_scenes_with_platek_mention_him():
    for key in prompts.SCENES:
        mentions = "Płatek" in prompts.SCENES[key]["scene"]
        assert mentions == ("platek" in prompts.scene_references(key)), key


def test_scene_camera_override():
    assert "push-in" in prompts.scene_motion_prompt("zorza", 8)
    kula = prompts.scene_motion_prompt("kula", 8)
    assert "Static camera" in kula and "push-in." not in kula.replace("no push-in", "")


def test_voice_sample_text_fits_voice_design_limits():
    assert 100 <= len(prompts.VOICE_SAMPLE_TEXT) <= 1000


def test_general_lines_have_both_variants():
    for lines in prompts.GENERAL_LINES.values():
        assert lines["single"] and lines["plural"]
        # Kwestia zwracająca się do jednego dziecka musi mieć inną wersję dla rodzeństwa.
        if any(word in lines["single"] for word in ("ciebie", "Twoje", "Spójrz", "Witaj ", "Słuchaj", "Popatrz")):
            assert lines["single"] != lines["plural"]


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


def test_variant_paths_count_other_extensions(tmp_path):
    # Nano Banana Pro potrafi zwrócić JPEG; kolejny wariant nie może go nadpisać.
    (tmp_path / "dom_01.jpg").write_bytes(b"x")
    (tmp_path / "dom_fast_05.mp4").write_bytes(b"x")
    paths = common.variant_paths(tmp_path, "dom", ".png", 1)
    assert [p.name for p in paths] == ["dom_02.png"]


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

    def fake_generate(client, prompt, references, aspect, size):
        seen.append(([r.read_bytes() for r in references], prompt))
        return b"IMG", "image/png"

    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", fake_generate)
    images.main(["scenes", "-n", "1", "--only", "dom", "sanie"])
    assert [refs for refs, _ in seen] == [[b"REF"], [b"REF"]]
    assert "sleigh" in seen[1][1]


def test_scenes_send_santa_and_platek_references_in_order(tmp_output, monkeypatch):
    (tmp_output / "selected").mkdir()
    (tmp_output / "selected" / "portrait.png").write_bytes(b"SANTA")
    (tmp_output / "selected" / "platek.png").write_bytes(b"PLATEK")
    seen = {}

    def fake_generate(client, prompt, references, aspect, size):
        seen[prompt] = [r.read_bytes() for r in references]
        return b"IMG", "image/png"

    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", fake_generate)
    images.main(["scenes", "-n", "1", "--only", "zaprzeg", "worek", "koperta"])
    assert seen[prompts.scene_prompt("zaprzeg")] == [b"SANTA", b"PLATEK"]
    assert seen[prompts.scene_prompt("worek")] == [b"PLATEK"]
    assert seen[prompts.scene_prompt("koperta")] == []
    assert (tmp_output / "images" / "scenes" / "zaprzeg_01.png").exists()


def test_scenes_with_platek_exit_without_his_portrait(tmp_output, monkeypatch, capsys):
    (tmp_output / "selected").mkdir()
    (tmp_output / "selected" / "portrait.png").write_bytes(b"SANTA")
    monkeypatch.setattr(images, "generate_image", lambda *a: pytest.fail("nie powinno generować"))
    with pytest.raises(SystemExit) as exc:
        images.main(["scenes", "--only", "kula", "stajnia"])
    assert "platek" in str(exc.value)


def test_platek_portrait_and_select(tmp_output, monkeypatch):
    seen = []
    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(
        images, "generate_image", lambda c, prompt, refs, *a: seen.append((prompt, refs)) or (b"IMG", "image/png")
    )
    images.main(["platek", "-n", "1"])
    assert seen == [(prompts.PLATEK_PORTRAIT_PROMPT, [])]
    images.main(["select", "platek", "1"])
    assert (tmp_output / "selected" / "platek.png").read_bytes() == b"IMG"


def test_templates_generate_each_new_template(tmp_output, monkeypatch):
    seen = []
    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", lambda c, prompt, refs, *a: seen.append(prompt) or (b"IMG", "image/png"))
    images.main(["templates", "-n", "1"])
    assert seen == list(prompts.TEMPLATES.values())
    assert sorted(p.name for p in (tmp_output / "images" / "templates").iterdir()) == sorted(
        f"{key}_01.png" for key in prompts.TEMPLATES
    )


def test_scenes_without_portrait_exit(tmp_output):
    with pytest.raises(SystemExit):
        images.main(["scenes"])


def test_generate_image_extracts_inline_data(monkeypatch):
    part = SimpleNamespace(inline_data=SimpleNamespace(data=b"IMG", mime_type="image/png"))
    response = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: response))
    assert images.generate_image(client, "prompt", [], "16:9", "2K") == (b"IMG", "image/png")


def test_lines_records_single_and_plural(tmp_output, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice123")
    calls = []
    monkeypatch.setattr(
        audio.elevenlabs, "text_to_speech", lambda text, vid, s: calls.append((text, vid)) or b"MP3"
    )
    audio.main(["lines", "--only", "lista"])
    files = sorted(p.name for p in (tmp_output / "audio" / "lines").iterdir())
    assert files == ["lista.mp3", "lista_rodzenstwo.mp3"]
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


def test_with_retry_stops_at_once_on_free_tier_quota(monkeypatch):
    monkeypatch.setattr(common.time, "sleep", lambda s: None)
    calls = []

    def fail():
        calls.append(1)
        raise RuntimeError(
            "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: "
            "generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0"
        )

    with pytest.raises(SystemExit, match="Free Tier"):
        common.with_retry(fail)
    assert len(calls) == 1


def test_with_retry_retries_transient_errors(monkeypatch):
    monkeypatch.setattr(common.time, "sleep", lambda s: None)
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("503 UNAVAILABLE")
        return "ok"

    assert common.with_retry(flaky) == "ok"
    assert len(calls) == 3


def test_portrait_variant_full_beard_uses_its_prompt(tmp_output, monkeypatch):
    seen = []
    monkeypatch.setattr(images, "google_client", lambda: object())
    monkeypatch.setattr(images, "generate_image", lambda c, prompt, *a: seen.append(prompt) or (b"IMG", "image/png"))
    images.main(["portrait", "-n", "1", "--wariant", "pelna-broda"])
    assert seen == [prompts.PORTRAIT_PROMPT_FULL_BEARD]
    assert "Santa hat" in seen[0] and "mustache" in seen[0] and "{" not in seen[0]


def test_elves_description_added_only_to_scenes_with_elves():
    assert prompts.ELVES_DESCRIPTION in prompts.scene_prompt("pracownia")
    assert prompts.ELVES_DESCRIPTION in prompts.scene_prompt("listy")
    assert prompts.ELVES_DESCRIPTION not in prompts.scene_prompt("renifery")
    for key, scene in prompts.SCENES.items():
        mentions_elves = "elves" in scene["scene"].lower()
        assert mentions_elves == bool(scene.get("elves")), key


def test_videos_generate_uses_first_frame_and_saves_clip(tmp_output, monkeypatch):
    from generator import videos

    monkeypatch.setattr(config, "VIDEOS_DIR", tmp_output / "videos")
    (tmp_output / "selected").mkdir()
    (tmp_output / "selected" / "zorza.png").write_bytes(b"FRAME")
    calls = {}

    class Files:
        def upload(self, file):
            calls["uploaded"] = Path(file).read_bytes()
            return SimpleNamespace(name="files/abc", uri="https://x/files/abc", mime_type="image/png",
                                   state=SimpleNamespace(name="ACTIVE"))

        def download(self, file):
            calls["downloaded"] = file
            return b"MP4"

    class Interactions:
        def create(self, **kw):
            calls["create"] = kw
            return SimpleNamespace(output_video=SimpleNamespace(uri="https://x/files/out"))

    client = SimpleNamespace(files=Files(), interactions=Interactions())
    monkeypatch.setattr(videos, "google_client", lambda: client)
    videos.main(["generate", "--only", "zorza", "--resolution", "360p"])

    assert calls["uploaded"] == b"FRAME"
    kw = calls["create"]
    assert kw["model"] == config.VIDEO_MODEL
    assert kw["input"][0]["uri"] == "https://x/files/abc"
    assert kw["input"][1]["text"].startswith("<FIRST_FRAME> In a single continuous shot")
    assert kw["response_format"]["resolution"] == "360p" and kw["response_format"]["duration"] == "8s"
    assert (tmp_output / "videos" / "zorza_01.mp4").read_bytes() == b"MP4"

    videos.main(["select", "zorza", "1"])
    assert (tmp_output / "selected" / "zorza.mp4").read_bytes() == b"MP4"


def test_with_retry_stops_at_once_on_missing_model(monkeypatch):
    monkeypatch.setattr(common.time, "sleep", lambda s: None)

    def fail():
        raise RuntimeError("404 NOT_FOUND. This model models/veo-3.1-fast-generate-preview is no longer available.")

    with pytest.raises(SystemExit, match="MIKOLAJ_VIDEO_MODEL"):
        common.with_retry(fail)
