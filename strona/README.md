# Strona sprzedażowa

Kod HTML trzech stron z projektu na kanwie:

| Plik | Strona |
|---|---|
| `index.html` | strona główna |
| `zamowienie.html` | formularz zamówienia: dziecko, co powie Mikołaj, dane i zgody |
| `potwierdzenie.html` | potwierdzenie po płatności |
| `faq.html` | pytania rodziców z wyszukiwarką (`js/faq.js`) |
| `regulamin.html` | układ regulaminu: spis treści, skrót, 10 paragrafów; treść od prawnika |
| `404.html` | błędny adres i wygasły link do filmu |
| `kontakt.html` | formularz kontaktowy (`js/kontakt.js`), adres e-mail z kopiowaniem, godziny, dane firmy |
| `js/cookies.js` | baner zgody na cookies i okno ustawień, dołączony do wszystkich stron |

Strony są statyczne: czysty HTML, jeden arkusz `css/style.css` i trochę JavaScriptu bez bibliotek (`js/`). Działają na każdym hostingu plików, np. Netlify, Cloudflare Pages albo zwykłym serwerze.

## Podgląd lokalny

```bash
cd strona
python3 -m http.server 8000
```

Potem otwórz http://localhost:8000. Formularz działa w **trybie pokazowym**: nic nie wysyła, tylko przechodzi do potwierdzenia z wpisanymi danymi.

## Do uzupełnienia przed startem

| Co | Gdzie |
|---|---|
| `[OSTATNI TERMIN ZAMÓWIEŃ]` | `index.html`: pasek u góry i karta z ceną |
| `[ADRES E-MAIL]` | `index.html` (stopka), `potwierdzenie.html` |
| `[ADRES NADAWCY]` | `potwierdzenie.html`: adres, z którego przychodzą maile |
| `[OPERATOR PŁATNOŚCI]` | `zamowienie.html`, podsumowanie |
| `[DŁUGOŚĆ]` i film przykładowy | `index.html`; pliki `media/przyklad.mp4` i `media/przyklad.jpg` (kadr) |
| `polityka-prywatnosci.html` | strona do dodania (treść od prawnika); linkują do niej stopka i zgody |
| Treść regulaminu | `regulamin.html`: miejsca `[Treść paragrafu od prawnika]`, dane sprzedawcy, daty wersji, plik `pliki/regulamin.pdf`; po wstawieniu usuń ramkę „Projekt układu” |
| Odpowiedzi do potwierdzenia | `faq.html`: `[DŁUGOŚĆ FILMU]`, faktura, czas odpowiedzi na maile, link ważny 60 dni |
| Treść zgód | `zamowienie.html`: do sprawdzenia przez prawnika |
| Kadr listy z imieniem | `index.html`, sekcja „Mikołaj zna szczegóły”: zamień makietę na kadr z filmu |

Ceny (49 zł i 15 zł za rodzeństwo) są w tekstach stron i w atrybutach formularza `data-cena-bazowa` i `data-cena-rodzenstwo`. Zmieniaj je w obu miejscach. Cenę, którą płaci klient, i tak musi wyliczyć serwer.

**404:** ustaw w hostingu `404.html` jako stronę błędu (np. Netlify i Cloudflare Pages robią to same, w nginx `error_page 404 /404.html;`). Strona używa ścieżek od korzenia (`/css/style.css`), więc działa pod każdym błędnym adresem, ale wymaga, żeby strona leżała w katalogu głównym domeny.

## Baner cookies

`js/cookies.js` pokazuje baner przy pierwszej wizycie i zapisuje wybór w przeglądarce (`localStorage`). Odrzucenie jest tak samo widoczne jak akceptacja, a kategorie opcjonalne są domyślnie wyłączone. Przycisk „Ustawienia cookies” w stopce otwiera okno ustawień ponownie.

Narzędzia analityczne i reklamowe wstawiaj tak, żeby ładowały się dopiero po zgodzie:

```html
<script type="text/plain" data-zgoda="reklamowe" data-src="https://adres-skryptu.js"></script>
<script type="text/plain" data-zgoda="analityczne">/* kod narzędzia */</script>
```

Nazwy narzędzi uzupełnij w tablicy `CATEGORIES` w `js/cookies.js`. Po zmianie kategorii albo narzędzi podnieś `VERSION`: każdy zobaczy baner ponownie. Treść banera trzeba sprawdzić z prawnikiem.

## Formularz kontaktowy

`kontakt.html` ma atrybut `data-endpoint`. Pusty oznacza tryb pokazowy: po wysłaniu pokazuje się podziękowanie, ale wiadomość nigdzie nie trafia. Podaj adres, który przyjmuje `POST` z JSON-em `{imie, email, temat, numer, wiadomosc, zgoda}` i odpowiada kodem 2xx (własny serwer albo usługa formularzy, np. Formspree). Godziny odpowiedzi i czas odpowiedzi na stronie to propozycja do potwierdzenia.

