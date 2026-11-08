---
name: interactive-data-visualization
description: "Build animated data visualizations as one HTML file."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [visualization, threejs, webgl, canvas, timeline, treemap, dataviz, prototype]
    related_skills: [claude-design, architecture-diagram, p5js, hermes-agent]
---

# Interactive data visualization

## When to Use

- "Help me see what happened over time", "an overview at a glance", a timelapse, an
  activity map, an animated tree/treemap, a spatial/3D scene over the user's own data.
- The user finds the shape hard to describe in words — stop asking for more prose and
  show a live probe on their real data instead.
- A chart has to animate, scrub, or drill in.

Deliverable: **one self-contained HTML artifact** that plays, scrubs and drills in.
Not static page design (`claude-design`) and not SVG infra diagrams
(`architecture-diagram`).

This skill is about encoding data spatially and getting the render inspectable. Design
taste and page composition are `claude-design`; static infra diagrams are
`architecture-diagram`.

## Non-negotiables

1. **Prototype on the user's real data before asking for design approval.** Pull the
   real rows first, cap to ~100-300 marks, and render those. Placeholder numbers or
   invented paths produce a mockup nobody can judge; real ones let the user point at
   a specific block and say "that's wrong".
2. **Self-contained output.** Inline both the rendering library and the dataset into
   one HTML file. No CDN at runtime — the artifact must open offline.
3. **Look at it yourself before showing it.** Load in a browser tool, screenshot at
   start / mid / end of playback, inspect the image, fix what you see. Every defect
   found this way is cheaper than the user finding it.
4. **Do not downgrade a requested 3D/WebGL treatment before testing it.** Vendoring
   three.js and animating boxes is a couple hundred lines; the costly parts are
   layout and labels, not the renderer. "Animation is hard" is not a reason to
   deliver fake-3D, and the user will rightly push back.
5. **Two encodings per mark, maximum.** Size (magnitude), opacity (recency), colour
   (category). A fourth dimension belongs in a second view, not in another channel.
6. **Fading must have a floor.** Unfloored exponential decay empties the scene for any
   window longer than the half-life. Keep cold marks at ~0.45 opacity and desaturate
   by at most ~0.35 toward grey, so structure survives playback.
7. **Animate the map, not only the marks.** Recompute the layout per time slice, lerp
   node positions toward their targets, and let the camera follow the live bounding box
   while playing. A camera fitted once at boot goes stale the moment nodes are pruned or
   added, and the scene drifts out of frame.

## Procedure

1. **Extract typed events** from the data source: `{ts, kind, path|bucket, magnitude}`.
   Normalise paths into buckets (2-3 segments under the root) — a week of activity is
   routinely 100+ directories, which is unreadable ungrouped.
2. **Choose the spatial mapping** (see "Layouts"). Tree for hierarchy, shelves for
   density, treemap for honest ranking.
3. **Set time geometry**: half-life ≈ window/5, playback duration ~30 s for 24-36 h of
   activity, auto-binning (day → 30 min → 1 min) as the window narrows.
4. **Generate the artifact with a build script**, not by hand: a Python generator that
   string-replaces `/*__LIB__*/` and `/*__DATA__*/` markers in a template. The output is
   800 KB+ and must never be edited in place.
5. **Labels last, in screen space** (see pitfalls). Then connectors, then colour.
6. **Verify**: screenshot at 5 %, 45 % and 100 % playhead plus one frame with a mark
   forced to full opacity. The last one tells you whether geometry or the fade floor is
   the problem.
7. **Iterate on the user's data** until they call the feel right. Write a spec only when
   the probe is going to become a product.

## Layouts

| Mapping | Reads as | Fails at |
|---|---|---|
| Rooted tree, root at left, depth to the right | hierarchy, "where is depth" | wide repos: sideways scroll, diagonal sprawl |
| Shelves (top-level dir = shelf, width ∝ activity) | density, no scroll | hides depth below two levels |
| Treemap (area ∝ activity) | honest ranking at a glance | loses parent/child reading |

Use a **tidy tree**: own height = `rows * pitch + pad`; subtree height =
`max(own, sum(child subtrees) + gap * (n-1))`; place each parent at its band centre.
Naive sibling stacking produces a diagonal scatter that no amount of styling fixes.

## Tree over time (pruning and re-flow)

A timelapse of a filesystem should show the working set reorganising, not a fixed map
with fading marks:

1. **Render the whole working set**, not a top-N slice: every directory with activity in
   the window, depth capped at ~3 levels so a deep repo cannot sprawl.
2. **Order siblings by trailing-window activity** (e.g. the last 24 h before the
   playhead), not by whole-window totals, so the hot shelf moves to the front as the
   work moves.
3. **Prune on a stated threshold** — "untouched for 24 h of playback time" is a good
   default. Pruned nodes stop taking layout slots and fade to zero opacity; their
   subtrees close up.
