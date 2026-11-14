"""Scenariusz 4 „Od listu do sań” (scenariusze/4_od_listu_do_san.md): prompty kadrów, klipów i szablonów.

Jedno ujęcie = jeden kadr startowy (Nano Banana Pro) i jeden klip (Gemini Omni Flash, 3–10 s).
Dłuższe sceny składają się z kilku ujęć. Ujęcia z kluczem "reuse" biorą gotowy kadr i klip
z wersji krótkiej (output/selected/<klucz>), więc nie generujemy ich drugi raz.

Zasady jak w generator/prompts.py: w kadrze tylko dorośli, bez napisów, wąsy Mikołaja na ustach.
Prompty piszemy po angielsku.
"""

from __future__ import annotations

from .. import prompts

NAME = "od_listu_do_san"
TITLE = "Od listu do sań"
DOC = "scenariusze/4_od_listu_do_san.md"

# --- postacie ----------------------------------------------------------------------------

# Płatek: najmłodszy renifer. Opis jest doklejany do każdego ujęcia z nim, a zatwierdzony
# portret (postacie/platek) idzie jako drugi obraz wzorcowy. Bez czerwonego, świecącego nosa:
# nie może przypominać znanych postaci reniferów.
PLATEK_DESCRIPTION = """\
The young reindeer is the youngest reindeer in Santa's stable: clearly smaller than the
adult reindeer, with fluffy light-brown fur, a small cream-colored spot shaped like a
snowflake on his forehead, short soft velvet antlers, big dark friendly eyes and a dark
brown nose that is not red and does not glow. He wears a red harness with one small
golden bell on his chest. Photorealistic and natural, like a real young reindeer."""

PLATEK_REFERENCE_NOTE = """\
The image attached after Santa's reference shows the young reindeer: keep his size, fur
color, the snowflake spot on his forehead, his antlers and his red harness with the golden
bell exactly the same as in that image."""

CHARACTERS = {
    "platek": {
        "opis": "Płatek: portret wzorcowy młodego renifera do wszystkich ujęć z nim",
        "prompt": f"""\
Photorealistic full-body portrait of a young reindeer standing on fresh hay in a cozy
wooden reindeer stable at night, lit by warm lanterns, three-quarter side view, the whole
animal visible from antlers to hooves, looking curiously towards the camera.
{PLATEK_DESCRIPTION}
Adult reindeer with warm red blankets rest in the soft-focus background.
Warm cinematic lighting, photorealistic, 16:9.
No people, no children. No brand logos, no text, no letters anywhere in the image.""",
    },
}

# --- ujęcia ------------------------------------------------------------------------------
#
# Klucze ujęcia:
#   scena    numer sceny w scenariuszu (1–11)
#   opis     po polsku, do listy ujęć
#   scene    opis kadru startowego (EN); pomijany przy "reuse"
#   motion   opis ruchu do klipu (EN); pomijany przy "reuse"
#   camera   ruch kamery; domyślnie prompts.DEFAULT_CAMERA (powolny najazd)
#   santa    False: Mikołaja nie ma w kadrze, więc bez jego portretu jako wzoru
#   elves    True: dokleja stały opis dorosłych elfów
#   platek   True: dokleja opis Płatka i jego portret jako drugi wzór
#   reuse    klucz gotowego ujęcia z wersji krótkiej (prompts.SCENES)
#   wideo    False: tylko kadr (np. obraz dla HeyGen), bez klipu
#   sekundy  sugerowana długość klipu (domyślnie 8)

STATIC = "Static camera, locked-off medium shot, no zoom, no push-in, no camera movement."

