# Tekst Mikołaja w Rails (scena 3): uzgodnienia

Data: 2026-11-14. Gałąź `generate-speech` (repo główne i `app/`).

## Decyzje

- **Tekst pisze Rails, nie Python.** Prompt i reguły przeniesione z `generator/order.py` i `generator/prompts.py` do `app/app/services/orders/`, potem rozwinięte (JSON, niżej): `SpeechPrompt` (jedyne źródło promptu), `SpeechChecker` (automatyczne uwagi), `GenerateSpeech` (wywołanie modelu), `SpeechConfig` (provider i model).
- **Python zamrożony.** `generator.order text` i `SPEECH_*` zostają awaryjnie do karty 6.3 (zapis tekstu w Rails), potem je usuwamy. Zmian promptu, w tym karty 1.5, nie robimy już w Pythonie.
- **Serwis, nie job.** `Orders::GenerateSpeech.call(order)` zwraca `{ text:, issues: }`, wołany ręcznie z konsoli. Nic nie zapisuje, nie zmienia statusu, nie tworzy `OrderEvent`. Job dojdzie w 6.3.
- **Model.** RubyLLM, `MIKOLAJ_TEXT_PROVIDER` (`gemini` domyślnie albo `anthropic`) i `MIKOLAJ_TEXT_MODEL` (domyślnie `gemini-3.8-flash` / `claude-sonnet-5-5`), `assume_model_exists: true`. Klucze tylko z płatnego planu API.
- **Dane jako JSON.** Dzieci idą do modelu w bloku JSON z opisowymi kluczami (`zwrot_w_wolaczu`, `osiagniecie_z_tego_roku`, `czy_prezent_kupiony`: `TAK` / `NIE`, brak danych to `null`). Nowa linia wpisana przez rodzica zostaje wewnątrz wartości i nie udaje reguły promptu.
- **Odpowiedź jako JSON.** Schemat `SpeechPrompt::RESPONSE_SCHEMA`: `text`, `needs_review`, `review_reason`. Zamiast umownego „DO SPRAWDZENIA” mamy flagę i powód dla kolejki przeglądu.
- **Zdanie końcowe dokleja kod.** Model pisze tekst bez niego (zakres słów w prompcie pomniejszony o 8 słów zdania końcowego), serwis usuwa je, jeśli model i tak je napisał, i dokleja własne.
- **Checker zostaje.** Samoocenie modelu nie ufamy; `SpeechChecker` sprawdza gotowy tekst (później także tekst poprawiony przez człowieka).

## Logowanie

| Co | Gdzie |
|---|---|
| Tekst i uwagi | tylko wartość zwrócona do wywołującego (terminal konsoli) |
| Metadane | `Rails.logger.info`, linia `[speech]`: numer zamówienia, provider, model, liczba słów, kody uwag, czas; przy błędzie klasa błędu. Dev: `log/development.log`, produkcja: STDOUT kontenera (`kamal app logs`) |
| RubyLLM | wbudowany logger na `WARN` (na `DEBUG` loguje pełne żądania), `redact_error_messages = true` |

## Pułapki portu

- `\w` w Ruby jest ASCII, więc słowa liczymy `[[:word:]]+`.
- Twarde spacje (NBSP) od modelu: `[[:space:]]` zamiast `\s` w regułach i przy obcinaniu.
- Zwrot z formularza może mieć spacje na końcu: obcinamy go w prompcie i w checkerze.
- Prompt celowo różni się od Pythona (JSON, zdanie końcowe), więc wzorce zgodności z `build_prompt` usunięte.
