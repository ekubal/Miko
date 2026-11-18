"""Głos Mikołaja, kwestie ogólne i podkład muzyczny (ElevenLabs).

Przykłady:
    python -m generator.audio design --rounds 2         # podglądy głosów do odsłuchania
    python -m generator.audio save-voice <generated_voice_id>
    python -m generator.audio lines                     # kwestie ogólne: pojedyncze i dla rodzeństwa
    python -m generator.audio lines --dluga             # tylko kwestie wersji długiej (d_*)
    python -m generator.audio tts --text "Ho, ho, ho!" -o test.mp3
    python -m generator.audio probki                    # ta sama kwestia w kilku ustawieniach głosu
    python -m generator.audio probki --glos ID1 ID2     # porównanie głosów (np. z biblioteki ElevenLabs)
    python -m generator.audio przemiana nagranie.m4a -o mikolaj.mp3   # nagranie człowieka głosem Mikołaja
    python -m generator.audio music --seconds 150
    python -m generator.audio select-music 1            # -> output/selected/podklad.mp3
"""

import argparse
import base64
import json
import re
import shutil
import sys
from pathlib import Path

from . import config, elevenlabs, prompts
from .common import selected_path, variant_paths, with_retry

# Spokojne, ciepłe tempo; speed < 1 zwalnia mowę.
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.8,
    "style": 0.15,
    "use_speaker_boost": True,
    "speed": 0.92,
}

# Zestawy ustawień głosu: wybór w .env (ELEVENLABS_PRESET, domyślnie v4) albo opcją --preset.
# Porównanie na jednej kwestii: `python -m generator.audio probki`. Model None = config.ELEVEN_TTS_MODEL.
# Eleven v4 przyjmuje tylko stabilność i podobieństwo (bez stylu i tempa); ekspresję dają wskazówki
# w nawiasach, np. [pause], [laughs]. Wysoka stabilność i zwolnione tempo (speed < 1) spłaszczają
# intonację starszych modeli. language_code wymusza polski tam, gdzie model to obsługuje.
PRESETS = {
    "v4": {
        "opis": "Eleven v4 (najnowszy, domyślny): naturalna polska wymowa, słucha wskazówek w nawiasach",
        "model": None,
        "settings": {"stability": 0.5, "similarity_boost": 0.75},
    },
    "v4_ekspresja": {
        "opis": "Eleven v4 z mniejszą stabilnością: więcej emocji i humoru, mniej przewidywalnie",
        "model": "eleven_v4",
        "settings": {"stability": 0.3, "similarity_boost": 0.75},
    },
    "naturalny": {
        "opis": "ten sam model, mniej stabilności, więcej ekspresji, normalne tempo",
        "model": "eleven_multilingual_v2",
        "settings": {"stability": 0.4, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True,
                     "speed": 1.0},
    },
    "v3": {
        "opis": "poprzedni model Eleven v3, tryb Natural",
        "model": "eleven_v3",
        "settings": {"stability": 0.5, "similarity_boost": 0.75},
    },
    "flash_pl": {
        "opis": "szybki model Flash v2.5 z wymuszonym językiem polskim",
        "model": "eleven_flash_v2_5",
        "settings": {"stability": 0.45, "similarity_boost": 0.8, "speed": 1.0},
        "language_code": "pl",
    },
    "dotychczasowy": {
        "opis": "dawne ustawienia: Multilingual v2, stabilnie i wolniej (punkt odniesienia)",
        "model": "eleven_multilingual_v2",
        "settings": VOICE_SETTINGS,
    },
}

# Modele, które rozumieją wskazówki w nawiasach kwadratowych; pozostałe przeczytałyby je na głos.
TAG_MODELS = {"eleven_v3", "eleven_v4", "eleven_v4_turbo"}


def strip_tags(text: str) -> str:
    """Usuwa wskazówki w nawiasach ([pause], [laughs]…) dla modeli, które ich nie obsługują."""
    return re.sub(r" {2,}", " ", re.sub(r"\[[^\]]*\]", "", text)).strip()

# Zamiana głosu (speech-to-speech): intonację i akcent bierze z nagrania człowieka.
STS_SETTINGS = {"stability": 0.5, "similarity_boost": 0.85, "style": 0.0, "use_speaker_boost": True}


