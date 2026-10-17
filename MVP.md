# MVP: Film od Mikołaja z AI

15 paź 2026 · @Jak

## Założenia MVP

MVP robimy ręcznie: pierwsze 30–50 filmów powstaje w gotowych narzędziach webowych, bez programowania. Automatyzację budujemy dopiero wtedy, gdy rodzice faktycznie płacą.

### Co dostaje klient

- Film 2–3 minuty w jakości 1080p, link mailem w ciągu 24 godzin.
- Część ogólna (ok. 1,5–2 min): sceny z domu i pracowni Mikołaja, przygotowane raz i używane w każdym filmie.
- Część personalizowana (30–45 s): Mikołaj mówi do dziecka po imieniu, wspomina jego osiągnięcie i marzenie.
- Zdjęcie dziecka w magicznej księdze oraz imię na liście grzecznych dzieci.

### Jak sprzedajemy

- Prosta strona z przykładowym filmem, formularz zamówienia i link do płatności.
- Cena testowa: 49 zł za film, +15 zł za każde kolejne dziecko z rodzeństwa.

### Czego MVP nie robi

- Nie animuje twarzy dziecka. Zdjęcie zostaje statyczne w księdze.
- Nie ma aplikacji ani automatycznej produkcji.
- Nie obiecuje konkretnego prezentu, chyba że rodzic zaznaczy, że jest już kupiony.

### Co chcemy sprawdzić do 6 grudnia

- Czy zbierzemy co najmniej 30 płatnych zamówień.
- Ile kosztuje pozyskanie jednego klienta z reklam.
- Czy produkcja jednego filmu zajmuje mniej niż 30 minut.
- Jak rodzice oceniają film (krótka ankieta po dostawie).

## Narzędzia i koszty

Cały MVP zmieści się w ok. 55–70 USD miesięcznie (plus VAT) za trzy subskrypcje; reszta narzędzi jest darmowa albo płatna od transakcji. Ceny sprawdzone 15 października 2026, przed zakupem potwierdź je na stronach dostawców.

| Etap | Narzędzie | Plan | Koszt miesięcznie | Co daje |
|---|---|---|---|---|
| Postać Mikołaja, tła, księga | Google Flow (model obrazu Nano Banana Pro) | Google AI Pro | 19,99 USD | 1000 kredytów miesięcznie + 50 dziennie |
| Sceny ogólne (wideo) | Google Flow (Veo 3.1) | ten sam plan | 0 USD | klip Veo 3.1 Fast (8 s) = 20 kredytów, czyli ok. 50 klipów miesięcznie |
| Głos Mikołaja | ElevenLabs | Starter, potem Creator | 6 USD, potem 22 USD | licencja komercyjna od Starter; ok. 30 min głosu (Starter) lub ok. 100 min (Creator) |
| Mówiący Mikołaj | HeyGen (Photo Avatar, Avatar IV) | Creator | 29 USD | 600 kredytów, nielimitowane awatary ze zdjęcia, własne audio, eksport 1080p |
| Tekst przemówienia | Gemini (w planie Google AI Pro) lub ChatGPT/Claude | — | 0 USD | pisanie spersonalizowanych kwestii |
| Muzyka | ElevenLabs Music lub biblioteka muzyki bez tantiem | — | 0 USD | podkład z licencją komercyjną |
| Montaż | CapCut (desktop) lub DaVinci Resolve | darmowy | 0 USD | szablon projektu, w którym podmieniasz 3 elementy |
| Strona i formularz | np. Carrd + Tally | darmowe plany | 0 USD | strona z przykładem, formularz z uploadem zdjęć |
| Płatności | Stripe Payment Links lub Przelewy24 (BLIK) | — | prowizja od transakcji | link do płatności bez sklepu |
| Dostawa | Google Drive + e-mail | — | 0 USD | link do pobrania filmu |

