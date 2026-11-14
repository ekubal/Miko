# Photo quality check Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After payment, a 5-minute dispatcher claims `paid` orders into `data_checking`, runs local face+sharpness checks on each child’s main photo, then sets `data_checked` or `waiting_for_parent` (+ mail 2).

**Architecture:** Solid Queue recurring `Orders::DispatchPhotoChecksJob` selects `paid` (and stale `data_checking`) orders and enqueues `Orders::CheckPhotosJob`. That job locks the order, claims `paid`→`data_checking`, runs `Orders::PhotoQualityCheck` (YuNet ONNX + vips Laplacian on face crop), then finalizes status under lock and sends mail after commit.

**Tech Stack:** Rails 8.1, Solid Queue, Active Storage, `ruby-vips` / `image_processing`, `onnxruntime`, RSpec, `config_for` YAML.

**Spec:** `docs/superpowers/specs/2026-11-14-photo-quality-check-design.md` (parent repo).

## Global Constraints

- Work Rails code in the **nested repo** `app/` (parent gitignores `/app/`). Design/plan docs live in the parent repo `Miko/`.
- Photos never leave the server; no third-party vision APIs.
- Only `Child#photo` (not `extra_photos`).
- No enqueue from `Order#mark_paid!`.
- Parent-facing copy in Polish via I18n; code comments in English.
- Test fixtures: stock/synthetic only — never real children’s photos.
- Commit messages in English; in `app/` follow `app/AGENTS.md` (optional plan ref `(6.7)`).
- Before `app/` commit: `bin/rspec` and `bin/rubocop` from `app/`.
- Docker already has `libvips`; add any `onnxruntime` native deps to `Dockerfile` if bundle needs them.
- No temp files with child photo data: decoded images and face crops stay in memory (`Vips::Image`); only Active Storage’s own `attachment.open` tempfile is used and it is removed after the block.
- `Child` validates `photo` as `attached: true` — factories cannot build a child without a photo. Replace the factory photo with `child.photo.attach(...)`; simulate a missing photo with `child.photo.purge`.
- `ApplicationJob` has no `retry_on`: a raised error does **not** retry by itself. Retries come only from the stale re-dispatch, capped by `max_check_attempts` (Task 8).
- Production Solid Queue uses a separate database (`queue`), so enqueueing inside a primary-DB transaction is not atomic. Mails are enqueued **after** the `with_lock` block returns (same pattern as `Payments::StripeEventHandler` + `mark_paid!`).

## Deviations from the design spec (sync spec in Task 10)

- New issue code `unreadable` (photo cannot be decoded) → `waiting_for_parent` + mail 2, instead of an endless technical retry.
- Technical failures are capped: after `max_check_attempts` failed runs the order goes to `review` (spec listed this as out of scope; without it a broken order re-dispatches every 5 minutes forever).
- Mail 2 copy avoids the genitive name (`{IMIE_DLA}` in `szablony/emaile.md`): the form does not collect it, so paragraphs start with “Imię:” style prefixes.

## File structure

| Path (under `app/`) | Role |
|---|---|
| `app/models/order.rb` | Add `data_checking` to `STATUSES` |
| `config/photo_quality.yml` | Thresholds, model path, stale minutes |
| `app/services/photos/config.rb` | Read `config_for(:photo_quality)` |
| `app/services/photos/prepared_image.rb` | Download blob, shrink-on-load + auto-orient (`Vips::Image.thumbnail`), in-memory RGB image + crop helper |
| `app/services/photos/unreadable_image.rb` | Error for files libvips cannot decode (→ issue `unreadable`) |
| `app/services/photos/sharpness_scorer.rb` | Laplacian variance |
| `app/services/photos/face_detector.rb` | YuNet ONNX detect |
| `app/services/orders/photo_quality_check.rb` | Orchestrate per-child issues → status/event/mail |
| `app/jobs/orders/check_photos_job.rb` | Claim + run check |
| `app/jobs/orders/dispatch_photo_checks_job.rb` | Recurring selector |
| `config/recurring.yml` | `every 5 minutes` |
| `vendor/models/face_detection_yunet_2023mar.onnx` | Model file + short LICENSE/README |
| `config/locales/pl.yml` | Event messages + mail 2 issue paragraphs |
| `spec/fixtures/files/photos/` | Stock: `sharp_face.jpg`, `blurry_face.jpg`, `no_face.jpg`, `rotated_face.jpg` |
| Specs under `spec/services/photos/`, `spec/services/orders/`, `spec/jobs/orders/` | |

---

### Task 1: Add `data_checking` status + event locales

**Files:**
- Modify: `app/app/models/order.rb` (`STATUSES`)
- Modify: `app/config/locales/pl.yml` (`orders.events`)
- Test: existing `spec/models/order_spec.rb` inclusion matcher covers new value once listed

**Interfaces:**
- Produces: `Order::STATUSES` includes `"data_checking"` immediately after `"paid"`

- [ ] **Step 1: Insert status**

In `Order::STATUSES`, after `paid`:

```ruby
  STATUSES = %w[
    new
    paid
    data_checking
    data_checked
    waiting_for_parent
    text_ready
    text_approved
    voice_ready
    voice_checked
    lipsync_ready
    film_ready
    quality_ok
    sent
    data_deleted
    review
  ].freeze
```

- [ ] **Step 2: Add I18n event strings**

Under `orders.events` in `config/locales/pl.yml`:

```yaml
      data_checking: Sprawdzanie zdjęć
      data_checked: Zdjęcia sprawdzone
      waiting_for_parent: Czekamy na poprawkę od rodzica
      photo_check_failed: Błąd techniczny przy sprawdzaniu zdjęć
      review: Do ręcznego sprawdzenia
```

Add these keys inside the existing `pl.orders.events` block — do not paste a second `orders:` key (YAML silently keeps only the last duplicate).

- [ ] **Step 3: Run model specs**

Run (from `app/`): `bin/rspec spec/models/order_spec.rb`

Expected: PASS (inclusion still green).

- [ ] **Step 4: Commit (app repo)**

```bash
cd app
git add app/models/order.rb config/locales/pl.yml
git commit -m "$(cat <<'EOF'
Allow data_checking order status for photo quality pipeline (6.7)

EOF
)"
```

