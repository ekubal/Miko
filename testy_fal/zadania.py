"""Plan i uruchamianie zadań. Jedno zadanie to jeden wariant jednego ujęcia w jednym modelu.

Każdy krok trafia do dziennika output/testy_fal/wyniki.jsonl (jedna linia JSON na zdarzenie):
start -> wyslane (z adresami kolejki fal) -> gotowe albo blad. Z niego korzystają
`wznow`, `porownaj` i `podsumowanie`.
"""

import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from generator import config

from . import fal_api, mapowanie, ujecia
from .modele import GOOGLE, Model

LOG = ujecia.OUT / "wyniki.jsonl"
SCHEMAS_DIR = ujecia.OUT / "schematy"
FILE_PREFIX = "file:"
STATUS_PL = {"IN_QUEUE": "w kolejce", "IN_PROGRESS": "generuje", "COMPLETED": "gotowe, pobieram"}

_log_lock = threading.Lock()


def rel(path: Path) -> str:
    path = Path(path)
    return str(path.relative_to(config.ROOT)) if path.is_relative_to(config.ROOT) else str(path)


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


# --- dziennik -------------------------------------------------------------------


def log_append(record: dict) -> None:
    with _log_lock:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def latest_by_job() -> dict[str, dict]:
    """Stan każdego zadania: kolejne zdarzenia z dziennika nakładane na siebie."""
    jobs: dict[str, dict] = {}
    if not LOG.exists():
        return jobs
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" in record:
            jobs.setdefault(record["id"], {}).update(record)
    return jobs


# --- schematy modeli --------------------------------------------------------------


def schema_cache_path(endpoint: str) -> Path:
    return SCHEMAS_DIR / (endpoint.replace("/", "__") + ".json")


