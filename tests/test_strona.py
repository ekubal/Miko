"""Strona sprzedażowa (strona/): spójność z generatorem i brak pozostałości po projekcie z kanwy."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "strona"
PAGES = ["index.html", "zamowienie.html", "potwierdzenie.html", "404.html", "regulamin.html", "faq.html", "kontakt.html", "polityka-prywatnosci.html", "zapisy.html"]
# Strony i pliki, które trzeba dopiero dodać (opisane w strona/README.md).
TODO_TARGETS = {"media/przyklad.mp4", "media/przyklad.jpg", "media/zwiastun.mp4", "media/zwiastun.jpg"}


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


def test_legal_pages_are_built_from_markdown():
    # Po zmianie dokumenty/*.md uruchom: python dokumenty/zbuduj.py
    import importlib.util

    spec = importlib.util.spec_from_file_location("zbuduj", ROOT / "dokumenty" / "zbuduj.py")
    zbuduj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(zbuduj)
    for slug in zbuduj.PAGES:
        meta, body = zbuduj.front_matter((ROOT / "dokumenty" / f"{slug}.md").read_text(encoding="utf-8"))
        page = (SITE / f"{slug}.html").read_text(encoding="utf-8")
        for anchor, label in zbuduj.toc(body):
            assert f'href="#{anchor}"' in page and f'id="{anchor}"' in page, (slug, anchor)


def test_legal_texts_follow_product_rules():
    for slug in ("regulamin", "polityka-prywatnosci"):
        text = (ROOT / "dokumenty" / f"{slug}.md").read_text(encoding="utf-8").lower()
        assert "fikcyj" not in text, slug
        assert "sztucznej inteligencji" in text, slug
        assert "7 dni" in text, slug


def test_redirects_lead_to_existing_pages():
    # Tryb przed startem: każda reguła prowadzi ze strony, która istnieje, na stronę, która istnieje.
    rules = [line.split() for line in (SITE / "_redirects").read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    assert rules, "brak reguł w _redirects"
    for source, target, status in rules:
        assert status in {"301", "302"}, source
        for path in (source, target):
            name = path.strip("/") or "index.html"
            if "." not in name:
                name += ".html"
            assert (SITE / name).exists(), f"_redirects: brak strony {path}"


def test_signup_page_has_form_and_consent():
    page = parse("zapisy.html")
    ids = set(page.ids)
    assert {"zapis", "zapis-formularz", "email-zapis", "zgoda-zapis", "zapis-wyslano"} <= ids
    form = next(a for a in page.attrs if a.get("id") == "zapis-formularz")
    assert "data-endpoint" in form
    text = (SITE / "zapisy.html").read_text(encoding="utf-8")
    assert "sztucznej inteligencji" in text
    assert "polityka-prywatnosci.html" in text


def test_order_form_has_discount_code():
    page = parse("zamowienie.html")
    form = next(a for a in page.attrs if a.get("id") == "zamowienie")
    assert "data-endpoint-kod" in form
    assert "kod-rabatowy" in page.ids
    script = (SITE / "js" / "zamowienie.js").read_text(encoding="utf-8")
    assert "kod_rabatowy:" in script


def test_email_templates_are_email_safe():
    for path in sorted((ROOT / "szablony").glob("email_*.html")):
        text = path.read_text(encoding="utf-8").lower()
        assert "<script" not in text and "<svg" not in text, path.name
        assert 'width="600"' in text, path.name
        # Zasada 2 z AGENTS.md: informacja o AI w mailu potwierdzającym (i w mailach do listy zapisów).
        if path.name == "email_1_potwierdzenie.html" or path.name.startswith("email_zapis_"):
            assert "sztucznej inteligencji" in text, path.name
