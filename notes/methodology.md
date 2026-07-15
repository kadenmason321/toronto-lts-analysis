# Toronto Cycling Stress Map: A Level of Traffic Stress Analysis

## Summary

Toronto's cycling infrastructure is heavily concentrated downtown.
Scoring the city's full street network for cyclist stress shows that
while 58% of streets citywide qualify as low-stress, protected bike
infrastructure drops from 4.4% of streets in the downtown core to just
1.7% citywide — meaning most of the city's "low stress" rating comes
from quiet residential streets having no traffic to begin with, not
from dedicated cycling infrastructure.

This project scores every street in Toronto for cyclist comfort using
a rule-based model adapted from the academic Level of Traffic Stress
(LTS) framework (Mekuria, Furth & Nixon, 2012), built to be portable
across cities through a config-driven architecture — proven by running
the identical scoring code, unmodified, against Toronto, Vancouver,
and Corvallis, Oregon.

## What is Level of Traffic Stress?

Level of Traffic Stress (LTS) classifies streets on a scale of 1-4
based on how comfortable an average adult would feel biking on them,
using measurable street characteristics — facility type, speed, lane
count, parking presence — rather than a survey of actual riders.

LTS 1 is extremely low stress: you'd feel comfortable teaching a child
to ride there. LTS 4 is high stress: only the most confident, experienced
cyclists are comfortable riding in that traffic, and most people would
avoid it if possible. Most people fall somewhere in between — comfortable
with quiet streets and protected bike lanes, but unwilling to ride in
heavy, fast traffic without dedicated space.

The scale comes from Mekuria, Furth & Nixon's 2012 research linking
these measurable street characteristics to the same rider-comfort
categories originally proposed by Roger Geller (Portland Bureau of
Transportation) — "strong and fearless," "enthused and confident,"
"interested but concerned," and "no way, no how" — without requiring
a new rider survey for every street being classified.## Methodology

**Data source.** This project uses OpenStreetMap (OSM) as its sole
data source, accessed via OSMnx. This follows an established pattern
in the field — the original LTS framework calls for up to ~18-21
variables, most of which aren't available as open data anywhere;
reducing the model to what's computable from OSM mirrors the approach
taken by other OSM-based LTS implementations (Conveyal, PeopleForBikes).

**Link-level scoring only.** This project scores individual street
segments (links), not intersections. Furth & Mekuria's framework treats
link-level and intersection-level stress as separate components, and
reliable intersection attributes (turn lanes, signal phasing) aren't
consistently available in OpenStreetMap. This is a deliberate scope
decision, not an oversight.

**Thresholds.** The numeric thresholds used to classify streets (speed
and lane-count breakpoints) are an adapted interpretation of Furth &
Mekuria's published LTS criteria. Because the original criteria are
published as image-based tables rather than machine-readable data,
this project translates the general published bands into explicit,
documented numeric rules — listed in full in `lts_rules.py` for
transparency and adjustment, rather than presented as an exact
reproduction of the source tables.

**One-way street adjustment.** Streets tagged as one-way have their
effective lane count doubled before scoring. On a one-way street, all
lanes move in the same direction as the cyclist, meaning more total
vehicle interaction (passing, lane changes) per direction of travel
than an equivalent two-way street, where only half the lanes carry
same-direction traffic. A one-way street with 2 lanes is treated as
equivalent in stress to a two-way street with 4 lanes (2 per
direction) — following the same doubling logic used in Furth's
original methodology. Known limitation: this doesn't distinguish a
one-way street that's busy because of high traffic volume (e.g.
downtown Adelaide/Richmond) from one that's one-way for traffic-calming
reasons on an otherwise quiet residential street — a blunt rule
inherited from the source methodology, not unique to this project.

**Excluded road types.** Motorways and trunk roads are excluded
entirely, since cyclists cannot legally ride on them.
## Key finding: the downtown/suburban infrastructure gap

