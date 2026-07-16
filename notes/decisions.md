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

## Finding: Toronto's low-stress network is severely fragmented
Built a low-stress-only (LTS 1-2) subgraph of the full Toronto network
and checked its connected components. Result: the low-stress network
is not one connected system -- it's 1,169 separate disconnected
fragments. Even the single largest connected piece holds only 16.3%
of all low-stress-network nodes.

Tested routing between real points:
- Union Station sits on an isolated 9-node fragment
- High Park sits on a separate isolated 9-node fragment
- Danforth/Broadview sits on a 998-node fragment
- Bloor/Shaw sits on the largest fragment (3,851 nodes)

None of these four points are mutually reachable while staying
entirely on LTS 1-2 streets -- every tested trip required at least
some travel on higher-stress streets to connect between fragments,
regardless of direction of approach to downtown.

Practical implication: Toronto's low-stress infrastructure exists as
disconnected pockets rather than a usable network. A cyclist who only
feels safe on LTS 1-2 streets cannot travel between most neighborhoods,
even physically close ones, without crossing higher-stress streets to
bridge fragments. This matches the "low-stress islands" problem
described in Furth's own connectivity follow-up research (2016) --
worth citing directly, since this project independently reproduces
that pattern using real, current Toronto data rather than assuming it.

## Investigation: is the fragmentation finding real or an artifact?
Given how extreme the fragmentation result looked (1,169 components,
largest holding only 16.3% of nodes), tested two likely artifact
explanations before treating it as confirmed:

**Test 1 -- one-way lane-doubling rule.** Re-scored without doubling
effective lane count for one-way streets. Result: 1,169 -> 1,139
components, largest fragment 16.3% -> 17.0% of nodes. Negligible
change despite 3,467 one-way edges being "rescued" into low-stress
status. Ruled out -- the doubling rule is not a meaningful driver of
fragmentation.

**Test 2 -- missing maxspeed data bias.** Checked what fraction of
high-stress (LTS 3-4) edges relied on a default speed value vs. a real
OSM tag. Result: 16.6% of high-stress edges used a default -- actually
LOWER than the network-wide ~23% missing-maxspeed rate, meaning
high-stress streets are if anything MORE likely to have real tagged
speeds than average (plausible: busier streets get mapped more
carefully). Ruled out -- missing data is not artificially inflating
the high-stress count.

**Conclusion:** two of the most likely artifact explanations were
tested and ruled out, which increases confidence that the
fragmentation reflects genuine structure in Toronto's street grid
(frequent arterial crossings breaking up the residential low-stress
grid) rather than a modeling error. Not fully confirmed -- a full audit
of lane-count defaults specifically has not yet been done, and remains
a reasonable next check. Presenting this finding with that honest
caveat rather than as fully settled.

## Finding: identified a specific, actionable "missing link"
Checked all pairs among the 10 largest low-stress network fragments
for the shortest possible connecting route through the full network,
using a 30-node sample per fragment for speed. Closest pair found:
fragment 3 (876 nodes) and fragment 7 (491 nodes), located in the
Weston/Etobicoke area near the Humber River, with an estimated bridge
length of ~1,662 m.

Re-verified this specific pair using ALL nodes in both fragments
(rather than the sample) for a trustworthy number on the single best
candidate. Confirmed shortest connecting bridge: 1,518 m, running
along St. Phillips Rd and Royal York Rd.

Checked this route visually via Google Maps and Street View. Initial
assumption (that the route ran parallel to the Humber River without
crossing it) was WRONG -- Street View imagery confirms St. Phillips Rd
crosses the Humber River via an existing vehicle bridge along this
route (concrete deck, guardrails, elevated over a wooded ravine).
Worth noting as a process point: an earlier draft of this finding
stated confidently that the route did not cross the river, based on a
misread of a static map screenshot -- that claim was wrong and was
corrected only after direct Street View verification. Good reminder
to verify visually rather than infer from a road/river label's
apparent parallel path on a schematic map.