**Ile filmów wytrzyma HeyGen Creator:** Avatar IV zużywa ok. 20 kredytów na minutę (admakeai), więc 600 kredytów to ok. 30 minut mówiącego Mikołaja. Przy części personalizowanej 45 s daje to ok. 40 filmów miesięcznie. Więcej zamówień = plan Pro za 49 USD (1000 kredytów, ok. 66 filmów). Niewykorzystane kredyty przechodzą na kolejny miesiąc.

**ElevenLabs:** plan darmowy nie daje praw komercyjnych, więc minimum to Starter. Przy zakupie z UE dochodzi VAT.

## Przygotowanie jednorazowe

Przygotowanie zajmuje ok. 2 tygodnie: tworzysz jedną postać Mikołaja, z niej wszystkie sceny i grafiki, potem głos i szablon montażu. Prompty są po angielsku, bo modele lepiej je wykonują; kwestie mówione są po polsku.

### Krok 1. Portret Mikołaja do awatara (Google Flow, Nano Banana Pro)

To najważniejszy obraz w projekcie: z niego HeyGen zrobi mówiącego Mikołaja, a modele obrazu — wszystkie pozostałe sceny. Wygeneruj 8–12 wersji i wybierz jedną.

```text
Photorealistic portrait of a warm, kind Santa Claus, about 70 years old,
full white natural-looking beard, rosy cheeks, gentle smiling eyes,
classic red velvet coat with white fur trim, no hat or with a soft red hat.
He sits in a cozy armchair in his wooden workshop, warm fireplace light,
soft bokeh Christmas lights in the background.
Front-facing, looking straight into the camera, head and shoulders framing,
mouth closed in a calm gentle smile, face evenly lit and fully visible,
nothing covering the mouth or beard.
Cinematic 16:9, high detail, natural skin texture.
Original character design, no brand logos, no text.
```

Wymagania, żeby awatar dobrze mówił: twarz na wprost, usta zamknięte, broda nie zasłania ust, równe światło, wysoka rozdzielczość.

### Krok 2. Pozostałe kadry z tą samą postacią (Nano Banana Pro)

Załącz wybrany portret jako obraz referencyjny i generuj kolejne kadry tym samym promptem bazowym, zmieniając tylko opis sceny:

```text
Use the attached image as the reference character. Keep Santa's face,
beard, hair, coat and proportions exactly the same.
Scene: [SCENE]
Warm cinematic lighting, photorealistic, 16:9.
No brand logos, no text, no letters anywhere in the image.
```

Warianty pola `[SCENE]`:

1. Exterior of Santa's cozy wooden house at night, snow falling, warm light in the windows, Santa not visible yet.
2. Santa walking through his busy workshop full of wrapped presents and toys, elves working in the background.
3. Santa sitting in his armchair, opening a huge old leather-bound book on his lap, golden magical glow coming from the pages.
4. Santa next to his sleigh with reindeer in the snow at night, waving goodbye to the camera.

### Krok 3. Grafiki do personalizacji (Nano Banana Pro)

To puste szablony, na które w montażu wklejasz zdjęcie i imię dziecka. Napisy dodajesz w edytorze, bo modele obrazu często psują polskie litery.

**Magiczna księga:**

```text
Top-down close-up of a huge old open leather book on a wooden table,
the right page holds an empty ornate golden picture frame (blank inside,
plain cream paper), the left page has decorative golden Christmas ornaments,
soft candle light, sparkles of magic dust. 16:9, photorealistic.
No text, no letters, no people.
```

**Lista grzecznych dzieci:**

```text
An old parchment scroll titled with an empty ornamental banner at the top,
unrolled on Santa's wooden desk, many blank lines, a red wax seal and a
quill pen next to it, warm candle light. 16:9, photorealistic.
No text, no letters, no writing on the scroll.
```

### Krok 4. Sceny wideo (Google Flow, Veo 3.1)

