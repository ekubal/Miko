"""Reklama zapisów (scenariusze/reklama_zapisy.md): Mikołaj mówi do rodziców, trzy warianty.

Film reklamowy przed startem sprzedaży, poziomy 16:9 (YouTube, reklamy Google, strona zapisów,
aktualności na Facebooku). Mikołaj mówi do rodziców, wyjaśnia, co zamawiają, podaje datę startu
zamówień (25 listopada) i zachęca do zapisu po kod −25%.

Ujęcia z mówiącym Mikołajem to tylko kadry ("wideo": False) dla HeyGen (Avatar IV) z nagraniem
głosu z ElevenLabs. Pozostałe ujęcia to klipy Gemini Omni Flash z głosem Mikołaja zza kadru:
wąsy zakrywają usta, więc nie potrzeba ruchu warg.

Zasady jak w generator/prompts.py: w kadrze tylko dorośli, bez napisów, wąsy Mikołaja na ustach.
Napisy, plansza końcowa i przykładowe imię na liście pojawiają się dopiero w montażu.
"""

from __future__ import annotations

from .. import prompts
from . import od_listu_do_san

NAME = "reklama_zapisy_poziomo"
TITLE = "Reklama zapisów: Mikołaj mówi do rodziców (16:9)"
DOC = "scenariusze/reklama_zapisy.md"

# Kadry i klipy poziome (CLI przekazuje ASPECT do modeli obrazu i wideo).
ASPECT = "16:9"

# Płatek występuje w wariancie 3: bierzemy zatwierdzony portret ze scenariusza 4,
# żeby wyglądał tak samo jak w filmie.
PLATEK_FROM = od_listu_do_san.NAME

SCENE_TITLES = {
    "wspolne": "Ujęcia wspólne dla wszystkich wariantów",
    "W1": "Wariant 1 „Tajna narada”",
    "W2": "Wariant 2 „Czy to już nagrywa?”",
    "W3": "Wariant 3 „Za długa lista”",
}

CHARACTERS: dict[str, dict] = {}
TEMPLATES: dict[str, dict] = {}
REUSED_TEMPLATES: dict[str, int] = {}

# Kompozycja: postać trochę z boku, spokojne tło po drugiej stronie i na dole kadru na napisy.
HORIZONTAL = (
    "wide horizontal 16:9 frame, the main subject slightly off-center, with calm, simple space "
    "on one side and in the bottom fifth of the frame"
)

STATIC = "Static camera, no zoom, no push-in, no camera movement; only the characters move."

# --- ujęcia ------------------------------------------------------------------------------
#
# Klucze jak w od_listu_do_san.py (scena, opis, scene, motion, camera, santa, elves, platek,
# wideo, sekundy). Dodatkowo:
#   heygen   opis ruchu dla HeyGen (Avatar IV) przy kadrach z mówiącym Mikołajem

