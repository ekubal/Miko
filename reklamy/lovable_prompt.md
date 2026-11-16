# Prompt do Lovable: pakiet reklam graficznych

Lovable zbuduje z tego promptu przeglądarkowe „Studio reklam”. Studio składa statyczne reklamy w formatach Meta i Google według zasad marki. Każdą reklamę pobierasz jako PNG w dokładnym rozmiarze, a cały pakiet jako ZIP z arkuszem tekstów do Menedżera reklam.

Prompty są po angielsku, tak jak inne prompty do narzędzi AI w tym projekcie. Wszystkie teksty reklam są po polsku i Lovable ma je wkleić bez zmian.

## Jak użyć

1. W Lovable utwórz nowy projekt. W **Project Knowledge** wklej sekcję „Wiedza o projekcie” (na końcu tego pliku): Lovable będzie pamiętać zasady przy każdej kolejnej zmianie.
2. Wklej **prompt 1**. Powstanie szkielet: marka, dwie pierwsze reklamy w trzech formatach Meta, wgrywanie kadrów i pobieranie PNG.
3. Wgraj kadry z filmu do odpowiednich miejsc (lista niżej) i sprawdź wygląd.
4. Po kolei wklej **prompt 2** (wszystkie koncepcje i formaty) i **prompt 3** (pakiet ZIP i arkusz tekstów). **Prompt 4** (klasyczne banery Google) jest opcjonalny.
5. Uzupełnij zmienne ([DATA STARTU], [DATA KOŃCA RABATU], [OSTATNI TERMIN], [ADRES STRONY]) i pobierz pakiet.

**Kadry do wgrania** (z `output/selected/` i `output/od_listu_do_san/wybrane/`; same kadry, bez napisów):

| Miejsce w studiu | Plik |
|---|---|
| `portret` | `portrait.png` (portret Mikołaja) |
| `dom` | `dom.png` |
| `pracownia` | `pracownia.png` |
| `ksiega` | `ksiega.png` |
| `sanie` | `sanie.png` |
| `platek` | portret Płatka (`platek.png`) |
| `kula` | kadr z kulą śnieżną (`kula.png`) |

Nie wgrywaj zdjęć dzieci. Reklamy z reakcjami dzieci (koncepcja 1 z MARKETING.md) to filmy, a nie grafiki. Wymagają też pisemnej zgody rodziców, więc tego pakietu nie dotyczą.

---

## Prompt 1: studio, marka i pierwsze reklamy

