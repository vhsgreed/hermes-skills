# three.js in a single HTML file

Concrete recipe for an animated 3D data scene that opens offline from one file.

## Vendor the library, inline it

```bash
curl -sL -o /tmp/three.min.js https://unpkg.com/three@0.160.0/build/three.min.js
head -c 300 /tmp/three.min.js     # UMD build; warns it is deprecated past r150 but ships
```

- ~654 KB, sets a global `THREE`. Check the tail contains `t.XXX=` exports.
- Do **not** use the ES-module build: `import` from `file://` needs a server, and a
  single copied HTML file should just work.
- Inline it at build time. Generate the artifact from a Python script that does
  `TEMPLATE.replace("/*__THREE__*/", lib).replace("/*__DATA__*/", json.dumps(payload))`.
  The 800 KB result is never hand-edited; you edit the generator and re-run it.

## Screen-space labels, not sprites

```js
const _v = new THREE.Vector3();
function project(x, y, z) {
  const r = renderer.domElement.getBoundingClientRect();
  _v.set(x, y, z).project(camera);
  return [(_v.x * .5 + .5) * r.width, (-_v.y * .5 + .5) * r.height, _v.z];
}
// per frame
const [sx, sy, sz] = project(node.x, 1.05, node.z);
node.el.style.transform = `translate(-50%,-50%) translate(${sx}px,${sy}px)`;
node.el.style.opacity = sz > 1 ? 0 : (0.42 + 0.58 * Math.exp(-dt / HALF)).toFixed(2);
```

Chip CSS that reads over any dark scene:

```css
.nlabel{position:absolute;background:rgba(13,15,21,.94);border:1px solid rgba(132,146,190,.5);
  border-radius:6px;padding:2px 7px 3px;font-size:11.5px;font-weight:600;color:#f1f3fa;
  white-space:nowrap;box-shadow:0 2px 10px rgba(0,0,0,.55)}
.nlabel small{color:#868ba3;margin-left:6px;font-weight:500;font-size:10.5px}
```

Put the chip above the group, put the count in `<small>`, and set
`pointer-events:none` on the label layer.

## Magnitude and recency

```js
// cube edge: volume encoding, capped below the grid pitch
const e = Math.min(pitch * 0.97, .55 + .46 * Math.cbrt(lines));
// recency: floored exponential, so cold marks stay visible
const a = 0.46 + 0.54 * Math.exp(-dt / HALF);      // HALF ≈ window / 5
const stale = Math.min(1, 1 - Math.exp(-dt / HALF));
mat.color.copy(baseCol).lerp(GREY, stale * 0.35);
mat.opacity = a;
```

Give materials an `emissive` equal to the base colour times ~0.22 so cold cubes never
render black against a dark patch.

## Tidy tree placement (Python side)

```python
n["own"] = max(1.15, rows * 1.3 + 0.5)
def height(pid):                     # subtree band
    ch = kids.get(pid, [])
    n["sub"] = n["own"] if not ch else max(n["own"], sum(height(c) for c in ch) + GAP * (len(ch) - 1))
    return n["sub"]
def assign(pid, z0):                 # x by depth, z banded
    z = z0
    for c in kids[pid]:
        assign(c, z); z += nodes[c]["sub"] + GAP
    n["zc"] = z0 + n["sub"] / 2
    pos[pid] = (n["depth"] * X_STEP, n["zc"])
```

`GAP ≈ 2.2` and `X_STEP ≈ 8.2` at pitch 1.4 keep chips from colliding on a ~40-unit tree.

## Connectors: one trunk per parent

Build the ribbons **per parent**, not per edge. Children of one parent share a vertical
trunk in the depth gap; each child taps it at its own z. Sibling subtrees occupy disjoint
z bands, so two parents' trunks can never collide.

```js
// build once: parent -> {stub, trunk, kids:[{id, rib}]}
const bus = busByParent[n.parent];
bus.kids.push({id: n.id, rib: mkRib(ribMat)});

function placeRib(m, x1, z1, x2, z2){            // axis-aligned box between two points
  const dx = x2-x1, dz = z2-z1, len = Math.hypot(dx, dz);
  if(len < 1e-4){ m.visible = false; return; }
  m.visible = true;
  m.position.x = (x1+x2)/2; m.position.z = (z1+z2)/2;
  m.scale.x = Math.max(0.001, len); m.rotation.y = -Math.atan2(dz, dx);
}

// per frame
const px = p.cur.x + p.hw + 0.22, pz = p.cur.z;
const bx = px + (kids[0].n.cur.x - kids[0].n.hw - 0.22 - px) * 0.45;   // trunk column
const zmin = Math.min(...kids.map(o=>o.n.cur.z));
const zmax = Math.max(...kids.map(o=>o.n.cur.z));
placeRib(b.stub,  px, pz, bx, pz);                                     // parent tap
placeRib(b.trunk, bx, zmin, bx, zmax);                                 // the trunk
kids.forEach(({k,n}) => placeRib(k.rib, bx, n.cur.z, n.cur.x - n.hw - 0.22, n.cur.z));
```

