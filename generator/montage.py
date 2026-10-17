"""Automatyczny montaż filmu dla zamówienia (ffmpeg + Pillow).

Zastępuje ręczną pracę w CapCut / DaVinci Resolve (krok 5 produkcji): skleja sceny
ogólne, klip z HeyGen, księgę ze zdjęciem dziecka i listę z imieniem, podkłada
kwestie, muzykę ściszaną pod głosem i eksportuje MP4 1080p.

Przykłady:
    python -m generator.montage calibrate        # podgląd ramki i imienia na szablonach
    python -m generator.montage build examples/zamowienie_kasia.json

Wymagane pliki zamówienia: output/orders/<id>/heygen.mp4 (klip z HeyGen) oraz zdjęcia
dzieci wskazane w polu "zdjecie" (ścieżka względem pliku JSON zamówienia).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from . import config
from .common import selected_path
from .order import load_order, order_dir

LAYOUT_FILE = config.ROOT / "layout.json"
FADE = 0.5  # przejście przez czerń na początku i końcu każdej sceny
VOICE_TAIL = 1.5  # cisza po kwestii, zanim scena się skończy
MAX_SLOWDOWN = 1.8  # klip 8 s można spowolnić najwyżej tyle razy; dalej stopklatka
BOOK_CLIP_SECONDS = 7.0  # ile klipu z otwieraniem księgi pokazać przed zbliżeniem na zdjęcie
MUSIC_VOLUME = 0.35
AMBIENT_VOLUME = 0.35

# Minimalne długości scen i moment wejścia głosu, według harmonogramu z MVP.md.
SCENE_TIMING = {
    "dom": {"min": 15.0, "voice_at": 3.0},
    "pracownia": {"min": 20.0, "voice_at": 1.0},
    "ksiega": {"min": 20.0, "voice_at": 1.5},
    "lista": {"min": 15.0, "voice_at": 1.0},
    "sanie": {"min": 20.0, "voice_at": 1.0},
}


@dataclass
class Format:
    width: int = 1920
    height: int = 1080
    fps: int = 25
    crf: int = 18
    preset: str = "medium"


@dataclass
class Assets:
    """Materiały wspólne dla wszystkich filmów (z przygotowania jednorazowego)."""

    clips: dict[str, Path]  # dom, pracownia, ksiega, sanie
    lines: dict[str, Path]  # scena1_dom, scena2_pracownia, scena4_ksiega, scena5_lista, scena6_pozegnanie
    book_template: Path
    list_template: Path
    music: Path | None
    layout: dict = field(default_factory=dict)
    font: Path | None = None

    def missing(self) -> list[Path]:
        paths = [*self.clips.values(), *self.lines.values(), self.book_template, self.list_template]
        if self.music:
            paths.append(self.music)
        if self.font:
            paths.append(self.font)
        return [p for p in paths if not p.exists()]


def load_layout() -> dict:
    return json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))


def resolve_font(layout: dict) -> Path:
    font = Path(os.environ.get("MIKOLAJ_FONT") or layout["font"])
    return font if font.is_absolute() else config.ROOT / font


def default_assets(siblings: bool, music: Path | None) -> Assets:
    suffix = "_rodzenstwo" if siblings else ""
    lines_dir = config.AUDIO_DIR / "lines"
    layout = load_layout()
    return Assets(
        clips={key: selected_path(key, ".mp4") for key in ("dom", "pracownia", "ksiega", "sanie")},
        lines={
            key: lines_dir / f"{key}{suffix}.mp3"
            for key in ("scena1_dom", "scena2_pracownia", "scena4_ksiega", "scena5_lista", "scena6_pozegnanie")
        },
        book_template=selected_path("szablon_ksiega"),
        list_template=selected_path("szablon_lista"),
        music=music,
        layout=layout,
        font=resolve_font(layout),
    )


# --- ffmpeg -------------------------------------------------------------------


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg zakończył się błędem:\n{' '.join(cmd)}\n{result.stderr[-2000:]}")


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def has_audio(path: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return bool(out)


def normalize(fmt: Format) -> str:
    return (
        f"scale={fmt.width}:{fmt.height}:force_original_aspect_ratio=increase,"
        f"crop={fmt.width}:{fmt.height},setsar=1,fps={fmt.fps},format=yuv420p"
    )


def ken_burns(fmt: Format, duration: float, zoom: float = 0.08) -> str:
    """Powolne przybliżenie nieruchomego obrazu (wejście: obraz zapętlony z -loop 1)."""
    frames = max(1, round(duration * fmt.fps))
    return (
        f"scale={fmt.width * 2}:{fmt.height * 2},"
        f"zoompan=z='1+{zoom}*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d=1:s={fmt.width}x{fmt.height}:fps={fmt.fps},setsar=1,format=yuv420p"
    )


@dataclass
class AudioPart:
    input_index: int
    delay: float = 0.0
    volume: float = 1.0
    duration: float | None = None  # przytnij do tylu sekund


def render_segment(
    out: Path,
    inputs: list[list[str]],
    video_graph: str,
    audio: list[AudioPart],
    duration: float,
    fmt: Format,
) -> None:
    """Koduje jedną scenę. `video_graph` musi kończyć się etykietą [v]."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for inp in inputs:
        cmd += inp
    # Cicha ścieżka gwarantuje dźwięk o dokładnej długości sceny, nawet bez kwestii.
    silent = len(inputs)
    cmd += ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    parts = [*audio, AudioPart(silent)]

    graph = [video_graph]
    graph.append(
        f"[v]trim=duration={duration:.3f},setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d={FADE},fade=t=out:st={duration - FADE:.3f}:d={FADE}[vout]"
    )
    labels = []
    for i, part in enumerate(parts):
        chain = f"[{part.input_index}:a]aresample=48000,aformat=channel_layouts=stereo"
        if part.duration is not None:
            chain += f",atrim=0:{part.duration:.3f}"
        chain += f",volume={part.volume}"
        if part.delay:
            chain += f",adelay={int(part.delay * 1000)}:all=1"
        graph.append(f"{chain}[a{i}]")
        labels.append(f"[a{i}]")
    graph.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,"
        f"apad,atrim=0:{duration:.3f},afade=t=in:d=0.3,afade=t=out:st={duration - FADE:.3f}:d={FADE}[aout]"
    )
    cmd += ["-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]"]
    cmd += encode_args(fmt) + [str(out)]
    run(cmd)


