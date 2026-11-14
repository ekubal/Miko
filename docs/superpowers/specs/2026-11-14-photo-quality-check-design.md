# Photo quality check (`data_checked`) — design

Date: 2026-11-14  
Status: implemented (app branch `photo-quality-check`); revised during implementation — see “Changes during implementation”  
Related: `AUTOMATYZACJA.md` (DANE_SPRAWDZONE), `PLAN_WDROZENIA.md` §6.7, `Order::STATUSES`

## Goal

After payment, automatically verify each child’s **main** photo (face + sharpness) on the Rails server with no external AI. Pass → `data_checked`. Fail → `waiting_for_parent` + mail 2.

Note: full `DANE_SPRAWDZONE` in product docs also covers form fields; **v1 is photo-only**. Status name `data_checked` stays for pipeline compatibility; field heuristics come later.

## Scope (v1)

In:

- New transitional status `data_checking` (“sprawdzanie zdjęć w toku”)
- Face detection (local ONNX YuNet) + EXIF auto-orient before detect
- Sharpness (Laplacian variance via ruby-vips on largest accepted face crop)
- Recurring Solid Queue task every **5 minutes** that finds orders awaiting check and enqueues per-order jobs
- Status transitions, `OrderEvent`, `OrderMailer#missing_data`
- Operational workaround doc for `waiting_for_parent` without parent upload UI

Out:

- Form-field heuristics
- Parent self-serve upload form / automatic re-check after reply
- Starting text generation after `data_checked`

## Status flow

New value in `Order::STATUSES`: `data_checking` (after `paid`, before `data_checked` / `waiting_for_parent`).

```
new → paid
        ↓  (recurring dispatcher every 5 min)
     data_checking          # transitional: check in progress
        ↓
     data_checked           # all main photos OK
        or
     waiting_for_parent     # quality failure + mail 2
```

Semantic gap vs docs: `data_checked` here means “photos OK”, not yet “all form data reviewed”.

## Architecture

```
Stripe / return-page sync
  → Order#mark_paid!     # new → paid only; does NOT enqueue photo check
  → OrderMailer.confirmation (unchanged, in StripeEventHandler)

Orders::DispatchPhotoChecksJob   # Solid Queue recurring: every 5 minutes
  → find orders with status: paid
  → also find stale data_checking (updated_at older than e.g. 15 min)  # crash recovery
  → for each: Orders::CheckPhotosJob.perform_later(order.id)

Orders::CheckPhotosJob
  → with_lock:
       if paid → set data_checking (+ optional OrderEvent)
       elsif data_checking → continue (retry / stale re-dispatch)
       else → no-op (already finished)
  → Orders::PhotoQualityCheck.call(order)
       for each Child (main `photo` only; ignore `extra_photos`):
         download blob
         auto-orient (vips / image_processing)
         Photos::FaceDetector   (YuNet ONNX + preprocess/NMS)
         Photos::SharpnessScorer (Laplacian on largest accepted face crop)
  → with_lock, only if still data_checking:
       all OK  → data_checked + event
       any fail → waiting_for_parent + event + mail 2 (deliver_later after commit)
```

### Why transitional status + poller

- `data_checking` shows that work started (panel / support), and claims the order so two workers do not both treat it as `paid`.
- Dispatcher every 5 min decouples Stripe webhook from production pipeline; missed enqueue is self-healing.
- Stale `data_checking` re-dispatch recovers crashed jobs without blaming the parent.

Siblings: one failing main photo holds the whole order; mail lists every problem.

Multiple faces: use the **largest** face that passes score + relative size. Group photos may pass (accepted for v1).

Photos never leave the server (no third-party vision APIs).

## Components

| Unit | Responsibility |
|---|---|
| `Orders::DispatchPhotoChecksJob` | Recurring every 5 min; select `paid` (+ stale `data_checking`); enqueue per-order jobs |
| `Orders::CheckPhotosJob` | Claim `paid` → `data_checking` under lock; run check; finalize status |
| `Orders::PhotoQualityCheck` | Per-child checks; build issues; status + event + mail |
| `Photos::FaceDetector` | YuNet ONNX (preprocess, inference, NMS); ≥ 1 face above thresholds |
| `Photos::SharpnessScorer` | Laplacian variance on largest accepted face crop |
| Config | `config/photo_quality.yml` via `config_for` (thresholds, model path, stale minutes) |
| Model file | Committed ONNX under `vendor/models/`; filename pinned in config |
| Recurring | `config/recurring.yml` — every 5 minutes in production (and dev if desired) |

Gem: `onnxruntime` (+ numeric helper if needed). Docker: keep `libvips`; add any native deps required by `onnxruntime` to the image.

Check order per child: missing main `photo` → `missing_photo`; else auto-orient → face detect; if no qualifying face → `no_face` (skip sharpness); else sharpness on that crop → `blurry` or OK.

Undecodable file (libvips cannot open it): issue `unreadable` → `waiting_for_parent` + mail 2 — the parent has to send the photo again.

Missing model / ONNX crash / Active Storage download error: **raise**, status stays `data_checking`. `ApplicationJob` has no `retry_on`, so the retry is the stale re-dispatch. Each failure writes `photo_check_failed`; after `max_check_attempts` (default 3) failures since the latest claim the order goes to `review`. Do not revert to `paid` on tech failure (avoids flip-flop with the dispatcher).

