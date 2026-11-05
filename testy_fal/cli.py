"""Polecenia testów modeli wideo. Uruchamiaj z katalogu głównego repozytorium.

    python -m testy_fal modele                       # modele, ceny, uwagi
    python -m testy_fal ujecia                       # ujęcia testowe i stan kadrów
    python -m testy_fal sprawdz                      # schematy modeli na fal (bez kosztów)
    python -m testy_fal kadry --only kardamon -n 3   # kadry startowe (Nano Banana Pro)
    python -m testy_fal wybierz kardamon 2
    python -m testy_fal generuj --na-sucho           # plan, koszt i zapytania bez wysyłania
    python -m testy_fal generuj                      # domyślne modele i ujęcia, po 1 wariancie
    python -m testy_fal wznow                        # dokończ przerwane zapytania fal
    python -m testy_fal porownaj                     # siatki porównawcze MP4
    python -m testy_fal podsumowanie                 # czasy, koszty, błędy
"""

import argparse
import json
import mimetypes
import shutil
import sys

from generator import config
from generator.common import variant_paths, with_retry

from . import fal_api, mapowanie, porownanie, zadania
from .modele import DEFAULT_MODELS, MODELS
from .ujecia import (
    CHOSEN_DIR,
    DEFAULT_SHOTS,
    FRAMES_DIR,
    SHOTS,
    TEST_SHOTS,
    VIDEO_SHOTS,
    VIDEOS_DIR,
    frame_prompt,
    kardamon_path,
    portrait_path,
)
from .zadania import rel

EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def money(value) -> str:
    return f"${value:.2f}" if value is not None else "?"


# --- informacje -------------------------------------------------------------------------


def cmd_modele(_args):
    for model in MODELS.values():
        prices = ", ".join(f"{res} ${p:g}/s" for res, p in model.price.items()) or "cena nieznana"
        where = "Gemini API" if model.is_google else model.endpoints[0]
        print(f"{model.key:16} {model.name}")
        print(f"{'':16} {where} | tryb {model.mode} | {prices}")
        if model.note:
            print(f"{'':16} {model.note}")
    print(f"\nDomyślnie testowane: {', '.join(DEFAULT_MODELS)}")


def cmd_ujecia(_args):
    for key in [s.key for s in TEST_SHOTS] + [k for k in SHOTS if SHOTS[k].produkcja]:
        shot = SHOTS[key]
        state = "kadr wybrany" if shot.frame_path.exists() else "brak kadru"
        print(f"{key:18} {state:13} {shot.opis}")
    print(f"\nDomyślnie testowane: {', '.join(DEFAULT_SHOTS)}")
    print("Kadry ujęć testowych: python -m testy_fal kadry; sceny wersji krótkiej: python -m generator.images scenes")


def cmd_sprawdz(args):
    keys = args.modele or [k for k, m in MODELS.items() if not m.is_google]
    sample = SHOTS["poczta"]
    failed = 0
    for key in keys:
        model = MODELS[key]
        print(f"\n=== {key}: {model.name}")
        if model.is_google:
            print("  Gemini API (generator/videos.py): 360p/720p/1080p/4k, 3–10 s, kadr jako pierwsza klatka")
            continue
        try:
            endpoint, openapi = zadania.model_schema(model, refresh=args.odswiez)
            props, required, components = mapowanie.input_schema(openapi)
        except (fal_api.FalError, mapowanie.MappingError) as exc:
            print(f"  ! {exc}")
            failed += 1
            continue
        print(f"  endpoint: {endpoint}   (* = pole wymagane)")
        print("\n".join(mapowanie.describe_fields(props, required, components)))
        mapped = []
        for logical in mapowanie.CANDIDATES:
            name = mapowanie.choose_field(logical, props, model.fields)
            if logical in ("image", "references") and (logical == "image") != (model.mode == "i2v"):
                continue
            mapped.append(f"{mapowanie.LABELS[logical]} -> {name or '-'}")
        print("  nasze parametry: " + "; ".join(mapped))
        try:
            job = zadania.plan_job(sample, model, VIDEOS_DIR / "x.mp4", args.rozdzielczosc, args.czas,
                                   {key: (endpoint, openapi)})
        except mapowanie.MappingError as exc:
            print(f"  ! {exc}")
            failed += 1
            continue
        seconds = f"{job.seconds:g}" if job.seconds else "?"
        print(f"  przy {args.rozdzielczosc}, {args.czas:g} s: rozdzielczość {job.resolution or 'domyślna'}, "
              f"{seconds} s, ok. {money(job.cost)} za klip")
        for note in job.notes:
            print(f"  uwaga: {note}")
    if failed:
        sys.exit(f"\nModele z błędami: {failed} (powód przy każdym z nich powyżej).")


