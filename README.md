# Personalized Yoga Asana Recommendation System

**B.Tech Project (Jan ’24 → Jun ’24)** • **Advisor:** Assistant Prof. **Veena Kumari**
**Stack:** Python · **FastAPI** · Pydantic · (optional) Redis cache · pytest · GitHub Actions

> FastAPI service that returns **top-3 personalized poses** and **full routines**.
> Median end-to-end latency: **\~1.8 s** (cold start excluded).

---

## What it does

* **Personalized recommendations:** Given a short user profile (level, goals, time, injuries, equipment), the API returns:

  * **Top-3 poses** with reasons and contraindication flags.
  * A **complete routine** (warm-up → main flow → cool-down) sized to the requested duration.
* **Production hygiene:** strict input validation, caching, and robust error handling to reduce bad requests and improve stability.
* **Ops ready:** unit/integration tests, lightweight CI, structured logs, and basic metrics for quick failure triage.

---



---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload  # http://127.0.0.1:8000/docs (Swagger)
```

**Optional Redis cache**

```bash
# set REDIS_URL to enable shared cache, otherwise in-process LRU is used
export REDIS_URL=redis://localhost:6379/0
```

---

## API (FastAPI)

### POST `/recommend`

**Request (JSON)**

```json
{
  "level": "beginner",          // beginner | intermediate | advanced
  "goals": ["flexibility", "stress_relief"],
  "duration_min": 20,           // 10–60
  "focus_areas": ["hamstrings", "hips"],
  "injuries": ["lower_back_pain"],   // used for contraindication filters
  "equipment": ["mat", "block"],
  "preferences": {"pace": "gentle", "include_breathing": true}
}
```

**Response (JSON)**

```json
{
  "top_poses": [
    {"id": "uttanasana", "name": "Standing Forward Fold", "reasons": ["hamstrings", "flexibility"], "flagged_contra": false},
    {"id": "baddha_konasana", "name": "Bound Angle Pose", "reasons": ["hips", "stress_relief"], "flagged_contra": false},
    {"id": "supta_padangusthasana", "name": "Reclining Hand-to-Big-Toe", "reasons": ["hamstrings"], "flagged_contra": true}
  ],
  "routine": {
    "duration_min": 20,
    "sections": {
      "warmup":   ["cat_cow", "childs_pose", "easy_twist"],
      "mainflow": ["low_lunge", "lizard", "uttanasana", "baddha_konasana"],
      "cooldown": ["supine_twist", "legs_up_the_wall", "savasana"]
    }
  },
  "notes": [
    "Avoid deep flexion if lower_back_pain is acute; use blocks in uttanasana.",
    "Breath cues included; keep gentle pace."
  ],
  "trace": {"cached": false, "p50_ms": 1800}
}
```

---

## Recommendation logic (summary)

1. **Validate & normalize** request via **Pydantic**; reject impossible combos early (e.g., duration < 5).
2. **Filter** pose catalog by:

   * level and equipment availability,
   * **contraindications** derived from injuries/conditions,
   * focus areas and goal tags.
3. **Score** remaining poses with a weighted function:

   * goal match, focus-area coverage, level fit, transition smoothness, novelty/diversity.
4. **Top-3** = best three distinct poses with coverage diversity.
5. **Routine assembly**:

   * **Warm-up** (spine/breath), **Main flow** (progression in difficulty), **Cool-down** (down-regulation).
   * Time-box to `duration_min` using per-pose default seconds and transitions.
6. **Caching**: key = hash of normalized request + catalog version; TTL configurable.

> Guardrails: never return poses failing hard contraindications; fallback to safest substitutes and annotate `flagged_contra`.

---

## Pose catalog schema (`poses.yaml`)

```yaml
- id: "uttanasana"
  english: "Standing Forward Fold"
  sanskrit: "Uttānāsana"
  difficulty: 1           # 1–5
  focus_areas: ["hamstrings", "spine"]
  goals: ["flexibility", "stress_relief"]
  equipment: ["mat", "block?"]
  duration_s: 45
  transitions_to: ["ardha_uttanasana","low_lunge"]
  contraindications:
    absolute: ["acute_lower_back_pain", "vertigo_severe"]
    caution:  ["pregnancy_trimester_3"]
```

---

## Testing & CI

```bash
pytest -q                      # fast unit & API tests (FastAPI TestClient)
pytest -q -k "integration"     # slower catalog/routine tests
```

**CI:** `.github/workflows/ci.yml` runs `pip install`, `pytest`, and lint (flake8/ruff).
**Fixtures** cover: input validation, contraindication filtering, time-boxing, and caching correctness.

---

## Observability

* **Structured logs** (json/logfmt) with `request_id`, route, status, latency.
* **Metrics** (optional Prometheus): request counts, errors, and latency histograms.
* **Trace fields** in responses (dev mode) show cache hits and timing to speed debugging.

---

## Performance

* **Median end-to-end ≈ 1.8 s** per request (catalog I/O + planning + response).
* Warm cache typically returns faster; cold starts include catalog load.

---

## Running in Docker

```bash
docker build -t yoga-asana-api .
docker run -p 8000:8000 -e REDIS_URL=redis://host.docker.internal:6379/0 yoga-asana-api
```

---

## Safety & disclaimer

This system is **for educational/wellness guidance only** and **not medical advice**.
If you have pain, injuries, or conditions, consult a qualified professional before practicing.

--

### Notes

* The service ships with sensible defaults; weights and guardrails are configurable in `app/recommender/rules.py`.
* To extend: add breathwork blocks, difficulty ramps per section, or a feedback loop to learn user preferences over time.
