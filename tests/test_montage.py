"""Montaż na sztucznych materiałach w małej rozdzielczości (wymaga ffmpeg, bez sieci)."""

import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from generator import montage

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="brak ffmpeg")

FMT = montage.Format(width=320, height=180, fps=10, preset="ultrafast")
LAYOUT = {"ksiega_ramka": [0.56, 0.22, 0.84, 0.78], "lista_imiona": [0.3, 0.34, 0.7, 0.6]}
DEJAVU = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def make_clip(path: Path, seconds: float, audio: bool = True):
    cmd = ["-f", "lavfi", "-i", f"testsrc2=s=640x360:r=24:d={seconds}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=f=220:d={seconds}", "-c:a", "aac"]
    ffmpeg(*cmd, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-shortest", str(path))


def make_tone(path: Path, seconds: float, freq: int = 440):
    ffmpeg("-f", "lavfi", "-i", f"sine=f={freq}:d={seconds}", str(path))


def stream_info(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return {"video": [s for s in out if s.startswith("video")], "audio": [s for s in out if s.startswith("audio")]}


@pytest.fixture
def assets(tmp_path):
    clips = {}
    for key in ("dom", "pracownia", "ksiega", "sanie"):
        clips[key] = tmp_path / f"{key}.mp4"
        # Jeden klip bez dźwięku: Veo nie zawsze go generuje.
        make_clip(clips[key], 8, audio=key != "pracownia")
    lines = {}
    for key, seconds in [("scena1_dom", 3), ("scena2_pracownia", 21), ("scena4_ksiega", 9),
                         ("scena5_lista", 6), ("scena6_pozegnanie", 10)]:
        lines[key] = tmp_path / f"{key}.mp3"
        make_tone(lines[key], seconds)
    Image.new("RGB", (1280, 720), "#5a3b1e").save(tmp_path / "ksiega.png")
    Image.new("RGB", (1280, 720), "#e8d9b0").save(tmp_path / "lista.png")
    music = tmp_path / "podklad.mp3"
    make_tone(music, 30, 330)
    return montage.Assets(
        clips=clips,
        lines=lines,
        book_template=tmp_path / "ksiega.png",
        list_template=tmp_path / "lista.png",
        music=music,
        layout=LAYOUT,
        font=DEJAVU if DEJAVU.exists() else None,
    )


def test_assemble_full_film(tmp_path, assets):
    heygen = tmp_path / "heygen.mp4"
    make_clip(heygen, 6)
    photo = tmp_path / "kasia.jpg"
    Image.new("RGB", (400, 600), "#c08080").save(photo)
    out = tmp_path / "zamowienie" / "film.mp4"

    order = {"id": "t1", "dzieci": [{"imie": "Kasia"}]}
    montage.assemble(order, [photo], heygen, assets, out, FMT)

    # dom 15 (minimum) + pracownia 1+21+1.5 + heygen 6 + ksiega 20 + lista 15 + sanie 20
    expected = 15 + 23.5 + 6 + 20 + 15 + 20
    assert montage.probe_duration(out) == pytest.approx(expected, abs=0.6)
    info = stream_info(out)
    assert info["video"] == ["video,320,180"] and len(info["audio"]) == 1
    assert not (out.parent / "montage_tmp").exists()


def test_assemble_reports_missing_files(tmp_path, assets):
    with pytest.raises(FileNotFoundError, match="heygen.mp4"):
        montage.assemble({"id": "t", "dzieci": [{"imie": "A"}]}, [], tmp_path / "heygen.mp4", assets,
                         tmp_path / "film.mp4", FMT)


def test_compose_book_places_photos_inside_frame(tmp_path):
    template = tmp_path / "t.png"
    Image.new("RGB", (1000, 500), "black").save(template)
    photos = []
    for i, color in enumerate(["red", "blue"]):
        photos.append(tmp_path / f"{i}.png")
        Image.new("RGB", (300, 300), color).save(photos[-1])
    page = montage.compose_book(template, photos, LAYOUT)
    x0, y0, x1, y1 = montage.frac_box(LAYOUT["ksiega_ramka"], page.size)
    mid_y = (y0 + y1) // 2
    assert page.getpixel((x0 + 5, mid_y)) == (255, 0, 0)
    assert page.getpixel((x1 - 5, mid_y)) == (0, 0, 255)
    assert page.getpixel((5, 5)) == (0, 0, 0)  # poza ramką bez zmian


def test_render_names_stays_inside_box():
    layer = montage.render_names((1280, 720), ["Łucja", "Józef"], LAYOUT, DEJAVU if DEJAVU.exists() else None)
    bbox = layer.getbbox()
    x0, y0, x1, y1 = montage.frac_box(LAYOUT["lista_imiona"], layer.size)
    assert bbox is not None
    assert x0 <= bbox[0] and bbox[2] <= x1 and y0 <= bbox[1] and bbox[3] <= y1
