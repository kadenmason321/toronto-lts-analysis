# LTS Project — Roadmap

Goal: complete before next week.

---

## Phase 1: Polish LTS (make the existing thing actually done)
Target: 1 solid session, ~2-3 hours

- [x] Full Toronto run (not just Old Toronto)
- [ ] Real validation set — 8-10 corridors, predict-then-check
- [ ] Informal cyclist survey (drafted, ready to send — 8 streets, 1-4 scale)
- [x] Threshold sensitivity check + write up findings
- [ ] Styled poster map (QGIS, matching unrun-streets aesthetic)
- [ ] Methodology write-up (decisions.md is the raw material)
- [ ] Push to GitHub with a real README

**Exit condition:** could email this to Metrolinx or Corvallis relative today
without caveats. Do not start Phase 2 until this is genuinely true.

---

## Phase 2: Low-stress connectivity analysis
Target: 1-2 sessions

- [ ] Load scored network into NetworkX (same pattern as unrun-streets)
- [ ] Filter to LTS 1-2 edges only -> "low-stress subgraph"
- [ ] Pick sample origin-destination pairs (neighborhoods -> downtown /
      transit hubs)
- [ ] Compare shortest path on full network vs. low-stress-only network
- [ ] Visualize where forcing low-stress routing causes big detours or
      makes trips impossible -> "missing link" candidates
- [ ] Add section to write-up citing Furth's own low-stress connectivity
      follow-up work (2016, 2018)

**Exit condition:** can point at a specific map location and say "this is
a documented gap in Toronto's low-stress network," with numbers behind it.

---

## Phase 3: Interactive public-facing tool
Target: 1-2 sessions (most unfamiliar territory)

- [ ] Leaflet or Folium web map, colored by LTS score, standalone HTML
- [ ] Click-to-inspect: score, facility type, and why
- [ ] Optional: toggle low-stress-only view (Phase 2 integration)
- [ ] Deploy via GitHub Pages -> real public URL for resume/portfolio

**Exit condition:** a link that opens directly in a browser, no setup
required on the other end.

---
---

## Phase 4: Temporal + economic + demand context (future, not yet scheduled)
Captured for later — do not start until Phases 1-3 are done. Risk of
scope creep is high here; each of these is roughly its own project.

### Temporal (infrastructure recency)
- OSM doesn't reliably tag install dates — use Toronto Open Data's
  cycling network dataset instead (has install year for many segments)
- This becomes a second data source merged into the pipeline, not
  something derivable from current OSM-only approach
- Output: map/stat showing how old the existing low-stress network is
- Smallest, most contained piece of Phase 4 — could be a single
  afternoon add to the Phase 1 write-up rather than a full phase

### Economic (cost)
- Do NOT invent dollar figures — not defensible without real
  engineering cost data
- Instead: relative cost TIERS (paint-only < buffered lane < physical
  protection), sourced from Toronto's own published cycling network
  capital plan if unit costs are cited there
- Goal: "upgrading X is a bigger lift than upgrading Y," not precise
  budgets

### Usage / ridership potential (the big one)
- This is a demand-modeling problem, not an LTS problem — roughly as
  much work as the entire LTS build (gravity models, population/
  employment density weighting, distance decay from transit)
- Most valuable of the three if done well: LTS says "this street is
  stressful," this would say "and here's how many people fixing it
  would actually help"
- Deserves to be its own dedicated project phase, not a casual add

### How Phase 4 items detract from modularity (know this before starting)
- All three break the "one universal OSM data source" pattern that
  makes the current tool portable — each introduces a SECOND,
  city-specific data source (Toronto Open Data, local cost plans,
  population/transit data) that won't have an equivalent in every city
- If pursued, frame explicitly as a Toronto case study extension,
  clearly separated from the core portable LTS engine — don't imply
  the whole tool is equally portable once these are added
-----
---

## Phase 5: Modularity-strengthening additions (future, not yet scheduled)
Unlike Phase 4, these strengthen the "one universal data source, config-
driven" story rather than diluting it. Prioritize these before Phase 4
if choosing what to build next after Phase 1-3.

