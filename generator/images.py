"""Generowanie obrazów w Nano Banana Pro (Gemini API).

Przykłady:
    python -m generator.images portrait -n 10
    python -m generator.images portrait -n 4 --wariant pelna-broda
    python -m generator.images select portrait 4
    python -m generator.images platek -n 6       # portret wzorcowy Płatka (sceny z reniferem)
    python -m generator.images select platek 2
    python -m generator.images scenes -n 3
    python -m generator.images select dom 2      # i tak dla pracownia, ksiega, sanie
    python -m generator.images templates -n 3
    python -m generator.images select szablon_ksiega 1
    python -m generator.images scenes -n 3 --dry-run   # plan i szacowany koszt, bez wysyłania

Po każdym obrazie i na końcu polecenia wypisuje koszt policzony z tokenów odpowiedzi
i cennika w config (IMAGE_PRICE_*). To podgląd; rozliczenie jest w Google Cloud Billing.
"""

import argparse
import mimetypes
import shutil
import sys
from pathlib import Path

from . import config, prompts
from .common import google_client, selected_path, variant_paths, with_retry

EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def usd(amount: float) -> str:
    return f"{amount:.3f} USD"


def image_cost(usage) -> float | None:
    """Koszt jednej odpowiedzi w USD z usage_metadata; None, gdy model nie podał tokenów."""
    if usage is None or usage.prompt_token_count is None:
        return None
    output = usage.candidates_token_count or 0
    details = usage.candidates_tokens_details or []
    if details:
        image = sum(d.token_count or 0 for d in details if getattr(d.modality, "name", d.modality) == "IMAGE")
    else:
        image = output
    text = output - image + (usage.thoughts_token_count or 0)
    return (
        usage.prompt_token_count * config.IMAGE_PRICE_INPUT
        + image * config.IMAGE_PRICE_OUTPUT_IMAGE
        + text * config.IMAGE_PRICE_OUTPUT_TEXT
    ) / 1_000_000


def estimate_cost(prompt: str, reference_count: int, size: str) -> float:
    """Szacunek kosztu jednego obrazu przed wysłaniem: referencje, prompt (ok. 4 znaki na token) i wynik."""
    tokens_in = reference_count * config.IMAGE_INPUT_TOKENS_PER_REFERENCE + len(prompt) // 4
    tokens_out = config.IMAGE_OUTPUT_TOKENS[size]
    return (tokens_in * config.IMAGE_PRICE_INPUT + tokens_out * config.IMAGE_PRICE_OUTPUT_IMAGE) / 1_000_000


def generate_image(client, prompt: str, references: list[Path], aspect_ratio: str, size: str):
    """Zwraca (bajty, mime_type, koszt_usd albo None) pierwszego obrazu z odpowiedzi modelu.

    Referencje idą przed promptem w podanej kolejności (prompt odwołuje się do ich numerów).
    """
    from google.genai import types

    contents: list = []
    for reference in references:
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
                cost = image_cost(getattr(response, "usage_metadata", None))
                return part.inline_data.data, part.inline_data.mime_type or "image/png", cost
    reason = response.candidates[0].finish_reason if response.candidates else response.prompt_feedback
    raise RuntimeError(f"Model nie zwrócił obrazu (powód: {reason}).")


def generate_variants(client, name: str, prompt: str, directory: Path, references: list[Path], args):
    """Generuje args.count wariantów; zwraca (koszt_usd, liczba obrazów, liczba obrazów bez kosztu)."""
    print(f"[{name}] {args.count} wariant(ów) -> {directory}")
    total, made, unknown = 0.0, 0, 0
    for path in variant_paths(directory, name, ".png", args.count):
        try:
            data, mime, cost = generate_image(client, prompt, references, args.aspect_ratio, args.size)
        except Exception as exc:
            print(f"  x {path.name}: {exc}")
            continue
        path = path.with_suffix(EXTENSIONS.get(mime, ".png"))
        path.write_bytes(data)
        made += 1
        if cost is None:
            unknown += 1
        else:
            total += cost
        shown = path.relative_to(config.ROOT) if path.is_relative_to(config.ROOT) else path
        print(f"  + {shown}  ({usd(cost) if cost is not None else 'koszt nieznany'})")
    return total, made, unknown


