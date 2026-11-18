"""Wszystkie prompty i kwestie z MVP.md w jednym miejscu.

Prompty dla modeli obrazu i wideo są po angielsku (modele lepiej je wykonują),
kwestie mówione po polsku.
"""

# --- Obrazy (Nano Banana Pro) -------------------------------------------------

PORTRAIT_PROMPT = """\
Photorealistic portrait of a warm, kind Santa Claus, about 70 years old,
full white natural-looking beard, rosy cheeks, gentle smiling eyes,
classic red velvet coat with white fur trim, no hat or with a soft red hat.
He sits in a cozy armchair in his wooden workshop, warm fireplace light,
soft bokeh Christmas lights in the background.
Front-facing, looking straight into the camera, head and shoulders framing,
mouth closed in a calm gentle smile, face evenly lit and fully visible,
nothing covering the mouth or beard.
Cinematic 16:9, high detail, natural skin texture.
Original character design, no brand logos, no text."""

# Wariant z bardzo długą brodą, okularami i klasycznym, zadbanym strojem: bez dzierganej
# czapki i zniszczonego wyglądu, które dawał pierwszy prompt. Krzaczaste wąsy całkowicie zakrywają usta,
# więc przy mówieniu widać tylko ruch wąsów i brody, a drobne niedokładności
# synchronizacji z dźwiękiem są mniej widoczne. Szkła bez odblasków, żeby było widać oczy.
# Kadr pokazuje większą część sylwetki, do kolan.
PORTRAIT_PROMPT_FULL_BEARD = """\
Photorealistic portrait of the classic, magical Santa Claus from a storybook:
a kind, gentle, well-cared-for elderly grandfather, about 80 years old,
with a warm, healthy glow and the wise, kindly face of a very old man.
His mustache is long and heavy and hangs straight down from under his nose, covering
his mouth completely, and flows directly into his beard as one continuous mass of
white hair. Below his nose there is only white hair, no visible mouth.
An enormous, very voluminous snow-white beard, wide and full, softly flowing and only
slightly wavy, spreading over his whole chest and reaching down to his belly and lap.
Long, softly flowing snow-white hair falling over his shoulders.
The beard and hair look real and natural, full, clean and well cared for.
Small round gold wire-rimmed spectacles resting on his nose, clear lenses without
glare, so his bright, kind, twinkling eyes are fully visible through them.
Clearly elderly features: soft wrinkles across the forehead, deep laugh lines and
crow's feet around the eyes, full rosy cheeks, bushy snow-white eyebrows.
Aged but well cared for, never tired or neglected.
His kindness shows in his eyes and cheeks.
A classic Santa hat in rich red velvet with a thick white fur trim and a white pompom.
A luxurious deep red velvet coat with pristine, thick white fur trim,
a wide black leather belt with a polished gold buckle, white fur cuffs.
Everything he wears is clean, rich and immaculate.
He sits comfortably in a grand carved wooden armchair with red upholstery in his
cozy workshop, hands resting calmly on the armrests,
warm golden fireplace light, soft bokeh Christmas tree lights in the background.
Front-facing, looking straight into the camera, medium shot framed from the top
of the hat down to his knees, so most of his figure and the whole beard are visible,
with the face still large and clear in the upper part of the frame.
Face evenly lit.
Again, the most important detail: the heavy mustache hangs straight down over the
mouth into the beard, so the mouth is fully covered by hair.
Cinematic 16:9, high detail, warm storybook atmosphere.
Original character design, no brand logos, no text."""

PORTRAIT_VARIANTS = {
    "klasyczny": PORTRAIT_PROMPT,
    "pelna-broda": PORTRAIT_PROMPT_FULL_BEARD,
}

# Portret wzorcowy Płatka, najmłodszego renifera (scenariusz 4). Jest referencją dla
# wszystkich kadrów z Płatkiem, żeby w stajni, przy worku i w zaprzęgu wyglądał tak samo.
# Znak rozpoznawczy: biała łatka w kształcie płatka śniegu na czole i dzwoneczek na
# czerwonej wstążce. Nos zwykły, czarny: Płatek to nasza postać, nie znany czerwononosy renifer.
PLATEK_PORTRAIT_PROMPT = """\
Photorealistic full-body portrait of Płatek, the youngest reindeer of Santa's team:
a young, small and slender reindeer calf, clearly smaller than an adult reindeer,
with long thin legs, big shiny dark eyes with long lashes and soft fluffy fur.
His fur is warm light brown with a cream-white chest, cream-white muzzle and
cream-white fur around the hooves. On his forehead, between the eyes, there is one
small clear white patch shaped like a snowflake. Short, young, velvety antlers with
only two small points on each side. A normal black reindeer nose, not red, not glowing.
Around his neck a thin red ribbon with one small round golden bell.
He stands on fresh straw in a cozy wooden reindeer stable at night, seen from a
three-quarter side view, the whole body from antlers to hooves visible and sharp,
head turned towards the camera with a curious, eager and friendly expression.
Warm lantern light, softly blurred wooden stalls in the background.
Cinematic 16:9, high detail, warm storybook atmosphere.
Original character design, no people, no brand logos, no text."""

