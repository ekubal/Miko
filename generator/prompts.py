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

SCENE_PROMPT = """\
Use the attached image as the reference character. Keep Santa's face,
beard, hair, coat and proportions exactly the same.
Scene: {scene}
Warm cinematic lighting, photorealistic, 16:9.
No brand logos, no text, no letters anywhere in the image."""

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
    },
    "renifery": {
        "scene": "Santa in a cozy wooden reindeer stable at night, gently stroking a reindeer's neck, "
        "several reindeer with warm red blankets, hay, glowing lanterns.",
        "motion": "Santa gently strokes a reindeer, the reindeer nod and breathe out small warm clouds",
    },
    "listy": {
        "scene": "Santa's letter room: piles of colorful envelopes from children, elves sorting them "
        "into wooden pigeonholes, Santa sitting at a desk reading one letter with a warm smile. "
        "All envelopes and letters are blank, without any writing.",
        "motion": "Elves sort envelopes into the pigeonholes, Santa slowly reads a letter and smiles",
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
}

# --- Wideo (Veo 3.1) ----------------------------------------------------------

MOTION_PROMPT = """\
Gentle slow camera push-in. {motion}. Calm, magical Christmas atmosphere,
soft ambient sounds only (crackling fire, sleigh bells far away).
Nobody speaks, no lip movement, no text, no logos. 8 seconds."""

# --- Głos i muzyka (ElevenLabs) -----------------------------------------------

VOICE_DESCRIPTION = """\
A warm, deep, gentle voice of a kind elderly man around 70, like a loving
grandfather telling a bedtime story. Slow, calm pace, soft friendly
laugh, slightly husky, very clear diction. Native Polish speaker."""

# Voice Design wymaga 100–1000 znaków tekstu próbnego.
VOICE_SAMPLE_TEXT = (
    "Ho, ho, ho! Dzień dobry, kochanie. Cały rok patrzyłem, jak pięknie rośniesz. "
    "Moje elfy opowiadały mi o tobie same dobre rzeczy, a renifery już nie mogą się "
    "doczekać Wigilii. Usiądź wygodnie, bo mam dla ciebie wiadomość."
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
}

# --- Tekst personalizowany (scena 3) ------------------------------------------

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
