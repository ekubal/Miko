# Reklama zapisów: Mikołaj mówi do rodziców

Film reklamowy na etap zapisów przed startem sprzedaży, w trzech wariantach do testu. Mikołaj mówi do rodziców, wyjaśnia, co zamawiają, podaje datę startu zamówień (**środa, 25 listopada**) i zachęca do zapisu po kod −25%. Każdy wariant ma inny żart.

Wszystkie prompty (kadry, ruch, HeyGen) i kwestie są w `generator/scenariusze/reklama_zapisy.py`. Czytelna kopia, generowana z modułu: [`reklama_zapisy_prompty.md`](reklama_zapisy_prompty.md).

## Wspólne zasady

- **Format:** pion 9:16 (1080×1920) do Reels, Stories i TikToka; wersja 4:5 (1080×1350) do aktualności powstaje w montażu przez przycięcie. Długość 40–50 s, do tego skrót ok. 20 s.
- **Mikołaj jest prawdziwy.** Mówi do rodziców jak do wspólników w świątecznej tajemnicy. Dziecko, które zerknie na telefon, zobaczy Mikołaja, który szykuje dla niego niespodziankę. Bez słów „film AI”, „generowany”, „aktor”.
- **Bez dzieci w kadrach.** Elfy są dorosłe. Księga pokazuje pustą, świecącą złotą ramkę, a na liście montaż dopisuje odręcznie „Imię Twojego dziecka”, bez prawdziwego imienia i zdjęcia.
- **Mikołaj mówi w liczbie mnogiej („Wy”, „Wasze dziecko”)**, bez form zależnych od płci rodzica i dziecka.
- **Bez napisów w generowanych kadrach.** Napisy, planszę końcową i imię na liście dodaje montaż.
- **Rabat zawsze jako kod dla zapisanych**, bez przekreślonych cen.
- **Napisy na ekranie przez cały film** (większość ogląda bez dźwięku): pełny tekst kwestii plus 2–3 wyróżnione hasła. Font Nunito Sans pogrubiony, ok. 60 px, kremowy na półprzezroczystym granatowym tle. Napisy trzymamy poza górnymi 270 px i dolnymi 380 px kadru, bo tam są przyciski aplikacji.
- **Plansza końcowa (3 s, w każdym wariancie):** logo (płatek śniegu i „Wiadomość od Mikołaja”), „Zapisz się po kod −25%”, „Start zamówień: 25 listopada”, „[ADRES STRONY]/zapisy”. Granatowe tło, złote akcenty, padający śnieg.
- **Dźwięk:** głos Mikołaja z ElevenLabs. Pod spodem cicho podkład muzyczny z `generator.audio music`, a do tego proste efekty: kliknięcie kamery, szelest pergaminu, dzwoneczek Płatka.

## Ujęcia wspólne

Dwa ujęcia pokazują, co dostaje dziecko, i są w każdym wariancie:

| Ujęcie | Co widać | Montaż dodaje |
|---|---|---|
| `ksiega_pion` | Mikołaj przewraca stronę złotej księgi, pusta złota ramka zaczyna świecić | napis „Tu będzie zdjęcie Waszego dziecka” obok ramki |
| `lista_pion` | ręka Mikołaja przybija czerwoną pieczęć na liście grzecznych dzieci | odręczne „Imię Twojego dziecka” (font Caveat) na pustej linii nad pieczęcią |

---

## Wariant 1 „Tajna narada”