# Zasady wspólne dla każdego kadru sceny; przed nimi stoją reguły postaci z referencji.
SCENE_RULES = """\
Scene: {scene}
Warm cinematic lighting, photorealistic, 16:9.
No children appear in the image; every person in it is an adult.
No brand logos, no text, no letters anywhere in the image."""

# Kadr z jedną referencją: portretem Mikołaja (sceny z wersji krótkiej i większość nowych).
SCENE_PROMPT = """\
Use the attached image as the reference character. Keep Santa's face, age,
glasses, beard, mustache, hair, hat, coat and proportions exactly the same.
His mustache hangs down over his mouth into the beard exactly as in the reference,
so his mouth stays covered by hair.
""" + SCENE_RULES

# Reguły postaci, gdy kadr ma kilka referencji albo tylko Płatka. {nr} to numer obrazu
# w kolejności wysyłania (kolejność z klucza "refs" sceny).
REFERENCE_RULES = {
    "portrait": """\
Santa: attached image {nr} is his reference. Keep Santa's face, age, glasses, beard,
mustache, hair, hat, coat and proportions exactly the same as in it.
His mustache hangs down over his mouth into the beard exactly as in the reference,
so his mouth stays covered by hair.""",
    "platek": """\
Płatek, the youngest reindeer: attached image {nr} is his reference. Keep his small
size, light brown fur with cream-white chest and muzzle, the white snowflake-shaped
patch on his forehead, his short young antlers, his black nose and the red ribbon
with a small golden bell exactly the same as in it. He is clearly smaller than
the adult reindeer.""",
}

# Kadr bez postaci z referencji (np. zbliżenie na kopertę).
SCENE_PROMPT_NO_REFERENCE = SCENE_RULES

# Wygląd elfów, dopisywany do każdej sceny z "elves": True, żeby we wszystkich scenach
# wyglądały tak samo (portret pilnuje tylko wyglądu Mikołaja). Elfy są wyraźnie dorosłe:
# model wideo odrzuca kadry z dziećmi, a "nastolatkowie" wychodzili jak dzieci.
ELVES_DESCRIPTION = """\
Santa's elves are all adults: slim young adult men and women in their mid twenties,
clearly grown-up, with adult faces, adult height and adult body proportions,
about as tall as Santa. They have slightly pointed ears and natural, healthy skin
without any makeup, and wear green and red wool outfits and pointed felt caps. They are always busy working,
focused on their tasks, never posing. Fairy-tale but realistic, in the same
photorealistic, warm cinematic style as the rest of the image.
There are no children anywhere in the image."""


def scene_references(key: str) -> list[str]:
    """Nazwy zatwierdzonych obrazów (output/selected/<nazwa>.png) wysyłanych jako referencje.

    Domyślnie portret Mikołaja; scena może podać własną listę w kluczu "refs"
    (np. ["portrait", "platek"] albo [] dla kadru bez postaci).
    """
    return list(SCENES[key].get("refs", ["portrait"]))


def scene_prompt(key: str) -> str:
    """Pełny prompt kadru sceny: reguły postaci z referencji, opis sceny i, jeśli w scenie są elfy, ich stały wygląd."""
    scene = SCENES[key]
    refs = scene_references(key)
    if refs == ["portrait"]:
        prompt = SCENE_PROMPT.format(scene=scene["scene"])
    elif refs:
        rules = [REFERENCE_RULES[ref].format(nr=nr) for nr, ref in enumerate(refs, start=1)]
        prompt = "\n".join(["Use the attached images as references for the characters.", *rules, ""])
        prompt += SCENE_RULES.format(scene=scene["scene"])
    else:
        prompt = SCENE_PROMPT_NO_REFERENCE.format(scene=scene["scene"])
    if scene.get("elves"):
        prompt += "\n" + ELVES_DESCRIPTION
    return prompt


