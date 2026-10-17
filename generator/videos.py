"""Generowanie klipów scen ogólnych w Veo 3.1 (Gemini API), z kadru jako pierwszej klatki.

Przykłady:
    python -m generator.videos -n 2                 # wszystkie 4 sceny, tryb Fast
    python -m generator.videos --only ksiega --quality
"""

import argparse
import sys
import time
from pathlib import Path

from . import config, prompts
from .common import google_client, selected_path, variant_paths, with_retry

POLL_SECONDS = 10


def generate_clip(client, prompt: str, first_frame: Path, model: str, resolution: str, out: Path) -> None:
    from google.genai import types

    operation = with_retry(
        lambda: client.models.generate_videos(
            model=model,
            prompt=prompt,
            image=types.Image(image_bytes=first_frame.read_bytes(), mime_type="image/png"),
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                resolution=resolution,
                duration_seconds=8,
            ),
        )
    )
    started = time.time()
    while not operation.done:
        time.sleep(POLL_SECONDS)
        operation = client.operations.get(operation)
        print(f"    ... {time.time() - started:.0f} s", end="\r")
    if operation.error:
        raise RuntimeError(operation.error)
    videos = operation.response.generated_videos if operation.response else None
    if not videos:
        raise RuntimeError("Veo nie zwróciło klipu (możliwa blokada filtrów bezpieczeństwa).")
    client.files.download(file=videos[0].video)
    videos[0].video.save(str(out))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Klipy scen ogólnych (Veo 3.1)")
    parser.add_argument("-n", "--count", type=int, default=1, help="liczba wariantów na scenę")
    parser.add_argument("--only", nargs="+", choices=list(prompts.SCENES))
    parser.add_argument("--quality", action="store_true", help="model Quality zamiast Fast")
    parser.add_argument("--resolution", default="1080p", choices=["720p", "1080p"])
    args = parser.parse_args(argv)

    keys = args.only or list(prompts.SCENES)
    missing = [k for k in keys if not selected_path(k).exists()]
    if missing:
        sys.exit(
            f"Brak zatwierdzonych kadrów: {', '.join(missing)}.\n"
            "Wygeneruj je (python -m generator.images scenes) i wybierz (python -m generator.images select <scena> N)."
        )

    model = config.VIDEO_MODEL_QUALITY if args.quality else config.VIDEO_MODEL_FAST
    mode = "quality" if args.quality else "fast"
    client = google_client()
    for key in keys:
        prompt = prompts.MOTION_PROMPT.format(motion=prompts.SCENES[key]["motion"])
        print(f"[{key}] {args.count} klip(ów), model {model}")
        for out in variant_paths(config.VIDEOS_DIR, f"{key}_{mode}", ".mp4", args.count):
            try:
                generate_clip(client, prompt, selected_path(key), model, args.resolution, out)
                print(f"  + {out}")
            except Exception as exc:
                print(f"  x {out.name}: {exc}")


if __name__ == "__main__":
    main()
