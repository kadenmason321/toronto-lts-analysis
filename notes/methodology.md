# Toronto Cycling Stress Map: A Level of Traffic Stress Analysis

## Summary

Toronto's cycling infrastructure is heavily concentrated downtown, and
the city's low-stress cycling network is severely fragmented — split
into over 1,400 disconnected pieces, with the largest holding only
14.4% of all low-stress streets. A comparative analysis with
Amsterdam reveals this isn't simply a matter of infrastructure
quantity: Amsterdam's low-stress network, by contrast, is almost
entirely unified — 90% of its low-stress streets belong to a single
connected network.

This project scores every street in a city for cyclist comfort using
a rule-based model adapted from the academic Level of Traffic Stress
(LTS) framework (Mekuria, Furth & Nixon, 2012), built to be portable
across cities through a config-driven architecture. It has been run,
unmodified at the rule-engine level, against Toronto, Vancouver,
Corvallis (Oregon), Seattle, and Amsterdam.

## What is Level of Traffic Stress?

Level of Traffic Stress (LTS) classifies streets on a scale of 1-4
based on how comfortable an average adult would feel biking on them,
using measurable street characteristics — facility type, speed, lane
count, parking presence — rather than a survey of actual riders.

LTS 1 is extremely low stress: you'd feel comfortable teaching a child
to ride there. LTS 4 is high stress: only the most confident,
experienced cyclists are comfortable riding in that traffic, and most
people would avoid it if possible. Most people fall somewhere in
between — comfortable with quiet streets and protected bike lanes, but
unwilling to ride in heavy, fast traffic without dedicated space.

The scale comes from Mekuria, Furth & Nixon's 2012 research linking
these measurable street characteristics to the same rider-comfort
categories originally proposed by Roger Geller (Portland Bureau of
Transportation) — "strong and fearless," "enthused and confident,"
"interested but concerned," and "no way, no how" — without requiring
a new rider survey for every street being classified.

## Methodology

**Data source.** This project uses OpenStreetMap (OSM) as its sole
data source, accessed via OSMnx. This follows an established pattern
in the field — the original LTS framework calls for up to ~18-21
variables, most of which aren't available as open data anywhere;
reducing the model to what's computable from OSM mirrors the approach
taken by other OSM-based LTS implementations (Conveyal, PeopleForBikes).

