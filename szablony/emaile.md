# Szablony e-maili

Trzy wiadomości z MVP.md: potwierdzenie zamówienia, prośba o brakujące dane i dostawa filmu, oraz trzy wiadomości dla listy zapisów przed startem sprzedaży (kod −25%). Każdy szablon ma pola w nawiasach klamrowych, a pod nim przykład wypełniony dla jednego z zamówień z `examples/`.

## Pliki

| Mail | Szablon HTML | Podgląd |
|---|---|---|
| 1. Potwierdzenie zamówienia | [`email_1_potwierdzenie.html`](email_1_potwierdzenie.html) | [komputer](podglad/email_1_potwierdzenie.png) · [telefon](podglad/email_1_potwierdzenie_telefon.png) |
| 2. Prośba o brakujące dane | [`email_2_brakujace_dane.html`](email_2_brakujace_dane.html) | [komputer](podglad/email_2_brakujace_dane.png) · [telefon](podglad/email_2_brakujace_dane_telefon.png) |
| 3. Dostawa filmu | [`email_3_dostawa.html`](email_3_dostawa.html) | [komputer](podglad/email_3_dostawa.png) · [telefon](podglad/email_3_dostawa_telefon.png) |
| Zapisy 1. Potwierdzenie zapisu | [`email_zapis_1_potwierdzenie.html`](email_zapis_1_potwierdzenie.html) | [komputer](podglad/email_zapis_1_potwierdzenie.png) · [telefon](podglad/email_zapis_1_potwierdzenie_telefon.png) |
| Zapisy 2. Start sprzedaży i kod | [`email_zapis_2_start.html`](email_zapis_2_start.html) | [komputer](podglad/email_zapis_2_start.png) · [telefon](podglad/email_zapis_2_start_telefon.png) |
| Zapisy 3. Ostatni dzień rabatu | [`email_zapis_3_ostatni_dzien.html`](email_zapis_3_ostatni_dzien.html) | [komputer](podglad/email_zapis_3_ostatni_dzien.png) · [telefon](podglad/email_zapis_3_ostatni_dzien_telefon.png) |

Szablony HTML są przygotowane pod programy pocztowe: układ na tabelach, style wpisane w elementy, szerokość 600 px, bez SVG i bez skryptów. Na telefonie zwężają się do szerokości ekranu. Wklejasz je do narzędzia do wysyłki (np. jako własny szablon HTML) albo wysyłasz z Gmaila przez rozszerzenie obsługujące HTML. Podglądy pokazują maile wypełnione danymi z przykładów poniżej.

Przed pierwszą wysyłką wyślij każdy szablon do siebie i obejrzyj w Gmailu, Outlooku i na telefonie. Outlook na Windows nie obsługuje zaokrągleń, więc przyciski i ramki będą tam kanciaste, ale czytelne.

## Pola do podmiany