---

### Task 2: Photo quality config

**Files:**
- Create: `app/config/photo_quality.yml`
- Create: `app/app/services/photos/config.rb`
- Test: `app/spec/services/photos/config_spec.rb`

**Interfaces:**
- Produces: `Photos::Config.face_score_min`, `.face_min_relative_size`, `.sharpness_min`, `.stale_checking_after`, `.max_check_attempts` (Integer), `.analysis_max_size` (Integer, px), `.model_path` (Pathname)

- [ ] **Step 1: Write failing spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::Config do
  it "exposes thresholds from photo_quality.yml" do
    expect(described_class.face_score_min).to be_a(Float)
    expect(described_class.face_min_relative_size).to be_a(Float)
    expect(described_class.sharpness_min).to be_a(Float)
    expect(described_class.stale_checking_after).to eq(15.minutes)
    expect(described_class.max_check_attempts).to eq(3)
    expect(described_class.analysis_max_size).to eq(1600)
    expect(described_class.model_path).to be_a(Pathname)
  end
end
```

- [ ] **Step 2: Run spec — expect FAIL** (`uninitialized constant Photos::Config`)

Run: `bin/rspec spec/services/photos/config_spec.rb`

- [ ] **Step 3: Add YAML + config class**

`config/photo_quality.yml`:

```yaml
default: &default
  face_score_min: 0.6
  face_min_relative_size: 0.02
  sharpness_min: 80.0
  stale_checking_after_minutes: 15
  # Failed technical runs (exceptions) before the order goes to review.
  max_check_attempts: 3
  # Longest side after shrink-on-load; keeps 20 MB uploads cheap in the Puma process.
  analysis_max_size: 1600
  model_relative_path: vendor/models/face_detection_yunet_2023mar.onnx

development:
  <<: *default

test:
  <<: *default

production:
  <<: *default
```

Same thresholds in every environment: fixture specs exist to prove the **production** values separate good and bad photos. Never override thresholds under `test:`; if a fixture fails, recalibrate the default and note the measured values in `spec/fixtures/files/photos/README.md`.

`app/services/photos/config.rb`:

```ruby
# frozen_string_literal: true

module Photos
  module Config
    module_function

    def face_score_min
      config.fetch("face_score_min").to_f
    end

    def face_min_relative_size
      config.fetch("face_min_relative_size").to_f
    end

    def sharpness_min
      config.fetch("sharpness_min").to_f
    end

    def stale_checking_after
      config.fetch("stale_checking_after_minutes").to_i.minutes
    end

    def max_check_attempts
      config.fetch("max_check_attempts").to_i
    end

    def analysis_max_size
      config.fetch("analysis_max_size").to_i
    end

    def model_path
      Rails.root.join(config.fetch("model_relative_path"))
    end

    def config
      Rails.application.config_for(:photo_quality).with_indifferent_access
    end
    private_class_method :config
  end
end
```

- [ ] **Step 4: Run spec — expect PASS**

Run: `bin/rspec spec/services/photos/config_spec.rb`

- [ ] **Step 5: Commit**

```bash
git add config/photo_quality.yml app/services/photos/config.rb spec/services/photos/config_spec.rb
git commit -m "$(cat <<'EOF'
Add photo_quality config for face and sharpness thresholds (6.7)

EOF
)"
```

---

### Task 3: Stock photo fixtures (manual + factory helpers)

**Files:**
- Create: `app/spec/fixtures/files/photos/README.md`
- Create (you provide binaries):  
  `sharp_face.jpg`, `blurry_face.jpg`, `no_face.jpg`, `rotated_face.jpg` under `spec/fixtures/files/photos/`
- Modify: `app/spec/factories/children.rb` (optional trait `:with_stock_photo`)

**Interfaces:**
- Produces: fixture paths usable as `Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg")`

- [ ] **Step 1: Add README for fixtures**

```markdown
# Photo quality fixtures

Stock / synthetic images only — never real customers’ children.

| File | Purpose |
|---|---|
| sharp_face.jpg | Clear frontal face, good focus |
| blurry_face.jpg | Face present but soft/blurry |
| no_face.jpg | Landscape or object, no face |
| rotated_face.jpg | Same as sharp but EXIF Orientation = 6 (or 90° CW) |

License: use photos with a clear stock license; note source here when adding files.
```

- [ ] **Step 2: Drop in the four JPEGs** (operator / you). Verify with `file` and that `rotated_face.jpg` has Orientation tag (`exiftool` or `vipsheader -a`).

- [ ] **Step 3: Commit fixtures when files exist**

```bash
git add spec/fixtures/files/photos/
git commit -m "$(cat <<'EOF'
Add stock photo fixtures for quality check specs (6.7)

EOF
)"
```

If binaries are not ready yet: commit README only and pause detector/scorer calibration tasks until files land; later tasks may stub detector scores.

---

### Task 4: Prepared image (download + shrink-on-load + auto-orient, in memory)

**Files:**
- Create: `app/app/services/photos/unreadable_image.rb`
- Create: `app/app/services/photos/prepared_image.rb`
- Test: `app/spec/services/photos/prepared_image_spec.rb`
- Gem already: `image_processing` (pulls `ruby-vips` 2.3), `libvips` in Docker

**Interfaces:**
- Consumes: Active Storage attachment or file path
- Produces: `Photos::PreparedImage.open_attachment(attachment) { |prepared| ... }` and `.open_path(path) { |prepared| ... }`; `prepared.image` (in-memory upright 8-bit sRGB `Vips::Image`, no alpha, longest side ≤ `Photos::Config.analysis_max_size`), `#width`, `#height`, `#crop(x:, y:, w:, h:) -> Vips::Image` (clamped to bounds)
- Raises: `Photos::UnreadableImage` when libvips cannot decode the file (Task 7 maps it to issue `unreadable`)

Why `Vips::Image.thumbnail`: it shrinks on load (cheap for 20 MB uploads in the Puma process) and applies EXIF orientation itself. Do **not** use `new_from_file(access: :sequential)` + `autorot` — a 90° rotation on a sequential image fails with “out of order read”. Nothing is written to disk: no oriented copy, no crop files.

- [ ] **Step 1: Failing specs (orientation on a synthetic image, alpha, size, unreadable, crop)**