def get_preset(name: str | None = None) -> dict:
    name = name or config.ELEVEN_PRESET
    if name not in PRESETS:
        sys.exit(f"Nieznany zestaw ustawień głosu: {name}. Dostępne: {', '.join(PRESETS)} "
                 "(ELEVENLABS_PRESET w .env albo --preset).")
    return PRESETS[name]


def synthesize(text: str, voice_id: str, preset: dict, settings: dict | None = None) -> bytes:
    # Model i język przekazujemy tylko, gdy zestaw je ustala; inaczej obowiązuje config.ELEVEN_TTS_MODEL.
    if (preset["model"] or config.ELEVEN_TTS_MODEL) not in TAG_MODELS:
        text = strip_tags(text)
    extra = {}
    if preset["model"]:
        extra["model"] = preset["model"]
    if preset.get("language_code"):
        extra["language_code"] = preset["language_code"]
    return elevenlabs.text_to_speech(text, voice_id, settings or preset["settings"], **extra)


def speak(text: str, out: Path, settings: dict | None = None, preset: str | None = None) -> None:
    chosen = get_preset(preset)
    voice_id = elevenlabs.saved_voice_id()
    audio = with_retry(lambda: synthesize(text, voice_id, chosen, settings))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    print(f"  + {out}")


def cmd_design(args):
    directory = config.AUDIO_DIR / "voice_design"
    index_path = directory / "previews.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
    for _ in range(args.rounds):
        previews = with_retry(lambda: elevenlabs.design_voice(prompts.VOICE_DESCRIPTION, args.text))
        for preview, path in zip(previews, variant_paths(directory, "preview", ".mp3", len(previews))):
            path.write_bytes(base64.b64decode(preview["audio_base_64"]))
            index.append({"file": path.name, "generated_voice_id": preview["generated_voice_id"]})
            print(f"  + {path}  ({preview['generated_voice_id']})")
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOdsłuchaj podglądy i zapisz najlepszy: python -m generator.audio save-voice <generated_voice_id>")