# --- kadry startowe ------------------------------------------------------------------------


def generate_frame(client, prompt: str, references: list, size: str):
    """Nano Banana Pro z kilkoma obrazami referencyjnymi (Mikołaj, Kardamon). Zwraca (bajty, mime)."""
    from google.genai import types

    contents: list = []
    for path in references:
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))
    contents.append(prompt)
    response = with_retry(
        lambda: client.models.generate_content(
            model=config.IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9", image_size=size),
            ),
        )
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else None) or []:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data, part.inline_data.mime_type or "image/png"
    reason = response.candidates[0].finish_reason if response.candidates else response.prompt_feedback
    raise RuntimeError(f"Model nie zwrócił obrazu (powód: {reason}).")


def cmd_kadry(args):
    from generator.common import google_client

    keys = args.only or [s.key for s in TEST_SHOTS]
    shots = [SHOTS[k] for k in keys]
    if any(not s.tylko_kadr for s in shots) and not portrait_path().exists():
        sys.exit(
            f"Brak portretu Mikołaja: {rel(portrait_path())}\n"
            "Najpierw: python -m generator.images portrait, potem: python -m generator.images select portrait N"
        )
    client = google_client()
    for shot in shots:
        refs = [] if shot.tylko_kadr else [portrait_path()]
        if shot.kardamon:
            if kardamon_path().exists():
                refs.append(kardamon_path())
            else:
                print(f"! [{shot.key}] brak wybranego portretu Kardamona: jego wygląd będzie się różnił między "
                      "ujęciami. Najpierw: kadry --only kardamon, potem: wybierz kardamon N")
        prompt = frame_prompt(shot, kardamon_path() in refs)
        print(f"[{shot.key}] {args.count} wariant(ów) -> {rel(FRAMES_DIR)}")
        for path in variant_paths(FRAMES_DIR, shot.key, ".png", args.count):
            try:
                data, mime = generate_frame(client, prompt, refs, args.size)
            except Exception as exc:
                print(f"  x {path.name}: {exc}")
                continue
            path = path.with_suffix(EXTENSIONS.get(mime, ".png"))
            path.write_bytes(data)
            print(f"  + {rel(path)}")
    print("Obejrzyj kadry i wybierz najlepsze: python -m testy_fal wybierz <ujęcie> <numer>")


def cmd_wybierz(args):
    matches = sorted(FRAMES_DIR.glob(f"{args.ujecie}_{args.numer:02d}.*"))
    if not matches:
        sys.exit(f"Nie ma kadru {args.ujecie}_{args.numer:02d} w {rel(FRAMES_DIR)}")
    target = CHOSEN_DIR / f"{args.ujecie}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    if matches[0].suffix == ".png":
        shutil.copyfile(matches[0], target)
    else:
        from PIL import Image

        Image.open(matches[0]).save(target)
    print(f"Wybrano {matches[0].name} -> {rel(target)}")


# --- generowanie wideo ---------------------------------------------------------------------


def missing_inputs(shots, models) -> list[str]:
    problems = []
    if any(m.mode == "i2v" for m in models):
        for shot in shots:
            if shot.frame_path.exists():
                continue
            fix = (f"python -m generator.images scenes --only {shot.key}, potem select {shot.key} N"
                   if shot.produkcja else
                   f"python -m testy_fal kadry --only {shot.key}, potem wybierz {shot.key} N")
            problems.append(f"  {rel(shot.frame_path)}: {fix}")
    if any(m.mode == "ref" for m in models) and not portrait_path().exists():
        problems.append(f"  {rel(portrait_path())}: python -m generator.images select portrait N")
    return problems


