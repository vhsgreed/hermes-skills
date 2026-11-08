# Playwright Python recipes

Copyable probes and helpers for the sync-API contract. See SKILL.md for
when each applies.

## Re-entrancy probe (prove a binding callback is safe before you build on it)

```python
# A binding callback that calls back into the driver DEADLOCKS the sync API.
# Run this once against the library version you ship; the outcome is the
# contract your host code must obey.
def probe():
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        def cb(source, name, payload=None):
            page.evaluate("() => 1")  # re-entrant call
        page.expose_binding("skibidiEvent", cb)
        page.set_content("<div>x</div>")
        page.evaluate("() => window.skibidiEvent('ping', {})")  # hangs if unsafe
```

Host-side fix shape: queue closures while dispatching an event, flush them
after the pumping `evaluate` returns, and defer `close()` the same way.

## Pump-aware wait helper

```python
def wait_until(page, pred, timeout=3.0, interval=0.05):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if pred():
            return True
        page.wait_for_timeout(int(interval * 1000))  # pumps the connection
    return pred()
```

## Media fixture page (no binary media shipped)

```html
<script>
  Object.defineProperty(HTMLMediaElement.prototype, "duration", { get() { return 8.0; } });
</script>
<video></video>  <!-- repeat in scrollable 90vh sections -->
```

Serve statically, load the script under test with
`page.add_init_script(path=...)` and collect events through
`page.expose_binding`.

## Exact window geometry (works on Wayland)

```python
cdp = context.new_cdp_session(page)
win = cdp.send("Browser.getWindowForTarget")
cdp.send("Browser.setWindowBounds", {"windowId": win["windowId"], "bounds": {
    "left": x, "top": y, "width": w, "height": h, "windowState": "normal"}})
```

Launch with `viewport=None` so the driver's default viewport does not append
its own `--window-size`. For unmuted autoplay add
`--autoplay-policy=no-user-gesture-required` to the launch args and set
`video.muted = false` from the injected script.

## Kill and verify

```python
# capture at launch (the profile dir string is unique to the browser command line)
pid = int(subprocess.run(["pgrep", "-f", f"--user-data-dir={prof}"],
                         capture_output=True, text=True).stdout.split()[0])
# after close-with-deadline times out:
os.kill(pid, signal.SIGKILL)
# verify after the run (pattern must not self-match the shell):
#   pgrep -f "skibidi-wait/profil[e]"
```