Synthetic images only — no fixture needed, so these specs never skip.

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::PreparedImage do
  def write_jpeg(dir, width:, height:, orientation: nil)
    image = Vips::Image.black(width, height).add(120).cast(:uchar)
    image = image.bandjoin([image, image]).copy(interpretation: :srgb)
    image = image.mutate { |m| m.set_type!(GObject::GINT_TYPE, "orientation", orientation) } if orientation
    path = File.join(dir, "synthetic.jpg")
    image.write_to_file(path)
    path
  end

  it "applies EXIF orientation: 300x200 stored with Orientation=6 comes out 200x300" do
    Dir.mktmpdir do |dir|
      path = write_jpeg(dir, width: 300, height: 200, orientation: 6)
      raw = Vips::Image.new_from_file(path)
      expect([raw.width, raw.height]).to eq([300, 200]) # header ignores orientation

      described_class.open_path(path) do |prepared|
        expect([prepared.width, prepared.height]).to eq([200, 300])
      end
    end
  end

  it "shrinks the longest side to analysis_max_size" do
    max = Photos::Config.analysis_max_size
    Dir.mktmpdir do |dir|
      path = write_jpeg(dir, width: max * 2, height: max)

      described_class.open_path(path) do |prepared|
        expect(prepared.width).to eq(max)
        expect(prepared.height).to eq(max / 2)
      end
    end
  end

  it "returns 3-band uchar sRGB without alpha for a grayscale PNG with alpha" do
    Dir.mktmpdir do |dir|
      gray = Vips::Image.black(40, 30).add(90).cast(:uchar)
      path = File.join(dir, "ga.png")
      gray.bandjoin(255).copy(interpretation: :b_w).write_to_file(path)

      described_class.open_path(path) do |prepared|
        expect(prepared.image.bands).to eq(3)
        expect(prepared.image.format).to eq(:uchar)
        expect(prepared.image.has_alpha?).to be(false)
      end
    end
  end

  it "raises UnreadableImage for bytes libvips cannot decode" do
    Dir.mktmpdir do |dir|
      path = File.join(dir, "broken.jpg")
      File.binwrite(path, "\xFF\xD8\xFF not really a jpeg".b)

      expect { described_class.open_path(path) { nil } }.to raise_error(Photos::UnreadableImage)
    end
  end

  it "clamps crops to image bounds" do
    Dir.mktmpdir do |dir|
      path = write_jpeg(dir, width: 100, height: 80)

      described_class.open_path(path) do |prepared|
        crop = prepared.crop(x: 90, y: -10, w: 50, h: 50)
        expect([crop.width, crop.height]).to eq([10, 40])
      end
    end
  end
end
```

The temp dirs above hold synthetic images only (never child photos). If `jpegsave` does not carry the `orientation` metadata into EXIF on the installed libvips, verify with `vipsheader -f orientation` and set `exif-ifd0-Orientation` instead; the assertion (dimensions swapped vs raw header) stays.

- [ ] **Step 2: Implement**

`app/services/photos/unreadable_image.rb`:

```ruby
# frozen_string_literal: true

module Photos
  # The uploaded file cannot be decoded — a parent-side problem, not a technical failure.
  class UnreadableImage < StandardError; end
end
```

`app/services/photos/prepared_image.rb`:

```ruby
# frozen_string_literal: true

require "vips"

module Photos
  # Upright, 8-bit sRGB copy of a photo held in memory (nothing is written to disk).
  class PreparedImage
    attr_reader :image

    def self.open_attachment(attachment, &block)
      raise ArgumentError, "photo missing" unless attachment&.attached?

      attachment.open { |file| open_path(file.path, &block) }
    end

    def self.open_path(path)
      yield new(decode(path))
    end

    # thumbnail: shrink-on-load + EXIF autorotate; copy_memory forces the decode
    # here, so a broken file raises before the caller's block runs.
    def self.decode(path)
      size = Config.analysis_max_size
      image = Vips::Image.thumbnail(path.to_s, size, height: size, size: :down)
      image = image.colourspace(:srgb) unless image.interpretation == :srgb
      image = image.flatten(background: [255, 255, 255]) if image.has_alpha?
      image = image.cast(:uchar) unless image.format == :uchar
      image.copy_memory
    rescue Vips::Error => error
      raise UnreadableImage, error.message
    end
    private_class_method :decode

    def initialize(image)
      @image = image
    end

    def width
      image.width
    end

    def height
      image.height
    end

    # Box in this image's pixels (detector output); clamped, returned as an in-memory Vips::Image.
    def crop(x:, y:, w:, h:)
      left = x.round.clamp(0, width - 1)
      top = y.round.clamp(0, height - 1)
      crop_width = (x.round + w.round - left).clamp(1, width - left)
      crop_height = (y.round + h.round - top).clamp(1, height - top)
      image.crop(left, top, crop_width, crop_height)
    end
  end
end
```

Note: `rescue` sits in `decode`, not around `yield`, so errors raised inside the caller's block (detector, ONNX) stay technical errors.

- [ ] **Step 3: Run spec**

Run: `bin/rspec spec/services/photos/prepared_image_spec.rb`

Expected: PASS, no skips.

- [ ] **Step 4: Commit**

```bash
git add app/services/photos/unreadable_image.rb app/services/photos/prepared_image.rb \
  spec/services/photos/prepared_image_spec.rb
git commit -m "$(cat <<'EOF'
Decode photos in memory with shrink-on-load and EXIF orientation (6.7)

EOF
)"
```

---

### Task 5: Sharpness scorer

**Files:**
- Create: `app/app/services/photos/sharpness_scorer.rb`
- Test: `app/spec/services/photos/sharpness_scorer_spec.rb`

**Interfaces:**
- Consumes: in-memory `Vips::Image` (normally `PreparedImage#crop` of the face; alpha already flattened by `PreparedImage`)
- Produces: `Photos::SharpnessScorer.score(image) -> Float` (variance of the Laplacian)

libvips has no `laplacian` operation — use `conv` with a 3×3 mask. Cast to float first (a uchar input with a negative mask otherwise clips), and take the variance as `deviate ** 2`.

