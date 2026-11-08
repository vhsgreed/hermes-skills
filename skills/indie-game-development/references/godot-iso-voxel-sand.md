# Godot isometric voxel-column (heightfield) sand

Recipe for an iso 2.5D world where sand is stacks of cubes per ground column, run in a
Godot web export. Worked example: the author's isometric sand game and its spike (not published).

## Data model
- Flat baseplate (height 0); all geometry is sand. height[c] per column (uint8), colour
  class per voxel stored per 32x32-column chunk, allocated only when sand first lands there
  (dense 512x512x128 = 33 MB; sparse = the dump area only).
- Limitation to state up front: a heightfield has no overhangs, tunnels or caves; "mining"
  into a pile is a crater/shaft from the top or a machine that counts what it removes.

## Sand rules
- 8 neighbours. With cube voxels (height = width): max stable step 1 orthogonal, 1 diagonal
  plus 1 extra on a FIXED 41% of columns (chosen at setup) -> rounded-square cone ~35-45 deg.
  A per-check random tolerance makes stable columns re-slide forever (cost explodes).
- Pour by DESCENT: walk each new grain downhill to its rest column at pour time; keep the
  angle-of-repose relax() (active set of disturbed columns, max moves per column per tick)
  only for bites/avalanches. ~2.3x cheaper than relax-only on the full tick. Batching (move
  half the excess per check) gained nothing.
- Descent places the grain instantly: under a no-teleport rule, animate the grain along its
  recorded descent path (visual only) and grow the column on arrival.
- Fewer slide outcomes (3-4 directions) do not save compute: cost is re-checks while
  settling, not directions; they also give lopsided/diamond piles.
- Conservation check every second: sum(height) == poured - removed, exactly.

## Performance (Godot 4.7.2 web, single-thread, Chrome, 2,000 grains/s + 4 bites/s)
| full sand tick p95 | GDScript relax-only | GDScript descent | C++ GDExtension descent |
|---|---|---|---|
| web | 10.1 ms | 4.3-4.5 ms | 0.2 ms |
Render (one MultiMesh box per column scaled to height, colour = top voxel, only dirty
columns/chunks updated) stays < 0.5 ms. Generating a 512x512 map + 60k-voxel pour: ~50 ms.
- Time the WHOLE subsystem tick (pour + bite + relax + readback). An optimisation that moves
  work into another function hides it from a function-level timer.

## C++ GDExtension for web
- emsdk at Godot's own web CI version (EM_VERSION in the engine tag's
  `.github/workflows/web_builds.yml`; 4.0.11 for 4.7.2) in ~/src/emsdk; godot-cpp at the
  newest branch <= engine version in ~/src/godot-cpp; scons in a venv (~/src/scons-venv).
- Build: `scons platform=web target=template_release threads=no`, plus linux
  template_release and template_debug for headless native tests (~3 min first build each).
- .gdextension: `web.release.wasm32` AND `web.debug.wasm32` ->
  `res://bin/libX.web.template_release.wasm32.nothreads.wasm`; `compatibility_minimum` =
  godot-cpp branch.
- Export preset: `variant/extensions_support=true`, `variant/thread_support=false`,
  `exclude_filter="ext/*,tools/*,out/*"`. Web build ~12 MB gz (index.side.wasm ~10.6).
- API shape: coarse calls only (setup, pour(n), relax(), take_dirty_chunks(),
  chunk_buffer(ci) returning a packed MultiMesh buffer: 12 transform floats + 4 colour
  floats per instance, assign to `multimesh.buffer`). Never per-cell calls across the boundary.
- Only the sand kernel goes to C++; everything else stays GDScript unless it fails its own bar.

## Single-thread vs threads vs standalone
- Web threads need COOP/COEP cross-origin isolation (itch.io has a checkbox; breaks some
  embeds/browsers). Single-thread works everywhere: default for a stranger-play probe.
- Standalone/desktop export is near-free from the same project (Steam later) but adds a
  download step to stranger play and makes session analytics harder.

## Camera, light, shadows (fixed iso)
- Orthographic Camera3D, `look_at_from_position(target + (1,1,1).normalized()*D, target)`;
  pan in ground-plane axes (divide the vertical-screen component by sin(35.264 deg)); zoom by
  `cam.size` steps.