```text
Build a browser app called "Studio reklam – Wiadomość od Mikołaja". It renders a package of static ad creatives for my product and exports each one as a pixel-exact PNG. All interface labels and all ad copy must be in Polish, exactly as written below (copy the Polish text verbatim, do not translate or rephrase it). No backend, no login, no database: everything runs in the browser. Save settings in localStorage and uploaded images in IndexedDB (idb-keyval).

## 1. Product context
"Wiadomość od Mikołaja" sells personalized Christmas videos from Santa Claus (Mikołaj) in Poland. A parent fills in a 5-minute form: the child's name, how Santa should address the child, age, a photo, an achievement from this year, interests, the dream gift. In the film Santa speaks to the child by name, praises the achievement, shows the child's photo in a magic golden book and writes the name on the nice list. The link to the film arrives by email within 24 hours. Price: 49 zł, plus 15 zł for each sibling in the same film. Audience: Polish parents aged 25–45. Ads run on Meta (Facebook, Instagram) and Google.

There are two campaign phases:
- A "Przed startem" (pre-launch): people leave their email and get a personal −25% discount code on launch day. Landing page: [ADRES STRONY]/zapisy.
- B "Sprzedaż" (sales): direct orders. Landing page: [ADRES STRONY].

## 2. Content rules (non-negotiable)
1. Santa is real. Children may see these ads on a parent's phone. Never suggest that Santa is fictional, an actor or a generated character, and never show "behind the scenes".
2. No images of children at all: do not generate, draw or use stock photos of children or of any people.
3. Do not generate images with AI. Use only the images I upload (frames from our film) and decorative elements drawn in SVG/CSS. Until an image is uploaded, show a placeholder: navy background, subtle snowflake pattern, the slot name in small text.
4. Santa's look comes only from the uploaded frames (about 80 years old, glasses, long white beard, thick moustache covering the mouth). Never draw a cartoon Santa.
5. No invented social proof: no star ratings, review quotes, customer counts, "bestseller" badges or numbers other than those given here.
6. No crossed-out prices and no "was/now" prices. Show "49 zł" as a plain price. The pre-launch discount is always a code for people who sign up ("kod −25% dla zapisanych").
7. No text baked into images: all text is live HTML on top of the image, so it stays sharp and editable.
8. Polish typography: „…” quotes, en dash "–", the real minus sign in "−25%", a non-breaking space between a number and "zł" and after one-letter words (a, i, o, u, w, z).

## 3. Brand
Colors as CSS variables:
--navy #0e1726 (night background), --navy-deep #0a111d, --navy-soft #1b2a44,
--accent #e3a948 (gold), --red #a3222b, --red-dark #8a1c23,
--cream #f5ecdc, --paper #fbf6ec, --gold-frame #c9a24a, --green #2f7a55,
--ink #2b1f14 (text on light backgrounds), --text-on-dark #c9d2e3.
Fonts, self-hosted with @fontsource so they are embedded in exported PNGs: Fraunces 600/700 for headlines (the emphasized words in italic gold), Nunito Sans 400/700 for body text and buttons, Caveat 600 only for handwritten names on the nice list.
Logo: a thin six-armed snowflake icon with a gold stroke plus the wordmark "Wiadomość od Mikołaja" in Fraunces 600. Build it as an SVG component in two versions: on navy (cream text) and on cream (ink text).
Recurring motifs, drawn in SVG/CSS: falling snow dots; a garland of small bulbs in red, gold, green and cream; a red gift bow; a gold picture frame (10 px gold border, rounded corners) around film frames; the nice list (a cream paper sheet with the heading "Lista grzecznych dzieci", a handwritten name in Caveat and a red wax seal with a star); a round gold "−25%" badge rotated −8° with "KOD" under the number; pill-shaped buttons (red with white text, or gold with ink text). Buttons on ads are visual only.
Tone: warm, simple and concrete, addressed to the parent ("Twoje dziecko").
Each ad comes in two color variants: "noc" (navy background, cream text) and "papier" (cream background, ink text).

## 4. Image slots
A panel "Kadry" lets me upload images by drag and drop into named slots and set a focal point (object-position) per slot: portret (Santa portrait), dom (Santa's house at night), pracownia (workshop), ksiega (magic golden book), sanie (sleigh with reindeer), platek (Płatek, a young reindeer), kula (Santa with a snow globe). Each ad has a default slot, which I can change per ad.

## 5. Formats
Render every ad at its exact native size and show it scaled down in the interface.
- meta-1x1: 1080×1080 (Facebook/Instagram feed)
- meta-4x5: 1080×1350 (Facebook/Instagram feed)
- meta-9x16: 1080×1920 (Stories/Reels): no text or buttons in the top 270 px and the bottom 380 px
- google-191: 1200×628 (Google Demand Gen / Display)
- google-1x1: 1200×1200
- google-4x5: 960×1200
- logo-1x1: 1200×1200 and logo-4x1: 1200×300 (logo only, for Google)
Layouts must adapt to each aspect ratio instead of just scaling: in 1200×628 the text sits on the left and the framed image on the right; in 9:16 the image fills the upper part and the text block sits in the safe middle area. Minimum text size on 1080-wide formats: 28 px. Text contrast at least 4.5:1.

## 6. Variables
A panel "Zmienne" edits values used in copy: [DATA STARTU], [DATA KOŃCA RABATU], [OSTATNI TERMIN], [ADRES STRONY], price (49 zł), sibling price (15 zł). Any placeholder still in square brackets is highlighted on the ad and in the gallery with a red badge "Uzupełnij zmienne".

## 7. What to build in this first version
- The design system above, the logo component and the nice list, badge, garland, bow and frame components.
- Two concepts in meta-1x1, meta-4x5 and meta-9x16, each in "noc" and "papier":
  A1 "Po imieniu" (slot portret). Headline: „Mikołaj powie do Twojego dziecka po imieniu” with "po imieniu" in italic gold. Subline: „Zapisz się przed startem, a dostaniesz kod −25% na pierwszy film.” Gold −25% badge. Button: „Zapisz się po kod −25%”.
  B1 "Po imieniu" (slot portret). Headline: „Kiedy Mikołaj mówi do Ciebie po imieniu…” with "po imieniu" in italic gold. Subline: „Spersonalizowany film na Święta. Link mailem w 24 godziny.” Button: „Zamów film – 49 zł”.
  Every ad shows the logo small in a corner.
- A gallery page "Reklamy" grouped by campaign and concept, with filters for campaign, format and color variant. Each tile shows the scaled preview, the size, the file name and a button „Pobierz PNG”.
- An editor: clicking a tile opens the ad fitted to the screen with a side panel: headline, subline and button text (editable, saved per ad, with a button „Przywróć tekst z pakietu”), slot choice, focal point, color variant, a toggle for the safe-zone overlay in 9:16 (overlay never exported) and a toggle for a small fine print „Film powstaje z pomocą narzędzi sztucznej inteligencji” (off by default).
- PNG export: render the native-size node off-screen, wait for document.fonts.ready and image decoding, export with html-to-image (pixelRatio 1, exact width and height). File names: A1_po-imieniu_meta-1x1_noc.png.
- Keep all content (brand tokens, formats, concepts and copy) in one file, src/data/pakiet.ts, so I can edit it in one place.
- An accessible interface: labels for all fields, visible keyboard focus.
```