**Corrected implication:** because an existing bridge already provides
the physical river crossing, a low-stress infrastructure upgrade along
this corridor would NOT require building new river-crossing
infrastructure -- only adding dedicated cycling space to a road (and
bridge) that already exists. This is arguably a stronger, more
actionable finding than a pure street-level gap would be: the
hardest, most expensive part of a river crossing (the bridge
structure itself) is already built. Retrofitting bike infrastructure
onto an existing bridge/road is a comparatively lower-cost, lower-
barrier intervention than constructing a new crossing, making this a
genuinely credible candidate for prioritized investment.

Practical takeaway: this is a concrete, specific, real-world example
of what the connectivity analysis is meant to surface -- not just "the
low-stress network is fragmented" as an abstract claim, but a named
street, in a named place, with a measurable gap length (1.5 km) and a
plausible, comparatively low-cost path to reconnecting two real
low-stress neighborhoods.

**Caveat:** the initial pair-ranking across all 10 fragments (which
identified this pair as the closest) used a 30-node sample per
fragment for speed. This single top result has been fully verified
against all nodes and is trustworthy. The relative rankings of the
OTHER pairs in that initial list have not been individually re-
verified and could shift somewhat if fully checked -- worth flagging
if presenting the full ranked list rather than just this top finding.
## Finding: a second, shorter missing link (Scarborough)
Verified the second-closest fragment pair from the original ranked
list: fragment 5 (713 nodes) and fragment 8 (450 nodes). True shortest
bridge (checked against all nodes, not sampled): 456 m.

Location: Lawrence Ave East, between Beechgrove Dr and Meadowvale Rd,
in the Scarborough/Highland Creek area, crossing Highland Creek near
Lower Highland Creek Park. Verified via Street View: a straightforward
multi-lane suburban arterial (50 km/h posted), no visible cycling
infrastructure. Like the first finding, this gap also crosses water --
Highland Creek runs through this stretch, meaning the road already
carries a bridge/crossing structure over it.

This means BOTH verified findings share the same underlying pattern:
the physical crossing (river or creek) already exists as built
infrastructure. In neither case would closing the low-stress gap
require constructing a new crossing -- both are cases of adding
dedicated cycling space to a road and bridge that already exist. At
under 500m, this is a shorter gap to close than the St. Phillips/
Royal York finding, in a part of the city (Scarborough) that the
earlier full-city analysis already flagged as having disproportionately
less cycling infrastructure than downtown.

Worth noting as a methodological observation: two out of two verified
missing-link candidates so far happen to cross water. This may not be
coincidental -- low-stress fragments are plausibly bounded by
waterways (creek/river valleys) as much as by busy roads, since
Toronto's ravine system creates natural neighborhood edges. Water
crossings may be disproportionately common among the shortest bridges
between fragments precisely because rivers/creeks are already a
geographic seam separating neighborhoods. Worth checking a third
example without a water crossing before generalizing this pattern
with confidence.

Two verified findings together (both involving existing water
crossings, in different parts of the city -- one downtown-adjacent,
one suburban) demonstrate the missing-link methodology works across
different contexts, and both point toward the same actionable
conclusion: the expensive infrastructure (bridges) is often already
built, and the gap is specifically about missing cycling
infrastructure on top of existing road/bridge structures.

