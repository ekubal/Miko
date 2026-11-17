"""Głos Mikołaja: zestawy ustawień, porównanie próbek i zamiana głosu (bez sieci: requests i API podmienione)."""

import json

import pytest

from generator import audio, config, elevenlabs


class FakeResponse:
    ok = True
    status_code = 200
    content = b"MP3"
    text = ""


@pytest.fixture
def posts(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        return FakeResponse()

    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setattr(elevenlabs.requests, "post", fake_post)
    return calls


def test_text_to_speech_sends_model_and_language_only_when_given(posts):
    elevenlabs.text_to_speech("Ho, ho, ho!", "voice1", {"stability": 0.5})
    elevenlabs.text_to_speech("Ho, ho, ho!", "voice1", {"stability": 0.5}, model="eleven_flash_v2_5",
                              language_code="pl")
    first, second = (call["json"] for call in posts)
    assert first["model_id"] == config.ELEVEN_TTS_MODEL and "language_code" not in first
    assert second["model_id"] == "eleven_flash_v2_5" and second["language_code"] == "pl"
    assert posts[0]["url"].endswith("/v1/text-to-speech/voice1")


def test_speech_to_speech_uploads_recording_as_form(posts, tmp_path):
    recording = tmp_path / "nagranie.wav"
    recording.write_bytes(b"RIFF")
    assert elevenlabs.speech_to_speech(recording, "voice1", {"stability": 0.5}, "eleven_multilingual_sts_v2",
                                       remove_background_noise=True) == b"MP3"
    call = posts[0]
    assert call["url"].endswith("/v1/speech-to-speech/voice1")
    assert call["files"]["audio"][0] == "nagranie.wav" and call["files"]["audio"][1] == b"RIFF"
    assert call["data"]["model_id"] == "eleven_multilingual_sts_v2"
    assert json.loads(call["data"]["voice_settings"]) == {"stability": 0.5}
    assert call["data"]["remove_background_noise"] == "true"
    assert "Content-Type" not in call["headers"]


def test_presets_are_complete_and_default_keeps_current_settings():
    assert audio.PRESETS["obecny"]["settings"] is audio.VOICE_SETTINGS
    assert audio.PRESETS["obecny"]["model"] is None
    for name, preset in audio.PRESETS.items():
        assert preset["opis"] and preset["settings"].get("stability") is not None, name
        if name != "obecny":
            # Zwolnione tempo spłaszcza intonację: zestawy do poprawy brzmienia mówią w normalnym tempie.
            assert preset["settings"].get("speed", 1.0) == 1.0, name
    with pytest.raises(SystemExit):
        audio.get_preset("nie_ma_takiego")


def test_probki_records_each_preset_and_skips_failing_ones(monkeypatch, tmp_path):
    calls = []

    def fake_tts(text, voice_id, settings, **extra):
        calls.append((voice_id, extra))
        if extra.get("model") == "eleven_v3":
            raise RuntimeError("ElevenLabs: HTTP 400: model not available")
        return b"MP3"

    monkeypatch.setattr(config, "AUDIO_DIR", tmp_path)
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice123")
    monkeypatch.setattr(audio.elevenlabs, "text_to_speech", fake_tts)
    audio.main(["probki", "--presety", "obecny", "v3", "flash_pl"])
    files = sorted(p.name for p in (tmp_path / "probki").iterdir())
    assert files == ["voice123_flash_pl_01.mp3", "voice123_obecny_01.mp3"]
    assert calls[0] == ("voice123", {})
    assert calls[2] == ("voice123", {"model": "eleven_flash_v2_5", "language_code": "pl"})


def test_preset_from_env_is_used_by_speak(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(config, "ELEVEN_PRESET", "naturalny")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice123")
    monkeypatch.setattr(audio.elevenlabs, "text_to_speech",
                        lambda text, vid, settings, **extra: calls.append((settings, extra)) or b"MP3")
    audio.speak("Ho, ho, ho!", tmp_path / "test.mp3")
    assert calls == [(audio.PRESETS["naturalny"]["settings"], {"model": "eleven_multilingual_v2"})]