def run_jobs(jobs: list[tuple[str, str, Path, list[Path]]], args):
    """Generuje warianty dla zadań (nazwa, prompt, katalog, referencje) i podsumowuje koszt.

    Przy --dry-run tylko wypisuje plan i szacowany koszt, bez wywołań API.
    """
    if args.dry_run:
        total = 0.0
        for name, prompt, _, references in jobs:
            each = estimate_cost(prompt, len(references), args.size)
            total += each * args.count
            print(f"[{name}] {args.count} × ~{usd(each)} = ~{usd(each * args.count)}")
        print(f"Razem (szacunek): {len(jobs) * args.count} obraz(ów), ~{usd(total)}. Nic nie wysłano.")
        return
    client = google_client()
    total, made, unknown = 0.0, 0, 0
    for name, prompt, directory, references in jobs:
        cost, count, missing = generate_variants(client, name, prompt, directory, references, args)
        total, made, unknown = total + cost, made + count, unknown + missing
    note = f"; {unknown} bez danych o koszcie" if unknown else ""
    print(f"Razem: {made} obraz(ów), ok. {usd(total)}{note}. Rozliczenie: Google Cloud Billing.")


def require_references(args, keys: list[str]) -> dict[str, Path]:
    """Ścieżki referencji potrzebnych wybranym scenom; kończy program, gdy którejś brakuje."""
    needed = {ref for key in keys for ref in prompts.scene_references(key)}
    paths = {}
    for ref in sorted(needed):
        path = Path(args.reference) if ref == "portrait" and args.reference else selected_path(ref)
        if not path.exists():
            sys.exit(
                f"Brak obrazu referencyjnego: {path}\n"
                f"Najpierw: python -m generator.images {ref}, potem: python -m generator.images select {ref} N"
            )
        paths[ref] = path
    return paths


def cmd_portrait(args):
    print(f"Wariant portretu: {args.wariant}")
    prompt = prompts.PORTRAIT_VARIANTS[args.wariant]
    run_jobs([("portrait", prompt, config.IMAGES_DIR / "portrait", [])], args)


def cmd_platek(args):
    run_jobs([("platek", prompts.PLATEK_PORTRAIT_PROMPT, config.IMAGES_DIR / "portrait", [])], args)


def cmd_scenes(args):
    keys = args.only or list(prompts.SCENES)
    if args.dry_run:
        # Szacunek liczy tylko liczbę referencji, więc nie wymaga zatwierdzonych portretów.
        paths = {ref: selected_path(ref) for key in keys for ref in prompts.scene_references(key)}
    else:
        paths = require_references(args, keys)
    jobs = []
    for key in keys:
        references = [paths[ref] for ref in prompts.scene_references(key)]
        jobs.append((key, prompts.scene_prompt(key), config.IMAGES_DIR / "scenes", references))
    run_jobs(jobs, args)


def cmd_templates(args):
    keys = args.only or list(prompts.TEMPLATES)
    run_jobs([(key, prompts.TEMPLATES[key], config.IMAGES_DIR / "templates", []) for key in keys], args)


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
        p.add_argument("--dry-run", action="store_true", help="pokaż plan i szacowany koszt, nic nie wysyłaj")

    p = sub.add_parser("portrait", help="portret Mikołaja do awatara (krok 1)")
    add_common(p, 10)
    p.add_argument(
        "--wariant",
        choices=list(prompts.PORTRAIT_VARIANTS),
        default="klasyczny",
        help="klasyczny albo pelna-broda (długa broda, wąsy zakrywające usta, okulary, kadr do kolan)",
    )
    p.set_defaults(func=cmd_portrait)

    p = sub.add_parser("platek", help="portret wzorcowy Płatka, referencja scen z reniferem")
    add_common(p, 6)
    p.set_defaults(func=cmd_platek)

    p = sub.add_parser("scenes", help="kadry scen z tą samą postacią (krok 2)")
    add_common(p, 3)
    p.add_argument("--reference", help="portret referencyjny (domyślnie output/selected/portrait.png)")
    p.add_argument("--only", nargs="+", choices=list(prompts.SCENES), help="tylko wybrane sceny")
    p.set_defaults(func=cmd_scenes)

    p = sub.add_parser("templates", help="puste szablony do personalizacji w montażu (krok 3)")
    add_common(p, 3)
    p.add_argument("--only", nargs="+", choices=list(prompts.TEMPLATES))
    p.set_defaults(func=cmd_templates)

    p = sub.add_parser("select", help="zatwierdź wariant, np. select portrait 4")
    p.add_argument("name", choices=["portrait", "platek", *prompts.SCENES, *prompts.TEMPLATES])
    p.add_argument("number", type=int)
    p.set_defaults(func=cmd_select)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
