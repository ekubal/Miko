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

## File structure

| Path (under `app/`) | Role |
|---|---|
| `app/models/order.rb` | Add `data_checking` to `STATUSES` |
| `config/photo_quality.yml` | Thresholds, model path, stale minutes |
| `app/services/photos/config.rb` | Read `config_for(:photo_quality)` |
| `app/services/photos/prepared_image.rb` | Download blob, auto-orient, expose RGB + face crop helpers |
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
      data_checked: Dane zdjęć sprawdzone
      waiting_for_parent: Czekamy na poprawkę od rodzica
```

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
- Produces: `Photos::Config.face_score_min`, `.face_min_relative_size`, `.sharpness_min`, `.stale_checking_after`, `.model_path` (Pathname)

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
  model_relative_path: vendor/models/face_detection_yunet_2023mar.onnx

development:
  <<: *default

test:
  <<: *default
  # Lower bar so tiny CI fixtures can pass sharpness once real stock faces exist;
  # detector specs will stub or use dedicated files under photos/.
  sharpness_min: 20.0

production:
  <<: *default
```

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

### Task 4: Prepared image (download + auto-orient)

**Files:**
- Create: `app/app/services/photos/prepared_image.rb`
- Test: `app/spec/services/photos/prepared_image_spec.rb`
- Gem already: `image_processing`, `libvips` in Docker

**Interfaces:**
- Consumes: ActiveStorage attachment or file path
- Produces: `Photos::PreparedImage.open(attachment) { |img| ... }` with `#width`, `#height`, `#with_vips`, `#crop_pixels(x,y,w,h)`, `#path` (oriented tempfile)

- [ ] **Step 1: Failing spec (orientation)**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::PreparedImage do
  it "applies EXIF orientation so rotated_face matches upright dimensions intent" do
    path = Rails.root.join("spec/fixtures/files/photos/rotated_face.jpg")
    skip "add rotated_face.jpg fixture" unless path.exist?

    described_class.open_path(path) do |image|
      # After autorot, width should be greater than height for a typical portrait shot stored as landscape+Orientation.
      expect(image.width).to be > 0
      expect(image.height).to be > 0
    end
  end
end
```

- [ ] **Step 2: Implement minimal PreparedImage**

```ruby
# frozen_string_literal: true

require "vips"
require "tmpdir"

module Photos
  class PreparedImage
    attr_reader :path, :width, :height

    def self.open_attachment(attachment, &block)
      raise ArgumentError, "photo missing" unless attachment&.attached?

      attachment.open do |file|
        open_path(file.path, &block)
      end
    end

    def self.open_path(path)
      Dir.mktmpdir("photo-prep-") do |dir|
        oriented = File.join(dir, "oriented.jpg")
        image = Vips::Image.new_from_file(path.to_s, access: :sequential)
        image = image.autorot
        image.write_to_file(oriented)
        prepared = new(oriented, image.width, image.height)
        yield prepared
      end
    end

    def initialize(path, width, height)
      @path = path
      @width = width
      @height = height
    end

    def with_vips
      Vips::Image.new_from_file(path, access: :sequential)
    end

    # x,y,w,h in pixels on the oriented image; clamps to bounds.
    def crop_to_tempfile(x:, y:, w:, h:)
      img = with_vips.crop(x, y, w, h)
      out = File.join(Dir.tmpdir, "face-crop-#{SecureRandom.hex(8)}.jpg")
      img.write_to_file(out)
      out
    end
  end
end
```

- [ ] **Step 3: Run spec**

Run: `bin/rspec spec/services/photos/prepared_image_spec.rb`

- [ ] **Step 4: Commit**

```bash
git add app/services/photos/prepared_image.rb spec/services/photos/prepared_image_spec.rb
git commit -m "$(cat <<'EOF'
Prepare photos with EXIF autorot for quality checks (6.7)

EOF
)"
```

---

### Task 5: Sharpness scorer

**Files:**
- Create: `app/app/services/photos/sharpness_scorer.rb`
- Test: `app/spec/services/photos/sharpness_scorer_spec.rb`

**Interfaces:**
- Consumes: filesystem path to JPEG/PNG crop or full image
- Produces: `Photos::SharpnessScorer.score(path) -> Float` (Laplacian variance)

- [ ] **Step 1: Failing spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Photos::SharpnessScorer do
  let(:sharp) { Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg") }
  let(:blurry) { Rails.root.join("spec/fixtures/files/photos/blurry_face.jpg") }

  it "scores a sharp image higher than a blurry one" do
    skip "stock fixtures missing" unless sharp.exist? && blurry.exist?

    expect(described_class.score(sharp)).to be > described_class.score(blurry)
  end
end
```

