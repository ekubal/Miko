"""Kadry, klipy, postacie i szablony długich scenariuszy.

Przykłady (scenariusz domyślny: od_listu_do_san):
    python -m generator.scenariusze lista
    python -m generator.scenariusze opis                      # prompty do pliku scenariusze/..._prompty.md
    python -m generator.scenariusze postacie -n 4             # portret Płatka
    python -m generator.scenariusze wybierz platek 2
    python -m generator.scenariusze kadry --only kula poczta_sala -n 3
    python -m generator.scenariusze wybierz kula 1
    python -m generator.scenariusze wideo --only kula --resolution 360p
    python -m generator.scenariusze wybierz-wideo kula 2
    python -m generator.scenariusze szablony -n 2

Wyniki: output/<scenariusz>/{postacie,kadry,szablony,wideo}/, zatwierdzone w output/<scenariusz>/wybrane/.
Ujęcia z wersji krótkiej („reuse”) biorą pliki z output/selected/.
"""

import argparse
import shutil
import sys
from pathlib import Path

from .. import config
from ..common import selected_path, variant_paths
from . import SCENARIUSZE, get


def out_dir(sc) -> Path:
    return config.OUTPUT_DIR / sc.NAME


def chosen(sc, key: str, suffix: str = ".png") -> Path:
    shot = sc.SHOTS.get(key, {})
    if "reuse" in shot:
        return selected_path(shot["reuse"], suffix)
    return out_dir(sc) / "wybrane" / f"{key}{suffix}"


def rel(path: Path) -> str:
    return str(path.relative_to(config.ROOT)) if path.is_relative_to(config.ROOT) else str(path)


# --- opis i lista -------------------------------------------------------------------------


def render_markdown(sc, seconds: int = 8) -> str:
    lines = [
        f"# Prompty: {sc.TITLE}",
        "",
        f"Wygenerowane z `generator/scenariusze/{sc.NAME}.py` poleceniem "
        "`python -m generator.scenariusze opis`. Nie edytuj ręcznie: zmieniaj moduł i wygeneruj plik ponownie.",
        "",
        f"Scenariusz: [`{sc.DOC}`](../{sc.DOC.split('/', 1)[1]}). Kadry: Nano Banana Pro z portretem Mikołaja "
        "(i portretem Płatka) jako obrazami wzorcowymi. Klipy: Gemini Omni Flash, kadr jako pierwsza klatka.",
        "",
        "## Postacie",
        "",
    ]
    for key, ch in sc.CHARACTERS.items():
        lines += [f"### `{key}`: {ch['opis']}", "", "```", ch["prompt"], "```", ""]
    current = None
    for key, shot in sc.SHOTS.items():
        if shot["scena"] != current:
            current = shot["scena"]
            lines += [f"## Scena {current}", ""]
        lines += [f"### `{key}`: {shot['opis']}", ""]
        if "reuse" in shot:
            lines += [f"Gotowe ujęcie z wersji krótkiej: `{shot['reuse']}` (prompt w `generator/prompts.py`).", ""]
            continue
        refs = ["portret Mikołaja"] if shot.get("santa", True) else []
        if shot.get("platek"):
            refs.append("portret Płatka")
        lines += [f"Obrazy wzorcowe: {', '.join(refs) or 'brak'}.", "", "**Kadr:**", "", "```",
                  sc.frame_prompt(key), "```", ""]
        if shot.get("wideo", True):
            secs = shot.get("sekundy", seconds)
            lines += [f"**Ruch ({secs} s):**", "", "```", sc.motion_prompt(key, secs), "```", ""]
        else:
            lines += ["Bez klipu z AI: kadr jest obrazem wejściowym dla HeyGen.", ""]
    lines += ["## Szablony", ""]
    for key, tpl in sc.TEMPLATES.items():
        lines += [f"### `{key}` (scena {tpl['scena']}): {tpl['opis']}", "", "```", tpl["prompt"], "```", ""]
    for key, scene_no in getattr(sc, "REUSED_TEMPLATES", {}).items():
        lines += [f"### `{key}` (scena {scene_no}): z wersji krótkiej", "",
                  "Prompt w `generator/prompts.py` (TEMPLATES).", ""]
    return "\n".join(lines).rstrip() + "\n"


def prompts_doc_path(sc) -> Path:
    stem = Path(sc.DOC).stem
    return config.ROOT / "scenariusze" / f"{stem}_prompty.md"


