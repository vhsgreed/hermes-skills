---
name: indie-game-development
description: "Use when designing or building small indie games."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Godot, Game-Design, Horror, Indie, Audio]
    related_skills: [niche-validation, p5js]
---

# Indie game development (Godot or web, short games)

For designing, scoping, and building short games (horror, puzzle, sim, incremental) that
Karl publishes on itch.io first. The goal is a polished short game inside a fixed hour cap,
with reusable parts going into a shared framework repo. Karl has said a game must be built
from prompts end to end (agent writes code, tunes with bots, screenshots; Karl playtests
and decides), so prefer genres that are code-heavy and art-light.

## Roles (standing, Karl's call on game projects)

The agent MANAGES the project and Karl plays it. The agent owns scope, the order of work,
cuts, deadlines and the definition of done, and tells Karl what to look at and what
question to answer. Karl owns eyes and taste (short playtests, an unconditional veto on
"this feels bad") and the human-only steps: his own accounts, release clicks, community
posts.
- Definition of done: the pre-registered probe is live and its bar returns a verdict.
  "Finished" never means feature-complete; building features the probe cannot measure is
  the thing to cut first.
- When Karl hands over a feature list, triage it yourself into in-slice / deferred / cut
  as a table with owners and dates, then execute. Do not ask permission per step.
- Give ONE playtest assignment at a time, timeboxed (~30 min), with 1-3 pointed questions
  answered in one line each. His unanswered playtest questions block the next design
  decision, not the whole pipeline.
- Numbers over mood before planning: an undefined goal is unmeasurable, say so. Report
  measured-vs-bar first, what changed second, next assignment third.
- Scope that misses the verdict metric gets pushback, and reported playtest defects are
  fixed and verified before any new feature.

## When to Use

- Karl pitches a game idea and wants pushback or a design doc.
- Setting up Godot / the Godot MCP, scaffolding a project, or building/polishing a game.
- Scoring a game build probe (hours per game, stranger pickup).

Market and revenue questions go to `niche-validation`.

## Always-on rules (Karl's polish bar)

These come from his list of what ruins short horror games; treat each as a release gate.
- Playtested start to finish by someone other than Karl before release. His past network
  is off-limits, so playtesters are strangers (Godot Discord playtest channels,
  r/playmygame), posted around day 5 of a week build.
- One art direction: one asset style, a limited palette, low resolution with integer
  nearest-neighbour upscale, audio degraded to match the era. Nothing off-style. Default
  to 960x540: exact 2x to 1080p and 4x to 4K, no pillarbox on streams/YouTube (640x480 is
  4:3; 854x480 and 640-line heights do not scale evenly into 1080).
- Content warning: one terse line, no apology, covering only real medical concerns plus
  the theme, e.g. "Contains flashing lights, sudden loud sounds, and themes of X." No
  help-resource or disclaimer padding; it is a horror game.
- Accessibility that is required, not cut: photosensitivity warning + flash-intensity
  slider when flashes are a mechanic, toggle for any sustained/high tone, subtitles.
- Narration: at most 3 sentences per beat, and the player is never locked in place while it
  plays (Half-Life style: talk while the player can move/interact), or use a real cutscene.
- Honest store label: a walking/driving sim is labelled as one; never pitch "horror"
  without horror mechanics.
- Player-facing names are plain language (e.g. red/grey/white, not flavour names like
  minerals or alchemy terms) unless the flavour IS the joke; and every requirement the
  player must meet is stated on the control that needs it (colour swatch + in-stock count
  on the product button, target shown on the machine), never hidden in a menu or doc.
  Karl stopped a session over mineral colour names and over mould targets that were
  guessable only from code.
- Audio balance is make-or-break, for players AND for streamers editing footage. Spec it in
  loudness, not peak dB: ambient bed about -30 to -26 LUFS short-term, dialogue and SFX
  about -20 to -18, whole mix about -18 LUFS integrated, jumpscare peaks limited at
  -1 dBTP (never 0 dBFS). Check with a loudness meter on a recorded playthrough, since that
  is what streamers hear (YouTube normalizes to about -14 LUFS).
