"""Klient kolejki fal (REST): schemat modelu, wysłanie, status, wynik, pobranie pliku.

Kolejka: POST https://queue.fal.run/<endpoint> zwraca request_id, status_url i response_url.
Zapisujemy je w dzienniku, więc przerwany test można dokończyć (`wznow`) bez płacenia drugi raz.
"""

import base64
import io
import threading
import time
from pathlib import Path

import requests

from generator import config

QUEUE_URL = "https://queue.fal.run"
OPENAPI_URL = "https://fal.ai/api/openapi/queue/openapi.json"


class FalError(RuntimeError):
    pass


def _headers() -> dict:
    return {"Authorization": f"Key {config.require_env('FAL_KEY')}"}


def _check(response: requests.Response, what: str) -> None:
    if response.status_code < 400:
        return
    hints = {
        401: "Sprawdź FAL_KEY w pliku .env (fal.ai/dashboard/keys).",
        403: "Sprawdź FAL_KEY i czy konto ma środki (fal.ai/dashboard/billing).",
        404: "Nie ma takiego modelu albo zapytania: popraw identyfikator w testy_fal/modele.py.",
        422: "Model odrzucił parametry: uruchom `python -m testy_fal sprawdz --odswiez --modele ...`.",
    }
    hint = hints.get(response.status_code, "")
    raise FalError(f"{what}: HTTP {response.status_code} {response.text[:800]}" + (f"\n{hint}" if hint else ""))


def _request(method: str, url: str, attempts: int = 4, **kwargs) -> requests.Response:
    """Zapytanie z ponawianiem przy błędach sieci i 5xx (nie przy 4xx: te trzeba poprawić)."""
    for attempt in range(1, attempts + 1):
        try:
            response = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt == attempts:
                raise FalError(f"Brak połączenia z {url}: {exc}") from exc
        else:
            if response.status_code < 500 or attempt == attempts:
                return response
        time.sleep(2 * 2 ** (attempt - 1))
    raise AssertionError("unreachable")


def fetch_schema(endpoint: str) -> dict:
    """Publiczny schemat OpenAPI modelu (nie wymaga klucza i nic nie kosztuje)."""
    response = _request("GET", OPENAPI_URL, params={"endpoint_id": endpoint}, timeout=30)
    _check(response, f"schemat {endpoint}")
    data = response.json()
    if not isinstance(data, dict) or not data.get("paths"):
        raise FalError(f"fal nie zwrócił schematu dla {endpoint} (zły identyfikator?).")
    return data


def submit(endpoint: str, payload: dict) -> dict:
    response = _request("POST", f"{QUEUE_URL}/{endpoint}", attempts=2, json=payload, headers=_headers(), timeout=120)
    _check(response, f"wysłanie do {endpoint}")
    data = response.json()
    if not all(k in data for k in ("request_id", "status_url", "response_url")):
        raise FalError(f"Nieoczekiwana odpowiedź kolejki fal: {str(data)[:500]}")
    return data


def wait(status_url: str, timeout_s: int = 1800, poll_s: float = 5, on_change=None) -> None:
    """Czeka, aż zapytanie wyjdzie z kolejki (IN_QUEUE -> IN_PROGRESS -> COMPLETED)."""
    deadline = time.time() + timeout_s
    last = None
    while True:
        response = _request("GET", status_url, headers=_headers(), timeout=60)
        _check(response, "status zapytania")
        data = response.json()
        status = data.get("status")
        if status != last and on_change:
            on_change(status, data)
        last = status
        if status == "COMPLETED":
            # Zakończone z błędem (np. odrzucony kadr) też ma status COMPLETED, z polem error.
            if data.get("error"):
                kind = f" ({data['error_type']})" if data.get("error_type") else ""
                raise FalError(f"Model zakończył z błędem{kind}: {str(data['error'])[:800]}")
            return
        if status not in ("IN_QUEUE", "IN_PROGRESS"):
            raise FalError(f"Nieznany status zapytania: {str(data)[:500]}")
        if time.time() > deadline:
            raise FalError(
                f"Brak wyniku po {timeout_s // 60} min. Zapytanie nadal jest w kolejce fal: "
                "dokończ później poleceniem `python -m testy_fal wznow`."
            )
        time.sleep(poll_s)


def result(response_url: str) -> dict:
    response = _request("GET", response_url, headers=_headers(), timeout=120)
    _check(response, "wynik zapytania")
    return response.json()


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_suffix(out.suffix + ".part")
    with _request("GET", url, stream=True, timeout=300) as response:
        _check(response, "pobieranie wideo")
        with partial.open("wb") as handle:
            for chunk in response.iter_content(1 << 20):
                handle.write(chunk)
    partial.replace(out)


_upload_lock = threading.Lock()
_uploads: dict[tuple[str, float], str] = {}


def upload_image(path: Path) -> str:
    """Wgrywa kadr do magazynu fal (pakiet fal-client) albo, bez niego, zwraca data URI (JPEG).

    Wysyłamy wyłącznie wygenerowane kadry i portrety Mikołaja i elfów, nigdy zdjęć dzieci.
    """
    key = (str(path.resolve()), path.stat().st_mtime)
    with _upload_lock:
        if key in _uploads:
            return _uploads[key]
        try:
            import fal_client
        except ImportError:
            url = data_uri(path)
        else:
            url = fal_client.upload_file(str(path))
        _uploads[key] = url
        return url


def data_uri(path: Path, max_side: int = 1920) -> str:
    from PIL import Image

    image = Image.open(path).convert("RGB")
    image.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
