---
name: linux-crash-diagnosis
description: "Use when a Linux machine freezes, glitches, or misbehaves."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [linux, hardware, ram, memtest, journalctl, amdgpu, stability]
    related_skills: [backup-and-recovery, systematic-debugging, pre-registered-experiments, swedish-consumer-disputes]
---

# Linux crash and freeze diagnosis

Find the cause from evidence before blaming the workload that happened to be running.

## When to Use

Hard freezes, display death with no recovery, spontaneous reboots, "why is this machine so unstable", or a long job that died with the whole machine. Also machine-level annoyances: screen tearing / colored-pixel artifacts under load, and a screen that blanks and recovers when a video goes fullscreen (see `references/amdgpu-display-glitches.md`) and "why so many system updates" / repeated install-on-reboot screens (see `references/ubuntu-update-sources.md`). Not for a single app crash with a stack trace (use `systematic-debugging`).

Before any of it: read `~/STATUS.md` for prior hardware history on this machine (RAM swaps, memtest results, kernel params). Past fixes change the interpretation of new symptoms (e.g. single-channel RAM starves an iGPU).

## Procedure

1. **Classify the death from the journal.** `journalctl --list-boots`, then for each recent boot: the last 2 lines (`journalctl -b -N -n 2`) and whether it ended cleanly (`grep -c -E "Journal stopped|systemd-shutdown"` in its last 30 lines). Tabulate every abrupt ending with date and time; one freeze is an anecdote, a pattern across boots is a diagnosis.
2. **Read the previous boot for a cause.** `journalctl -b -1 -k -p warning` filtered for `amdgpu|drm|ring .* timeout|reset|mce|hardware error|oom|killed process|thermal|hung|watchdog|soft lockup`. Also check `/var/crash/`, `/sys/fs/pstore`, `/var/lib/systemd/pstore`. A journal cut mid-write with no kernel error and no dump = whole-system lockup below the kernel's reporting: RAM, power, firmware or GPU hang, not an app crash.
3. **Use a running job as a clock.** A job that logs at a steady interval pins the freeze time to seconds; its last line is the moment of death.
4. **Compare load across freezes.** `sar -q` / `sar -r` / `sar -S` from `/var/log/sysstat/saDD` in the window before each abrupt end, and against a heavier run that survived. A freeze at near-idle load clears the workload as primary cause and points at hardware (RAM first).
5. **Rule out thermals and memory pressure with numbers.** Read `hwmon` temps (`/sys/class/hwmon/*/name`, `temp*_input`) during a 90 s all-core matmul load; check swap and memory peaks from sar. Report them so they are eliminated, not just unmentioned.
6. **Identify the RAM.** SPD EEPROMs at `/sys/bus/i2c/devices/0-005N/eeprom` (needs the `ee1004`/`spd5118` driver): DDR5 part number at bytes 521..551, manufacturer id 512..514 (`802c` = Micron/Crucial), year/week 515..517. Mismatched date codes on a "kit" = two sources. Ask whether the RAM is second-hand.
7. **memtest86+** (the `memtest86+` package adds grub entry "Memory test (mt86+x64)"):
   - Its EFI binary is unsigned: Secure Boot must be off (`systemctl reboot --firmware-setup`), and turned back on after.
   - Hidden grub menu: `sudo grub-reboot "Memory test (mt86+x64)"` then reboot, or tap Esc at boot (too many taps drop to `grub>`; type `normal`).
   - Run at least 4 passes; start it warm. Any error = faulty. memtest freezing mid-test is itself typical of bad RAM.
   - It saves nothing to disk: the user's phone photo is the record. Load it with vision; if text is small, crop/rotate with PIL and re-read. XOR expected vs found per error line: an identical bit mask across all errors = one physical fault (chip or contacts), which is the evidence a seller claim needs.
   - Bisect: one stick at a time in slot A, then the other; then the second slot if both pass.
8. **After a RAM fault is confirmed, assess damage.** `git fsck` across repos; quarantine (not delete) any computed results made while the fault existed; warn that the daily backup may have mirrored corrupted files over good ones and that older remote copies are the net.
9. **Report the consequences of the fix.** Fewer/one stick: capacity (subtract the iGPU VRAM carve-out, `mem_info_vram_total`), single-channel bandwidth (time one known unit before vs after), and which local models no longer fit.

## Rules

- Answer "is it the experiment?" plainly with evidence; a workload that survived heavier load elsewhere is a trigger at most.
- Steps that need sudo the agent lacks (`softlockup_panic`/`hardlockup_panic` so kdump captures the next freeze, BIOS, grub-reboot) go to the user as exact commands.
- Cheapest discriminating test first: logs and sar take minutes, memtest is overnight, BIOS/kernel swaps come after RAM is cleared.
- When the logs are clean (no driver error for a visible symptom), ask the user in ONE clarify form: onset (always / after which change), trigger, appearance, scope (fullscreen only vs whole desktop). Those four answers discriminate more than another log pass.
- **A silent symptom is not a driver-free symptom.** Modern atomic modesets, compositor fullscreen transitions and overlay-plane promotion can blank the display without printing one line to either the kernel or the user journal. Capture the journal across a reproduction (`journalctl -f -o short-precise > /tmp/repro.log`, then have the user trigger it) and read the window; if the window is empty, that rules out nothing and the next test is a renderer switch, not another log grep.
- **Identify the app from processes, not from `command -v`.** Flatpak and Snap apps are not on PATH, so "no browser installed" can be flatly wrong while Chrome has been running for days. Check `ps -eo pid,etimes,args | grep -iE '<app>'` and `flatpak list`. Likewise the agent shell has no session env (`XDG_SESSION_TYPE` prints empty): read the real one from `loginctl list-sessions` + `loginctl show-session <id> -p Type -p Desktop`, and an app's actual platform from `/proc/<pid>/environ`.
- **Two "different" apps that both misbehave can be one engine.** An Electron app and Chrome are both Chromium; a symptom reproduced in both has not cleared the application layer. Split engine from driver with a renderer that shares no code with either (see the fullscreen-blank test ladder in `references/amdgpu-display-glitches.md`).
- One change per test (firmware, then clock pin, then kernel), each with an exact undo command and a fallback (older kernel in the boot menu), so the fix is attributable.
- "Are there newer drivers?" means upstream, not apt: `apt-cache policy` + `fwupdmgr get-updates` only prove Ubuntu's latest. Check upstream linux-firmware, kernel mainline and the vendor BIOS page too (recipe in `references/amdgpu-display-glitches.md`). Say "newest Ubuntu ships", never "latest", until upstream is checked.
- If the faulty part was bought second-hand, hand off to `swedish-consumer-disputes` for the claim.