## Finding: Amsterdam reveals a structural blind spot in the pipeline
Added Amsterdam as a genuinely different-tagging-culture test city
(vs. Toronto/Vancouver/Corvallis's shared North American conventions).
Amsterdam's LTS scoring showed protected+bike_lane facility coverage
of only ~3.4% -- LOWER than Toronto's ~11.6%, despite Amsterdam being
globally recognized for extensive, high-quality cycling infrastructure.
This was surprising enough to investigate rather than accept.

Root cause, confirmed via direct test: this project's fetch pipeline
uses network_type="drive" in OSMnx, which pulls only the DRIVABLE road
network. In North American cities, protected cycle tracks are usually
tagged directly onto the parent road (cycleway=track), so they're
captured even on a drive-only pull. In Amsterdam, protected cycling
infrastructure is very often mapped as an entirely SEPARATE OSM way
(highway=cycleway) with no parent road relationship at all --
physically distinct infrastructure, mapped as distinct data.

Verified directly: in a single test neighborhood (De Pijp), the
drive-only network pull returned 280 edges, while the full network
(network_type="all") returned 1,011 edges -- 181 of which were
standalone highway=cycleway ways completely invisible to the current
pipeline.

**This is a genuine architectural limitation, not a config or tagging
inconsistency.** It cannot be fixed by editing a city config file --
it requires a pipeline change (pulling network_type="all" or "bike"
in addition to "drive", and correctly merging standalone cycleway ways
into the scoring model, likely as automatic LTS 1/protected
facilities). This is exactly the kind of gap the Amsterdam test was
added to find -- a different tagging CULTURE breaking an assumption
the North American cities never exposed, rather than just a units/
config difference.

**Practical implication for the write-up:** the project's current LTS
scores for Amsterdam (and likely any city with substantial standalone
cycling-path infrastructure) understate actual low-stress cycling
availability. This should be stated as an explicit limitation, and
ideally addressed before presenting Amsterdam's numbers as comparable
to the other three cities' facility-coverage stats.

## Resolution: standalone cycleway fix implemented and verified
Implemented the fix for the Amsterdam finding above: fetch_network.py
now supports an include_standalone_cycleways config flag. When set,
it pulls network_type="all" in addition to the normal drive network,
finds standalone highway=cycleway ways not already present in the
drive network, and merges them in with a _standalone_cycleway marker.
score_network.py's get_facility_type() checks this marker first,
treating standalone cycleways as automatically "protected."

Hit a real bug while verifying the fix: the marker check initially
used Python truthiness (`if row.get("_standalone_cycleway")`), which
incorrectly returned True for ALL edges, not just the merged-in ones.
Root cause: pandas fills missing values in a column with NaN for rows
that never had the attribute set, and NaN is truthy in Python
(bool(float('nan')) == True). This caused every single edge in
Amsterdam to score LTS 1 / protected on the first corrected run --
an obviously wrong result that was caught immediately rather than
accepted. Fixed by checking explicitly for True/"True"/"true" instead
of relying on truthiness.

**Verified result after the real fix:**
- Facility coverage jumped from ~3.4% (drive-only, undercounting) to
  ~46% (protected + bike_lane combined) once standalone cycleways are
  correctly counted
- LTS 1 share rose from a low, implausible number to 84% of the
  network -- now consistent with Amsterdam's real-world reputation for
  extensive, high-quality low-stress cycling infrastructure

This is a strong before/after methodological story: a genuinely
different tagging culture (Amsterdam) exposed a real architectural
blind spot in the pipeline (drive-only network pulls miss standalone
cycling infrastructure), which was root-caused, fixed, and verified
with a clear numeric before/after -- and a real bug was caught and
corrected during the fix itself rather than accepted on a
too-good-to-be-true first result (100% protected across every edge
was an immediate red flag, not a validated success).

**Remaining question, not yet resolved:** whether this same blind spot
exists to any meaningful degree in the North American cities
(Toronto, Vancouver, Corvallis, Seattle) -- a multi-city diagnostic
check is in progress to determine whether this fix needs to be applied
more broadly or is genuinely Amsterdam-specific.

## Standalone cycleway fix applied to all five cities, verified
Extended the include_standalone_cycleways fix beyond Amsterdam to
Toronto, Vancouver, Corvallis, and Seattle after a multi-city
diagnostic showed the drive-only blind spot was NOT Amsterdam-specific
(standalone cycleways found at 81.1% of drive-network size in a
Toronto sample, 23.6% in Vancouver, 14.8% in Corvallis).

Facility coverage (protected + bike_lane) before -> after the fix:
- Toronto: ~5% -> ~15.3%
- Vancouver: ~0.1% -> ~19.4%
- Corvallis: 0% -> ~32.5%
- Seattle: ~1% -> ~13.8%
- Amsterdam: ~3.4% -> ~46%

Key confirmation: Seattle's result cleanly demonstrates the two major
findings from today are properly independent. Facility coverage rose
11x (480 -> 5,595 protected edges), but LTS 1 share barely moved
(541 -> 5,656 edges, ~1% -> ~10.3%), because the LTS-1 threshold
cliff (30 km/h vs. the US 25mph/40km/h residential norm) is a SEPARATE
mechanism from facility-type completeness. A data-completeness fix
correctly did not "fix" the threshold-sensitivity finding, because
they are unrelated problems -- this is a good sign the two findings
were correctly diagnosed as distinct in the first place, not
downstream of the same underlying bug.

**Follow-up work now required, not yet done:**
- Both Toronto posters (stress map, connectivity/fragmentation map)
  are now built on outdated data and need regenerating
- Toronto's connectivity/fragmentation analysis (1,169 components
  finding) needs to be RE-RUN on the new data -- the fragmentation
  pattern could shift now that ~9,000 more edges are classified as
  protected infrastructure