Expanding this analysis from a downtown test area (Old Toronto, 15,161
street segments) to the full amalgamated city (71,934 street segments)
revealed a clear pattern: Toronto's dedicated cycling infrastructure is
heavily concentrated in the downtown core, while the inner suburbs rely
almost entirely on mixed traffic.

| | Old Toronto (downtown) | Full City |
|---|---|---|
| Protected bike infrastructure | 4.4% of streets | 1.7% of streets |
| Painted bike lanes | 8.0% of streets | 3.4% of streets |
| Mixed traffic (no bike facility) | 87.5% of streets | 95.0% of streets |

Interestingly, the overall low-stress (LTS 1) percentage stayed roughly
flat citywide (~58% both times) — the suburbs add both more quiet
residential streets and more wide, fast arterials (e.g. Eglinton,
Finch, Sheppard, Lawrence), which appear to roughly cancel out in the
aggregate LTS distribution even though the underlying street character
is very different from downtown. The share of highest-stress streets
(LTS 4) did rise meaningfully citywide, from about 4% to 11% of all
streets.

The practical takeaway: a citywide "58% low stress" headline number
would be misleading on its own. Most of that low-stress rating in the
suburbs comes from quiet residential streets simply having little
traffic — not from the presence of dedicated cycling infrastructure,
which remains overwhelmingly concentrated downtown.
## Threshold sensitivity

To test how much the model's output depends on a single design choice,
I re-scored the full Toronto network at five different LTS-1 speed
thresholds (20, 25, 30, 35, and 40 km/h), holding everything else
constant.

| LTS-1 threshold | Share of network classified LTS 1 |
|---|---|
| 20 km/h | 1.9% |
| 25 km/h | 2.0% |
| 30 km/h | 58.0% |
| 35 km/h | 58.0% |
| 40 km/h | 75.8% |

The model is not smoothly sensitive to this threshold — it behaves
like a cliff. Moving the cutoff from 25 to 30 km/h alone reclassifies
56 percentage points of the entire network from LTS 2 to LTS 1, while
moving from 20 to 25 km/h barely changes anything at all.

This happens because 30 km/h is Toronto's actual default residential
speed limit, applied to the large majority of residential streets
either through a real posted-speed tag or through this project's own
fallback default. The threshold isn't cutting through a smooth
distribution of speeds across the city — it's sitting directly on top
of the single most common speed value in the entire dataset. A small
move in either direction crosses that concentration and reclassifies
a huge share of the network at once.

Practical implication: this model's citywide LTS-1 percentage is less
a precise, stable measurement and more a direct reflection of whether
Toronto's own 30 km/h default counts as "low stress" — a policy
question as much as a modeling one. This is worth stating plainly
rather than presenting the 58% LTS-1 figure as a robust, independently
derived result.
## Validation

Validation so far is limited but real, not fabricated. Two known
Toronto corridors were checked directly against the model's output
using QGIS's Identify Features tool:

- **Bloor St W (Shaw to Avenue Rd)** — protected cycle track — model
  correctly scored LTS 1
- **Danforth Ave (near Broadview)** — protected cycle track — model
  correctly scored LTS 1

Both matches confirm the core pipeline correctly identifies protected
infrastructure end-to-end, from raw OpenStreetMap tags through the
config translation layer to the final score.

This is a small sample, not formal validation. A broader informal
survey of Toronto cyclists, rating a fixed set of streets on the same
1-4 stress scale used by the model, is in progress at the time of
writing — results will be added here once collected. Formal validation
against a larger, independently-rated set of corridors is a clear next
step, not yet complete.


## Limitations

- Uses posted speed limits, not measured actual traffic speeds
- No traffic volume (ADT) data -- not available in OpenStreetMap
- Intersection-level stress not modeled -- link-level only
- ~23% of streets missing a maxspeed tag, relying on city-typical
  defaults instead of confirmed data
- Exploratory/educational tool, not validated for engineering or
  safety-critical use

## Data & Code

Built with OpenStreetMap data via OSMnx, scored with a custom Python
rule engine, styled in QGIS. Full code and city configs available at
[GitHub link -- add once pushed].
