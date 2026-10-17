# Film od Mikołaja: generator materiałów

Skrypty, które wykonują kroki z [MVP.md](MVP.md) przez API zamiast ręcznie w przeglądarce:

| Moduł | Co generuje | Usługa |
|---|---|---|
| `generator.images` | portret Mikołaja, 4 kadry scen, szablony księgi i listy | Gemini API: Nano Banana Pro |
| `generator.videos` | 4 klipy scen ogólnych (8 s, 1080p) z kadrów jako pierwszej klatki | Gemini API: Veo 3.1 (Fast / Quality) |
| `generator.audio` | głos Mikołaja (Voice Design), kwestie ogólne (pojedyncze i dla rodzeństwa), podkład muzyczny | ElevenLabs |
| `generator.order` | tekst Mikołaja dla dziecka (scena 3) i jego nagranie MP3 | Gemini API + ElevenLabs |

Mówiącego Mikołaja nadal robisz w HeyGen (Photo Avatar + Avatar IV), a montaż w CapCut lub DaVinci Resolve. Skrypty przygotowują wszystko, czego te narzędzia potrzebują.

Prompty i kwestie mówione są w jednym pliku, [`generator/prompts.py`](generator/prompts.py). Zmieniasz je tam, nie w kodzie skryptów.

## Instalacja

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # uzupełnij GEMINI_API_KEY i ELEVENLABS_API_KEY
```

**Koszty API:** wywołania przez Gemini API rozlicza się osobno, według cennika Google AI Studio lub Vertex AI, a nie z kredytów subskrypcji Google AI Pro i Flow z MVP.md. Klip z Veo przez API kosztuje wyraźnie więcej niż obraz, więc najpierw testuj w trybie Fast z `-n 1`. ElevenLabs liczy znaki z Twojego planu (licencja komercyjna od planu Starter). Muzyka przez API może wymagać wyższego planu.

Wszystkie pliki trafiają do `output/` (katalog jest w `.gitignore`). Kolejne uruchomienie nie nadpisuje istniejących wariantów, tylko dokłada nowe z kolejnymi numerami.

## Przygotowanie jednorazowe

Robisz to w tej kolejności, bo każdy krok korzysta z wariantu wybranego przez człowieka w poprzednim.

```bash
# 1. Portret do awatara: wygeneruj 8–12 wersji, obejrzyj, zatwierdź jedną
python -m generator.images portrait -n 10
python -m generator.images select portrait 4         # -> output/selected/portrait.png

# 2. Kadry scen z tą samą postacią (portret jako obraz referencyjny)
python -m generator.images scenes -n 3
python -m generator.images select dom 2
python -m generator.images select pracownia 1
python -m generator.images select ksiega 3
python -m generator.images select sanie 1

# 3. Puste szablony do personalizacji (napisy dodajesz w edytorze)
python -m generator.images templates -n 3
python -m generator.images select szablon_ksiega 2
python -m generator.images select szablon_lista 1

# 4. Klipy wideo z zatwierdzonych kadrów
python -m generator.videos -n 2                      # tryb Fast
python -m generator.videos --only ksiega --quality   # najlepszą scenę powtórz w Quality

# 5. Głos Mikołaja: odsłuchaj podglądy i zapisz najlepszy
python -m generator.audio design --rounds 2          # output/audio/voice_design/preview_*.mp3
python -m generator.audio save-voice <generated_voice_id>   # id z previews.json
python -m generator.audio lines                      # sceny 1, 2, 4, 5, 6 (+ wersje _rodzenstwo)
python -m generator.audio music --seconds 150 -n 2   # podkład; albo biblioteka bez tantiem
```

Na koniec w HeyGen utwórz Photo Avatar z `output/selected/portrait.png`.

Struktura wyników:

```
output/
  images/portrait/portrait_01.png ...
  images/scenes/dom_01.png, pracownia_01.png, ksiega_01.png, sanie_01.png ...
  images/templates/szablon_ksiega_01.png, szablon_lista_01.png ...
  selected/portrait.png, dom.png, ..., szablon_lista.png   <- zatwierdzone warianty
  videos/dom_fast_01.mp4, ksiega_quality_01.mp4 ...
  audio/voice_design/preview_01.mp3 ..., previews.json
  audio/lines/scena1_dom.mp3, scena1_dom_rodzenstwo.mp3 ...
  audio/music/podklad_01.mp3
  voice.json                                               <- voice_id głosu Mikołaja
  orders/<id>/tekst.txt, glos.mp3
```

## Produkcja jednego zamówienia

Dane z formularza zapisz jako JSON. Przykłady są w [`examples/`](examples/): jedno dziecko z kupionym prezentem, jedno z niekupionym i rodzeństwo.

```bash
# Krok 2: tekst Mikołaja + automatyczne uwagi (liczba słów, zwrot, zdanie końcowe, obietnica prezentu)
python -m generator.order text examples/zamowienie_kasia.json

# Przeczytaj i popraw output/orders/<id>/tekst.txt. W MVP każdy tekst zatwierdza człowiek.

# Krok 3: nagranie zatwierdzonego tekstu
python -m generator.order voice examples/zamowienie_kasia.json --approved
```

Jeśli imię jest źle wymawiane, dodaj w JSON zapis fonetyczny formy użytej w tekście (zwykle wołacza), np. `"wymowa": {"Jessico": "Dzesiko"}`. Podmiana dotyczy tylko nagrania, `tekst.txt` się nie zmienia.

Plik `glos.mp3` wgrywasz w HeyGen jako źródło dźwięku (Avatar IV, 16:9, 1080p), a dalej postępujesz według kroków 5–7 z MVP.md.

Do modelu tekstowego trafiają tylko pola z formularza: zwrot, płeć, wiek, osiągnięcie, zainteresowania, prezent. Skrypty nie wysyłają zdjęcia dziecka do żadnego modelu AI.

### Format zamówienia

```json
{
  "id": "2026-001-kasia",
  "dzieci": [
    {
      "imie": "Kasia",
      "zwrot": "Kasiu",
      "plec": "dziewczynka",
      "wiek": "5 lat",
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

Dla rodzeństwa dodaj kolejne obiekty do `dzieci`. Tekst ma wtedy 110–130 słów (ok. 50–55 s).

## Konfiguracja

Modele i katalog wyjściowy możesz zmienić w `.env` (zob. `.env.example`), np. gdy Google opublikuje nową wersję modelu:

| Zmienna | Domyślnie |
|---|---|
| `MIKOLAJ_IMAGE_MODEL` | `gemini-3-pro-image-preview` (Nano Banana Pro) |
| `MIKOLAJ_VIDEO_MODEL_FAST` | `veo-3.1-fast-generate-preview` |
| `MIKOLAJ_VIDEO_MODEL_QUALITY` | `veo-3.1-generate-preview` |
| `MIKOLAJ_TEXT_MODEL` | `gemini-2.5-flash` |
| `ELEVENLABS_TTS_MODEL` | `eleven_multilingual_v2` |
| `ELEVENLABS_VOICE_ID` | z `output/voice.json` |
| `MIKOLAJ_OUTPUT_DIR` | `output` |

## Testy

```bash
python -m pytest -q
```

Testy działają bez kluczy API i bez sieci.