Ribbon colour ~`0x5b688c`, thickness `0.09 x 0.17`, `y = 0.035`. One elbow per edge
instead stacks N near-identical trunks from the same parent and renders as a diagonal
smear wherever siblings are close.

## Layout over time: prune and re-flow

```js
// hourly activity per node, descendants rolled up into ancestors
const HOUR = 3600, NB = Math.ceil(span/HOUR) + 1;
const binOf = t => Math.max(0, Math.min(NB-1, Math.floor((t - start)/HOUR)));

function computeTargets(now){
  const b0 = binOf(now - DAY), b1 = binOf(now);          // ordering window
  node.weight = sum(hourly[node.id][b0..b1]);
  node.live   = lastTouchedIn(b0, b1) > now - KEEP;      // KEEP = 24h prune threshold
  // sort kids by weight desc, tidy-tree over live nodes, assign target (x, z)
  // pruned nodes: target = parent's target, so they collapse instead of floating
}
```

```js
// per frame: recompute on a coarse clock, smooth every frame
if(Math.floor(now/900) !== lastLayoutBin){ lastLayoutBin = Math.floor(now/900); computeTargets(now); }
node.cur.lerp(node.target, 1 - Math.pow(0.001, dt*3.2));
node.opacity += ((node.live?1:0) - node.opacity) * Math.min(1, dt*3.0);
```

Camera follows the live bounds while playing (skip while the user drags):

```js
if(playing && !drag){
  const k = Math.min(1, dt*1.6);
  cx += (tcx-cx)*k; cz += (tcz-cz)*k; dist += (tdist-dist)*k; place();
}
```

## Marker: spring, trail, destination reticle

```js
const stiff = 46, damp = 11;                       // critically-damped-ish at 60 fps
agentVel.x += ((target.x-agentPos.x)*stiff - agentVel.x*damp) * dt;
agentPos.x += agentVel.x * dt;                     // same for y, z
// trail: push when the marker actually moved, cap the length, reset on seek
if(Math.hypot(agentPos.x-last.x, agentPos.z-last.z) > 0.18){ ghostHist.push(agentPos.clone()); }
if(ghostHist.length > 26) ghostHist.shift();
```

- Trail = `THREE.Line` over `ghostHist` with `setDrawRange(0, n)`; clear it on seek or the
  jump draws a line across the whole map.
- Destination reticle = a second ring parked on the **next** event's cube (binary search
  forward from the playhead), pulsing `1 + 0.16*sin(t/230)`.
- Marker height ≈ `cubeTop + 3.4` so DOM chips cannot cover it.

## Label de-overlap (screen space)

```js
for(let pass=0; pass<4; pass++){
  placed.sort((a,b)=>a._ly - b._ly);
  for(let i=1;i<placed.length;i++){
    const a = placed[i], b = placed[i-1];
    const aw = a.el.offsetWidth||90, bw = b.el.offsetWidth||90;
    if(Math.abs(a._lx-b._lx) < (aw+bw)/2 - 10 && Math.abs(a._ly-b._ly) < 22) a._ly = b._ly + 22;
  }
}
```

One pass is not enough — chips re-collide after being pushed; 3-4 passes settle a dense fan.


## Camera and interaction

- Perspective 38°, elevation ~0.66 rad, azimuth ~-1.02, `dist ≈ max(34, max(w, d*1.25)*0.78)`.
- Frame from the node bounding box, not from node 0 — the root is rarely the centre.
- Hand-roll orbit (drag = azimuth/elevation, wheel = distance); `OrbitControls` is not in
  the UMD build.
- Light: hemisphere ~1.25 + one directional at 1.5 + a rim light. `MeshLambertMaterial` is
  enough; skip shadows.

## Playback

```js
ph = Math.min(span, (performance.now() - t0) / 1000 / DUR * span);
```

Recompute last-touch by walking the event array with a cursor in both directions (seek
forward applies touches, seek backward only moves the index). Log rows, histogram
bars and the marker all read from the same cursor, so the sidebar stays in sync with
the scene.

## Numbers that worked

| Thing | Value |
|---|---|
| window | 36 h of real activity |
| events | ~1,900 tool calls → ~137 file cubes + 28 directory patches |
| playback | 34-40 s |
| half-life | window / 5.5 |
| prune threshold | untouched for 24 h of playback time |
| ordering window | trailing 24 h before the playhead |
| layout recompute | every 900 s of source time |
| position lerp | `1 - 0.001^(dt*3.2)` |
| cube edge | 0.55 + 0.46·∛lines, capped at pitch·0.97 |
| grid pitch | 1.42 |
| depth spacing | X_STEP ≈ 7.4, GAP ≈ 2.0, depth capped at 3 |
| opacity floor | 0.46 (fills), 0.42 (patches) |
| marker spring | stiffness 46, damping 11, trail 26 points |
| render cost | one mesh per cube; ~150 cubes + ~60 ribbons is fine, no instancing needed |