### European city test (highest-value modularity proof remaining)
- Toronto/Vancouver tested unit conventions (km/h), Corvallis tested
  mph — none tested a genuinely different OSM TAGGING CULTURE
- Netherlands or Germany: OSM cycling infrastructure tagging is
  unusually mature/detailed there — good stress test for whether the
  config's tag-mapping assumptions hold up, not just unit conversion
- This is the test most likely to actually reveal a gap in the config
  schema, since it's a different kind of test than the first three
  cities, not just another repetition

### Auto-detect reasonable defaults from the data itself
- Currently: defaults.speed_by_highway / defaults.lanes_by_highway are
  hand-typed guesses per city (Vancouver's were literally copy-pasted
  from Toronto's, unverified)
- Better: for a new city, compute the MEDIAN tagged speed/lane count
  per highway type from whatever real OSM data IS present in that
  city, use that as the default instead of a manual guess
- Falls back to a hardcoded value only if there's not enough real
  tagged data to compute a median
- Makes onboarding a new city partially self-calibrating instead of
  requiring manual research of each city's typical speeds/lanes
- Also strengthens the "how rigorous is this really" answer for any
  city, not just new ones

### Config validator / linter
- Small script: checks a new city config for completeness before
  attempting to run it (all required keys present, defaults are
  plausible numbers, no cycleway values referenced that aren't
  defined in the mapping)
- Supports the modularity claim directly — tooling FOR onboarding new
  cities, which is the thing being claimed is easy
- Also just useful the next time a config has a subtle typo

### Effort score (separate axis from LTS stress, NOT blended into it)
Keep as its own score — a hilly protected bike lane and a flat street
with no bike lane are different problems needing different fixes.
Blending into one number would blur the clarity that makes LTS
defensible.

Three factors, roughly in order of ease:
- Surface type/quality: OSM `surface` tag (paved/gravel/cobblestone/
  dirt) — already present in pulled data, zero new infrastructure
  needed, cheapest possible add
- Stop frequency: OSM traffic_signals / stop tags on nodes along the
  network — also already in pulled data, measures a real effort cost
  (accel/decel) that neither LTS nor grade capture
- Grade/elevation: needs external data, but genuinely global/open —
  use Copernicus GLO-30 DEM (better than older SRTM) rather than
  building custom terrain data

### Other global open data worth knowing about (not necessarily using yet)
- Copernicus GLO-30 DEM — elevation, for effort score above
- ESA WorldCover — 10m global land cover incl. tree canopy class,
  relevant if ever revisiting "enjoyability/shade" idea
- WorldPop / Global Human Settlement Layer (GHSL) — global population
  density, relevant to Phase 4's ridership/demand modeling idea, not
  effort
- Explicitly NOT recommended: wind/climate data (ERA5) — direction-
  and time-dependent, breaks the static per-segment score model the
  whole tool is built on
---

## Phase 6: Uncertainty mapping (future, not yet scheduled)
Makes data confidence visible instead of silent. Currently the pipeline
uses defaults/assumptions when data is missing but discards that
information immediately — it's known internally for a split second and
then thrown away. This phase keeps it and turns it into its own layer.

Track, per segment, whether each of these came from a real tag or a
fallback/assumption:
- Speed: real maxspeed tag vs. config default used
- Lane count: real lanes tag vs. config default used
- Parking: explicit tag present vs. assumed absent (no tag at all) —
  these are different kinds of guesses, worth distinguishing
- (Facility type already effectively has this — "mixed" is both a real
  finding and the fallback when no cycleway tag exists at all; may be
  worth splitting those two cases apart too)

Output: an uncertainty score per segment (e.g. count of the above that
were assumed rather than real, 0-4), rendered as its own map layer
alongside the LTS score map — shows WHERE the model is guessing, not
just how often, in aggregate, across the whole city.

Directly extends the "% of low-stress streets that relied on a default
vs. a real tag" stat from the evidence/validation work — this makes
that number spatial and inspectable instead of a single aggregate
figure.

Good pairing with the poster map work in Phase 1 — a confidence map
next to the LTS map is a strong, honest pair for a portfolio piece.
---

## Phase 7: Automated validation tooling (future, not yet scheduled)
Two distinct kinds of validation — keep them separate, they're solved
differently.

### A. Config/data validation (fully automatable)
Overlaps with the "config validator/linter" idea in Phase 5 — expand it
into a proper pre-flight check script, run before fetch/score:
- All required config keys present (catches the KeyError-crash class of
  bug from earlier today)
- Defaults are plausible numbers (e.g. speed_by_highway values are
  positive, under some sane ceiling like 150 km/h)
- No cycleway/parking values referenced in tags that aren't defined in
  the corresponding mapping dict
- After a fetch: sanity-check the raw GraphML itself (non-zero edges,
  required OSM columns present) before scoring runs on it

This can be a real pytest-style test suite, not just a manual script —
genuinely portfolio-relevant on its own ("I wrote automated tests for
my data pipeline" is a real engineering signal, separate from the GIS
content).

### B. Model/ground-truth validation (partially automatable)
Can't be fully automated — requires real-world ground truth, which is
external to the codebase. But the COMPARISON step can be:
- Maintain a small validation CSV: street name, coordinates or way ID,
  expected LTS score (from personal knowledge + the cyclist survey),
  source/reasoning
- Write a script that looks up each validation street's actual scored
  segment(s) in the output and reports match/mismatch automatically,
  rather than manually eyeballing in QGIS every time
- Re-run this automatically any time the rule engine or a config
  changes — turns validation into a regression test: "did this
  threshold tweak break something that used to be right?"
- This is the coded version of the validation table from the evidence/
  discussion work — same data, but checked by script instead of by eye

Together, A + B mean: config errors get caught before a run wastes
time, and score changes get checked against known-correct answers
automatically instead of requiring a fresh manual QGIS pass each time.

---

## Phase 8: Failure analysis (future, not yet scheduled)
Explicit, deliberate answer to "what does this NOT do well" — stronger
if written proactively than if an interviewer has to extract it.

Candidates to investigate and document:
- Streets that change character mid-block (speed limit or facility type
  shifts partway) — our simplification takes worst-case per edge, may
  misrepresent long OSM-simplified segments that span multiple real
  conditions
- Contraflow bike lanes — asymmetric treatments, does get_facility_type
  handle these correctly or silently miss them?
- Roundabouts — Furth has separate draft criteria for these (2014) that
  we haven't implemented at all; check how our mixed-traffic fallback
  scores them, likely wrong
- Streets with cycleway tagged only on ONE side (asymmetric) — are we
  applying weakest-link logic correctly per Furth's guidance, or
  accidentally scoring both directions the same?
- Any street where posted speed diverges significantly from actual
  traffic speed (arterials in commercial areas, etc.) — known
  limitation already, but worth finding concrete Toronto examples
- Segments with high uncertainty score (Phase 6) that also got an
  LTS 1 or 2 — these are the "how much are we trusting an assumption"
  cases most worth flagging specifically, not just in aggregate

Deliverable: a short "known limitations, with examples" section for the
write-up — a few real, named streets where the model demonstrably gets
it wrong or is on shaky ground, with a plain explanation of why. More
credible than a generic disclaimer paragraph.

---

## Phase 9: Case studies — real trip scenarios, per city (future, not
yet scheduled)
Complements the connectivity work (Phase 2) with concrete, narrative
examples — answers "so what can I actually DO with this" in a way a
distribution table can't.

Format: pick a realistic origin-destination trip per city, run it
through the low-stress network (Phase 2 routing), and narrate the
result plainly.

Toronto example: "Can someone bike comfortably from High Park to Union
Station?" — show the low-stress route (if one exists), where it detours
around high-stress segments, how much longer it is than the direct
route, and where the network forces a stress compromise if no full
low-stress path exists.

Do 1-2 per city (Toronto, Vancouver, Corvallis, eventually the European
test city) — a common trip type per city (e.g. residential neighborhood
to downtown/transit hub) makes a nice small-multiples comparison, and
doubles as another portability proof: same case-study SCRIPT, different
city's data.

Good candidate for the interactive tool (Phase 3) — could literally be
a "try a route" feature rather than just a static write-up example.

## Sequencing note
Do not skip to Phase 3 early. An interactive map of an unvalidated model
is a worse portfolio piece than a static poster of a validated one.
Phase 1 first, no exceptions.
