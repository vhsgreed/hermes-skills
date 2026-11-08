# Level/layout editor for a web sim game

Use when the player-tester wants to arrange the machines himself instead of reporting
coordinates. Built and verified for a TS incremental prototype (TS + esbuild, ~1 h).

## Order
1. Inventory every hard-coded coordinate first: grep the engine, game and overlay files
   for 2-3 digit literals and named layout constants (walls, bins, spawn, paths, worker
   zones, text anchors). Missed literals are what break after a drag.
2. One `layout.ts` module: a typed `Layout`, `DEFAULT_LAYOUT`, a mutable `L` the game
   reads LIVE (no cached copies), `applyLayout(json)` that merges onto the defaults
   (missing keys keep defaults, fixed-count arrays fall back if the count is wrong),
   `loadLayout()` fetching `layout.json?ts` with `cache: 'no-store'`, derived helpers
   (caster intake, gear nip) and `validate(l) -> string[]`.
3. Put line tuning that depends on the layout (belt speed, grind rate, gear spin) in the
   layout's `tune` block and copy it into the game tuning at boot.
4. Replace every literal with `L.*`; type-check (`tsc --noEmit --strict`) to catch the
   leftovers, then grep again for the old constant names.
5. Editor = separate entry (`editor.ts` -> `editor.js`, `editor.html`) importing the SAME
   layout module, so its warnings are exactly what the game checks. Features that
   mattered: drag to move, drag corners / belt ends / gear rim to resize, arrow nudge
   (Shift x10), snap select, undo/redo (JSON snapshots), properties panel with numeric
   inputs, live checks panel, capacity readout per store (footprint rule), add/delete
   free walls and path points, Save (Ctrl+S), Save + Play, Download/Load JSON fallback,
   beforeunload guard. Draw derived things (intake slot, nip gap coloured red/green, tooth
   reach ring, claw reach envelope) so problems are visible before playing.
6. Saving: a tiny `tools/serve.py` (ThreadingHTTPServer on 127.0.0.1) that serves `web/`
   with `Cache-Control: no-store` and accepts `POST /layout.json` (size cap, minimal
   schema check), copying the previous file to `layouts/layout-<timestamp>.json` before
   overwriting. The game logs "layout: layout.json" vs "built-in default" plus each
   validate() warning at boot.
7. Verify with Playwright and real mouse drags: drag an object, provoke a warning, undo,
   Ctrl+S, confirm the file on disk, reload the game and probe the moved wall in the grid.
   Remove the test layout afterwards so the user starts from the default.
8. The world often grows after layouts exist (wider world + camera scroll): keep axis
   coordinates stable so saved layout.json files stay valid, keep fixed safety geometry
   (world bottom/edge walls) outside the layout, and extend only the DEFAULTS to the new
   bounds - never silently rewrite the user's saved coordinates. Fit the editor canvas to
   the window with CSS (`width:100%`); hit-testing through `getBoundingClientRect` already
   scales, so no coordinate rewrite is needed for a fit-to-window editor.
