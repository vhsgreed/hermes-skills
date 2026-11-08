---
name: browser-automation
description: "Use when code must drive a real browser (Playwright, CDP)."
version: 1.0.0
author: Karl Sundström
license: MIT
metadata:
  hermes:
    tags: [browser, playwright, cdp, e2e, automation]
    related_skills: [test-driven-development, systematic-debugging, computer-use]
---

# Browser Automation

Build software whose code drives a real browser: tool wrappers, E2E suites,
watchers, injected page overlays. Playwright (Python) is the default driver.
The rules below are its real contract, not its docs' happy path.

## When to Use

- Building a tool or wrapper whose code opens and drives a browser window.
- E2E-testing web UIs, including scripts injected into third-party pages.
- Automating a site in the user's own logged-in session.

Not for driving the desktop GUI (`computer-use`) or just fetching page text
(`web_extract`).

## Procedure

1. **Pick the context.** `launch_persistent_context` when the user's own
   logins and cookies matter (they sign in themselves in the window; you
   never touch credentials). Fresh headless contexts for tests.
   When the user must log in by hand (BankID, 2FA), the window has to be
   VISIBLE. The browser_exec helpers launch Chrome with `--headless=new`,
   so check `/proc/<pid>/cmdline` before telling the user to look for a
   window. Copying the real profile does not carry the session either:
   session-cookie logins don't survive the copy, and the copy is refused
   while their Chrome holds the profile lock. Instead, launch a visible
   Chrome yourself as a tracked background process (terminal
   `background=true`, not nohup): `/opt/google/chrome/chrome
   --user-data-dir=<scratch dir> --remote-debugging-port=9333
   --no-first-run --disable-features=Translate --new-window <url>`. Confirm
   with `curl localhost:9333/json/list` that the page target exists, have
   the user log in there, then drive it over CDP on that port (Playwright
   `connect_over_cdp("http://localhost:9333")`). Turn translation off,
   because auto-translate corrupts medical and legal terms.
2. **Characterize the target page before choosing input and scroll
   mechanisms.** One instrumented probe answers: what scrolls it (document
   scroll vs inner container vs fixed player), which inputs it actually
   accepts, and how content change is observable. Automate the mechanism
   that works, not the one you assumed.
3. **Write the page script against stable selectors only**: element tags
   (`video`, `input`, `button`) and `data-*` attributes. Never
   framework-hashed class names — they churn silently and the failure mode
   is a feature that stops firing, not an error.
4. **Define the event contract** between page and host: the page calls one
   exposed binding (`window.<name>(event, payload)`) with flat JSON payloads;
   the host sends state back through targeted `page.evaluate` calls.
5. **Wire the host loop**: pump the connection on a fixed interval (one cheap
   `page.evaluate`), process queued events, send updates back. On task end,
   kill the window with a hard deadline and SIGKILL fallback, then verify the
   process tree is gone.
6. **Test in two layers**: unit tests with fakes for host logic, and one live
   E2E per integration boundary against the real library (a local fixture
   page is enough). Only the live layer proves the library's delivery
   semantics.

## Pitfalls

- **Never call driver APIs from inside an exposed-binding callback (sync
  API).** The callback executes inside the outer driver call; a re-entered
  sync call deadlocks the connection forever. Queue the work in the callback
  and flush it after the pumping call returns.
- **Every wait loop that expects page events must pump.** Binding callbacks
  only deliver while a driver call is in flight, so `time.sleep` polling
  never drains them. Sleep with `page.wait_for_timeout` instead.
- **Window flags lie; settle the geometry and verify it landed.** The driver
  appends its own `--window-size` derived from its default viewport, and
  `viewport=None` does NOT opt out of viewport emulation — the page keeps an
  emulated 1280x720 layout inside whatever window you create and content
  overflows it. `no_viewport=True` is the real opt-out. Wayland WMs ignore
  `--window-position`. Set the final geometry with CDP
  `Browser.getWindowForTarget` + `Browser.setWindowBounds`, sent after a
  warm-up navigation (bounds sent before the window maps get ignored or
  reverted) and re-sent until `window.outerWidth` actually matches, with a
  bounded timeout. Never fit layout with
  `Emulation.setDeviceMetricsOverride`: it resizes the OS window to the
  metrics.
- **Fakes cannot reproduce a library's callback/async semantics.** A green
  fake suite can sail straight through a re-entered-call deadlock; only a
  live test against the real library catches that class of bug.
- **Verify hard-kills externally.** Closing a wedged context can leave the
  whole process tree alive. After the kill, `pgrep` for the browser's
  user-data-dir to confirm nothing remains, and capture the OS pid at launch
  so the SIGKILL fallback has a real target.
- **Pattern-matching your own processes is a self-kill trap.** Write a
  pattern that cannot match the invoking shell's own command line
  (`profil[e]`, not `profile`) — `pkill -f`/`pgrep -f` match the shell running
  them and kill your session. A pattern starting with `--` is parsed as an
  option: pass the `--` terminator (`pgrep -f -- "--user-data-dir=..."`).
  Before SIGKILLing a matched pid, filter by `/proc/<pid>/comm` (`chrome`,
  `chromium`) so a shell whose argv merely contains the pattern is never
  killed.
- **Fake media in test fixtures with
  `Object.defineProperty(HTMLMediaElement.prototype, "duration", ...)`**
  instead of shipping binary media; scripts that read `duration` then run
  unmodified against the fixture.
- **Playhead position is not content change.** `currentTime` advances just by
  playing, and MSE players reuse one `<video>` with a constant blob `src`, so
  neither detects a clip swap. Identify content by identity (caption +
  duration) and, for swap-in-place players, subscribe to `durationchange` on
  the element — it never leaves the DOM, so IntersectionObserver never
  re-fires. Before trusting any change detector, negative-control it: it must
  report "no change" for a case you know did not change.
- **Fixed-player feeds defeat scrolling entirely.** When
  `document.scrollingElement.scrollHeight <= clientHeight + 4`, nothing
  scrolls: `scrollBy`, wheel, and DOM-constructed touch events are all no-ops,
  and even CDP `Input.dispatchTouchEvent` can be ignored by gesture code that
  demands real touch. Seek the clip to its end
  (`video.currentTime = video.duration - 0.05`) to trigger the player's own
  ended/auto-advance logic, and derive clip transitions from `durationchange`.
- **DOM-constructed events carry `isTrusted=false` and gesture code may
  ignore them.** `new TouchEvent(...)` / `new PointerEvent(...)` dispatched
  from page JS are untrusted; CDP `Input.dispatch*` events are trusted input
  but still not universally sufficient. Verify an input path with the honest
  detector above, never with "the event dispatched successfully".
- **Probe volume can degrade the target.** Sites serve crippled pages to
  clients that look robotic (many launches, no login). When probes and the
  user's real session disagree, re-test in a real logged-in session before
  concluding the feature is broken.

## Recipes

`references/playwright-python-recipes.md`: re-entrancy probe, pump-aware
wait helper, media fixture page, CDP window bounds, unmuted-autoplay launch
flag, process-tree kill and verify.