# Klucz sceny -> opis [SCENE] dla kadru i [MOTION] dla klipu wideo.
SCENES = {
    "zorza": {
        "scene": "Wide view of a snowy North Pole village at night under a bright green and violet "
        "aurora borealis, small wooden houses with warm glowing windows, Santa not visible.",
        "motion": "The aurora ripples slowly across the sky, smoke rises from the chimneys, snow sparkles",
    },
    "dom": {
        "scene": "Exterior of Santa's cozy wooden house at night, snow falling, "
        "warm light in the windows, Santa not visible yet.",
        "motion": "Snow falls softly, lights flicker in the windows",
    },
    "pracownia": {
        "scene": "Santa walking through his busy workshop full of wrapped presents "
        "and toys, elves working in the background.",
        "motion": "Santa walks slowly between shelves with presents, elves busy in the background",
        "elves": True,
    },
    "renifery": {
        "scene": "Santa in a cozy wooden reindeer stable at night, gently stroking a reindeer's neck, "
        "several reindeer with warm red blankets, hay, glowing lanterns.",
        "motion": "Santa gently strokes a reindeer, the reindeer nod and breathe out small warm clouds",
    },
    "listy": {
        "scene": "Santa's letter room: piles of colorful envelopes with letters sent to Santa, elves sorting them "
        "into wooden pigeonholes, Santa sitting at a desk reading one letter, his eyes smiling warmly. "
        "All envelopes and letters are blank, without any writing.",
        "motion": "Elves sort envelopes into the pigeonholes, Santa slowly reads a letter, his eyes smiling",
        "elves": True,
    },
    "ksiega": {
        "scene": "Santa sitting in his armchair, opening a huge old leather-bound book "
        "on his lap, golden magical glow coming from the pages.",
        "motion": "Santa slowly opens the book, golden light rises from the pages",
    },
    "mapa": {
        "scene": "Santa standing in front of a huge old illuminated world map on a wooden wall, "
        "tiny golden lights glowing across it, a large globe nearby, warm lamp light. "
        "The map has no labels and no text.",
        "motion": "Tiny lights on the map twinkle one by one, Santa points at the map and nods happily",
    },
    "sanie": {
        "scene": "Santa next to his sleigh with reindeer in the snow at night, "
        "waving goodbye to the camera.",
        "motion": "Santa waves goodbye, reindeer shake their heads, the sleigh lifts off",
    },
    # Scenariusz 4 („Od listu do sań”), scena 3: śnieżna kula daje znak, że przyszło dziecko.
    # Na końcu filmu ta sama kula pokazuje dom dziecka (szablon_kula + zdjęcie w montażu).
    "kula": {
        "scene": "Medium shot of Santa sitting at his large wooden desk in his cozy study at night, framed from "
        "the waist up, his whole face, glasses and beard clearly visible. He is writing with a quill pen in a "
        "big leather notebook with blank pages. On the desk in front of him, slightly to the side, stands a "
        "small glass snow globe on a carved dark wooden base, with a tiny snowy village of wooden houses inside. "
        "Warm light from a desk lamp, a crackling fireplace softly blurred in the background, frost patterns "
        "on the window. The notebook pages are blank, without any writing.",
        "motion": "Santa calmly writes with the quill pen. Then the snow inside the small glass globe on the "
        "desk starts to swirl and the tiny village inside glows with warm golden light. Santa notices it, "
        "smiles with his eyes, puts the quill down and gently picks up the snow globe with both hands, "
        "holding it at chest height below his beard, so his face stays fully visible. He looks warmly towards "
        "the camera. Santa stays in the frame, in the same place and the same size for the whole shot; "
        "he never fades, disappears or turns into something else. The glass globe stays small, whole and round",
        # Bez najazdu: zbliżenie na kulę robi osobne ujęcie (szablon_kula) w montażu.
        "camera": "Static camera, locked-off medium shot, no zoom, no push-in, no camera movement.",
    },
    # Scenariusz 4, scena 4: sortownia na Poczcie Mikołaja. Inny kadr niż "listy" z wersji krótkiej.
    "sortownia": {
        "scene": "Santa's big post office hall at night: a long curved wooden slide in the middle of the room "
        "with sacks of colorful envelopes sliding down it, elves sorting the envelopes into tall walls of "
        "wooden pigeonholes, warm lantern light. Santa walks down the middle of the hall and pulls one "
        "envelope out of a pile, looking at it with a warm smile in his eyes. "
        "All envelopes are blank, without any writing, stamps or addresses.",
        "motion": "Envelopes slide down the wooden slide, elves sort them into the pigeonholes, Santa walks "
        "slowly and pulls out one envelope, looking at it warmly",
        "elves": True,
    },
    # Scena 4 bez zdjęcia listu: zbliżenie na kopertę z pieczęcią, bez postaci.
    "koperta": {
        "scene": "Close-up of a single cream paper envelope lying on Santa's old wooden desk, closed with "
        "a round red wax seal pressed with a small star, a quill pen and a candle beside it, warm candle "
        "light, softly blurred fireplace glow in the background. No people in the image. "
        "The envelope is blank, without any writing, stamps or addresses.",
        "motion": "The candle flame flickers gently, warm light plays over the red wax seal",
        "refs": [],
    },
    # Scena 6: Płatek ćwiczy podskoki i ląduje w sianie (sam Płatek, bez Mikołaja).
    "stajnia_skok": {
        "scene": "Inside a cozy wooden reindeer stable at night: Płatek, the young reindeer, stands on a soft "
        "pile of hay in the middle of the stable, crouching playfully as if getting ready to jump. Adult "
        "reindeer with warm red blankets watch from their stalls, glowing lanterns, golden straw on the floor. "
        "Santa is not visible.",
        "motion": "Płatek bounces a few times, tries to lift his hooves off the ground, jumps up a little and "
        "lands softly in the hay, then shakes his head happily; the adult reindeer watch calmly",
        "refs": ["platek"],
    },
    # Scena 6: Mikołaj głaszcze Płatka; ujęcie pod kwestie [W] i [P] o kibicowaniu.
    "stajnia": {
        "scene": "Santa in a cozy wooden reindeer stable at night, kneeling on the hay next to Płatek, the young "
        "reindeer, and gently stroking his neck. Płatek looks up at Santa eagerly. Adult reindeer with warm "
        "red blankets rest in their stalls in the background, glowing lanterns, golden straw.",
        "motion": "Santa gently strokes Płatek's neck and laughs softly, Płatek does one small happy hop "
        "in place and nuzzles Santa's hand",
        "refs": ["portrait", "platek"],
    },
    # Scena 8: pakowanie prezentu i dwie wstążki do wyboru.
    "pakowanie": {
        "scene": "Santa's wrapping room at night: on a big wooden table elves wrap a box in shiny red paper "
        "with small golden stars. Santa stands at the table holding up two large spools of ribbon, a red "
        "one in one hand and a golden one in the other, showing them with a warm smile in his eyes. "
        "Rolls of wrapping paper, ribbons and bows around, warm lamp light.",
        "motion": "Elves fold the red paper with golden stars around the box, Santa lifts the red and the "
        "golden ribbon spools one after another, as if asking which one to choose",
        "elves": True,
    },
    # Scena 8: wpadka elfa ze wstążką. Najtrudniejsze ujęcie, test w testy_fal (karta 2.1).
    "wpadka": {
        "scene": "Santa's wrapping room at night: one adult elf is comically tangled from shoulders to knees "
        "in long red and golden ribbons, with a big bow stuck on top of his cap, looking surprised. Two other "
        "elves hold the ends of the ribbons, ready to unwind him, and Santa stands beside them laughing "
        "warmly with his eyes, one hand on his belly. A half-wrapped red box with golden stars on the table.",
        "motion": "The tangled elf turns slowly in place while the other elves unwind the ribbons from him, "
        "the bow falls off his cap, Santa laughs warmly and helps pull the last ribbon free",
        "elves": True,
    },
    # Scena 9: Mikołaj czyta wiadomość od bliskich. Ramka ze zdjęciem to osobne zbliżenie (szablon_bliscy).
    "bliscy": {
        "scene": "Medium shot of Santa sitting at his large wooden desk in his cozy study at night, framed "
        "from the waist up, his whole face, glasses and beard clearly visible. He holds an open cream "
        "envelope sealed with a small red wax heart and reads a folded letter from it, his eyes smiling "
        "warmly. In the background on the desk stands a small glass snow globe on a carved dark wooden "
        "base. Warm desk lamp light, snow falling outside the window, fireplace glow. "
        "The envelope and the letter are blank, without any writing.",
        "motion": "Santa unfolds the letter and reads it slowly, smiling with his eyes and nodding gently, "
        "snow falls outside the window",
        "camera": "Static camera, locked-off medium shot, no zoom, no push-in, no camera movement.",
    },
    # Scena 10: prezent wpada do worka, Płatek dopycha paczkę. Bez Mikołaja.
    "worek": {
        "scene": "A big wooden sleigh hangar at night: a wrapped red present with golden stars and a big bow "
        "rides along a wooden conveyor belt towards a huge open red sack lying on Santa's sleigh. Next to "
        "the sack stands Płatek, the young reindeer, pushing a small parcel that almost fell back onto the "
        "belt with his nose. Elves stand around the sleigh clapping. Warm lantern light. Santa is not visible.",
        "motion": "The present rides along the conveyor belt and drops into the red sack, Płatek nudges a "
        "slipping parcel back with his nose, the elves clap happily",
        "elves": True,
        "refs": ["platek"],
    },
    # Scena 11: zaprzęganie; Płatek pierwszy raz w zaprzęgu.
    "zaprzeg": {
        "scene": "Outside Santa's sleigh hangar on a snowy night: reindeer stand in pairs in front of Santa's "
        "big red wooden sleigh full of presents, elves fasten harnesses with golden bells. Płatek, the young "
        "reindeer, stands in the harness at the front for the first time, head held high. Santa sits in the "
        "sleigh holding the reins and smiling with his eyes. Green aurora in the sky above the village.",
        "motion": "Elves buckle the last harness, the bells jingle, Płatek trembles a little and then lifts his "
        "head proudly, Santa takes the reins",
        "elves": True,
        "refs": ["portrait", "platek"],
    },
    # Scena 11: start sań i odlot w stronę zorzy.
    "start": {
        "scene": "Santa's red sleigh pulled by reindeer, with Płatek, the young reindeer, at the front, lifting "
        "off from the snowy village at night and flying up towards a bright green and violet aurora. Santa "
        "sits in the sleigh holding the reins, a big red sack of presents behind him. Wide shot, small wooden "
        "houses with warm glowing windows below.",
        "motion": "The reindeer run, the sleigh lifts off the snow and climbs into the sky towards the aurora, "
        "Płatek flies at the front with the others",
        "camera": "Camera slowly tilts up and follows the sleigh into the sky.",
        "refs": ["portrait", "platek"],
    },
}