- Physics and movement speed tuned and tested, not left at defaults.
- Add a FoV slider when the design uses a narrow FoV (motion sickness).
- Engagement mechanics are core game design, not something to refuse or lecture about:
  help fully with reward loops, variable/jackpot payouts, loud win signals, near-miss
  tension, prestige pacing, "one more upgrade". Karl pushed back hard on an over-broad
  refusal. The only line, stated once and briefly: no real money inside a random reward
  (paid loot boxes/rerolls), no deceiving the player (losses disguised as wins, misleading
  odds), no punishing absence (decay, losable streaks, guilt timers). Do not repeat it
  every turn.
- When Karl cites research (psych studies, papers), fact-check each claim in a table
  (real / garbled / wrong + correct citation) and then translate it into a design rule.

## Procedure

### 0. Genre and idea triage (when Karl brings a genre or a list of ideas)
- Pull the genre's top titles from data, not memory: `references/genre-market-research.md`
  (SteamSpy tag recipe, tiered common-denominator analysis, incremental-genre findings).
- Score each idea in one table: genre fit, buildability from prompts, clip-ability,
  named incumbents from a direct search (with review/CCU numbers), verdict. Recommend one,
  allow combining two ideas, name a runner-up, reject the rest with one line each.
- Before designing, identify the tech risk and pre-register a spike pass bar (e.g. fps at a
  grain count) with a named fallback; write it to a notes file before any code.

### 1. Design pushback before building
- Find the ONE core mechanic already in the pitch and build the loop from it. Reject
  unrelated minigames (pong/tetris/2048 etc.): each is a separate game that breaks the
  scene and eats the hour cap. Accept on-theme skill checks when they feed the same state
  as the core loop; build them as ONE input mechanic (timing ring / hold-and-release) with
  several thematic skins, so extra skins cost art and text, not code.
- Then turn the loop into explicit state variables, a verb table, and an ending resolution
  order, and run a strategy sim before building: `references/loop-design-and-tuning.md`.
  Karl thinks in GDScript-style variables; answer in that form.
- Make the tension a trade-off the player feels every cycle (e.g. watch the threat vs look
  normal to companions), with a clock (an event sequence) and 1-3 endings.
- Stagger verbs: introduce ONE new verb per stage, each triggered by an in-world event
  (a text, a scare, a friend asking "are you okay?"), with a one-line "why" as the
  player's own thought. Giving every verb at once confused Karl in playtest 1 ("a lot of
  options, no clear explanation why"). Open with a calm segment before the main event
  that teaches the first verbs and replaces intro cards.
- A mechanic must be readable at the target resolution in the time it is shown (e.g. a
  1-second flash needs a high-contrast silhouette); check it in the first playtest.