- [ ] **Step 1: Failing spec (synthetic, never skips)**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::SharpnessScorer do
  let(:noise) { Vips::Image.gaussnoise(128, 128, mean: 128, sigma: 40).cast(:uchar) }

  it "scores a sharp image higher than a blurred copy" do
    expect(described_class.score(noise)).to be > described_class.score(noise.gaussblur(2))
  end

  it "accepts 3-band sRGB input" do
    rgb = noise.bandjoin([noise, noise]).copy(interpretation: :srgb)

    expect(described_class.score(rgb)).to be_a(Float).and be > 0
  end
end
```

Threshold checks against real faces (`sharp_face` ≥ `sharpness_min`, `blurry_face` < `sharpness_min`) live in Task 6, where the face crop exists.

- [ ] **Step 2: Implement**

```ruby
# frozen_string_literal: true

require "vips"

module Photos
  module SharpnessScorer
    LAPLACIAN = [[0, 1, 0], [1, -4, 1], [0, 1, 0]].freeze

    module_function

    # Variance of the Laplacian on a grayscale copy — higher means sharper.
    def score(image)
      gray = image.colourspace("b-w")
      gray = gray.extract_band(0) if gray.bands > 1
      mask = Vips::Image.new_from_array(LAPLACIAN)
      laplacian = gray.cast(:float).conv(mask, precision: :float)
      (laplacian.deviate**2).to_f
    end
  end
end
```

- [ ] **Step 3: Run spec**

Run: `bin/rspec spec/services/photos/sharpness_scorer_spec.rb`

Expected: PASS, no skips.

- [ ] **Step 4: Commit**

```bash
git add app/services/photos/sharpness_scorer.rb spec/services/photos/sharpness_scorer_spec.rb
git commit -m "$(cat <<'EOF'
Score photo sharpness with Laplacian variance (6.7)

EOF
)"
```

---

### Task 6: Face detector (YuNet ONNX)

**Files:**
- Add gem: `onnxruntime` (and `numo-narray` if needed for tensors) to `Gemfile`
- Create: `app/vendor/models/face_detection_yunet_2023mar.onnx` (+ `vendor/models/README.md` with source URL + Apache-2.0 OpenCV zoo attribution)
- Create: `app/app/services/photos/face.rb` (simple Data)
- Create: `app/app/services/photos/face_detector.rb`
- Modify: `app/Dockerfile` if native libs required after `bundle install` in build
- Test: `app/spec/services/photos/face_detector_spec.rb`

**Interfaces:**
- Consumes: `Photos::PreparedImage` (reads `prepared.image`, an in-memory `Vips::Image`)
- Produces: `Photos::FaceDetector.detect(prepared_image) -> Array<Photos::Face>` (all detections after NMS)  
  `Photos::FaceDetector.best_face(prepared_image) -> Photos::Face or nil` — largest face with `score >= face_score_min` and `area / (width * height) >= face_min_relative_size`; Task 7 uses only this  
  `Photos::Face` = `Data.define(:x, :y, :width, :height, :score)` in `PreparedImage` pixels (after shrink-on-load)

- [ ] **Step 1: Bundle gem**

```bash
bundle add onnxruntime
# if needed: bundle add numo-narray
bundle exec ruby -e 'require "onnxruntime"; puts OnnxRuntime::VERSION'
```

- [ ] **Step 2: Download model into vendor**

Use OpenCV Zoo YuNet 2023-03 ONNX (verify URL at implementation time), e.g.:

```bash
mkdir -p vendor/models
# curl -L -o vendor/models/face_detection_yunet_2023mar.onnx \
#   "<opencv-zoo yunet onnx url>"
```

Write `vendor/models/README.md` with source + license.

- [ ] **Step 3: Failing detector spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::FaceDetector do
  it "finds a face on sharp_face.jpg" do
    path = Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg")
    skip "fixture missing" unless path.exist?

    Photos::PreparedImage.open_path(path) do |image|
      faces = described_class.detect(image)
      expect(faces).not_to be_empty
      expect(faces.first.score).to be >= Photos::Config.face_score_min
    end
  end

  it "finds no face on no_face.jpg" do
    path = Rails.root.join("spec/fixtures/files/photos/no_face.jpg")
    skip "fixture missing" unless path.exist?

    Photos::PreparedImage.open_path(path) do |image|
      expect(described_class.detect(image)).to be_empty
    end
  end

  # Production thresholds (no test override): this is the calibration gate.
  it "keeps sharp_face above and blurry_face below sharpness_min on the face crop" do
    sharp = Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg")
    blurry = Rails.root.join("spec/fixtures/files/photos/blurry_face.jpg")
    skip "fixtures missing" unless sharp.exist? && blurry.exist?

    score = ->(path) {
      Photos::PreparedImage.open_path(path) do |image|
        face = described_class.best_face(image)
        expect(face).not_to be_nil
        Photos::SharpnessScorer.score(image.crop(x: face.x, y: face.y, w: face.width, h: face.height))
      end
    }

    expect(score.call(sharp)).to be >= Photos::Config.sharpness_min
    expect(score.call(blurry)).to be < Photos::Config.sharpness_min
  end
end
```

- [ ] **Step 4: Implement Face + FaceDetector**

Implement YuNet input letterbox/resize to model input size, `OnnxRuntime::Model` run, decode boxes, NMS. Keep all logic inside `Photos::FaceDetector` (private class methods). Public API only:

`app/services/photos/face.rb`:

```ruby
# frozen_string_literal: true

module Photos
  Face = Data.define(:x, :y, :width, :height, :score) do
    def area
      width * height
    end
  end
end
```

`app/services/photos/face_detector.rb` (public part):

```ruby
module Photos
  class FaceDetector
    def self.detect(prepared_image)
      new(prepared_image).detect
    end

    # Largest face passing both thresholds, or nil.
    def self.best_face(prepared_image)
      image_area = prepared_image.width * prepared_image.height
      detect(prepared_image)
        .select { |face| face.score >= Config.face_score_min }
        .select { |face| face.area.fdiv(image_area) >= Config.face_min_relative_size }
        .max_by(&:area)
    end
    # ...
  end
end
```

Calibrate against fixtures by changing the **default** values in `photo_quality.yml` (never a `test:` override); write the measured scores into `spec/fixtures/files/photos/README.md`.