W Flow użyj opcji „Frames to Video”: kadr z kroku 2 jako pierwsza klatka. Generuj w trybie Fast (20 kredytów za klip), najlepsze wersje możesz powtórzyć w trybie Quality. Prompt dla każdej sceny:

```text
Gentle slow camera push-in. [MOTION]. Calm, magical Christmas atmosphere,
soft ambient sounds only (crackling fire, sleigh bells far away).
Nobody speaks, no lip movement, no text, no logos. 8 seconds.
```

Warianty pola `[MOTION]`:

1. snow falls softly, lights flicker in the windows
2. Santa walks slowly between shelves with presents, elves busy in the background
3. Santa slowly opens the book, golden light rises from the pages
4. Santa waves goodbye, reindeer shake their heads, the sleigh lifts off

### Krok 5. Głos Mikołaja (ElevenLabs, Voice Design)

Opis głosu w narzędziu Voice Design:

```text
A warm, deep, gentle voice of a kind elderly man around 70, like a loving
grandfather telling a bedtime story. Slow, calm pace, soft friendly
laugh, slightly husky, very clear diction. Native Polish speaker.
```

Testuj na zdaniu: „Ho, ho, ho! Dzień dobry, kochanie. Cały rok patrzyłem, jak pięknie rośniesz.” Zapisz najlepszy głos i używaj tylko jego. Nagraj też raz kwestie ogólne (powitanie, opis pracowni, pożegnanie).

### Krok 6. Szablon montażu (CapCut lub DaVinci Resolve)

Zbuduj jeden projekt-wzór, który przy każdym zamówieniu kopiujesz i podmieniasz w nim trzy elementy:

| Czas | Scena | Co się zmienia |
|---|---|---|
| 0:00–0:15 | Dom Mikołaja nocą + muzyka | nic |
| 0:15–0:35 | Pracownia + głos ogólny | nic |
| 0:35–1:20 | Mówiący Mikołaj z HeyGen | cały klip |
| 1:20–1:40 | Magiczna księga | zdjęcie dziecka w ramce |
| 1:40–1:55 | Lista grzecznych dzieci + pieczęć | imię dziecka |
| 1:55–2:15 | Pożegnanie przy saniach | nic |

Na koniec zrób 5 filmów testowych dla dzieci znajomych i pokaż je rodzicom, zanim wydasz złotówkę na reklamy.

## Produkcja jednego zamówienia

Jeden film to 7 kroków i ok. 20–30 minut pracy, z czego większość to czekanie na wygenerowanie klipu w HeyGen. Przy kilku zamówieniach naraz rób każdy krok seriami.

### Krok 1. Sprawdź zamówienie

Płatność zaksięgowana, zgody zaznaczone, zdjęcie ostre i z widoczną twarzą. Brakuje czegoś — napisz do rodzica od razu, nie po wygenerowaniu.

### Krok 2. Tekst Mikołaja (Gemini, ChatGPT lub Claude)

```text
Jesteś Świętym Mikołajem. Napisz tekst, który powiesz do dziecka w filmie.

Dane od rodzica:
- Jak zwracać się do dziecka (forma w wołaczu): {ZWROT}
- Wiek: {WIEK}
- Osiągnięcie z tego roku: {OSIAGNIECIE}
- Co lubi: {ZAINTERESOWANIA}
- Nad czym może popracować (opcjonalnie): {DO_POPRAWY}
- Wymarzony prezent: {PREZENT}
- Czy prezent jest już kupiony: {TAK/NIE}

Zasady:
- 90–110 słów, czyli ok. 40–45 sekund mówienia.
- Zwróć się do dziecka 2–3 razy, zawsze dokładnie w podanej formie.
- Ciepło i prosto, językiem zrozumiałym dla dziecka w tym wieku.
- Pochwal konkretne osiągnięcie z danych.
- "Do poprawy" wspomnij delikatnie jako zachętę, nigdy jako zarzut ani groźbę.
- Prezent kupiony: powiedz, że elfy już go szykują. Niekupiony: powiedz,
  że zapisałeś to marzenie, bez obietnicy.
- Nie wymyślaj faktów spoza danych. Żadnych adresów, nazwisk ani marek.
- Jeśli dane zawierają coś nieodpowiedniego dla dziecka, odpowiedz tylko:
  DO SPRAWDZENIA
- Zakończ zdaniem: "A teraz zajrzyjmy razem do mojej magicznej księgi!"

Zwróć wyłącznie tekst do przeczytania, z interpunkcją ułatwiającą
naturalne czytanie.
```

