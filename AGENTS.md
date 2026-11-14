# AGENTS.md

Instrukcje dla agentów kodujących (Cursor, Claude Code i inne) pracujących w tym repozytorium.

## Projekt

„Wiadomość od Mikołaja”: spersonalizowane filmy od Mikołaja dla dzieci, sprzedawane w Polsce (konkurencja np. elfi.pl). Rodzic wypełnia formularz (imię, zwrot, wiek, zdjęcie, osiągnięcie, zainteresowania, prezent), a system składa film: wspólne sceny wygenerowane raz i część personalizowaną (tekst, głos, mówiący Mikołaj, zdjęcie w księdze, imię na liście).

Opis produktu: `MVP.md`. Plan automatyzacji i panelu: `AUTOMATYZACJA.md`. Reklamy: `MARKETING.md`. Pełna instrukcja skryptów: `README.md`.

Język projektu to **polski**: kod komentujemy, piszemy komunikaty CLI, dokumentację i commity po polsku. Prompty do modeli AI piszemy po angielsku (zob. `generator/prompts.py`).

## Struktura

| Ścieżka | Zawartość |
|---|---|
| `generator/` | pakiet Pythona: `images` (Nano Banana Pro), `videos` (Gemini Omni Flash), `audio` + `elevenlabs` (głos, muzyka), `order` (tekst i głos dla zamówienia), `montage` (ffmpeg), `prompts` (wszystkie prompty i kwestie), `config`, `common` |
| `generator/scenariusze/` | prompty długich scenariuszy (moduł na scenariusz, np. `od_listu_do_san.py`: ujęcia, postacie, szablony) i polecenie `python -m generator.scenariusze`; czytelna kopia promptów w `scenariusze/*_prompty.md` |
| `testy_fal/` | robocze skrypty porównujące modele wideo na fal.ai; nie są częścią produkcji |
| `strona/` | statyczna strona sprzedażowa: `index.html`, `zamowienie.html`, `potwierdzenie.html`, `css/style.css`, `js/` (bez bibliotek) |
| `szablony/` | maile HTML (tabele, style inline), opis pól, przykładowa transkrypcja filmu |
| `scenariusze/`, `SCENARIUSZ_8MIN.md` | scenariusze długiej wersji filmu (md, docx, pdf); odrzucone w `scenariusze/odrzucone/` |
| `examples/` | przykładowe pliki zamówień JSON (format danych dziecka) |
| `tests/` | pytest; działają bez sieci i bez kluczy |
| `output/` | wyniki generowania; w `.gitignore`, zawiera dane dzieci, nigdy nie commitować |

## Polecenia

```bash
pip install -r requirements.txt
python -m pytest -q                       # wszystkie testy (montaż wymaga ffmpeg)
python -m generator.images portrait -n 4  # przykłady; reszta w README.md
python -m generator.videos generate --only zorza --resolution 360p
python -m testy_fal generuj --na-sucho    # plan i koszt testu modeli bez wysyłania
cd strona && python3 -m http.server 8000  # podgląd strony
```

Polecenia uruchamiamy z katalogu głównego repozytorium (`python -m ...`). Przed commitem uruchom `python -m pytest -q`.

## Konwencje kodu