def encode_args(fmt: Format) -> list[str]:
    return [
        "-c:v", "libx264", "-preset", fmt.preset, "-crf", str(fmt.crf), "-pix_fmt", "yuv420p",
        "-r", str(fmt.fps), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    ]


def scene_duration(scene: str, voice: Path) -> float:
    timing = SCENE_TIMING[scene]
    return max(timing["min"], timing["voice_at"] + probe_duration(voice) + VOICE_TAIL)


def clip_ambient(clip: Path, index: int, duration: float | None = None) -> list[AudioPart]:
    return [AudioPart(index, volume=AMBIENT_VOLUME, duration=duration)] if has_audio(clip) else []


# --- sceny --------------------------------------------------------------------


def segment_clip(scene: str, clip: Path, voice: Path, out: Path, fmt: Format) -> None:
    """Klip Veo z kwestią. Krótszy klip jest spowalniany, a dalej zatrzymany na ostatniej klatce."""
    duration = scene_duration(scene, voice)
    slowdown = min(max(duration / probe_duration(clip), 1.0), MAX_SLOWDOWN)
    video = (
        f"[0:v]setpts={slowdown:.4f}*PTS,{normalize(fmt)},"
        f"tpad=stop_mode=clone:stop_duration={duration:.3f}[v]"
    )
    audio = clip_ambient(clip, 0) + [AudioPart(1, delay=SCENE_TIMING[scene]["voice_at"])]
    render_segment(out, [["-i", str(clip)], ["-i", str(voice)]], video, audio, duration, fmt)


