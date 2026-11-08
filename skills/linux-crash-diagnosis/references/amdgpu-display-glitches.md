# AMD iGPU display tearing / artifacts (amdgpu, Wayland)

Symptom class: tearing line, green/pink pixelated lines, garbage blocks, worse under GPU load, visible on desktop and cursor area as well as fullscreen.

## Fullscreen goes black for ~1 s, or content renders at a fixed offset (2026-11-02, geekom A7 Max)

Symptom: every fullscreen window (Chrome, Electron, ffplay) blanks 0.5-1 s on
entering fullscreen and comes back with content shifted by a fixed amount (~600 px on
a 1440-high screen); moving the cursor blanks and re-renders the shifted frame.
Windowed is fine. Monitor shows **no** OSD during the blank, so the GPU never stops
sending frames — the wrong memory region is being scanned out.

Cause found: **Variable refresh rate enabled** (`~/.config/monitors.xml`
`<ratemode>variable</ratemode>`, panel running 2560x1440 @ ~75 Hz over HDMI on a
Phoenix1 iGPU, single-channel RAM). Turning VRR off in Settings -> Displays fixed it.

Diagnostic order that works, cheapest first:
1. Read `~/.config/monitors.xml` for `<ratemode>` and `<rate>` — a variable ratemode is
the answer often enough to check first. Compare against the EDID preferred timing
(parse DTD at byte 54) to see if the panel is being driven above it.
2. `power_dpm_force_performance_level=high` (undo: `auto`) — if this changes nothing,
the display engine is not merely underflowing on a clock switch.
3. Confirm it is not the app: play the file with ffplay (`SDL_VIDEODRIVER=x11`,
`XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.*`, since the ffmpeg bundle has no
SDL wayland driver). Blanking in a non-Chromium renderer clears the app/codec.
4. Only then boot the previous kernel.

Notes: kernel and mutter both log **nothing** during this event, so a silent journal
is evidence of a compositor/scanout plane problem, not of "no problem". If the monitor
loses signal (OSD appears) the fault is one layer lower than this.

## Evidence pass (no sudo needed)

```bash
lspci -nnk | grep -iA3 -E "vga|display"           # chip + driver
echo $XDG_SESSION_TYPE; uname -r; cat /proc/cmdline # wayland/x11, kernel, existing amdgpu.* params
for b in -5 -4 -3 -2 -1 0; do echo "$b: $(journalctl -k -b $b | grep -ciE 'amdgpu.*(timeout|reset|fault|hang)|REG_WAIT|flip_done|ring .* timeout')"; done
D=/sys/class/drm/card*/device; cat $D/mem_info_vram_total $D/power_dpm_force_performance_level $D/pp_dpm_sclk $D/pp_dpm_mclk
for c in /sys/class/drm/card*-*; do [ "$(cat $c/status)" = connected ] && echo $c; done   # active connector (HDMI vs DP)
journalctl -k -b | grep "DMUB hardware"            # display firmware version in use
cat /sys/class/dmi/id/{product_name,bios_version,bios_date}
```
- One boot-time `REG_WAIT timeout ... optc*_disable_crtc` and `Failed to setup vendor infoframe` are routine on Phoenix; they are not the cause unless they repeat during use.
- Zero runtime errors with visible corruption = fault is below the kernel's reporting: display engine underflow or the cable/link.
- Existing `amdgpu.sg_display=0` on the cmdline means a flicker workaround was already applied; don't re-suggest it.
- Monitor model: parse EDID descriptors 0xfc/0xff from `/sys/class/drm/<conn>/edid`.

## Interpreting

- Display underflow (bandwidth starvation): scales with GPU load, colored lines/blocks. Worse on single-channel RAM, since the iGPU shares system memory bandwidth.
- Signal integrity (HDMI cable/port): sparkles regardless of load; 1440p60 is low bandwidth, so suspect less unless swapping ports changes it.

## Fullscreen blank that recovers, with nothing in the log

Symptom: the whole screen goes black for about a second when a video enters fullscreen, then
returns; windowed playback is fine; every video, in every app; onset in the last few weeks.

This is a different class from the tearing/artifacts above, and the logs are empty for it —
no kernel line, no mutter/gnome-shell line, no amdgpu error. Treat the silence as a fact
about the layer, not as evidence that nothing happened.

Evidence pass to add to the block above:

