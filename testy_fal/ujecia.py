"""Ujęcia testowe: najtrudniejsze momenty długich scenariuszy i sceny z wersji krótkiej.

Zasady jak w generator/prompts.py: wszyscy w kadrze są dorośli, bez dzieci, bez napisów,
wąsy Mikołaja zakrywają usta. Kadry startowe dostają portret Mikołaja jako referencję,
a ujęcia z Kardamonem także jego wybrany portret (ujęcie "kardamon").
"""

from dataclasses import dataclass
from pathlib import Path

from generator import config, prompts
from generator.common import selected_path

OUT = config.OUTPUT_DIR / "testy_fal"
FRAMES_DIR = OUT / "kadry"
CHOSEN_DIR = OUT / "wybrane"
VIDEOS_DIR = OUT / "wideo"

KARDAMON_DESCRIPTION = """\
Kardamon, Santa's Head Elf for Gift Affairs, is an adult man in his late thirties:
clearly grown-up, with an adult face, adult height and adult body proportions,
about as tall as Santa. He has slightly pointed ears, neatly combed chestnut hair,
small round glasses, a clean-shaven face and natural skin without any makeup.
He wears a dark green wool waistcoat over a cream shirt, a small red bow tie
and a pointed green felt cap, and he carries a wooden clipboard."""

KARDAMON_PORTRAIT = f"""\
Photorealistic medium shot of Kardamon standing in Santa's cozy wooden office,
shelves with folders and a warm fireplace in the soft-focus background.
{KARDAMON_DESCRIPTION}
He looks friendly and diligent, a little proud of his work.
Warm cinematic lighting, photorealistic, 16:9.
Only Kardamon is in the image, and he is an adult. No children appear in the image.
No brand logos, no text, no letters anywhere in the image."""

KARDAMON_REFERENCE_NOTE = """\
The second attached image shows Kardamon, Santa's head elf: keep his face, glasses,
hair, outfit and proportions exactly the same as in that image."""


@dataclass(frozen=True)
class Shot:
    key: str
    opis: str  # po polsku, do listy ujęć
    kadr: str  # opis sceny (EN): kadr startowy albo scena w trybie ref
    ruch: str  # opis ruchu (EN) do promptu wideo
    elfy: bool = False
    kardamon: bool = False
    produkcja: bool = False  # kadr z output/selected/ (sceny wersji krótkiej)
    tylko_kadr: bool = False  # portret referencyjny, bez wideo

    @property
    def frame_path(self) -> Path:
        return selected_path(self.key) if self.produkcja else CHOSEN_DIR / f"{self.key}.png"


TEST_SHOTS = [
    Shot(
        "kardamon",
        "Portret Kardamona: referencja do kadrów i trybu ref (bez wideo)",
        KARDAMON_PORTRAIT,
        "",
        tylko_kadr=True,
    ),
    Shot(
        "kaczka",
        "Kontrola jakości (scen. 1, scena 7): kaczka i bączek w dłoniach Mikołaja",
        "Santa sitting at a sturdy wooden workbench marked with a small golden star, with a serious, "
        "concentrated look, holding a yellow rubber duck in his hand. A wooden spinning top and a small "
        "red wooden toy car lie on the table in front of him. Two elves stand beside the table holding "
        "small notebooks, waiting for his verdict. Busy workshop in the soft-focus background.",
        "Santa squeezes the rubber duck with a serious face, then his eyes crinkle with laughter. "
        "He puts the duck down and gives the wooden spinning top a twist, and it spins steadily on the "
        "table. The elves smile and write in their notebooks",
        elfy=True,
    ),
    Shot(
        "pieczec",
        "Podpis i woskowa pieczęć (scen. 3, scena 8): drobna praca rąk",
        "Santa sitting at his large wooden office desk, holding a stick of red sealing wax over a lit "
        "candle. In front of him lies a golden card decorated with a drawn wrapped present, without any "
        "writing. A quill pen stands in an inkwell and a heavy gold signet ring is on his finger. "
        "Warm candle and fireplace light.",
        "Santa tilts the red wax stick over the candle and lets a few drops of melted wax fall onto the "
        "golden card. Then he presses his signet ring firmly into the soft wax and lifts it, leaving a "
        "neat round seal. The candle flame flickers",
    ),
    Shot(
        "poczta",
        "Poczta pneumatyczna (scen. 3, scena 9): fizyka i Kardamon",
        "A pneumatic tube post station in Santa's wooden office: polished brass pipes with small glass "
        "windows run along the wall and up through the ceiling. Kardamon stands at the brass pipe "
        "opening, holding a brass capsule with a rolled golden card inside. Santa watches with a smile "
        "from his desk in the background.",
        "Kardamon slides the brass capsule into the pipe opening and closes the little hatch. With a "
        "whoosh the capsule shoots up the pipe, flashes past the small glass windows and disappears "
        "through the ceiling. Kardamon nods with satisfaction",
        kardamon=True,
    ),
    Shot(
        "kardamon_raporty",
        "Kardamon i raporty elfów (scen. 3, scena 2): druga postać, ujęcie 1",
        "Santa sitting at his large wooden office desk covered with neat stacks of report folders. "
        "Kardamon stands beside the desk, handing him a thick folder tied with a red ribbon. Shelves "
        "full of folders and a warm fireplace in the background.",
        "Kardamon opens the folder and points to a page. Santa leans in, adjusts his glasses and nods "
        "slowly, his eyes smiling. Kardamon turns the page",
        kardamon=True,
    ),
    Shot(
        "kardamon_karta",
        "Karta prezentu (scen. 3, scena 7): druga postać, ujęcie 2",
        "Santa sitting in his armchair behind the office desk. Kardamon walks towards him carrying a "
        "golden card on a small red velvet cushion with both hands. Warm, festive light, garlands on "
        "the shelves. The card has no writing.",
        "Kardamon walks up to the desk and bows slightly, presenting the golden card. Santa takes the "
        "card carefully with both hands and looks at it, his eyes smiling warmly",
        kardamon=True,
    ),
    Shot(
        "lot",
        "Lot nad lasami (scen. 2, scena 6): łatwe ujęcie do porównania cen",
        "Santa's sleigh pulled by eight reindeer flying at night high above snowy pine forests under a "
        "full moon, seen from slightly behind and above. Santa sits in the sleigh holding the reins, "
        "seen from behind. Lights of a small town glow far below.",
        "The sleigh glides smoothly forward over the forest, the reindeer gallop through the air, snow "
        "sparkles on the trees below, the camera follows the sleigh",
    ),
]