| Pole | Przykład | Uwagi |
|---|---|---|
| `{IMIE_DLA}` | Kasi, Jasia, Zosi i Antka | imię w dopełniaczu („film dla kogo?”); formularz go nie zbiera, wpisz ręcznie |
| `{IMIE_WIEK}` | Kasia, 5 lat | imię i wiek z formularza |
| `{ZWROT}` | Kasiu | forma, której użyje Mikołaj |
| `{NR_ZAMOWIENIA}` | 2026-001 | |
| `{KWOTA}` | 49 zł | |
| `{BRAKUJACE_DANE}` | opis, czego brakuje | zob. gotowe akapity niżej |
| `{LINK_DO_FILMU}` | link z Google Drive | |
| `{DATA_WYGASNIECIA}` | 31 stycznia 2027 | do kiedy działa link |
| `{LINK_DO_ANKIETY}` | link do ankiety | |
| `{PODPIS}` | Zespół Wiadomości od Mikołaja | |
| `{TEMAT}` | Potrzebujemy jeszcze jednego zdjęcia Jasia | tylko mail 2, tytuł strony HTML |
| `{MINIATURA_FILMU}` | link do obrazka 920×518 px | tylko mail 3; kadr z filmu, np. z Google Drive (link publiczny) |
| `{INFO_O_DANYCH}` | Zdjęcie i dane dziecka usuniemy… | tylko mail 3, w liczbie pojedynczej lub mnogiej (zob. przykład) |
| `{LINK_REGULAMIN}`, `{LINK_PRYWATNOSC}` | adresy stron | stopka |
| `{EMAIL_KONTAKT}` | kontakt@… | stopka |
| `{LINK_POTWIERDZENIA}` | link z narzędzia do maili | tylko zapisy 1; podwójne potwierdzenie adresu |
| `{DATA_STARTU}` | 1 grudnia | zapisy 1 |
| `{DATA_KONCA_RABATU}` | 7 grudnia | zapisy 1–3 |
| `{KOD}` | ZAPIS-7KQ2 | zapisy 2–3; osobny kod dla każdego adresu |
| `{LINK_ZAMOWIENIA}` | `https://[ADRES STRONY]/zamowienie.html?kod={KOD}` | zapisy 2–3; formularz wpisze kod sam |
| `{OSTATNI_TERMIN}` | 20 grudnia | zapisy 2; ostatni dzień zamówień przed Wigilią |
| `{LINK_WYPISANIA}` | link z narzędzia do maili | zapisy 2–3 |
| `{ADRES_STRONY}` | adres strony | zapisy 1–2, stopka |
| `{DANE_FIRMY}` | nazwa firmy i adres | stopka maili z listy zapisów (to wiadomości handlowe: nadawca musi być wskazany) |

Dla rodzeństwa pisz w liczbie mnogiej, np. „czeka na Was”, „Zdjęcia i dane dzieci”.

---

## 1. Potwierdzenie zamówienia

Wysyłasz zaraz po zaksięgowaniu płatności.

**Temat:** Mamy Twoje zamówienie – film dla {IMIE_DLA}
**Podgląd:** Elfy już pracują. Link do filmu wyślemy w ciągu 24 godzin.

```text
Dziękujemy! Mamy Twoje zamówienie

Dzień dobry,

płatność dotarła, a elfy już zabierają się do pracy nad filmem dla {IMIE_DLA}.
Link do gotowego filmu wyślemy na ten adres w ciągu 24 godzin.

Podsumowanie zamówienia
- Numer zamówienia: {NR_ZAMOWIENIA}
- Film dla: {IMIE_WIEK}
- Mikołaj powie: „{ZWROT}”
- Zapłacono: {KWOTA}

Coś się nie zgadza?
Jeśli chcesz poprawić imię, formę zwracania się albo inne dane, po prostu
odpowiedz na tego maila, najlepiej w ciągu kilku godzin. Poprawimy wszystko
przed nagraniem.

Ciepło pozdrawiamy,
{PODPIS}

Zdjęcie i dane dziecka usuniemy 7 dni po wysłaniu filmu. Film powstaje
z pomocą narzędzi sztucznej inteligencji.
```

### Przykład: Kasia, 5 lat

**Temat:** Mamy Twoje zamówienie – film dla Kasi

```text
Dziękujemy! Mamy Twoje zamówienie

Dzień dobry,

płatność dotarła, a elfy już zabierają się do pracy nad filmem dla Kasi.
Link do gotowego filmu wyślemy na ten adres w ciągu 24 godzin.

Podsumowanie zamówienia
- Numer zamówienia: 2026-001
- Film dla: Kasia, 5 lat
- Mikołaj powie: „Kasiu”
- Zapłacono: 49 zł

Coś się nie zgadza?
Jeśli chcesz poprawić imię, formę zwracania się albo inne dane, po prostu
odpowiedz na tego maila, najlepiej w ciągu kilku godzin. Poprawimy wszystko
przed nagraniem.

Ciepło pozdrawiamy,
Zespół Wiadomości od Mikołaja
```

