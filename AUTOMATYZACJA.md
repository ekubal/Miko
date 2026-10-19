# Automatyzacja systemu i panel administracyjny

19 paź 2026 · zmienia założenie z [MVP.md](MVP.md), że pierwsze filmy powstają ręcznie

## Cel

Zamówienie przechodzi od płatności do wysłanego filmu **bez udziału człowieka**. Człowiek zajmuje się tylko wyjątkami, które system sam oznaczy, oraz nadzoruje całość w panelu administracyjnym.

Dotychczasowe skrypty (`generator/`) zostają rdzeniem produkcji. Zmienia się to, co je uruchamia: zamiast poleceń wpisywanych ręcznie robi to kolejka zadań na serwerze.

## Co trzeba zastąpić, żeby nie było kroków ręcznych

| Krok ręczny dziś | Zastępstwo w automacie | Ryzyko |
|---|---|---|
| Przepisanie danych z formularza | Własny formularz zapisuje zamówienie w bazie; płatność potwierdza powiadomienie (webhook) ze Stripe | niskie |
| Sprawdzenie zdjęcia | Lokalna kontrola na serwerze: wykrycie twarzy i ostrości (bez wysyłania zdjęcia do zewnętrznych usług). Słabe zdjęcie → automatyczny mail 2 z prośbą o nowe | niskie |
| Człowiek czyta i zatwierdza tekst | Reguły (liczba słów, zwrot, zdanie końcowe, obietnica prezentu) + moderacja treści przez model + odpowiedź „DO SPRAWDZENIA”. Wątpliwe → kolejka przeglądu. **Opcjonalnie: rodzic zatwierdza tekst jednym kliknięciem przed nagraniem** | średnie: treść dla dziecka |
| Odsłuchanie imienia | Rozpoznanie mowy na nagraniu (speech-to-text) i porównanie z tekstem; przy niezgodności imienia automatyczny zapis fonetyczny i ponowne nagranie, po 2 próbach → przegląd | średnie |
| **HeyGen ręcznie** | **API usługi lip-sync** (HeyGen API albo inna, zob. niżej) | **wysokie: koszt i jakość** |
| Montaż | Bez zmian (`generator.montage`), na serwerze z ffmpeg | niskie |
| Kontrola jakości | Automatyczna: długości scen, obecność dźwięku, zgodność transkrypcji z tekstem, czy imię na liście i zdjęcie należą do zamówienia (dane z bazy, nie ręczne kopiowanie). W pierwszym tygodniu dodatkowo losowa kontrola człowieka, np. co 5. film | średnie |
| Wgranie na Drive i mail | Prywatny magazyn plików, strona z filmem pod linkiem z tokenem, mail przez usługę wysyłkową | niskie |
| Usunięcie zdjęć po 7 dniach | Automatyczne zadanie codzienne + reguła wygasania plików w magazynie | niskie |

### Mówiący Mikołaj: decyzja do podjęcia

To jedyny krok, którego koszt rośnie z każdym filmem i który decyduje o jakości.

- **HeyGen API:** ten sam wygląd co w planie, ale API ma osobny cennik, inny niż plan Creator. Według dostępnych zestawień Avatar IV kosztuje ok. 0,05–0,10 USD za sekundę, czyli ok. 8–17 zł za 45 sekund. Przy cenie 49 zł zostaje wtedy ok. 15–30 zł na reklamę i zysk, więc docelowy koszt pozyskania klienta z [MARKETING.md](MARKETING.md) trzeba obniżyć do ok. 10–15 zł albo podnieść cenę.
- **Inne usługi lip-sync** (np. sync.so, D-ID, Hedra): do porównania na jednym teście. Kryteria to jakość ruchu ust po polsku, koszt za minutę, czas generowania i umowa powierzenia danych (DPA).
- **Do sprawdzenia:** czy taniej wychodzi gotowy klip Mikołaja (raz wygenerowany) z podmianą samego ruchu ust do nowego nagrania (lip-sync wideo do wideo) niż generowanie awatara ze zdjęcia przy każdym filmie.

Rekomendacja: przed budową całości jeden dzień na test 2–3 dostawców na tym samym nagraniu i wybór po jakości i cenie. Kod ma mieć wymiennego dostawcę (jeden moduł `lipsync`), żeby zmiana nie wymagała przebudowy.

## Architektura