SHOTS: dict[str, dict] = {
    # 1. Zorza nad wioską
    "zorza": {"scena": 1, "opis": "Zorza nad wioską (wersja krótka)", "reuse": "zorza"},
    # 2. Dom Mikołaja
    "dom": {"scena": 2, "opis": "Dom Mikołaja (wersja krótka)", "reuse": "dom"},
    # 3. Powitanie: śnieżna kula
    "kula": {
        "scena": 3,
        "opis": "Mikołaj przy biurku, w kuli zaczyna padać śnieg, bierze ją w dłonie",
        "scene": "Medium shot of Santa sitting at his large wooden desk in his cozy study at night, framed "
        "from the waist up, his whole face, glasses and beard clearly visible. He is writing with a quill pen "
        "in a big leather notebook with blank pages. On the desk in front of him, slightly to the side, stands "
        "a small glass snow globe on a carved dark wooden base, with a tiny snowy village of wooden houses "
        "inside. Next to it stands an empty wooden photo frame turned slightly away from the camera. Warm light "
        "from a desk lamp, a crackling fireplace softly blurred in the background, frost patterns on the "
        "window. The notebook pages are blank, without any writing.",
        "motion": "Santa calmly writes with the quill pen. Then the snow inside the small glass globe on the "
        "desk starts to swirl and the tiny village inside glows with warm golden light. Santa notices it, "
        "smiles with his eyes, puts the quill down and gently picks up the snow globe with both hands, holding "
        "it at chest height below his beard, so his face stays fully visible. He looks warmly towards the "
        "camera. Santa stays in the frame, in the same place and the same size for the whole shot; he never "
        "fades, disappears or turns into something else. The glass globe stays small, whole and round",
        "camera": STATIC,
    },
    "kula_heygen": {
        "scena": 3,
        "opis": "Kadr dla HeyGen: Mikołaj trzyma kulę i patrzy w kamerę (bez wideo z AI)",
        "scene": "Medium close-up of Santa sitting at his wooden desk in his cozy study at night, looking "
        "straight into the camera with a warm, kind expression, holding a small glass snow globe with both "
        "hands at chest height below his beard. Inside the globe a tiny snowy village glows warmly. His whole "
        "face, glasses, beard and heavy mustache are clearly visible and well lit from the front, eyes open, "
        "head straight. Desk lamp and blurred fireplace glow in the background.",
        "wideo": False,
    },
    # 4. List na poczcie
    "poczta_sala": {
        "scena": 4,
        "opis": "Poczta Mikołaja: zjeżdżalnia z listami, elfy sortują, Mikołaj idzie środkiem",
        "scene": "A huge wooden mail hall in Santa's village at night: a long polished wooden slide down which "
        "sacks of colorful envelopes slide, tall walls of wooden pigeonholes full of envelopes, warm lanterns. "
        "Elves sort letters into the pigeonholes. Santa walks down the middle of the hall, smiling with his "
        "eyes. All envelopes are blank, without any writing or stamps with text.",
        "motion": "Sacks of colorful envelopes slide down the wooden slide and the envelopes spill gently into "
        "baskets. Elves quickly sort envelopes into the pigeonholes. Santa walks slowly down the middle of the "
        "hall towards the camera and stops, looking around with a smile",
        "elves": True,
    },
    "poczta_koperta": {
        "scena": 4,
        "opis": "Mikołaj wyciąga z przegródki jedną kopertę z czerwoną pieczęcią",
        "scene": "Close medium shot of Santa standing in front of a wall of wooden pigeonholes full of colorful "
        "envelopes, reaching towards one cream envelope sealed with a red wax seal. Warm lantern light. All "
        "envelopes are blank, without any writing.",
        "motion": "Santa reaches into the pigeonhole, slowly pulls out the cream envelope with the red wax "
        "seal, looks at it closely through his glasses and smiles with his eyes, then turns it gently in his "
        "hands. The envelope stays blank",
    },
    # 5. Pracownia
    "pracownia": {"scena": 5, "opis": "Pracownia (wersja krótka)", "reuse": "pracownia"},
    "pracownia_mlotki": {
        "scena": 5,
        "opis": "Elfy stukają młoteczkami przy stole z drewnianymi zabawkami",
        "scene": "A long wooden workbench in Santa's busy workshop, warm light. Elves work on wooden toys: one "
        "taps a small wooden hammer on a toy train, another paints a wooden horse, a third sands a toy car. "
        "Shelves of colorful toys in the background. Santa is not in this shot.",
        "motion": "The elves tap their small wooden hammers in a cheerful steady rhythm, wood shavings fly a "
        "little, one elf lifts the finished toy train and smiles",
        "santa": False,
        "elves": True,
    },
    # 6. Stajnia: Płatek
    "stajnia": {"scena": 6, "opis": "Stajnia reniferów (wersja krótka)", "reuse": "renifery"},
    "platek_podskoki": {
        "scena": 6,
        "opis": "Płatek ćwiczy podskoki, ląduje w sianie i kicha śniegiem; Mikołaj się śmieje",
        "scene": "A cozy wooden reindeer stable lit by lanterns, fresh hay on the floor. The young reindeer "
        "stands in the foreground near a soft pile of hay, getting ready to jump. Santa stands a few steps "
        "behind him, watching with a warm smile, hands on his belt. Adult reindeer with red blankets rest in "
        "the background.",
        "motion": "The young reindeer bounces up on all four legs, trying to take off, rises a little and "
        "lands softly in the pile of hay; a puff of hay and snowflakes flies up and he shakes his head, "
        "blinking. Santa laughs warmly, his belly shaking, and steps closer to scratch him gently behind the "
        "ear",
        "platek": True,
    },
    "platek_proba": {
        "scena": 6,
        "opis": "Płatek podskakuje wyżej i przez chwilę unosi się nad ziemią",
        "scene": "Wide shot of the cozy wooden reindeer stable lit by lanterns, the young reindeer standing in "
        "the middle on fresh hay, a little golden sparkle in the air around his hooves. Santa is not in this "
        "shot.",
        "motion": "The young reindeer takes a few quick steps and jumps higher than before; for a moment he "
        "floats in the air above the hay with tiny golden sparkles under his hooves, his golden bell jingling, "
        "then he lands softly and proudly lifts his head",
        "santa": False,
        "platek": True,
        "camera": "Static camera, wide shot, no zoom.",
    },
    # 7. Księga i opowieść o dziecku (strona ze zdjęciem: szablon_ksiega z wersji krótkiej)
    "ksiega": {"scena": 7, "opis": "Mikołaj otwiera księgę (wersja krótka)", "reuse": "ksiega"},
    # 8. Przygotowanie prezentu i wpadka elfa
    "pakowanie": {
        "scena": 8,
        "opis": "Elfy owijają pudełko papierem w gwiazdki, Mikołaj trzyma szpule wstążek",
        "scene": "Santa's wrapping room: a big wooden table with a gift box half wrapped in red paper with "
        "small golden stars. Two elves hold the paper, Santa stands at the table holding two spools of "
        "ribbon, one red and one golden. Warm light, rolls of wrapping paper in the background. The paper "
        "has no letters or text.",
        "motion": "The elves fold the red paper neatly around the box and smooth the edges. Santa lifts the "
        "red ribbon spool in one hand and the golden one in the other, looks from one to the other as if "
        "choosing, and smiles with his eyes",
        "elves": True,
    },
    "wpadka": {
        "scena": 8,
        "opis": "Wpadka: elf zaplątuje się we wstążki i kręci jak bączek, drugi go odwija",
        "scene": "The same wrapping room: one elf stands next to the wrapping table holding the ends of two "
        "long ribbons, red and golden, that trail across the floor; another elf stands beside him. The "
        "wrapped gift box is on the table. Santa is not in this shot.",
        "motion": "The first elf pulls both ribbons at once, they wrap around him and he spins slowly in place "
        "like a spinning top until he is wrapped in red and golden ribbon from shoulders to knees, looking "
        "surprised but cheerful. The second elf calmly unwinds him, and the first elf proudly holds up a big, "
        "perfect two-colored bow. Funny, gentle, slapstick moment, nobody gets hurt",
        "santa": False,
        "elves": True,
        "camera": "Static camera, medium-wide shot, no zoom.",
    },
    "kokarda": {
        "scena": 8,
        "opis": "Gotowa paczka z dwukolorową kokardą i pustym bilecikiem",
        "scene": "Close-up of the finished gift box wrapped in red paper with small golden stars, tied with a "
        "big two-colored bow, red and golden, with a small blank cream gift tag hanging from the bow on a "
        "thin string. Warm soft light, wooden table. The tag is completely blank, without any writing. "
        "Santa is not in this shot.",
        "motion": "The bow ribbons settle gently, the blank tag swings slowly on its string and a few golden "
        "sparkles drift past",
        "santa": False,
    },
    # 9. Bliscy: ramka i koperta (zdjęcie w ramce: szablon_ramka)
    "gabinet_koperta": {
        "scena": 9,
        "opis": "Gabinet: ramka na biurku obok kuli, Mikołaj otwiera kopertę z sercem i czyta",
        "scene": "Medium shot of Santa sitting at his wooden desk in the cozy study at night, framed from the "
        "waist up, face, glasses and beard clearly visible. On the desk stand the small glass snow globe and "
        "a wooden photo frame turned towards Santa. He holds a cream envelope sealed with a red wax heart. "
        "Desk lamp, blurred fireplace glow. The envelope has no writing.",
        "motion": "Santa glances warmly at the photo frame on the desk, then gently breaks the red heart seal, "
        "takes out a folded letter, reads it and his eyes smile warmly; he nods slowly and holds the letter "
        "close to his heart. Santa stays in the frame the whole time",
        "camera": STATIC,
    },
    # 10. Załadunek sań
    "tasma_worek": {
        "scena": 10,
        "opis": "Prezent jedzie taśmą i wpada do wielkiego czerwonego worka w hangarze",
        "scene": "A big wooden hangar at night where Santa's sleigh stands: a wooden conveyor belt carries "
        "wrapped gifts with bows towards an enormous red sack on the sleigh. Elves stack gifts inside the "
        "sack. Lanterns, snow outside the open gate. Santa is not in this shot.",
        "motion": "Wrapped gifts ride along the wooden conveyor belt and one by one drop softly into the big "
        "red sack, the sack bulges a little; elves wave cheerfully and arrange the gifts",
        "santa": False,
        "elves": True,
    },
    "platek_worek": {
        "scena": 10,
        "opis": "Płatek nosem popycha ostatnią paczkę głębiej do worka",
        "scene": "Close medium shot of the big red sack on Santa's sleigh in the hangar, one wrapped gift "
        "sticking out of the top. The young reindeer stands next to the sleigh, leaning his head towards the "
        "sack. Warm lantern light. Santa is not in this shot.",
        "motion": "The young reindeer gently pushes the last gift deeper into the sack with his nose, his "
        "golden bell jingles, he steps back and proudly lifts his head",
        "santa": False,
        "platek": True,
    },
    # 11. Zaprzęganie, pierwszy lot Płatka i dom w kuli (koniec: szablon_kula + nakładka śniegu)
    "zaprzeganie": {
        "scena": 11,
        "opis": "Renifery w zaprzęgu, elfy zapinają uprząż Płatkowi tuż przy saniach",
        "scene": "Snowy yard in front of the stable at night under a green aurora: eight adult reindeer stand "
        "in pairs in front of Santa's sleigh, harnessed with bells. At the back, right next to the sleigh, "
        "the young reindeer stands in his own small harness while two elves buckle it. Santa sits in the "
        "sleigh holding the reins, the big red sack behind him.",
        "motion": "The elves finish buckling the young reindeer's harness and step back. The young reindeer "
        "stands tall and taps his hooves impatiently, the reindeer shake their heads and the bells jingle. "
        "Santa lifts the reins and smiles with his eyes",
        "elves": True,
        "platek": True,
    },
    "start": {
        "scena": 11,
        "opis": "Start: sanie ruszają i wzbijają się nad wioskę",
        "scene": "Wide shot of Santa's sleigh with the reindeer team on a snowy runway lined with small "
        "lanterns, the village and a green aurora in the background, Santa in the sleigh holding the reins, "
        "the big red sack behind him. The young reindeer runs at the back of the team right next to the "
        "sleigh.",
        "motion": "The reindeer start to run, the sleigh glides faster along the lantern-lit runway and lifts "
        "off into the night sky, rising above the snowy roofs of the village towards the aurora; snow sparkles "
        "behind the runners",
        "platek": True,
        "camera": "The camera stays in place and slowly tilts up to follow the sleigh into the sky.",
    },
    "platek_leci": {
        "scena": 11,
        "opis": "Zbliżenie: Płatek biegnie w powietrzu razem z zaprzęgiem",
        "scene": "Night sky above the snowy village, the green aurora behind. Close side view of the young "
        "reindeer in his red harness with the golden bell, flying through the air at the back of the reindeer "
        "team, the edge of Santa's red sleigh visible behind him. Santa is not visible in this shot.",
        "motion": "The young reindeer gallops through the air with steady, confident strides next to the "
        "other reindeer, his golden bell jingling, snowflakes rushing past; he turns his head for a moment "
        "with a happy, proud look and keeps flying",
        "santa": False,
        "platek": True,
        "camera": "Smooth tracking shot flying alongside the young reindeer, keeping him in the center of the "
        "frame.",
    },
    "sanie": {"scena": 11, "opis": "Sanie i pożegnanie (wersja krótka, opcjonalnie)", "reuse": "sanie"},
}

