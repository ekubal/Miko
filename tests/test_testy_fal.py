"""Testy skryptów testy_fal bez sieci: schematy modeli są sztuczne, kolejka fal podmieniona."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from testy_fal import cli, fal_api, mapowanie, porownanie, ujecia, zadania
from testy_fal.modele import MODELS


def openapi(name: str, properties: dict, required: list[str], extra: dict | None = None) -> dict:
    """Schemat w kształcie OpenAPI kolejki fal: POST z ciałem + ścieżki statusu."""
    schemas = {f"{name}Input": {"type": "object", "properties": properties, "required": required}}
    schemas.update(extra or {})
    return {
        "paths": {
            f"/vendor/{name}": {
                "post": {"requestBody": {"content": {"application/json": {
                    "schema": {"$ref": f"#/components/schemas/{name}Input"}}}}}
            },
            "/vendor/requests/{request_id}/status": {"get": {}},
        },
        "components": {"schemas": schemas},
    }


KLING_LIKE = openapi(
    "Kling",
    {
        "prompt": {"type": "string"},
        "start_image_url": {"type": "string"},
        "end_image_url": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "duration": {"allOf": [{"$ref": "#/components/schemas/Duration"}], "default": "5"},
        "negative_prompt": {"type": "string", "default": "blur"},
        "generate_audio": {"type": "boolean", "default": True},
    },
    ["prompt", "start_image_url"],
    {"Duration": {"type": "string", "enum": ["5", "10"]}},
)

MINIMAX_LIKE = openapi(
    "Minimax",
    {
        "prompt": {"type": "string"},
        "image_url": {"type": "string"},
        "duration": {"type": "integer", "minimum": 5, "maximum": 15, "default": 6},
        "resolution": {"type": "string", "enum": ["480P", "768P", "1080P"], "default": "768P"},
        "prompt_optimizer": {"type": "boolean", "default": True},
    },
    ["prompt", "image_url"],
)

REF_LIKE = openapi(
    "Ref",
    {
        "prompt": {"type": "string"},
        "image_urls": {"type": "array", "items": {"type": "string"}},
        "resolution": {"type": "string", "enum": ["480p", "720p"]},
        "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"]},
    },
    ["prompt", "image_urls"],
)


def wanted(**overrides) -> dict:
    base = {
        "prompt": "Santa nods. {seconds} seconds.",
        "image": "file:/kadr.png",
        "duration": 8,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "negative_prompt": mapowanie.NEGATIVE_PROMPT,
        "audio": False,
        "prompt_expansion": False,
    }
    base.update(overrides)
    return base


def build(schema, **kwargs):
    props, required, components = mapowanie.input_schema(schema)
    return mapowanie.build_payload(props, required, components, kwargs.pop("wanted", wanted()), **kwargs)


# --- mapowanie parametrów -------------------------------------------------------------------


def test_kling_like_schema_uses_start_image_and_nearest_duration():
    payload, notes, seconds = build(KLING_LIKE)
    assert payload["start_image_url"] == "file:/kadr.png"
    assert payload["duration"] == "10"  # 8 s: bliżej 10 niż 5
    assert seconds == 10
    assert payload["generate_audio"] is False
    assert payload["prompt"] == "Santa nods. 10 seconds."
    assert "resolution" not in payload
    assert any("rozdzielczość" in n for n in notes)
    assert any("8 -> 10" in n for n in notes)


def test_minimax_like_schema_maps_resolution_enum_and_integer_duration():
    payload, _notes, seconds = build(MINIMAX_LIKE)
    assert payload["image_url"] == "file:/kadr.png"
    assert payload["resolution"] == "1080P"
    assert payload["duration"] == 8 and seconds == 8
    assert payload["prompt_optimizer"] is False

    payload, notes, _ = build(MINIMAX_LIKE, wanted=wanted(resolution="720p", duration=20))
    assert payload["resolution"] == "768P"
    assert payload["duration"] == 15
    assert any("720p -> 768P" in n for n in notes)


def test_reference_schema_gets_list_of_images():
    payload, _notes, seconds = build(
        REF_LIKE, wanted=wanted(image=None, references=["file:/santa.png", "file:/elf.png"])
    )
    assert payload["image_urls"] == ["file:/santa.png", "file:/elf.png"]
    assert payload["resolution"] == "720p"
    assert payload["aspect_ratio"] == "16:9"
    assert seconds is None  # model bez pola długości


def test_missing_frame_field_is_an_error():
    schema = openapi("NoImage", {"prompt": {"type": "string"}}, ["prompt"])
    with pytest.raises(mapowanie.MappingError, match="kadr startowy"):
        build(schema)


def test_required_field_can_be_supplied_by_fixed():
    schema = openapi("Mode", {"prompt": {"type": "string"}, "image_url": {"type": "string"},
                              "mode": {"type": "string"}}, ["prompt", "image_url", "mode"])
    with pytest.raises(mapowanie.MappingError, match="mode"):
        build(schema)
    payload, _notes, _ = build(schema, fixed={"mode": "pro"})
    assert payload["mode"] == "pro"


def test_field_overrides_rename_and_disable():
    payload, _notes, _ = build(KLING_LIKE, overrides={"negative_prompt": None})
    assert "negative_prompt" not in payload
    schema = openapi("Odd", {"prompt": {"type": "string"}, "frame": {"type": "string"}}, ["prompt"])
    payload, _notes, _ = build(schema, overrides={"image": "frame"})
    assert payload["frame"] == "file:/kadr.png"


def test_helpers():
    assert mapowanie.height("1080p") == 1080
    assert mapowanie.height("768P") == 768
    assert mapowanie.height("4K") == 2160
    assert mapowanie.nearest(["6", "10"], 8, mapowanie.number) == "10"  # remis -> dłuższy
    assert mapowanie.number("5s") == 5
    assert mapowanie.find_video_url({"video": {"url": "https://x/v.mp4"}}) == "https://x/v.mp4"
    assert mapowanie.find_video_url({"data": {"items": ["https://x/a.mp4?t=1"]}}) == "https://x/a.mp4?t=1"
    assert mapowanie.find_video_url({"seed": 1}) is None


def test_model_prices():
    assert MODELS["h3-turbo"].price_per_second("1080P") == 0.08
    assert MODELS["kling-3"].price_per_second(None) == 0.112  # jedna cena, model bez pola rozdzielczości
    assert MODELS["h3-max"].price_per_second(None) is None
    assert MODELS["wan-2.6"].price_per_second("1080p") is None


def test_shot_prompts_follow_production_rules():
    shot = ujecia.SHOTS["poczta"]
    frame = ujecia.frame_prompt(shot, with_kardamon_reference=True)
    assert "No children" in frame and "Kardamon" in frame and "second attached image" in frame
    assert "{seconds}" in ujecia.motion_prompt(shot)
    ref = ujecia.ref_prompt(shot, "seedance", [Path("a.png"), Path("b.png")])
    assert "@Image1" in ref and "@Image2" in ref and "mouth stays covered" in ref
    assert all(not s.tylko_kadr for k, s in ujecia.SHOTS.items() if k in ujecia.VIDEO_SHOTS)
    assert set(ujecia.DEFAULT_SHOTS) <= set(ujecia.VIDEO_SHOTS)


# --- plan i uruchamianie z podmienioną kolejką fal ------------------------------------------------


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Katalogi testów w tmp_path, sztuczne schematy, kadr i portret."""
    out = tmp_path / "testy_fal"
    for module, name, value in [
        (ujecia, "CHOSEN_DIR", out / "wybrane"),
        (ujecia, "VIDEOS_DIR", out / "wideo"),
        (cli, "VIDEOS_DIR", out / "wideo"),
        (porownanie, "VIDEOS_DIR", out / "wideo"),
        (zadania, "LOG", out / "wyniki.jsonl"),
        (zadania, "SCHEMAS_DIR", out / "schematy"),
        (zadania.config, "ROOT", tmp_path),
    ]:
        monkeypatch.setattr(module, name, value)
    schemas = {"minimax/h3-max-turbo/image-to-video": MINIMAX_LIKE,
               "fal-ai/kling-video/v3/pro/image-to-video": KLING_LIKE}

    def fake_schema(endpoint):
        if endpoint not in schemas:
            raise fal_api.FalError(f"schemat {endpoint}: HTTP 404")
        return schemas[endpoint]

    monkeypatch.setattr(fal_api, "fetch_schema", fake_schema)
    (out / "wybrane").mkdir(parents=True)
    Image.new("RGB", (64, 36), "red").save(out / "wybrane" / "kaczka.png")
    return out


