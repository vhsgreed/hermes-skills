# Turning the scene into an MP4

Recipe for capturing a deterministic three.js page frame by frame and encoding a
vertical social cut. Verified end to end: 52 s, 1080x1920, 30 fps, ~11 MB, ~3 min of
capture plus ~30 s of encoding.

## 1. The page must expose a pure function of time

```js
function renderAt(T){
  const t = Math.max(0, Math.min(DATA.total, T));
  const prog = Math.min(1, t / DATA.timeline_end);   // 0..1 across the build
  // camera from prog, heights from the bin at t, captions from t, fade from t
  rnd.render(scene, cam);
  return true;
}
window.renderAt = renderAt;
```

Rules that make this capturable:

- Derive camera azimuth/elevation/distance, building heights, caption text and opacity,
  HUD counter and end fade **from `t` alone**. Recompute rather than accumulate.
- Gate the live preview behind a URL flag so the capture page is not also animating:
  `if(!location.search.includes('static')) { /* rAF preview */ }` and load `?static=1`.
- Render with `preserveDrawingBuffer:true` so a screenshot always has pixels.

## 2. Pin the layout to the video's exact size

```css
html,body{margin:0;background:#07080c;overflow:hidden;width:1080px;height:1920px}
#stage{position:absolute;left:0;top:0;width:1080px;height:1920px}
#cap{position:absolute;left:80px;width:920px;top:1480px;text-align:center}  /* not bottom: */
#fade{position:absolute;left:0;top:0;width:1080px;height:1920px}
```

`inset:0` on an absolutely positioned overlay resolves against the **viewport**, not
`body`'s declared height. With a window shorter than the page the caption lands in the
middle of the frame and `getBoundingClientRect()` reports the small height, which looks
like a CSS bug and is not one.

## 3. Capture loop (Python via the browser tool, one CDP call per frame)

```python
import base64, os, time
OUT = ".../out/frames"; FPS = 30
CLIP = {"x":0, "y":0, "width":1080, "height":1920, "scale":1}

goto_url("http://127.0.0.1:8899/city.html?static=1")
wait_for_load(); time.sleep(2.5)          # let textures build before the first frame

t0 = time.time()
for i in range(START, STOP):              # 500-800 frames per call
    js(f"renderAt({i/FPS:.4f})")
    r = cdp("Page.captureScreenshot", format="jpeg", quality=85,
            captureBeyondViewport=True, clip=CLIP)
    open(f"{OUT}/f_{i:05d}.jpg", "wb").write(base64.b64decode(r["data"]))
print("frames", STOP-START, "in", round(time.time()-t0, 1), "s")
```

- ~0.10 s per frame; 1,560 frames is three calls of ~80 s each.
- JPEG q82-85 keeps a 1,560-frame sequence near 100 MB on disk.
- `Page.captureScreenshot` retries worth knowing: a 60 s timeout on the first attempt
  after a reload usually means the tab was recreated, not that the page hung — check the
  tab is the expected one and reuse it rather than opening a new target.

## 4. Verify before encoding

```python
from PIL import Image; import os, collections
sizes = collections.Counter(Image.open(os.path.join(d, f)).size for f in sorted(os.listdir(d)))
assert len(sizes) == 1 and list(sizes)[0] == (1080, 1920), sizes
assert len(os.listdir(d)) == EXPECTED_FRAMES
```

A single frame at a different size makes libx264 refuse to open the encoder with a
message about width/height, which points at the encoder instead of the frames.

## 5. Encode and inspect

```bash
ffmpeg -y -framerate 30 -i frames/f_%05d.jpg \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p \
  -movflags +faststart out.mp4

ffprobe -v error -show_entries format=duration,size:stream=width,height,r_frame_rate \
  -of default=noprint_wrappers=1 out.mp4

# contact sheet: six stills across the cut, one image to review
ffmpeg -y -i out.mp4 -vf \
  "select='eq(n\,45)+eq(n\,280)+eq(n\,560)+eq(n\,860)+eq(n\,1180)+eq(n\,1440)',scale=400:711,tile=6x1" \
  -frames:v 1 contact.png
```

Read the contact sheet with your own vision before delivering; composition defects are
invisible in the live page and obvious in six stills side by side.

## 6. Compatibility cut when the target machine struggles

If playback stutters, tears or blanks the screen on the machine that will actually watch
it, ship a minimum-compatibility sibling before touching the render:

```bash
ffmpeg -y -i out.mp4 -vf "scale=720:1280" \
  -c:v libx264 -profile:v baseline -level 3.1 -preset faster \
  -crf 23 -maxrate 2000k -bufsize 4000k -pix_fmt yuv420p -movflags +faststart out-720p.mp4
```

~3 MB for a 52 s cut. Constrained Baseline is the most widely decodable H.264 profile there
is. It doubles as a diagnostic: if the light file also fails, the file was never the problem
and the fault is above it (player, compositor, display driver) — hand off to
`linux-crash-diagnosis` instead of re-encoding harder. State which hypothesis it rules out
when you deliver it, or the user reads it as a downgrade.

## 7. Numbers that worked

| Thing | Value |
|---|---|
| canvas | 1080 x 1920, `setPixelRatio(1)` |
| fps / duration | 30 / 52 s (48 s of build + ~4 s fade) |
| capture | ~0.10 s/frame, 3 chunks of ~520-780 |
| frames | 1,560 JPEGs q85, ~100 MB |
| encode | libx264 slow, crf 19, yuv420p, faststart → ~11 MB |
| caption block | 920 px wide, 40 px type, `top:1480px`, fade 0.7 s in / 0.5 s out |
| districts | packed 2 columns, bounds centred on the origin before fitting |
| fog | far plane set well beyond the fitted camera distance |