- The two verified missing-link findings (St. Phillips/Royal York,
  Lawrence Ave E) should be spot-checked against the new data, though
  expected to hold since they were scored high-stress due to absent
  cycleway tags, not the standalone-cycleway blind spot specifically
- methodology.md's cited facility-coverage percentages need updating
- The interactive map's underlying GeoJSON files need regenerating

## Re-run: fragmentation analysis after standalone cycleway fix
Re-ran the connectivity/fragmentation analysis on Toronto's updated
network (80,685 edges, up from 71,934 after the standalone cycleway
fix). Result was counterintuitive -- predicted fragmentation would
DECREASE (more real low-stress infrastructure = more connections
between fragments), but it actually INCREASED: 1,169 -> 1,438
components. Largest fragment's share of the low-stress network also
dropped slightly (16.3% -> 14.4%).

Likely explanation: many of the newly-added standalone cycleway edges
are genuinely isolated recreational paths (park trails, ravine paths,
schoolyard connectors) that don't touch any existing low-stress
fragment at either end. Rather than merging fragments together, each
of these becomes its OWN new tiny fragment, increasing the total
count. This is a plausible and even interesting finding in its own
right: Toronto appears to have meaningful disconnected recreational
cycling infrastructure -- trails that exist but don't connect to
anything -- distinct from and additional to the earlier "the STREET
network is fragmented" finding.

Reference points re-checked for stability:
- Bloor/Shaw: still in the largest fragment (now 4,083 nodes, was
  3,851) -- consistent
- Danforth/Broadview: still an isolated fragment, grew to 1,027 nodes
  (was 998) -- consistent
- Union Station: still an isolated 9-node island -- UNCHANGED
- High Park: still an isolated 9-node island -- UNCHANGED

The core finding (severe fragmentation, specific known points remain
disconnected from each other) is ROBUST to the standalone-cycleway
fix -- the underlying pattern held even though the fix changed the
edge count substantially, which strengthens confidence that this is a
real structural finding rather than an artifact of incomplete data.

## Third missing-link example, verified after data refresh (Brookhaven-Amesbury/York)
Re-ran the missing-link search after the standalone-cycleway fix
(fragment numbering shifted; old pairs 3<->7 and 5<->8 no longer
appear in the new top-10 list). New closest pair: fragment 0
(largest, 4,083 nodes) and fragment 9. True shortest bridge (full-node
verified): 1,823 m.

Location: via Kincort St and Sheffield St, in the Brookhaven-Amesbury/
York area near Eglinton West. Verified via Google Maps: NO water
crossing -- Google explicitly labels the route "mostly flat," and the
area has no rivers/ravines. This is the genuinely ordinary case: a gap
between two low-stress neighborhoods caused by nothing more than an
absence of connecting infrastructure, no geographic complication at
all.