- [ ] **Step 2: Implement**

```ruby
# frozen_string_literal: true

require "vips"

module Photos
  module SharpnessScorer
    module_function

    # Variance of Laplacian — higher means sharper.
    def score(path)
      image = Vips::Image.new_from_file(path.to_s, access: :sequential)
      gray = image.colourspace("b-w")
      lap = gray.laplacian()
      # vips laplacian returns float image; variance via (mean of squares - mean^2)
      mean = lap.avg
      mean_sq = (lap**2).avg
      (mean_sq - (mean * mean)).to_f
    end
  end
end
```

Note: if `laplacian` API differs on the installed libvips, use `gray.conv(Vips::Image.new_from_array([[0,1,0],[1,-4,1],[0,1,0]]))` instead.

- [ ] **Step 3: Run spec; tune `sharpness_min` in `photo_quality.yml` so sharp passes and blurry fails in later tasks**

Run: `bin/rspec spec/services/photos/sharpness_scorer_spec.rb`

- [ ] **Step 4: Commit**

```bash
git add app/services/photos/sharpness_scorer.rb spec/services/photos/sharpness_scorer_spec.rb config/photo_quality.yml
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
- Produces: `Photos::FaceDetector.detect(prepared_image) -> Array<Photos::Face>`  
  `Photos::Face` = `Data.define(:x, :y, :width, :height, :score)` in oriented-image pixels  
- Pass filter later uses `Photos::Config` thresholds

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
end
```

- [ ] **Step 4: Implement Face + FaceDetector**

Implement YuNet input letterbox/resize to model input size, `OnnxRuntime::Model` run, decode boxes, NMS. Keep all logic inside `Photos::FaceDetector` (private class methods). Public API only:

```ruby
Photos::Face = Data.define(:x, :y, :width, :height, :score)

module Photos
  class FaceDetector
    def self.detect(prepared_image)
      new(prepared_image).detect
    end
    # ...
  end
end
```

Calibrate against fixtures; adjust `face_score_min` / `face_min_relative_size` as needed.

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
- Modify: `app/config/locales/pl.yml` (`orders.photo_quality` issue texts + mail subject helper keys)
- Test: `app/spec/services/orders/photo_quality_check_spec.rb`

**Interfaces:**
- Consumes: `Order` in `data_checking` (caller ensures claim)
- Produces: updates status to `data_checked` or `waiting_for_parent`, creates `OrderEvent`, enqueues mail 2 on failure  
- Issue codes: `missing_photo`, `no_face`, `blurry`

- [ ] **Step 1: Add I18n for mail bodies**

```yaml
  orders:
    photo_quality:
      mail_subject_one: "Potrzebujemy jeszcze jednego zdjęcia %{name}"
      mail_subject_many: "Potrzebujemy poprawki zdjęć (%{names})"
      issues:
        missing_photo: "Nie dotarło do nas zdjęcie %{name}. Dołącz je w odpowiedzi, najlepiej ostre, z twarzą widoczną na wprost, w formacie JPG lub PNG."
        no_face: "Na zdjęciu %{name} nie widać wyraźnie twarzy. W magicznej księdze potrzebujemy ostrego zdjęcia z twarzą widoczną na wprost."
        blurry: "Przesłane zdjęcie jest nieostre i twarz %{name} jest słabo widoczna. W magicznej księdze nie wyglądałoby dobrze. Najlepiej sprawdzi się ostre zdjęcie w świetle dziennym, z twarzą widoczną na wprost, w formacie JPG lub PNG."
```

- [ ] **Step 2: Failing service specs**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe Orders::PhotoQualityCheck do
  include ActiveJob::TestHelper

  def attach_stock!(child, filename)
    path = Rails.root.join("spec/fixtures/files/photos/#{filename}")
    skip "missing #{filename}" unless path.exist?
    child.photo.attach(io: File.open(path), filename: filename, content_type: "image/jpeg")
  end

  it "marks data_checked when the main photo is sharp with a face" do
    order = create(:order, status: "data_checking", attach_photos: false)
    child = order.children.first
    attach_stock!(child, "sharp_face.jpg")

    expect { described_class.call(order) }
      .to change { order.reload.status }.from("data_checking").to("data_checked")
    expect(order.events.order(:id).last.kind).to eq("data_checked")
  end

  it "marks waiting_for_parent and emails on blurry photo" do
    order = create(:order, status: "data_checking", attach_photos: false)
    attach_stock!(order.children.first, "blurry_face.jpg")

    expect {
      perform_enqueued_jobs { described_class.call(order) }
    }.to change { order.reload.status }.to("waiting_for_parent")

    expect(ActionMailer::Base.deliveries.last.subject).to include("zdję")
  end