**Two network types are pulled and merged.** Initially, this project
pulled only the drivable road network (network_type="drive"), since
North American cities typically tag protected cycling infrastructure
directly onto the parent road (e.g. cycleway=track). Testing against
Amsterdam revealed this was a significant blind spot: in cities with
extensive off-street cycling infrastructure, protected paths are very
often mapped as entirely separate OSM ways (highway=cycleway) with no
relationship to any road at all — invisible to a drive-only pull.
A follow-up multi-city check confirmed this gap exists in every city
tested, not just Amsterdam (standalone cycleways found at up to 81%
of a sample drive-network's size in Toronto). The pipeline now
optionally pulls the full network and merges in standalone cycleways,
treating them as automatically low-stress ("protected") infrastructure.
This fix was applied to all five cities in this analysis.

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
effective lane count doubled before scoring, reflecting that all
lanes move in the cyclist's direction rather than being split by
opposing traffic. Known limitation: this doesn't distinguish a busy
one-way arterial from a narrow, calm one-way residential street.

**Excluded road types.** Motorways and trunk roads are excluded
entirely, since cyclists cannot legally ride on them.

## Key finding: the downtown/suburban infrastructure gap

Expanding this analysis from a downtown test area (Old Toronto) to
the full amalgamated city revealed that Toronto's cycling
infrastructure is heavily concentrated in the downtown core relative
to the inner suburbs, even after correcting for the standalone-
cycleway blind spot described above. Suburban arterials (Eglinton,
Finch, Sheppard, Lawrence) contribute a disproportionate share of the
city's highest-stress streets.

## Key finding: Toronto's low-stress network is severely fragmented

Building a low-stress-only (LTS 1-2) subgraph of Toronto's network and
analyzing its connected components revealed that the network is not
one connected system — it is split into 1,438 separate fragments. The
single largest fragment holds only 14.4% of all low-stress nodes.

Real, verified examples of this fragmentation were identified and
checked against Google Maps/Street View:

- **St. Phillips Rd / Royal York Rd** (Weston/Etobicoke): a 1.5km gap
  connecting two low-stress neighborhoods, crossing the Humber River
  via an EXISTING vehicle bridge — meaning a low-stress upgrade here
  would not require new river-crossing infrastructure, only adding
  cycling space to a road and bridge that already exist.
- **Lawrence Ave East** (Scarborough): a 456m gap, also crossing an
  existing bridge (over Highland Creek), on an ordinary suburban
  arterial with no dedicated cycling infrastructure.
- **Kincort St / Sheffield St** (Brookhaven-Amesbury/York): a 1.8km
  gap with no water crossing or geographic complication at all — the
  ordinary case, where two low-stress neighborhoods are separated
  simply by an absence of connecting infrastructure.

Together, these three examples show that Toronto's fragmentation has
more than one underlying cause: some gaps involve existing water
crossings needing only a cycling-infrastructure retrofit, others are
ordinary streets with no complicating geography at all.

## Comparative finding: Amsterdam's network is structurally unified

Running the identical fragmentation analysis on Amsterdam produced a
striking contrast:

| | Toronto | Amsterdam |
|---|---|---|
| Total low-stress network components | 1,438 | 617 |
| Largest component (% of low-stress network) | 14.4% | 90.0% |

Amsterdam's low-stress network is, for practical purposes, one
unified, traversable system. All tested reference points — including
a location across the IJ river, a genuine physical barrier — belong to
the same main network. A cyclist confined to low-stress streets in
Amsterdam can reach nearly anywhere in the city; the equivalent
cyclist in Toronto is confined to a small, isolated fragment
regardless of starting neighborhood.

This reframes the difference between the two cities: it is not simply
that Amsterdam has more low-stress infrastructure than Toronto (a
widely known fact), but that Amsterdam's infrastructure forms a
coherent network while Toronto's forms scattered, disconnected
pockets. This is a structural, not just quantitative, difference.

**Caveat:** Amsterdam is geographically far more compact than
Toronto, which likely makes full network connectivity structurally
easier to achieve regardless of infrastructure investment. This
comparison illustrates a real structural difference but is not a
perfectly controlled experiment isolating infrastructure quality from
city scale and geography.

## Threshold sensitivity

Re-scoring Toronto's network at five different LTS-1 speed thresholds
(20, 25, 30, 35, 40 km/h) revealed the model behaves like a cliff, not
a gradient, around 30 km/h — Toronto's actual default residential
speed limit. Moving the threshold from 25 to 30 km/h alone reclassified
56 percentage points of the network from LTS 2 to LTS 1.

This same threshold-cliff pattern was independently reproduced in both
Corvallis and Seattle, where standard US 25mph (~40km/h) residential
streets structurally cannot reach LTS 1 under this model's thresholds
— only streets at or below ~18.6mph can. In Seattle specifically, this
held true even after the standalone-cycleway fix substantially
increased measured facility coverage (11x more protected-infrastructure
edges), confirming that threshold sensitivity and facility-coverage
completeness are independent properties of the model, not entangled
symptoms of the same underlying issue.

## Validation

Two known Toronto corridors (Bloor St bike lane, Danforth Ave bike
lane) were checked directly against the model's output using QGIS's
Identify Features tool and both correctly scored LTS 1. This is a
small sample, not formal validation. A broader informal survey of
Toronto cyclists is in progress at the time of writing.

## Limitations

- Uses posted speed limits, not measured actual traffic speeds
- No traffic volume (ADT) data — not available in OpenStreetMap
- Intersection-level stress not modeled — link-level only
- A meaningful share of streets are missing a maxspeed tag, relying
  on city-typical defaults instead of confirmed data
- The standalone-cycleway fix treats any such path as automatically
  "protected" (LTS 1) regardless of width, surface, or crowding —
  a simplification that may overstate comfort on narrow or
  heavily-used paths
- Exploratory/educational tool, not validated for engineering or
  safety-critical use

## Data & Code

Built with OpenStreetMap data via OSMnx, scored with a custom Python
rule engine, visualized in QGIS and as an interactive multi-city web
map. Full code, city configs, and an interactive explorer available at
[GitHub link].
