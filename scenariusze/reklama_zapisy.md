# Reklama zapisów: Mikołaj mówi do rodziców

Film reklamowy na etap zapisów przed startem sprzedaży. **Wybrany: wariant 2 „Czy to już nagrywa?”**; warianty 1 i 3 zostają jako zapas do testu. Mikołaj mówi do rodziców, wyjaśnia, co zamawiają, podaje datę startu zamówień (**środa, 25 listopada**) i zachęca do zapisu po kod −25%. Każdy wariant ma inny żart.

Wszystkie prompty (kadry, ruch, HeyGen) i kwestie są w `generator/scenariusze/reklama_zapisy_poziomo.py`. Czytelna kopia, generowana z modułu: [`reklama_zapisy_prompty.md`](reklama_zapisy_prompty.md).

## Wspólne zasady

- **Format:** poziom 16:9 (1920×1080): YouTube i reklamy Google, strona zapisów (miejsce na film 16:9 w sekcji „Zwiastun”), aktualności i reklamy w filmach na Facebooku. Długość 40–50 s, do tego skrót ok. 20 s. Kompozycja: postać trochę z boku kadru, spokojne tło po drugiej stronie i na dole kadru na napisy.
- **Mikołaj jest prawdziwy.** Mówi do rodziców jak do wspólników w świątecznej tajemnicy. Dziecko, które zerknie na telefon, zobaczy Mikołaja, który szykuje dla niego niespodziankę. Bez słów „film AI”, „generowany”, „aktor”.
- **Bez dzieci w kadrach.** Elfy są dorosłe. Księga pokazuje pustą, świecącą złotą ramkę, a na liście montaż dopisuje odręcznie „Imię Twojego dziecka”, bez prawdziwego imienia i zdjęcia.
- **Mikołaj mówi w liczbie mnogiej („Wy”, „Wasze dziecko”)**, bez form zależnych od płci rodzica i dziecka.
- **Bez napisów w generowanych kadrach.** Napisy, planszę końcową i imię na liście dodaje montaż.
- **Rabat zawsze jako kod dla zapisanych**, bez przekreślonych cen.
- **Napisy na ekranie przez cały film** (wiele osób ogląda bez dźwięku): pełny tekst kwestii plus 2–3 wyróżnione hasła. Font Nunito Sans pogrubiony, ok. 48 px, kremowy na półprzezroczystym granatowym tle, w dolnej części kadru, wyśrodkowane, najwyżej 2 linie, co najmniej 60 px od krawędzi.
- **Plansza końcowa (3 s, w każdym wariancie):** po lewej logo (płatek śniegu i „Wiadomość od Mikołaja”), po prawej „Zapisz się po kod −25%”, „Start zamówień: 25 listopada” i „[ADRES STRONY]/zapisy”. Granatowe tło, złote akcenty, padający śnieg.
- **Dźwięk:** głos Mikołaja z ElevenLabs. Pod spodem cicho podkład muzyczny z `generator.audio music`, a do tego proste efekty: kliknięcie kamery, szelest pergaminu, dzwoneczek Płatka.

## Ujęcia wspólne

Dwa ujęcia pokazują, co dostaje dziecko, i są w każdym wariancie:

| Ujęcie | Co widać | Montaż dodaje |
|---|---|---|
| `ksiega` | Mikołaj przewraca stronę złotej księgi, pusta złota ramka zaczyna świecić | napis „Tu będzie zdjęcie Waszego dziecka” obok ramki |
| `lista` | ręka Mikołaja przybija czerwoną pieczęć na liście grzecznych dzieci | odręczne „Imię Twojego dziecka” (font Caveat) na pustej linii nad pieczęcią |

---

## Wariant 1 „Tajna narada”

**Pomysł:** Mikołaj rozmawia z rodzicami szeptem, jak przy wspólnym sekrecie. **Żarty:** elf podsłuchuje zza fotela, a na końcu Mikołaj śmieje się za głośno i sam się ucisza. **Haczyk na pierwsze sekundy:** szept „Ciii… czy dzieci już śpią?”.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:09 | `w1_mowi` (HeyGen): Mikołaj w fotelu przy kominku, pochylony do kamery | Ciii… Drodzy rodzice, czy dzieci już śpią? To dobrze. Mam do Was sprawę, ale musi zostać między nami, dorosłymi. | Ciii… czy dzieci już śpią? |
| 0:09–0:12 | `w1_elf`: elf wychyla się zza fotela, przyłapany chowa się z powrotem | Elfy też nie podsłuchują! | — |
| 0:12–0:22 | `w1_mowi` (HeyGen) | W tym roku nagram dla Waszego dziecka osobistą wiadomość. Powiem do niego po imieniu i pochwalę za to, czego się nauczyło. | Osobista wiadomość od Mikołaja |
| 0:22–0:32 | `ksiega`, potem `lista` | Pokażę jego zdjęcie w mojej magicznej księdze i wpiszę imię na listę grzecznych dzieci. Szczegóły podpowiecie mi w krótkim formularzu. | Imię · osiągnięcie · zdjęcie w księdze |
| 0:32–0:42 | `w1_mowi` (HeyGen) | Zamówienia przyjmuję od dwudziestego piątego listopada. A kto zapisze się wcześniej, dostanie ode mnie kod rabatowy: minus dwadzieścia pięć procent. | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:42–0:48 | `w1_ciii`: Mikołaj śmieje się, nagle robi „ciii” i rozgląda się, potem puszcza oko | Zapiszcie się już dziś. I ani słowa dzieciom! Ho, ho, ho! …Ciii. | Zapisz się już dziś |
| 0:48–0:51 | plansza końcowa | — | — |