SHOTS: dict[str, dict] = {
    # --- wspólne: co dostaje dziecko -----------------------------------------------------
    "ksiega": {
        "scena": "wspolne",
        "opis": "Mikołaj otwiera złotą księgę, na stronie świeci pusta złota ramka",
        "scene": "Santa sitting at his large wooden desk in his cozy study at night, seen from the chest up, "
        "looking down with a warm smile at a large antique book with a golden embossed cover lying open in "
        "front of him. On the open page there is an empty ornate golden picture frame that glows softly from "
        "inside, and tiny golden sparkles float above it. His face, glasses and beard are clearly visible. "
        "Warm desk-lamp light, a fireplace softly blurred in the background. The pages have no writing at all "
        "and the golden frame is empty.",
        "motion": "Santa turns a page of the golden book with one hand; the empty golden frame on the new page "
        "starts to glow brighter and golden sparkles rise from it. Santa looks at the page and smiles with his "
        "eyes, then glances up warmly towards the camera. Santa stays in the frame the whole time and the "
        "golden frame on the page stays empty",
        "camera": STATIC,
        "sekundy": 6,
    },
    "lista": {
        "scena": "wspolne",
        "opis": "Mikołaj przybija czerwoną pieczęć na liście grzecznych dzieci (puste linie: imię dodaje montaż)",
        "scene": "Close-up of a long cream parchment scroll, the nice list, lying on Santa's wooden desk, with "
        "empty ruled lines, a quill pen and a small pot of red sealing wax next to it. Santa's hand, in the "
        "red sleeve of his coat, holds a brass seal just above the parchment. Warm candle light. The parchment "
        "is completely blank, without any writing or letters.",
        "motion": "Santa's hand presses the brass seal onto a blob of red wax on the parchment, lifts it and "
        "leaves a neat round red wax seal with a star; a few golden sparkles twinkle above the list. The "
        "parchment stays blank",
        "camera": STATIC,
        "sekundy": 5,
    },
    # --- wariant 1: „Tajna narada” ---------------------------------------------------------
    "w1_mowi": {
        "scena": "W1",
        "opis": "Kadr dla HeyGen: Mikołaj w fotelu przy kominku, pochylony do kamery jak przy sekrecie",
        "scene": "Medium close-up of Santa sitting in a big red velvet armchair next to a crackling fireplace "
        "in his cozy living room at night, leaning slightly towards the camera as if about to share a secret, "
        "looking straight into the camera with a warm, playful, conspiratorial expression. His whole face, "
        "glasses, beard and heavy mustache are clearly visible and well lit from the front, eyes open, head "
        "straight, hands resting calmly on his knees. A Christmas tree with warm lights is softly blurred in "
        "the background.",
        "wideo": False,
        "heygen": "Santa speaks softly and a little secretively, leaning in slightly towards the camera, with "
        "small nods, warm smiling eyes and an occasional small hand gesture at chest height. His head stays "
        "steady and his face stays fully visible.",
    },
    "w1_elf": {
        "scena": "W1",
        "opis": "Elf wychyla się zza oparcia fotela, przyłapany chowa się z powrotem",
        "scene": "The back of a big red velvet armchair by the fireplace in Santa's cozy living room at night. "
        "One adult elf peeks out from behind the armchair backrest, only his head, pointed felt cap and curious "
        "eyes visible, clearly eavesdropping. Warm firelight, Christmas tree lights softly blurred in the "
        "background. Santa is not in this shot.",
        "motion": "The elf slowly peeks out from behind the armchair, listening curiously, then suddenly "
        "realizes he has been noticed, gives a sheepish, guilty smile and slowly sinks back down behind the "
        "armchair until only the tip of his pointed cap is visible. Funny, gentle moment",
        "santa": False,
        "elves": True,
        "camera": STATIC,
        "sekundy": 5,
    },
    "w1_ciii": {
        "scena": "W1",
        "opis": "Mikołaj śmieje się za głośno, szybko robi „ciii” i rozgląda się, czy dzieci nie słyszą",
        "scene": "Medium shot of Santa sitting in the big red velvet armchair next to the crackling fireplace "
        "in his cozy living room at night, leaning back and laughing heartily, eyes squeezed with joy behind "
        "his glasses. His whole face, glasses and beard are clearly visible. Christmas tree lights softly "
        "blurred in the background.",
        "motion": "Santa laughs heartily, then suddenly stops, quickly raises one finger to the front of his "
        "beard in a hush gesture and glances guiltily left and right, as if checking that nobody else heard "
        "him, then winks at the camera. Santa stays in the frame the whole time",
        "camera": STATIC,
        "sekundy": 6,
    },
    # --- wariant 2: „Czy to już nagrywa?” ---------------------------------------------------
    "w2_za_blisko": {
        "scena": "W2",
        "opis": "Mikołaj za blisko kamery: same okulary i broda, potem odsuwa się i poprawia okulary",
        "scene": "Extreme close-up of Santa's face much too close to the camera lens, filling the frame: his "
        "round glasses, bushy white eyebrows, the top of his heavy mustache and his white beard, his eyes "
        "squinting curiously into the lens. Behind him, out of focus, his cozy study with warm lamp light.",
        "motion": "Santa peers curiously into the lens from very close, then slowly leans back until he is "
        "in a normal medium shot sitting at his wooden desk, adjusts his glasses with one hand and straightens "
        "his coat, looking a little embarrassed but cheerful. Santa stays in the frame the whole time",
        "camera": "Static camera on a tripod, no zoom, no camera movement; only Santa moves.",
        "sekundy": 6,
    },
    "w2_elf": {
        "scena": "W2",
        "opis": "Elf za starą drewnianą kamerą na statywie pokazuje kciuk w górę",
        "scene": "An adult elf stands behind an old wooden film camera with brass details on a wooden tripod "
        "in Santa's cozy study at night; a small red lamp on top of the camera glows. The elf looks over the "
        "camera towards the scene in front of it. Warm lamp light, bookshelves softly blurred in the "
        "background. Santa is not in this shot.",
        "motion": "The elf looks over the old camera, checks the small glowing red lamp, then gives a big, "
        "proud thumbs-up with a cheerful nod. Gentle, funny moment",
        "santa": False,
        "elves": True,
        "camera": STATIC,
        "sekundy": 4,
    },
    "w2_mowi": {
        "scena": "W2",
        "opis": "Kadr dla HeyGen: Mikołaj przy biurku patrzy w kamerę",
        "scene": "Medium close-up of Santa sitting at his large wooden desk in his cozy study at night, "
        "looking straight into the camera with a warm, friendly, slightly proud expression, as if recording "
        "a message for the first time. His whole face, glasses, beard and heavy mustache are clearly visible "
        "and well lit from the front, eyes open, head straight, hands folded on the desk. Desk lamp, "
        "bookshelves and fireplace glow softly blurred in the background.",
        "wideo": False,
        "heygen": "Santa speaks cheerfully and a little formally, like someone recording a video message for "
        "the first time: small proud nods, warm smiling eyes, occasional open-hand gesture. His head stays "
        "steady and his face stays fully visible.",
    },
    "w2_wylacz": {
        "scena": "W2",
        "opis": "Mikołaj nachyla się do kamery, szuka przycisku i zasłania obiektyw dłonią",
        "scene": "Medium close-up of Santa at his wooden desk in his cozy study at night, leaning forward "
        "towards the camera and reaching one hand towards the lens with a puzzled, curious look over his "
        "glasses, as if searching for a button. His face, glasses and beard are clearly visible. Warm "
        "desk-lamp light.",
        "motion": "Santa leans closer to the camera, squints over his glasses, searches with his fingers for "
        "a button just in front of the lens, shrugs with a chuckle and finally covers the lens with his palm, "
        "so the frame turns dark. Santa stays in the frame until his hand covers the lens",
        "camera": "Static camera on a tripod, no zoom, no camera movement; only Santa moves.",
        "sekundy": 5,
    },
    # --- wariant 3: „Za długa lista” ---------------------------------------------------------
    "w3_rolka": {
        "scena": "W3",
        "opis": "Mikołaj rozwija listę grzecznych dzieci, która toczy się przez gabinet i wylatuje drzwiami na śnieg",
        "scene": "Santa stands in his cozy study at night, seen from head to knees, holding the top end of a "
        "very long cream parchment scroll, the nice list, at chest height; the rolled part rests on the "
        "wooden floor in front of him. Behind him an open wooden door shows snow falling outside. Warm lamp "
        "light. His face, glasses and beard are clearly visible. The parchment has empty ruled lines without "
        "any writing.",
        "motion": "Santa lets go of the rolled part of the scroll: it unrolls across the wooden floor, keeps "
        "rolling past the desk and out through the open door into the snow, getting longer and longer. Santa "
        "watches it go with wide, surprised eyes behind his glasses, then laughs and holds his belly. Santa "
        "stays in the frame the whole time and the parchment stays blank",
        "camera": "Static camera, medium-wide shot, no zoom, no camera movement.",
        "sekundy": 7,
    },
    "w3_mowi": {
        "scena": "W3",
        "opis": "Kadr dla HeyGen: Mikołaj z rulonem listy pod pachą patrzy w kamerę",
        "scene": "Medium close-up of Santa standing in his cozy study at night, holding a thick roll of cream "
        "parchment, the nice list, under one arm, looking straight into the camera with a warm, amused "
        "expression. His whole face, glasses, beard and heavy mustache are clearly visible and well lit from "
        "the front, eyes open, head straight. Bookshelves and fireplace glow softly blurred in the background. "
        "The parchment has no writing.",
        "wideo": False,
        "heygen": "Santa speaks warmly and with gentle humor, small nods, smiling eyes, occasionally patting "
        "the roll of parchment under his arm. His head stays steady and his face stays fully visible.",
    },
    "w3_platek": {
        "scena": "W3",
        "opis": "Płatek trzyma koniec listy w pysku jak szalik, Mikołaj ciągnie za drugi koniec",
        "scene": "Santa stands at the open wooden door of his cozy study at night, holding one end of a very "
        "long cream parchment scroll. The young reindeer stands in the doorway holding the other end of the "
        "scroll gently in his mouth, with part of it wrapped around his neck like a scarf. Snow falls outside. "
        "Warm light. Santa's face, glasses and beard are clearly visible. The parchment has no writing.",
        "motion": "The young reindeer playfully tugs his end of the scroll, Santa gently tugs back, shaking his "
        "head with a laugh; the young reindeer tilts his head innocently and the scroll slips from his neck "
        "like a scarf. Funny, gentle moment, nobody gets hurt. Santa stays in the frame the whole time",
        "platek": True,
        "camera": "Static camera, medium-wide shot, no zoom, no camera movement.",
        "sekundy": 6,
    },
}

