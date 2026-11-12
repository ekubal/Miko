"""Generowanie klipów scen ogólnych w Gemini Omni Flash (Gemini API), z kadru jako pierwszej klatki.

Veo 3.1 w Gemini API zostało wyłączone 22.10.2026; jego następcą jest Gemini Omni Flash
(`gemini-omni-1.1-flash`), wywoływany przez Interactions API.

Przykłady:
    python -m generator.videos generate --only zorza --resolution 360p   # tani test
    python -m generator.videos generate -n 2                             # wszystkie sceny, 1080p
    python -m generator.videos select zorza 2                            # -> output/selected/zorza.mp4
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

from . import config, prompts
from .common import google_client, selected_path, variant_paths, with_retry

RESOLUTIONS = ["360p", "720p", "1080p", "4k"]
# Czas jednego wywołania: generowanie klipu trwa zwykle kilka minut, 4k dłużej.
REQUEST_TIMEOUT_S = 900


def upload_frame(client, frame: Path):
    """Wgrywa kadr do Files API i czeka, aż będzie gotowy do użycia."""
    uploaded = with_retry(lambda: client.files.upload(file=str(frame)))
    deadline = time.time() + 300
    while getattr(uploaded.state, "name", str(uploaded.state)) == "PROCESSING":
        if time.time() > deadline:
            raise RuntimeError(f"Kadr {frame.name} nie został przetworzony w 5 minut.")
        time.sleep(3)
        uploaded = client.files.get(name=uploaded.name)
    if getattr(uploaded.state, "name", str(uploaded.state)) == "FAILED":
        raise RuntimeError(f"Files API odrzuciło kadr {frame.name}.")
    return uploaded


def generate_clip(client, prompt: str, frame_file, resolution: str, duration: int, out: Path) -> None:
    """Jedno wywołanie Interactions API: kadr jako pierwsza klatka + prompt ruchu -> plik MP4."""
    started = time.time()
    interaction = with_retry(
        lambda: client.interactions.create(
            model=config.VIDEO_MODEL,
            input=[
                {"type": "image", "uri": frame_file.uri, "mime_type": frame_file.mime_type},
                {"type": "text", "text": f"<FIRST_FRAME> {prompt}"},
            ],
            response_format={
                "type": "video",
                "delivery": "uri",
                "aspect_ratio": "16:9",
                "duration": f"{duration}s",
                "resolution": resolution,
            },
            timeout=REQUEST_TIMEOUT_S,
        )
    )
    video = interaction.output_video
    if not video or not video.uri:
        raise RuntimeError("Model nie zwrócił klipu (możliwa blokada filtrów bezpieczeństwa).")
    out.write_bytes(client.files.download(file=video.uri))
    print(f"    ({time.time() - started:.0f} s)")


def cmd_generate(args):
    keys = args.only or list(prompts.SCENES)
    missing = [k for k in keys if not selected_path(k).exists()]
    if missing:
        sys.exit(
            f"Brak zatwierdzonych kadrów: {', '.join(missing)}.\n"
            "Wygeneruj je (python -m generator.images scenes) i wybierz (python -m generator.images select <scena> N)."
        )

    client = google_client()
    for key in keys:
        prompt = prompts.scene_motion_prompt(key, args.duration)
        print(f"[{key}] {args.count} klip(ów), {config.VIDEO_MODEL}, {args.resolution}, {args.duration} s")
        frame_file = upload_frame(client, selected_path(key))
        for out in variant_paths(config.VIDEOS_DIR, key, ".mp4", args.count):
            try:
                generate_clip(client, prompt, frame_file, args.resolution, args.duration, out)
                print(f"  + {out}")
            except Exception as exc:
                print(f"  x {out.name}: {exc}")


def cmd_select(args):
    source = config.VIDEOS_DIR / f"{args.scene}_{args.number:02d}.mp4"
    if not source.exists():
        sys.exit(f"Nie znaleziono klipu {source}")
    target = selected_path(args.scene, ".mp4")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Wybrano {source.name} -> {target}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Klipy scen ogólnych (Gemini Omni Flash)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="wygeneruj klipy z zatwierdzonych kadrów")
    p.add_argument("-n", "--count", type=int, default=1, help="liczba wariantów na scenę")
    p.add_argument("--only", nargs="+", choices=list(prompts.SCENES))
    p.add_argument("--resolution", default="1080p", choices=RESOLUTIONS, help="360p na tani test")
    p.add_argument("--duration", type=int, default=8, choices=range(3, 11), metavar="3-10", help="sekundy klipu")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("select", help="zatwierdź klip, np. select zorza 2")
    p.add_argument("scene", choices=list(prompts.SCENES))
    p.add_argument("number", type=int)
    p.set_defaults(func=cmd_select)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