4. **Recompute the layout every ~15 min of source time** (a cheap tidy-tree pass over
   live nodes), then spring-lerp each node's current position toward its target every
   frame. Jumps become reorganisation; without the lerp the map snaps and looks broken.
5. **Park pruned nodes on their parent's position** rather than leaving them at stale
   coordinates, so they collapse instead of floating.
6. Expect sparse stretches: an honest day has quiet hours and the map will shrink to a
   handful of nodes. That is data, not a bug — say so before the user reports it as one.

## Delivering a video (social cut)

When the artifact is for Reddit / X / Bluesky rather than a local page, the deliverable is
an **MP4**, not HTML: 1080x1920, 30 fps, 45-60 s, burned-in captions, silent-safe (most
feeds autoplay muted, so captions carry the whole story).

1. **Make the page deterministic.** Expose `window.renderAt(t)` that derives every bit of
   state from `t` alone — camera, heights, captions, HUD, end fade. No `rAF` clock, no
   physics, no randomness. A real-time animation cannot be captured frame-accurately, and
   a half-second drift shows up as a stutter in the final cut.
2. **Capture one frame per CDP call** by setting the clock and screenshotting, then encode
   with ffmpeg. Recipe, clip settings and the encode line: `references/video-export.md`.
3. **Capture with an explicit `clip` region**, never by resizing the viewport (see
   pitfalls). This is the single defect that wastes the most time in this pipeline: the
   frames look plausible, and the encode or the composition is wrong.
4. **Chunk the loop** (500-800 frames per tool call) and write JPEGs to disk as you go, so
   a timeout costs one chunk instead of the whole render. Clear the directory first; a
   stale frame from the previous pass re-encodes silently.
5. **Write the copy to the audience, not the schema.** Translate tool calls into human
   verbs (edited / checked it still works / looked something up / wrote down a rule /
   handed work to a helper) and drop paths, tool names, token counts and currency. A lay
   viewer understands "34 days, 500 conversations"; they cannot decode `patch` or a
   directory tree. Karl's register is flat and declarative — numbers escalating, then one
   cold short sentence; he rejects pitch-deck closers and neat final metaphors as "AI
   first draft", so prefer silence or a hard number over a clever line.
6. **Assert nothing the data cannot prove.** Every caption number must come from a count
   you actually ran, and every "is now live / is published" claim must be checked (fetch
   the URL, query the registry) before it enters the frame. A cheap model may rephrase a
   fact sheet; it may never infer an achievement. Also distrust derived aggregates in the
   source: a summed cost field that comes out negative, or a per-session counter that
   disagrees with the row count, means count from the raw events and leave money out.
7. **Re-cut after the first viewing.** Framing defects (city off-centre, dead top third,
   labels under the caption) only become obvious when you watch the encoded file, not the
   live page — extract stills at 4-6 points and look at them as a contact sheet. But a
   contact-sheet tile can invent an artifact: a black band, a hard edge or a duplicated
   strip that is not in the frame. Before reporting a rendering bug, extract that single
   frame at full size and look again.
8. **Ship a compatibility fallback next to the master.** Encode a second file with
   `-vf scale=720:1280 -profile:v baseline -level 3.1 -crf 23` (~3 MB for a minute). It
   is the most playable H.264 there is, so when the user reports stutter, blanking or
   "my machine can't play it", handing them the fallback clears the file as a suspect in
   one step instead of opening a debugging session about their hardware. Do this before
   offering any diagnosis of their machine.

## Pitfalls

- **Canvas-texture sprites for labels turn to mush.** A chip that is legible on its own
  canvas shrinks to a few pixels once it is a world-space sprite in a zoomed-out scene.
  Use DOM elements positioned by projecting the anchor point each frame
  (`vec.project(cam)` → NDC → pixels, `translate(-50%,-50%)`). Fixed 11-12 px text, real
  background, readable at any zoom. This was the single most expensive mistake.
- **Connectors: floor ribbons, one trunk per parent.** `Line` primitives vanish once the
  camera pulls back, so use thin boxes; and route each parent's children through a single
  vertical trunk inside the depth gap (parent stub → trunk spanning the children's z range
  → per-child stubs) instead of one elbow per edge. Per-edge elbows from the same parent
  stack on top of each other and read as a diagonal smear wherever siblings sit close.
- **Two node models diverge and the scene renders empty.** The layout must write to the
  same objects the frame loop reads: build `NODES = payload.map(n => runtime[n.id])` once
  and use it for layout, pruning, labels and camera. Writing targets onto the payload
  array leaves every mesh at the origin while the camera and fps look healthy — it reads
  as a renderer bug and costs an hour.
- **Patches sized `rows * cols` leave big empty tiles** when a group holds few marks.
  Size the patch to hug its contents, or the view is mostly empty floor.