Przeczytaj tekst przed dalszym krokiem. W MVP każdy tekst zatwierdza człowiek.

### Krok 3. Głos (ElevenLabs)

Wklej tekst, wybierz zapisany głos Mikołaja, pobierz plik MP3. Odsłuchaj imię: jeśli jest źle wymawiane, zapisz je fonetycznie (np. „Dzesika” zamiast „Jessica”) i wygeneruj ponownie.

### Krok 4. Mówiący Mikołaj (HeyGen)

1. Raz na początku: utwórz Photo Avatar z portretu Mikołaja z przygotowania (krok 1).
2. Przy zamówieniu: nowy film → wybierz awatara → źródło dźwięku: wgrane audio (MP3 z ElevenLabs).
3. Model Avatar IV, format 16:9, eksport 1080p.
4. Jeśli dostępny jest opis ruchu, wpisz: `gentle nodding, warm smile, calm small hand gestures, looking into the camera`.

### Krok 5. Montaż (CapCut lub DaVinci Resolve)

1. Skopiuj projekt-wzór i nazwij go numerem zamówienia.
2. Podmień klip z HeyGen (0:35–1:20).
3. Wklej zdjęcie dziecka w ramkę księgi, dodaj delikatną poświatę.
4. Wpisz imię na liście fontem odręcznym z polskimi znakami.
5. Eksport: MP4, 1080p.

### Krok 6. Kontrola jakości

- [ ] Imię brzmi poprawnie i jest w dobrej formie (wołacz).
- [ ] Usta zgadzają się z głosem, twarz Mikołaja bez zniekształceń.
- [ ] Zdjęcie i imię należą do właściwego dziecka.
- [ ] Brak obietnicy prezentu, jeśli rodzic zaznaczył, że nie jest kupiony.

### Krok 7. Dostawa

Wgraj film do folderu na Google Drive z dostępem przez link i wyślij mail z szablonu (link, podziękowanie, prośba o ocenę w ankiecie). Zdjęcia dziecka usuń po 7 dniach od dostawy.

## Materiały i formularz

Przed startem potrzebujesz 10 materiałów własnych i formularza z 13 polami; najważniejsze dla polskiej wersji są forma wołacza imienia i rodzaj gramatyczny.

### Materiały do przygotowania

- [ ] Portret Mikołaja do awatara (1 obraz)
- [ ] 4 kadry scen i 4 klipy wideo z nich (dom, pracownia, księga, sanie)
- [ ] 2 puste szablony: magiczna księga z ramką i lista grzecznych dzieci
- [ ] Zapisany głos Mikołaja i nagrane kwestie ogólne (powitanie, pracownia, pożegnanie)
- [ ] Podkład muzyczny 2–3 min z licencją komercyjną
- [ ] Font odręczny z polskimi znakami (np. z Google Fonts)
- [ ] Projekt-wzór montażu
- [ ] Film demonstracyjny na stronę (dziecko znajomych za pisemną zgodą rodziców)
- [ ] Strona: opis, demo, cena, FAQ, regulamin, polityka prywatności
- [ ] Szablony maili (potwierdzenie, prośba o brakujące dane, dostawa) i ankieta po dostawie

### Pola formularza zamówienia