def test_dry_run_plans_jobs_without_sending(sandbox, monkeypatch, capsys):
    monkeypatch.setattr(fal_api, "submit", lambda *a, **k: pytest.fail("na sucho nie wolno wysyłać"))
    cli.main(["generuj", "--modele", "h3-turbo", "kling-3", "--ujecia", "kaczka", "--na-sucho"])
    out = capsys.readouterr().out
    assert "Plan: 2 klip(ów)" in out
    assert "$0.64" in out  # H3 Turbo: 8 s x $0.08
    assert "$1.12" in out  # Kling 3: 10 s x $0.112
    assert '"start_image_url": "file:' in out
    assert (sandbox / "schematy" / "minimax__h3-max-turbo__image-to-video.json").exists()


def test_unknown_endpoint_is_skipped(sandbox, capsys):
    cli.main(["generuj", "--modele", "h3-turbo", "h3-max", "--ujecia", "kaczka", "--na-sucho"])
    out = capsys.readouterr().out
    assert "pomijam model h3-max" in out
    assert "Plan: 1 klip(ów)" in out


def test_run_logs_job_and_resume_finishes_interrupted(sandbox, monkeypatch):
    monkeypatch.setenv("FAL_KEY", "test")
    sent = []
    monkeypatch.setattr(fal_api, "upload_image", lambda path: f"https://cdn/{path.name}")
    monkeypatch.setattr(fal_api, "submit", lambda endpoint, payload: sent.append(payload) or {
        "request_id": "r1", "status_url": "https://q/status", "response_url": "https://q/result"})
    monkeypatch.setattr(fal_api, "wait", lambda *a, **k: None)
    monkeypatch.setattr(fal_api, "result", lambda url: {"video": {"url": "https://cdn/out.mp4"}})
    monkeypatch.setattr(fal_api, "download", lambda url, out: out.parent.mkdir(parents=True, exist_ok=True)
                        or out.write_bytes(b"mp4"))

    cli.main(["generuj", "--modele", "h3-turbo", "--ujecia", "kaczka", "--tak"])
    assert sent[0]["image_url"] == "https://cdn/kaczka.png"
    clip = sandbox / "wideo" / "kaczka" / "h3-turbo_01.mp4"
    assert clip.exists()
    state = next(iter(zadania.latest_by_job().values()))
    assert state["stan"] == "gotowe" and state["koszt_usd"] == 0.64 and state["request_id"] == "r1"

    # Przerwane po wysłaniu: wznow pobiera wynik bez ponownego wysyłania.
    zadania.log_append({"id": "x1", "stan": "start", "ujecie": "kaczka", "model": "h3-turbo",
                        "plik": "testy_fal/wideo/kaczka/h3-turbo_02.mp4"})
    zadania.log_append({"id": "x1", "stan": "wyslane", "status_url": "s", "response_url": "r"})
    assert zadania.resume() == (1, 1)
    assert (sandbox / "wideo" / "kaczka" / "h3-turbo_02.mp4").exists()
    assert len(sent) == 1


