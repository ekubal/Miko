"""Modele wideo do porównania.

Identyfikatory endpointów pochodzą ze stron modeli na fal.ai (stan XI 2026). Jeśli model
zmieni adres, `python -m testy_fal sprawdz` pokaże błąd 404: wtedy wpisz nowy identyfikator
ze strony modelu (fal.ai/models/<identyfikator>).

Ceny to szacunki z porównywarek i stron fal (IX–XI 2026), w USD za sekundę wideo.
Służą tylko do podglądu kosztu przed uruchomieniem; prawdziwe rozliczenie widać
w panelu fal (fal.ai/dashboard/usage-billing). Brak ceny = nieznana.

Pola modelu:
- endpoints: identyfikatory na fal, sprawdzane po kolei (pierwszy działający wygrywa);
- mode: "i2v" (kadr jako pierwsza klatka) albo "ref" (postacie z obrazów referencyjnych);
- ref_style: "seedance", gdy prompt odwołuje się do obrazów przez @Image1, @Image2;
- fields: ręczne nazwy pól, gdy automat (mapowanie.CANDIDATES) wybiera źle,
  np. {"image": "start_image_url"}; None wyłącza parametr, np. {"negative_prompt": None};
- fixed: stałe parametry dopisywane do każdego zapytania, np. {"cfg_scale": 0.5}.
"""

from dataclasses import dataclass, field

GOOGLE = "google"


@dataclass(frozen=True)
class Model:
    key: str
    name: str
    endpoints: tuple[str, ...]
    price: dict[str, float] = field(default_factory=dict)
    mode: str = "i2v"
    ref_style: str = "generic"
    fields: dict = field(default_factory=dict)
    fixed: dict = field(default_factory=dict)
    note: str = ""

    @property
    def is_google(self) -> bool:
        return self.endpoints == (GOOGLE,)

    def price_per_second(self, resolution) -> float | None:
        """Cena za sekundę w danej rozdzielczości; bez rozdzielczości tylko przy jednej cenie."""
        if resolution is None:
            return next(iter(self.price.values())) if len(self.price) == 1 else None
        return {k.lower(): v for k, v in self.price.items()}.get(str(resolution).lower())


MODELS: dict[str, Model] = {
    m.key: m
    for m in [
        Model(
            "omni",
            "Gemini Omni Flash (obecny, Google)",
            (GOOGLE,),
            {"360p": 0.03, "720p": 0.10, "1080p": 0.15, "4k": 0.30},
            note="punkt odniesienia; używa GEMINI_API_KEY, nie fal; ujęcia 3–10 s",
        ),
        Model(
            "h3-turbo",
            "MiniMax H3 Max Turbo",
            ("minimax/h3-max-turbo/image-to-video",),
            {"480p": 0.025, "768p": 0.04, "1080p": 0.08},
            note="połowa ceny H3 Max; ujęcia 5–15 s; kadr końcowy opcjonalny",
        ),
        Model(
            "h3-max",
            "MiniMax H3 Max",
            ("minimax/h3-max/image-to-video",),
            {"480p": 0.05, "768p": 0.08, "1080p": 0.16},
            note="ujęcia 5–15 s",
        ),
        Model(
            "h3-ref",
            "MiniMax H3 Max Reference",
            ("minimax/h3-max/reference-to-video",),
            {"480p": 0.05, "768p": 0.08},
            mode="ref",
            note="bez kadru startowego: Mikołaj (i Kardamon) z obrazów referencyjnych",
        ),
        Model(
            "kling-3",
            "Kling 3.0 Pro",
            ("fal-ai/kling-video/v3/pro/image-to-video",),
            {"1080p": 0.112},
            note="kadr w polu start_image_url; ujęcia 3–15 s",
        ),
        Model(
            "kling-4",
            "Kling 4.0",
            ("kling/v4/image-to-video", "fal-ai/kling-video/v4/image-to-video"),
            note="nowy model, cena nieznana: sprawdź na stronie modelu",
        ),
        Model(
            "seedance-2",
            "Seedance 2.0",
            ("bytedance/seedance-2.0/image-to-video",),
            {"720p": 0.30, "1080p": 0.68},
            note="ceny z dźwiękiem; bez dźwięku mogą być niższe",
        ),
        Model(
            "seedance-2-fast",
            "Seedance 2.0 Fast",
            ("bytedance/seedance-2.0/fast/image-to-video",),
            {"720p": 0.24},
        ),
        Model(
            "seedance-2-ref",
            "Seedance 2.0 Reference",
            ("bytedance/seedance-2.0/reference-to-video",),
            {"720p": 0.30},
            mode="ref",
            ref_style="seedance",
            note="do 9 obrazów referencyjnych, odwołania @Image1, @Image2 w prompcie",
        ),
        Model(
            "wan-2.6",
            "Wan 2.6",
            ("wan/v2.6/image-to-video",),
            note="najtańszy w porównaniach; cena na fal nieznana",
        ),
    ]
}

# Zestaw na pierwszy test: obecny model i trzy najmocniejsze alternatywy w podobnej cenie.
DEFAULT_MODELS = ["omni", "h3-turbo", "kling-3", "seedance-2-fast"]
