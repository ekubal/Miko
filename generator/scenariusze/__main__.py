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

Reklama zapisów (pionowa, trzy warianty, głos Mikołaja do rodziców):
    python -m generator.scenariusze -s reklama_zapisy lista
    python -m generator.scenariusze -s reklama_zapisy kadry --only w1_mowi -n 3
    python -m generator.scenariusze -s reklama_zapisy kwestie --only w1_1 w1_2

Wyniki: output/<scenariusz>/{postacie,kadry,szablony,wideo,glos}/, zatwierdzone w output/<scenariusz>/wybrane/.
Ujęcia z wersji krótkiej („reuse”) biorą pliki z output/selected/.
"""

import argparse
import shutil
import sys
from pathlib import Path

from .. import config
from ..common import selected_path, variant_paths
from . import SCENARIUSZE, get

DEFAULT = "od_listu_do_san"


def out_dir(sc) -> Path:
    return config.OUTPUT_DIR / sc.NAME


def aspect(sc) -> str:
    return getattr(sc, "ASPECT", "16:9")


def option(sc) -> str:
    # Przełącznik -s w podpowiedziach poleceń; scenariusz domyślny go nie potrzebuje.
    return "" if sc.NAME == DEFAULT else f"-s {sc.NAME} "


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
        f"`python -m generator.scenariusze {option(sc)}opis`. Nie edytuj ręcznie: zmieniaj moduł i wygeneruj "
        "plik ponownie.",
        "",
        f"Scenariusz: [`{sc.DOC}`]({Path(sc.DOC).name}). Kadry: Nano Banana Pro z portretem Mikołaja "
        "(i portretem Płatka) jako obrazami wzorcowymi. Klipy: Gemini Omni Flash, kadr jako pierwsza klatka.",
        "",
    ]
    if aspect(sc) != "16:9":
        lines += [f"Format kadrów i klipów: {aspect(sc)}.", ""]
    if sc.CHARACTERS:
        lines += ["## Postacie", ""]
    for key, ch in sc.CHARACTERS.items():
        lines += [f"### `{key}`: {ch['opis']}", "", "```", ch["prompt"], "```", ""]
    titles = getattr(sc, "SCENE_TITLES", {})
    current = None
    for key, shot in sc.SHOTS.items():
        if shot["scena"] != current:
            current = shot["scena"]
            lines += [f"## {titles.get(current, f'Scena {current}')}", ""]
        lines += [f"### `{key}`: {shot['opis']}", ""]
        if "reuse" in shot:
            lines += [f"Gotowe ujęcie z wersji krótkiej: `{shot['reuse']}` (prompt w `generator/prompts.py`).", ""]
            continue
        refs = ["portret Mikołaja"] if shot.get("santa", True) else []
        if shot.get("platek"):
            refs.append("portret Płatka")
        if hasattr(sc, "extra_references"):
            refs.append("zatwierdzony kadr pionowy, jeśli jest")
        lines += [f"Obrazy wzorcowe: {', '.join(refs) or 'brak'}.", "", "**Kadr:**", "", "```",
                  sc.frame_prompt(key), "```", ""]
        if shot.get("wideo", True):
            secs = shot.get("sekundy", seconds)
            lines += [f"**Ruch ({secs} s):**", "", "```", sc.motion_prompt(key, secs), "```", ""]
        elif shot.get("heygen"):
            lines += ["Bez klipu z AI: kadr jest obrazem wejściowym dla HeyGen.", "",
                      "**HeyGen (Avatar IV, opis ruchu):**", "", "```", shot["heygen"], "```", ""]
        else:
            lines += ["Bez klipu z AI: kadr jest obrazem wejściowym dla HeyGen.", ""]
    if getattr(sc, "KWESTIE", None):
        lines += ["## Kwestie Mikołaja (ElevenLabs)", "",
                  f"Nagrania: `python -m generator.scenariusze {option(sc)}kwestie`.", ""]
        for key, line in sc.KWESTIE.items():
            lines += [f"- `{key}` ({line['ujecie']}): {line['tekst']}"]
        lines += [""]
    if not sc.TEMPLATES and not getattr(sc, "REUSED_TEMPLATES", {}):
        return "\n".join(lines).rstrip() + "\n"
    lines += ["## Szablony", ""]
    for key, tpl in sc.TEMPLATES.items():
        lines += [f"### `{key}` (scena {tpl['scena']}): {tpl['opis']}", "", "```", tpl["prompt"], "```", ""]
    for key, scene_no in getattr(sc, "REUSED_TEMPLATES", {}).items():
        lines += [f"### `{key}` (scena {scene_no}): z wersji krótkiej", "",
                  "Prompt w `generator/prompts.py` (TEMPLATES).", ""]
    return "\n".join(lines).rstrip() + "\n"


def prompts_doc_path(sc) -> Path:
    if hasattr(sc, "PROMPTY"):
        return config.ROOT / sc.PROMPTY
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
            data, mime, _cost = generate_image(client, prompt, refs, aspect(sc), args.size)
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
    # Scenariusz może korzystać z portretu Płatka zatwierdzonego w innym (PLATEK_FROM).
    platek = chosen(get(getattr(sc, "PLATEK_FROM", sc.NAME)), "platek")
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
        if hasattr(sc, "extra_references"):
            # Np. wersja pozioma reklamy: zatwierdzony kadr pionowy jako ostatni obraz wzorcowy.
            extra = sc.extra_references(key)
            if not extra:
                print(f"! [{key}] brak zatwierdzonego kadru pionowego: kadr poziomy może wyglądać inaczej.")
            refs += extra
            prompt = sc.frame_prompt(key, platek in refs, bool(extra))
        else:
            prompt = sc.frame_prompt(key, platek in refs)
        generate(sc, key, prompt, "kadry", refs, args)


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
                videos.generate_clip(client, prompt, frame, args.resolution, seconds, out, aspect(sc))
                print(f"  + {rel(out)}")
            except Exception as exc:
                print(f"  x {out.name}: {exc}")


def cmd_kwestie(sc, args):
    from ..audio import speak

    lines = getattr(sc, "KWESTIE", {})
    if not lines:
        sys.exit(f"Scenariusz {sc.NAME} nie ma kwestii do nagrania (kwestie wspólne: python -m generator.audio lines).")
    # Scenariusz może dzielić nagrania z innym (GLOS_FROM), np. wersja pozioma z pionową.
    target = get(getattr(sc, "GLOS_FROM", sc.NAME))
    for key in args.only or list(lines):
        out = out_dir(target) / "glos" / f"{key}.mp3"
        if out.exists() and not args.force:
            print(f"  = {rel(out)} (istnieje, użyj --force)")
            continue
        speak(lines[key]["tekst"], out)


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
    pre.add_argument("-s", "--scenariusz", default=DEFAULT, choices=list(SCENARIUSZE))
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

    p = sub.add_parser("kwestie", help="nagraj kwestie Mikołaja scenariusza (ElevenLabs), np. dla reklama_zapisy")
    p.add_argument("--only", nargs="+", choices=list(getattr(sc, "KWESTIE", {})) or None)
    p.add_argument("--force", action="store_true", help="nadpisz istniejące nagrania")
    p.set_defaults(func=cmd_kwestie)

    args = parser.parse_args(argv)
    args.func(sc, args)


if __name__ == "__main__":
    main()