- "Only the mound casts": ground `cast_shadow = OFF`; DirectionalLight3D, shadow on,
  `SHADOW_ORTHOGONAL` (one map suffices with a fixed camera). 60 fps over a compressed day.
- Sun AND moon on ONE horizontal arc from screen-right, through BEHIND the subject (away from
  the camera) at noon, to screen-left, so shadows always fall on the visible side and never
  flip. Fade light energy to 0 near each horizon so the sun<->moon swap is invisible. Moon
  casts too (energy ~0.5, ambient ~0.16, blue tint). Peak elevation sets the noon shadow
  length: with ~35-45 deg piles, a ~38 deg sun gives a short noon shadow.
- Test continuity numerically: sample the shadow direction over a whole day, report the max
  angle step between lit samples (should be < 1 deg), then a 4-panel screenshot grid
  (morning/noon/dusk/midnight) checked with vision.

## Ground and map gen (cheap, RimWorld-style)
- Ground = one plane + shader mixing two FastNoiseLite images (broad fbm tone, fine grain)
  between dirt and grass; water = an L8 mask texture (one noise-warped river edge-to-edge or
  one fbm-threshold lake) with a darker shore band sampled in the shader; yard = rect uniform.
- Automated map check per seed: yard never touches water; BFS over dry land from the yard
  reaches a map edge. Run 10 seeds via `?test=seeds`.

## Test harness (Godot web + Playwright)
- Playwright does not reliably see Godot's web console output: write results with
  `JavaScriptBridge.eval("window.__x = " + JSON.stringify(d))` and poll `window.__x`.
- Read URL params via `JavaScriptBridge.eval("new URLSearchParams(location.search).get('k')")`
  on web and `OS.get_cmdline_user_args()` (`-- --k=v`) natively; the same `?test=` modes run
  in both.
- Headless Chrome with SwiftShader is too slow for a Godot web build; use headless Chrome
  with `--enable-gpu --use-angle=vulkan --enable-features=Vulkan --ignore-gpu-blocklist`.
- Serve export/web with `python3 -m http.server` as a persisted background process.

## Multi-scale matter core (billions of cubes in a browser tab)
- Per-cube colour storage dies at scale (1e9 cubes = 1 GB). Store counts instead: 15 class
  counts (int32) per megacell-layer (16x16 columns x 32 layers = 8192 cubes) + uint16 heights.
  1,000,590,609 cubes measured: build 116 ms, ~60 MB (counts 43 MB + heights 11.5 MB + caches).
- The arrangement (which cube is which class) is a PURE FUNCTION of (counts, heights, seed):
  enumerate the layer's valid slots canonically (each column's bottom k cubes, k from heights,
  prefix-summed), scatter the exact class multiset over j = 0..T-1 by a bijective stride
  permutation (j*S+O) mod T, class at rank = cumulative-count lookup. Exact per class AND per
  column with no fixup. A tiny per-layer cache {k[256], prefix[256], T, S, O} gives O(1) cold
  lookups for rendering without materialising anything.
- Hot/cold: cold regions render from the pure function. An EDIT freezes the layer into a byte
  array FIRST (so untouched cubes keep their look after counts change), decrements counts in
  the same breath as the array cell, and the freeze is dropped on dehydrate — which is only
  allowed out of view, since regeneration from new counts rearranges the layer.
- Bites freeze only the 1-4 layers a touched column crosses. Bulk hydrate is the worst case:
  64x64-column full-depth zone p95 8.0 ms web (against an 8 ms bar), dehydrate 0.3 ms. Precompute
  the per-layer class band (T fills) then place with O(1) per-slot lookups; a cumulative-count
  lookup per slot (O(15)) doubled the cost.
- Render in 2 LODs, both one box per grid unit: per-column boxes in a 256x256-column window
  around the camera target (colour = top class), and one box per megacell outside it (count-
  weighted average colour, centre height), hidden where the window covers. Evict caches for
  megacells outside the window (long sessions otherwise leak megabytes per camera tour).
- Rebuilding the whole window when the camera moves costs ~10.5 ms in one frame (4.2 MB buffer
  copy): fine for a spike, a stutter risk to fix incrementally in a game build.
- The conservation guard must cover PER-CLASS totals across cold counts + hot arrays + removed:
  totals alone matched while class counts drifted hundreds of grains in a buggy generator.