`Orders::CheckPhotosJob` uses Solid Queue `limits_concurrency` (one run per order), so dispatcher duplicates during a queue backlog wait and then no-op on the finished status.

### Problem codes → parent copy

| Code | Meaning | Mail copy source |
|---|---|---|
| `missing_photo` | Main `photo` not attached | I18n from `szablony/emaile.md` — brak zdjęcia |
| `unreadable` | libvips cannot decode the file | Dedicated I18n (plik się nie otwiera) |
| `no_face` | No face above confidence / size threshold | Dedicated I18n (twarz niewidoczna / nie nadaje się do księgi) |
| `blurry` | Face-crop sharpness below threshold | I18n from `szablony/emaile.md` — nieostre zdjęcie |

Mail: `OrderMailer.missing_data` via `deliver_later` after the `with_lock` block returns (production queue uses a separate database, so enqueueing inside the transaction is not atomic). Copy avoids the genitive name (`{IMIE_DLA}`), which the form does not collect: paragraphs start with “Kasia: …”.

### Thresholds (tunable)

In `config/photo_quality.yml`:

- `face_score_min`
- `face_min_relative_size` (required in v1)
- `sharpness_min`
- `stale_checking_after_minutes` (default 15) — for dispatcher re-enqueue

Exact numeric thresholds calibrated on fixtures during implementation.

## Status & events

| Step | From | To | Event `kind` | Mail |
|---|---|---|---|---|
| Claim | `paid` | `data_checking` | `data_checking` (optional) | none |
| Pass | `data_checking` | `data_checked` | `data_checked` | none |
| Fail | `data_checking` | `waiting_for_parent` | `waiting_for_parent` | mail 2 |
| Tech error | `data_checking` | `data_checking` | `photo_check_failed` (`meta.error` = class) | none |
| Tech error cap | `data_checking` | `review` | `review` | none |

Event `meta` (no paths / binaries):

- `issues`: `[{ "child_id", "position", "code", "face_score", "sharpness" }, …]`

## Operational workaround (`waiting_for_parent`)

v1 has **no** parent upload form. Until that exists:

1. Parent replies to mail 2 with a new photo (or support requests it).
2. Operator replaces the child’s main Active Storage `photo` (panel or Rails console).
3. Operator sets order status back to **`paid`** (so the 5-minute dispatcher picks it up again).  
   Do **not** set `data_checking` by hand — the per-order job claims that.
4. Optionally enqueue `Orders::CheckPhotosJob` immediately after reset if waiting ~5 min is too slow.
5. Confirm outcome: `data_checked` or another mail 2 / still `waiting_for_parent`.

Document this procedure in `AUTOMATYZACJA.md` next to the state machine (CZEKA_NA_RODZICA).

## Integration points

- **No** enqueue from `Order#mark_paid!`
- Dispatcher: Solid Queue recurring schedule every 5 minutes
- Mail 1 unchanged in `Payments::StripeEventHandler`
- Only attachment checked: `Child#photo` (not `extra_photos`)

## Testing

Offline only (no network, no API keys).

- Fixtures: **stock / synthetic photos only** (no real children’s photos in the repo). Provide at least: sharp face, blurry face, no face / landscape.
- Always run EXIF-orient path in unit tests (rotated fixture).
- Unit: detector / scorer on fixtures
- Job: `paid` → claim `data_checking` → `data_checked` or `waiting_for_parent` + mail
- Dispatcher: selects `paid` and stale `data_checking`; ignores `data_checked` / `waiting_for_parent`
- Idempotency: job no-op when status is already terminal for this step
- Concurrency: two jobs on same `paid` order → only one claims; one mail max

## Success criteria

1. Blurry / no-face stock fixture → `waiting_for_parent` + mail 2  
2. Good stock fixture → `data_checked` + event  
3. Within ~5 minutes of `paid`, order is claimed (`data_checking`) without enqueue from webhook  
4. Stale `data_checking` is re-dispatched  
5. Specs pass without network; no child PII photos in git  

## Changes during implementation

- Issue code `unreadable` (corrupt file → parent fixes it, not an endless technical retry).
- Technical failures capped by `max_check_attempts` → `review` (was out of scope; without it a broken order re-dispatches every 5 minutes forever).
- `limits_concurrency` on `Orders::CheckPhotosJob`.
- Images decoded in memory with `Vips::Image.thumbnail` (shrink-on-load to `analysis_max_size`, EXIF orientation); no temp files with child photos.
- Same thresholds in every environment; calibration on public-domain fixtures, measured values in `app/spec/fixtures/files/photos/README.md`.
- Model: OpenCV Zoo `face_detection_yunet_2023mar.onnx` (MIT), fixed 640×640 input, `vendor/models/README.md`.

## Open calibration (implementation, not design blockers)

- Concrete YuNet ONNX filename + license/attribution note in `vendor/models/`
- Initial threshold numbers from fixture measurements  
- Exact Polish copy for `no_face` vs `blurry`  
- Whether `data_checking` always writes an `OrderEvent` (recommended: yes, for timeline)  
