"""Buduje regulamin i politykę prywatności z plików Markdown w tym katalogu.

    python dokumenty/zbuduj.py

Tworzy:
- strona/regulamin.html, strona/polityka-prywatnosci.html (strony w stylu serwisu);
- dokumenty/*.docx (do poprawek prawnika, ze śledzeniem zmian);
- strona/pliki/*.pdf (do pobrania ze strony).

Wymaga programów pandoc i (dla PDF) LibreOffice. Treść zmieniaj tylko w plikach .md.
"""

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "dokumenty"
SITE = ROOT / "strona"

PAGES = {
    "regulamin": {"title": "Regulamin", "skip": "Przejdź do treści"},
    "polityka-prywatnosci": {"title": "Polityka prywatności", "skip": "Przejdź do treści"},
}

FOOTER_LINKS = [
    ("regulamin.html", "Regulamin"),
    ("polityka-prywatnosci.html", "Polityka prywatności"),
    ("faq.html", "Pytania"),
    ("kontakt.html", "Kontakt"),
]


def front_matter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, text[match.end():]


def pandoc_html(body: str) -> str:
    out = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--section-divs", "--wrap=none"],
        input=body, capture_output=True, text=True, check=True,
    ).stdout
    # Sekcje paragrafów dostają styl strony; skrót zostaje w ramce summary-box.
    out = re.sub(r'<section id="(?!skrot)([^"]+)" class="level2">', r'<section id="\1" class="legal-section">', out)
    out = out.replace('<section id="skrot" class="level2">', '<section aria-labelledby="skrot">')
    out = re.sub(r'<div class="summary-box">', '<div class="summary-box" role="note">', out)
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out)
    out = out.replace("</table>", "</table></div>")
    return out


def toc(body: str) -> list[tuple[str, str]]:
    return [(m.group(2), m.group(1)) for m in re.finditer(r"^## (.+?) \{#([^}]+)\}$", body, re.M)
            if m.group(2) != "skrot"]


def page_html(slug: str, meta: dict, content: str, items: list[tuple[str, str]]) -> str:
    title = PAGES[slug]["title"]
    toc_items = "\n".join(f'      <li><a href="#{anchor}">{html.escape(label)}</a></li>' for anchor, label in items)
    footer = "\n".join(
        f'      <a href="{href}"{" aria-current=\"page\"" if href == slug + ".html" else ""}>{label}</a>'
        for href, label in FOOTER_LINKS
    )
    note = ""
    if meta.get("projekt", "tak") != "nie":
        note = ('    <!-- Usuń po zatwierdzeniu przez prawnika: ustaw "projekt: nie" w pliku .md. -->\n'
                '    <p class="note-box note-box--legal" role="note"><strong>Projekt dokumentu.</strong> '
                'Treść czeka na sprawdzenie przez prawnika. Pola w nawiasach kwadratowych trzeba uzupełnić.</p>\n')
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – Wiadomość od Mikołaja</title>
<meta name="description" content="{html.escape(meta.get('opis', ''))}">
<meta name="theme-color" content="#0e1726">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700&display=swap">
<link rel="stylesheet" href="css/style.css">
<script src="js/cookies.js" defer></script>
</head>
<!-- Plik generowany: zmieniaj dokumenty/{slug}.md i uruchom python dokumenty/zbuduj.py -->
<body class="page-confirm page-legal">
<a class="skip-link" href="#tresc">{PAGES[slug]["skip"]}</a>

<header class="dark">
  <div class="container page-header__bar">
    <a class="brand" href="index.html">
      <svg class="icon icon--30" viewBox="0 0 24 24" fill="none" style="stroke: var(--accent)" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7M12 2l-2 2M12 2l2 2M12 22l-2-2M12 22l2-2"/></svg>
      Wiadomość od Mikołaja
    </a>
    <a class="page-header__back" href="index.html">Wróć na stronę główną</a>
  </div>
  <div class="container page-header__body">
    <h1 class="page-header__title">{title}</h1>
    <p class="subpage-hero__meta">Wersja z {meta.get('wersja', '')} · obowiązuje od {meta.get('obowiazuje', '')}</p>
  </div>
</header>

<div class="container info-layout">
  <nav class="info-side toc" aria-labelledby="spis-h">
    <h2 id="spis-h" class="toc__title">Spis treści</h2>
    <ol>
{toc_items}
    </ol>
    <a class="btn btn--outline btn--block" href="pliki/{slug}.pdf">Pobierz PDF</a>
  </nav>

  <main id="tresc" class="info-main legal">
{note}{content}
  </main>
</div>

<footer class="site-footer dark">
  <div class="container site-footer__inner">
    <p>Film powstaje z pomocą sztucznej inteligencji.</p>
    <nav class="site-footer__links" aria-label="Informacje">
{footer}
      <button type="button" class="link-button" data-cookies-ustawienia>Ustawienia cookies</button>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def build_docx(slug: str, meta: dict, body: str) -> Path:
    # Do Worda: bez ramki skrótu jako bloku stylu, tytuł i wersja na górze.
    text = f"# {PAGES[slug]['title']}\n\nWersja z {meta.get('wersja', '')}, obowiązuje od {meta.get('obowiazuje', '')}.\n\n"
    text += re.sub(r"^:::.*$", "", body, flags=re.M)
    text = re.sub(r" \{#[^}]+\}$", "", text, flags=re.M)
    out = DOCS / f"{slug}.docx"
    cmd = ["pandoc", "-f", "markdown", "-o", str(out)]
    style = DOCS / "styl.docx"
    if style.exists():
        cmd += ["--reference-doc", str(style)]
    subprocess.run(cmd, input=text, text=True, check=True)
    return out


def build_pdf(docx: Path) -> None:
    office = shutil.which("soffice") or shutil.which("libreoffice")
    if not office:
        print("  ! brak LibreOffice: pomijam PDF")
        return
    target = SITE / "pliki"
    target.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([office, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(docx)],
                       capture_output=True, check=True)
        shutil.move(str(Path(tmp) / (docx.stem + ".pdf")), target / (docx.stem + ".pdf"))


def main() -> None:
    if not shutil.which("pandoc"):
        sys.exit("Brak programu pandoc (https://pandoc.org/installing.html).")
    for slug in PAGES:
        meta, body = front_matter((DOCS / f"{slug}.md").read_text(encoding="utf-8"))
        content = "\n".join("    " + line if line else "" for line in pandoc_html(body).splitlines())
        (SITE / f"{slug}.html").write_text(page_html(slug, meta, content, toc(body)), encoding="utf-8")
        docx = build_docx(slug, meta, body)
        build_pdf(docx)
        print(f"{slug}: strona/{slug}.html, dokumenty/{slug}.docx, strona/pliki/{slug}.pdf")


if __name__ == "__main__":
    main()