def segment_heygen(clip: Path, out: Path, fmt: Format) -> None:
    if not has_audio(clip):
        raise RuntimeError(f"Klip z HeyGen nie ma dźwięku: {clip}")
    duration = probe_duration(clip)
    render_segment(out, [["-i", str(clip)]], f"[0:v]{normalize(fmt)}[v]", [AudioPart(0)], duration, fmt)


def segment_book(clip: Path, page: Path, voice: Path, out: Path, fmt: Format) -> None:
    """Mikołaj otwiera księgę (klip), potem przenikanie do zbliżenia na zdjęcie w ramce."""
    duration = scene_duration("ksiega", voice)
    clip_part = min(probe_duration(clip), BOOK_CLIP_SECONDS)
    still_part = duration - clip_part + 1.0  # 1 s nakładki przenikania
    video = (
        f"[0:v]{normalize(fmt)},trim=duration={clip_part:.3f},setpts=PTS-STARTPTS[c];"
        f"[1:v]{ken_burns(fmt, still_part)},trim=duration={still_part:.3f},setpts=PTS-STARTPTS[s];"
        f"[c][s]xfade=transition=fade:duration=1:offset={clip_part - 1:.3f}[v]"
    )
    inputs = [
        ["-i", str(clip)],
        ["-loop", "1", "-framerate", str(fmt.fps), "-t", f"{still_part:.3f}", "-i", str(page)],
        ["-i", str(voice)],
    ]
    audio = clip_ambient(clip, 0, clip_part) + [AudioPart(2, delay=SCENE_TIMING["ksiega"]["voice_at"])]
    render_segment(out, inputs, video, audio, duration, fmt)


def segment_list(scroll: Path, names: Path, voice: Path, out: Path, fmt: Format) -> None:
    """Pergamin; imię pojawia się, gdy Mikołaj mówi, że jest zapisane."""
    duration = scene_duration("lista", voice)
    voice_at = SCENE_TIMING["lista"]["voice_at"]
    reveal = voice_at + 0.35 * probe_duration(voice)
    video = (
        f"[1:v]format=rgba,fade=t=in:st={reveal:.3f}:d=1.5:alpha=1[n];"
        f"[0:v][n]overlay=0:0:format=auto,{ken_burns(fmt, duration)}[v]"
    )
    loop = ["-loop", "1", "-framerate", str(fmt.fps), "-t", f"{duration:.3f}", "-i"]
    inputs = [loop + [str(scroll)], loop + [str(names)], ["-i", str(voice)]]
    render_segment(out, inputs, video, [AudioPart(2, delay=voice_at)], duration, fmt)


# --- grafiki ------------------------------------------------------------------


def frac_box(box: list[float], size: tuple[int, int]) -> tuple[int, int, int, int]:
    w, h = size
    return int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)


def compose_book(template: Path, photos: list[Path], layout: dict) -> Image.Image:
    """Wkleja zdjęcia dzieci w ramkę księgi (obok siebie dla rodzeństwa) z ciepłą poświatą."""
    base = Image.open(template).convert("RGBA")
    x0, y0, x1, y1 = frac_box(layout["ksiega_ramka"], base.size)
    gap = int((x1 - x0) * 0.04) if len(photos) > 1 else 0
    slot_w = (x1 - x0 - gap * (len(photos) - 1)) // len(photos)
    glow_size = max(4, int(base.width * 0.012))

    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for i in range(len(photos)):
        sx = x0 + i * (slot_w + gap)
        draw.rectangle(
            (sx - glow_size, y0 - glow_size, sx + slot_w + glow_size, y1 + glow_size),
            fill=layout.get("kolor_poswiaty", "#ffd27a"),
        )
    glow.putalpha(glow.getchannel("A").point(lambda a: a * 0.7))
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(glow_size * 1.5)))

    for i, photo in enumerate(photos):
        img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
        # Twarz jest zwykle w górnej części zdjęcia, więc kadrujemy lekko powyżej środka.
        img = ImageOps.fit(img, (slot_w, y1 - y0), centering=(0.5, 0.4))
        base.paste(img, (x0 + i * (slot_w + gap), y0))
    return base.convert("RGB")


