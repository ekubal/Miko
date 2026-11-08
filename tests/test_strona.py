"""Strona sprzedażowa (strona/): spójność z generatorem i brak pozostałości po projekcie z kanwy."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "strona"
PAGES = ["index.html", "zamowienie.html", "potwierdzenie.html", "404.html", "regulamin.html", "faq.html", "kontakt.html"]
# Strony i pliki, które trzeba dopiero dodać (opisane w strona/README.md).
TODO_TARGETS = {"polityka-prywatnosci.html", "media/przyklad.mp4", "media/przyklad.jpg", "pliki/regulamin.pdf"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs: list[dict] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        data["_tag"] = tag
        self.attrs.append(data)
        if "id" in data:
            self.ids.append(data["id"])


def parse(name: str) -> Collector:
    collector = Collector()
    collector.feed((SITE / name).read_text(encoding="utf-8"))
    return collector


def test_no_canvas_leftovers():
    for name in PAGES:
        text = (SITE / name).read_text(encoding="utf-8")
        assert "{{" not in text, name
        assert ".dc.html" not in text, name
        assert "support.js" not in text, name
        assert not re.search(r'(fill|stroke)="var\(', text), f"{name}: zmienne CSS w atrybutach SVG"


def test_local_links_exist():
    for name in PAGES:
        for attrs in parse(name).attrs:
            for key in ("href", "src", "data-video", "data-poster"):
                target = attrs.get(key)
                if not target or re.match(r"^(https?:|mailto:|#|data:)", target):
                    continue
                # 404.html używa ścieżek od korzenia ("/css/style.css", "/#cena").
                target = target.lstrip("/").split("#")[0] or "index.html"
                if target in TODO_TARGETS:
                    continue
                assert (SITE / target).exists(), f"{name}: brak pliku {target}"


def test_ids_are_unique():
    for name in PAGES:
        ids = parse(name).ids
        assert len(ids) == len(set(ids)), f"{name}: powtórzone id"


def test_form_fields_match_generator_order():
    example = json.loads((ROOT / "examples" / "zamowienie_kasia.json").read_text(encoding="utf-8"))
    expected = set(example["dzieci"][0])
    template = (SITE / "zamowienie.html").read_text(encoding="utf-8").split('<template id="szablon-dziecka">')[1]
    fields = set(re.findall(r'data-pole="([a-z_]+)"', template))
    assert fields == expected
    assert 'value="dziewczynka"' in template and 'value="chłopiec"' in template
    script = (SITE / "js" / "zamowienie.js").read_text(encoding="utf-8")
    for key in expected:
        assert f"{key}:" in script, f"zamowienie.js nie wysyła pola {key}"