def test_failed_job_is_logged(sandbox, monkeypatch):
    monkeypatch.setenv("FAL_KEY", "test")
    monkeypatch.setattr(fal_api, "upload_image", lambda path: "https://cdn/x.png")

    def reject(endpoint, payload):
        raise fal_api.FalError("wysłanie: HTTP 422 zły parametr")

    monkeypatch.setattr(fal_api, "submit", reject)
    cli.main(["generuj", "--modele", "h3-turbo", "--ujecia", "kaczka", "--tak"])
    state = next(iter(zadania.latest_by_job().values()))
    assert state["stan"] == "blad" and "422" in state["blad"]


def test_missing_frame_stops_before_spending(sandbox):
    with pytest.raises(SystemExit, match="Brakuje kadrów"):
        cli.main(["generuj", "--modele", "h3-turbo", "--ujecia", "pieczec", "--tak"])


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data, self.status_code, self.text = data, status_code, json.dumps(data)

    def json(self):
        return self._data


def test_wait_follows_statuses_and_reports_model_error(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "test")
    monkeypatch.setattr(fal_api.time, "sleep", lambda s: None)
    replies = iter([FakeResponse({"status": "IN_QUEUE", "queue_position": 2}, 202),
                    FakeResponse({"status": "IN_PROGRESS", "logs": []}, 202),
                    FakeResponse({"status": "COMPLETED", "logs": []})])
    monkeypatch.setattr(fal_api, "_request", lambda *a, **k: next(replies))
    seen = []
    fal_api.wait("https://q/status", on_change=lambda status, _data: seen.append(status))
    assert seen == ["IN_QUEUE", "IN_PROGRESS", "COMPLETED"]

    monkeypatch.setattr(fal_api, "_request", lambda *a, **k: FakeResponse(
        {"status": "COMPLETED", "error": "Content policy violation", "error_type": "content_policy"}))
    with pytest.raises(fal_api.FalError, match="content_policy"):
        fal_api.wait("https://q/status")

    monkeypatch.setattr(fal_api, "_request", lambda *a, **k: FakeResponse({"detail": "bad"}, 422))
    with pytest.raises(fal_api.FalError, match="sprawdz --odswiez"):
        fal_api.submit("vendor/model", {})


# --- siatka porównawcza ------------------------------------------------------------------------


def test_grid_layout():
    assert porownanie.grid_columns(4) == 2 and porownanie.grid_columns(5) == 3
    assert porownanie.grid_layout(4, 2) == "0_0|640_0|0_404|640_404"


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="brak ffmpeg")
def test_build_grid_with_three_clips(tmp_path):
    clips = []
    for i, seconds in enumerate([1, 1.5, 1]):
        path = tmp_path / f"m{i}_01.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc2=s=320x180:r=24:d={seconds}",
             "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(path)],
            check=True,
        )
        clips.append((path, f"model {i} | ~$0.64"))
    out = tmp_path / "grid.mp4"
    porownanie.build_grid(clips, out)
    info = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(out)],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(info)
    assert data["streams"][0]["width"] == 3 * 640 and data["streams"][0]["height"] == 404
    assert abs(float(data["format"]["duration"]) - 1.5) < 0.2