- Keep the core commodity physical (Karl's standing law: no teleporting). Every transfer
  between places needs a visible carrier (jaws, belt, pipe, chute, gate, worker hands);
  the commodity may become a count only INSIDE a closed machine (bin, mould, pipe, belt)
  and re-enters the world at that machine's outlet. Drops route per grain to what is
  physically under the cursor (a store accepts only its kind; the rest spills as loose
  sand). Before adding any convenience transfer (catcher -> store, store -> mould), ask
  "what carries it?"; if nothing visible does, build the carrier or don't add it.
- Physical means simulated, not animated: a tool that "holds" things must hold them by
  contact (tool shapes stamped into the cell grid like sprites, jointed chain), never by a
  spring/hover pulling the object under it. Karl reads lerped lag and hover as fake.
- Work from a board, ONE card at a time (Karl, after a multi-surface run left every part
  unfinished): `BOARD.md` holds his feature tree with a status per node; a card enters
  BUILD only after he approves its SPEC, written as GDScript-style pseudocode plus a
  done-check he can judge in <= 5 minutes of play. English prose specs were too lossy.
  Nothing outside the BUILD card is touched; new ideas go to ICEBOX.
- Engine choice follows perspective: side-view per-pixel falling sand favours TypeScript +
  typed arrays; a top-down/iso voxel-column (heightfield) sand with UI, minimap and
  pathfinding favours Godot, but only after a pre-registered web-export sand spike.
- Iso heightfield (voxel-column) sand in Godot: algorithm (descent pour + relax on disturb,
  fixed per-column slope tolerance), measured costs, the C++ GDExtension web build, fixed-iso
  camera, mound-only shadows with a non-flipping sun/moon arc, cheap noise ground + one water
  feature, the JavaScriptBridge test harness, and the multi-scale matter core (1e9 cubes as
  per-megacell-layer counts + exact arrangement generator + hot/cold materialisation):
  `references/godot-iso-voxel-sand.md`.
  Order: try the algorithm in GDScript first, port only the sand kernel to C++ when the
  pre-registered tick bar still fails; the fallback order is fixed before the spike.
- Bar timers wrap the WHOLE subsystem tick (e.g. pour + bite + relax + readback) from the
  start, never one function: an optimisation that moves work into another function hides it,
  and a spike signed off on the hidden number has to be reopened and re-reported.
- Construct exact invariants by construction, never with a repair pass: scattering an exact
  multiset (class counts) over a structured valid-slot set is done by enumerating the valid
  slots canonically and applying a bijective permutation over [0,T). Proportional floors plus
  a fixup loop both drift and the fixup's rescan dominates the hot path. Permutation pitfalls:
  an incremental (j*S+O) mod T walk needs S reduced into [0,T) with gcd(S,T)==1 or it escapes
  range and scrambles the multiset; affine+xor compositions are bijective only on power-of-2
  domains. Check conservation PER CLASS, not just totals — totals matched exactly while
  classes drifted hundreds of grains.
- Light and shadow are judged across a whole cycle, not one frame: before a day/night card
  goes to review, check numerically that the shadow direction never jumps (max step between
  samples) and screenshot morning/noon/dusk/night. A sun path that crosses the camera axis
  flips the shadow at noon, and a moon that does not cast leaves night shadowless.
- When Karl hints at a future scale ("how big this could get"), ask for the number (cubes,
  footprint, height) and answer with which limit breaks first (column height type, chunk
  memory, draw footprint, active-set cost) and the fix cost; log it as an ICEBOX card, do
  not build for it inside the current card.
- Track the agreed slice as a checklist and report against it every update. Never swap a
  spec item for a quicker abstraction silently; if a substitute is necessary, name it as a
  deviation in the same message. Karl audits builds against the agreed list.
- Mental-illness premises written from the author's lived experience: the player-as-patient
  framing is theirs to use; do not treat it as a borrowed trope. Keep two guardrails: (a) the
  horror is the doubt, and breakdowns are shown from inside (first person, a few seconds,
  loss of control), never as a third-person spectacle; (b) every coping tool works and
  every tool costs, so failure reads "sometimes it doesn't hold", not "you didn't try".
  Mechanize the author's real experiences (e.g. side effects as blur/vignette/tone that
  also impair the core verb) instead of moralizing. Play first, commentary in a short
  skippable intro and per-ending outro cards (outside play, so the 3-sentence cap is not
  broken). Must stay accessible to a general audience.
- Endings: multiple endings are wanted and cheap in logic; the cost is writing and final
  shots. Keep the core ambiguity unresolved and let endings vary how real its effect on
  the player was. Build order: neutral/survival ending first, then the failures.
- Write the design to `DESIGN-<name>.md`: pitch, loop, scope cuts, polish bar, and a cut
  order to apply if the cap is hit (e.g. endings -> secondary systems -> dialogue choices).
- When transferring an earlier chat answer into the doc, carry every section over (lists,
  tables, the WHY column), not a condensed version; Karl checks and will paste back what
  went missing. Incremental/sandbox reward layering: loop-design reference section 6.
- Karl's own vision description is the authoritative spec: when it conflicts with what is
  designed or built, rewrite the design doc in a section explicitly marked as superseding
  the old text and rebuild to match. Where his wording is ambiguous enough to delete a
  core system (a phrase that could mean "remove the pile" or "redesign the pile"), clarify
  before cutting; a vision sentence is not an implementation constraint to reinterpret.
- Do not benchmark while another heavy job (model run) uses the machine; write the spike
  code meanwhile and measure after.

### 2. Hour cap, estimates, assets
- Every work session, Hermes-assisted ones included, goes in `probe-hours.csv`
  (date,start,end,task), wall-clock including time waiting on generation. Setup done by
  the agent does not count.