---

## 2. Prośba o brakujące dane

Wysyłasz od razu, gdy w kroku 1 produkcji („Sprawdź zamówienie”) czegoś brakuje. Nie czekaj, aż film będzie częściowo gotowy.

**Temat:** Potrzebujemy jeszcze jednego zdjęcia {IMIE_DLA}
(albo, przy innych brakach: Jedno pytanie o film dla {IMIE_DLA})
**Podgląd:** Wystarczy odpowiedzieć na tego maila – film zrobimy od razu.

```text
Jeszcze jedna drobna rzecz

Dzień dobry,

zaczęliśmy przygotowywać film dla {IMIE_DLA} (zamówienie {NR_ZAMOWIENIA})
i potrzebujemy od Ciebie jednej rzeczy, żeby wszystko wyszło pięknie.

Co trzeba uzupełnić
{BRAKUJACE_DANE}

Jak to zrobić?
Wystarczy odpowiedzieć na tego maila. Film wyślemy w ciągu 24 godzin
od Twojej odpowiedzi.

Dziękujemy i pozdrawiamy,
{PODPIS}
```

Gotowe akapity do `{BRAKUJACE_DANE}`:

- **Nieostre zdjęcie:** Przesłane zdjęcie jest nieostre i twarz {IMIE_DLA} jest słabo widoczna. W magicznej księdze nie wyglądałoby dobrze. Najlepiej sprawdzi się ostre zdjęcie w świetle dziennym, z twarzą widoczną na wprost, w formacie JPG lub PNG.
- **Brak zdjęcia:** Nie dotarło do nas zdjęcie {IMIE_DLA}. Dołącz je do odpowiedzi, najlepiej ostre, z twarzą widoczną na wprost, w formacie JPG lub PNG.
- **Niepewna forma imienia:** Chcemy się upewnić, jak Mikołaj ma zwracać się do dziecka. W formularzu jest „{ZWROT}”. Czy tak mówicie w domu?
- **Za mało szczegółów:** Mikołaj chętnie pochwali konkretne osiągnięcie z tego roku. Napisz w jednym, dwóch zdaniach, co się udało, np. „nauczyła się jeździć na rowerze bez bocznych kółek”.
- **Treść do wyjaśnienia** (odpowiedź „DO SPRAWDZENIA” z kroku 2 produkcji): Niektóre informacje w formularzu chcemy z Tobą omówić, zanim Mikołaj je powie. Czy możesz napisać, jak chcesz, żeby Mikołaj o tym wspomniał, albo czy wolisz to pominąć?

### Przykład: Jaś, 8 lat (nieostre zdjęcie)

**Temat:** Potrzebujemy jeszcze jednego zdjęcia Jasia

```text
Jeszcze jedna drobna rzecz

Dzień dobry,

zaczęliśmy przygotowywać film dla Jasia (zamówienie 2026-002) i potrzebujemy
od Ciebie jednej rzeczy, żeby wszystko wyszło pięknie.

Co trzeba uzupełnić
Przesłane zdjęcie jest nieostre i twarz Jasia jest słabo widoczna.
W magicznej księdze nie wyglądałoby dobrze. Najlepiej sprawdzi się ostre
zdjęcie w świetle dziennym, z twarzą widoczną na wprost, w formacie JPG lub PNG.

Jak to zrobić?
Wystarczy odpowiedzieć na tego maila i dołączyć nowe zdjęcie. Film wyślemy
w ciągu 24 godzin od Twojej odpowiedzi.

Dziękujemy i pozdrawiamy,
Zespół Wiadomości od Mikołaja
```

---

## 3. Dostawa filmu

Wysyłasz po kontroli jakości (krok 6 produkcji). Ten mail może zobaczyć dziecko, więc nie ma w nim mowy o AI ani o tym, jak powstaje film.

