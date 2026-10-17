"""Materiały do jednego zamówienia: tekst Mikołaja (scena 3) i jego nagranie.

Przykłady:
    python -m generator.order text examples/zamowienie_kasia.json
    # przeczytaj i ewentualnie popraw output/orders/<id>/tekst.txt
    python -m generator.order voice examples/zamowienie_kasia.json --approved

Gotowe MP3 wgrywasz do HeyGen (Photo Avatar, Avatar IV) jako źródło dźwięku.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from . import config, prompts
from .audio import speak
from .common import google_client, with_retry


def load_order(path: str) -> dict:
    order = json.loads(Path(path).read_text(encoding="utf-8"))
    if not order.get("id") or not order.get("dzieci"):
        sys.exit("Zamówienie musi mieć pola 'id' i 'dzieci' (lista co najmniej jednego dziecka).")
    return order


def order_dir(order: dict) -> Path:
    return config.ORDERS_DIR / str(order["id"])


def _child_data(child: dict) -> str:
    bought = child.get("prezent_kupiony")
    return prompts.CHILD_DATA.format(
        zwrot=child["zwrot"],
        plec=child["plec"],
        wiek=child["wiek"],
        osiagniecie=child["osiagniecie"],
        zainteresowania=child["zainteresowania"],
        do_poprawy=child.get("do_poprawy") or "brak",
        prezent=child.get("prezent") or "brak",
        prezent_kupiony="TAK" if bought else "NIE",
    )


def word_range(order: dict) -> tuple[int, int]:
    return (90, 110) if len(order["dzieci"]) == 1 else (110, 130)


def build_prompt(order: dict) -> str:
    children = order["dzieci"]
    min_words, max_words = word_range(order)
    if len(children) == 1:
        return prompts.SPEECH_PROMPT.format(
            adresat="dziecka",
            adresat_dop="dziecka",
            dane=_child_data(children[0]),
            min_words=min_words,
            max_words=max_words,
            seconds="40–45",
            needs_review=prompts.NEEDS_REVIEW,
            closing=prompts.SPEECH_CLOSING,
        )
    data = "\n\n".join(f"Dziecko {i}:\n{_child_data(c)}" for i, c in enumerate(children, 1))
    return prompts.SPEECH_PROMPT.format(
        adresat="rodzeństwa (mówisz do wszystkich dzieci naraz)",
        adresat_dop="każdego dziecka",
        dane=data,
        min_words=min_words,
        max_words=max_words,
        seconds="50–55",
        needs_review=prompts.NEEDS_REVIEW,
        closing=prompts.SPEECH_CLOSING,
    )


def check_speech(text: str, order: dict) -> list[str]:
    """Automatyczne uwagi do tekstu. Nie zastępują czytania przez człowieka."""
    if prompts.NEEDS_REVIEW in text:
        return [f"Model zwrócił {prompts.NEEDS_REVIEW}: sprawdź dane od rodzica."]
    issues = []
    words = len(re.findall(r"\w+", text))
    min_words, max_words = word_range(order)
    if not min_words <= words <= max_words:
        issues.append(f"Liczba słów {words} poza zakresem {min_words}–{max_words}.")
    for child in order["dzieci"]:
        if child["zwrot"] not in text:
            issues.append(f"Brak zwrotu „{child['zwrot']}” w tekście.")
    if not text.rstrip().endswith(prompts.SPEECH_CLOSING):
        issues.append(f"Tekst nie kończy się zdaniem: „{prompts.SPEECH_CLOSING}”.")
    for child in order["dzieci"]:
        if not child.get("prezent_kupiony") and re.search(r"elfy\s+(już\s+)?(go\s+)?(szykują|pakują)", text, re.IGNORECASE):
            issues.append("Prezent nie jest kupiony, a tekst sugeruje, że elfy go szykują.")
            break
    return issues


def apply_pronunciation(text: str, order: dict) -> str:
    """Podmienia słowa na zapis fonetyczny tylko na potrzeby nagrania (np. Jessico -> Dzesiko).

    Klucze muszą odpowiadać formie użytej w tekście, zwykle wołaczowi z pola 'zwrot'.
    """
    for written, spoken in (order.get("wymowa") or {}).items():
        text = re.sub(rf"\b{re.escape(written)}", spoken, text)
    return text


def cmd_text(args):
    order = load_order(args.order)
    out = order_dir(order) / "tekst.txt"
    if out.exists() and not args.force:
        sys.exit(f"{out} już istnieje (użyj --force, żeby wygenerować od nowa).")
    client = google_client()
    response = with_retry(lambda: client.models.generate_content(model=config.TEXT_MODEL, contents=build_prompt(order)))
    text = (response.text or "").strip()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nZapisano: {out}")
    issues = check_speech(text, order)
    for issue in issues:
        print(f"  ! {issue}")
    print("\nPrzeczytaj tekst (w MVP każdy tekst zatwierdza człowiek), popraw w pliku i uruchom:")
    print(f"  python -m generator.order voice {args.order} --approved")


def cmd_voice(args):
    if not args.approved:
        sys.exit("Najpierw przeczytaj i zatwierdź tekst, potem uruchom z flagą --approved.")
    order = load_order(args.order)
    directory = order_dir(order)
    text_path = directory / "tekst.txt"
    if not text_path.exists():
        sys.exit(f"Brak {text_path}. Uruchom najpierw: python -m generator.order text {args.order}")
    text = text_path.read_text(encoding="utf-8").strip()
    if prompts.NEEDS_REVIEW in text:
        sys.exit(f"Tekst zawiera {prompts.NEEDS_REVIEW}: wyjaśnij dane z rodzicem.")
    speak(apply_pronunciation(text, order), directory / "glos.mp3")
    print("Odsłuchaj imię. Jeśli brzmi źle, dodaj zapis fonetyczny w polu 'wymowa' i powtórz.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Tekst i głos dla zamówienia")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("text", help="wygeneruj tekst Mikołaja (krok 2 produkcji)")
    p.add_argument("order", help="plik JSON zamówienia")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_text)

    p = sub.add_parser("voice", help="nagraj zatwierdzony tekst (krok 3 produkcji)")
    p.add_argument("order")
    p.add_argument("--approved", action="store_true", help="potwierdzam, że tekst został przeczytany")
    p.set_defaults(func=cmd_voice)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