- Do not lead with inflated hour estimates or warnings that scope will not fit; code is
  generated fast and the real limits are tokens/s and assets. State the cut order and let
  the hours log decide.
- Plan assets first, since they are the bottleneck: CC0 packs (Kenney, Quaternius, KayKit),
  CC0 audio (Freesound CC0 filter, sfxr); a full-frame palette-quantize + dither shader so
  mixed-source assets read as one style; silhouettes/night to hide detail; effects
  (fireworks, water, light) as shaders/particles instead of assets.
- Pick the palette/LUT BEFORE collecting assets, or polish becomes recoloring.
- Theme variety via CC0 packs: one pack + palette + one new mechanic per world/level
  (e.g. DCSS tiles for a dungeon world, Kenney packs for others). Check each pack's exact
  licence on its source page: `references/sim-tech-and-assets.md` lists known traps.
- Engine choice: Godot web export (WebGL2 Compatibility renderer, no compute shaders,
  slow per-pixel GDScript) is a poor fit for per-pixel simulations; use TypeScript +
  typed arrays (+ Rust/WASM fallback) for those. Details in `references/sim-tech-and-assets.md`.
- Billboards only for things seen at distance (crowds, animals); companions the player
  walks around at 2 m need rigged low-poly models (darkened), or they read as cardboard.
- Asset list format: tiers M/S/C with a source code per item (CC0/FS0/shader/proc/Karl's
  own photo/AI-gen with itch disclosure); Karl's photos cover moon, skyline, stills.
- At the cap: stop adding, ship what exists, score honestly. Never push through; Karl's
  previous creative project ended on hours-per-unit overload.

### 3. Setup (once per machine)
- Install the official Linux build from GitHub releases (latest tag via
  `api.github.com/repos/godotengine/godot/releases/latest`), verify against the release's
  `SHA512-SUMS.txt` with `sha512sum -c`, unzip to `~/.local/opt/godot/`, symlink to
  `~/.local/bin/godot`.
- Godot MCP: Coding-Solo/godot-mcp, built from source in `~/src/godot-mcp`
  (`npm ci --ignore-scripts && npm run build`), then
  `hermes mcp add godot --command node --env GODOT_PATH=$HOME/.local/bin/godot --args $HOME/src/godot-mcp/build/index.js`
  (`--args` must be last). Tools load in a new session or after `/reload-mcp`. Before
  adopting a different MCP, check stars, last push, license, and grep its source for
  spawn/exec/network calls.
- Export templates (~1 GB download, 2 GB unpacked) only when publishing or a web spike is
  near. Verify with `grep ' Godot_v<ver>-stable_export_templates.tpz$' SHA512-SUMS.txt |
  sha512sum -c`: a loose grep also matches the mono .tpz and the check fails on a file never
  downloaded. Web templates include `web_nothreads_release.zip` (single-thread build).
- Karl also has the snap `godot-4` (same 4.7.2). `godot` = the pinned official binary.
  Snap is sandboxed: its `user://` lives under `~/snap/godot-4/`, so saves (e.g. the DDA
  window) differ between the two; the snap auto-updates and could save in a newer format.

### 4. Project skeleton and smoke test
- Low-res pixel setup in `project.godot`: `window/size/viewport_width/height` = target res,
  `window/size/window_width/height_override` = 2x, `window/stretch/mode="viewport"`,
  `window/stretch/scale_mode="integer"`, `rendering/textures/canvas_textures/default_texture_filter=0`.
- `.gitignore`: `.godot/`, `*.import`, `export/`.
- Smoke test headless: `godot --headless --path . --import`, then run the project with a
  main script that prints a marker and calls `get_tree().quit()` when
  `DisplayServer.get_name() == "headless"`; grep for the marker and `ERROR`.

### 4b. Grey-box build pattern (first playable)
- All balance numbers in one `class_name Tuning extends Resource` script with `@export`
  groups, instanced as `tuning.tres`; load and `.duplicate()` at start. Karl tunes in the
  inspector, not in code.