def cmd_save_voice(args):
    voice_id = elevenlabs.create_voice(args.name, prompts.VOICE_DESCRIPTION, args.generated_voice_id)
    config.VOICE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.VOICE_FILE.write_text(
        json.dumps({"voice_id": voice_id, "name": args.name}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Zapisano głos {args.name}: voice_id={voice_id} -> {config.VOICE_FILE}")


def cmd_lines(args):
    variants = ["single", "plural"] if args.variant == "all" else [args.variant]
    directory = config.AUDIO_DIR / "lines"
    for key, lines in prompts.GENERAL_LINES.items():
        if args.only and key not in args.only:
            continue
        if args.dluga and key not in prompts.LONG_LINES:
            continue
        for variant in variants:
            suffix = "" if variant == "single" else "_rodzenstwo"
            out = directory / f"{key}{suffix}.mp3"
            if out.exists() and not args.force:
                print(f"  = {out} (istnieje, użyj --force)")
                continue
            speak(lines[variant], out, preset=args.preset)


def cmd_tts(args):
    text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
    speak(text.strip(), Path(args.output), preset=args.preset)


def cmd_probki(args):
    # Bez ponawiania: model niedostępny w planie albo nieobsługiwana opcja to błąd 4xx,
    # który zgłaszamy i przechodzimy do następnego zestawu.
    voices = args.glos or [elevenlabs.saved_voice_id()]
    directory = config.AUDIO_DIR / "probki"
    print(f"Tekst: {args.text}\n")
    for voice_id in voices:
        for name in args.presety:
            preset = get_preset(name)
            stem = f"{voice_id[:8]}_{name}"
            for out in variant_paths(directory, stem, ".mp3", args.count):
                try:
                    out.write_bytes(synthesize(args.text, voice_id, preset))
                    print(f"  + {out}  ({preset['opis']})")
                except Exception as exc:
                    print(f"  x {stem}: {exc}")
    print(f"\nOdsłuchaj pliki w {directory}. Najlepszy zestaw wpisz w .env jako ELEVENLABS_PRESET=<nazwa>,\n"
          "a najlepszy głos jako ELEVENLABS_VOICE_ID. Potem nagraj kwestie ponownie z --force.")


def cmd_przemiana(args):
    source = Path(args.nagranie)
    if not source.exists():
        sys.exit(f"Nie ma pliku {source}")
    voice_id = elevenlabs.saved_voice_id()
    audio = with_retry(lambda: elevenlabs.speech_to_speech(
        source, voice_id, STS_SETTINGS, config.ELEVEN_STS_MODEL, args.bez_szumu))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    print(f"  + {out}")


def cmd_music(args):
    directory = config.AUDIO_DIR / "music"
    for out in variant_paths(directory, "podklad", ".mp3", args.count):
        audio = with_retry(lambda: elevenlabs.compose_music(args.prompt, args.seconds * 1000))
        out.write_bytes(audio)
        print(f"  + {out}")


def cmd_select_music(args):
    source = config.AUDIO_DIR / "music" / f"podklad_{args.number:02d}.mp3"
    if not source.exists():
        sys.exit(f"Nie znaleziono {source}")
    target = selected_path("podklad", ".mp3")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Wybrano {source.name} -> {target}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Głos i muzyka (ElevenLabs)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("design", help="Voice Design: podglądy głosu Mikołaja (krok 5)")
    p.add_argument("--rounds", type=int, default=1, help="każda runda daje kilka podglądów")
    p.add_argument("--text", default=prompts.VOICE_SAMPLE_TEXT, help="tekst próbny (100–1000 znaków)")
    p.set_defaults(func=cmd_design)

    p = sub.add_parser("save-voice", help="zapisz wybrany podgląd jako głos w bibliotece")
    p.add_argument("generated_voice_id")
    p.add_argument("--name", default="Mikolaj")
    p.set_defaults(func=cmd_save_voice)

    p = sub.add_parser("lines", help="nagraj kwestie wspólne (wersja krótka i długa)")
    p.add_argument("--variant", choices=["single", "plural", "all"], default="all")
    p.add_argument("--only", nargs="+", choices=list(prompts.GENERAL_LINES))
    p.add_argument("--dluga", action="store_true", help="tylko kwestie wersji długiej (klucze d_*)")
    p.add_argument("--force", action="store_true", help="nadpisz istniejące nagrania")
    p.add_argument("--preset", choices=list(PRESETS), help="zestaw ustawień głosu (domyślnie ELEVENLABS_PRESET)")
    p.set_defaults(func=cmd_lines)

    p = sub.add_parser("tts", help="dowolny tekst głosem Mikołaja")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--file")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--preset", choices=list(PRESETS), help="zestaw ustawień głosu (domyślnie ELEVENLABS_PRESET)")
    p.set_defaults(func=cmd_tts)

    p = sub.add_parser("probki", help="ta sama kwestia w kilku zestawach ustawień (i głosach) do odsłuchania")
    p.add_argument("--text", default=prompts.VOICE_TEST_TEXT)
    p.add_argument("--presety", nargs="+", choices=list(PRESETS), default=list(PRESETS))
    p.add_argument("--glos", nargs="+", help="id głosów do porównania (domyślnie zapisany głos Mikołaja)")
    p.add_argument("-n", "--count", type=int, default=1, help="wersji na zestaw (każde nagranie brzmi inaczej)")
    p.set_defaults(func=cmd_probki)

    p = sub.add_parser("przemiana", help="nagranie człowieka zamienione na głos Mikołaja (speech-to-speech)")
    p.add_argument("nagranie", help="plik z nagraniem (mp3, wav, m4a)")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--bez-szumu", action="store_true", help="usuń szum tła z nagrania")
    p.set_defaults(func=cmd_przemiana)

    p = sub.add_parser("music", help="podkład muzyczny (ElevenLabs Music)")
    p.add_argument("--seconds", type=int, default=150)
    p.add_argument("--prompt", default=prompts.MUSIC_PROMPT)
    p.add_argument("-n", "--count", type=int, default=1)
    p.set_defaults(func=cmd_music)

    p = sub.add_parser("select-music", help="zatwierdź podkład do montażu, np. select-music 2")
    p.add_argument("number", type=int)
    p.set_defaults(func=cmd_select_music)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
