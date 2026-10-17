"""Głos Mikołaja, kwestie ogólne i podkład muzyczny (ElevenLabs).

Przykłady:
    python -m generator.audio design --rounds 2         # podglądy głosów do odsłuchania
    python -m generator.audio save-voice <generated_voice_id>
    python -m generator.audio lines                     # kwestie ogólne: pojedyncze i dla rodzeństwa
    python -m generator.audio tts --text "Ho, ho, ho!" -o test.mp3
    python -m generator.audio music --seconds 150
"""

import argparse
import base64
import json
from pathlib import Path

from . import config, elevenlabs, prompts
from .common import variant_paths, with_retry

# Spokojne, ciepłe tempo; speed < 1 zwalnia mowę.
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.8,
    "style": 0.15,
    "use_speaker_boost": True,
    "speed": 0.92,
}


def speak(text: str, out: Path, settings: dict | None = None) -> None:
    voice_id = elevenlabs.saved_voice_id()
    audio = with_retry(lambda: elevenlabs.text_to_speech(text, voice_id, settings or VOICE_SETTINGS))
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
        for variant in variants:
            suffix = "" if variant == "single" else "_rodzenstwo"
            out = directory / f"{key}{suffix}.mp3"
            if out.exists() and not args.force:
                print(f"  = {out} (istnieje, użyj --force)")
                continue
            speak(lines[variant], out)


def cmd_tts(args):
    text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
    speak(text.strip(), Path(args.output))


def cmd_music(args):
    directory = config.AUDIO_DIR / "music"
    for out in variant_paths(directory, "podklad", ".mp3", args.count):
        audio = with_retry(lambda: elevenlabs.compose_music(args.prompt, args.seconds * 1000))
        out.write_bytes(audio)
        print(f"  + {out}")


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

    p = sub.add_parser("lines", help="nagraj kwestie ogólne (sceny 1, 2, 4, 5, 6)")
    p.add_argument("--variant", choices=["single", "plural", "all"], default="all")
    p.add_argument("--only", nargs="+", choices=list(prompts.GENERAL_LINES))
    p.add_argument("--force", action="store_true", help="nadpisz istniejące nagrania")
    p.set_defaults(func=cmd_lines)

    p = sub.add_parser("tts", help="dowolny tekst głosem Mikołaja")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--file")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_tts)

    p = sub.add_parser("music", help="podkład muzyczny (ElevenLabs Music)")
    p.add_argument("--seconds", type=int, default=150)
    p.add_argument("--prompt", default=prompts.MUSIC_PROMPT)
    p.add_argument("-n", "--count", type=int, default=1)
    p.set_defaults(func=cmd_music)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