# --- szablony (montaż wkleja w nie zdjęcia albo imię) --------------------------------------

TEMPLATES = {
    "szablon_kula": {
        "scena": 11,
        "opis": "Pusta śnieżna kula na koniec filmu: montaż wkleja zdjęcie domu albo ogólny domek",
        "prompt": """\
Close-up, straight front view of a glass snow globe standing on a carved dark
wooden base on Santa's wooden desk at night. The inside of the glass sphere is
empty and filled with soft, even, cream-white mist, with no objects inside,
so a picture can be placed inside later. Gentle reflections only on the edges
of the glass. Warm candle and desk lamp light, blurred golden fireplace glow in
the background. The globe is centered and fills about half of the frame height.
16:9, photorealistic. No text, no letters, no people.""",
    },
    "szablon_ramka": {
        "scena": 9,
        "opis": "Ramka na biurku: montaż wkleja zdjęcie bliskich albo złotą gwiazdę",
        "prompt": """\
Close-up, straight front view of a simple carved wooden photo frame standing on
Santa's wooden desk at night, next to a small glass snow globe on the side.
Inside the frame there is only an empty, flat, evenly lit cream-white surface,
with no picture, so a photo can be placed inside later. Warm desk lamp light,
blurred fireplace glow in the background. The frame is centered and fills about
two thirds of the frame height. 16:9, photorealistic. No text, no letters, no people.""",
    },
    "szablon_list": {
        "scena": 4,
        "opis": "Biurko z pustą kartką w ramce: montaż wkleja zdjęcie listu albo rysunku dziecka",
        "prompt": """\
Top-down view of Santa's wooden desk at night with a large sheet of plain cream
paper lying in the center inside a thin golden frame, completely blank, so a
picture of a child's letter or drawing can be placed on it later. Around it: an
opened cream envelope with a broken red wax seal, a quill pen in an inkwell, his
reading glasses and a candle. Warm candle light. 16:9, photorealistic.
No text, no letters, no writing anywhere, no people.""",
    },
    "szablon_bilecik": {
        "scena": 8,
        "opis": "Duży pusty bilecik przy kokardzie: montaż wpisuje imię dziecka",
        "prompt": """\
Close-up of a large blank cream gift tag with rounded corners tied with a thin
golden string to a big red and golden bow on a gift wrapped in red paper with
small golden stars. The tag faces the camera, flat and evenly lit, and fills
about a third of the frame, so a name can be written on it later. Warm soft
light, shallow depth of field. 16:9, photorealistic.
No text, no letters, no writing anywhere, no people.""",
    },
}

