# Future Projects — Running List

Ideas and priorities banked across sessions, outside the core LTS
roadmap. Not committed to timelines, just captured so nothing gets
lost.

---

## Immediate priority
- **LTS Phase 3** — interactive map (in progress). Finish this before
  starting anything else new.

---

## Next up: Orca / Southern Resident risk model
PNW-focused, marine conservation. Overlay bathymetry, public whale
sighting data (OrcaSound, Whale Alert), and vessel traffic density
into a risk-scoring model -- same rule-based, config-driven
architecture as LTS, applied to a different domain. Directly
demonstrates the "transferable methodology" story across two
portfolio pieces. Scope this properly (real scope doc, explicit
reach-goal boundaries) before writing any code, same discipline as
LTS's original scoping session.

---

## After orca: tool-building practice projects
Chosen specifically to test/reinforce the "I love building usable
tools, not just analysis" realization from today -- each of these
passes the test of "a real person would actually open this and use
it for a real decision."

- **Tide-current-aware kayak/small-boat route planner** (PNW,
  NOAA tidal data) -- cheapest, cleanest way to re-test the "tool
  someone would actually use" feeling before diving into orca's
  bigger scope.
- **Banff trip-day dashboard** -- weather, sunrise/sunset, trailhead
  drive times, elevation profile, packing checklist per day. Built
  for personal use on the actual October trip.
- **Banff memento poster** -- GPS tracks + elevation strip + waypoint
  annotations + personal text, styled like a keepsake rather than a
  cartographic output. Consider building as a reusable script (drop
  in any GPX, get a styled poster) rather than a one-off, so it
  doubles as a "hand this to a hiking friend" tool.
- **City config generator/wizard for LTS** -- an interactive
  script/form that walks someone through their city's tag
  conventions and generates the YAML config for them, instead of
  requiring hand-written configs. Most direct "make LTS itself more
  tool, less report" move available.

---

## Other project ideas, lower priority / more speculative
- Vessel-speed-compliance checker (Southern Resident orca zones)
- Citizen-science orca sighting submission/validation tool
- Banff day-hike matcher (fitness level + preferences -> trail rec)
- Banff trailhead parking/crowding predictor
- "Which viewpoint am I looking at" tool (bearing + GPS -> visible
  peak names)
- Bike theft hotspot mapping (Toronto Police open data) -- side
  project, crime analytics, deliberately kept separate from transit
  planning portfolio focus
- Land use / zoning impact visualizer -- best "range broadener" for
  a second portfolio piece if orca ends up feeling too similar in
  shape to LTS

---

## Career-path notes (from July 15 conversation)
- Real realization: enjoy tool-building/making things modular and
  usable by others AT LEAST as much as the analysis itself --
  concretely, the LTS config system + giving it to Corvallis relative
  was the specific moment this became clear.
- Worth exploring "GIS Developer / Geospatial Software Engineer" as a
  distinct career lane from "Transportation Planner," not necessarily
  choosing between them yet. Companies to know: Conveyal (closest
  direct analog to what LTS does), Remix/Via, Replica, StreetLight
  Data, Ecopia AI (Toronto-based).
- Geography major + GIS minor is a legitimate, non-compromise path
  into tool-building roles -- domain knowledge often matters more
  than CS pedigree in this specific niche. Possible gap-filling
  electives if this becomes a serious direction: data structures, web
  development, databases.
- Ask directly in future informational interviews: "does your agency
  have an internal data/tools team, separate from planning analysts?"

---

## Daily-life dashboard tools (same "one page, answers what should I
do today" shape as the Banff trip dashboard, generalized to daily life)

- **Commute/city-life dashboard** (top pick) -- TTC service alerts on
  usual lines, weather, maybe fastest-route-today for a recurring
  destination (dojo, campus). Most direct daily-life translation of
  the Banff dashboard concept; solves a real existing problem
  (car-free, transit-dependent, weather affects mode choice) without
  needing a pre-existing routine to be useful.
- Training/gym-day dashboard -- planned workout for the day (judo vs
  running vs rest), weather if relevant, simple readiness note.
- Study/coursework dashboard -- pulls together upcoming deadlines
  across Fall 2026 courses, spaced-repetition style reminders for
  exam material.
- Music production session-starter -- pulls "what was I working on
  last" from Ableton project folders, maybe a rotating reference
  track/prompt to start a session.
- Weather-dependent decision dashboard -- translates today's weather/
  air quality/wind into a plain go/no-go recommendation for outdoor
  activity, rather than raw numbers to interpret.

---

## LTS: NYC and Helsinki (next session, not done tonight)

### NYC
Closes the original scope doc's loop (Toronto -> Vancouver ->
Corvallis -> NYC was the original planned order). A second large
North American metro alongside Seattle -- useful for testing whether
Toronto's severe fragmentation (1,438 components, largest = 14.4%) is
typical of big North American cities generally, or something more
specific to Toronto. Low-risk addition: NYC's OSM tagging should
behave like the other North American cities, no new architectural
surprises expected (unlike Amsterdam).

### Helsinki
More analytically interesting, not just "another city." Known for
extensive, well-integrated cycling infrastructure, but geographically
LESS compact than Amsterdam -- a genuine test of whether Amsterdam's
90%-unified-network result is about infrastructure QUALITY or simply
about Amsterdam being small and naturally connected (a caveat already
flagged in methodology.md). If Helsinki also shows high connectivity
despite being bigger/more sprawling than Amsterdam, that's a much
stronger version of the Amsterdam finding. If it doesn't, that's
equally valuable -- it would nuance/bound the Amsterdam claim rather
than just repeat it.

Also worth going in expecting a possible new standalone-cycleway-style
surprise -- Nordic/Finnish cycling infrastructure has its own mapping
conventions, not necessarily identical to Dutch tagging patterns.

### Scope note
Both are legitimate additions but real work, not quick tack-ons: each
needs a full fetch/score cycle, and ideally the same fragmentation
depth given to Toronto/Amsterdam (not just base LTS scoring) to
actually answer the questions above. Treat as a dedicated next-session
item, not squeezed into an already-long session.