```
Rodzic ── strona + formularz ──► API ──► Stripe Checkout (BLIK, karta)
                                  │            │ webhook „zapłacono”
                                  ▼            ▼
                              Baza danych (zamówienia, statusy, zdarzenia)
                                  │
                                  ▼
                           Kolejka zadań ──► Worker(y) z ffmpeg
                                  │             ├─ Gemini: tekst, moderacja
                                  │             ├─ ElevenLabs: głos, rozpoznanie mowy
                                  │             ├─ lip-sync API: mówiący Mikołaj
                                  │             └─ montaż (generator.montage)
                                  ▼
                     Magazyn plików (UE, szyfrowany, wygasanie po 7 dniach)
                                  │
                                  ▼
                 Usługa e-mail ──► Rodzic: link do strony z filmem
                                  
Panel administracyjny ◄── ta sama baza i kolejka
```

| Element | Propozycja | Uwagi |
|---|---|---|
| Backend i panel | Python (FastAPI), jedna aplikacja | używa bezpośrednio modułów `generator/` |
| Baza | PostgreSQL | zamówienia, dzieci, zdarzenia, koszty |
| Kolejka | Redis + RQ albo kolejka w bazie | zadania z ponawianiem i limitem równoległości |
| Worker | kontener z ffmpeg i fontem | skalowany liczbą procesów w szczycie grudnia |
| Magazyn plików | S3-kompatybilny w UE (np. Cloudflare R2, Backblaze, Google Cloud Storage w regionie UE) | szyfrowanie, linki wygasające, automatyczne usuwanie |
| Płatności | Stripe Checkout z BLIK-iem i kartą (albo Przelewy24) | numer zamówienia przekazywany do płatności; webhook potwierdza zapłatę |
| E-mail | usługa transakcyjna (np. Postmark, Resend, Brevo) | domena z SPF i DKIM; szablony z `szablony/` |
| Hosting | serwer lub chmura w UE | RODO: dane dzieci nie wychodzą poza UE bez potrzeby |

### Przebieg zamówienia (maszyna stanów)

```
OPŁACONE
  → DANE_SPRAWDZONE      (zdjęcie: twarz i ostrość; pola formularza)      ✗ → CZEKA_NA_RODZICA (mail 2)
  → TEKST_GOTOWY         (Gemini)
  → TEKST_ZATWIERDZONY   (reguły + moderacja [+ zgoda rodzica])            ✗ → PRZEGLĄD
  → GŁOS_GOTOWY          (ElevenLabs)
  → GŁOS_SPRAWDZONY      (rozpoznanie mowy, imię)                          ✗ → ponów z wymową, potem PRZEGLĄD
  → MIKOŁAJ_GOTOWY       (lip-sync API)                                    ✗ → ponów, potem PRZEGLĄD
  → FILM_GOTOWY          (montaż)
  → KONTROLA_OK          (automatyczna kontrola jakości [+ losowa ręczna]) ✗ → PRZEGLĄD
  → WYSŁANE              (mail 3 z linkiem)
  → DANE_USUNIĘTE        (7 dni po wysłaniu)
```

Każdy krok:
- da się bezpiecznie powtórzyć (nie dubluje kosztów ani maili);
- zapisuje czas, koszt (np. sekundy lip-sync, znaki ElevenLabs) i wynik w dzienniku zdarzeń;
- przy błędzie ponawia z rosnącym odstępem, a po limicie trafia do kolejki przeglądu z opisem problemu.

Licznik 24 godzin biegnie od płatności. Zamówienie zagrożone opóźnieniem trafia na górę panelu i wysyła alert.

## Panel administracyjny

Panel nie służy do robienia filmów, tylko do nadzoru i obsługi wyjątków.

### 1. Pulpit
- zamówienia dziś i w sezonie, przychód, cel 30 zamówień do 6 grudnia;
- liczba zamówień na każdym etapie, średni czas od płatności do wysyłki, zamówienia zagrożone przekroczeniem 24 godzin;
- błędy i kolejka przeglądu;
- koszt AI na film (tekst, głos, lip-sync) i łącznie, marża po kosztach;
- stan kont u dostawców: pozostałe środki lub kredyty (Gemini, ElevenLabs, lip-sync), z alertem przy niskim poziomie.

### 2. Kolejka przeglądu (wyjątki)
Lista zamówień zatrzymanych przez system, z powodem:
- tekst oznaczony przez moderację albo „DO SPRAWDZENIA”;
- niezgodność imienia w nagraniu po ponowieniach;
- błąd lip-sync lub montażu po ponowieniach;
- losowa kontrola jakości;
- rodzic poprosił o poprawkę.

Akcje: popraw tekst lub wymowę i **wznów od wybranego kroku**, zatwierdź mimo ostrzeżenia, napisz do rodzica, anuluj ze zwrotem.

