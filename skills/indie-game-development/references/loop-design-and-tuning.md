# Loop design and tuning (before building)

Turn a pitch into a loop that has no dominant strategy, on paper, in under an hour.

## 1. Minimize state
- Use the fewest independent variables (0..1 floats). If one quantity is the theme's
  metaphor for another (the monster's distance IS the illness), DERIVE it:
  `func distance() -> float: return 100.0 * (1.0 - paranoia)`. Three independent meters
  allow nonsense states (threat at the shore while the illness meter is low).
- Typical pair for social horror: an internal meter (illness/fear) and an external one
  (companions' worry). Hang AV tiers on thresholds of the internal one (0.25 / 0.5 / 0.75).
- Count time in discrete beats of the clock event (e.g. 12 firework bursts), not seconds,
  so tuning is deterministic.

## 2. Verb table
One row per player verb: when it is available (gap / flash), delta to each variable, note.
Rules:
- The threat must also be where you cope. If looking only hurts, the optimal play is to
  never look and the horror vanishes. Looking without a tool feeds it; looking with a
  tool fights it; not looking lets a passive tick run.
- Every reducer has a cost on the other meter or a scarcity (limited doses, diminishing
  returns per use, side effects that impair the core verb for N beats).
- Exactly one verb reduces the external meter (e.g. talk / ritual), and it costs a beat
  you did not spend coping.
- Each meter needs a consequence at 1.0 that ends or changes the run, plus a mid
  threshold that changes play (e.g. at 0.6 companions block the view).

## 3. Ending resolution order
Write endings as an ordered table of conditions (first match wins), e.g. internal hits
1.0 -> breakdown; external hits 1.0 -> branch on internal; show ends -> branch on internal.

## 4. Strategy sim
Write `tuning_sim.py` next to the design doc: a `P` dict of tunables, `play(strategy,
skill, seed)` returning an ending, and named strategies (passive, stare, spam each single
tool, mixed coping) run 1000x at timing skill 0.5 and 0.8. Read-out targets:
- every lazy or single-tool strategy lands on a DIFFERENT failure ending;
- only mixed coping reaches the good ending;
- skilled play should not win 100% if the theme says "sometimes it doesn't hold"; add
  late-show pressure (faster tick in final beats).
Any strategy at 100% good ending is a dominant strategy: fix it with diminishing returns
or scarcity, then re-run. The sim is for shape only; real numbers come from playtests.
Retire it once the playable build exists: juice (audio, feedback, tension) changes player
behaviour, so port every `P` value into the Godot tuning resource and tune from playtests.

## 5. Adaptive difficulty (Karl's target)
Target: a skilled player can reach ANY chosen ending on the first try (failure endings by
deliberate strategy); a weaker player reaches the good ending by run 2. Two invisible
layers, both needed (timing adaptation alone lifts weak players far too high; the
director alone does not help weak hands):
1. Timing window: miss -> window x1.2, hit -> x0.9, clamp 0.3-3.0; model hit chance as
   `1 - (1 - base) ** win` so the window scales cleanly. Persist it across runs
   (`user://dda.cfg`), since one run has too few checks to converge.
2. Director: the passive tick follows a target curve of the internal meter over the show;
   `k = clamp(1 + gain * (target - meter) / 0.25, 0.4, 2.2)`. Coasting speeds it up,
   struggling slows it.
- Adaptation must never rescue a lazy or single-tool strategy; re-run the sim with DDA on
  and confirm those still fail 100%.
- A symmetric director makes skilled players fail a few % (conflicts with "any ending first
  try"); a help-only director makes everyone win. Surface the trade-off, let playtest decide.
- Never tell the player (no assist popup); offer an explicit "wider timing" accessibility
  toggle instead.
- A short tutorial segment before the main loop pays twice: it teaches each meter through
  an in-world event instead of a tooltip, and one forgiving coping check seeds the timing
  window before the first real beat.

## 6. Incremental / sim-sandbox design (reward layering)
- Name 3 pillars up front and require every feature to serve one (e.g. every grain is
  real; the core verb feels incredible; something new every 10 minutes).
- Pillars of feel: input (same-frame response), feedback ("juice", Jonasson & Purho 2012;
  audio first, people forgive plain art sooner than a flat crunch), readability,
  progression, one identity idea. Audio/visual/input are channels of the feedback loop.
- Make the simulation carry the economy ("the pixels are the loot"): materials read from
  the art, value counted per unit, purity multiplier, so sorting/automation is the idle
  puzzle layer instead of decoration.
- Reward table by timescale, each with its mechanism: seconds (sensory), ~1 min (next
  upgrade visibly close, goal gradient), ~5 min (new object, curiosity), 10-20 min (new
  machine/material that changes rules, novelty), ~1 h (visible boss gate), era (prestige
  into a new world/asset pack), game (collection + ending).
- Grind rewards list: base value, first-discovery bonus, rare variants visible BEFORE the
  payoff (anticipation), hidden jackpot cores with a loud win signal, active combo with an
  overfeed failure, small completable bundles (~1/min), losses shown visibly.
- Every resource a producer emits must have a sink (an order/mould/machine that consumes
  it), or that branch dead-ends and its storage fills uselessly. And an order/recipe system
  must offer 2-3 choices matched to what the player is actually producing: one fixed
  recipe stalls the whole loop whenever the intake mix drifts.
- Real consequences are fine when visible and caused by neglect (e.g. workers crushed
  past a readable pressure gauge, hire fee lost); tune so loss comes from neglect, not luck.
- Hazards/new materials: each is a threat AND a resource, never only a tax; introduce one
  per band or world.
- Physical limits make prestige land: e.g. storage occupies space equal to capacity until
  a prestige machine relaxes exactly ONE constraint (space, distance, sorting time).
- Economy of mixed piles (measured): a falling-sand pile HOMOGENISES, so any sample leans
  only ~1/N on one material and pocket-sorting caps near 1/N. Make the core verb two-stage
  (rough sort now vs clean cast later, the second stage a slow polish worker/machine) and
  never put a quality gate above what mixing allows.
- Purity/quality curves: when a ubiquitous by-product counts as a contaminant (pixel-art
  outlines are ~40% of pixels -> "soot"), quality targets become unreachable. Give it zero
  value and compute purity over real materials (burn-off is a fine fiction), and fold minor
  materials into majors (green -> flesh) so they stop diluting share math.
- Floor product: always keep one product that accepts ANY mix at a flat price, and let
  quality decide WHAT a load becomes, never whether the machine accepts it — gating input
  on quality starves the loop, and gating a sale on a quality level only an unbought
  upgrade can reach deadlocks player and bot alike. Give junk a home (a mixed bin feeding
  the floor product) or sorting has nowhere to put imperfect scoops.
- Keep the engine setting-agnostic (materials, machines, orders as data tables) so an
  alternate setting is a reskin, not a rebuild.
- Scope guard: list systems, define a v0.1 slice that must be fun alone, and a cut order.
  When Karl adds ideas mid-design, fold them into the doc and the cut order rather than
  debating them; flag only the scope or sim-cost tension they create.