end
```

- [ ] **Step 3: Implement service**

Core algorithm per child:

1. If `!child.photo.attached?` → issue `missing_photo`
2. `PreparedImage.open_attachment` → `FaceDetector.detect` → filter by score + `area/(w*h) >= face_min_relative_size`
3. If none → `no_face`
4. Else largest face by area → crop → `SharpnessScorer.score` → if `< sharpness_min` → `blurry`

Finalize under `order.with_lock` only if `status == "data_checking"`:

- no issues → `data_checked` + event  
- else → `waiting_for_parent` + event with `meta: { "issues" => [...] }` + `OrderMailer.missing_data(...).deliver_later`

Build `missing_details` by joining I18n paragraphs; subject from `mail_subject_one` / `mail_subject_many`.

Technical errors: re-raise (do not change status).

- [ ] **Step 4: Run specs**

Run: `bin/rspec spec/services/orders/photo_quality_check_spec.rb`

- [ ] **Step 5: Commit**

```bash
git add app/services/orders/photo_quality_check.rb \
  spec/services/orders/photo_quality_check_spec.rb config/locales/pl.yml
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
- Produces: `paid`→`data_checking` claim event; then delegates to `Orders::PhotoQualityCheck`

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

  it "claims paid into data_checking then runs the check" do
    order = create(:order, status: "paid")
    expect(Orders::PhotoQualityCheck).to receive(:call) do |o|
      expect(o.reload.status).to eq("data_checking")
    end
    described_class.perform_now(order.id)
    expect(order.events.where(kind: "data_checking")).to exist
  end
end
```

- [ ] **Step 2: Implement job**

```ruby
# frozen_string_literal: true

module Orders
  class CheckPhotosJob < ApplicationJob
    queue_as :default

    def perform(order_id)
      order = Order.find(order_id)

      order.with_lock do
        case order.status
        when "paid"
          order.update!(status: "data_checking")
          order.events.create!(
            kind: "data_checking",
            message: I18n.t("orders.events.data_checking")
          )
        when "data_checking"
          # retry / stale re-dispatch
        else
          return
        end
      end

      Orders::PhotoQualityCheck.call(order.reload)
    end
  end
end
```

- [ ] **Step 3: Run spec**

Run: `bin/rspec spec/jobs/orders/check_photos_job_spec.rb`

- [ ] **Step 4: Commit**

```bash
git add app/jobs/orders/check_photos_job.rb spec/jobs/orders/check_photos_job_spec.rb
git commit -m "$(cat <<'EOF'
Claim paid orders into data_checking before photo check (6.7)

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
- Parent docs already updated (`AUTOMATYZACJA.md`, design spec) — if operator workaround text drifts, sync
- Update: `app/AGENTS.md` one line under Order statuses mentioning `data_checking` photo check

- [ ] **Step 1: Integration-style spec**

```ruby
# frozen_string_literal: true

require "rails_helper"

RSpec.describe "photo quality pipeline", type: :job do
  include ActiveJob::TestHelper

  it "goes paid → data_checking → data_checked via dispatcher and check job" do
    path = Rails.root.join("spec/fixtures/files/photos/sharp_face.jpg")
    skip "fixture missing" unless path.exist?

    order = create(:order, status: "paid", attach_photos: false)
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

- [ ] **Step 4: Parent-repo note (optional)** — if anything in the design changed during implementation, update `docs/superpowers/specs/2026-11-14-photo-quality-check-design.md` in the parent repo and commit there separately.

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
| Tech errors stay `data_checking` / raise | 7–8 |
| Operator workaround documented | already in AUTOMATYZACJA + design |

## Self-review notes

- No `mark_paid!` changes — intentional.
- Threshold numbers in YAML are starting points; Task 5–6 calibrate against real stock fixtures.
- YuNet NMS details stay inside Task 6; public API is stable for Task 7.
- Two git roots: commit Rails work in `app/`, docs in parent `Miko/`.