```bash
grep -hE " install (linux-image|linux-modules|linux-firmware|mesa|libdrm|mutter|gnome-shell)" \
  /var/log/dpkg.log /var/log/dpkg.log.1 | tail -25          # what changed near the onset
ls -1 /boot/vmlinuz-*                                        # an older kernel still present = free A/B
ps -eo pid,etimes,args | grep -iE "chrome|electron" | grep -v -- --type=   # real app identity
cat /sys/class/drm/card1-HDMI-A-1/vrr_enabled 2>/dev/null     # absent attr = no adaptive sync to blame
```

Least-cost ladder, each rung clearing one layer (no sudo needed until rung 4):

1. **A renderer that shares no code with the app.** The bundled static `ffplay` is SDL2 +
   OpenGL; its SDL is built x11-only (`SDL_VIDEODRIVER=wayland` fails with "wayland not
   available"), so drive it through XWayland and hand it the compositor's auth cookie:
   ```bash
   A=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
   env DISPLAY=:0 XAUTHORITY="$A" SDL_VIDEODRIVER=x11 \
     ffplay -fs -autoexit <file>.mp4
   ```
   Blanks too = fault is below the app (driver, compositor, display engine). Clean = narrow
   it to Chromium's fullscreen path and take rungs 2-3.
2. **Native Wayland vs XWayland:** `flatpak run com.google.Chrome --ozone-platform=wayland`.
   Blanks under one and not the other = the direct-scanout / window-promotion path.
3. **Chromium without its own compositor:** `--disable-gpu-compositing`. Clean = GPU
   compositing, and hardware acceleration is a candidate to leave off.
4. **Older kernel from the boot menu** when a new one landed near the onset. Both kernels
   usually stay in `/boot`, so this costs a reboot and is reversible by rebooting back.

Keep a Phoenix iGPU on single-channel RAM in mind: that is the display-underflow substrate,
and the ledger records whether the second stick was pulled. Say which layer each result
cleared instead of naming a cause early — a blank that leaves no trace is often a modeset,
and the user's "it happens in more than one app" does not rule out a shared engine.

## Discriminating tests, cheapest first (user runs sudo)

1. Screenshot during a glitch: artifact in the screenshot = rendered wrong (driver/memory); clean screenshot = scanout or link.
2. Pin clocks: `echo high | sudo tee /sys/class/drm/card1/device/power_dpm_force_performance_level` (undo: `auto`; resets at reboot). Glitches gone = DPM clock switching starves the display.
3. Other port/cable the user already owns (second HDMI, USB-C DP alt-mode). Don't recommend buying a cable before this result (user checks gear-buy urges).

## Checking for newer drivers than Ubuntu ships

- Display firmware (DMCUB) is the best match for load-dependent scanout artifacts. Phoenix (780M, gfx1103) uses `amdgpu/dcn_3_1_4_dmcub.bin`. Compare upstream to installed:
  ```bash
  curl -s "https://gitlab.com/api/v4/projects/kernel-firmware%2Flinux-firmware/repository/commits?path=amdgpu/dcn_3_1_4_dmcub.bin&per_page=5"
  curl -sfLo dmcub.bin https://gitlab.com/kernel-firmware/linux-firmware/-/raw/main/amdgpu/dcn_3_1_4_dmcub.bin
  zstd -dc /lib/firmware/amdgpu/dcn_3_1_4_dmcub.bin.zst | cmp -s - dmcub.bin && echo SAME || echo DIFFERENT
  ```
  Install as an override (reversible, doesn't touch the package):
  ```bash
  sudo mkdir -p /lib/firmware/updates/amdgpu && sudo cp dmcub.bin /lib/firmware/updates/amdgpu/dcn_3_1_4_dmcub.bin
  sudo update-initramfs -u -k $(uname -r) && reboot   # verify DMUB version changed in journal
  ```
  Undo: remove the file, rerun update-initramfs. Fallback: previous kernel in the boot menu (its initramfs is untouched).
- Kernel: Ubuntu `-hwe-edge` often equals the regular HWE kernel; check `apt-cache policy` before suggesting it. Mainline builds: `curl -s https://kernel.ubuntu.com/mainline/ | grep -oE 'v7\.[0-9]+[^/]*/' | sort -uV | tail`. Unsigned, so only bootable with Secure Boot off (`mokutil --sb-state`); no zfs/v4l2loopback modules, no auto updates: test-only.
- Mesa: renders app content; unlikely to fix artifacts that also hit the cursor/desktop scanout.
- BIOS: sets UMA carve-out and memory timings. GEEKOM: help.geekompc.com (USB FAT32 flash, Secure Boot off, F7 boot menu). Flash only if a newer version exists.
