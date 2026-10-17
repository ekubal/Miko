"""Generowanie obrazów w Nano Banana Pro (Gemini API).

Przykłady:
    python -m generator.images portrait -n 10
    python -m generator.images select portrait 4
    python -m generator.images scenes -n 3
    python -m generator.images select dom 2      # i tak dla pracownia, ksiega, sanie
    python -m generator.images templates -n 3
    python -m generator.images select szablon_ksiega 1
"""

import argparse
import mimetypes
import shutil
import sys
from pathlib import Path

from . import config, prompts
from .common import google_client, selected_path, variant_paths, with_retry

EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def generate_image(client, prompt: str, reference: Path | None, aspect_ratio: str, size: str):
    """Zwraca (bajty, mime_type) pierwszego obrazu z odpowiedzi modelu."""
    from google.genai import types

    contents: list = []
    if reference is not None:
        mime = mimetypes.guess_type(reference.name)[0] or "image/png"
        contents.append(types.Part.from_bytes(data=reference.read_bytes(), mime_type=mime))
    contents.append(prompt)

    response = with_retry(
        lambda: client.models.generate_content(
            model=config.IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio, image_size=size),
            ),
        )
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else None) or []:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data, part.inline_data.mime_type or "image/png"
    reason = response.candidates[0].finish_reason if response.candidates else response.prompt_feedback
    raise RuntimeError(f"Model nie zwrócił obrazu (powód: {reason}).")


def generate_variants(name: str, prompt: str, directory: Path, count: int, reference: Path | None, args):
    client = google_client()
    print(f"[{name}] {count} wariant(ów) -> {directory}")
    for path in variant_paths(directory, name, ".png", count):
        try:
            data, mime = generate_image(client, prompt, reference, args.aspect_ratio, args.size)
        except Exception as exc:
            print(f"  x {path.name}: {exc}")
            continue
        path = path.with_suffix(EXTENSIONS.get(mime, ".png"))
        path.write_bytes(data)
        print(f"  + {path.relative_to(config.ROOT) if path.is_relative_to(config.ROOT) else path}")


def require_reference(args) -> Path:
    reference = Path(args.reference) if args.reference else selected_path("portrait")
    if not reference.exists():
        sys.exit(
            f"Brak portretu referencyjnego: {reference}\n"
            "Najpierw: python -m generator.images portrait, potem: python -m generator.images select portrait N"
        )
    return reference


def cmd_portrait(args):
    generate_variants("portrait", prompts.PORTRAIT_PROMPT, config.IMAGES_DIR / "portrait", args.count, None, args)


def cmd_scenes(args):
    reference = require_reference(args)
    keys = args.only or list(prompts.SCENES)
    for key in keys:
        prompt = prompts.SCENE_PROMPT.format(scene=prompts.SCENES[key]["scene"])
        generate_variants(key, prompt, config.IMAGES_DIR / "scenes", args.count, reference, args)


def cmd_templates(args):
    keys = args.only or list(prompts.TEMPLATES)
    for key in keys:
        generate_variants(key, prompts.TEMPLATES[key], config.IMAGES_DIR / "templates", args.count, None, args)


def cmd_select(args):
    matches = sorted(config.IMAGES_DIR.rglob(f"{args.name}_{args.number:02d}.*"))
    if not matches:
        sys.exit(f"Nie znaleziono wariantu {args.name}_{args.number:02d} w {config.IMAGES_DIR}")
    target = selected_path(args.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Zapisujemy zawsze jako .png, żeby kolejne kroki znały stałą nazwę pliku.
    if matches[0].suffix == ".png":
        shutil.copyfile(matches[0], target)
    else:
        from PIL import Image

        Image.open(matches[0]).save(target)
    print(f"Wybrano {matches[0].name} -> {target}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Obrazy Mikołaja (Nano Banana Pro)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p, default_count):
        p.add_argument("-n", "--count", type=int, default=default_count, help="liczba wariantów")
        p.add_argument("--aspect-ratio", default="16:9")
        p.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])

    p = sub.add_parser("portrait", help="portret Mikołaja do awatara (krok 1)")
    add_common(p, 10)
    p.set_defaults(func=cmd_portrait)

    p = sub.add_parser("scenes", help="kadry scen z tą samą postacią (krok 2)")
    add_common(p, 3)
    p.add_argument("--reference", help="portret referencyjny (domyślnie output/selected/portrait.png)")
    p.add_argument("--only", nargs="+", choices=list(prompts.SCENES), help="tylko wybrane sceny")
    p.set_defaults(func=cmd_scenes)

    p = sub.add_parser("templates", help="puste szablony księgi i listy (krok 3)")
    add_common(p, 3)
    p.add_argument("--only", nargs="+", choices=list(prompts.TEMPLATES))
    p.set_defaults(func=cmd_templates)

    p = sub.add_parser("select", help="zatwierdź wariant, np. select portrait 4")
    p.add_argument("name", choices=["portrait", *prompts.SCENES, *prompts.TEMPLATES])
    p.add_argument("number", type=int)
    p.set_defaults(func=cmd_select)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