**Temat:** Film od Mikołaja dla {IMIE_DLA} jest gotowy!
**Podgląd:** Mikołaj nagrał wiadomość. Obejrzyjcie ją razem.

```text
Film dla {IMIE_DLA} jest gotowy!
Mikołaj odłożył na chwilę pracę, żeby nagrać tę wiadomość.

Dzień dobry,

film od Mikołaja dla {IMIE_DLA} czeka na Was. Najwięcej radości daje wspólne
oglądanie, najlepiej na dużym ekranie.

[Obejrzyj i pobierz film] {LINK_DO_FILMU}
Link działa do {DATA_WYGASNIECIA}. Pobierz film, żeby mieć go na zawsze.

Jak się podobało?
Trzy krótkie pytania, minuta Twojego czasu. Każda odpowiedź pomaga nam robić
lepsze filmy.
[Odpowiedz na 3 pytania] {LINK_DO_ANKIETY}

Jeśli film sprawił Wam radość, podziel się nim z rodziną albo poleć nas
znajomym rodzicom. Dla nas to najlepszy prezent.

Wesołych Świąt!
{PODPIS}

Zdjęcie i dane dziecka usuniemy 7 dni po wysłaniu tej wiadomości.
Pobrany film zostaje u Ciebie.
```

### Przykład: rodzeństwo Zosia (3 lata) i Antek (6 lat)

**Temat:** Film od Mikołaja dla Zosi i Antka jest gotowy!

```text
Film dla Zosi i Antka jest gotowy!
Mikołaj odłożył na chwilę pracę, żeby nagrać tę wiadomość.

Dzień dobry,

film od Mikołaja dla Zosi i Antka czeka na Was. Najwięcej radości daje wspólne
oglądanie, najlepiej na dużym ekranie.

[Obejrzyj i pobierz film] https://drive.google.com/...
Link działa do 31 stycznia 2027. Pobierz film, żeby mieć go na zawsze.

Jak się podobało?
Trzy krótkie pytania, minuta Twojego czasu. Każda odpowiedź pomaga nam robić
lepsze filmy.
[Odpowiedz na 3 pytania] https://...

Jeśli film sprawił Wam radość, podziel się nim z rodziną albo poleć nas
znajomym rodzicom. Dla nas to najlepszy prezent.

Wesołych Świąt!
Zespół Wiadomości od Mikołaja

Zdjęcia i dane dzieci usuniemy 7 dni po wysłaniu tej wiadomości.
Pobrany film zostaje u Ciebie.
```

---

## Lista zapisów przed startem (kod −25%)

Trzy wiadomości dla osób zapisanych na stronie `strona/zapisy.html`. Wysyła je narzędzie do maili, w którym jest lista zapisów (pola z nawiasów klamrowych zamień na znaczniki tego narzędzia). Kolejność:

| Mail | Kiedy | Do kogo |
|---|---|---|
| Zapisy 1. Potwierdzenie zapisu | od razu po zapisie | każdy nowy adres; bez kliknięcia w link adres nie trafia na listę |
| Zapisy 2. Start sprzedaży i kod | w dniu startu, rano | potwierdzone adresy |
| Zapisy 3. Ostatni dzień rabatu | dzień przed końcem rabatu | tylko adresy, które jeszcze nie użyły kodu |

Ceny z kodem są wpisane na stałe (36,75 zł i 48 zł przy cenie 49 zł i 15 zł za rodzeństwo). Jeśli zmienisz ceny, popraw je w mailach 2 i 3. Po końcu rabatu usuń z listy adresy osób, które nie złożyły zamówienia (tak obiecuje strona zapisów i polityka prywatności).

### Zapisy 1. Potwierdzenie zapisu

**Temat:** Potwierdź zapis i odbierz kod −25%
**Podgląd:** Jedno kliknięcie, a w dniu startu dostaniesz kod rabatowy.