PRODUCTION_SHOTS = [
    Shot(key, "Scena z wersji krótkiej (kadr z output/selected/)", s["scene"], s["motion"],
         elfy=bool(s.get("elves")), produkcja=True)
    for key, s in prompts.SCENES.items()
]

SHOTS: dict[str, Shot] = {s.key: s for s in [*TEST_SHOTS, *PRODUCTION_SHOTS]}
VIDEO_SHOTS = [key for key, s in SHOTS.items() if not s.tylko_kadr]
DEFAULT_SHOTS = ["kaczka", "pieczec", "poczta", "kardamon_raporty"]


def portrait_path() -> Path:
    return selected_path("portrait")


def kardamon_path() -> Path:
    return CHOSEN_DIR / "kardamon.png"


def frame_prompt(shot: Shot, with_kardamon_reference: bool) -> str:
    """Prompt kadru startowego dla Nano Banana Pro."""
    if shot.tylko_kadr:
        return shot.kadr
    prompt = prompts.SCENE_PROMPT.format(scene=shot.kadr)
    if shot.elfy:
        prompt += "\n" + prompts.ELVES_DESCRIPTION
    if shot.kardamon:
        if with_kardamon_reference:
            prompt += "\n" + KARDAMON_REFERENCE_NOTE
        prompt += "\n" + KARDAMON_DESCRIPTION
    return prompt


def motion_prompt(shot: Shot) -> str:
    """Prompt ruchu jak w produkcji; {seconds} uzupełnia mapowanie długością wysłaną do modelu."""
    return prompts.MOTION_PROMPT.format(motion=shot.ruch, seconds="{seconds}")


def references(shot: Shot) -> list[Path]:
    """Obrazy referencyjne dla trybu ref: portret Mikołaja i (w scenach z nim) Kardamona."""
    paths = [portrait_path()]
    if shot.kardamon and kardamon_path().exists():
        paths.append(kardamon_path())
    return paths


def ref_prompt(shot: Shot, style: str, refs: list[Path]) -> str:
    """Prompt trybu ref: opis postaci z obrazów, scena i ruch w jednym tekście."""
    if style == "seedance":
        santa, elf = "@Image1", "@Image2"
    else:
        santa, elf = "the first reference image", "the second reference image"
    lines = [
        f"Santa Claus looks exactly like the man in {santa}: keep his face, age, glasses, long white "
        "beard, hat and coat the same. His heavy mustache hangs down over his mouth into the beard, "
        "so his mouth stays covered by hair."
    ]
    if shot.kardamon and len(refs) > 1:
        lines.append(f"Kardamon, the head elf, looks exactly like the man in {elf}.")
    lines.append(f"Scene: {shot.kadr}")
    if shot.elfy:
        lines.append(prompts.ELVES_DESCRIPTION)
    if shot.kardamon:
        lines.append(KARDAMON_DESCRIPTION)
    lines.append(
        "Photorealistic, warm cinematic lighting, 16:9. No children appear; every person is an adult. "
        "No text, no letters, no logos."
    )
    lines.append(motion_prompt(shot))
    return "\n".join(lines)