# Puste szablony do personalizacji (napisy dodaje się w edytorze).
TEMPLATES = {
    "szablon_ksiega": """\
Top-down close-up of a huge old open leather book on a wooden table,
the right page holds an empty ornate golden picture frame (blank inside,
plain cream paper), the left page has decorative golden Christmas ornaments,
soft candle light, sparkles of magic dust. 16:9, photorealistic.
No text, no letters, no people.""",
    "szablon_lista": """\
An old parchment scroll titled with an empty ornamental banner at the top,
unrolled on Santa's wooden desk, many blank lines, a red wax seal and a
quill pen next to it, warm candle light. 16:9, photorealistic.
No text, no letters, no writing on the scroll.""",
    # Scenariusz 4, koniec filmu: w pustą kulę montaż wkleja zdjęcie domu albo ogólny domek.
    "szablon_kula": """\
Close-up, straight front view of a glass snow globe standing on a carved dark
wooden base on Santa's wooden desk at night. The inside of the glass sphere is
empty and filled with soft, even, cream-white mist, with no objects inside,
so a picture can be placed inside later. Gentle reflections only on the edges
of the glass. Warm candle and desk lamp light, blurred golden fireplace glow in
the background. The globe is centered and fills about half of the frame height.
16:9, photorealistic. No text, no letters, no people.""",
    # Koniec filmu bez zdjęcia domu: ta sama kula z ogólnym domkiem w środku.
    "szablon_kula_domek": """\
Close-up, straight front view of a glass snow globe standing on a carved dark
wooden base on Santa's wooden desk at night. Inside the glass sphere stands one
tiny snowy wooden cottage with a snow-covered roof and one warmly glowing window,
on a small snowy hill, with gentle snowflakes floating around it. Gentle
reflections only on the edges of the glass. Warm candle and desk lamp light,
blurred golden fireplace glow in the background. The globe is centered and
fills about half of the frame height.
16:9, photorealistic. No text, no letters, no people.""",
    # Scena 4: w pustą ramkę montaż wkleja zdjęcie listu albo rysunku dziecka.
    "szablon_poczta": """\
Top-down close-up of Santa's old wooden desk with a large empty wooden picture
frame lying flat in the center, the inside of the frame is plain, even cream
paper, completely blank, so a picture can be placed inside later. Around the
frame: a few blank cream envelopes, a red wax seal, a quill pen and a burning
candle, soft warm candle light. The frame fills about two thirds of the frame
height. 16:9, photorealistic. No text, no letters, no writing, no people.""",
    # Scena 8: na pustym bileciku montaż wypisuje imię dziecka odręcznym pismem.
    "szablon_bilecik": """\
Close-up of a present wrapped in shiny red paper with small golden stars,
tied with a red and a golden ribbon in one big double bow. A blank cream paper
gift tag hangs from the bow on a thin golden string, facing the camera straight
on, flat and evenly lit, large and sharp in the center of the frame, completely
empty, so a name can be written on it later. Warm lamp light, softly blurred
Christmas lights in the background. 16:9, photorealistic.
No text, no letters, no writing on the tag, no people.""",
    # Scena 9: w pustą ramkę na biurku montaż wkleja zdjęcie bliskich.
    "szablon_bliscy": """\
Close-up of a small carved wooden picture frame standing upright on Santa's
wooden desk at night, facing the camera straight on, the inside of the frame is
plain, even cream paper, completely blank, so a photo can be placed inside later.
Next to it an open cream envelope with a small red wax heart seal. In the softly
blurred background a small glass snow globe, a desk lamp and fireplace glow,
snow falling outside the window. The frame is centered and fills about half of
the frame height. 16:9, photorealistic. No text, no letters, no people.""",
}