- F3 debug overlay showing every state variable, the DDA window and director k.
- Self-play autotest via user args (`godot --headless --path . -- --autotest --skill=0.8`):
  an autopilot runs the strategy, aims at the ring with probability `skill`, prints
  `LF_BURST`/`LF_END` lines, quits at the end. Shrink every timer in autotest mode (gaps,
  flashes, post-beat pauses) or each run takes minutes and the tool call times out.
  Parallelize runs with `printf ... | xargs -P N -I{} sh -c 'godot ... --skill={}'`
  (foreground `&` is refused by the terminal tool).
- Visual check: a `--shot=PATH` arg that forces the key moment (flash + figure + ring),
  waits a few frames, saves `get_viewport().get_texture().get_image()` to PNG and quits;
  run WITHOUT `--headless` (headless has no renderer) and inspect with vision. Catches
  overlapping HUD text and unreadable silhouettes before Karl plays.
- Procedural placeholder audio with `AudioStreamGenerator` (brown-noise bed, boom, heartbeat,
  tone), hard-clamped below -1 dBFS; say plainly that loudness was not measured.
- Report honestly: what was verified (autotest endings per skill, screenshot) vs not
  (real input feel, audio by ear), plus expected playtest problems from the bot logs.

### 4b2. Browser (web) game spikes
- Benchmark in real headed browsers with Playwright from Python (`channel='chrome'` for
  system Chrome; `python3 -m playwright install firefox` for Firefox). Do not use
  browser_exec local mode: it fails while Karl's Chrome holds the profile lock.
- Measure per-frame work time (performance.now around sim+render) as the deciding
  number; Playwright Firefox paces rAF at a flat ~58.6 fps regardless of load, and Firefox
  timers are 1 ms resolution. Pre-register that caveat.
- Spike procedure: write `SPIKE<n>.md` with numbered PASS bars, the winner rule and a
  named fallback BEFORE any code; do a short unrecorded smoke run (20 s) with screenshots;
  any fix made after the smoke run goes into a "Deviations" section with the reason, bars
  unchanged; then the recorded 60 s runs; then append RESULTS (table per bar per browser,
  verdict, honest caveats incl. what was not tested). Inspect screenshots with vision as
  a bar of its own: numeric bars passed while sprites visibly floated/jammed.
- Serve the page with `python3 -m http.server PORT --directory web` as a background
  process (foreground servers are refused); kill it when done.