| Pole | Przykład | Wymagane | Po co |
|---|---|---|---|
| Imię dziecka | Kasia | tak | lista grzecznych dzieci |
| Jak Mikołaj ma się zwracać | Kasiu, Kasieńko | tak | wołacz w przemówieniu |
| Chłopiec czy dziewczynka | dziewczynka | tak | formy „nauczyłeś / nauczyłaś” |
| Wiek | 5 lat | tak | język dopasowany do wieku |
| Zdjęcie dziecka (1–2) | JPG lub PNG, twarz widoczna | tak | ramka w księdze |
| Osiągnięcie z tego roku | nauczyła się jeździć na rowerze | tak | pochwała |
| Co lubi | dinozaury, rysowanie | tak | ciepły szczegół |
| Nad czym może popracować | sprzątanie zabawek | nie | delikatna zachęta |
| Wymarzony prezent | rower z koszykiem | nie | wzmianka o marzeniu |
| Czy prezent jest już kupiony | tak / nie | tak | czy Mikołaj może go obiecać |
| Rodzeństwo w filmie | drugi zestaw pól | nie | dopłata 15 zł |
| E-mail rodzica i termin | do 5 grudnia | tak | dostawa |
| Zgody | zaznaczenie pól | tak | RODO, regulamin, informacja o AI |

Treść zgód powinna obejmować: przetwarzanie zdjęcia i danych dziecka wyłącznie w celu wykonania filmu, usunięcie ich po 7 dniach od dostawy, akceptację regulaminu oraz informację, że film powstaje z pomocą AI. Treść zgód i regulaminu warto dać do sprawdzenia prawnikowi.

## Budżet i marża

Narzędzia na dwa miesiące sezonu kosztują ok. 400–680 zł, a koszt narzędzi na jeden film to ok. 7–14 zł, więc o zysku decyduje koszt reklam, nie AI. Przeliczenia przy założonym kursie 3,70 zł za 1 USD, ceny narzędzi bez VAT.

| Scenariusz (listopad–grudzień) | 30 filmów | 100 filmów |
|---|---|---|
| Plany narzędzi | Google AI Pro, ElevenLabs Starter, HeyGen Creator | Google AI Pro, ElevenLabs Creator, HeyGen Pro |
| Koszt narzędzi za 2 miesiące | 110 USD ≈ 407 zł | 182 USD ≈ 673 zł |
| Przychód przy 49 zł za film | 1470 zł | 4900 zł |
| Wynik przed reklamami | ok. 1060 zł | ok. 4230 zł |
| Koszt narzędzi na film | ok. 13,6 zł | ok. 6,7 zł |

Czego tabela nie obejmuje:

- **Reklamy:** każde 10 zł kosztu pozyskania klienta to 1000 zł mniej przy 100 zamówieniach. Dlatego pierwsze zamówienia warto zebrać z poleceń, grup rodziców i przedszkoli.
- **Prowizja operatora płatności:** zależy od cennika Stripe lub Przelewy24.
- **VAT od sprzedaży:** jeśli jesteś płatnikiem VAT, z 49 zł brutto zostaje 39,84 zł netto.
- **Twój czas:** 20–30 minut na film, czyli 35–50 godzin przy 100 filmach.

Powyżej ok. 40 filmów miesięcznie HeyGen Creator nie wystarczy: plan Pro za 49 USD daje 1000 kredytów (ok. 66 filmów), a wyższe progi Pro mają więcej kredytów.

## Harmonogram i prawo

Sprzedaż może ruszyć 16 listopada, jeśli przygotowanie zacznie się w poniedziałek 19 października; film jest cyfrowy, więc sprzedaje się do samej Wigilii.

### Kwestie prawne