# --- Wideo (Gemini Omni Flash) ----------------------------------------------------------

MOTION_PROMPT = """\
In a single continuous shot, no scene cuts. {camera} {motion}.
Calm, magical Christmas atmosphere, soft ambient sounds only (crackling fire,
sleigh bells far away). No dialogue, nobody speaks, no lip movement, no music,
no text, no logos. {seconds} seconds."""

# Ruch kamery w klipie. Domyślnie powolny najazd; scena może podać własny w kluczu "camera".
# Przy kuli najazd sprawiał, że model „gubił” Mikołaja, więc tam kamera stoi.
DEFAULT_CAMERA = "Gentle slow camera push-in."


def motion_prompt(motion: str, seconds, camera: str | None = None) -> str:
    """Prompt ruchu dla klipu wideo: stałe zasady, ruch kamery i opis ruchu sceny."""
    return MOTION_PROMPT.format(camera=camera or DEFAULT_CAMERA, motion=motion, seconds=seconds)


def scene_motion_prompt(key: str, seconds) -> str:
    scene = SCENES[key]
    return motion_prompt(scene["motion"], seconds, scene.get("camera"))

# --- Głos i muzyka (ElevenLabs) -----------------------------------------------

VOICE_DESCRIPTION = """\
A warm, deep, gentle voice of a kind elderly man around 70, like a loving
grandfather telling a bedtime story. Slow, calm pace, soft friendly
laugh, slightly husky, very clear diction. Native Polish speaker with a
natural Polish accent and lively, warm intonation."""

# Voice Design wymaga 100–1000 znaków tekstu próbnego.
VOICE_SAMPLE_TEXT = (
    "Ho, ho, ho! Dzień dobry, kochanie. Cały rok patrzyłem, jak pięknie rośniesz. "
    "Moje elfy opowiadały mi o tobie same dobre rzeczy, a renifery już nie mogą się "
    "doczekać Wigilii. Usiądź wygodnie, bo mam dla ciebie wiadomość."
)

# Tekst do porównania ustawień głosu (`audio probki`): pytanie, śmiech, powitanie i ciepłe zdanie,
# żeby było słychać intonację, a nie tylko barwę.
# Wskazówki w nawiasach czytają tylko modele v3 i v4; dla starszych audio.synthesize je usuwa.
VOICE_TEST_TEXT = (
    "[curious] Halo? Czy to już nagrywa? [laughs] Ho, ho, ho! Dzień dobry, drodzy rodzice! W tym roku nagram "
    "dla Waszego dziecka osobistą wiadomość. Powiem do niego po imieniu i pochwalę za to, czego się nauczyło. "
    "[pause] A teraz… [confused] jak to się wyłącza?"
)

