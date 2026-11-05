"""Siatka porównawcza: wszystkie klipy jednego ujęcia obok siebie, z podpisem modelu i kosztu."""

import subprocess
import tempfile
from pathlib import Path

from .modele import MODELS
from .ujecia import OUT, VIDEOS_DIR
from .zadania import latest_by_job, rel

COMPARE_DIR = OUT / "porownania"
TILE_W, TILE_H, LABEL_H = 640, 360, 44
FPS = 24
MAX_TILES = 9


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip() or 0)


def model_of(path: Path) -> str:
    return path.stem.rsplit("_", 1)[0]


def clips_for(shot: str, models: list[str] | None = None) -> list[tuple[Path, str]]:
    """Klipy ujęcia w kolejności modeli z modele.py, z podpisami z dziennika."""
    done = {r["plik"]: r for r in latest_by_job().values() if r.get("stan") == "gotowe" and "plik" in r}
    order = list(MODELS)
    files = [p for p in sorted((VIDEOS_DIR / shot).glob("*.mp4")) if not models or model_of(p) in models]
    files.sort(key=lambda p: (order.index(model_of(p)) if model_of(p) in order else len(order), p.name))
    clips = []
    for path in files:
        record = done.get(rel(path), {})
        number = path.stem.rsplit("_", 1)[-1]
        parts = [f"{model_of(path)} #{number}"]
        if record.get("sekundy"):
            parts.append(f"{record['sekundy']:g} s")
        if record.get("rozdzielczosc"):
            parts.append(str(record["rozdzielczosc"]))
        if record.get("koszt_usd") is not None:
            parts.append(f"~${record['koszt_usd']:.2f}")
        if record.get("czas_generowania_s"):
            parts.append(f"gen. {record['czas_generowania_s']} s")
        clips.append((path, " | ".join(parts)))
    return clips


def grid_columns(count: int) -> int:
    return 1 if count == 1 else 2 if count in (2, 4) else 3


def grid_layout(cells: int, columns: int) -> str:
    tile_h = TILE_H + LABEL_H
    return "|".join(f"{(i % columns) * TILE_W}_{(i // columns) * tile_h}" for i in range(cells))


def load_font(size: int):
    from PIL import ImageFont

    for name in ("DejaVuSans.ttf", "Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def label_image(text: str, path: Path) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (TILE_W, LABEL_H), (24, 24, 28))
    ImageDraw.Draw(image).text((12, 10), text, fill=(240, 240, 240), font=load_font(22))
    image.save(path)


def build_grid(clips: list[tuple[Path, str]], out: Path) -> None:
    if not clips:
        raise ValueError("Brak klipów do porównania.")
    clips = clips[:MAX_TILES]
    count = len(clips)
    columns = grid_columns(count)
    cells = -(-count // columns) * columns
    duration = max(probe_duration(path) for path, _ in clips)

    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["ffmpeg", "-y", "-v", "error"]
        for path, _ in clips:
            cmd += ["-i", str(path)]
        for i, (_, text) in enumerate(clips):
            label = Path(tmp) / f"label_{i}.png"
            label_image(text, label)
            cmd += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(label)]

        parts = []
        for i in range(count):
            parts.append(
                f"[{i}:v]scale={TILE_W}:{TILE_H}:force_original_aspect_ratio=decrease,"
                f"pad={TILE_W}:{TILE_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},"
                f"tpad=stop_mode=clone:stop_duration={duration:.3f},trim=duration={duration:.3f},"
                f"setpts=PTS-STARTPTS,format=yuv420p[c{i}]"
            )
            parts.append(f"[{count + i}:v]fps={FPS},setsar=1,format=yuv420p[l{i}]")
            parts.append(f"[l{i}][c{i}]vstack=inputs=2[t{i}]")
        for i in range(count, cells):
            parts.append(f"color=c=black:s={TILE_W}x{TILE_H + LABEL_H}:r={FPS}:d={duration:.3f},format=yuv420p[t{i}]")
        if cells == 1:
            parts.append("[t0]null[v]")
        else:
            tiles = "".join(f"[t{i}]" for i in range(cells))
            parts.append(f"{tiles}xstack=inputs={cells}:layout={grid_layout(cells, columns)}[v]")

        out.parent.mkdir(parents=True, exist_ok=True)
        cmd += [
            "-filter_complex", ";".join(parts), "-map", "[v]", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-t", f"{duration:.3f}", str(out),
        ]
        subprocess.run(cmd, check=True)