- [ ] **Step 5: Run specs**

Run: `bin/rspec spec/services/photos/face_detector_spec.rb`

- [ ] **Step 6: Commit**

```bash
git add Gemfile Gemfile.lock vendor/models app/services/photos/face.rb \
  app/services/photos/face_detector.rb spec/services/photos/face_detector_spec.rb Dockerfile
git commit -m "$(cat <<'EOF'
Detect faces locally with YuNet ONNX (6.7)

EOF
)"
```

---

### Task 7: `Orders::PhotoQualityCheck` + mail copy

**Files:**
- Create: `app/app/services/orders/photo_quality_check.rb`
- Modify: `app/config/locales/pl.yml` (`pl.orders.photo_quality`: subjects + issue paragraphs)
- Test: `app/spec/services/orders/photo_quality_check_spec.rb`

**Interfaces:**
- Consumes: `Order` claimed as `data_checking` (Task 8); `Photos::PreparedImage`, `Photos::FaceDetector.best_face`, `Photos::SharpnessScorer`, `Photos::UnreadableImage`
- Produces: `Orders::PhotoQualityCheck.call(order) -> "data_checked" | "waiting_for_parent" | nil` (`nil` = order left `data_checking` meanwhile, nothing changed); one `OrderEvent`; mail 2 enqueued **after** the lock block on failure
- Issue codes: `missing_photo`, `unreadable`, `no_face`, `blurry`
- Technical errors (ONNX, missing model, Active Storage download): re-raised, status untouched — Task 8 counts them

- [ ] **Step 1: Add I18n for mail 2**

Inside the existing `pl.orders` block (no second `orders:` key). The form does not collect the genitive name (`{IMIE_DLA}` in `szablony/emaile.md`), so every text uses the plain first name after a colon instead of declining it:

```yaml
    photo_quality:
      mail_subject_one: "Potrzebujemy jeszcze jednego zdjęcia: %{name}"
      mail_subject_many: "Potrzebujemy nowych zdjęć: %{names}"
      issues:
        missing_photo: "%{name}: nie dotarło do nas zdjęcie. Dołącz je do odpowiedzi, najlepiej ostre, z twarzą widoczną na wprost, w formacie JPG lub PNG."
        unreadable: "%{name}: nie udało nam się otworzyć przesłanego zdjęcia. Dołącz je ponownie do odpowiedzi, w formacie JPG lub PNG."
        no_face: "%{name}: na przesłanym zdjęciu nie widać wyraźnie twarzy. W magicznej księdze potrzebujemy zdjęcia z twarzą widoczną na wprost. Najlepiej sprawdzi się ostre zdjęcie w świetle dziennym, w formacie JPG lub PNG."
        blurry: "%{name}: przesłane zdjęcie jest nieostre i twarz jest słabo widoczna. W magicznej księdze nie wyglądałoby dobrze. Najlepiej sprawdzi się ostre zdjęcie w świetle dziennym, z twarzą widoczną na wprost, w formacie JPG lub PNG."
```

Paragraphs are joined with `"\n\n"`; `missing_data.html.haml` renders them with `simple_format`.