# Szablony z wersji krótkiej używane w tym scenariuszu.
REUSED_TEMPLATES = {"szablon_ksiega": 7}

# --- budowanie promptów ---------------------------------------------------------------------

BASE_NO_SANTA = """\
Scene: {scene}
Same photorealistic, warm cinematic style as the rest of the film, 16:9.
No children appear in the image; every person in it is an adult.
No brand logos, no text, no letters anywhere in the image."""


def frame_prompt(key: str, with_platek_reference: bool = True) -> str:
    """Prompt kadru startowego ujęcia (Nano Banana Pro)."""
    shot = SHOTS[key]
    if "reuse" in shot:
        return prompts.scene_prompt(shot["reuse"])
    if shot.get("santa", True):
        prompt = prompts.SCENE_PROMPT.format(scene=shot["scene"])
    else:
        prompt = BASE_NO_SANTA.format(scene=shot["scene"])
    if shot.get("elves"):
        prompt += "\n" + prompts.ELVES_DESCRIPTION
    if shot.get("platek"):
        if with_platek_reference:
            prompt += "\n" + PLATEK_REFERENCE_NOTE
        prompt += "\n" + PLATEK_DESCRIPTION
    return prompt


def motion_prompt(key: str, seconds) -> str:
    """Prompt ruchu klipu (Gemini Omni Flash)."""
    shot = SHOTS[key]
    if "reuse" in shot:
        return prompts.scene_motion_prompt(shot["reuse"], seconds)
    motion = shot["motion"]
    if shot.get("platek"):
        motion += ". The young reindeer keeps exactly the same look, size and red harness for the whole shot"
    return prompts.motion_prompt(motion, seconds, shot.get("camera"))


def needs_santa_reference(key: str) -> bool:
    return SHOTS[key].get("santa", True)


def video_shots() -> list[str]:
    return [k for k, s in SHOTS.items() if "reuse" not in s and s.get("wideo", True)]


def new_frame_shots() -> list[str]:
    return [k for k, s in SHOTS.items() if "reuse" not in s]