This RESOLVES the earlier open question from the first two findings
(both of which crossed water, prompting a note that it was "worth
checking a third example before generalizing"). With this third,
water-free example: 2 of 3 verified missing-link candidates involve
existing water crossings, 1 of 3 does not. The earlier hypothesis
("low-stress fragments may be disproportionately bounded by
waterways") is only partially supported -- water crossings appear
common but NOT universal among missing-link candidates. Appropriate
conclusion: both waterway-adjacent gaps AND ordinary street-level gaps
are real, occurring patterns in Toronto's low-stress network
fragmentation, not a single dominant cause.

Note: this finding is based on the POST-FIX network data (includes
standalone cycleways). The two earlier findings (St. Phillips/Royal
York; Lawrence Ave E) were verified against the PRE-FIX network and
are presented as illustrative case studies from an earlier analysis
pass, not necessarily the current top candidates under the corrected
data.

## Finding: Amsterdam's low-stress network is structurally unified, Toronto's is not
Ran the same fragmentation/connectivity analysis on Amsterdam that was
run on Toronto, as a direct comparison test.

| | Toronto | Amsterdam |
|---|---|---|
| Total components | 1,438 | 617 |
| Largest component (% of low-stress network) | 14.4% | 90.0% |

Amsterdam's low-stress network is essentially ONE unified,
well-connected system -- 90% of all low-stress infrastructure belongs
to a single connected component. All four tested Amsterdam reference
points (Centraal station, De Pijp, Vondelpark area, and a point across
the IJ river -- a genuine physical water barrier) belong to this same
main network.

Toronto's low-stress network, by contrast, is fragmented into 1,438
disconnected pieces, with the largest holding only 14.4% of the total.

**This is the strongest comparative finding of the project.** It
reframes the Toronto/Amsterdam difference from a simple, well-known
fact ("Amsterdam has more cycling infrastructure than Toronto") into a
specific, non-obvious structural insight: the difference isn't just
QUANTITY of low-stress infrastructure, it's CONNECTIVITY. Amsterdam's
infrastructure forms a coherent, traversable network; Toronto's forms
scattered, disconnected pockets. A cyclist in Amsterdam who only feels
safe on low-stress streets can reach nearly anywhere in the city
without leaving the low-stress network. A cyclist in Toronto with the
same constraint is confined to a small, isolated fragment of the city
regardless of which neighborhood they start in.

Caveat: Amsterdam's network is smaller in absolute geographic extent
than Toronto's (compact European city vs. sprawling North American
metro), which likely makes full connectivity structurally easier to
achieve. This is a real, relevant confound worth stating explicitly --
the comparison is illustrative of a real structural difference, not a
perfectly controlled experiment isolating infrastructure quality alone
from city geography/scale.

---

## Session summary: the standalone-cycleway architecture fix (chronological recap)
Tonight's session, condensed into a clean narrative, since the entries
above were written in the order things happened, not necessarily the
clearest reading order.

1. Added Amsterdam as a deliberate "different tagging culture" test
   city (vs. Toronto/Vancouver/Corvallis/Seattle's shared North
   American conventions).
2. Amsterdam's initial facility-coverage result was suspiciously LOW
   (~3.4%) given its real-world reputation for extensive cycling
   infrastructure -- investigated rather than accepted.
3. Root cause found and verified directly: the pipeline's
   network_type="drive" pull misses standalone highway=cycleway ways,
   which Amsterdam uses heavily for protected infrastructure (181
   standalone cycleways found invisible to the drive pull in a single
   test neighborhood alone).
4. A multi-city check confirmed this blind spot exists in EVERY city
   tested, not just Amsterdam -- ruling out the "Amsterdam is just
   different" theory in favor of "this is a general pipeline gap."
5. Implemented a fix: fetch_network.py can now optionally pull the
   full network and merge in standalone cycleways, marked so
   score_network.py treats them as automatically protected.
6. Hit and fixed a real bug during verification: a pandas NaN-
   truthiness issue caused every edge to incorrectly score as
   protected on the first corrected run -- caught immediately because
   the result (100% LTS 1) was implausible, not accepted at face
   value.
7. Applied the verified fix to all five cities, re-fetched and
   re-scored everything.
8. Re-ran Toronto's fragmentation analysis on the corrected data.
   Result was counterintuitive: fragmentation INCREASED (1,169 -> 1,438
   components) rather than decreasing, because many newly-added
   standalone cycleways are isolated recreational paths that don't
   connect to the existing low-stress network. Core finding (severe
   fragmentation, same reference points remain disconnected) held
   robust despite this.
9. Re-verified the missing-link methodology on the corrected data,
   surfacing a new closest pair (Kincort St/Sheffield St, 1,823m, no
   water crossing) that resolved the earlier "2 of 2 findings involve
   water" open question -- now 2 of 3 involve water, 1 of 3 does not.
10. Ran the same fragmentation analysis on Amsterdam as a direct
    comparison. Result: Amsterdam's low-stress network is 90% one
    unified component; Toronto's largest component is only 14.4% of
    its network. This is arguably the single strongest comparative
    finding of the whole project.
11. Exported Amsterdam's fragments for visualization and added them to
    the interactive multi-city map alongside Toronto's, enabling
    direct visual comparison.
12. Updated methodology.md to reflect all of the above as the current,
    accurate state of the project.

**What's still outdated and requires follow-up (not done tonight):**
- Both static QGIS posters (Toronto stress map, Toronto connectivity
  map) were built on PRE-FIX data and need regenerating
- Vancouver, Corvallis, and Seattle have NOT had fragmentation
  analysis run on them (only Toronto and Amsterdam have)
- GitHub Pages deployment of the interactive map has not been done
- The interactive map has not yet been re-pushed to GitHub with
  tonight's updated data

## RESOLVED: node-snapping investigation from earlier -- likely a real trail gap, not a data bug
Followed up on the open question above. Located the exact spot: the
Humber River Recreational Trail meets Old Dundas Street near the
historic Lambton House. Widened the search to 500m around this
location (initial 150m search only caught 3 nodes -- too few to be a
real test) and re-ran the near-miss node check against 66 nodes /
2,145 pairs. Result: NO unsnapped near-miss nodes found.

Independently, a web search surfaced a Toronto cycling blog
documenting a REAL, known discontinuity at this exact location: the
Humber River Recreational Trail does not continue directly through
here -- cyclists have to leave the trail, briefly ride on Lundy Avenue
and Old Dundas Street, before the trail picks up again. This is a
genuine, real-world "missing link" in the trail system itself, not a
data artifact.

**Conclusion:** the visual "touching" of red and green fragments on
the mobile map most likely reflects this REAL trail discontinuity
correctly, not a graph bug. Two genuinely separate pieces of
infrastructure (trail segment, road segment) can be geographically
adjacent on screen while remaining legitimately disconnected in the
network -- which is exactly what a real "missing link" looks like when
rendered. Marking this investigation closed. Does not change the
core fragmentation finding or its magnitude; if anything, this
specific example is a nice, small, real-world illustration of exactly
the kind of gap the whole connectivity analysis is designed to
surface.

## Finding: five-city connectivity comparison complete
Ran the same fragmentation/connectivity analysis (previously done for
Toronto and Amsterdam only) on Vancouver, Corvallis, and Seattle,
completing the comparison across all five cities.

| City | Largest fragment (% of low-stress network) | Total components |
|---|---|---|
| Toronto | 14.4% | 1,438 |
| Seattle | 34.1% | 735 |
| Corvallis | 41.8% | 172 |
| Vancouver | 83.5% | 325 |
| Amsterdam | 90.0% | 617 |

Two things worth noting:

1. Real, ordered spread across cities, not a binary "fragmented vs.
   not." Toronto is a clear outlier at the low end; Vancouver sits
   much closer to Amsterdam's near-unified end despite being a North
   American city, ruling out "this is just a North American thing" as
   a full explanation.

2. Seattle's structure is qualitatively different from the others,
   not just quantitatively lower. It has TWO large, comparably-sized
   fragments (6,825 and 4,948 nodes) rather than one dominant fragment
   with a steep drop-off -- unlike Toronto, Corvallis, and Vancouver,
   which all show a single clear leader. This suggests Seattle's
   low-stress network may be split into two genuinely separate major
   sub-networks (plausibly divided by a geographic feature like a lake
   or hill terrain) rather than one core network with scattered small
   fragments around it. Worth investigating which two areas these
   correspond to as a specific example, similar to the Toronto missing-
   link case studies.

## Checked and cleared: highway=path blind spot hypothesis (Hudson River Greenway)
Before fully trusting NYC's facility-coverage numbers, tested a
hypothesis: does cycling infrastructure sometimes get tagged as
highway=path + bicycle=designated instead of highway=cycleway? If so,
this would be a real, uncaught blind spot -- our standalone-cycleway
merge only looks for highway=cycleway specifically.

Tested against a small bounding box covering the Hudson River
Greenway near Chelsea/Hell's Kitchen, Manhattan -- a well-known,
heavily-used dedicated bike/ped corridor, chosen as the highest-risk
test case. Result: 36 highway=cycleway ways found (correctly captured
by the existing fix), ZERO highway=path ways found at all.

**Conclusion:** the highway=path blind spot hypothesis does NOT hold
in this specific, high-profile corridor. This doesn't prove the
pattern never occurs anywhere in NYC or elsewhere, but it rules out
the single highest-risk location for it. Treating this as a checked,
cleared hypothesis rather than an open question -- the appropriate
level of confidence given a real, specific, well-chosen test, not
blanket certainty.

## Finding: NYC is the MOST fragmented city in the six-city comparison
Completed NYC's connectivity analysis. Result: 3,118 total components,
largest fragment only 4,038 nodes (11.1% of the low-stress network).

Full six-city comparison, complete:

| City | Largest fragment (%) | Total components |
|---|---|---|
| NYC | 11.1% | 3,118 |
| Toronto | 14.4% | 1,438 |
| Seattle | 34.1% | 735 |
| Corvallis | 41.8% | 172 |
| Vancouver | 83.5% | 325 |
| Amsterdam | 90.0% | 617 |

**This is a genuinely counterintuitive, newsworthy result.** NYC has
invested heavily and visibly in cycling infrastructure over roughly
two decades and has a strong public reputation as a leading US
cycling city -- yet it comes out as the MOST fragmented network
tested, not the least. Worse than Toronto by both measures (smaller
largest fragment AND more total pieces).

Plausible explanation, not yet verified: NYC's infrastructure
investment may be real but concentrated in specific corridors
(protected lanes on major avenues, greenways along the rivers) that
don't necessarily connect to each other or to the broader residential
grid -- consistent with the low overall LTS 1 share found earlier
(7.8%, lowest of all six cities) and the low edge-retention rate in
the low-stress subgraph (47.9%, also lowest of all six cities).

This reinforces the project's core methodological point: infrastructure
QUANTITY and infrastructure CONNECTIVITY are different things, and a
city's reputation for having "a lot of bike lanes" doesn't guarantee a
connected low-stress network. NYC is now the strongest illustration of
this distinction in the whole dataset -- a stronger example than the
original Toronto/Amsterdam contrast, since NYC's reputation runs
directly counter to what the data shows.

## IMPORTANT CAVEAT to NYC fragmentation finding: one-way doubling has a MUCH larger effect here than in Toronto
Ran the same one-way-doubling artifact test used to validate Toronto's
fragmentation finding, against NYC. Unlike Toronto (where disabling
doubling barely changed anything: 1,169->1,139 components, 16.3%->17.0%
largest fragment), NYC showed a dramatic swing:

- WITH doubling (current/reported number): 3,118 components, largest
  fragment 11.1%
- WITHOUT doubling: 2,291 components, largest fragment 27.3% -- more
  than DOUBLE the largest-fragment size, and 25%+ fewer total
  components

Cause: NYC has 41,618 one-way edges (a much larger share of the
network than Toronto's one-way streets), and 22,907 of them (55%)
would score low-stress WITHOUT the doubling rule applied. NYC's
famous one-way avenue grid means this single rule is doing far more
work here than in any other city tested so far.

**This does NOT mean the "NYC is the most fragmented city" finding is
wrong** -- the doubling rule may be correctly capturing genuine stress
on NYC's busy one-way avenues (which are often wide, fast, and
multi-lane, functioning very differently from a typical calm one-way
residential street). But unlike Toronto, where this specific concern
was tested and CLEARED, NYC's result cannot currently be presented
with the same confidence. The 11.1% / 3,118-component figure is
real output of the current model, but it is now KNOWN to be sensitive
to a specific, debatable methodological choice in a way Toronto's
figure is not.

**Honest framing for any write-up:** present NYC's fragmentation
finding with this caveat explicitly stated, or hold off on presenting
NYC as "the most fragmented" as a headline claim until this is
resolved. A defensible middle path: report a RANGE (11.1%-27.3%
largest fragment, depending on treatment of one-way streets) rather
than a single number, until there's a principled reason to prefer one
treatment over the other specifically for NYC's avenue grid.

**Not yet resolved. Worth revisiting**: is there real-world evidence
(rider reports, DOT data) about whether NYC's one-way avenues actually
feel comparable in stress to a 4+ lane two-way road, or whether the
doubling rule overstates it for this specific case? This is exactly
the kind of city-specific validation the LTS literature itself
flags as a real limitation of blanket rules.