def render_names(size: tuple[int, int], names: list[str], layout: dict, font_path: Path | None) -> Image.Image:
    """Przezroczysta warstwa z imionami (jedno pod drugim), dopasowana do pola na liście."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = frac_box(layout["lista_imiona"], size)
    box_w, box_h = x1 - x0, y1 - y0

    def load(font_size):
        if font_path is None:
            return ImageFont.load_default(font_size)
        return ImageFont.truetype(str(font_path), font_size)

    font_size = int(box_h / len(names) * 0.85)
    while font_size > 8:
        font = load(font_size)
        widths = [draw.textbbox((0, 0), n, font=font)[2] for n in names]
        if max(widths) <= box_w * 0.95:
            break
        font_size = int(font_size * 0.92)

    line_h = box_h / len(names)
    for i, name in enumerate(names):
        cx, cy = x0 + box_w / 2, y0 + line_h * (i + 0.5)
        draw.text((cx, cy), name, font=font, fill=layout.get("kolor_imienia", "#3b2412"), anchor="mm")
    return layer


# --- składanie filmu ----------------------------------------------------------


def child_photos(order: dict, order_file: Path) -> list[Path]:
    photos = []
    for child in order["dzieci"]:
        if not child.get("zdjecie"):
            sys.exit(f"Brak pola 'zdjecie' dla dziecka {child.get('imie')} w {order_file}.")
        path = Path(child["zdjecie"])
        photos.append(path if path.is_absolute() else order_file.parent / path)
    return photos


def assemble(order: dict, photos: list[Path], heygen: Path, assets: Assets, out: Path, fmt: Format, keep_temp=False):
    missing = assets.missing() + [p for p in [heygen, *photos] if not p.exists()]
    if missing:
        raise FileNotFoundError("Brakuje plików:\n" + "\n".join(f"  - {p}" for p in missing))

    work = out.parent / "montage_tmp"
    work.mkdir(parents=True, exist_ok=True)
    try:
        page = work / "ksiega.png"
        compose_book(assets.book_template, photos, assets.layout).save(page)
        scroll = Image.open(assets.list_template).convert("RGB")
        scroll.save(work / "lista.png")
        render_names(scroll.size, [c["imie"] for c in order["dzieci"]], assets.layout, assets.font).save(
            work / "imiona.png"
        )

        segments = [work / f"{i}.mp4" for i in range(1, 7)]
        steps = [
            ("dom", lambda: segment_clip("dom", assets.clips["dom"], assets.lines["scena1_dom"], segments[0], fmt)),
            ("pracownia", lambda: segment_clip(
                "pracownia", assets.clips["pracownia"], assets.lines["scena2_pracownia"], segments[1], fmt)),
            ("heygen", lambda: segment_heygen(heygen, segments[2], fmt)),
            ("księga", lambda: segment_book(
                assets.clips["ksiega"], page, assets.lines["scena4_ksiega"], segments[3], fmt)),
            ("lista", lambda: segment_list(
                work / "lista.png", work / "imiona.png", assets.lines["scena5_lista"], segments[4], fmt)),
            ("sanie", lambda: segment_clip(
                "sanie", assets.clips["sanie"], assets.lines["scena6_pozegnanie"], segments[5], fmt)),
        ]
        for i, (name, step) in enumerate(steps, 1):
            print(f"  [{i}/6] {name}")
            step()

        concat_list = work / "sceny.txt"
        concat_list.write_text("".join(f"file '{s.resolve()}'\n" for s in segments), encoding="utf-8")
        joined = work / "sceny.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat_list), "-c", "copy", str(joined)])
        add_music(joined, assets.music, out)
    finally:
        if not keep_temp:
            shutil.rmtree(work, ignore_errors=True)
    print(f"Gotowe: {out} ({probe_duration(out):.0f} s)")


def add_music(video: Path, music: Path | None, out: Path) -> None:
    """Podkład pod całym filmem, automatycznie ściszany, gdy Mikołaj mówi."""
    base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video)]
    if music is None:
        run(base + ["-c", "copy", "-movflags", "+faststart", str(out)])
        return
    total = probe_duration(video)
    graph = (
        "[0:a]asplit=2[mowa][sc];"
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={MUSIC_VOLUME},atrim=0:{total:.3f}[muz];"
        "[muz][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=600[cicha];"
        f"[mowa][cicha]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={max(total - 3, 0):.3f}:d=3[a]"
    )
    run(base + ["-stream_loop", "-1", "-i", str(music), "-filter_complex", graph,
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(out)])


# --- CLI ----------------------------------------------------------------------


def cmd_build(args):
    if not shutil.which("ffmpeg"):
        sys.exit("Brak ffmpeg. Zainstaluj go (np. brew install ffmpeg / apt install ffmpeg).")
    order_file = Path(args.order)
    order = load_order(args.order)
    directory = order_dir(order)
    music = None if args.no_music else Path(args.music) if args.music else selected_path("podklad", ".mp3")
    assets = default_assets(len(order["dzieci"]) > 1, music)
    heygen = Path(args.heygen) if args.heygen else directory / "heygen.mp4"
    out = directory / f"film_{order['id']}.mp4"
    fmt = Format(preset=args.preset)
    print(f"Montaż zamówienia {order['id']} -> {out}")
    try:
        assemble(order, child_photos(order, order_file), heygen, assets, out, fmt, args.keep_temp)
    except FileNotFoundError as exc:
        sys.exit(str(exc))


def cmd_calibrate(args):
    """Rysuje pola z layout.json na szablonach i wstawia przykładowe zdjęcie i imię."""
    layout = load_layout()
    out_dir = config.OUTPUT_DIR / "montage_preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    font = resolve_font(layout)
    if not font.exists():
        print(f"  ! Brak fontu {font}: podgląd użyje fontu domyślnego (bez gwarancji polskich znaków).")
        font = None

    for name, key in (("szablon_ksiega", "ksiega_ramka"), ("szablon_lista", "lista_imiona")):
        template = selected_path(name)
        if not template.exists():
            print(f"  x Brak {template}: wybierz szablon (python -m generator.images select {name} N).")
            continue
        if name == "szablon_ksiega":
            sample = out_dir / "przykladowe_zdjecie.png"
            Image.new("RGB", (600, 800), "#8a9bb0").save(sample)
            image = compose_book(template, [sample] * args.children, layout)
        else:
            image = Image.open(template).convert("RGBA")
            names = ["Kasia", "Józef", "Łucja"][: args.children]
            image = Image.alpha_composite(image, render_names(image.size, names, layout, font)).convert("RGB")
        ImageDraw.Draw(image).rectangle(frac_box(layout[key], image.size), outline="red", width=4)
        target = out_dir / f"{name}.png"
        image.save(target)
        print(f"  + {target}")
    print(f"Popraw pola w {LAYOUT_FILE.name}, jeśli czerwone ramki nie pasują do szablonów.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Automatyczny montaż filmu (ffmpeg)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="zmontuj film dla zamówienia")
    p.add_argument("order", help="plik JSON zamówienia")
    p.add_argument("--heygen", help="klip z HeyGen (domyślnie output/orders/<id>/heygen.mp4)")
    p.add_argument("--music", help="podkład (domyślnie output/selected/podklad.mp3)")
    p.add_argument("--no-music", action="store_true")
    p.add_argument("--preset", default="medium", help="preset x264: ultrafast (podgląd) ... slow (jakość)")
    p.add_argument("--keep-temp", action="store_true", help="zostaw pliki pośrednie scen")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("calibrate", help="podgląd ramki na zdjęcie i pola na imię")
    p.add_argument("--children", type=int, default=1, choices=[1, 2, 3])
    p.set_defaults(func=cmd_calibrate)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