def model_schema(model: Model, refresh: bool = False) -> tuple[str, dict]:
    """(działający identyfikator, OpenAPI) modelu; schematy są zapamiętywane w output/testy_fal/schematy/."""
    errors = []
    for endpoint in model.endpoints:
        path = schema_cache_path(endpoint)
        if path.exists() and not refresh:
            return endpoint, json.loads(path.read_text(encoding="utf-8"))
        try:
            data = fal_api.fetch_schema(endpoint)
        except fal_api.FalError as exc:
            errors.append(f"  {endpoint}: {exc}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        return endpoint, data
    raise fal_api.FalError(f"Model {model.key}: żaden identyfikator nie działa.\n" + "\n".join(errors))


# --- plan ---------------------------------------------------------------------------


@dataclass
class Job:
    shot: ujecia.Shot
    model: Model
    out: Path
    endpoint: str = GOOGLE
    payload: dict = field(default_factory=dict)  # fal; pliki lokalne jako "file:<ścieżka>"
    prompt: str = ""  # Google
    seconds: float | None = None
    resolution: str | None = None
    notes: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    @property
    def cost(self) -> float | None:
        price = self.model.price_per_second(self.resolution)
        return price * self.seconds if price is not None and self.seconds else None


def plan_job(shot: ujecia.Shot, model: Model, out: Path, resolution: str, seconds: float, schemas: dict) -> Job:
    if model.is_google:
        from generator.videos import RESOLUTIONS

        res = mapowanie.nearest(RESOLUTIONS, mapowanie.height(resolution) or 1080, mapowanie.height)
        secs = int(min(max(round(seconds), 3), 10))
        notes = [f"rozdzielczość: {resolution} -> {res}"] if res != resolution else []
        if secs != seconds:
            notes.append(f"długość: {seconds:g} -> {secs}")
        prompt = ujecia.motion_prompt(shot).replace("{seconds}", str(secs))
        return Job(shot, model, out, prompt=prompt, seconds=secs, resolution=res, notes=notes)

    endpoint, openapi = schemas[model.key]
    props, required, components = mapowanie.input_schema(openapi)
    wanted = {
        "prompt": None,
        "image": None,
        "references": None,
        "duration": seconds,
        "resolution": resolution,
        "aspect_ratio": "16:9",
        "negative_prompt": mapowanie.NEGATIVE_PROMPT,
        "audio": False,
        "prompt_expansion": False,
    }
    if model.mode == "ref":
        refs = ujecia.references(shot)
        wanted["prompt"] = ujecia.ref_prompt(shot, model.ref_style, refs)
        wanted["references"] = [FILE_PREFIX + str(p) for p in refs]
    else:
        wanted["prompt"] = ujecia.motion_prompt(shot)
        wanted["image"] = FILE_PREFIX + str(shot.frame_path)
    payload, notes, secs = mapowanie.build_payload(props, required, components, wanted, model.fields, model.fixed)

    res_field = mapowanie.choose_field("resolution", props, model.fields)
    res = payload.get(res_field) if res_field else None
    if res is None and res_field in props:
        res = mapowanie.field_info(props[res_field], components)["default"]
    return Job(
        shot, model, out, endpoint=endpoint, payload=payload, seconds=secs,
        resolution=str(res) if res is not None else None, notes=notes,
    )


# --- uruchamianie ---------------------------------------------------------------------


def materialize(value):
    """Zamienia "file:<ścieżka>" na adres wgranego pliku (rekurencyjnie w słownikach i listach)."""
    if isinstance(value, str) and value.startswith(FILE_PREFIX):
        return fal_api.upload_image(Path(value[len(FILE_PREFIX):]))
    if isinstance(value, list):
        return [materialize(v) for v in value]
    if isinstance(value, dict):
        return {k: materialize(v) for k, v in value.items()}
    return value


def fetch_result(status_url: str, response_url: str, out: Path, tag: str) -> None:
    fal_api.wait(status_url, on_change=lambda status, _data: print(f"{tag} {STATUS_PL.get(status, status)}"))
    data = fal_api.result(response_url)
    url = mapowanie.find_video_url(data)
    if not url:
        raise fal_api.FalError(f"Brak wideo w odpowiedzi modelu: {json.dumps(data, ensure_ascii=False)[:600]}")
    fal_api.download(url, out)


def run_google(job: Job) -> None:
    from generator import videos
    from generator.common import google_client

    client = google_client()
    frame = videos.upload_frame(client, job.shot.frame_path)
    job.out.parent.mkdir(parents=True, exist_ok=True)
    videos.generate_clip(client, job.prompt, frame, job.resolution, int(job.seconds), job.out)


def run_job(job: Job) -> bool:
    tag = f"[{job.shot.key}/{job.model.key}]"
    cost = job.cost
    log_append({
        "id": job.id,
        "czas": now(),
        "stan": "start",
        "ujecie": job.shot.key,
        "model": job.model.key,
        "endpoint": job.endpoint,
        "plik": rel(job.out),
        "sekundy": job.seconds,
        "rozdzielczosc": job.resolution,
        "koszt_usd": round(cost, 3) if cost is not None else None,
        "notatki": job.notes,
        "payload": job.payload or {"prompt": job.prompt},
    })
    started = time.time()
    try:
        if job.model.is_google:
            print(f"{tag} generuje (Gemini API)")
            run_google(job)
        else:
            submitted = fal_api.submit(job.endpoint, materialize(job.payload))
            log_append({
                "id": job.id,
                "stan": "wyslane",
                "request_id": submitted["request_id"],
                "status_url": submitted["status_url"],
                "response_url": submitted["response_url"],
            })
            print(f"{tag} wysłane do fal ({submitted['request_id']})")
            fetch_result(submitted["status_url"], submitted["response_url"], job.out, tag)
    except (Exception, SystemExit) as exc:  # SystemExit: błędy Gemini, których nie da się ponowić
        log_append({"id": job.id, "czas": now(), "stan": "blad", "blad": str(exc)[:1500]})
        print(f"{tag} x {exc}")
        return False
    elapsed = round(time.time() - started)
    log_append({"id": job.id, "czas": now(), "stan": "gotowe", "czas_generowania_s": elapsed})
    print(f"{tag} + {rel(job.out)} ({elapsed} s)")
    return True


def run_all(jobs: list[Job], parallel: int) -> int:
    with ThreadPoolExecutor(max_workers=max(1, parallel)) as pool:
        return sum(pool.map(run_job, jobs))


def resume() -> tuple[int, int]:
    """Dokańcza zadania wysłane do fal, których wyniku nie pobrano (np. po przerwaniu skryptu)."""
    pending = [r for r in latest_by_job().values() if r.get("stan") == "wyslane"]
    done = 0
    for record in pending:
        tag = f"[{record.get('ujecie')}/{record.get('model')}]"
        try:
            fetch_result(record["status_url"], record["response_url"], config.ROOT / record["plik"], tag)
        except Exception as exc:
            log_append({"id": record["id"], "czas": now(), "stan": "blad", "blad": str(exc)[:1500]})
            print(f"{tag} x {exc}")
            continue
        log_append({"id": record["id"], "czas": now(), "stan": "gotowe"})
        print(f"{tag} + {record['plik']}")
        done += 1
    return done, len(pending)
