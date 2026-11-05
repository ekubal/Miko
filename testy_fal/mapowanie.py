"""Dopasowanie naszych parametrów do schematu wejścia modelu na fal (OpenAPI).

Każdy model na fal nazywa pola inaczej (image_url, start_image_url, first_frame_image_url…)
i przyjmuje inne wartości (duration "5"/"10" albo liczba 3–15, resolution "768P" albo "1080p").
Zamiast wpisywać to ręcznie dla każdego modelu, czytamy jego schemat i dobieramy:
- nazwę pola z listy kandydatów (CANDIDATES), chyba że modele.py podaje ją wprost;
- wartość najbliższą zamówionej, jeśli pole ma listę dozwolonych wartości.
Wszystkie zmiany (np. 8 s -> 10 s) trafiają do notatek, które widać przed wysłaniem.
"""

import re

# Logiczne nazwy naszych parametrów -> możliwe nazwy pól w modelach na fal (w kolejności).
CANDIDATES = {
    "prompt": ["prompt"],
    "image": ["image_url", "start_image_url", "first_frame_image_url", "first_frame_url", "first_image_url"],
    "end_image": ["end_image_url", "tail_image_url", "last_frame_image_url", "last_image_url", "end_frame_url"],
    "references": ["reference_image_urls", "image_urls", "reference_images", "references", "input_image_urls"],
    "duration": ["duration", "duration_seconds", "num_seconds", "seconds", "video_length"],
    "resolution": ["resolution", "video_resolution"],
    "aspect_ratio": ["aspect_ratio"],
    "negative_prompt": ["negative_prompt"],
    # Wyłączamy: dźwięk dodaje montaż, a "ulepszanie" promptu potrafi dopisać rzeczy,
    # których nie chcemy (np. dzieci) i zaciera porównanie modeli.
    "audio": ["generate_audio", "enable_audio", "with_audio", "audio"],
    "prompt_expansion": ["enable_prompt_expansion", "prompt_optimizer", "expand_prompt", "enhance_prompt"],
}

LABELS = {
    "prompt": "prompt",
    "image": "kadr startowy",
    "end_image": "kadr końcowy",
    "references": "obrazy referencyjne",
    "duration": "długość",
    "resolution": "rozdzielczość",
    "aspect_ratio": "proporcje",
    "negative_prompt": "negative prompt",
    "audio": "wyłączenie dźwięku",
    "prompt_expansion": "wyłączenie ulepszania promptu",
}

# Bez tych pól test nie ma sensu: lepiej przerwać niż wysłać zapytanie bez kadru.
ESSENTIAL = {"prompt", "image", "references"}
# Dodatki: ich brak widać w `sprawdz`, w planie generowania tylko by zaśmiecał uwagi.
QUIET = {"end_image", "aspect_ratio", "negative_prompt", "audio", "prompt_expansion"}

NEGATIVE_PROMPT = (
    "children, kids, toddlers, text, letters, captions, logos, watermark, "
    "curled mustache, visible mouth, lip movement, talking, scene cut"
)


class MappingError(Exception):
    pass


def resolve(schema: dict, components: dict) -> dict:
    """Rozwija odwołania $ref do components/schemas."""
    seen = 0
    while isinstance(schema, dict) and "$ref" in schema and seen < 20:
        schema = components.get(schema["$ref"].rsplit("/", 1)[-1], {})
        seen += 1
    return schema if isinstance(schema, dict) else {}


def input_schema(openapi: dict) -> tuple[dict, list[str], dict]:
    """Zwraca (pola, wymagane, components) schematu wejścia z OpenAPI kolejki fal."""
    components = openapi.get("components", {}).get("schemas", {})
    body = None
    for operations in openapi.get("paths", {}).values():
        post = operations.get("post") if isinstance(operations, dict) else None
        content = (post or {}).get("requestBody", {}).get("content", {})
        if "application/json" in content:
            body = content["application/json"].get("schema")
            break
    if body is None:
        names = [name for name in components if name.endswith("Input")]
        if names:
            body = {"$ref": f"#/components/schemas/{names[0]}"}
    if body is None:
        raise MappingError("Nie znalazłem schematu wejścia w OpenAPI modelu.")

    props: dict = {}
    required: set[str] = set()

    def merge(schema):
        schema = resolve(schema, components)
        for sub in schema.get("allOf", []):
            merge(sub)
        props.update(schema.get("properties", {}))
        required.update(schema.get("required", []))

    merge(body)
    if not props:
        raise MappingError("Schemat wejścia modelu nie ma żadnych pól.")
    return props, sorted(required), components