Known gap (out of scope): the mail body intro uses `mail_for_whom` (“film dla #{@for_whom}”), which falls back to the nominative too. Leave it; fixing it needs a genitive field in the form.

- [ ] **Step 2: Failing service specs**

Detector and scorer are stubbed here so the spec covers status, issue mapping, meta and mail without the ONNX model; real-model behaviour lives in `spec/services/photos/`. The factory photo (`spec/fixtures/files/child.jpg`) is decoded for real by `PreparedImage`. Children are processed in `position` order, so stub return values are listed in that order.

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Orders::PhotoQualityCheck do
  # Child validates photo presence, so the factory always attaches child.jpg.
  let(:order) { create(:order, status: "data_checking", children_count: 2) }
  let(:kasia) { order.children.first }
  let(:antek) { order.children.second.tap { |c| c.update!(first_name: "Antek", vocative: "Antku") } }
  let(:face) { Photos::Face.new(x: 0, y: 0, width: 40, height: 40, score: 0.93) }
  let(:sharp) { Photos::Config.sharpness_min + 50 }
  let(:soft) { Photos::Config.sharpness_min - 10 }

  before { antek }

  def stub_checks(faces:, sharpness:)
    allow(Photos::FaceDetector).to receive(:best_face).and_return(*faces)
    allow(Photos::SharpnessScorer).to receive(:score).and_return(*sharpness)
  end

  it "marks data_checked when every main photo passes" do
    stub_checks(faces: [face, face], sharpness: [sharp, sharp])

    expect { described_class.call(order) }
      .to change { order.reload.status }.from("data_checking").to("data_checked")
      .and not_have_enqueued_mail(OrderMailer, :missing_data)
    expect(order.events.order(:id).last.kind).to eq("data_checked")
  end

  it "holds the order for one blurry sibling and records scores in meta" do
    stub_checks(faces: [face, face], sharpness: [soft, sharp])

    expect { described_class.call(order) }
      .to change { order.reload.status }.to("waiting_for_parent")
      .and have_enqueued_mail(OrderMailer, :missing_data).once

    event = order.events.order(:id).last
    expect(event.kind).to eq("waiting_for_parent")
    expect(event.meta["issues"]).to contain_exactly(
      a_hash_including("child_id" => kasia.id, "position" => 0, "code" => "blurry",
        "face_score" => 0.93, "sharpness" => soft.round(1))
    )
  end

  it "builds one paragraph per problem and a plural subject for siblings" do
    stub_checks(faces: [nil, face], sharpness: [soft])

    perform_enqueued_jobs { described_class.call(order) }

    mail = ActionMailer::Base.deliveries.last
    expect(mail.subject).to eq("Potrzebujemy nowych zdjęć: Kasia i Antek")
    expect(mail.text_part.body.to_s)
      .to include("Kasia: na przesłanym zdjęciu nie widać wyraźnie twarzy")
      .and include("Antek: przesłane zdjęcie jest nieostre")
  end

  it "uses the singular subject when one child has a problem" do
    stub_checks(faces: [face, face], sharpness: [sharp, soft])

    perform_enqueued_jobs { described_class.call(order) }

    expect(ActionMailer::Base.deliveries.last.subject).to eq("Potrzebujemy jeszcze jednego zdjęcia: Antek")
  end

  it "reports missing_photo without running the detector for that child" do
    kasia.photo.purge
    stub_checks(faces: [face], sharpness: [sharp])

    described_class.call(order.reload)

    expect(Photos::FaceDetector).to have_received(:best_face).once
    expect(order.events.order(:id).last.meta["issues"].pluck("code")).to eq(["missing_photo"])
  end

  it "reports unreadable when the file cannot be decoded" do
    allow(Photos::PreparedImage).to receive(:open_attachment).and_raise(Photos::UnreadableImage, "bad jpeg")

    described_class.call(order)

    expect(order.reload.status).to eq("waiting_for_parent")
    expect(order.events.order(:id).last.meta["issues"].pluck("code")).to eq(%w[unreadable unreadable])
  end

  it "changes nothing when the order left data_checking meanwhile" do
    allow(Photos::FaceDetector).to receive(:best_face).and_return(nil)
    Order.where(id: order.id).update_all(status: "paid")

    expect { expect(described_class.call(order)).to be_nil }
      .to not_change { order.reload.status }
      .and not_change { order.events.count }
      .and not_have_enqueued_mail(OrderMailer, :missing_data)
  end

  it "re-raises technical errors and leaves the status" do
    allow(Photos::FaceDetector).to receive(:best_face).and_raise(RuntimeError, "onnx crashed")

    expect { described_class.call(order) }.to raise_error(RuntimeError, "onnx crashed")
    expect(order.reload.status).to eq("data_checking")
    expect(enqueued_jobs).to be_empty
  end
end
```

Add `RSpec::Matchers.define_negated_matcher :not_change, :change` to `spec/support/negated_matchers.rb` if it is not there yet. Mail jobs use the `:test` adapter like `stripe_event_handler_spec.rb`; include `ActiveJob::TestHelper` if `perform_enqueued_jobs` is not available globally.

- [ ] **Step 3: Implement service**

```ruby
# frozen_string_literal: true

module Orders
  # Checks every child's main photo and moves a data_checking order on (photos never leave the server).
  class PhotoQualityCheck
    def self.call(order)
      new(order).call
    end

    def initialize(order)
      @order = order
    end

    def call
      issues = @order.children.filter_map { |child| issue_for(child) }
      status = finalize(issues)
      # Separate queue database in production: enqueue only after the status commit.
      deliver_missing_data_mail(issues) if status == "waiting_for_parent"
      status
    end

    private

    def issue_for(child)
      base = { "child_id" => child.id, "position" => child.position }
      return base.merge("code" => "missing_photo") unless child.photo.attached?

      Photos::PreparedImage.open_attachment(child.photo) do |image|
        face = Photos::FaceDetector.best_face(image)
        next base.merge("code" => "no_face") unless face

        sharpness = Photos::SharpnessScorer.score(
          image.crop(x: face.x, y: face.y, w: face.width, h: face.height)
        )
        next if sharpness >= Photos::Config.sharpness_min

        base.merge("code" => "blurry", "face_score" => face.score.round(3), "sharpness" => sharpness.round(1))
      end
    rescue Photos::UnreadableImage
      base.merge("code" => "unreadable")
    end

    # Returns the new status, or nil when another run already moved the order.
    def finalize(issues)
      @order.with_lock do
        next unless @order.status == "data_checking"

        status = issues.empty? ? "data_checked" : "waiting_for_parent"
        @order.update!(status: status)
        @order.events.create!(
          kind: status,
          message: I18n.t("orders.events.#{status}"),
          meta: issues.empty? ? {} : { "issues" => issues }
        )
        status
      end
    end

    def deliver_missing_data_mail(issues)
      children = @order.children.index_by(&:id)
      names = issues.map { |issue| children.fetch(issue["child_id"]).first_name }
      details = issues.zip(names).map { |issue, name|
        I18n.t("orders.photo_quality.issues.#{issue['code']}", name: name)
      }
      subject =
        if names.one?
          I18n.t("orders.photo_quality.mail_subject_one", name: names.first)
        else
          I18n.t("orders.photo_quality.mail_subject_many", names: names.join(I18n.t("mailers.common.name_join")))
        end

      OrderMailer.missing_data(@order, missing_details: details.join("\n\n"), subject: subject).deliver_later
    end
  end
end
```

Notes:
- `with_lock` reloads the order, so the guard sees a status changed by another run; `next` returns `nil` from the block (same idiom as `Order#mark_paid!`).
- The mail is enqueued only by the run whose `finalize` changed the status — at most one mail per check. A crash between commit and enqueue loses the mail (accepted for v1; the order is visibly `waiting_for_parent` in the panel).
- For more than two names `name_join` gives “Kasia i Zosia i Antek”; acceptable for v1 (max children per order is small).

- [ ] **Step 4: Run specs**

Run: `bin/rspec spec/services/orders/photo_quality_check_spec.rb`

Expected: PASS, no skips.

- [ ] **Step 5: Commit**

```bash
git add app/services/orders/photo_quality_check.rb \
  spec/services/orders/photo_quality_check_spec.rb spec/support/negated_matchers.rb config/locales/pl.yml
git commit -m "$(cat <<'EOF'
Check order photos and transition to data_checked or waiting_for_parent (6.7)

EOF
)"
```

---

### Task 8: `Orders::CheckPhotosJob`

**Files:**
- Create: `app/app/jobs/orders/check_photos_job.rb`
- Test: `app/spec/jobs/orders/check_photos_job_spec.rb`

**Interfaces:**
- Consumes: `order_id`
- Produces: `paid`→`data_checking` claim + event; delegates to `Orders::PhotoQualityCheck`; on a technical error writes `photo_check_failed` and re-raises; after `Photos::Config.max_check_attempts` failures since the latest claim moves the order to `review`

Two guards against duplicate work:
- `limits_concurrency` (Solid Queue) — the dispatcher can enqueue the same `paid` order every 5 minutes while the queue is backlogged; duplicates wait for the running job and then no-op on the finished status instead of running detection in parallel.
- Claim under `with_lock` — only the run that sees `paid` writes the `data_checking` event.

Why the attempt cap: `ApplicationJob` has no `retry_on`, so a raised error just lands in Solid Queue failed executions. Recovery is the stale re-dispatch (Task 9), and since a failure does not touch `orders.updated_at`, a permanently broken order would be re-dispatched every 5 minutes forever. The cap stops that and puts the order in front of the operator (`review`). Setting the order back to `paid` (operator workaround) writes a new claim event and resets the count.

- [ ] **Step 1: Failing job spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Orders::CheckPhotosJob, type: :job do
  it "no-ops when order is not paid or data_checking" do
    order = create(:order, status: "data_checked")
    expect(Orders::PhotoQualityCheck).not_to receive(:call)

    described_class.perform_now(order.id)
  end

  it "no-ops for a missing order" do
    expect { described_class.perform_now(0) }.not_to raise_error
  end

  it "claims paid into data_checking then runs the check" do
    order = create(:order, status: "paid")
    expect(Orders::PhotoQualityCheck).to receive(:call) do |o|
      expect(o.reload.status).to eq("data_checking")
    end

    described_class.perform_now(order.id)

    expect(order.events.where(kind: "data_checking").count).to eq(1)
  end

  it "re-runs a stale data_checking order without a second claim event" do
    order = create(:order, status: "paid")
    allow(Orders::PhotoQualityCheck).to receive(:call) # simulates a crashed first run

    2.times { described_class.perform_now(order.id) }

    expect(Orders::PhotoQualityCheck).to have_received(:call).twice
    expect(order.events.where(kind: "data_checking").count).to eq(1)
  end

  it "is a no-op once the check finished" do
    order = create(:order, status: "paid")
    allow(Orders::PhotoQualityCheck).to receive(:call) { |o| o.update!(status: "data_checked") }

    2.times { described_class.perform_now(order.id) }

    expect(Orders::PhotoQualityCheck).to have_received(:call).once
  end

  it "records a technical failure, re-raises and keeps data_checking" do
    order = create(:order, status: "paid")
    allow(Orders::PhotoQualityCheck).to receive(:call).and_raise(RuntimeError, "onnx crashed")

    expect { described_class.perform_now(order.id) }.to raise_error(RuntimeError)

    expect(order.reload.status).to eq("data_checking")
    expect(order.events.where(kind: "photo_check_failed").last.meta).to eq("error" => "RuntimeError")
  end

  it "moves to review after max_check_attempts failures since the claim" do
    order = create(:order, status: "paid")
    allow(Orders::PhotoQualityCheck).to receive(:call).and_raise(RuntimeError)

    Photos::Config.max_check_attempts.times do
      expect { described_class.perform_now(order.id) }.to raise_error(RuntimeError)
    end

    expect(order.reload.status).to eq("review")
    expect(order.events.order(:id).last.kind).to eq("review")
    expect { described_class.perform_now(order.id) }.not_to raise_error # review is not picked up again
  end

  it "declares a per-order concurrency limit" do
    expect(described_class.concurrency_limit).to eq(1)
    expect(described_class.new(42).concurrency_key).to include("42")
  end
end
```

The `:test` adapter ignores `limits_concurrency`, so the last example only checks the declaration; real blocking is a Solid Queue guarantee. Adjust `concurrency_key` expectations to the Solid Queue 1.7 API if the method name differs.

- [ ] **Step 2: Implement job**

```ruby
# frozen_string_literal: true

module Orders
  class CheckPhotosJob < ApplicationJob
    queue_as :default

    # One run per order at a time: dispatcher duplicates wait, then no-op on a finished status.
    limits_concurrency to: 1, key: ->(order_id) { "check_photos/#{order_id}" }, duration: 15.minutes

    def perform(order_id)
      order = Order.find_by(id: order_id)
      return unless order && claim(order)

      begin
        Orders::PhotoQualityCheck.call(order)
      rescue StandardError => error
        record_failure(order, error)
        raise
      end
    end

    private

    # true when this run should check photos: paid (claim now) or data_checking (re-run).
    def claim(order)
      order.with_lock do
        case order.status
        when "paid"
          order.update!(status: "data_checking")
          order.events.create!(kind: "data_checking", message: I18n.t("orders.events.data_checking"))
          true
        when "data_checking"
          true
        else
          false
        end
      end
    end

    # Error class only in meta (messages may carry paths); full error stays in Solid Queue.
    def record_failure(order, error)
      order.with_lock do
        next unless order.status == "data_checking"

        order.events.create!(
          kind: "photo_check_failed",
          message: I18n.t("orders.events.photo_check_failed"),
          meta: { "error" => error.class.name }
        )
        next if failures_since_claim(order) < Photos::Config.max_check_attempts

        order.update!(status: "review")
        order.events.create!(
          kind: "review",
          message: I18n.t("orders.events.review"),
          meta: { "reason" => "photo_check_failed" }
        )
      end
    end

    def failures_since_claim(order)
      claimed_at = order.events.where(kind: "data_checking").maximum(:id) || 0
      order.events.where(kind: "photo_check_failed").where("id > ?", claimed_at).count
    end
  end
end
```

If `record_failure` itself raises (e.g. the database is down), that error propagates with the original as `cause`; the stale re-dispatch retries later.

- [ ] **Step 3: Run spec**

Run: `bin/rspec spec/jobs/orders/check_photos_job_spec.rb`

- [ ] **Step 4: Commit**

```bash
git add app/jobs/orders/check_photos_job.rb spec/jobs/orders/check_photos_job_spec.rb
git commit -m "$(cat <<'EOF'
Claim paid orders into data_checking and cap failed photo checks (6.7)

EOF
)"
```

---

### Task 9: Dispatcher job + recurring schedule

**Files:**
- Create: `app/app/jobs/orders/dispatch_photo_checks_job.rb`
- Modify: `app/config/recurring.yml`
- Test: `app/spec/jobs/orders/dispatch_photo_checks_job_spec.rb`

**Interfaces:**
- Produces: enqueues `CheckPhotosJob` for each `paid` order and each `data_checking` with `updated_at < Time.current - Photos::Config.stale_checking_after`

- [ ] **Step 1: Failing dispatcher spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Orders::DispatchPhotoChecksJob, type: :job do
  include ActiveJob::TestHelper

  it "enqueues check jobs for paid orders" do
    paid = create(:order, status: "paid")
    create(:order, status: "data_checked")
    create(:order, status: "review") # capped technical failures are never re-dispatched

    expect {
      described_class.perform_now
    }.to have_enqueued_job(Orders::CheckPhotosJob).with(paid.id).once
  end

  it "re-enqueues stale data_checking orders" do
    stale = create(:order, status: "data_checking", updated_at: 1.hour.ago)
    fresh = create(:order, status: "data_checking", updated_at: Time.current)

    expect {
      described_class.perform_now
    }.to have_enqueued_job(Orders::CheckPhotosJob).with(stale.id)

    expect(Orders::CheckPhotosJob).not_to have_been_enqueued.with(fresh.id)
  end
end
```