def cmd_opis(sc, args):
    path = Path(args.plik) if args.plik else prompts_doc_path(sc)
    path.write_text(render_markdown(sc), encoding="utf-8")
    print(f"Zapisano {rel(path)}")


def cmd_lista(sc, args):
    print(f"{sc.TITLE}: {len(sc.SHOTS)} ujęć, {len(sc.video_shots())} nowych klipów do wygenerowania\n")
    for key, ch in sc.CHARACTERS.items():
        state = "wybrany" if chosen(sc, key).exists() else "brak"
        print(f"postać  {key:18} {state:8} {ch['opis']}")
    for key, shot in sc.SHOTS.items():
        frame = "kadr ✓" if chosen(sc, key).exists() else "kadr –"
        if shot.get("wideo", True):
            clip = "klip ✓" if chosen(sc, key, ".mp4").exists() else "klip –"
        else:
            clip = "HeyGen"
        source = f"[z wersji krótkiej: {shot['reuse']}] " if "reuse" in shot else ""
        print(f"sc.{shot['scena']:<3} {key:18} {frame} {clip}  {source}{shot['opis']}")
    for key, tpl in sc.TEMPLATES.items():
        state = "wybrany" if chosen(sc, key).exists() else "brak"
        print(f"szablon {key:18} {state:8} {tpl['opis']}")


# --- generowanie -------------------------------------------------------------------------


def generate(sc, name: str, prompt: str, folder: str, refs: list[Path], args) -> None:
    from ..common import google_client
    from ..images import EXTENSIONS, generate_image

    directory = out_dir(sc) / folder
    print(f"[{name}] {args.count} wariant(ów) -> {rel(directory)}")
    client = google_client()
    for path in variant_paths(directory, name, ".png", args.count):
        try:
            data, mime = generate_image(client, prompt, refs or None, "16:9", args.size)
        except Exception as exc:
            print(f"  x {path.name}: {exc}")
            continue
        path = path.with_suffix(EXTENSIONS.get(mime, ".png"))
        path.write_bytes(data)
        print(f"  + {rel(path)}")


def cmd_postacie(sc, args):
    for key in args.only or list(sc.CHARACTERS):
        generate(sc, key, sc.CHARACTERS[key]["prompt"], "postacie", [], args)


def cmd_kadry(sc, args):
    keys = args.only or sc.new_frame_shots()
    portrait = selected_path("portrait")
    platek = chosen(sc, "platek")
    for key in keys:
        shot = sc.SHOTS[key]
        if "reuse" in shot:
            print(f"[{key}] gotowy kadr z wersji krótkiej: {rel(selected_path(shot['reuse']))}")
            continue
        refs = []
        if sc.needs_santa_reference(key):
            if not portrait.exists():
                sys.exit(f"Brak portretu Mikołaja: {rel(portrait)} (python -m generator.images select portrait N)")
            refs.append(portrait)
        if shot.get("platek"):
            if platek.exists():
                refs.append(platek)
            else:
                print(f"! [{key}] brak wybranego portretu Płatka: jego wygląd może się różnić między ujęciami.\n"
                      "  Najpierw: postacie, potem: wybierz platek N")
        generate(sc, key, sc.frame_prompt(key, platek in refs), "kadry", refs, args)


def cmd_szablony(sc, args):
    for key in args.only or list(sc.TEMPLATES):
        generate(sc, key, sc.TEMPLATES[key]["prompt"], "szablony", [], args)


def cmd_wybierz(sc, args):
    folders = ["postacie", "kadry", "szablony"]
    matches = [p for f in folders for p in sorted((out_dir(sc) / f).glob(f"{args.klucz}_{args.numer:02d}.*"))]
    if not matches:
        sys.exit(f"Nie ma {args.klucz}_{args.numer:02d} w {rel(out_dir(sc))}/{{{','.join(folders)}}}")
    target = out_dir(sc) / "wybrane" / f"{args.klucz}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    if matches[0].suffix == ".png":
        shutil.copyfile(matches[0], target)
    else:
        from PIL import Image

        Image.open(matches[0]).save(target)
    print(f"Wybrano {matches[0].name} -> {rel(target)}")