- **Dane dziecka (RODO):** zgoda rodzica, cel wyłącznie wykonanie filmu, usunięcie po 7 dniach. W tym MVP zdjęcie dziecka nie trafia do żadnego narzędzia AI, tylko do edytora; do modeli tekstu i głosu przekazuj tylko imię i informacje z formularza, bez nazwiska i adresu.
- **Informacja o AI:** od 2 sierpnia 2026 obowiązują przepisy art. 50 AI Act o przejrzystości treści generowanych przez AI (Cooley). Mikołaj jest postacią fikcyjną, ale w opisie produktu i regulaminie napisz wprost, że film powstaje z pomocą AI.
- **Licencje:** prawa komercyjne dają dopiero płatne plany (ElevenLabs od Starter, HeyGen bez znaku wodnego od Creator). Muzyka tylko z licencją komercyjną. Żadnych znanych postaci, logo ani stylizacji na reklamy znanych marek.
- **Prawa konsumenta:** film jest treścią cyfrową robioną na zamówienie. Dodaj w formularzu zgodę na rozpoczęcie realizacji przed upływem terminu na odstąpienie od umowy i informację o utracie tego prawa.
- **Forma działalności:** sprawdź, czy mieścisz się w limicie działalności nierejestrowanej, czy potrzebujesz firmy.

Regulamin, politykę prywatności i treść zgód warto przed startem dać do sprawdzenia prawnikowi.

### Plan do startu

Przygotowania zajmują cztery tygodnie, a okno sprzedaży trwa niespełna sześć tygodni, od 16 listopada do Wigilii.

## Przykładowe scenariusze

Każdy film składa się z 6 scen: 5 ogólnych nagrywasz raz, a scenę 3 piszesz od nowa dla każdego dziecka. Kwestie ogólne są bez form „byłeś / byłaś”, żeby pasowały do każdego dziecka; dla rodzeństwa nagraj je drugi raz w liczbie mnogiej.

### Scenariusz ogólny

#### Scena 1. Dom Mikołaja nocą (0:00–0:15)

- **Obraz:** Śnieg pada na drewniany dom, w oknach ciepłe światło, kamera powoli się przybliża.
- **Mikołaj (głos zza kadru):** „Ho, ho, ho! Witaj w moim domu na dalekiej Północy.”

#### Scena 2. Pracownia (0:15–0:35)

- **Obraz:** Mikołaj idzie między półkami pełnymi prezentów, w tle pracują elfy.
- **Mikołaj:** „Tu, w mojej pracowni, elfy pracują dzień i noc. Pakują prezenty i pilnują, żeby wszystko było gotowe na Święta. Ale dziś odkładam pracę na chwilę, bo mam bardzo ważną wiadomość. Wiadomość tylko dla ciebie.”
- **Wersja dla rodzeństwa:** „…Wiadomość tylko dla was.”

#### Scena 3. Mikołaj mówi do dziecka (0:35–1:20)

- **Obraz:** mówiący Mikołaj z HeyGen w fotelu przy kominku.
- **Mikołaj:** tekst personalizowany (przykłady niżej).

#### Scena 4. Magiczna księga (1:20–1:40)

- **Obraz:** Mikołaj otwiera księgę, złote światło; zbliżenie na stronę ze zdjęciem dziecka w ramce.
- **Mikołaj:** „To moja magiczna księga. Zapisuję w niej wszystkie dzieci, które w tym roku starały się być dobre. Spójrz, kto jest na tej stronie! Księga nigdy się nie myli.”

#### Scena 5. Lista grzecznych dzieci (1:40–1:55)

- **Obraz:** pergamin na biurku, imię dziecka pojawia się odręcznym pismem, czerwona pieczęć.
- **Mikołaj:** „A tu jest moja lista grzecznych dzieci. Twoje imię jest już na niej zapisane. Przybijam pieczęć… gotowe!”
- **Wersja dla rodzeństwa:** „…Wasze imiona są już na niej zapisane.”

#### Scena 6. Pożegnanie przy saniach (1:55–2:15)