MUSIC_PROMPT = (
    "Gentle, warm instrumental Christmas underscore for a children's video. "
    "Soft orchestral strings, celesta, sleigh bells and light piano, magical and cozy, "
    "calm tempo, no vocals, no lyrics, suitable as background under narration."
)

# Kwestie ogólne: wersja dla jednego dziecka i dla rodzeństwa (liczba mnoga).
# Klucz = nazwa sceny i pliku MP3 (audio/lines/<klucz>.mp3), kolejność w montage.TIMELINE.
GENERAL_LINES = {
    "zorza": {
        "single": "Ho, ho, ho! Spójrz w niebo. Tak tańczy zorza polarna nad moją wioską "
        "na dalekiej Północy.",
        "plural": "Ho, ho, ho! Spójrzcie w niebo. Tak tańczy zorza polarna nad moją wioską "
        "na dalekiej Północy.",
    },
    "dom": {
        "single": "Witaj w moim domu. Mieszkam tu razem z elfami i reniferami.",
        "plural": "Witajcie w moim domu. Mieszkam tu razem z elfami i reniferami.",
    },
    "pracownia": {
        "single": "Tu, w mojej pracowni, elfy pracują dzień i noc. Pakują prezenty i pilnują, "
        "żeby wszystko było gotowe na Święta.",
        "plural": "Tu, w mojej pracowni, elfy pracują dzień i noc. Pakują prezenty i pilnują, "
        "żeby wszystko było gotowe na Święta.",
    },
    "renifery": {
        "single": "A to moje renifery. Codziennie ćwiczą latanie, żeby w Wigilię być "
        "najszybsze na świecie. Lubią, kiedy drapię je za uszami.",
        "plural": "A to moje renifery. Codziennie ćwiczą latanie, żeby w Wigilię być "
        "najszybsze na świecie. Lubią, kiedy drapię je za uszami.",
    },
    "listy": {
        "single": "Tutaj trafiają listy od dzieci z całego świata. Elfy czytają każdy z nich "
        "bardzo uważnie. Ale dziś odkładam pracę na chwilę, bo mam bardzo ważną wiadomość. "
        "Wiadomość tylko dla ciebie.",
        "plural": "Tutaj trafiają listy od dzieci z całego świata. Elfy czytają każdy z nich "
        "bardzo uważnie. Ale dziś odkładam pracę na chwilę, bo mam bardzo ważną wiadomość. "
        "Wiadomość tylko dla was.",
    },
    "ksiega": {
        "single": "To moja magiczna księga. Zapisuję w niej wszystkie dzieci, które w tym roku "
        "starały się być dobre. Spójrz, kto jest na tej stronie! Księga nigdy się nie myli.",
        "plural": "To moja magiczna księga. Zapisuję w niej wszystkie dzieci, które w tym roku "
        "starały się być dobre. Spójrzcie, kto jest na tej stronie! Księga nigdy się nie myli.",
    },
    "lista": {
        "single": "A tu jest moja lista grzecznych dzieci. Twoje imię jest już na niej zapisane. "
        "Przybijam pieczęć… gotowe!",
        "plural": "A tu jest moja lista grzecznych dzieci. Wasze imiona są już na niej zapisane. "
        "Przybijam pieczęć… gotowe!",
    },
    "mapa": {
        "single": "A to moja wielka mapa. Świecą na niej domy wszystkich grzecznych dzieci. "
        "Popatrz, jak pięknie świeci. Elfy sprawdzają ją każdego wieczoru.",
        "plural": "A to moja wielka mapa. Świecą na niej domy wszystkich grzecznych dzieci. "
        "Popatrzcie, jak pięknie świeci. Elfy sprawdzają ją każdego wieczoru.",
    },
    "sanie": {
        "single": "Muszę już wracać do pracy, bo reniferów nie można zostawiać samych na długo. "
        "Słuchaj rodziców i uśmiechaj się często. Do zobaczenia w Wigilię! Ho, ho, ho! "
        "Wesołych Świąt!",
        "plural": "Muszę już wracać do pracy, bo reniferów nie można zostawiać samych na długo. "
        "Słuchajcie rodziców i uśmiechajcie się często. Do zobaczenia w Wigilię! Ho, ho, ho! "
        "Wesołych Świąt!",
    },
    # --- Wersja długa: scenariusz 4 „Od listu do sań”, kwestie [W] ---
    # Przedrostek d_ oddziela je od kwestii wersji krótkiej (te zostają do czasu TIMELINE_LONG,
    # karta 1.6). Scena z kilkoma kwestiami ma klucze _1, _2, …, bo pauzę na reakcję
    # dziecka wstawia montaż między nagraniami. Kolejność jak w filmie.
    "d_zorza": {
        "single": "Ho, ho, ho! Spójrz w niebo. Tak tańczy zorza polarna nad moją wioską "
        "na dalekiej Północy.",
        "plural": "Ho, ho, ho! Spójrzcie w niebo. Tak tańczy zorza polarna nad moją wioską "
        "na dalekiej Północy.",
    },
    "d_dom": {
        "single": "A to mój dom. Wejdź, proszę. Przy kominku jest ciepło, a ja mam dziś "
        "gościa specjalnego.",
        "plural": "A to mój dom. Wejdźcie, proszę. Przy kominku jest ciepło, a ja mam dziś "
        "gości specjalnych.",
    },
    # Zza kadru, gdy w kuli zaczyna padać śnieg; potem lip-sync z imieniem (HeyGen).
    "d_kula": {
        "single": "Ho, ho, ho! Moja śnieżna kula nigdy nie śnieży bez powodu. Robi to tylko wtedy, "
        "gdy zagląda do mnie ktoś wyjątkowy…",
        "plural": "Ho, ho, ho! Moja śnieżna kula nigdy nie śnieży bez powodu. Robi to tylko wtedy, "
        "gdy zaglądają do mnie wyjątkowi goście…",
    },
    # Po niej kwestia [P] z imieniem: „…ten jest od ciebie” / „…te są od was”.
    "d_poczta": {
        "single": "To moja poczta. Każdego dnia przychodzą tu tysiące listów z całego świata. "
        "Elfy sortują je według krajów, miast i ulic. A ten list…",
        "plural": "To moja poczta. Każdego dnia przychodzą tu tysiące listów z całego świata. "
        "Elfy sortują je według krajów, miast i ulic. A te listy…",
    },
    "d_pracownia_1": {
        "single": "Tu, w mojej pracowni, powstają prezenty dla dzieci z całego świata. Elfy pracują "
        "dzień i noc. Pomóż im! Weź niewidzialny młoteczek i stukaj razem z nimi: puk, puk, puk!",
        "plural": "Tu, w mojej pracowni, powstają prezenty dla dzieci z całego świata. Elfy pracują "
        "dzień i noc. Pomóżcie im! Weźcie niewidzialne młoteczki i stukajcie razem z nimi: "
        "puk, puk, puk!",
    },
    # Po pauzie 5 s na stukanie.
    "d_pracownia_2": {
        "single": "Ho, ho! Z taką pomocą skończymy przed czasem! A teraz chodź, ktoś w stajni "
        "bardzo chce cię poznać.",
        "plural": "Ho, ho! Z taką pomocą skończymy przed czasem! A teraz chodźcie, ktoś w stajni "
        "bardzo chce was poznać.",
    },
    # Po niej kwestia [P]: „{ZWROT}, pokaż mu, jak wysoko umiesz skakać!”.
    "d_stajnia_1": {
        "single": "To Płatek, najmłodszy z moich reniferów. Cały rok ćwiczy podskoki, bo marzy "
        "o pierwszym locie w zaprzęgu. Jeszcze trochę mu brakuje… Hop!",
        "plural": "To Płatek, najmłodszy z moich reniferów. Cały rok ćwiczy podskoki, bo marzy "
        "o pierwszym locie w zaprzęgu. Jeszcze trochę mu brakuje… Hop!",
    },
    # Po pauzie 3 s na kibicowanie. Mikołaj mówi do Płatka, więc wersje są takie same.
    "d_stajnia_2": {
        "single": "Brawo! Widzisz, Płatku? Masz kibiców. Jeszcze dziś może przyjść twoja wielka "
        "chwila. A my zajrzyjmy do magicznej księgi, elfy coś zapisały.",
        "plural": "Brawo! Widzisz, Płatku? Masz kibiców. Jeszcze dziś może przyjść twoja wielka "
        "chwila. A my zajrzyjmy do magicznej księgi, elfy coś zapisały.",
    },
    # Po niej opowieść o dziecku [T].
    "d_ksiega": {
        "single": "To moja magiczna księga. Elfy zapisują w niej wszystko, co ważnego wydarzyło się "
        "u dzieci w tym roku. Zobaczmy, co jest na twojej stronie…",
        "plural": "To moja magiczna księga. Elfy zapisują w niej wszystko, co ważnego wydarzyło się "
        "u dzieci w tym roku. Zobaczmy, co jest na waszych stronach…",
    },
    # Po zdaniu o prezencie ([T] kupiony / [P] niekupiony); potem pauza 3 s na wybór kokardy.
    "d_pakowanie_1": {
        "single": "Jaką kokardę wybierzemy: czerwoną czy złotą? Powiedz głośno!",
        "plural": "Jaką kokardę wybierzemy: czerwoną czy złotą? Powiedzcie głośno!",
    },
    # Wpadka elfa ze wstążką.
    "d_pakowanie_2": {
        "single": "Ojej… ktoś tu trochę przesadził z dekoracją! Spokojnie, spokojnie, wystarczy "
        "odwinąć… i gotowe!",
        "plural": "Ojej… ktoś tu trochę przesadził z dekoracją! Spokojnie, spokojnie, wystarczy "
        "odwinąć… i gotowe!",
    },
    "d_pakowanie_3": {
        "single": "Ho, ho! W takim razie elfy zawiążą obie kokardy, żeby było podwójnie pięknie. "
        "I jeszcze bilecik z imieniem, żeby nikt nie pomylił prezentów.",
        "plural": "Ho, ho! W takim razie elfy zawiążą na każdym prezencie obie kokardy, żeby było "
        "podwójnie pięknie. I jeszcze bileciki z imionami, żeby nikt nie pomylił prezentów.",
    },
    # Po niej kwestia [P] z {BLISCY} i opcjonalna wiadomość od bliskich [T].
    "d_bliscy_1": {
        "single": "Wiesz, kto pomaga mi najbardziej? Ci, którzy są przy tobie każdego dnia.",
        "plural": "Wiecie, kto pomaga mi najbardziej? Ci, którzy są przy was każdego dnia.",
    },
    # Bez „przytul ich”: rodzic może wybrać jedną osobę („mama”), więc zwrot pasuje do każdej liczby.
    "d_bliscy_2": {
        "single": "Zrób coś dla mnie: kiedy skończy się film, przytul mocno każdego, kto ogląda go "
        "razem z tobą. To najlepszy prezent, jaki można dać.",
        "plural": "Zróbcie coś dla mnie: kiedy skończy się film, przytulcie mocno każdego, kto ogląda "
        "go razem z wami. To najlepszy prezent, jaki można dać.",
    },
    # „Pomogłeś” mówi Mikołaj do Płatka, nie do dziecka.
    "d_worek": {
        "single": "I… hop! Prezent ląduje w moim worku. Mój worek jest magiczny: zmieszczą się "
        "w nim wszystkie prezenty świata, a i tak nigdy nie jest za ciężki. Brawo, Płatku, "
        "właśnie pomogłeś przy prawdziwej dostawie!",
        "plural": "I… hop! Prezenty lądują w moim worku. Mój worek jest magiczny: zmieszczą się "
        "w nim wszystkie prezenty świata, a i tak nigdy nie jest za ciężki. Brawo, Płatku, "
        "właśnie pomogłeś przy prawdziwej dostawie!",
    },
    # Po niej pauza 5 s na wspólne odliczanie.
    "d_zaprzeg": {
        "single": "Renifery, do zaprzęgu! Dzwoneczki zapięte, worek na miejscu. Dziś z nami leci "
        "Płatek, pierwszy raz! Pomożesz mi wystartować? Odliczaj ze mną: pięć… cztery… trzy… "
        "dwa… jeden…",
        "plural": "Renifery, do zaprzęgu! Dzwoneczki zapięte, worek na miejscu. Dziś z nami leci "
        "Płatek, pierwszy raz! Pomożecie mi wystartować? Odliczajcie ze mną: pięć… cztery… trzy… "
        "dwa… jeden…",
    },
    # Po niej klamra z kulą i pożegnanie [P] z imieniem.
    "d_start": {
        "single": "START! Ho, ho, ho!",
        "plural": "START! Ho, ho, ho!",
    },
}