def print_plan(jobs) -> None:
    print(f"\nPlan: {len(jobs)} klip(ów)")
    print(f"  {'ujęcie':18} {'model':16} {'rozdz.':8} {'s':>4}  koszt")
    for job in jobs:
        seconds = f"{job.seconds:g}" if job.seconds else "?"
        print(f"  {job.shot.key:18} {job.model.key:16} {job.resolution or 'domyśl.':8} {seconds:>4}  {money(job.cost)}")
        for note in dict.fromkeys(job.notes):
            print(f"  {'':18} uwaga: {note}")
    known = [j.cost for j in jobs if j.cost is not None]
    unknown = sorted({j.model.key for j in jobs if j.cost is None})
    line = f"Szacowany koszt: {money(sum(known))}"
    if unknown:
        line += f" plus modele bez znanej ceny: {', '.join(unknown)}"
    print(line + " (szacunek; rozliczenie w panelu fal i Google)")


def cmd_generuj(args):
    models = [MODELS[k] for k in dict.fromkeys(args.modele)]
    shots = [SHOTS[k] for k in dict.fromkeys(args.ujecia)]

    problems = missing_inputs(shots, models)
    if problems:
        sys.exit("Brakuje kadrów:\n" + "\n".join(problems))
    if any(s.kardamon for s in shots) and any(m.mode == "ref" for m in models) and not kardamon_path().exists():
        print("! Brak portretu Kardamona: modele ref dostaną tylko portret Mikołaja.")

    schemas = {}
    for model in models:
        if model.is_google:
            continue
        try:
            schemas[model.key] = zadania.model_schema(model, refresh=args.odswiez)
        except fal_api.FalError as exc:
            print(f"! {exc}\n  pomijam model {model.key}")
    models = [m for m in models if m.is_google or m.key in schemas]

    jobs = []
    for shot in shots:
        for model in models:
            for out in variant_paths(VIDEOS_DIR / shot.key, model.key, ".mp4", args.count):
                try:
                    jobs.append(zadania.plan_job(shot, model, out, args.rozdzielczosc, args.czas, schemas))
                except mapowanie.MappingError as exc:
                    print(f"! [{shot.key}/{model.key}] {exc}")
                    break
    if not jobs:
        sys.exit("Nie ma nic do wygenerowania.")
    print_plan(jobs)

    if args.na_sucho:
        for job in jobs:
            print(f"\n--- {job.shot.key}/{job.model.key} -> {job.endpoint}")
            print(json.dumps(job.payload or {"prompt": job.prompt}, ensure_ascii=False, indent=2))
        print("\nTryb na sucho: nic nie wysłano.")
        return

    if any(not j.model.is_google for j in jobs):
        config.require_env("FAL_KEY")
    if any(j.model.is_google for j in jobs):
        config.require_env("GEMINI_API_KEY", "GOOGLE_API_KEY")
    if not args.tak:
        answer = input("Uruchomić? [t/N] ").strip().lower()
        if answer not in ("t", "tak", "y", "yes"):
            sys.exit("Przerwano, nic nie wysłano.")

    ok = zadania.run_all(jobs, args.rownolegle)
    print(f"\nGotowe: {ok} z {len(jobs)}. Klipy: {rel(VIDEOS_DIR)}/<ujęcie>/")
    print(f"Porównanie: python -m testy_fal porownaj --ujecia {' '.join(s.key for s in shots)}")


def cmd_wznow(_args):
    done, pending = zadania.resume()
    print("Brak przerwanych zapytań." if not pending else f"Dokończono {done} z {pending}.")


def cmd_porownaj(args):
    keys = args.ujecia or sorted(p.name for p in VIDEOS_DIR.glob("*") if p.is_dir())
    made = 0
    for key in keys:
        clips = porownanie.clips_for(key, args.modele)
        if not clips:
            print(f"[{key}] brak klipów")
            continue
        if len(clips) > porownanie.MAX_TILES:
            print(f"[{key}] {len(clips)} klipów, w siatce mieści się {porownanie.MAX_TILES}: użyj --modele")
        out = porownanie.COMPARE_DIR / f"{key}.mp4"
        porownanie.build_grid(clips, out)
        print(f"[{key}] + {rel(out)} ({min(len(clips), porownanie.MAX_TILES)} klipów)")
        made += 1
    if not made:
        sys.exit("Nie ma klipów do porównania: najpierw python -m testy_fal generuj")


