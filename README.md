# Film od Mikołaja: generator materiałów

Skrypty, które wykonują kroki z [MVP.md](MVP.md) przez API zamiast ręcznie w przeglądarce. Ten plik opisuje, jak je skonfigurować i uruchomić.

**Spis treści**

1. [Przegląd](#1-przegląd)
2. [Wymagania](#2-wymagania)
3. [Instalacja](#3-instalacja)
4. [Konfiguracja](#4-konfiguracja)
5. [Pierwsze uruchomienie (test)](#5-pierwsze-uruchomienie-test)
6. [Mechanizmy](#6-mechanizmy)
   - [6.1 Obrazy](#61-obrazy-generatorimages)
   - [6.2 Klipy wideo](#62-klipy-wideo-generatorvideos)
   - [6.3 Głos i muzyka](#63-głos-i-muzyka-generatoraudio)
   - [6.4 Tekst i głos dla zamówienia](#64-tekst-i-głos-dla-zamówienia-generatororder)
   - [6.5 Montaż](#65-montaż-generatormontage)
   - [6.6 HeyGen (ręcznie)](#66-heygen-ręcznie)
7. [Przebieg pracy](#7-przebieg-pracy)
8. [Pliki wynikowe](#8-pliki-wynikowe)
9. [Rozwiązywanie problemów](#9-rozwiązywanie-problemów)
10. [Testy](#10-testy)

## 1. Przegląd

| Moduł | Co robi | Usługa | Koszt |
|---|---|---|---|
| `generator.images` | portret Mikołaja, 4 kadry scen, puste szablony księgi i listy | Gemini API: Nano Banana Pro | za obraz |
| `generator.videos` | 4 klipy scen ogólnych (8 s) z kadrów jako pierwszej klatki | Gemini API: Veo 3.1 | za sekundę wideo |
| `generator.audio` | głos Mikołaja, kwestie ogólne, podkład muzyczny | ElevenLabs | znaki / minuty z planu |
| `generator.order` | tekst Mikołaja dla dziecka i jego nagranie | Gemini API + ElevenLabs | grosze za zamówienie |
| `generator.montage` | gotowy film MP4 1080p | ffmpeg + Pillow, lokalnie | 0 zł |

Mówiącego Mikołaja robisz ręcznie w HeyGen (zob. [6.6](#66-heygen-ręcznie)).

```
Przygotowanie (raz):  images ──> videos      audio (głos, kwestie, muzyka)      montage calibrate
                         │                                                          │
Każde zamówienie:     order text ──> [człowiek czyta] ──> order voice ──> HeyGen ──> montage build ──> film
```

Zasada działania wszystkich modułów: skrypt generuje kilka wariantów, **człowiek ogląda je i zatwierdza jeden** poleceniem `select`, a następny krok korzysta tylko z zatwierdzonego. Ponowne uruchomienie nie nadpisuje wariantów, tylko dokłada nowe z kolejnymi numerami.

Wszystkie polecenia uruchamiasz z głównego katalogu repozytorium.

## 2. Wymagania

| Co | Po co | Skąd |
|---|---|---|
| Python 3.10 lub nowszy | wszystkie skrypty | python.org, `brew install python`, Microsoft Store |
| ffmpeg (z ffprobe) | montaż | `brew install ffmpeg` / `sudo apt install ffmpeg` / `winget install ffmpeg` |
| Font odręczny z polskimi znakami (`.ttf`) | imię na liście grzecznych dzieci | np. [Caveat](https://fonts.google.com/specimen/Caveat) z Google Fonts |
| Konto Google AI Studio z płatnościami | obrazy, wideo, tekst | [aistudio.google.com](https://aistudio.google.com) |
| Konto ElevenLabs, plan co najmniej Starter | głos, muzyka | [elevenlabs.io](https://elevenlabs.io) |
| Konto HeyGen, plan Creator | mówiący Mikołaj | [heygen.com](https://www.heygen.com) |

## 3. Instalacja

macOS / Linux:

```bash
git clone https://github.com/ekubal/Miko.git && cd Miko
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows (PowerShell):

```powershell
git clone https://github.com/ekubal/Miko.git; cd Miko
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Font: pobierz plik `.ttf` i zapisz go jako `fonts/handwriting.ttf` (albo wskaż inną ścieżkę, zob. [4.4](#44-układ-montażu-layoutjson)). Font nie jest w repozytorium.

Sprawdzenie instalacji (bez kluczy API, ok. 20 s):

```bash
python -m pytest -q
ffmpeg -version
```

Pamiętaj, żeby w każdym nowym terminalu aktywować środowisko (`source .venv/bin/activate` albo `.venv\Scripts\Activate.ps1`).

## 4. Konfiguracja

### 4.1 Klucze API

**Gemini API** (obrazy, wideo, tekst):

1. Wejdź na [aistudio.google.com/apikey](https://aistudio.google.com/apikey) i utwórz klucz.
2. W projekcie Google Cloud powiązanym z kluczem włącz płatności. Bez tego Veo i Nano Banana Pro zwykle nie są dostępne albo mają bardzo niski limit.
3. Wpisz klucz w `.env` jako `GEMINI_API_KEY`.

Uwaga: wywołania przez API są rozliczane z konta Google Cloud według cennika Gemini API, a **nie** z kredytów subskrypcji Google AI Pro i Flow opisanych w MVP.md. Wideo jest najdroższe: testuj z `-n 1` i w 720p.

**ElevenLabs** (głos, muzyka):

1. Wejdź w *Settings → API Keys* i utwórz klucz.
2. Jeśli ograniczasz uprawnienia klucza, włącz co najmniej: Text to Speech, Voices (odczyt i zapis), Voice Generation, a dla podkładu także Music.
3. Wpisz klucz w `.env` jako `ELEVENLABS_API_KEY`.

Plan darmowy nie daje praw komercyjnych, minimum to Starter. Generowanie muzyki przez API może wymagać wyższego planu. Jeśli go nie masz, użyj muzyki z biblioteki bez tantiem (zob. [6.3](#63-głos-i-muzyka-generatoraudio)).

### 4.2 Plik `.env`

| Zmienna | Wymagana | Domyślnie | Opis |
|---|---|---|---|
| `GEMINI_API_KEY` | tak | — | klucz Gemini API (działa też `GOOGLE_API_KEY`) |
| `ELEVENLABS_API_KEY` | tak | — | klucz ElevenLabs |
| `ELEVENLABS_VOICE_ID` | nie | z `output/voice.json` | gotowy głos Mikołaja, np. zapisany wcześniej w panelu ElevenLabs |
| `MIKOLAJ_IMAGE_MODEL` | nie | `gemini-3-pro-image-preview` | model obrazu (Nano Banana Pro) |
| `MIKOLAJ_VIDEO_MODEL_FAST` | nie | `veo-3.1-fast-generate-preview` | Veo w trybie Fast |
| `MIKOLAJ_VIDEO_MODEL_QUALITY` | nie | `veo-3.1-generate-preview` | Veo w trybie Quality |
| `MIKOLAJ_TEXT_MODEL` | nie | `gemini-2.5-flash` | model piszący tekst Mikołaja |
| `ELEVENLABS_TTS_MODEL` | nie | `eleven_multilingual_v2` | model zamiany tekstu na mowę |
| `ELEVENLABS_VOICE_DESIGN_MODEL` | nie | `eleven_multilingual_ttv_v2` | model projektowania głosu |
| `ELEVENLABS_OUTPUT_FORMAT` | nie | `mp3_44100_128` | format plików audio |
| `ELEVENLABS_API_URL` | nie | `https://api.elevenlabs.io` | adres API (np. serwer w UE, jeśli masz do niego dostęp) |
| `MIKOLAJ_OUTPUT_DIR` | nie | `output` | gdzie zapisywać wyniki |
| `MIKOLAJ_FONT` | nie | `font` z `layout.json` | ścieżka do fontu odręcznego |

Nazwy modeli Google w wersji „preview” zmieniają się co kilka miesięcy. Jeśli skrypt zgłasza, że model nie istnieje, sprawdź aktualną nazwę w dokumentacji Gemini API i wpisz ją w `.env`, bez zmiany kodu.

Plik `.env` jest w `.gitignore`. Nie wysyłaj go do repozytorium.

### 4.3 Prompty i kwestie: `generator/prompts.py`

Wszystkie treści są w jednym pliku. Zmieniasz je tam, nie w kodzie skryptów.

| Stała | Co zawiera |
|---|---|
| `PORTRAIT_PROMPT` | prompt portretu Mikołaja (krok 1 przygotowania) |
| `SCENE_PROMPT`, `SCENES[...]["scene"]` | prompt bazowy kadrów i opisy 4 scen |
| `TEMPLATES` | prompty pustej księgi i listy |
| `MOTION_PROMPT`, `SCENES[...]["motion"]` | prompt ruchu dla Veo |
| `VOICE_DESCRIPTION`, `VOICE_SAMPLE_TEXT` | opis głosu i tekst próbny do Voice Design (100–1000 znaków) |
| `MUSIC_PROMPT` | opis podkładu muzycznego |
| `GENERAL_LINES` | kwestie ogólne scen 1, 2, 4, 5, 6: `single` dla jednego dziecka, `plural` dla rodzeństwa |
| `SPEECH_PROMPT`, `CHILD_DATA`, `SPEECH_CLOSING` | prompt tekstu dla dziecka i wymagane zdanie końcowe |

Po zmianie kwestii w `GENERAL_LINES` nagraj je ponownie: `python -m generator.audio lines --force`.

### 4.4 Układ montażu: `layout.json`

| Pole | Opis |
|---|---|
| `ksiega_ramka` | prostokąt ramki na zdjęcie w szablonie księgi: `[lewo, góra, prawo, dół]` jako ułamki szerokości i wysokości obrazu, np. `0.56` = 56% szerokości |
| `lista_imiona` | prostokąt, w którym wypisywane jest imię na liście (tak samo jak wyżej) |
| `font` | ścieżka do fontu, względna wobec katalogu repozytorium |
| `kolor_imienia` | kolor imienia, np. `#3b2412` (ciemny brąz atramentu) |
| `kolor_poswiaty` | kolor poświaty wokół zdjęcia |

Wartości dopasowujesz raz, po wybraniu szablonów, poleceniem `montage calibrate` (zob. [6.5](#65-montaż-generatormontage)).

### 4.5 Ustawienia dla zaawansowanych

Nie trzeba ich zmieniać, ale warto wiedzieć, gdzie są:

- **Brzmienie głosu:** `VOICE_SETTINGS` w `generator/audio.py`: stabilność, podobieństwo, styl i tempo (`speed`, domyślnie 0,92, czyli trochę wolniej niż normalnie).
- **Montaż:** stałe na górze `generator/montage.py`:
  - `MUSIC_VOLUME`: głośność podkładu (domyślnie 0,35);
  - `AMBIENT_VOLUME`: dźwięk otoczenia z klipów Veo;
  - `SCENE_TIMING`: minimalna długość każdej sceny i moment wejścia głosu;
  - `MAX_SLOWDOWN`: ile razy można zwolnić klip;
  - `BOOK_CLIP_SECONDS`: ile klipu z księgą pokazać przed zbliżeniem na zdjęcie;
  - `VOICE_TAIL`: cisza po kwestii.

## 5. Pierwsze uruchomienie (test)

Zanim wygenerujesz pełen zestaw, sprawdź każdą usługę jednym tanim wywołaniem. Jeśli coś nie działa, zobacz [rozdział 9](#9-rozwiązywanie-problemów).

```bash
# Gemini: obraz
python -m generator.images portrait -n 1 --size 1K
python -m generator.images select portrait 1

# Gemini: obraz z referencją
python -m generator.images scenes -n 1 --only dom --size 1K
python -m generator.images select dom 1

# Veo: jeden klip w 720p
python -m generator.videos generate --only dom --resolution 720p

# ElevenLabs: projekt głosu, zapis, krótkie nagranie
python -m generator.audio design
python -m generator.audio save-voice <generated_voice_id z output/audio/voice_design/previews.json>
python -m generator.audio tts --text "Ho, ho, ho! Wesołych Świąt!" -o output/test.mp3

# Gemini: tekst dla dziecka
python -m generator.order text examples/zamowienie_kasia.json
```

Wyniki testu możesz potem usunąć (`output/`) albo zostawić: kolejne warianty dostaną następne numery.

## 6. Mechanizmy

### 6.1 Obrazy (`generator.images`)

Generuje obrazy w Nano Banana Pro. Odpowiada krokom 1–3 przygotowania z MVP.md.

| Polecenie | Co robi | Wynik |
|---|---|---|
| `portrait` | portret Mikołaja do awatara | `output/images/portrait/portrait_NN.png` |
| `scenes` | 4 kadry z tą samą postacią; jako referencję wysyła zatwierdzony portret | `output/images/scenes/<scena>_NN.png` |
| `templates` | pusta księga z ramką i pusta lista | `output/images/templates/<szablon>_NN.png` |
| `select <nazwa> <N>` | zatwierdza wariant N | `output/selected/<nazwa>.png` |

Opcje `portrait`, `scenes`, `templates`:

| Opcja | Domyślnie | Opis |
|---|---|---|
| `-n`, `--count` | 10 / 3 / 3 | liczba wariantów |
| `--size` | `2K` | `1K` (tańszy test), `2K`, `4K` |
| `--aspect-ratio` | `16:9` | proporcje obrazu |
| `--only` | wszystkie | tylko wybrane sceny (`dom pracownia ksiega sanie`) lub szablony (`szablon_ksiega szablon_lista`) |
| `--reference` | `output/selected/portrait.png` | tylko `scenes`: inny portret referencyjny |

Nazwy dla `select`: `portrait`, `dom`, `pracownia`, `ksiega`, `sanie`, `szablon_ksiega`, `szablon_lista`.

```bash
python -m generator.images portrait -n 10
python -m generator.images select portrait 4
python -m generator.images scenes -n 3
python -m generator.images scenes -n 2 --only ksiega      # dołóż warianty jednej sceny
python -m generator.images select ksiega 5
python -m generator.images templates -n 3
python -m generator.images select szablon_lista 2
```

Na co patrzeć przy wyborze portretu: twarz na wprost, usta zamknięte i niezasłonięte brodą, równe światło. Od tego zależy, jak dobrze HeyGen ożywi Mikołaja.

### 6.2 Klipy wideo (`generator.videos`)

Robi z zatwierdzonych kadrów 8-sekundowe klipy w Veo 3.1. Kadr jest pierwszą klatką, a Veo dodaje ruch i dźwięk otoczenia. Wymaga zatwierdzonych kadrów `dom`, `pracownia`, `ksiega`, `sanie`. Generowanie jednego klipu trwa zwykle 1–3 minuty, skrypt czeka i pokazuje upływający czas.

| Polecenie | Co robi | Wynik |
|---|---|---|
| `generate` | klipy dla scen | `output/videos/<scena>_<fast\|quality>_NN.mp4` |
| `select <scena> <fast\|quality> <N>` | zatwierdza klip | `output/selected/<scena>.mp4` |

| Opcja `generate` | Domyślnie | Opis |
|---|---|---|
| `-n`, `--count` | 1 | wariantów na scenę |
| `--only` | wszystkie | wybrane sceny |
| `--quality` | wyłączone | model Quality zamiast Fast: lepszy, droższy |
| `--resolution` | `1080p` | `720p` na testy |

```bash
python -m generator.videos generate -n 2
python -m generator.videos generate --only ksiega --quality
python -m generator.videos select dom fast 2
python -m generator.videos select ksiega quality 1
```

### 6.3 Głos i muzyka (`generator.audio`)

| Polecenie | Co robi | Wynik |
|---|---|---|
| `design` | Voice Design: kilka podglądów głosu według `VOICE_DESCRIPTION` | `output/audio/voice_design/preview_NN.mp3` i `previews.json` z ich identyfikatorami |
| `save-voice <id>` | zapisuje wybrany podgląd w bibliotece ElevenLabs | `output/voice.json` (`voice_id`) |
| `lines` | nagrywa kwestie ogólne scen 1, 2, 4, 5, 6 | `output/audio/lines/<scena>.mp3` i `<scena>_rodzenstwo.mp3` |
| `tts` | dowolny tekst głosem Mikołaja | wskazany plik |
| `music` | podkład muzyczny (ElevenLabs Music, bez wokalu) | `output/audio/music/podklad_NN.mp3` |
| `select-music <N>` | zatwierdza podkład do montażu | `output/selected/podklad.mp3` |

| Polecenie | Opcja | Domyślnie | Opis |
|---|---|---|---|
| `design` | `--rounds` | 1 | każda runda daje kilka podglądów |
| `design` | `--text` | z `prompts.py` | tekst próbny (100–1000 znaków) |
| `save-voice` | `--name` | `Mikolaj` | nazwa głosu w bibliotece |
| `lines` | `--variant` | `all` | `single`, `plural` albo `all` |
| `lines` | `--only` | wszystkie | wybrane sceny, np. `scena2_pracownia` |
| `lines` | `--force` | wyłączone | nadpisz istniejące nagrania |
| `tts` | `--text` / `--file`, `-o` | — | tekst lub plik z tekstem, plik wynikowy |
| `music` | `--seconds`, `--prompt`, `-n` | 150, z `prompts.py`, 1 | długość, opis, liczba wariantów |

```bash
python -m generator.audio design --rounds 2
# odsłuchaj preview_*.mp3, znajdź id w previews.json
python -m generator.audio save-voice abc123XYZ
python -m generator.audio lines
python -m generator.audio music --seconds 150 -n 2
python -m generator.audio select-music 2
```

- **Gotowy głos:** jeśli masz już głos zapisany w panelu ElevenLabs, pomiń `design` i `save-voice`, a jego id wpisz w `.env` jako `ELEVENLABS_VOICE_ID`.
- **Własna muzyka:** skopiuj plik do `output/selected/podklad.mp3` albo podaj go przy montażu przez `--music`.
- **Używaj zawsze tego samego głosu.** Po zmianie głosu nagraj kwestie ogólne ponownie z `--force`.

### 6.4 Tekst i głos dla zamówienia (`generator.order`)

Wymaga pliku JSON z danymi z formularza. Przykłady są w [`examples/`](examples/): jedno dziecko z kupionym prezentem, jedno z niekupionym i rodzeństwo.

```json
{
  "id": "2026-001-kasia",
  "dzieci": [
    {
      "imie": "Kasia",
      "zwrot": "Kasiu",
      "plec": "dziewczynka",
      "wiek": "5 lat",
      "zdjecie": "zdjecia/kasia.jpg",
      "osiagniecie": "nauczyła się jeździć na rowerze bez bocznych kółek",
      "zainteresowania": "dinozaury, rysowanie",
      "do_poprawy": "",
      "prezent": "zestaw do rysowania z dinozaurami",
      "prezent_kupiony": true
    }
  ],
  "wymowa": {}
}
```

| Pole | Wymagane | Opis |
|---|---|---|
| `id` | tak | identyfikator zamówienia, nazwa katalogu w `output/orders/` |
| `dzieci[].imie` | tak | imię na liście grzecznych dzieci |
| `dzieci[].zwrot` | tak | forma w wołaczu, dokładnie tak, jak Mikołaj ma mówić |
| `dzieci[].plec` | tak | `dziewczynka` / `chłopiec` (formy „nauczyłaś / nauczyłeś”) |
| `dzieci[].wiek` | tak | dopasowanie języka |
| `dzieci[].zdjecie` | do montażu | ścieżka do zdjęcia, względna wobec pliku JSON |
| `dzieci[].osiagniecie`, `zainteresowania` | tak | treść pochwały |
| `dzieci[].do_poprawy`, `prezent` | nie | puste = pominięte |
| `dzieci[].prezent_kupiony` | tak | `true` = elfy szykują prezent; `false` = Mikołaj zapisuje marzenie, bez obietnicy |
| `wymowa` | nie | zapis fonetyczny tylko do nagrania, np. `{"Jessico": "Dzesiko"}` |

Rodzeństwo: dodaj kolejne obiekty do `dzieci`. Tekst ma wtedy 110–130 słów zamiast 90–110.

| Polecenie | Co robi | Wynik |
|---|---|---|
| `text <zamówienie.json>` | pisze tekst i wypisuje automatyczne uwagi: liczba słów, brak zwrotu, brak zdania końcowego, obietnica niekupionego prezentu, „DO SPRAWDZENIA” | `output/orders/<id>/tekst.txt` |
| `voice <zamówienie.json> --approved` | nagrywa zatwierdzony tekst, z podmianami z `wymowa` | `output/orders/<id>/glos.mp3` |

```bash
python -m generator.order text zamowienia/2026-001.json
# przeczytaj i popraw output/orders/2026-001-kasia/tekst.txt
python -m generator.order voice zamowienia/2026-001.json --approved
```

- `text` nie nadpisze istniejącego tekstu bez `--force`.
- `voice` nie ruszy bez `--approved`: w MVP każdy tekst czyta człowiek.
- Jeśli imię brzmi źle, dodaj wpis w `wymowa` dla formy użytej w tekście (zwykle wołacza) i uruchom `voice` ponownie.
- Do modelu tekstowego trafiają tylko pola opisowe. Zdjęcie dziecka nie trafia do żadnego modelu AI.

### 6.5 Montaż (`generator.montage`)

Składa gotowy film lokalnie przez ffmpeg. Wymaga ffmpeg, fontu i wszystkich zatwierdzonych materiałów. Brakujące pliki wypisuje przed startem.

**Kalibracja (raz, po wybraniu szablonów):**

```bash
python -m generator.montage calibrate                # jedno dziecko
python -m generator.montage calibrate --children 2   # rodzeństwo
```

W `output/montage_preview/` powstają szablony z czerwonymi prostokątami, przykładowym zdjęciem i imieniem. Jeśli prostokąt nie pokrywa ramki w księdze albo pustych linii na liście, popraw liczby w `layout.json` i uruchom ponownie. Przykład: ramka zaczyna się w 60% szerokości i 25% wysokości, a kończy w 85% i 75%, więc `"ksiega_ramka": [0.60, 0.25, 0.85, 0.75]`.

**Montaż zamówienia:**

```bash
python -m generator.montage build zamowienia/2026-001.json
# -> output/orders/<id>/film_<id>.mp4
```

| Opcja | Domyślnie | Opis |
|---|---|---|
| `--heygen` | `output/orders/<id>/heygen.mp4` | inny plik z HeyGen |
| `--music` | `output/selected/podklad.mp3` | inny podkład |
| `--no-music` | wyłączone | bez podkładu |
| `--preset` | `medium` | `ultrafast` = szybki podgląd, `slow` = lepsza kompresja |
| `--keep-temp` | wyłączone | zostaw pliki pojedynczych scen w `montage_tmp/` |

Co trafia do filmu:

| Scena | Obraz | Dźwięk | Min. długość |
|---|---|---|---|
| 1. Dom | `selected/dom.mp4` | `scena1_dom.mp3` | 15 s |
| 2. Pracownia | `selected/pracownia.mp4` | `scena2_pracownia.mp3` | 20 s |
| 3. Mikołaj mówi | `orders/<id>/heygen.mp4` | dźwięk z HeyGen | długość klipu |
| 4. Księga | `selected/ksiega.mp4`, potem zbliżenie na zdjęcie w ramce | `scena4_ksiega.mp3` | 20 s |
| 5. Lista | `selected/szablon_lista.png` z imieniem pojawiającym się w trakcie kwestii | `scena5_lista.mp3` | 15 s |
| 6. Pożegnanie | `selected/sanie.mp4` | `scena6_pozegnanie.mp3` | 20 s |

- **Długość scen:** gdy kwestia jest dłuższa niż minimum, scena się wydłuża. Klip jest wtedy zwalniany (najwyżej 1,8 raza), a dalej zatrzymuje się na ostatniej klatce.
- **Muzyka** gra pod całym filmem i sama się ścisza, gdy Mikołaj mówi.
- **Rodzeństwo:** montaż bierze kwestie `_rodzenstwo`, wkleja zdjęcia obok siebie i wypisuje imiona jedno pod drugim.
- **Czas montażu:** od kilkudziesięciu sekund do kilku minut na film, zależnie od komputera i presetu.

### 6.6 HeyGen (ręcznie)

Raz na początku:

1. *Avatars → Create → Photo Avatar*, wgraj `output/selected/portrait.png`.

Przy każdym zamówieniu:

1. Nowy film, wybierz awatara Mikołaja.
2. Źródło dźwięku: *Upload audio*, wgraj `output/orders/<id>/glos.mp3`.
3. Model Avatar IV, format 16:9, eksport 1080p.
4. Jeśli jest pole opisu ruchu, wpisz: `gentle nodding, warm smile, calm small hand gestures, looking into the camera`.
5. Pobrany plik zapisz jako `output/orders/<id>/heygen.mp4`.

## 7. Przebieg pracy

### Przygotowanie jednorazowe

```bash
python -m generator.images portrait -n 10              # 1. portret
python -m generator.images select portrait N
python -m generator.images scenes -n 3                 # 2. kadry
python -m generator.images select dom N                #    (i pracownia, ksiega, sanie)
python -m generator.images templates -n 3              # 3. szablony
python -m generator.images select szablon_ksiega N
python -m generator.images select szablon_lista N
python -m generator.videos generate -n 2               # 4. klipy
python -m generator.videos select dom fast N           #    (i pracownia, ksiega, sanie)
python -m generator.audio design --rounds 2            # 5. głos
python -m generator.audio save-voice <id>
python -m generator.audio lines                        #    kwestie ogólne
python -m generator.audio music -n 2                   #    podkład
python -m generator.audio select-music N
python -m generator.montage calibrate                  # 6. kalibracja montażu
```

Na koniec utwórz Photo Avatar w HeyGen ([6.6](#66-heygen-ręcznie)).

### Każde zamówienie

1. Sprawdź płatność, zgody i zdjęcie. Zapisz dane z formularza jako JSON, a zdjęcie obok niego.
2. `python -m generator.order text <zamówienie.json>`, potem przeczytaj i popraw `tekst.txt`.
3. `python -m generator.order voice <zamówienie.json> --approved` i odsłuchaj imię.
4. HeyGen: klip z `glos.mp3`, zapisany jako `heygen.mp4`.
5. `python -m generator.montage build <zamówienie.json>`.
6. Kontrola jakości według listy z MVP.md:
   - imię brzmi poprawnie i jest w dobrej formie (wołacz);
   - usta zgadzają się z głosem, twarz Mikołaja bez zniekształceń;
   - zdjęcie i imię należą do właściwego dziecka;
   - brak obietnicy prezentu, jeśli rodzic zaznaczył, że nie jest kupiony.
7. Dostawa: Google Drive i mail. Po 7 dniach usuń zdjęcia i katalog zamówienia.

## 8. Pliki wynikowe

```
output/
  images/portrait/portrait_NN.png
  images/scenes/<scena>_NN.png
  images/templates/<szablon>_NN.png
  videos/<scena>_<fast|quality>_NN.mp4
  audio/voice_design/preview_NN.mp3, previews.json
  audio/lines/<scena>.mp3, <scena>_rodzenstwo.mp3
  audio/music/podklad_NN.mp3
  selected/                  <- zatwierdzone warianty, z nich korzysta montaż
    portrait.png, dom.png, pracownia.png, ksiega.png, sanie.png
    szablon_ksiega.png, szablon_lista.png
    dom.mp4, pracownia.mp4, ksiega.mp4, sanie.mp4, podklad.mp3
  voice.json                 <- voice_id głosu Mikołaja
  montage_preview/           <- podgląd kalibracji
  orders/<id>/
    tekst.txt, glos.mp3, heygen.mp4, film_<id>.mp4
```

Katalog `output/` jest w `.gitignore`. Zawiera dane dzieci, więc nie wysyłaj go do repozytorium i nie udostępniaj.

## 9. Rozwiązywanie problemów

| Objaw | Przyczyna i rozwiązanie |
|---|---|
| `Brak klucza API: ustaw ...` | brak klucza w `.env` (plik musi leżeć w głównym katalogu repozytorium) |
| `ModuleNotFoundError: generator` | uruchom polecenie z głównego katalogu repozytorium |
| `ModuleNotFoundError: google` / `requests` / `PIL` | nieaktywne środowisko: `source .venv/bin/activate`, potem `pip install -r requirements.txt` |
| Błąd 404 / `model not found` | zmieniła się nazwa modelu: wpisz aktualną w `.env` (`MIKOLAJ_*_MODEL`) |
| Błąd 429 / `quota` / `billing` | brak płatności w projekcie Google albo przekroczony limit; skrypty ponawiają wywołanie 3 razy, potem odczekaj |
| `Model nie zwrócił obrazu` / `Veo nie zwróciło klipu` | blokada filtrów bezpieczeństwa; uruchom ponownie albo złagodź opis w `prompts.py` |
| ElevenLabs HTTP 401 | zły klucz albo brak uprawnień klucza (zob. [4.1](#41-klucze-api)) |
| ElevenLabs HTTP 402 / 403 przy `music` lub `design` | funkcja niedostępna w Twoim planie; zmień plan albo użyj własnej muzyki / gotowego głosu |
| ElevenLabs: tekst za krótki przy `design` | tekst próbny musi mieć 100–1000 znaków |
| Głos z obcym akcentem | wygeneruj więcej podglądów (`--rounds 3`) albo dopisz w `VOICE_DESCRIPTION` „Polish accent” |
| Imię źle wymawiane | wpis w `wymowa` w JSON zamówienia, potem `order voice` ponownie |
| `Brak ffmpeg` | zainstaluj ffmpeg (zob. [2](#2-wymagania)) i otwórz nowy terminal |
| `Brakuje plików: ...` przy montażu | brak zatwierdzonego materiału: wykonaj podany `select` albo brakujący krok |
| Kwadraciki zamiast ą, ę, ł | font bez polskich znaków; wybierz font z zestawem „Latin Extended” |
| Zdjęcie lub imię nie w tym miejscu | `montage calibrate` i poprawka `layout.json` |
| Muzyka za głośna lub za cicha | `MUSIC_VOLUME` w `generator/montage.py` |
| `Klip z HeyGen nie ma dźwięku` | w HeyGen eksportuj film z dźwiękiem (MP4) |

## 10. Testy

```bash
python -m pytest -q
```

Testy działają bez kluczy API i bez sieci. Test montażu składa cały film ze sztucznych materiałów w małej rozdzielczości (ok. 20 s). Gdy w systemie nie ma ffmpeg, jest pomijany.
