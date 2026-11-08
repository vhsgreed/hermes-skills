# Pixel simulation tech and CC0 asset licences

## Falling-sand / per-pixel simulation
| Approach | Notes | Use |
|---|---|---|
| CPU cellular automaton | Bottom-up scan, alternate L/R per row, per-cell updated-this-tick parity bit, chunks with dirty rects so settled chunks sleep. Noita multithreads with a 4-pass checkerboard (chunk + 32 px margin). Source: Purho, GDC 2019. | Default: exact grain counts for economy, easy reactions |
| Rust -> WASM (Sandspiel) | JS Uint8Array view over WASM memory uploaded as a WebGL texture each frame, no copy. MIT, maxbittker.com/making-sandspiel | Fallback when TS misses the bar |
| GPU block CA (Margolus 2x2, diagonal offset alternate steps) | Race-free, very fast; blocky/diagonal motion, branching reactions hard, CPU readback needed for counting. github.com/GelamiSalami/GPU-Falling-Sand-CA | Only for pure visuals |

- Default sizing: 480x270 cells at 2x on a 960x540 viewport (~130k cells), chunk 32.
- Measured (geekom, Ryzen 7940HS / Radeon 780M): TS typed arrays, single thread,
  50-75k grains = 0.3-1.5 ms/frame Chrome, 1-4 ms Firefox. WASM not needed at this size.
  Chunk sleeping saves little here (16 px chunks cost MORE than none when everything
  moves); it pays off for wider worlds, resting-sand processes, and per-chunk texture upload.
- Benchmark the real game case (settled mound + pour stream + digging + sale chute), not
  only grains in free fall.
- Slow processes inside resting sand (fungus, heat, ants) run as a low-rate random-tick
  pass that wakes a chunk only when a cell actually moves; otherwise sleeping is defeated.
- Storage machines (silos, hoppers, moulds) hold COUNTS, not cells; grains become numbers
  on entry and cells again on pour, so the sim only holds sand in transit or on piles.
  Draw the interior as a static fill texture to its level.
- Spike bar template: >= 50k moving grains, work p95 <= 16.7 ms, 60 s, Chrome AND Firefox,
  in-page counter. Fail -> WASM; fail again -> halve grid.
- Godot web (Compatibility renderer, WebGL2) has no compute shaders; per-pixel GDScript
  loops are too slow. Use web tech for these games.

## Rigid sprite bodies coupled to sand (measured PASS, Rapier 2D chosen)
- Engines: Rapier 2D (`@dimforge/rapier2d-compat`, WASM, `await RAPIER.init()`) and
  planck.js both pass with 50 bodies: work p95 3.5/6 ms (Rapier Chrome/Firefox) vs
  3.9/7 ms (planck, Firefox spike to 13). Rapier wins on Firefox tail.
- Coupling per frame (Noita pattern): erase awake bodies' pixels from the grid -> physics
  step -> stamp back by inverse-rotating each grid cell into sprite space (no holes);
  sand inside a stamped cell is displaced to the nearest empty cell above (count lost
  grains, bar <= 0.1%). Sleeping bodies keep their stamp.
- Ground = static polyline of the sand surface (sample every 4 cells, lift 1 cell),
  rebuilt only when samples change; wake sleeping bodies whose ground dropped.
- Colliders: use an 8-direction support polygon (k-DOP octagon) of the remaining opaque
  pixel corners, not the sprite bbox: bboxes include transparent margins, so sprites float
  on each other and rotated boxes jam in hoppers. Rebuild every ~16 pixels lost.
- Grinding: peel body pixels inside the teeth zone into grains (cap per frame), kill the
  body below ~24 pixels and convert the remnant to grains. Add feed rollers (minimum
  downward velocity inside the hopper) or bodies wedge above the teeth.
- Mass from material densities; claw = velocity-driven body (or joint) with lift + drop.
- Burial verified: sand accumulating over resting bodies displaces cleanly; grid-walker
  agents (workers) walking the pile need their own sand-above counter for stuck/crushed
  states (the physics bodies do not carry that logic).
- Ship Rapier only with the .wasm as a separate file; the compat build inlines base64
  and a dual-engine bundle hit 3.5 MB.