def cmd_podsumowanie(_args):
    records = sorted(zadania.latest_by_job().values(), key=lambda r: r.get("czas", ""))
    if not records:
        sys.exit("Dziennik jest pusty: najpierw python -m testy_fal generuj")
    print(f"{'ujęcie':18} {'model':16} {'stan':8} {'s':>4} {'rozdz.':8} {'koszt':>7} {'gen.':>6}  plik / błąd")
    totals: dict[str, list] = {}
    for r in records:
        seconds = f"{r['sekundy']:g}" if r.get("sekundy") else "?"
        took = f"{r['czas_generowania_s']} s" if r.get("czas_generowania_s") else ""
        detail = r.get("plik", "") if r.get("stan") != "blad" else str(r.get("blad", ""))[:90].replace("\n", " ")
        print(f"{r.get('ujecie', '?'):18} {r.get('model', '?'):16} {r.get('stan', '?'):8} {seconds:>4} "
              f"{str(r.get('rozdzielczosc') or ''):8} {money(r.get('koszt_usd')):>7} {took:>6}  {detail}")
        total = totals.setdefault(r.get("model", "?"), [0, 0, 0.0])
        if r.get("stan") == "gotowe":
            total[0] += 1
            total[2] += r.get("koszt_usd") or 0
        elif r.get("stan") == "blad":
            total[1] += 1
    print("\nModel             gotowe  błędy  koszt (szacunek)")
    for key, (ok, errors, cost) in totals.items():
        print(f"{key:18} {ok:>6} {errors:>6}  {money(cost)}")
    print(f"Razem: {money(sum(t[2] for t in totals.values()))}")


# --- argumenty ------------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m testy_fal", description="Testy modeli wideo na fal.ai")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("modele", help="lista modeli z cenami").set_defaults(func=cmd_modele)
    sub.add_parser("ujecia", help="lista ujęć i stan kadrów").set_defaults(func=cmd_ujecia)

    def add_video_options(p):
        p.add_argument("--rozdzielczosc", default="1080p", help="zamawiana rozdzielczość (domyślnie 1080p)")
        p.add_argument("--czas", type=float, default=8, help="zamawiana długość klipu w sekundach (domyślnie 8)")
        p.add_argument("--odswiez", action="store_true", help="pobierz schematy modeli od nowa")

    p = sub.add_parser("sprawdz", help="schematy modeli i dopasowanie parametrów (bez kosztów)")
    p.add_argument("--modele", nargs="+", choices=list(MODELS))
    add_video_options(p)
    p.set_defaults(func=cmd_sprawdz)

    p = sub.add_parser("kadry", help="kadry startowe ujęć testowych (Nano Banana Pro)")
    p.add_argument("--only", nargs="+", choices=[s.key for s in TEST_SHOTS])
    p.add_argument("-n", "--count", type=int, default=3, help="liczba wariantów (domyślnie 3)")
    p.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])
    p.set_defaults(func=cmd_kadry)

    p = sub.add_parser("wybierz", help="zatwierdź kadr, np. wybierz kaczka 2")
    p.add_argument("ujecie", choices=[s.key for s in TEST_SHOTS])
    p.add_argument("numer", type=int)
    p.set_defaults(func=cmd_wybierz)

    p = sub.add_parser("generuj", help="wygeneruj klipy w wybranych modelach")
    p.add_argument("--modele", nargs="+", choices=list(MODELS), default=DEFAULT_MODELS)
    p.add_argument("--ujecia", nargs="+", choices=VIDEO_SHOTS, default=DEFAULT_SHOTS)
    p.add_argument("-n", "--count", type=int, default=1, help="warianty na model i ujęcie (domyślnie 1)")
    p.add_argument("--rownolegle", type=int, default=3, help="ile zapytań naraz (domyślnie 3)")
    p.add_argument("--na-sucho", action="store_true", help="pokaż plan i zapytania, nic nie wysyłaj")
    p.add_argument("--tak", action="store_true", help="nie pytaj o potwierdzenie")
    add_video_options(p)
    p.set_defaults(func=cmd_generuj)

    sub.add_parser("wznow", help="dokończ zapytania przerwane w trakcie").set_defaults(func=cmd_wznow)

    p = sub.add_parser("porownaj", help="siatki porównawcze MP4 (output/testy_fal/porownania/)")
    p.add_argument("--ujecia", nargs="+", choices=VIDEO_SHOTS)
    p.add_argument("--modele", nargs="+", choices=list(MODELS))
    p.set_defaults(func=cmd_porownaj)

    sub.add_parser("podsumowanie", help="czasy, koszty i błędy z dziennika").set_defaults(func=cmd_podsumowanie)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