# --- kwestie Mikołaja (ElevenLabs, zapisany głos Mikołaja) ----------------------------------
#
# Liczby słownie, żeby głos przeczytał je poprawnie. Mikołaj mówi do rodziców w liczbie
# mnogiej („Wy”), bez form zależnych od płci rodzica i dziecka. Nagrania: polecenie
# `kwestie`, pliki output/reklama_zapisy_poziomo/glos/<klucz>.mp3.
#   ujecie   gdzie słychać kwestię: kadr HeyGen (ruch warg) albo klip, pod który idzie głos zza kadru

KWESTIE: dict[str, dict] = {
    # Wariant 1 „Tajna narada”
    "w1_1": {"ujecie": "w1_mowi", "tekst": "Ciii… Drodzy rodzice, czy dzieci już śpią? To dobrze. "
             "Mam do Was sprawę, ale musi zostać między nami, dorosłymi."},
    "w1_2": {"ujecie": "w1_elf", "tekst": "Elfy też nie podsłuchują!"},
    "w1_3": {"ujecie": "w1_mowi", "tekst": "W tym roku nagram dla Waszego dziecka osobistą wiadomość. "
             "Powiem do niego po imieniu i pochwalę za to, czego się nauczyło."},
    "w1_4": {"ujecie": "ksiega, lista", "tekst": "Pokażę jego zdjęcie w mojej magicznej księdze "
             "i wpiszę imię na listę grzecznych dzieci. Szczegóły podpowiecie mi w krótkim formularzu."},
    "w1_5": {"ujecie": "w1_mowi", "tekst": "Zamówienia przyjmuję od dwudziestego piątego listopada. "
             "A kto zapisze się wcześniej, dostanie ode mnie kod rabatowy: minus dwadzieścia pięć procent."},
    "w1_6": {"ujecie": "w1_ciii", "tekst": "Zapiszcie się już dziś. I ani słowa dzieciom! Ho, ho, ho! …Ciii."},
    # Wariant 2 „Czy to już nagrywa?”
    "w2_1": {"ujecie": "w2_za_blisko", "tekst": "Halo? Czy to już nagrywa? Elfie, czerwona lampka się świeci?"},
    "w2_2": {"ujecie": "w2_mowi", "tekst": "Ho, ho, ho! Dzień dobry, drodzy rodzice! Elfy namówiły mnie "
             "na to nagranie, bo w tym roku mam dla Was coś nowego."},
    "w2_3": {"ujecie": "ksiega, lista", "tekst": "Nagram dla Waszego dziecka osobistą wiadomość. "
             "Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, pokażę jego zdjęcie w magicznej "
             "księdze i wpiszę imię na listę grzecznych dzieci."},
    "w2_4": {"ujecie": "w2_mowi", "tekst": "Zamówienia ruszają dwudziestego piątego listopada. Kto zapisze się "
             "wcześniej, dostanie kod rabatowy. Elfy mówią, że to minus dwadzieścia pięć procent. "
             "Ja mówię: prezent dla rodziców!"},
    "w2_5": {"ujecie": "w2_wylacz", "tekst": "Zapiszcie się już dziś. A teraz… jak to się wyłącza? Elfie?"},
    # Wariant 3 „Za długa lista”
    "w3_1": {"ujecie": "w3_rolka", "tekst": "Ho, ho, ho! W tym roku dzieci są tak grzeczne, że lista "
             "nie mieści się w gabinecie!"},
    "w3_2": {"ujecie": "w3_mowi", "tekst": "Dlatego, drodzy rodzice, potrzebuję Waszej pomocy. "
             "Nagram dla Waszego dziecka osobistą wiadomość."},
    "w3_3": {"ujecie": "ksiega", "tekst": "Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, "
             "i pokażę jego zdjęcie w magicznej księdze. Szczegóły podpowiecie mi w krótkim formularzu."},
    "w3_4": {"ujecie": "w3_mowi", "tekst": "Zamówienia ruszają dwudziestego piątego listopada. Zapiszcie się "
             "wcześniej, a dostaniecie kod rabatowy, minus dwadzieścia pięć procent, i wiadomość o starcie "
             "jako pierwsi."},
    "w3_5": {"ujecie": "w3_platek", "tekst": "Płatku! Oddaj listę, to nie jest szalik!"},
}