- Coupling pitfalls:
  - Imposed velocities (claw/crane dragging a body at 2.5+ cells/tick) tunnel bodies
    through thin static walls and turn into penetration explosions (100-280 cells/s
    ejections). Fixes: walls >= 3 cells, side walls at the world edges (easy to forget),
    clamp drag speed (~110 cells/s), and a stuck-release (if the body moves < 0.4 cells
    for 45 ticks while far from the target, let go) instead of squeezing forever.
  - Drag paths must not cross wall corners: use a 3-phase crane (lift straight up,
    move across above the wall, lower). Two-phase diagonal drags wedge on corners.
  - Bodies stack into unreadable mush above ~40 on one screen: cap the intake, spread
    spawn x across the full floor, and stagger spawns one body per ~16 ticks — several
    bodies spawned at once into a small area overlap and penetration resolution ejects
    them across the map.
  - rapier2d-compat rotation APIs take a 2D angle (number), not a quaternion; passing
    {w,x,y,z} panics with a bare "unreachable". Its `rotation()` accessor returns that
    same angle.
  - Never touch a rigid-body or collider handle after killing it in the same tick (a
    `wakeUp()` one line below a kill is enough): stale handles panic "unreachable" with no
    useful stack. Guard with the body registry's `has(id)`.
  - A per-tick velocity override must preserve vy, or gravity cancels every tick and
    bodies float down in slow motion.
  - Units: the physics API is m/s. cells/s = value * SCALE; cells/tick = value * SCALE
    * 60. Put the unit in the tuning key name (e.g. `beltSpeedCellsPerSec`) — silent unit
    errors are the most common tuning bug.
  - Grind ON CONTACT, never in a zone box: peel only body pixels within a tooth reach
    (~4 cells) of each gear rim, a few pixels per gear per tick. A box around the
    mechanism reads to the player as the sprite "melting at an arbitrary line". Make the
    gears counter-rotate (tops moving into the nip), give the colliders a radius 1 cell
    LARGER than drawn so the physical nip is narrower than the visual one, and add hopper
    walls beside the pair so husks cannot roll off the outer sides and escape whole.
  - Feeder interlock: hold the belt (vx = 0) while >= ~4 bodies wait above the gears and
    show it on screen ("HOPPER FULL"); otherwise the queue overflows the hopper walls onto
    whatever machine is next door.
  - Belt feel: ~18 cells/s (a 220-cell belt in ~12 s) reads as a conveyor; ~120 cells/s
    reads as sprites being thrown. Tune speed by crossing time, not by the number.
  - Gear-pair layout checks: nip gap 2-12 cells, both gears at the same height, belt end
    over the first gear and above its top, floor >= 20 cells below the gears (closer
    chokes instantly).
  - Conservation: every spawn-into-no-room path needs a fallback (climb the column to the
    surface and drop there), and audit spawned vs all sinks (grid, stores, in-transit,
    sold, lost) every ~30 s in KPI snapshots so leaks localise themselves.

## Palette -> material snapping
- HSV threshold rules can pass numeric bars yet fail visually on pixel art: dark outlines
  and shadows become the dominant material. Use a per-world hand-tuned LUT on the
  quantized palette and give outline pixels their own low-value material ("soot").
- Always render a contact sheet (original | material view) for named sprites and inspect
  it; numbers alone hide this.
- Measure the material histogram of the real input BEFORE fixing a purity/quality curve.
  Outline "soot" was ~40% of every DCSS sprite, so no scoop could reach 50% purity until
  soot was excluded from purity (it burns off and pays 0). Fold minor hues into a family
  (green into flesh) or they dilute every share. A ground mound homogenises: one claw
  scoop leans only ~25-40% on any material, so cleaning must come from a slower second
  stage (workers polishing), and junk scoops need their own bin or the loop stalls.

## CC0 asset licence traps
- Dungeon Crawl Stone Soup: only the OpenGameArt packages are CC0 ("Dungeon Crawl 32x32
  tiles" Oct 2010 + "supplemental"; the zip carries LICENSE.txt = CC0, monsters in
  `dc-mon/`, ~550 usable 32x32 sprites); tiles in current DCSS builds are not all CC0.
  Denzi's 32x32 set is CC-BY-SA: never mix it into a CC0 build.
- Isometric Stone Soup (Screaming Brain Studios): CC0 floors/walls.
- Kenney, Quaternius, KayKit: CC0. Credit as a courtesy anyway.