**Skrót (ok. 20 s):** pierwsze zdanie z 0:00 („Ciii… Drodzy rodzice, czy dzieci już śpią?”), potem 0:32–0:48 i plansza.

## Wariant 2 „Czy to już nagrywa?” (wybrany)

**Pomysł:** Mikołaj nagrywa pierwszą w życiu wiadomość wideo, a elf jest operatorem starej drewnianej kamery. **Żarty:** Mikołaj zagląda w obiektyw z bliska, „elfy mówią, że to kod rabatowy, ja mówię: prezent dla rodziców”, a na końcu nie wie, jak wyłączyć kamerę. **Haczyk:** okulary i broda na cały ekran oraz „Halo? Czy to już nagrywa?”.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:06 | `w2_za_blisko` (6 s): twarz Mikołaja tuż przy obiektywie, potem odsuwa się i poprawia okulary | Halo? Czy to już nagrywa? Elfie, czerwona lampka się świeci? | Halo? Czy to już nagrywa? |
| 0:06–0:10 | `w2_elf` (4 s): elf za starą kamerą pokazuje kciuk w górę | — (dźwięk: kliknięcie) | — |
| 0:10–0:21 | `w2_mowi` (HeyGen): Mikołaj przy biurku, trochę uroczyście | Ho, ho, ho! Dzień dobry, drodzy rodzice! Elfy namówiły mnie na to nagranie, bo w tym roku mam dla Was coś nowego. | — |
| 0:21–0:35 | `ksiega` (8 s), potem `lista` (6 s) | Nagram dla Waszego dziecka osobistą wiadomość. Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, pokażę jego zdjęcie w magicznej księdze i wpiszę imię na listę grzecznych dzieci. | Po imieniu · z pochwałą · ze zdjęciem w księdze |
| 0:35–0:47 | `w2_mowi` (HeyGen) | Zamówienia ruszają dwudziestego piątego listopada. Kto zapisze się wcześniej, dostanie kod rabatowy. Elfy mówią, że to minus dwadzieścia pięć procent. Ja mówię: prezent dla rodziców! | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:47–0:52 | `w2_wylacz` (5 s): Mikołaj szuka przycisku i zasłania obiektyw dłonią | Zapiszcie się już dziś. A teraz… jak to się wyłącza? Elfie? | — |
| 0:52–0:55 | plansza końcowa (wyłania się z ciemności po zasłonięciu obiektywu) | — | — |

Czasy są szacunkowe: dokładne wyznaczą nagrania głosu. Klipy dłuższe od kwestii skracamy w montażu; jeśli kwestia jest dłuższa od klipu, ostatnią klatkę klipu zatrzymujemy na chwilę.

**Skrót (ok. 20 s):** 0:00–0:10, potem 0:35–0:52 i plansza.

## Wariant 3 „Za długa lista”

**Pomysł:** w tym roku dzieci są tak grzeczne, że lista grzecznych dzieci nie mieści się w gabinecie, więc Mikołaj prosi rodziców o pomoc. **Żarty:** pergamin toczy się przez cały gabinet i wylatuje drzwiami na śnieg, a na końcu młody renifer Płatek nosi listę jak szalik. **Haczyk:** rozwijająca się lista. Płatek jest postacią z filmu (scenariusz 4), więc reklama przedstawia go rodzicom przed premierą.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:08 | `w3_rolka`: lista toczy się przez gabinet i wylatuje drzwiami na śnieg, Mikołaj się śmieje | Ho, ho, ho! W tym roku dzieci są tak grzeczne, że lista nie mieści się w gabinecie! | Lista się nie mieści… |
| 0:08–0:14 | `w3_mowi` (HeyGen): Mikołaj z rulonem pod pachą | Dlatego, drodzy rodzice, potrzebuję Waszej pomocy. Nagram dla Waszego dziecka osobistą wiadomość. | Osobista wiadomość od Mikołaja |
| 0:14–0:26 | `ksiega` | Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, i pokażę jego zdjęcie w magicznej księdze. Szczegóły podpowiecie mi w krótkim formularzu. | Imię · osiągnięcie · zdjęcie w księdze |
| 0:26–0:37 | `w3_mowi` (HeyGen) | Zamówienia ruszają dwudziestego piątego listopada. Zapiszcie się wcześniej, a dostaniecie kod rabatowy, minus dwadzieścia pięć procent, i wiadomość o starcie jako pierwsi. | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:37–0:42 | `w3_platek`: Płatek ciągnie koniec listy jak szalik, Mikołaj ciągnie za drugi | Płatku! Oddaj listę, to nie jest szalik! | — |
| 0:42–0:45 | plansza końcowa | — | — |