## Prompt 2: wszystkie koncepcje i formaty

```text
Add the remaining concepts to src/data/pakiet.ts and the gallery. Use the Polish copy verbatim. Every concept comes in "noc" and "papier".

Campaign A "Przed startem" (button on image: „Zapisz się po kod −25%”):
- A2 "Lista grzecznych dzieci" (slot pracownia + nice list with the handwritten name „Kasia”). Headline: „Imię Twojego dziecka na liście grzecznych dzieci”. Subline: „Start [DATA STARTU]. Zapisani dostają kod −25%.”
- A3 "Wkrótce start" (slot dom). Headline: „Mikołaj szykuje już wiadomości na te Święta”. Subline: „Start [DATA STARTU]. Zapisz się, a kod −25% przyjdzie mailem.”

Campaign B "Sprzedaż" (button on image: „Zamów film – 49 zł” unless stated otherwise):
- B2 "Mikołaj wie" (slot ksiega). Headline: „Mikołaj wie, czego Twoje dziecko nauczyło się w tym roku”. Subline: „Imię, osiągnięcie i zdjęcie w magicznej księdze.”
- B3 "Jak to działa": a carousel of 4 cards, only in meta-1x1 and meta-4x5, with one garland running continuously across the card edges. Card 1: „Wypełniasz formularz” – „Imię, wiek, zdjęcie i kilka zdań o dziecku. Około 5 minut.” Card 2 (slot pracownia): „Mikołaj nagrywa film” – „Mówi po imieniu i chwali to, co się udało.” Card 3: „Link mailem w 24 godziny” – „Film zostaje u Ciebie na zawsze.” Card 4: „Film od Mikołaja – 49 zł” – „+15 zł za każde kolejne dziecko”, with the button. Big step numbers 1–3 in red circles with a gold ring.
- B4 "Rodzeństwo" (nice list with the handwritten names „Zosia” and „Antek”). Headline: „Jeden film dla całej gromadki”. Subline: „+15 zł za każde kolejne dziecko z rodzeństwa.”
- B5 "Ostatnia chwila" (slot sanie). Headline: „Zdążysz przed Wigilią”. Subline: „Film w ciągu 24 godzin. Zamów do [OSTATNI TERMIN].” Add a red ribbon banner across a corner.
- B6 "Remarketing" (slot kula). Headline: „Mikołaj czeka na imię Twojego dziecka”. Subline: „Wystarczy kilka minut, a link do filmu przyjdzie mailem w 24 godziny.” Button: „Dokończ zamówienie”.

Output matrix:
- A1, A2, A3, B1, B2, B4, B5, B6 in meta-1x1, meta-4x5 and meta-9x16.
- A1, B1, B2 and B5 also in google-191, google-1x1 and google-4x5.
- B3 as 4 cards in meta-1x1 and meta-4x5.
- The logo in logo-1x1 and logo-4x1, on navy and on cream.
Show the total number of files in the gallery header.
```

## Prompt 3: pakiet ZIP i arkusz tekstów