# --- budowanie promptów ---------------------------------------------------------------------

BASE_NO_SANTA = """\
Scene: {scene}
Warm cinematic lighting, photorealistic, {frame}.
No children appear in the image; every person in it is an adult.
No brand logos, no text, no letters anywhere in the image."""


def frame_prompt(key: str, with_platek_reference: bool = True) -> str:
    """Prompt kadru startowego ujęcia (Nano Banana Pro), poziomy 16:9."""
    shot = SHOTS[key]
    if shot.get("santa", True):
        # Wspólne zasady kadru (prompts.SCENE_RULES) kończą się „16:9”; dopisujemy kompozycję reklamy.
        prompt = prompts.SCENE_PROMPT.format(scene=shot["scene"]).replace(
            "photorealistic, 16:9.", f"photorealistic, {HORIZONTAL}.")
    else:
        prompt = BASE_NO_SANTA.format(scene=shot["scene"], frame=HORIZONTAL)
    if shot.get("elves"):
        prompt += "\n" + prompts.ELVES_DESCRIPTION
    if shot.get("platek"):
        if with_platek_reference:
            prompt += "\n" + od_listu_do_san.PLATEK_REFERENCE_NOTE
        prompt += "\n" + od_listu_do_san.PLATEK_DESCRIPTION
    return prompt


def motion_prompt(key: str, seconds) -> str:
    """Prompt ruchu klipu (Gemini Omni Flash). Głos Mikołaja dokłada montaż."""
    shot = SHOTS[key]
    motion = shot["motion"]
    if shot.get("platek"):
        motion += ". The young reindeer keeps exactly the same look, size and red harness for the whole shot"
    return prompts.motion_prompt(motion, seconds, shot.get("camera"))


def needs_santa_reference(key: str) -> bool:
    return SHOTS[key].get("santa", True)


def video_shots() -> list[str]:
    return [k for k, s in SHOTS.items() if s.get("wideo", True)]


def new_frame_shots() -> list[str]:
    return list(SHOTS)