def field_info(prop: dict, components: dict) -> dict:
    """Typy, dozwolone wartości, zakres i wartość domyślna pola (z anyOf/oneOf/allOf i $ref)."""
    info = {"types": set(), "enum": [], "minimum": None, "maximum": None, "default": None, "description": ""}

    def walk(schema):
        schema = resolve(schema, components)
        for key in ("anyOf", "oneOf", "allOf"):
            for sub in schema.get(key, []):
                walk(sub)
        kind = schema.get("type")
        if isinstance(kind, list):
            info["types"].update(kind)
        elif kind:
            info["types"].add(kind)
        for value in [*schema.get("enum", []), *([schema["const"]] if "const" in schema else [])]:
            if value is not None and value not in info["enum"]:
                info["enum"].append(value)
        for key in ("minimum", "maximum", "default"):
            if key in schema and info[key] is None:
                info[key] = schema[key]
        if schema.get("description") and not info["description"]:
            info["description"] = schema["description"]

    walk(prop)
    info["types"].discard("null")
    if not info["types"] and info["enum"]:
        info["types"] = {"string" if isinstance(v, str) else "number" for v in info["enum"]}
    return info


def number(value) -> float | None:
    """Liczba z wartości typu 8, "8", "8s", "10 sekund"."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def height(value) -> float | None:
    """Wysokość obrazu z nazwy rozdzielczości: "1080p" -> 1080, "4K" -> 2160, "768P" -> 768."""
    text = str(value).strip().lower()
    named = {"4k": 2160, "2k": 1440, "1k": 1080, "uhd": 2160, "fhd": 1080, "full_hd": 1080, "hd": 720, "sd": 480}
    if text in named:
        return named[text]
    match = re.fullmatch(r"(\d{3,4})p?", text)
    return float(match.group(1)) if match else None


def nearest(options: list, target: float, key) -> object | None:
    """Wartość z listy najbliższa celowi; przy remisie większa (dłuższe ujęcie, lepsza jakość)."""
    scored = [(abs(k - target), -k, option) for option in options if (k := key(option)) is not None]
    return min(scored, key=lambda s: (s[0], s[1]))[2] if scored else None


def coerce_duration(info: dict, seconds: float):
    if info["enum"]:
        return nearest(info["enum"], seconds, number)
    value = seconds
    if info["minimum"] is not None:
        value = max(value, info["minimum"])
    if info["maximum"] is not None:
        value = min(value, info["maximum"])
    if "string" in info["types"] and not info["types"] & {"integer", "number"}:
        return f"{value:g}"
    return int(value) if "integer" in info["types"] or float(value).is_integer() else value


def coerce_resolution(info: dict, resolution: str):
    if info["enum"]:
        for option in info["enum"]:
            if str(option).lower() == resolution.lower():
                return option
        target = height(resolution)
        return nearest(info["enum"], target, height) if target else None
    return resolution if "string" in info["types"] or not info["types"] else None


def coerce_aspect(info: dict, aspect: str):
    if info["enum"]:
        return aspect if aspect in info["enum"] else None
    return aspect


def coerce_false(info: dict, _value):
    return False if "boolean" in info["types"] else None


def coerce_references(info: dict, urls: list[str]):
    if "array" in info["types"] or not info["types"]:
        return list(urls)
    return urls[0] if "string" in info["types"] else None


def coerce_text(info: dict, value: str):
    return value if "string" in info["types"] or not info["types"] else None


COERCE = {
    "prompt": coerce_text,
    "image": coerce_text,
    "end_image": coerce_text,
    "references": coerce_references,
    "duration": coerce_duration,
    "resolution": coerce_resolution,
    "aspect_ratio": coerce_aspect,
    "negative_prompt": coerce_text,
    "audio": coerce_false,
    "prompt_expansion": coerce_false,
}


def choose_field(logical: str, props: dict, overrides: dict) -> str | None:
    if logical in overrides:
        return overrides[logical]
    return next((name for name in CANDIDATES[logical] if name in props), None)


def build_payload(
    props: dict,
    required: list[str],
    components: dict,
    wanted: dict,
    overrides: dict | None = None,
    fixed: dict | None = None,
) -> tuple[dict, list[str], float | None]:
    """Buduje zapytanie dla modelu. Zwraca (payload, notatki, sekundy klipu).

    `wanted` to nasze parametry pod logicznymi nazwami (klucze CANDIDATES); wartości None
    są pomijane. W prompcie znacznik {seconds} zamieniamy na długość, którą model dostanie.
    """
    overrides = overrides or {}
    payload: dict = {}
    notes: list[str] = []
    used: dict[str, str] = {}
    for logical, value in wanted.items():
        if value is None or value == []:
            continue
        name = choose_field(logical, props, overrides)
        if name is None:
            if logical in ESSENTIAL and logical not in overrides:
                raise MappingError(
                    f"Model nie ma pola na {LABELS[logical]}. Pola modelu: {', '.join(sorted(props))}.\n"
                    f"Wpisz właściwą nazwę w testy_fal/modele.py (fields={{'{logical}': '...'}})."
                )
            if logical not in overrides and logical not in QUIET:
                notes.append(f"brak pola na {LABELS[logical]}, pomijam")
            continue
        if name not in props:
            notes.append(f"pole {name} z modele.py nie występuje w schemacie, wysyłam mimo to")
        info = field_info(props.get(name, {}), components)
        coerced = COERCE[logical](info, value)
        if coerced is None:
            allowed = f" (dozwolone: {', '.join(map(str, info['enum']))})" if info["enum"] else ""
            notes.append(f"{LABELS[logical]}: wartość {value} nie pasuje do pola {name}{allowed}, pomijam")
            continue
        if logical in ("duration", "resolution") and str(coerced).lower() != str(value).lower():
            notes.append(f"{LABELS[logical]}: {value} -> {coerced}")
        payload[name] = coerced
        used[logical] = name

    for name, value in (fixed or {}).items():
        payload[name] = value

    missing = [name for name in required if name not in payload]
    if missing:
        raise MappingError(
            f"Brakuje wymaganych pól: {', '.join(missing)}. Dopisz je w testy_fal/modele.py "
            "(fixed={...}) albo wskaż ich nazwę w fields={...}."
        )

    seconds = None
    if "duration" in used:
        seconds = number(payload[used["duration"]])
    else:
        default = None
        for name in CANDIDATES["duration"]:
            if name in props:
                default = number(field_info(props[name], components)["default"])
                break
        seconds = default
        notes.append(
            "model nie ma pola długości, " + (f"domyślnie {seconds:g} s" if seconds else "długość domyślna modelu")
        )

    if "prompt" in used:
        prompt_seconds = seconds or number(wanted.get("duration")) or 8
        payload[used["prompt"]] = payload[used["prompt"]].replace("{seconds}", f"{prompt_seconds:g}")
    return payload, notes, seconds


def find_video_url(result) -> str | None:
    """Adres pliku wideo z odpowiedzi modelu (zwykle {"video": {"url": ...}})."""
    if isinstance(result, dict):
        video = result.get("video")
        if isinstance(video, dict) and isinstance(video.get("url"), str):
            return video["url"]
        if isinstance(video, str) and video.startswith("http"):
            return video
        for value in result.values():
            if url := find_video_url(value):
                return url
    elif isinstance(result, list):
        for value in result:
            if url := find_video_url(value):
                return url
    elif isinstance(result, str) and result.startswith("http") and re.search(r"\.(mp4|mov|webm)(\?|$)", result):
        return result
    return None


def describe_fields(props: dict, required: list[str], components: dict) -> list[str]:
    """Czytelna lista pól modelu do polecenia `sprawdz`."""
    lines = []
    for name in sorted(props):
        info = field_info(props[name], components)
        parts = ["/".join(sorted(info["types"])) or "?"]
        if info["enum"]:
            values = ", ".join(map(str, info["enum"][:12])) + (" …" if len(info["enum"]) > 12 else "")
            parts.append(f"wartości: {values}")
        if info["minimum"] is not None or info["maximum"] is not None:
            parts.append(f"zakres: {info['minimum']}–{info['maximum']}")
        if info["default"] is not None:
            parts.append(f"domyślnie: {info['default']}")
        mark = " *" if name in required else ""
        lines.append(f"  {name}{mark}: {'; '.join(parts)}")
    return lines