**Skrót (ok. 20 s):** 0:00–0:08, potem 0:26–0:42 i plansza.

---

## Produkcja

Polecenia uruchamiamy z katalogu głównego repozytorium. Wyniki trafiają do `output/reklama_zapisy_poziomo/`.

1. **Obrazy wzorcowe:** portret Mikołaja (`output/selected/portrait.png`) i portret Płatka ze scenariusza 4 (`output/od_listu_do_san/wybrane/platek.png`; bez niego Płatek może wyglądać inaczej niż w filmie).
2. **Kadry wariantu 2** (6 ujęć) i wybór najlepszego wariantu każdego z nich:
   ```bash
   python -m generator.scenariusze -s reklama_zapisy_poziomo kadry --only w2_za_blisko w2_elf w2_mowi w2_wylacz ksiega lista -n 3
   python -m generator.scenariusze -s reklama_zapisy_poziomo wybierz w2_mowi 2      # tak samo dla pozostałych 5
   ```
   Przy `w2_mowi` sprawdź, czy twarz, okulary i broda są dobrze widoczne i oświetlone z przodu: z tego kadru HeyGen robi mówiącego Mikołaja.
3. **Klipy** (5 ujęć bez mówienia do kamery: `w2_za_blisko`, `w2_elf`, `w2_wylacz`, `ksiega`, `lista`). Najpierw jeden tani test w 360p:
   ```bash
   python -m generator.scenariusze -s reklama_zapisy_poziomo wideo --only w2_za_blisko --resolution 360p -n 1
   python -m generator.scenariusze -s reklama_zapisy_poziomo wideo --only w2_za_blisko w2_elf w2_wylacz ksiega lista -n 2
   python -m generator.scenariusze -s reklama_zapisy_poziomo wybierz-wideo w2_za_blisko 1   # tak samo dla pozostałych
   ```
4. **Głos Mikołaja** (zapisany głos z `generator.audio`; wariant 2 ma 5 kwestii):
   ```bash
   python -m generator.scenariusze -s reklama_zapisy_poziomo kwestie --only w2_1 w2_2 w2_3 w2_4 w2_5
   ```
   `w2_1` („Halo? Czy to już nagrywa?”) ma brzmieć niepewnie, jak pytanie do elfa: jeśli wyjdzie zbyt uroczyście, nagraj je ponownie (`--only w2_1 --force`).

   **Jeśli głos brzmi sztucznie,** najpierw porównaj zestawy ustawień i głosy (`python -m generator.audio probki`, opis w README, rozdział 6.3). W reklamie liczy się wyczucie żartu, więc najpewniejsza jest przemiana nagrania człowieka:
   - ktoś z dobrą dykcją nagrywa telefonem 5 kwestii wariantu 2, z pauzami i humorem;
   - `python -m generator.audio przemiana w2_1.m4a -o output/reklama_zapisy_poziomo/glos/w2_1.mp3` (i tak dalej dla każdej kwestii);
   - intonację i polski akcent model bierze z nagrania, a barwę z głosu Mikołaja.
5. **HeyGen** (Avatar IV, format 16:9): dwa klipy z kadru `w2_mowi`, jeden z nagraniem `w2_2`, drugi z `w2_4`. Opis ruchu jest w pliku z promptami. (W innych wariantach: W1 `w1_1`, `w1_3`, `w1_5`; W3 `w3_2`, `w3_4`.)
6. **Montaż** (np. CapCut albo DaVinci Resolve, 1920×1080, 30 kl./s):
   - ujęcia według tabel, głos zza kadru pod klipy;
   - napisy, imię na liście, napis przy księdze i plansza końcowa;
   - podkład muzyczny ok. 18 dB ciszej niż głos.
   Eksport: 16:9 w pełnej wersji i skrót ok. 20 s (np. reklama przed filmem na YouTube).
7. **Publikacja:** postacie i sceny są wygenerowane z pomocą AI. Jeśli YouTube, Google albo Meta tego wymagają, zaznacz informację o AI przy publikacji reklamy.

**Kolejność:** robimy wariant 2. Pozostałe warto zrobić, gdy będzie czas na test: wszystkie trzy w jednej kampanii, z tym samym tekstem, a po 3 dniach zostają te z najniższym kosztem zapisu (zasady w `reklamy/plan_kampanii_zapisy.md`). Moje typy:
- **W1:** najmocniejszy haczyk na pierwsze sekundy;
- **W2:** najbardziej zabawny;
- **W3:** buduje znajomość z Płatkiem przed filmem.