- **A cube whose edge is `cbrt(volume)` outgrows its grid pitch.** Cap the edge below the
  pitch or neighbouring cubes fuse into one blob and magnitude stops reading.
- **Cold state must still be visible.** Check the first frame of playback, not the last:
  at a 36 h window with a 6 h half-life everything sits at the floor and the map looks
  broken unless the floor is raised.
- **Path-less events need session-vote attribution, not the cwd.** Shell commands, code
  runs and model calls carry no path, and `cwd` is `$HOME` for most sessions — defaulting
  to it dumps the majority of activity into one meaningless bucket. Instead: per session,
  count the projects its path-bearing calls touch; if one project holds ≥50 % of them,
  attribute the session's path-less calls to it; otherwise mark them `roaming`. Then
  exclude `roaming` from any spatial "where" view — a giant grey tower of unattributed
  work dominates the frame and reads as a rendering bug to everyone who sees it.
  Keep the roaming count for totals so headline numbers stay true.
- **Nested/subagent sessions inflate the parent.** Tag or dim them; never merge silently.
- **One assistant turn can carry several tool calls.** Count parsed call array elements,
  never rows.
- **A moving focus marker needs choreography, not teleporting.** Spring-damp the marker
  toward its target (stiffness ~46, damping ~11 at 60 fps), keep a short trail of recent
  positions, and park a separate pulsing reticle on the *next* event so the viewer sees
  where it is going as well as where it has been. Clear the trail on seek, or scrubbing
  draws a fake line across the map.
- **DOM label chips paint over the 3D marker.** Screen-space chips sit above the canvas,
  so a marker hovering at patch height disappears behind one. Raise it ~3 units above the
  patch and keep chips on a `pointer-events:none` layer.
- **Screen-space chips collide in dense clusters.** After projecting, run 3-4 sorted
  passes that push a chip down by its own height (+~8 px) when it overlaps the one above
  (compare with `el.offsetWidth`); a single pass leaves two-deep stacks in every fan.

- **`setDeviceMetricsOverride` does not survive the next tool call or new tab.** Frames
  silently come back at the browser window's size (e.g. 1280x577) while the page lays out
  at 1080x1920, so every capture is a cropped corner and the encode fails with a generic
  libx264 "incorrect parameters such as width or height". Pass an explicit
  `clip={x,y,width,height,scale}` with `captureBeyondViewport=True` on every screenshot
  instead of depending on the viewport, and assert the first frame's size before looping.
- **`position:absolute; inset:0` overlays anchor to the viewport, not the page height.**
  When the page is taller than the window, anchors resolve to the window and captions land
  mid-frame. Pin the stage to explicit pixels (`width:1080px;height:1920px`) and give every
  overlay layer its own width/height rather than `inset`.
- **A portrait frame has a much narrower horizontal field of view.** Compute the fit
  distance from the horizontal FOV — `hfov = 2*atan(tan(vfov/2)*aspect)` — not from the
  vertical one; at 1080x1920 the horizontal span is ~0.56x the vertical, and a distance
  that fits the height crops the city. Then raise the fog's far plane above that distance:
  a scene that vanishes into fog reads exactly like a black frame.
- **Pack the layout for the frame you are rendering.** Districts strung along one row need
  an enormous camera distance in portrait; pack them into a grid (2 columns) so the
  footprint is squarish, then centre the packed bounds on the origin before fitting.

## Companion mockup delivery

When iterating inside the `superpowers:brainstorming` visual companion, write the
**full document** into its `content/` directory (files starting `<!DOCTYPE` are served
as-is) and give each iteration a new filename. Verify it is served with
`curl -c jar '<keyed url>' -o /dev/null && curl -b jar <base url> | grep <marker>`
before telling the user to look.

The companion server exits after its idle timeout and starts a **new session directory**
on restart: restart it with the same `--project-dir` so the port and key are reused and
the user's open tab reconnects, then copy the current screen into the *new* `content/`
directory — an empty content dir serves a blank framed page that looks like a broken
build. For frame capture do not use the companion at all: serve the built file from a
plain `python3 -m http.server` and load it with `?static=1`, so a server restart cannot
decide a render has failed.

## References

- `references/hermes-activity-extraction.md` — SQL and tool→kind mapping for pulling
  tool calls, file paths, exact `patch` churn and session cwd out of `state.db`.
- `references/threejs-single-file.md` — vendoring three.js, DOM-label projection and
  de-overlap, decay and playback code, per-parent trunk connectors, spring marker with
  trail and destination, layout-over-time and camera follow, numbers that worked.
- `references/video-export.md` — deterministic `renderAt(t)`, CDP clip capture loop,
  frame-size verification, ffmpeg encode, and the numbers that worked for a 52 s cut.
- `templates/three-scene.html` — scene skeleton with `/*__LIB__*/` and `/*__DATA__*/`
  markers, screen-space labels, tidy-tree placement hooks, playhead transport.