- Python 3.10+, bez nowych zależności, jeśli da się bez nich (obecne: `google-genai`, `requests`, `pillow`, `fal-client`, `pytest`).
- Konfiguracja i klucze tylko przez `generator/config.py` (`.env`, `require_env`). Modele są nazwami w `config` z nadpisaniem przez zmienne `MIKOLAJ_*_MODEL`.
- Wywołania API owijamy w `common.with_retry`. Błędy, których nie da się ponowić (brak płatności, zły klucz, wyłączony model), kończą program z podpowiedzią (`permanent_error_hint`).
- Każdy generator tworzy warianty `nazwa_NN.ext` (`common.variant_paths`, nigdy nie nadpisuje), a człowiek zatwierdza jeden poleceniem `select` do `output/selected/`. Kolejne kroki czytają tylko zatwierdzone pliki.
- Prompty i kwestie Mikołaja trzymamy w `generator/prompts.py` (wersja krótka i wspólne zasady) oraz w `generator/scenariusze/<scenariusz>.py` (długie scenariusze), nie w kodzie innych modułów. Po zmianie promptów scenariusza uruchom `python -m generator.scenariusze opis`, żeby odświeżyć `scenariusze/*_prompty.md` (pilnuje tego test).
- Postacie powtarzające się w wielu ujęciach (np. renifer Płatek) mają portret wzorcowy, który idzie do kadrów jako dodatkowy obraz referencyjny, i stały opis doklejany do promptu.
- Montaż opisuje lista `TIMELINE` w `generator/montage.py`; nowe sceny dodajemy tam i w `prompts.SCENES`.
- Pola formularza na stronie mają te same nazwy co dane dziecka w `examples/*.json` (`imie`, `zwrot`, `plec`, `wiek`, `zdjecie`, `osiagniecie`, `zainteresowania`, `do_poprawy`, `prezent`, `prezent_kupiony`). Pilnuje tego `tests/test_strona.py`.
- Strona: czysty HTML/CSS/JS, kolory jako zmienne CSS w `:root` (`--accent`, `--red`, …), dostępność (etykiety, fokus, `aria-*`), działa na szerokości telefonu bez przewijania w poziomie.
- Maile HTML: układ na tabelach, style inline, szerokość 600 px, bez SVG i skryptów.

## Zasady produktu (obowiązkowe)

1. **Mikołaj jest prawdziwy.** Strona, maile i film mogą zobaczyć dzieci: nigdzie nie piszemy, że Mikołaj jest postacią fikcyjną ani kim „naprawdę” jest.
2. **Informacja o AI zostaje:** na stronie, w regulaminie i w mailu potwierdzającym („film powstaje z pomocą narzędzi sztucznej inteligencji”).
3. **Zdjęcia dzieci nigdy nie trafiają do narzędzi AI.** Są tylko wklejane w montażu i usuwane 7 dni po dostawie.
4. **Prezent tylko, gdy kupiony.** Konkretny prezent pada w filmie wyłącznie przy `prezent_kupiony: true`; inaczej Mikołaj mówi o zapisanym marzeniu, bez obietnicy.
5. **Kwestie wspólne bez form płciowych.** Formy zależne od płci są tylko w tekście pisanym dla konkretnego dziecka. Dla rodzeństwa kwestie są w liczbie mnogiej.
6. **W generowanych kadrach nie ma dzieci.** Elfy są dorosłe (inaczej modele wideo odrzucają kadry). Bez napisów w obrazach: napisy dodaje montaż.
7. **Wygląd Mikołaja:** ok. 80 lat, okulary, długa broda, gęste wąsy zakrywające usta (bez zakręconych końcówek). Zmiany w `PORTRAIT_PROMPT_FULL_BEARD` i `SCENE_PROMPT` testuj na nowych wariantach, nie zmieniaj tej zasady.
8. Każdy tekst Mikołaja dla dziecka czyta człowiek przed nagraniem (`NEEDS_REVIEW`, kolejka przeglądu).

## Bezpieczeństwo i dane

- Nie commituj `.env`, `output/`, fontów z `fonts/` ani zdjęć dzieci.
- Nie wpisuj kluczy API do kodu, dokumentacji ani testów; przykładowe zmienne trzymamy w `.env.example` bez wartości.
- Testy nie mogą wymagać sieci ani kluczy: zewnętrzne API podmieniamy (zob. `tests/test_testy_fal.py`).
- W danych przykładowych używaj tylko imion, nigdy nazwisk ani adresów.

## Styl tekstów po polsku

Piszemy prosto i konkretnie, w drugiej osobie do rodzica („Twoje dziecko”, „Zamów film”). Bez anglicyzmów, gdy jest polskie słowo. Przyciski mówią, co się stanie („Zapłać 64 zł”, „Dodaj rodzeństwo”). Komunikaty błędów mówią, co poprawić.