**Pomysł:** Mikołaj rozmawia z rodzicami szeptem, jak przy wspólnym sekrecie. **Żarty:** elf podsłuchuje zza fotela, a na końcu Mikołaj śmieje się za głośno i sam się ucisza. **Haczyk na pierwsze sekundy:** szept „Ciii… czy dzieci już śpią?”.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:09 | `w1_mowi` (HeyGen): Mikołaj w fotelu przy kominku, pochylony do kamery | Ciii… Drodzy rodzice, czy dzieci już śpią? To dobrze. Mam do Was sprawę, ale musi zostać między nami, dorosłymi. | Ciii… czy dzieci już śpią? |
| 0:09–0:12 | `w1_elf`: elf wychyla się zza fotela, przyłapany chowa się z powrotem | Elfy też nie podsłuchują! | — |
| 0:12–0:22 | `w1_mowi` (HeyGen) | W tym roku nagram dla Waszego dziecka osobistą wiadomość. Powiem do niego po imieniu i pochwalę za to, czego się nauczyło. | Osobista wiadomość od Mikołaja |
| 0:22–0:32 | `ksiega_pion`, potem `lista_pion` | Pokażę jego zdjęcie w mojej magicznej księdze i wpiszę imię na listę grzecznych dzieci. Szczegóły podpowiecie mi w krótkim formularzu. | Imię · osiągnięcie · zdjęcie w księdze |
| 0:32–0:42 | `w1_mowi` (HeyGen) | Zamówienia przyjmuję od dwudziestego piątego listopada. A kto zapisze się wcześniej, dostanie ode mnie kod rabatowy: minus dwadzieścia pięć procent. | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:42–0:48 | `w1_ciii`: Mikołaj śmieje się, nagle robi „ciii” i rozgląda się, potem puszcza oko | Zapiszcie się już dziś. I ani słowa dzieciom! Ho, ho, ho! …Ciii. | Zapisz się już dziś |
| 0:48–0:51 | plansza końcowa | — | — |

**Skrót (ok. 20 s):** pierwsze zdanie z 0:00 („Ciii… Drodzy rodzice, czy dzieci już śpią?”), potem 0:32–0:48 i plansza.

## Wariant 2 „Czy to już nagrywa?”

**Pomysł:** Mikołaj nagrywa pierwszą w życiu wiadomość wideo, a elf jest operatorem starej drewnianej kamery. **Żarty:** Mikołaj zagląda w obiektyw z bliska, „elfy mówią, że to kod rabatowy, ja mówię: prezent dla rodziców”, a na końcu nie wie, jak wyłączyć kamerę. **Haczyk:** okulary i broda na cały ekran oraz „Halo? Czy to już nagrywa?”.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:05 | `w2_za_blisko`: twarz Mikołaja tuż przy obiektywie, potem odsuwa się i poprawia okulary | Halo? Czy to już nagrywa? Elfie, czerwona lampka się świeci? | Halo? Czy to już nagrywa? |
| 0:05–0:08 | `w2_elf`: elf za starą kamerą pokazuje kciuk w górę | — (dźwięk: kliknięcie) | — |
| 0:08–0:19 | `w2_mowi` (HeyGen): Mikołaj przy biurku, trochę uroczyście | Ho, ho, ho! Dzień dobry, drodzy rodzice! Elfy namówiły mnie na to nagranie, bo w tym roku mam dla Was coś nowego. | — |
| 0:19–0:33 | `ksiega_pion`, potem `lista_pion` | Nagram dla Waszego dziecka osobistą wiadomość. Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, pokażę jego zdjęcie w magicznej księdze i wpiszę imię na listę grzecznych dzieci. | Po imieniu · z pochwałą · ze zdjęciem w księdze |
| 0:33–0:45 | `w2_mowi` (HeyGen) | Zamówienia ruszają dwudziestego piątego listopada. Kto zapisze się wcześniej, dostanie kod rabatowy. Elfy mówią, że to minus dwadzieścia pięć procent. Ja mówię: prezent dla rodziców! | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:45–0:50 | `w2_wylacz`: Mikołaj szuka przycisku i zasłania obiektyw dłonią | Zapiszcie się już dziś. A teraz… jak to się wyłącza? Elfie? | — |
| 0:50–0:53 | plansza końcowa (wyłania się z ciemności po zasłonięciu obiektywu) | — | — |

**Skrót (ok. 20 s):** 0:00–0:08, potem 0:33–0:50 i plansza.

## Wariant 3 „Za długa lista”

**Pomysł:** w tym roku dzieci są tak grzeczne, że lista grzecznych dzieci nie mieści się w gabinecie, więc Mikołaj prosi rodziców o pomoc. **Żarty:** pergamin toczy się przez cały gabinet i wylatuje drzwiami na śnieg, a na końcu młody renifer Płatek nosi listę jak szalik. **Haczyk:** rozwijająca się lista. Płatek jest postacią z filmu (scenariusz 4), więc reklama przedstawia go rodzicom przed premierą.