def cmd_wideo(sc, args):
    from .. import videos
    from ..common import google_client

    keys = args.only or sc.video_shots()
    skipped = [k for k in keys if "reuse" in sc.SHOTS[k] or not sc.SHOTS[k].get("wideo", True)]
    for k in skipped:
        print(f"[{k}] pomijam: " + ("klip z wersji krótkiej" if "reuse" in sc.SHOTS[k] else "tylko kadr dla HeyGen"))
    keys = [k for k in keys if k not in skipped]
    missing = [k for k in keys if not chosen(sc, k).exists()]
    if missing:
        sys.exit(f"Brak zatwierdzonych kadrów: {', '.join(missing)}. Najpierw: kadry, potem: wybierz <klucz> N")
    client = google_client()
    for key in keys:
        seconds = args.duration or sc.SHOTS[key].get("sekundy", 8)
        prompt = sc.motion_prompt(key, seconds)
        print(f"[{key}] {args.count} klip(ów), {config.VIDEO_MODEL}, {args.resolution}, {seconds} s")
        frame = videos.upload_frame(client, chosen(sc, key))
        for out in variant_paths(out_dir(sc) / "wideo", key, ".mp4", args.count):
            try:
                videos.generate_clip(client, prompt, frame, args.resolution, seconds, out)
                print(f"  + {rel(out)}")
            except Exception as exc:
                print(f"  x {out.name}: {exc}")


def cmd_wybierz_wideo(sc, args):
    source = out_dir(sc) / "wideo" / f"{args.klucz}_{args.numer:02d}.mp4"
    if not source.exists():
        sys.exit(f"Nie ma klipu {rel(source)}")
    target = out_dir(sc) / "wybrane" / f"{args.klucz}.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Wybrano {source.name} -> {rel(target)}")


def main(argv=None):
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("-s", "--scenariusz", default="od_listu_do_san", choices=list(SCENARIUSZE))
    sc = get(pre.parse_known_args(argv)[0].scenariusz)

    parser = argparse.ArgumentParser(prog="python -m generator.scenariusze", description="Długie scenariusze filmu",
                                     parents=[pre])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("lista", help="ujęcia, postacie, szablony i ich stan").set_defaults(func=cmd_lista)

    p = sub.add_parser("opis", help="zapisz wszystkie prompty do pliku Markdown")
    p.add_argument("--plik", help="ścieżka pliku (domyślnie scenariusze/<scenariusz>_prompty.md)")
    p.set_defaults(func=cmd_opis)

    def images_opts(p, choices):
        p.add_argument("--only", nargs="+", choices=choices)
        p.add_argument("-n", "--count", type=int, default=3, help="liczba wariantów (domyślnie 3)")
        p.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])

    p = sub.add_parser("postacie", help="portrety wzorcowe postaci (np. Płatek)")
    images_opts(p, list(sc.CHARACTERS))
    p.set_defaults(func=cmd_postacie)

    p = sub.add_parser("kadry", help="kadry startowe ujęć")
    images_opts(p, list(sc.SHOTS))
    p.set_defaults(func=cmd_kadry)

    p = sub.add_parser("szablony", help="szablony do montażu (kula, ramka, list, bilecik)")
    images_opts(p, list(sc.TEMPLATES))
    p.set_defaults(func=cmd_szablony)

    every = [*sc.CHARACTERS, *sc.SHOTS, *sc.TEMPLATES]
    p = sub.add_parser("wybierz", help="zatwierdź postać, kadr albo szablon, np. wybierz kula 2")
    p.add_argument("klucz", choices=every)
    p.add_argument("numer", type=int)
    p.set_defaults(func=cmd_wybierz)

    p = sub.add_parser("wideo", help="klipy z zatwierdzonych kadrów")
    p.add_argument("--only", nargs="+", choices=list(sc.SHOTS))
    p.add_argument("-n", "--count", type=int, default=1, help="liczba wariantów (domyślnie 1)")
    p.add_argument("--resolution", default="1080p", choices=["360p", "720p", "1080p", "4k"])
    p.add_argument("--duration", type=int, choices=range(3, 11), metavar="3-10",
                   help="sekundy klipu (domyślnie z ujęcia, zwykle 8)")
    p.set_defaults(func=cmd_wideo)

    p = sub.add_parser("wybierz-wideo", help="zatwierdź klip, np. wybierz-wideo kula 2")
    p.add_argument("klucz", choices=sc.video_shots())
    p.add_argument("numer", type=int)
    p.set_defaults(func=cmd_wybierz_wideo)

    args = parser.parse_args(argv)
    args.func(sc, args)


if __name__ == "__main__":
    main()