(Adjust matcher if `have_been_enqueued` needs `ActiveJob::TestHelper` assertions differently — use `enqueued_jobs` array if needed.)

- [ ] **Step 2: Implement dispatcher**

```ruby
# frozen_string_literal: true

module Orders
  class DispatchPhotoChecksJob < ApplicationJob
    queue_as :default

    def perform
      ids = Order.where(status: "paid").pluck(:id)
      stale = Order.where(status: "data_checking")
        .where("updated_at < ?", Photos::Config.stale_checking_after.ago)
        .pluck(:id)

      (ids + stale).uniq.each do |id|
        CheckPhotosJob.perform_later(id)
      end
    end
  end
end
```

- [ ] **Step 3: Recurring config**

In `config/recurring.yml` under `production:` (and optionally `development:`):

```yaml
  dispatch_photo_checks:
    class: Orders::DispatchPhotoChecksJob
    queue: default
    schedule: every 5 minutes
```

Confirm Solid Queue recurring is enabled in the deploy/process setup (`SOLID_QUEUE_IN_PUMA` / separate worker) — do not change Kamal unless needed for a running worker.

- [ ] **Step 4: Run specs**

Run: `bin/rspec spec/jobs/orders/dispatch_photo_checks_job_spec.rb`

- [ ] **Step 5: Commit**