## Formularz i serwer

Formularz ma atrybut `data-endpoint`. Gdy jest pusty, działa tryb pokazowy. Gdy podasz adres API, skrypt wysyła na niego `POST multipart/form-data`:

- pole `zamowienie`: JSON zamówienia;
- pliki `zdjecie_0`, `zdjecie_1`, …: zdjęcia dzieci w kolejności z JSON-a.

Przykładowy JSON zamówienia:

```json
{
  "dzieci": [
    {
      "imie": "Kasia", "zwrot": "Kasiu", "plec": "dziewczynka", "wiek": "5 lat",
      "zdjecie": "zdjecie_0",
      "osiagniecie": "nauczyła się jeździć na rowerze bez bocznych kółek",
      "zainteresowania": "dinozaury, rysowanie", "do_poprawy": "",
      "prezent": "zestaw do rysowania z dinozaurami", "prezent_kupiony": true
    }
  ],
  "email": "anna@example.com",
  "termin": "2026-12-20",
  "zgody": { "regulamin": true, "dane_dziecka": true, "ai": true, "realizacja": true },
  "kwota_zl": 49
}
```

Część `dzieci` ma ten sam format co pliki zamówień generatora (`examples/zamowienie_kasia.json`). Serwer zapisuje zdjęcia, wpisuje ich ścieżki w `zdjecie` i dopisuje `id` zamówienia. Wtedy plik od razu nadaje się do `python -m generator.order text …`.

**Odpowiedź serwera:**
- sukces: JSON `{"platnosc_url": "https://…"}`, a strona przekierowuje rodzica do płatności;
- błąd: kod 4xx/5xx i opcjonalnie `{"blad": "opis"}`. Formularz pokaże wtedy komunikat i pozwoli spróbować ponownie.

**Serwer musi sam sprawdzić dane.** Walidacja w przeglądarce tylko pomaga rodzicowi i da się ją obejść. Po stronie serwera sprawdź:
- wymagane pola, długości i typy plików;
- cenę;
- zgody.

## Potwierdzenie

Operator płatności przekierowuje rodzica na `potwierdzenie.html`. Numer zamówienia, imiona, e-mail i kwotę strona bierze z jednego z trzech źródeł:

1. **Serwer wpisuje je w HTML:** elementy z atrybutem `data-wartosc`.
2. **Strona pobiera je sama:** ustaw `<body data-podsumowanie="/api/zamowienia/{id}">`, a operator płatności niech wraca na `potwierdzenie.html?zamowienie=<id>`. Skrypt pobierze wtedy JSON `{"nr", "imiona", "email", "kwota"}`. Nie przekazuj e-maila w adresie strony.
3. **Tryb pokazowy:** dane zapisane przez formularz w tej karcie przeglądarki.

Bez żadnego z nich strona pokazuje ogólne teksty, bez danych zamówienia.

## Różnice względem projektu

- **Krok 2 formularza:** nagłówek to „Co Mikołaj ma powiedzieć?”, a imię dziecka jest nad nim. W projekcie było „Co Mikołaj ma powiedzieć dla Kasia?”, co nie odmienia imienia.
- **Pole „Dziecko to”:** zapisuje „chłopiec” z polską literą, tak jak pliki zamówień generatora.
- **Pole zdjęcia:**
  - pokazuje miniaturę wybranego zdjęcia;
  - przyjmuje przeciągnięty plik;
  - odrzuca pliki inne niż JPG/PNG i większe niż 20 MB (`data-maks-mb`).
- **Walidacja:** komunikaty błędów są pod polami, a fokus przechodzi na pierwsze błędne pole. Strona pyta przed zamknięciem, jeśli formularz jest częściowo wypełniony.
- **Film przykładowy:** odtwarza się po kliknięciu, gdy w `media/` jest plik.

## Fonty i prywatność

Strony wczytują fonty Fraunces, Nunito Sans i Caveat z Google Fonts. Przy tym przeglądarka wysyła do Google adres IP odwiedzającego. Bezpieczniej dla RODO jest hostować fonty u siebie:
1. pobierz pliki `woff2`, np. narzędziem google-webfonts-helper;
2. dodaj reguły `@font-face` na początku `css/style.css`;
3. usuń linki do `fonts.googleapis.com` z trzech stron.

## Treść do aktualizacji

Teksty pochodzą z projektu, który powstał dla filmu z 6 scenami (2–3 minuty). Obecny film z generatora ma 10 scen i trwa ok. 3 minut. Przed startem uzgodnij opis scen w sekcji „Co jest w filmie” i długość filmu (strona główna, karta z ceną, podsumowanie zamówienia) z wersją, którą sprzedajesz.

## Testy

`python -m pytest -q tests/test_strona.py` sprawdza:
- czy nie zostały pozostałości z kanwy;
- czy lokalne linki prowadzą do istniejących plików;
- czy identyfikatory się nie powtarzają;
- czy pola formularza zgadzają się z formatem zamówienia generatora.