```text
Add the export of the whole package and a copy sheet.

1. A page "Teksty reklam" with the text fields that go into Meta Ads Manager and Google Ads (not on the image). Show them as tables with a copy button per field and a live character counter that turns red above the limit (Meta: headline 40, description 30; Google: short headline 30, long headline 90, description 90, business name 25). Use this Polish copy verbatim:

Meta, campaign A (A1–A3):
- Tekst główny: „Mikołaj nagra film, w którym zwróci się do Twojego dziecka po imieniu i pochwali je za ten rok. Zapisz się przed startem: w dniu startu dostaniesz kod −25% na pierwszy film.”
- Nagłówek: „Kod −25% dla zapisanych”
- Opis: „Start [DATA STARTU]”
- Przycisk: „Zarejestruj się”
Meta, B1 and B2:
- Tekst główny: „Spersonalizowany film na Święta: Mikołaj mówi do Twojego dziecka po imieniu, chwali jego tegoroczne osiągnięcie i pokazuje zdjęcie w magicznej księdze. Wypełniasz formularz w 5 minut, a link do filmu dostajesz mailem w 24 godziny.”
- Nagłówek: „Film od Mikołaja – 49 zł”
- Opis: „Link mailem w 24 godziny”
- Przycisk: „Zamów teraz”
Meta, B3:
- Tekst główny: „Trzy kroki do filmu od Mikołaja: formularz, nagranie i link mailem w 24 godziny.”
- Nagłówek: „Film od Mikołaja – 49 zł”
- Opis: „Link mailem w 24 godziny”
- Przycisk: „Zamów teraz”
Meta, B4:
- Tekst główny: „Rodzeństwo w jednym filmie: Mikołaj zwraca się do każdego dziecka po imieniu, pokazuje wszystkie zdjęcia i wpisuje wszystkie imiona na listę grzecznych dzieci.”
- Nagłówek: „+15 zł za każde kolejne dziecko”
- Opis: „Jeden film dla całej gromadki”
- Przycisk: „Zamów teraz”
Meta, B5:
- Tekst główny: „Zamów do [OSTATNI TERMIN], a film od Mikołaja dotrze mailem przed Wigilią. Przygotujemy go w ciągu 24 godzin.”
- Nagłówek: „Zdążysz przed Wigilią”
- Opis: „Film w 24 godziny”
- Przycisk: „Zamów teraz”
Meta, B6:
- Tekst główny: „Film od Mikołaja dla Twojego dziecka czeka na dokończenie zamówienia. Wystarczy kilka minut, a link dostaniesz mailem w 24 godziny.”
- Nagłówek: „Dokończ zamówienie filmu”
- Opis: „49 zł, link w 24 godziny”
- Przycisk: „Zamów teraz”
Google (responsive ads, campaign B):
- Nazwa firmy: „Wiadomość od Mikołaja”
- Krótkie nagłówki: „Film od Mikołaja po imieniu”, „Mikołaj mówi po imieniu”, „Film od Mikołaja – 49 zł”, „Link mailem w 24 godziny”, „Zdążysz przed Wigilią”
- Długi nagłówek: „Spersonalizowany film, w którym Mikołaj mówi do Twojego dziecka po imieniu”
- Teksty reklamy: „Mikołaj chwali osiągnięcia dziecka i pokazuje jego zdjęcie w magicznej księdze.”, „Wypełnij formularz w 5 minut, a link do filmu dostaniesz mailem w 24 godziny.”, „Rodzeństwo w jednym filmie: +15 zł za każde kolejne dziecko.”, „Zamów do [OSTATNI TERMIN], a film od Mikołaja dotrze mailem przed Wigilią.”

2. A button „Pobierz cały pakiet (ZIP)” using jszip and file-saver. Show a progress bar while rendering. ZIP structure:
- A_przed-startem/meta/…png
- B_sprzedaz/meta/…png (carousel cards as B3_jak-to-dziala_karta-1_meta-1x1_noc.png and so on)
- B_sprzedaz/google/…png
- logo/…png
- teksty_meta.csv and teksty_google.csv (UTF-8 with BOM, semicolon separator, so Excel shows Polish letters)
- CZYTAJ.txt with the list of files, the landing page for each campaign and this note: „Kadry z filmu powstały z pomocą narzędzi AI. Jeśli Meta tego wymaga, zaznacz informację o AI przy publikacji reklamy.”
3. Before exporting, check all ads and texts for placeholders still in square brackets. If there are any, show the list and ask for confirmation („Pobierz mimo to” / „Uzupełnij zmienne”).
4. Verify that every PNG in the ZIP has exactly the format size and that Polish letters (ą ę ć ł ń ó ś ź ż) render in Fraunces, Nunito Sans and Caveat.
```

## Prompt 4 (opcjonalny): klasyczne banery Google

```text
Add classic Google Display banners for B1 and B5 in "noc" only: 300×250, 336×280, 728×90, 300×600 and 320×100. In banners up to 100 px high, show only the logo icon, the headline and the button, without the subline. Keep the 28 px minimum only for 1080-wide formats; in banners use at least 14 px. Add them to the ZIP under B_sprzedaz/google-banery/.
```

---

## Wiedza o projekcie (do Project Knowledge w Lovable)

```text
Product: "Wiadomość od Mikołaja", personalized Christmas videos from Santa for Polish children, sold to parents. All ad copy is Polish and must be used verbatim from src/data/pakiet.ts.
Rules: Santa is real (children may see the ads), never suggest otherwise. No images of children or other people, no AI-generated images, no cartoon Santa: only uploaded film frames and SVG/CSS decorations. No ratings, reviews, customer counts or invented numbers. No crossed-out or "was/now" prices; the pre-launch discount is "kod −25% dla zapisanych". No text baked into images.
Brand: navy #0e1726, gold #e3a948, red #a3222b, cream #f5ecdc, ink #2b1f14. Fraunces for headlines, Nunito Sans for text, Caveat only for handwritten names. Motifs: snow, bulb garland, red bow, gold frame, nice list with a wax seal, round gold −25% badge.
Export: exact pixel sizes, fonts self-hosted with @fontsource, Meta 9:16 safe zones (270 px top, 380 px bottom).
```