# Klucze kwestii wersji długiej w kolejności filmu (do nagrywania i montażu wersji długiej).
LONG_LINES = [key for key in GENERAL_LINES if key.startswith("d_")]

# --- Tekst personalizowany (scena 3) ------------------------------------------
# ZAMROŻONE. Źródłem promptu i reguł jest Rails: app/app/services/orders/speech_prompt.rb
# i speech_checker.rb. Tej kopii nie zmieniamy; usuniemy ją po zapisie tekstu w Rails (karta 6.3 w PLAN_WDROZENIA.md).

SPEECH_CLOSING = "A teraz zajrzyjmy razem do mojej magicznej księgi!"
NEEDS_REVIEW = "DO SPRAWDZENIA"

SPEECH_PROMPT = """\
Jesteś Świętym Mikołajem. Napisz tekst, który powiesz do {adresat} w filmie.

Dane od rodzica:
{dane}

Zasady:
- {min_words}–{max_words} słów, czyli ok. {seconds} sekund mówienia.
- Zwróć się do {adresat_dop} 2–3 razy, zawsze dokładnie w podanej formie.
- Ciepło i prosto, językiem zrozumiałym dla dziecka w tym wieku.
- Pochwal konkretne osiągnięcie z danych.
- Użyj form gramatycznych zgodnych z płcią dziecka.
- "Do poprawy" wspomnij delikatnie jako zachętę, nigdy jako zarzut ani groźbę.
- Prezent kupiony: powiedz, że elfy już go szykują. Niekupiony: powiedz,
  że zapisałeś to marzenie, bez obietnicy.
- Nie wymyślaj faktów spoza danych. Żadnych adresów, nazwisk ani marek.
- Jeśli dane zawierają coś nieodpowiedniego dla dziecka, odpowiedz tylko:
  {needs_review}
- Zakończ zdaniem: "{closing}"

Zwróć wyłącznie tekst do przeczytania, z interpunkcją ułatwiającą
naturalne czytanie."""

CHILD_DATA = """\
- Jak zwracać się do dziecka (forma w wołaczu): {zwrot}
- Płeć: {plec}
- Wiek: {wiek}
- Osiągnięcie z tego roku: {osiagniecie}
- Co lubi: {zainteresowania}
- Nad czym może popracować (opcjonalnie): {do_poprawy}
- Wymarzony prezent: {prezent}
- Czy prezent jest już kupiony: {prezent_kupiony}"""