- Measured baselines, rigid-body coupling recipe, palette snapping: see
  `references/sim-tech-and-assets.md` (worked example: the author's sorting incremental).
- Slice build and autotuning (after the spike passes): write FRAME.md acceptance bars
  BEFORE the slice code (economy: first reward <= 90 s and N rewards per 5 sim-min;
  perf: work p95; conservation: exactly zero resource loss; visual review at target res).
  Pre-registered bars are floors: never raise them after seeing numbers.
- Gate every web build with `npx tsc --noEmit --strict --target es2022 --module esnext
  --moduleResolution bundler --lib es2022,dom --skipLibCheck src/main.ts` BEFORE trusting
  it: esbuild does not type-check and will happily bundle a null-crash that only fires at
  runtime.
- Autotune with a scripted bot in-page: `?autotest=1&turbo=N&dur=S` runs the game N ticks
  per frame with a bot doing the real verbs (intake, carry, buy, fulfil orders); the page
  sets `window.__kpi` + `window.__done`; a Playwright runner reads them into
  `out/kpi-<mode>-<browser>.json`. Fix ONE bottleneck per run and re-measure; read the KPI
  file from disk (printed copies get truncated).
- Quantify a mechanic with A/B bot modes (same bot, mechanic disabled as a baseline mode
  in the URL) compared at a fixed sim-minute; a premium that never shows in the KPIs is a
  tuning bug, not a mystery. Bot state machines need explicit sub-states (a `spotted`
  flag, not just elapsed-time thresholds in separate branches): a decide step at 90 ticks
  silently pre-empts a survey step at 150 and the whole phase loops past its own setup.
- Audit the bot's mode gates before retuning an economy: a policy branch gated on a bot-mode
  string the runner never passes silently starves the loop (every unit falls to the fallback
  path) while the KPIs stay structurally valid. When measurements show the system stuck on
  its default path (nothing in the sorted stores, all output at the flat price), grep the
  policy for mode strings first.
- Before tuning a player verb's economy, compute its structural purity ceiling from corpus
  statistics: a scoop from a mixed pile with many classes rarely reaches a sort threshold,
  and routing whole units (a sprite's grind stream to one bin) caps purity at the median
  unit's dominant-class share (~47% for the DCSS set). No price curve fixes a ceiling;
  real purity needs grain-level separation (a sorter machine). Check the ceiling before
  building the verb, not after an A/B.
- Before an A/B, confirm the loop throughput yields enough output units to compare (e.g.
  5+ casts per arm): saved layout/tune values from playtests can starve the loop (slow
  belt + slow gears = 1 cast in 10 min), making both arms noise. Read the live tune first.
- Bot runs longer than ~5 minutes go in a background terminal process with notify, run in
  sequence (sort, then dump) in one command; foreground calls hit the tool timeout and lose
  the result.
- Have the page capture `window` 'error' events to `window.__err` and have the runner print
  it beside the KPI: a try/catch around the frame loop misses listener and HUD throws, which
  are exactly the crashes that vanish between runs.
- Any reclassification of content (materials to colour classes, tier regrouping) invalidates
  every tuned threshold: first measure the class distribution over the whole asset corpus,
  then re-derive purity/pacing thresholds from those statistics. Carrying constants across a
  classification change produces economies that only sell the fallback product.
- Fullscreen/camera conversion: keep draw code in world units via a transform scaled by
  px-per-cell, and rescale every font size by the same factor (font px is a backing-pixel
  quantity, so changing the backing from world-unit-sized to window-sized multiplies text
  2-4x). Map mouse input rect -> backing -> world units so CSS/backing drift cannot skew
  aim, and re-resize each frame when the container size drifts. After every WebGL canvas
  resize call `gl.viewport(0, 0, w, h)`: the GL viewport stays at its context-creation size
  (300x150), so the 2D overlay goes fullscreen while the world texture renders into a corner.
  Verify by reading `gl.getParameter(gl.VIEWPORT)` against canvas width/height, not by eye.
- When a rendered scene disagrees with expectations, expose debug handles on window
  (engine state, game state) and dump state (grain/material histograms, body positions,
  per-region probes) instead of theorising over the screenshot: a 'render bug' is often
  just crowd stacking or frozen bodies, and only state settles it. Counters beat
  inspection: monkey-patch the suspect method from Playwright evaluate (after waiting for
  the game handle on window) to count calls and returns — "never called" and "called but
  produced nothing" are different bugs with different fixes.
- Report each build run's KPI against the pre-registered bars in a BENCH.md (bar, measured,
  verdict), with an honest not-verified list (audio by ear, input feel, the fun question).
- Karl's playtest defect reports come first: fix and verify every reported defect and
  reply to it before resuming bot/economy tuning. A passing bot run says nothing about
  input feel, and drifting into tuning left his report unanswered.
- Verify input with REAL events (Playwright `page.mouse.move/down/up` on the canvas
  container), never by setting the game's target fields: the bot and a hand-set
  `claw.tx` both worked while the mouse did nothing. An overlay canvas stacked on the game
  canvas swallows events; set `pointer-events: none` on overlays and listen on the
  container.
- Bot carry/release logic keys on the CARRIED object's state (position fully over the
  target, low, velocity ~0), not the effector's: a held object lags and swings, so
  releasing when the claw is over the belt drops it short. Verify by sampling where each
  dropped object is ~1.5 s after release (count on-target vs miss).
- Physical grabber in a cell-sand sim (claw/jaws), in tick order: (1) run the capture
  BEFORE the effector's own solid stamp in the same tick - stamped solids displace the
  enclosed cells first and the capture then finds an empty pocket; (2) edge-trigger the
  capture at close-START, not at a closed-angle threshold - the closing sweep plows the
  bite out before any threshold fires; (3) reserve the cup (space between the jaws) out of
  the stamped shapes or the closed jaws are a solid slab with zero interior; (4) key
  release on the INPUT let-go, not the visual open angle - the angle lerp lags the button
  by several ticks, so angle-keyed release re-dumps the load the tick it was captured;
  (5) keep the carried load OUT of the cell grid: hold it as a list on the effector, draw
  it on the overlay, and count it in the conservation audit as "holding" - painting it as
  real cells each tick (erase+rewrite) duplicates sand, because the painted cells fall
  during the sim step and the erase only clears cells still at their painted index;
  (6) confirm the effector's
  max reach covers the full world depth before debugging capture - a segment-clamped
  chain short of the floor 'fails to grab' for purely kinematic reasons.
