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

SCENE_PROMPT = """\
Use the attached image as the reference character. Keep Santa's face,
beard, hair, coat and proportions exactly the same.
Scene: {scene}
Warm cinematic lighting, photorealistic, 16:9.
No brand logos, no text, no letters anywhere in the image."""

# Klucz sceny -> opis [SCENE] dla kadru i [MOTION] dla klipu wideo.
SCENES = {
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
    "ksiega": {
        "scene": "Santa sitting in his armchair, opening a huge old leather-bound book "
        "on his lap, golden magical glow coming from the pages.",
        "motion": "Santa slowly opens the book, golden light rises from the pages",
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
# Klucz = nazwa pliku MP3, zgodna z numeracją scen w MVP.md.
GENERAL_LINES = {
    "scena1_dom": {
        "single": "Ho, ho, ho! Witaj w moim domu na dalekiej Północy.",
        "plural": "Ho, ho, ho! Witajcie w moim domu na dalekiej Północy.",
    },
    "scena2_pracownia": {
        "single": "Tu, w mojej pracowni, elfy pracują dzień i noc. Pakują prezenty i pilnują, "
        "żeby wszystko było gotowe na Święta. Ale dziś odkładam pracę na chwilę, bo mam "
        "bardzo ważną wiadomość. Wiadomość tylko dla ciebie.",
        "plural": "Tu, w mojej pracowni, elfy pracują dzień i noc. Pakują prezenty i pilnują, "
        "żeby wszystko było gotowe na Święta. Ale dziś odkładam pracę na chwilę, bo mam "
        "bardzo ważną wiadomość. Wiadomość tylko dla was.",
    },
    "scena4_ksiega": {
        "single": "To moja magiczna księga. Zapisuję w niej wszystkie dzieci, które w tym roku "
        "starały się być dobre. Spójrz, kto jest na tej stronie! Księga nigdy się nie myli.",
        "plural": "To moja magiczna księga. Zapisuję w niej wszystkie dzieci, które w tym roku "
        "starały się być dobre. Spójrzcie, kto jest na tej stronie! Księga nigdy się nie myli.",
    },
    "scena5_lista": {
        "single": "A tu jest moja lista grzecznych dzieci. Twoje imię jest już na niej zapisane. "
        "Przybijam pieczęć… gotowe!",
        "plural": "A tu jest moja lista grzecznych dzieci. Wasze imiona są już na niej zapisane. "
        "Przybijam pieczęć… gotowe!",
    },
    "scena6_pozegnanie": {
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