| Czas | Obraz | Mikołaj mówi | Wyróżniony napis |
|---|---|---|---|
| 0:00–0:08 | `w3_rolka`: lista toczy się przez gabinet i wylatuje drzwiami na śnieg, Mikołaj się śmieje | Ho, ho, ho! W tym roku dzieci są tak grzeczne, że lista nie mieści się w gabinecie! | Lista się nie mieści… |
| 0:08–0:14 | `w3_mowi` (HeyGen): Mikołaj z rulonem pod pachą | Dlatego, drodzy rodzice, potrzebuję Waszej pomocy. Nagram dla Waszego dziecka osobistą wiadomość. | Osobista wiadomość od Mikołaja |
| 0:14–0:26 | `ksiega_pion` | Powiem do niego po imieniu, pochwalę za to, czego się nauczyło, i pokażę jego zdjęcie w magicznej księdze. Szczegóły podpowiecie mi w krótkim formularzu. | Imię · osiągnięcie · zdjęcie w księdze |
| 0:26–0:37 | `w3_mowi` (HeyGen) | Zamówienia ruszają dwudziestego piątego listopada. Zapiszcie się wcześniej, a dostaniecie kod rabatowy, minus dwadzieścia pięć procent, i wiadomość o starcie jako pierwsi. | Start zamówień: 25 listopada · Zapisani: kod −25% |
| 0:37–0:42 | `w3_platek`: Płatek ciągnie koniec listy jak szalik, Mikołaj ciągnie za drugi | Płatku! Oddaj listę, to nie jest szalik! | — |
| 0:42–0:45 | plansza końcowa | — | — |

**Skrót (ok. 20 s):** 0:00–0:08, potem 0:26–0:42 i plansza.

---

## Produkcja

Polecenia uruchamiamy z katalogu głównego repozytorium. Wyniki trafiają do `output/reklama_zapisy/`.

1. **Obrazy wzorcowe:** portret Mikołaja (`output/selected/portrait.png`) i portret Płatka ze scenariusza 4 (`output/od_listu_do_san/wybrane/platek.png`; bez niego Płatek może wyglądać inaczej niż w filmie).
2. **Kadry pionowe** (12 ujęć) i wybór najlepszych:
   ```bash
   python -m generator.scenariusze -s reklama_zapisy kadry -n 3
   python -m generator.scenariusze -s reklama_zapisy wybierz w1_mowi 2
   ```
3. **Klipy** (9 ujęć bez mówienia do kamery). Najpierw tani test w 360p: sprawdza, czy model przyjmuje format 9:16. Jeśli nie, wygeneruj kadry i klipy w 16:9 i przytnij je w montażu.
   ```bash
   python -m generator.scenariusze -s reklama_zapisy wideo --only w1_elf --resolution 360p -n 1
   python -m generator.scenariusze -s reklama_zapisy wideo -n 2
   python -m generator.scenariusze -s reklama_zapisy wybierz-wideo w1_elf 1
   ```
4. **Głos Mikołaja** (16 kwestii, zapisany głos z `generator.audio`):
   ```bash
   python -m generator.scenariusze -s reklama_zapisy kwestie
   ```
   W1 zaczyna się szeptem: jeśli nagranie `w1_1` jest za głośne, nagraj je ponownie spokojniej (`--only w1_1 --force`).
5. **HeyGen** (Avatar IV, format 9:16): dla każdego kadru `w*_mowi` osobny klip na każdą kwestię mówioną do kamery. W W1 są to `w1_1`, `w1_3` i `w1_5`; w W2 `w2_2` i `w2_4`; w W3 `w3_2` i `w3_4`. Opis ruchu jest w pliku z promptami.
6. **Montaż** (np. CapCut albo DaVinci Resolve, 1080×1920, 30 kl./s):
   - ujęcia według tabel, głos zza kadru pod klipy;
   - napisy, imię na liście, napis przy księdze i plansza końcowa;
   - podkład muzyczny ok. 18 dB ciszej niż głos.
   Eksport: 9:16, 4:5 i skróty ok. 20 s.
7. **Publikacja:** postacie i sceny są wygenerowane z pomocą AI. Jeśli Meta tego wymaga, zaznacz informację o AI przy publikacji reklamy.

**Test:** wszystkie trzy warianty w jednej grupie reklam na Meta, z tym samym tekstem. Po 3 dniach zostają te z najniższym kosztem zapisu (zasady w `reklamy/plan_kampanii_zapisy.md`). Moje typy:
- **W1:** najmocniejszy haczyk na pierwsze sekundy;
- **W2:** najbardziej zabawny;
- **W3:** buduje znajomość z Płatkiem przed filmem.