- Any helper that pushes a grain out of a solid's way (displace) COPIES it to free space;
  the caller must then claim the source cell unconditionally (set it to the solid). A
  conditional "claim only if now empty" leaves the original in place and doubles sand on
  every stamp. Grep every new caller of such helpers for that pattern.
- Ship a conservation guard in the game itself, not only in the bot harness: every ~60
  ticks compare spawned vs accounted grains; on a negative delta beyond a small tolerance,
  pause the sim, show a message and log it. A duplication bug otherwise grows the grid
  until the player's PC crawls, and the player can only report "it got slow".
- Before handing a new physical verb to Karl, run a hard-use loop with real mouse events
  (12-16 grab/drag-through/carry/release/sprinkle cycles at the live mound) and check the
  audit delta, lost count and heap after each cycle. Single happy-path probes passed while
  real play duplicated sand.
- Give the live dev server a client log so Karl's playtests are observable without him
  describing them: page sends `navigator.sendBeacon('/log', json)` for window 'error' /
  'unhandledrejection', a boot line (UA, viewport, DPR) and a state snapshot every 5 s
  (verb state, counts, canvas backing vs CSS size, `__err`); the static server appends
  POST /log to `out/client.log`. Ask him to hard-reload (Ctrl+Shift+R) after each rebuild,
  or the log shows nothing from his session. Run the server as a persistent background
  process; one started inside a foreground command dies with that shell.
- Verify mechanics with per-object traces, not totals: e.g. record for every body where it
  first lost pixels (distance from the gear rim) and where it ended; that separates
  "grinds on contact" from "melts at a line" and finds bodies escaping past the machine.
- When Karl asks to sort out the layout himself, make the layout data-driven and give
  him an editor: `references/web-level-editor.md`. When a new machine needs room, copy his
  saved layout to `layouts/` first, then shift his pieces as a block so their relative
  positions stay his, and say so in the report.
- When refactoring by slicing a source file between comment markers, assert the markers
  are unique and start < end before cutting: a generic marker ('// workers') can occur
  earlier in the file and the slice silently duplicates a whole region (shows up as
  duplicate function declarations from tsc, not as a bad slice).

### 4c. Session hygiene on autobiographical premises
- When Karl says it is late or he is tired: document only (playtest notes file), no code.
- Playtest notes go to `PLAYTEST-N.md`: raw feedback, answers to his questions, proposed
  fixes (not built), still-to-test.
- Long sessions writing the author's own experience into endings/stigma can produce strong
  resistance. Do not push through or decide while he is sleep-deprived; next day separate
  tiredness vs the material vs the project. The loop/mechanics are premise-agnostic, so a
  premise swap is a cheap fix if the material is the cause; a clean stop is fine too.

### 5. Publish (probe mode)
- itch.io CLI = butler (official, MIT): install from
  `https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default` into
  `~/.local/opt/butler`, symlink to `~/.local/bin`. It only pushes builds
  (`butler push export/web user/game:html5`, delta uploads, versioned channels). Karl
  creates the page once in the browser (text, tags, price, warning) and runs `butler login`
  himself so the key never passes through the agent. Third-party "itchio-cli" repos are
  negligible. Read stranger view counts from the dashboard; the server API was not
  confirmed to expose views.
- itch.io only ($0), PWYW with a small suggested price, screenshots + GIF. Steam Direct
  ($100/app) only after a game shows stranger pull. Post to public communities, strangers
  only. Market numbers: the creator-and-game-economics reference in `niche-validation`.
- Re-read every in-game and product name as a stranger before publishing (double meanings,
  slang) and flag it once; keep it if the joke is intentional.