- **Obraz:** Mikołaj przy saniach z reniferami macha do kamery, sanie unoszą się w górę.
- **Mikołaj:** „Muszę już wracać do pracy, bo reniferów nie można zostawiać samych na długo. Słuchaj rodziców i uśmiechaj się często. Do zobaczenia w Wigilię! Ho, ho, ho! Wesołych Świąt!”

### Scena 3, przykład 1: Kasia, 5 lat

**Dane:** nauczyła się jeździć na rowerze bez bocznych kółek; lubi dinozaury i rysowanie; prezent (zestaw do rysowania z dinozaurami) jest kupiony.

> Ho, ho, ho! Kasiu, mam dla ciebie wspaniałe wieści! Moje elfy przez cały rok sprawdzały, jak sobie radzisz. I wiesz, co mi powiedziały? Że nauczyłaś się jeździć na rowerze bez bocznych kółek! To było bardzo odważne. Jestem z ciebie ogromnie dumny, Kasiu. Słyszałem też, że uwielbiasz dinozaury i pięknie rysujesz. Pewnie twoje dinozaury są groźniejsze niż moje renifery! Pamiętaj, że każdy rysunek zrobiony z uśmiechem sprawia mi wielką radość. Zapisałem też twoje marzenie o zestawie do rysowania z dinozaurami. Elfy już go starannie pakują. A teraz zajrzyjmy razem do mojej magicznej księgi!

### Scena 3, przykład 2: Jaś, 8 lat

**Dane:** sam przeczytał pierwszą całą książkę; lubi piłkę nożną; do poprawy: sprzątanie zabawek; prezent (piłka i bramka) nie jest kupiony, więc Mikołaj go nie obiecuje.

> Ho, ho, ho! Jasiu, jak dobrze cię widzieć! Mam w pracowni specjalną lunetę, przez którą patrzę na wszystkie dzieci. W tym roku zobaczyłem coś niezwykłego: sam przeczytałeś swoją pierwszą całą książkę! To wielka sprawa, Jasiu. Książki to prawdziwe magiczne przygody. Wiem też, że kochasz piłkę nożną. Elfy szepnęły mi jeszcze jedną rzecz… że zabawki czasem zostają na podłodze. Wierzę, że od dziś będziesz moim pomocnikiem w sprzątaniu, prawda? Twoje marzenie o piłce i bramce zapisałem na mojej liście marzeń. A teraz zajrzyjmy razem do mojej magicznej księgi!

### Scena 3, przykład 3: rodzeństwo Zosia (3 lata) i Antek (6 lat)

**Dane:** Zosia pierwszy raz poszła do przedszkola i lubi tańczyć; Antek pomagał opiekować się siostrą i lubi klocki; prezenty są kupione. W scenie 4 pokaż oba zdjęcia, w scenie 5 oba imiona. Ta wersja jest dłuższa (ok. 50–55 s), więc zużywa więcej kredytów HeyGen.

> Ho, ho, ho! Zosiu i Antku, dzisiaj mam wiadomość dla was obojga! Zosiu, słyszałem, że w tym roku pierwszy raz poszłaś do przedszkola. To była wielka odwaga! I podobno tańczysz tak pięknie, że nawet moje elfy próbują cię naśladować. Antku, a ty byłeś wspaniałym starszym bratem. Pomagałeś Zosi i dbałeś o nią, a to dla mnie bardzo ważne. Wiem też, że budujesz z klocków niesamowite budowle. Elfy już pakują dla was prezenty, o których marzycie. Pamiętajcie, żeby zawsze trzymać się razem. A teraz zajrzyjmy razem do mojej magicznej księgi!

## Źródła

- HeyGen – cennik
- Google Flow – cennik
- Hooked – koszt klipu Veo 3.1 Fast w Flow
- gradually.ai – cennik ElevenLabs
- admakeai – kredyty HeyGen Avatar IV
- Cooley – AI Act, art. 50