```bash
git add app/jobs/orders/dispatch_photo_checks_job.rb \
  spec/jobs/orders/dispatch_photo_checks_job_spec.rb config/recurring.yml
git commit -m "$(cat <<'EOF'
Dispatch photo checks every five minutes for paid orders (6.7)

EOF
)"
```

---

### Task 10: End-to-end job path + docs touch-up

**Files:**
- Test: `app/spec/jobs/orders/photo_quality_pipeline_spec.rb` (optional integration)
- Update: `app/AGENTS.md` one line under Order statuses mentioning `data_checking` photo check
- Update (parent repo): `docs/superpowers/specs/2026-11-14-photo-quality-check-design.md`, `szablony/emaile.md`, `AUTOMATYZACJA.md`

- [ ] **Step 1: Integration-style spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe "photo quality pipeline", type: :job do
  include ActiveJob::TestHelper

  it "goes paid → data_checking → data_checked via dispatcher and check job" do
    path = Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg")
    skip "fixture missing" unless path.exist?

    # Child requires a photo, so replace the factory one instead of building without it.
    order = create(:order, status: "paid")
    order.children.first.photo.attach(io: File.open(path), filename: "sharp_face.jpg", content_type: "image/jpeg")

    perform_enqueued_jobs do
      Orders::DispatchPhotoChecksJob.perform_now
    end

    expect(order.reload.status).to eq("data_checked")
  end
end
```

- [ ] **Step 2: Run full related suite + rubocop**

```bash
bin/rspec spec/services/photos spec/services/orders/photo_quality_check_spec.rb spec/jobs/orders
bin/rubocop
```

Expected: green.

- [ ] **Step 3: Commit**

```bash
git add spec/jobs/orders/photo_quality_pipeline_spec.rb AGENTS.md
git commit -m "$(cat <<'EOF'
Cover photo quality pipeline from dispatcher to data_checked (6.7)

EOF
)"
```

- [ ] **Step 4: Sync parent-repo docs (required)** — commit in the parent repo `Miko/`, separately from `app/`:
  - design spec: add issue code `unreadable`; replace “Solid Queue retries” with the stale re-dispatch + `max_check_attempts` cap → `review` (remove “Moving technical failures to review” from Out); mention `limits_concurrency`; mail enqueued after the lock block (separate queue DB).
  - `szablony/emaile.md`: mail 2 variants without `{IMIE_DLA}` (“Kasia: …” paragraphs, new subjects) plus the `unreadable` and `no_face` variants.
  - `AUTOMATYZACJA.md` operator workaround: an order in `review` after failed checks is reset the same way (fix the cause, set `paid`).
  - Plus any threshold or behaviour change made during implementation.

---

## Spec coverage checklist

| Spec requirement | Task |
|---|---|
| Status `data_checking` | 1 |
| Config thresholds + stale minutes | 2 |
| Stock fixtures only | 3 |
| EXIF autorot | 4 |
| Sharpness on face crop | 5 + 7 |
| YuNet ONNX local | 6 |
| Issue codes + mail 2 | 7 |
| Lock claim paid→checking | 8 |
| 5-minute dispatcher + stale re-queue | 9 |
| No enqueue from `mark_paid!` | 8–9 (never touch mark_paid) |
| Only main `photo` | 7 |
| Tech errors stay `data_checking` / raise | 7–8 (capped → `review`, Task 8) |
| Undecodable file → `unreadable` + mail 2 | 4 + 7 (deviation) |
| Concurrency: one claim, one mail max | 7 (finalize guard) + 8 (`limits_concurrency`, claim lock) |
| Mail after status commit | 7 |
| Operator workaround documented | already in AUTOMATYZACJA + design |

## Self-review notes

- No `mark_paid!` changes — intentional.
- Threshold numbers in YAML are starting points; Task 6 calibrates the **production** values against stock fixtures (no `test:` overrides).
- First deploy sweeps every existing `paid` order — accepted: production has not launched yet, so there are no real orders to re-check.
- YuNet NMS details stay inside Task 6; public API is stable for Task 7.
- Two git roots: commit Rails work in `app/`, docs in parent `Miko/`.