### 3. Zamówienia
- wyszukiwarka (numer, e-mail, imię dziecka) i filtry po statusie, dacie, źródle (UTM, kod rabatowy);
- karta zamówienia:
  - dane z formularza i miniatury zdjęć (dopóki nie usunięte);
  - oś czasu kroków z czasem i kosztem każdego;
  - podgląd wyników: tekst, nagranie, klip lip-sync, gotowy film;
  - historia maili i odpowiedzi rodzica;
  - płatność (Stripe) i zwrot;
  - akcje: wznów od kroku, wyślij ponownie maila, przedłuż link do filmu, usuń dane teraz.

### 4. Dane osobowe (RODO)
- harmonogram automatycznego usuwania i dziennik usunięć (dowód realizacji);
- ręczne usunięcie na żądanie rodzica i eksport danych (prawo dostępu);
- rejestr dostawców przetwarzających dane (tekst i głos: Gemini, ElevenLabs, lip-sync) z informacją, jakie dane do nich trafiają. Zdjęcie dziecka nie trafia do żadnego z nich.

### 5. Sprzedaż i marketing
- kody rabatowe (influencerzy) z limitem i licznikiem użyć;
- wydatki na reklamy: wpisywane ręcznie albo pobierane z API Meta i Google Ads;
- koszt pozyskania klienta per kanał i kod;
- wyniki ankiety po dostawie.

### 6. Ustawienia produkcji
- cena, dopłata za rodzeństwo, ostatni termin zamówień;
- **wyłącznik sprzedaży** (np. gdy kończą się kredyty albo kolejka jest za długa); strona pokazuje wtedy komunikat zamiast formularza;
- polityka przeglądu: czy rodzic zatwierdza tekst, jaki odsetek losowej kontroli ręcznej, ile ponowień przed przeglądem;
- wersje materiałów wspólnych (portret, klipy, głos, muzyka) i promptów: zmiana działa od kolejnych zamówień, a każde zamówienie pamięta, na jakiej wersji powstało;
- dostawca lip-sync i jego ustawienia;
- stan integracji: klucze API, webhooki, ostatnie błędy.

### 7. Dostęp
- logowanie z dwuskładnikowym uwierzytelnianiem, 1–3 konta administratorów;
- dziennik działań (kto, co i kiedy zmienił lub obejrzał);
- dostęp do zdjęć dzieci tylko w karcie zamówienia, bez masowego pobierania.

## Strona rodzica (część automatu)

- **Status zamówienia** pod linkiem z maila potwierdzającego: na jakim etapie jest film. Bez szczegółów technicznych, bezpieczny dla dziecka.
- **Opcjonalne zatwierdzenie tekstu:** „Tak Mikołaj powie do Kasi. Zatwierdź albo popraw.” Brak reakcji w ciągu np. 6 godzin oznacza automatyczne zatwierdzenie, jeśli tekst przeszedł reguły i moderację.
- **Uzupełnienie danych:** link z maila 2 prowadzi do formularza z jednym brakującym polem (np. nowe zdjęcie), a zamówienie wraca do kolejki samo.
- **Strona z filmem:** odtwarzacz, pobieranie, data wygaśnięcia linku, ankieta.

## Plan prac do 16 listopada

Cztery tygodnie to mało na pełny automat, więc kolejność musi chronić start sprzedaży.

| Tydzień | Zakres |
|---|---|
| 20–26 paź | Test dostawców lip-sync i wybór. Materiały wspólne (portret, sceny, klipy, głos, muzyka). Szkielet backendu: baza, kolejka, worker z ffmpeg, magazyn plików |
| 27 paź – 2 lis | Formularz i Stripe Checkout z webhookiem. Kroki automatu od tekstu do montażu na kolejce. Kontrola zdjęcia, moderacja tekstu, rozpoznanie mowy |
| 3–9 lis | Wysyłka maili, strona z filmem, usuwanie danych. Panel: pulpit, kolejka przeglądu, karta zamówienia z „wznów od kroku” |
| 10–15 lis | Testy całości na 10–20 zamówieniach próbnych (znajomi), poprawki, piksele i oznaczenia źródła, dokumenty prawne |
| od 16 lis | Start sprzedaży. Losowa kontrola ręczna w pierwszym tygodniu, potem według wyników |

Po starcie: statystyki marketingowe w panelu, eksport danych, import wydatków z API reklamowych.

## Decyzje do podjęcia

1. **Dostawca lip-sync i budżet na film.** Od tego zależy marża i docelowy koszt pozyskania klienta.
2. **Kontrola tekstu:** w pełni automatyczna z przeglądem wyjątków czy z jednoklikowym zatwierdzeniem przez rodzica.
3. **Hosting:** zarządzana chmura (mniej pracy, wyższy koszt) czy własny serwer w UE (taniej, więcej utrzymania).
4. **Płatności:** Stripe czy Przelewy24.
