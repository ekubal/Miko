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
| `generator.images` | portrety Mikołaja i Płatka, kadry scen, puste szablony do montażu | Gemini API: Nano Banana Pro | za obraz |
| `generator.videos` | 8 klipów scen ogólnych (8 s) z kadrów jako pierwszej klatki | Gemini API: Gemini Omni Flash | za sekundę wideo |
| `generator.audio` | głos Mikołaja, kwestie ogólne, podkład muzyczny | ElevenLabs | znaki / minuty z planu |
| `generator.order` | nagranie tekstu Mikołaja (tekst pisze Rails: `Orders::GenerateSpeech`; `order text` zamrożone) | ElevenLabs | grosze za zamówienie |
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
2. W projekcie Google Cloud powiązanym z kluczem włącz płatności. Bez tego modele wideo i Nano Banana Pro zwykle nie są dostępne albo mają bardzo niski limit.
3. Wpisz klucz w `.env` jako `GEMINI_API_KEY`.

Uwaga: wywołania przez API są rozliczane z konta Google Cloud według cennika Gemini API, a **nie** z kredytów subskrypcji Google AI Pro i Flow opisanych w MVP.md. Wideo jest najdroższe: testuj z `-n 1` i w 360p.

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
| `MIKOLAJ_VIDEO_MODEL` | nie | `gemini-omni-1.1-flash` | model wideo (Gemini Omni Flash) |
| `MIKOLAJ_TEXT_MODEL` | nie | `gemini-3.8-flash` | model piszący tekst Mikołaja |
| `MIKOLAJ_IMAGE_PRICE_INPUT` | nie | `2.0` | cena wejścia modelu obrazu (prompt, referencje), USD za 1 mln tokenów; tylko do podglądu kosztu |
| `MIKOLAJ_IMAGE_PRICE_OUTPUT_IMAGE` | nie | `120.0` | cena obrazu wynikowego, USD za 1 mln tokenów |
| `MIKOLAJ_IMAGE_PRICE_OUTPUT_TEXT` | nie | `12.0` | cena tekstu i myślenia w odpowiedzi, USD za 1 mln tokenów |
| `ELEVENLABS_TTS_MODEL` | nie | `eleven_multilingual_v2` | model zamiany tekstu na mowę |
| `ELEVENLABS_VOICE_DESIGN_MODEL` | nie | `eleven_multilingual_ttv_v2` | model projektowania głosu |
| `ELEVENLABS_OUTPUT_FORMAT` | nie | `mp3_44100_128` | format plików audio |
| `ELEVENLABS_API_URL` | nie | `https://api.elevenlabs.io` | adres API (np. serwer w UE, jeśli masz do niego dostęp) |
| `MIKOLAJ_OUTPUT_DIR` | nie | `output` | gdzie zapisywać wyniki |
| `MIKOLAJ_FONT` | nie | `font` z `layout.json` | ścieżka do fontu odręcznego |
| `FAL_KEY` | nie | — | klucz fal.ai, tylko do testów innych modeli wideo ([6.7](#68-testy-innych-modeli-wideo-testy_fal)) |

Nazwy modeli Google w wersji „preview” zmieniają się co kilka miesięcy. Jeśli skrypt zgłasza, że model nie istnieje, sprawdź aktualną nazwę w dokumentacji Gemini API i wpisz ją w `.env`, bez zmiany kodu.

Plik `.env` jest w `.gitignore`. Nie wysyłaj go do repozytorium.

### 4.3 Prompty i kwestie: `generator/prompts.py`

Wszystkie treści są w jednym pliku. Zmieniasz je tam, nie w kodzie skryptów.

| Stała | Co zawiera |
|---|---|
| `PORTRAIT_PROMPT` | prompt portretu Mikołaja (krok 1 przygotowania) |
| `SCENE_PROMPT`, `SCENES[...]["scene"]` | prompt bazowy kadrów i opisy 8 scen |
| `TEMPLATES` | prompty pustej księgi i listy |
| `MOTION_PROMPT`, `SCENES[...]["motion"]` | prompt ruchu dla modelu wideo |
| `VOICE_DESCRIPTION`, `VOICE_SAMPLE_TEXT` | opis głosu i tekst próbny do Voice Design (100–1000 znaków) |
| `MUSIC_PROMPT` | opis podkładu muzycznego |
| `GENERAL_LINES` | kwestie ogólne scen 1, 2, 4, 5, 6: `single` dla jednego dziecka, `plural` dla rodzeństwa |
| `SPEECH_PROMPT`, `CHILD_DATA`, `SPEECH_CLOSING` | zamrożona kopia; źródłem jest `app/app/services/orders/speech_prompt.rb` |

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
  - `AMBIENT_VOLUME`: dźwięk otoczenia z klipów wideo;
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

# Gemini Omni Flash: jeden klip w 360p
python -m generator.videos generate --only dom --resolution 360p

# ElevenLabs: projekt głosu, zapis, krótkie nagranie
python -m generator.audio design
python -m generator.audio save-voice <generated_voice_id z output/audio/voice_design/previews.json>
python -m generator.audio tts --text "Ho, ho, ho! Wesołych Świąt!" -o output/test.mp3

# Gemini: tekst dla dziecka (zamrożone; produkcyjnie tekst pisze Rails, zob. 6.4)
python -m generator.order text examples/zamowienie_kasia.json
```

Wyniki testu możesz potem usunąć (`output/`) albo zostawić: kolejne warianty dostaną następne numery.

## 6. Mechanizmy

### 6.1 Obrazy (`generator.images`)

Generuje obrazy w Nano Banana Pro. Odpowiada krokom 1–3 przygotowania z MVP.md.

| Polecenie | Co robi | Wynik |
|---|---|---|
| `portrait` | portret Mikołaja do awatara | `output/images/portrait/portrait_NN.png` |
| `platek` | portret wzorcowy Płatka, najmłodszego renifera (scenariusz 4) | `output/images/portrait/platek_NN.png` |
| `scenes` | kadry scen z tymi samymi postaciami; jako referencje wysyła zatwierdzone portrety, które podaje scena (domyślnie Mikołaj, w scenach z Płatkiem także `platek`) | `output/images/scenes/<scena>_NN.png` |
| `templates` | puste szablony do personalizacji w montażu (księga, lista, kula, ramki, bilecik) | `output/images/templates/<szablon>_NN.png` |
| `select <nazwa> <N>` | zatwierdza wariant N | `output/selected/<nazwa>.png` |

Po każdym obrazie polecenie wypisuje jego koszt, a na końcu sumę, np. `Razem: 3 obraz(ów), ok. 0.405 USD`. Koszt liczy z tokenów zwróconych przez model i cennika z `.env` (`MIKOLAJ_IMAGE_PRICE_*`, domyślnie cennik Nano Banana Pro z XI 2026: ok. 0,134 USD za obraz 1K/2K, 0,24 USD za 4K). To podgląd; rozliczenie jest w Google Cloud Billing.

Opcje `portrait`, `platek`, `scenes`, `templates`:

| Opcja | Domyślnie | Opis |
|---|---|---|
| `-n`, `--count` | 10 / 6 / 3 / 3 | liczba wariantów |
| `--size` | `2K` | `1K` (tańszy test), `2K`, `4K` |
| `--aspect-ratio` | `16:9` | proporcje obrazu |
| `--only` | wszystkie | tylko wybrane sceny lub szablony (lista niżej) |
| `--dry-run` | wyłączone | pokazuje plan i szacowany koszt, nic nie wysyła i nie wymaga zatwierdzonych portretów |
| `--wariant` | `klasyczny` | tylko `portrait`: `pelna-broda` daje bardzo długą brodę, wąsy zakrywające usta, okulary, klasyczny strój i kadr do kolan |
| `--reference` | `output/selected/portrait.png` | tylko `scenes`: inny portret referencyjny |

Nazwy dla `select`: `portrait`, `platek` i wszystkie sceny oraz szablony:

| Grupa | Nazwy |
|---|---|
| sceny wersji krótkiej | `zorza dom pracownia renifery listy ksiega mapa sanie` |
| sceny scenariusza 4 (z Mikołajem) | `kula sortownia pakowanie wpadka bliscy` |
| sceny scenariusza 4 (z Płatkiem) | `stajnia_skok` i `worek` (sam Płatek), `stajnia`, `zaprzeg` i `start` (Mikołaj i Płatek) |
| scena bez postaci | `koperta` (scena 4, gdy rodzic nie przesłał zdjęcia listu) |
| szablony | `szablon_ksiega szablon_lista szablon_kula szablon_kula_domek szablon_poczta szablon_bilecik szablon_bliscy` |

Sceny z Płatkiem wymagają zatwierdzonego `output/selected/platek.png` (`platek`, potem `select platek N`). Bez niego `scenes` kończy się podpowiedzią, zanim cokolwiek wygeneruje.

```bash
python -m generator.images portrait -n 10
python -m generator.images select portrait 4
python -m generator.images platek -n 6
python -m generator.images select platek 2
python -m generator.images scenes -n 3 --dry-run   # najpierw szacunek kosztu
python -m generator.images scenes -n 3
python -m generator.images scenes -n 2 --only ksiega      # dołóż warianty jednej sceny
python -m generator.images select ksiega 5
python -m generator.images templates -n 3
python -m generator.images select szablon_lista 2
```

Na co patrzeć przy wyborze portretu: twarz na wprost, usta zamknięte i niezasłonięte brodą, równe światło. Od tego zależy, jak dobrze HeyGen ożywi Mikołaja.

### 6.2 Klipy wideo (`generator.videos`)

Robi z zatwierdzonych kadrów klipy w Gemini Omni Flash (`gemini-omni-1.1-flash`), następcy Veo 3.1, które Google wyłączyło w Gemini API 22 października 2026. Kadr jest pierwszą klatką, a model dodaje ruch i dźwięk otoczenia, w jednym ujęciu, bez cięć. Wymaga zatwierdzonych kadrów scen. Generowanie jednego klipu trwa zwykle kilka minut, a skrypt czeka na wynik.

| Polecenie | Co robi | Wynik |
|---|---|---|
| `generate` | klipy dla scen | `output/videos/<scena>_NN.mp4` |
| `select <scena> <N>` | zatwierdza klip | `output/selected/<scena>.mp4` |

| Opcja `generate` | Domyślnie | Opis |
|---|---|---|
| `-n`, `--count` | 1 | wariantów na scenę |
| `--only` | wszystkie | wybrane sceny |
| `--resolution` | `1080p` | `360p` (tani test), `720p`, `1080p`, `4k` |
| `--duration` | 8 | długość klipu w sekundach, 3–10 |

```bash
python -m generator.videos generate --only zorza --resolution 360p   # tani test ruchu
python -m generator.videos generate --only zorza                     # wersja docelowa 1080p
python -m generator.videos select zorza 2
```

### 6.3 Głos i muzyka (`generator.audio`)

| Polecenie | Co robi | Wynik |
|---|---|---|
| `design` | Voice Design: kilka podglądów głosu według `VOICE_DESCRIPTION` | `output/audio/voice_design/preview_NN.mp3` i `previews.json` z ich identyfikatorami |
| `save-voice <id>` | zapisuje wybrany podgląd w bibliotece ElevenLabs | `output/voice.json` (`voice_id`) |
| `lines` | nagrywa kwestie wspólne: wersji krótkiej i długiej (klucze `d_*`, scenariusz 4) | `output/audio/lines/<scena>.mp3` i `<scena>_rodzenstwo.mp3` |
| `tts` | dowolny tekst głosem Mikołaja | wskazany plik |
| `probki` | ta sama kwestia w kilku zestawach ustawień głosu (i głosach) do odsłuchania | `output/audio/probki/<głos>_<zestaw>_NN.mp3` |
| `przemiana <plik>` | nagranie człowieka zamienione na głos Mikołaja (speech-to-speech) | wskazany plik |
| `music` | podkład muzyczny (ElevenLabs Music, bez wokalu) | `output/audio/music/podklad_NN.mp3` |
| `select-music <N>` | zatwierdza podkład do montażu | `output/selected/podklad.mp3` |

| Polecenie | Opcja | Domyślnie | Opis |
|---|---|---|---|
| `design` | `--rounds` | 1 | każda runda daje kilka podglądów |
| `design` | `--text` | z `prompts.py` | tekst próbny (100–1000 znaków) |
| `save-voice` | `--name` | `Mikolaj` | nazwa głosu w bibliotece |
| `lines` | `--variant` | `all` | `single`, `plural` albo `all` |
| `lines` | `--only` | wszystkie | wybrane sceny, np. `pracownia` |
| `lines` | `--dluga` | wyłączone | tylko kwestie wersji długiej (`d_*`, kolejność w `prompts.LONG_LINES`) |
| `lines` | `--force` | wyłączone | nadpisz istniejące nagrania |
| `tts` | `--text` / `--file`, `-o` | — | tekst lub plik z tekstem, plik wynikowy |
| `lines`, `tts` | `--preset` | `ELEVENLABS_PRESET` albo `obecny` | zestaw ustawień głosu (`PRESETS` w `generator/audio.py`) |
| `probki` | `--presety`, `--glos`, `-n`, `--text` | wszystkie zestawy, zapisany głos, 1, kwestia próbna | co porównać |
| `przemiana` | `-o`, `--bez-szumu` | — | plik wynikowy, usunięcie szumu tła z nagrania |
| `music` | `--seconds`, `--prompt`, `-n` | 150, z `prompts.py`, 1 | długość, opis, liczba wariantów |

```bash
python -m generator.audio design --rounds 2
# odsłuchaj preview_*.mp3, znajdź id w previews.json
python -m generator.audio save-voice abc123XYZ
python -m generator.audio lines
python -m generator.audio lines --dluga      # tylko wersja długa
python -m generator.audio music --seconds 150 -n 2
python -m generator.audio select-music 2
```

- **Gotowy głos:** jeśli masz już głos zapisany w panelu ElevenLabs, pomiń `design` i `save-voice`, a jego id wpisz w `.env` jako `ELEVENLABS_VOICE_ID`.
- **Własna muzyka:** skopiuj plik do `output/selected/podklad.mp3` albo podaj go przy montażu przez `--music`.
- **Używaj zawsze tego samego głosu.** Po zmianie głosu nagraj kwestie ogólne ponownie z `--force`.

#### Gdy głos brzmi sztucznie (obcy akcent, płaska intonacja)

Sprawdzaj w tej kolejności:

1. **Ustawienia i model.** `python -m generator.audio probki` nagrywa tę samą kwestię próbną w pięciu zestawach: `obecny` (dotychczasowe ustawienia), `naturalny`, `v3`, `v3_ekspresja` i `flash_pl`. Odsłuchaj pliki z `output/audio/probki/` i wpisz najlepszy zestaw w `.env`: `ELEVENLABS_PRESET=v3`. Zestaw z modelem niedostępnym w Twoim planie zgłasza błąd i jest pomijany. Każde nagranie wychodzi trochę inaczej, więc `-n 2` daje po dwie wersje. Wysoka stabilność i zwolnione tempo (`speed` poniżej 1) spłaszczają intonację, dlatego nowe zestawy mają tempo 1.0.
2. **Głos.** Głos z Voice Design powstał z opisu po angielsku i może mówić po polsku z obcym akcentem. W bibliotece głosów ElevenLabs (Voice Library) ustaw filtry: język polski, mężczyzna, starszy wiek, narracja albo postacie. Kilka głosów dodaj do „My Voices” i porównaj: `probki --glos ID1 ID2 ID3 --presety naturalny v3`. Zwycięski wpisz w `.env` jako `ELEVENLABS_VOICE_ID`. Najlepszą jakość daje profesjonalny klon głosu polskiego lektora (Professional Voice Clone), za jego pisemną zgodą i z licencją na użycie.
3. **Nagranie człowieka głosem Mikołaja.** `python -m generator.audio przemiana nagranie.m4a -o kwestia.mp3`: intonację, tempo i polski akcent model bierze z nagrania, a barwę z głosu Mikołaja. Najlepsze do reklam i kwestii wspólnych, które nagrywa się raz. Nagrywaj w cichym pomieszczeniu, z telefonem ok. 20 cm od ust; `--bez-szumu` usuwa szum tła.
4. **Po zmianie** głosu albo zestawu nagraj kwestie ponownie z `--force`. Ten sam głos i zestaw ustaw w aplikacji Rails (`Orders::RecordPersonalLines`), inaczej kwestie z imieniem dziecka będą brzmiały inaczej niż reszta filmu.

Model Eleven v3 rozumie wskazówki w nawiasach kwadratowych, np. `[whispers]` albo `[laughs]`. Dopisujemy je do kwestii dopiero po wyborze v3, bo inne modele przeczytałyby je na głos.

### 6.4 Tekst i głos dla zamówienia (`generator.order`)

> **Tekst pisze teraz Rails.** W konsoli `app/` (`bin/rails console`):
> `r = Orders::GenerateSpeech.call(Order.find_by!(number: "2026-001"))`, potem `puts r[:text]` i `r[:issues].each { |i| puts "! #{i.message}" }`.
> Model: `MIKOLAJ_TEXT_PROVIDER` (`gemini` albo `anthropic`) i `MIKOLAJ_TEXT_MODEL`; klucz z płatnego planu (`GEMINI_API_KEY` / `ANTHROPIC_API_KEY` albo credentials). Polecenie `order text` poniżej jest zamrożone (awaryjnie, do czasu zapisu tekstu w Rails, karta 6.3 w PLAN_WDROZENIA.md) i nie dostaje zmian promptu.

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
| `bliscy` | tak | jak dziecko mówi do bliskich, z którymi ogląda film (`{BLISCY}` w scenie 9), np. `mama i tata`, albo zwrot wpisany przez rodzica |
| `bliscy_wybor` | tak | opcja z formularza: `mama i tata`, `mama`, `tata`, `babcia i dziadek` albo `inne` (zwrot w `bliscy` sprawdza człowiek) |
| `wiadomosc_od_bliskich` | nie | do 200 znaków, czyta ją Mikołaj w scenie 9; pusty tekst = bez wiadomości |
| `zdjecie_bliskich`, `zdjecie_listu`, `zdjecie_domu` | nie | ramka na biurku (scena 9), list lub rysunek na poczcie (scena 4), dom w śnieżnej kuli (scena 11); `null` = wariant bez zdjęcia. Tylko do montażu, nigdy do narzędzi AI |
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
| 1. Zorza polarna | `selected/zorza.mp4` | `zorza.mp3` | 12 s |
| 2. Dom | `selected/dom.mp4` | `dom.mp3` | 12 s |
| 3. Pracownia | `selected/pracownia.mp4` | `pracownia.mp3` | 15 s |
| 4. Renifery | `selected/renifery.mp4` | `renifery.mp3` | 15 s |
| 5. Listy od dzieci | `selected/listy.mp4` | `listy.mp3` | 15 s |
| 6. Mikołaj mówi | `orders/<id>/heygen.mp4` | dźwięk z HeyGen | długość klipu |
| 7. Księga | `selected/ksiega.mp4`, potem zbliżenie na zdjęcie w ramce | `ksiega.mp3` | 20 s |
| 8. Lista | `selected/szablon_lista.png` z imieniem pojawiającym się w trakcie kwestii | `lista.mp3` | 15 s |
| 9. Mapa | `selected/mapa.mp4` | `mapa.mp3` | 15 s |
| 10. Pożegnanie | `selected/sanie.mp4` | `sanie.mp3` | 20 s |

Kwestie leżą w `output/audio/lines/`. Kolejność i długości scen są w liście `TIMELINE` na górze `generator/montage.py`. Żeby skrócić film, usuń z niej scenę: wtedy nie trzeba generować jej klipu ani kwestii.

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

### 6.7 Długie scenariusze (`generator.scenariusze`)

Prompty długich scenariuszy mieszkają w `generator/scenariusze/`, jeden moduł na scenariusz. Pierwszy to „Od listu do sań” (`od_listu_do_san.py`, scenariusz w `scenariusze/4_od_listu_do_san.md`): 22 ujęcia w 11 scenach, portret renifera Płatka i 4 szablony do montażu. Ujęcia oznaczone „z wersji krótkiej” biorą gotowe kadry i klipy z `output/selected/`. Wszystkie prompty w czytelnej postaci: `scenariusze/4_od_listu_do_san_prompty.md`.

```bash
python -m generator.scenariusze lista                      # ujęcia i ich stan
python -m generator.scenariusze postacie -n 4              # 1. portret Płatka
python -m generator.scenariusze wybierz platek 2
python -m generator.scenariusze kadry -n 3                 # 2. kadry wszystkich nowych ujęć
python -m generator.scenariusze wybierz kula 1             #    i wybór każdego z nich
python -m generator.scenariusze wideo --resolution 360p    # 3. tani test ruchu
python -m generator.scenariusze wideo -n 2                 #    wersja 1080p
python -m generator.scenariusze wybierz-wideo kula 2
python -m generator.scenariusze szablony -n 2              # kula, ramka, list, bilecik
python -m generator.scenariusze opis                       # odśwież plik z promptami po zmianach
```

Wyniki: `output/od_listu_do_san/{postacie,kadry,szablony,wideo}/`, zatwierdzone w `output/od_listu_do_san/wybrane/`. Ujęcie `kula_heygen` to tylko kadr: obraz wejściowy dla mówiącego Mikołaja w HeyGen.

**Film reklamowy zapisów** (`reklama_zapisy_poziomo.py`, scenariusz w `scenariusze/reklama_zapisy.md`) to trzy warianty w poziomie (16:9), w których Mikołaj mówi do rodziców o starcie zamówień i kodzie −25%. Działa tak samo, z przełącznikiem `-s reklama_zapisy_poziomo`. Polecenie `kwestie` nagrywa jego kwestie głosem Mikołaja do `output/reklama_zapisy_poziomo/glos/`:

```bash
python -m generator.scenariusze -s reklama_zapisy_poziomo kadry --only w2_za_blisko w2_elf w2_mowi w2_wylacz ksiega lista -n 3
python -m generator.scenariusze -s reklama_zapisy_poziomo kwestie --only w2_1 w2_2 w2_3 w2_4 w2_5
```

### 6.8 Testy innych modeli wideo (`testy_fal`)

Robocze skrypty w katalogu `testy_fal/` porównują Gemini Omni Flash z modelami na fal.ai: MiniMax H3, Kling, Seedance i Wan. Wszystkie modele dostają te same kadry i prompty, a wyniki trafiają do siatki porównawczej z kosztem i czasem generowania. Produkcja (`generator/`) z nich nie korzysta. Szczegóły: [testy_fal/README.md](testy_fal/README.md).

```bash
python -m testy_fal sprawdz                 # schematy modeli na fal, bez kosztów
python -m testy_fal generuj --na-sucho      # plan i szacowany koszt
python -m testy_fal generuj                 # klipy w output/testy_fal/wideo/
python -m testy_fal porownaj                # siatki w output/testy_fal/porownania/
```

### 6.9 Strona sprzedażowa (`strona/`)

Kod HTML strony głównej, formularza zamówienia i potwierdzenia, przeniesiony z projektu graficznego. Strony są statyczne (HTML, CSS, JavaScript bez bibliotek). Bez podłączonego serwera formularz działa w trybie pokazowym. Pola formularza mają te same nazwy co pliki zamówień generatora. Wdrożenie, pola do uzupełnienia i format danych dla serwera: [strona/README.md](strona/README.md).

```bash
cd strona && python3 -m http.server 8000   # podgląd: http://localhost:8000
```

Regulamin i polityka prywatności są w `dokumenty/*.md` (projekty do sprawdzenia przez prawnika). Polecenie `python dokumenty/zbuduj.py` robi z nich strony `strona/regulamin.html` i `strona/polityka-prywatnosci.html`, pliki `.docx` dla prawnika i PDF-y w `strona/pliki/` (wymaga pandoc i LibreOffice).

## 7. Przebieg pracy

### Przygotowanie jednorazowe

```bash
python -m generator.images portrait -n 10              # 1. portret
python -m generator.images select portrait N
python -m generator.images scenes -n 3                 # 2. kadry
python -m generator.images select dom N                #    (i zorza, pracownia, renifery, listy, ksiega, mapa, sanie)
python -m generator.images templates -n 3              # 3. szablony
python -m generator.images select szablon_ksiega N
python -m generator.images select szablon_lista N
python -m generator.videos generate -n 2               # 4. klipy
python -m generator.videos select dom N                #    (i pozostałe sceny)
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
2. Tekst: `Orders::GenerateSpeech.call(order)` w konsoli Rails ([6.4](#64-tekst-i-głos-dla-zamówienia-generatororder)); przeczytaj, popraw i zapisz jako `output/orders/<id z JSON-a>/tekst.txt`.
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
  videos/<scena>_NN.mp4
  audio/voice_design/preview_NN.mp3, previews.json
  audio/lines/<scena>.mp3, <scena>_rodzenstwo.mp3
  audio/music/podklad_NN.mp3
  selected/                  <- zatwierdzone warianty, z nich korzysta montaż
    portrait.png, dom.png, pracownia.png, ksiega.png, sanie.png
    szablon_ksiega.png, szablon_lista.png
    zorza.mp4, dom.mp4, pracownia.mp4, renifery.mp4, listy.mp4, ksiega.mp4, mapa.mp4, sanie.mp4, podklad.mp3
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
| `Model nie zwrócił obrazu` / `Model nie zwrócił klipu` | blokada filtrów bezpieczeństwa; uruchom ponownie albo złagodź opis w `prompts.py` |
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
