# Testy modeli wideo na fal.ai

Robocze skrypty do porównania obecnego modelu (Gemini Omni Flash) z modelami dostępnymi na [fal.ai](https://fal.ai): MiniMax H3, Kling, Seedance i Wan. Każdy model dostaje **ten sam kadr startowy i ten sam prompt ruchu**, a wyniki trafiają do jednej siatki porównawczej z podpisem modelu, kosztu i czasu generowania. Na tej podstawie wybierzemy model do długiego filmu.

To nie jest część produkcji: `generator/` działa bez zmian i bez tych skryptów.

## Zawartość

| Plik | Co jest w środku |
|---|---|
| `modele.py` | lista modeli: identyfikatory endpointów fal, orientacyjne ceny, tryb (kadr startowy albo obrazy referencyjne) |
| `ujecia.py` | ujęcia testowe: opisy kadrów i ruchu, prompty z zasadami produkcji |
| `mapowanie.py` | dopasowanie parametrów do schematu każdego modelu (nazwy pól, dozwolone długości i rozdzielczości) |
| `fal_api.py` | klient kolejki fal: schemat, wysłanie, status, wynik, pobranie |
| `zadania.py` | plan, uruchamianie równoległe, dziennik `wyniki.jsonl`, dokańczanie przerwanych zapytań |
| `porownanie.py` | siatka porównawcza MP4 |
| `cli.py` | polecenia (`python -m testy_fal ...`) |

## Przygotowanie

1. Zainstaluj zależności: `pip install -r requirements.txt`. Dochodzi pakiet `fal-client` do wgrywania kadrów. Bez niego kadry idą w zapytaniu jako JPEG (data URI), co też działa, ale wolniej.
2. Utwórz klucz na [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) i wpisz go w `.env` jako `FAL_KEY=...`. Klucza nie wklejaj do czatu ani do repozytorium.
3. Doładuj konto w [fal.ai/dashboard/billing](https://fal.ai/dashboard/billing). Na pierwszy test wystarczy ok. $25 (zob. [Koszty](#koszty)).
4. Sprawdź, czy masz portret Mikołaja w `output/selected/portrait.png`. To ten sam portret, z którego powstają kadry produkcji.
5. Do porównania z Omni Flash potrzebny jest `GEMINI_API_KEY`, ten sam co w produkcji.

Wszystkie polecenia uruchamiaj z głównego katalogu repozytorium.

## Przebieg testu

### 1. Sprawdź modele (bez kosztów)

```bash
python -m testy_fal sprawdz
```

Skrypt pobiera publiczny schemat każdego modelu z fal i pokazuje:
- jego pola;
- które z nich dostaną nasze parametry;
- co zostanie zmienione, np. 8 s na 10 s, gdy model przyjmuje tylko 5 albo 10 s;
- ile kosztuje jeden klip.

Gdy model zmienił adres (błąd 404), wpisz nowy identyfikator w `modele.py`. Identyfikator to część adresu strony modelu po `fal.ai/models/`.

### 2. Kadry startowe (Nano Banana Pro, ok. $0,13 za kadr)

Najpierw portret Kardamona, żeby wyglądał tak samo we wszystkich ujęciach:

```bash
python -m testy_fal kadry --only kardamon -n 3
python -m testy_fal wybierz kardamon 2          # numer najlepszego wariantu
python -m testy_fal kadry -n 3                  # pozostałe ujęcia testowe
python -m testy_fal wybierz kaczka 1            # i tak dla każdego ujęcia
```

Warianty trafiają do `output/testy_fal/kadry/`, wybrane do `output/testy_fal/wybrane/`. Sprawdź na kadrach to samo co w produkcji:
- wąsy zakrywają usta;
- Mikołaj ma okulary;
- elfy i Kardamon są dorośli;
- nie ma napisów.

**Szybki start bez nowych kadrów:** sceny wersji krótkiej mają już kadry w `output/selected/`, np. `--ujecia zorza pracownia renifery`.

### 3. Plan i koszt, bez wysyłania

```bash
python -m testy_fal generuj --na-sucho
```

Pokazuje każdy klip (ujęcie, model, rozdzielczość, długość, koszt), uwagi z dopasowania i dokładne zapytania do fal.

### 4. Generowanie

```bash
python -m testy_fal generuj                                  # domyślne modele i ujęcia
python -m testy_fal generuj --modele h3-turbo h3-max --ujecia kaczka pieczec -n 2
python -m testy_fal generuj --rozdzielczosc 720p             # tańszy pierwszy przegląd
```

| Opcja | Domyślnie | Opis |
|---|---|---|
| `--modele` | `omni h3-turbo kling-3 seedance-2-fast` | modele z `modele.py` |
| `--ujecia` | `kaczka pieczec poczta kardamon_raporty` | ujęcia testowe albo sceny wersji krótkiej |
| `-n` | 1 | wariantów na model i ujęcie |
| `--rozdzielczosc` | `1080p` | zamawiana; model dostaje najbliższą dostępną |
| `--czas` | 8 | sekundy; model dostaje najbliższą dostępną długość |
| `--rownolegle` | 3 | ile zapytań naraz |
| `--na-sucho` | | tylko plan |
| `--tak` | | bez pytania o potwierdzenie |

Przed wysłaniem skrypt pokazuje plan z kosztem i pyta o potwierdzenie. Klipy trafiają do `output/testy_fal/wideo/<ujęcie>/<model>_NN.mp4`. Kolejne uruchomienia dokładają warianty i niczego nie nadpisują.

Gdy przerwiesz skrypt (Ctrl+C, uśpiony laptop), zapytania wysłane do fal i tak się wykonają. Pobierz je bez płacenia drugi raz:

```bash
python -m testy_fal wznow
```

### 5. Porównanie

```bash
python -m testy_fal porownaj                     # wszystkie ujęcia
python -m testy_fal porownaj --ujecia kaczka --modele h3-turbo kling-3
python -m testy_fal podsumowanie                 # czasy, koszty, błędy
```

Siatki trafiają do `output/testy_fal/porownania/<ujęcie>.mp4`: do 9 klipów obok siebie, z podpisem nad każdym klipem (model, długość, rozdzielczość, koszt, czas generowania). Krótsze klipy zatrzymują się na ostatniej klatce.

## Ujęcia testowe

| Ujęcie | Skąd | Co sprawdza |
|---|---|---|
| `kaczka` | scen. 1, kontrola jakości | dłonie i drobne przedmioty: kaczka, bączek |
| `pieczec` | scen. 3, podpis i pieczęć | precyzyjna praca rąk: wosk, sygnet |
| `poczta` | scen. 3, poczta pneumatyczna | prosta fizyka (kapsuła w rurze) i Kardamon |
| `kardamon_raporty` | scen. 3, raporty elfów | druga postać, ujęcie 1 |
| `kardamon_karta` | scen. 3, karta prezentu | druga postać, ujęcie 2: czy to ten sam Kardamon |
| `lot` | scen. 2, lot nad lasami | łatwe ujęcie: czy tańszy model wystarczy na krajobrazy |
| `kardamon` | | tylko portret referencyjny, bez wideo |
| `zorza`, `pracownia`, … | wersja krótka | kadry z `output/selected/` |

Nowe ujęcie dodasz, dopisując `Shot(...)` do `TEST_SHOTS` w `ujecia.py`.

## Modele

`python -m testy_fal modele` pokazuje aktualną listę. Dwa tryby:
- **i2v:** kadr startowy jest pierwszą klatką, jak dziś w produkcji. Wygląd Mikołaja ustalamy na tanim kadrze, a model wideo tylko go ożywia.
- **ref** (`h3-ref`, `seedance-2-ref`): bez kadru startowego. Model sam rysuje scenę, a wygląd Mikołaja (i Kardamona) bierze z portretów. Daje mniej kontroli nad wąsami i ustami, ale warto sprawdzić, czy postacie są spójniejsze.

Ceny w `modele.py` to szacunki z porównywarek i stron fal (IX–XI 2026). Rozliczenie widać w panelu fal (*Usage*). Model bez znanej ceny ma w planie „?”.

Nowy model dodasz, dopisując `Model(...)` w `modele.py` i uruchamiając `sprawdz`. Gdy automat źle dobierze pole, wskaż je w `fields` (np. `{"image": "start_image_url"}`). Gdy model wymaga dodatkowego parametru, dopisz go w `fixed`.

## Koszty

Domyślny test to 4 modele × 4 ujęcia × 1 wariant, przy 1080p i 8 s:

| Model | Za klip | 4 ujęcia |
|---|---|---|
| Omni Flash (1080p) | ok. $1,20 | ok. $4,80 |
| H3 Max Turbo (1080p) | ok. $0,64 | ok. $2,56 |
| Kling 3.0 Pro | ok. $0,90 | ok. $3,60 |
| Seedance 2.0 Fast (720p) | ok. $1,92 | ok. $7,68 |
| **Razem** | | **ok. $19** |

Do tego kadry: 6 ujęć × 3 warianty × $0,134, czyli ok. $2,50. Dokładną kwotę dla Twoich ustawień pokazuje `generuj --na-sucho`.

## Jak oceniać

Dla każdego ujęcia obejrzyj siatkę i oceń modele w skali 1–5:

1. **Mikołaj przez całe ujęcie:** okulary zostają, wąsy cały czas zakrywają usta, broda się nie zmienia.
2. **Dłonie i przedmioty:** czy kaczka, wosk, sygnet i kapsuła zachowują się sensownie, bez dodatkowych palców i znikających rzeczy.
3. **Kardamon:** czy w `kardamon_raporty` i `kardamon_karta` to ta sama osoba.
4. **Zasady:** brak dzieci, napisów i cięć w środku ujęcia; elfy dorosłe.
5. **Ruch:** spokojny, płynny, bez „gumowych” deformacji.
6. **Czas i koszt:** z podpisu i z `podsumowanie`.

Dla 1–2 najlepszych modeli wygeneruj `-n 3` na najtrudniejszych ujęciach. Wtedy zobaczysz, ile wariantów trzeba odrzucać, a to najbardziej wpływa na koszt długiego filmu.

## Zasady

- Do fal trafiają **wyłącznie wygenerowane kadry i portrety** (Mikołaj, Kardamon), nigdy zdjęcia dzieci.
- Prompty mają te same zasady co produkcja:
  - w kadrze są tylko dorośli, nie ma dzieci;
  - nie ma napisów;
  - wąsy Mikołaja zakrywają usta.
- Do modeli, które to obsługują, idzie też negative prompt z tymi zasadami.
- Wyłączamy dźwięk i „ulepszanie” promptu przez model. Dźwięk dodaje montaż, a przepisany prompt zaciera porównanie.
- Wyniki są w `output/` i nie trafiają do repozytorium.

## Rozwiązywanie problemów

| Objaw | Rozwiązanie |
|---|---|
| `Brak klucza API: ustaw FAL_KEY` | dopisz `FAL_KEY` w `.env` |
| HTTP 401 / 403 | zły klucz albo brak środków na koncie fal |
| HTTP 404 przy `sprawdz` | model zmienił identyfikator: popraw go w `modele.py` |
| HTTP 422 przy `generuj` | model nie przyjął parametru: `sprawdz --odswiez --modele <model>`, potem `fields` / `fixed` w `modele.py` |
| `Brakuje kadrów` | wygeneruj i wybierz kadr (polecenie jest w komunikacie) |
| `Brak wideo w odpowiedzi modelu` | model zwrócił błąd albo zablokował kadr; treść odpowiedzi jest w komunikacie i w `podsumowanie` |
| Długie czekanie | to normalne przy kolejce fal; po przerwaniu użyj `wznow` |
