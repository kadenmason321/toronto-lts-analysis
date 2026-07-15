# LTS Project — Decisions Log

Plain-language record of the choices made and why, for my own reference
and for defending this project later.

---

## Why Furth/Mekuria's LTS framework?
It's the standard the field actually uses — still cited as the basis for
current AASHTO and NACTO bike facility guidance. No single "more modern"
replacement exists; instead, the field has splintered into many variants
of the same framework, because everyone adapts it to whatever data they
have available. I'm doing the same thing, not cutting a unique corner.

## Why link-level only (no intersections)?
Intersection stress needs data (turn lanes, signal timing) that OpenStreetMap
doesn't reliably have. The published intersection criteria are also
described in the literature as thin and largely unchanged since 2012 — it's
a real open problem in the field, not something I skipped out of laziness.
Deliberately scoped out as a v2 item.

## Why OpenStreetMap only, no traffic volume (ADT) data?
The original 2012 framework uses up to ~18-21 variables, most of which
aren't available anywhere as open data. Reducing it to what's computable
from OSM follows an established pattern other researchers/tools have used
(Conveyal 2015, Lowry/Furth/Hadden-Loh 2016, PeopleForBikes) — I'm not
inventing this simplification, I'm following precedent.

The consequence: traffic volume (ADT) isn't a factor in my mixed-traffic
scoring, even though the original methodology uses it. Documented
limitation, not an oversight.

## Why config files instead of hardcoding each city?
So the scoring logic itself never has to change to support a new city —
only a config file does. Proven this works by running the identical code
against Toronto, Vancouver, and Corvallis without touching the rule engine.

## Why did I write my own numeric thresholds instead of using Furth's tables directly?
Furth's published criteria tables are images, not machine-readable data.
I translated the published bands into explicit numeric rules, documented
in `lts_rules.py`. This is standard practice — most real-world LTS tools
do the same thing for the same reason.

## Why does a one-way street get double the lane count?
A one-way street's traffic isn't split by an opposing lane/median the way
a two-way street's is, so it behaves more like a wider road than its raw
lane count suggests. Furth's methodology handles this by doubling the
effective lane count for one-way streets before scoring. Known
oversimplification: doesn't account for narrow one-way residential
streets that are one-way *because* they're calm, not because they're busy.

## Why are the missing-data defaults what they are?
When a street has no `maxspeed` or `lanes` tag (about 23% of streets are
missing maxspeed in Toronto), I fall back to typical values by road type
(e.g. residential = 30 km/h). These are reasonable assumptions, not
independently verified against each city's actual bylaws — this is a
real limitation I should state plainly rather than let the output look
more precise than it is.

## Why only 2 real-world validation checks so far?
Time-boxed first pass. Bloor St and Danforth Ave bike lanes both correctly
scored LTS 1, which validates the core pipeline works — but 2 checks is a
demo, not evidence. Next step is a proper validation set (8-10 corridors,
predicted score before checking) plus an informal poll of real cyclists.

## What surprised me / genuine findings, not just plumbing
- Corvallis test revealed that a completely standard US 25mph residential
  street can't score LTS 1 under my current thresholds — only streets
  ≤30 km/h (≈18.6 mph) can. Not a bug — a real, visible consequence of
  where I set the threshold, and worth discussing directly rather than
  hiding.
- OSMnx silently drops cycleway tags by default unless you explicitly
  tell it to keep them — a good example of a tool behaving in a way
  that looks like a data problem but is actually a tool-configuration
  problem. Worth checking for tool-default gotchas generally.

## What's explicitly NOT in scope right now
Intersection-level stress, driver stress, pedestrian stress, route
optimization, field verification. All reasonable v2 directions, not
being pursued yet so the link-level model gets solid first.

## Finding: full-city run reveals a bike infrastructure equity gap (added after full Toronto run)
Expanding from Old Toronto to the full amalgamated city (27,401 nodes,
73,015 edges vs. 5,779/15,161 for Old Toronto alone) surfaced a real
citywide pattern, not just more data:

- Protected bike infrastructure dropped from 4.4% of edges (Old Toronto)
  to 1.7% citywide
- Painted bike lanes dropped from 8.0% to 3.4% citywide
- Mixed traffic (no dedicated cycling facility) rose to 95% of all
  edges citywide, up from 87.5% in Old Toronto alone

Overall LTS distribution stayed roughly flat (~58% LTS 1 both times) —
my prediction that it would rise citywide (more quiet residential
suburbs) didn't hold. Likely explanation: the inner suburbs add both
more quiet local streets AND more wide, fast arterials (Eglinton,
Finch, Sheppard, Lawrence), roughly cancelling out in the aggregate
LTS 1 percentage even though the underlying street character is very
different from downtown.

LTS 4 (highest stress) share grew from ~4% to ~11% of edges citywide —
a real, meaningful increase, consistent with more wide/fast suburban
arterials entering the dataset.

Takeaway for the write-up: Toronto's cycling infrastructure is heavily
concentrated in the downtown/Old Toronto core. This is a genuine
citywide equity finding, not just a data quality note — worth stating
plainly rather than only presenting the flat overall LTS distribution,
which on its own would understate how uneven the underlying
infrastructure actually is.

## Finding: LTS-1 threshold sensitivity is a cliff, not a gradient
Ran a sensitivity analysis on the LTS-1 speed threshold (20/25/30/35/40
km/h) across the full Toronto network (71,934 edges). Result:

| Threshold (km/h) | LTS 1 % |
|---|---|
| 20 | 1.9% |
| 25 | 2.0% |
| 30 | 58.0% |
| 35 | 58.0% |
| 40 | 75.8% |

The model is NOT smoothly sensitive to this threshold — it's a cliff.
Moving from 25 to 30 km/h alone shifts 56 percentage points of the
network from LTS 2 to LTS 1. This is because Toronto's actual posted/
default residential speed limit is 30 km/h almost everywhere, so a
huge fraction of edges carry exactly that speed value (whether tagged
or defaulted). The LTS-1 threshold isn't cutting through a smooth
distribution — it's sitting directly on top of the single most common
speed value in the dataset.

Practical implication: this model's LTS-1 rate is highly sensitive to
whether ≤30 km/h counts as "low stress" or not -- essentially a
referendum on Toronto's own default speed policy rather than a stable,
robust model output. Worth stating plainly in the write-up rather than
presenting the 58% LTS-1 figure as if it were a precise, robust
measurement.