```text
Potwierdź swój adres

Dzień dobry,

dziękujemy za zapis! Kliknij przycisk poniżej, żebyśmy wiedzieli, że to Twój
adres. Bez potwierdzenia nie możemy wysłać kodu rabatowego.

[Potwierdzam zapis] {LINK_POTWIERDZENIA}

Co dalej?
{DATA_STARTU} wyślemy Ci osobisty kod −25% na pierwszy film od Mikołaja.
Kod będzie ważny do {DATA_KONCA_RABATU}.

Nikt z tego adresu się nie zapisywał? Zignoruj tę wiadomość. Bez kliknięcia
nie wyślemy nic więcej.

Ciepło pozdrawiamy,
{PODPIS}

Dostajesz tę wiadomość, bo ktoś wpisał ten adres w formularzu zapisu na stronie
{ADRES_STRONY}. Film powstaje z pomocą narzędzi sztucznej inteligencji.
```

### Zapisy 2. Start sprzedaży i kod

**Temat:** Startujemy! Twój kod −25% na film od Mikołaja
**Podgląd:** Kod jest ważny do {DATA_KONCA_RABATU}. Link otworzy formularz z kodem.

```text
Mikołaj przyjmuje już zamówienia

Dzień dobry,

dziś ruszamy, a zapisane osoby dostają kod jako pierwsze. Mikołaj nagra film,
w którym zwróci się do Twojego dziecka po imieniu, pochwali to, czego nauczyło
się w tym roku, i pokaże jego zdjęcie w magicznej księdze.

Twój kod: {KOD}
−25% na całe pierwsze zamówienie · ważny do {DATA_KONCA_RABATU}

Ile zapłacisz z kodem
- Film dla jednego dziecka: 36,75 zł zamiast 49 zł
- Wspólny film dla dwojga dzieci: 48 zł zamiast 64 zł

[Zamów film z kodem] {LINK_ZAMOWIENIA}
Kod wpisze się sam w podsumowaniu zamówienia.

Jak to działa
1. Opowiedz nam o dziecku: imię, wiek, zdjęcie i to, czym może się pochwalić.
   Zajmie to około 5 minut.
2. Zapłać BLIK-iem, kartą albo przez Przelewy24.
3. Link do filmu dostaniesz mailem w ciągu 24 godzin.

Zamów do {OSTATNI_TERMIN}, a film dotrze przed Wigilią.

Ciepło pozdrawiamy,
{PODPIS}

Dostajesz tę wiadomość, bo ten adres został zapisany po kod rabatowy na stronie
{ADRES_STRONY}. Nie chcesz więcej wiadomości? Wypisz się: {LINK_WYPISANIA}
Film powstaje z pomocą narzędzi sztucznej inteligencji. Zdjęcie dziecka nie
trafia do żadnego narzędzia AI.
```

### Zapisy 3. Ostatni dzień rabatu

**Temat:** Twój kod −25% jest ważny jeszcze do jutra
**Podgląd:** Zostały 24 godziny, żeby zamówić film od Mikołaja taniej.

```text
Kod jest ważny jeszcze do jutra

Dzień dobry,

przypominamy, że Twój kod −25% wygasa {DATA_KONCA_RABATU} o północy. Jeśli
chcesz, żeby Mikołaj w tym roku powiedział coś osobiście do Twojego dziecka,
to dobry moment.

Twój kod: {KOD}
36,75 zł za film dla jednego dziecka, 48 zł za wspólny film dla dwojga

[Zamów film z kodem] {LINK_ZAMOWIENIA}
Formularz zajmie około 5 minut. Link do filmu wyślemy w ciągu 24 godzin.

Masz pytanie przed zamówieniem? Odpowiedz na tego maila, chętnie pomożemy.

Ciepło pozdrawiamy,
{PODPIS}

To ostatnia wiadomość o rabacie. Po {DATA_KONCA_RABATU} usuniemy ten adres
z listy zapisów. Nie chcesz czekać? Wypisz się teraz: {LINK_WYPISANIA}
Film powstaje z pomocą narzędzi sztucznej inteligencji.
```
