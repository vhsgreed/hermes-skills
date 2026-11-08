---
name: retro-game-emulation
description: Use when setting up emulators or gamepads on Linux.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [emulation, retroarch, gamepad, flatpak, hobby]
    related_skills: []
---

# Retro game emulation on Linux

Covers emulator choice, RetroArch install/config, cores, ROM/BIOS layout, playlists, and gamepad mapping. Karl's live setup on geekom is in `references/geekom-setup.md`. Read it first when touching that machine. Button logger: `scripts/gamepad_probe.py`.

## Standing preferences
- Karl wants it to work without fiddling. Do the whole setup end to end: install, cores, config, controller, launcher, smoke test. Ask him only for physical actions (pressing buttons) or for files only he has.
- Everything in RetroArch (Flathub). Karl had the standalone emulators removed and plays the old era only. Suggest a standalone (PPSSPP, PCSX2, Dolphin, Azahar) only if he asks for PSP/PS2/GC or newer. The geekom specifics and filters live in the `retro-emulation` skill.
- Never download ROMs or BIOS. Use what the user has, and tell him which BIOS a system needs.

## Procedure
1. **Probe hardware first** (one call): `lscpu`, `free -h`, `lspci | grep -i vga`, session type (Wayland/X11), `flatpak list`, `lsusb`, `/proc/bus/input/devices`, `ls /dev/input/by-id/`. Also search `~/Downloads` for ROMs (`*.nes *.smc *.sfc *.md *.gen *.gba *.gb* *.nds *.cue *.chd *.z64 *.pbp`) so they can be filed.
2. **Install** as a user Flatpak in the background with notify. The system flathub remote does not cover `--user`:
   `flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo && flatpak install --user -y --noninteractive flathub org.libretro.RetroArch`
   This pulls about 1 GB of runtimes, so do the other steps while it runs.
3. **Cores without the GUI:** download `https://buildbot.libretro.com/nightly/linux/x86_64/latest/<core>_libretro.so.zip` and the core infos from `https://buildbot.libretro.com/assets/frontend/info.zip` into `~/.var/app/org.libretro.RetroArch/config/retroarch/{cores,info}`. Default set: mesen, snes9x, genesis_plus_gx, gambatte, mgba, melondsds, swanstation, mupen64plus_next, mednafen_pce_fast, fbneo.
4. **Layout:** `~/Emulation/{roms/<system>,bios,saves,states}`. Move ROMs and their `.srm` saves out of Downloads. Point `system_directory`, `savefile_directory` and `savestate_directory` at these folders. Put junk (`.oops`, empty saves, extracted zips) in a leftovers folder. Do not delete it.
5. **Controller mapping:** see the section below.
6. **retroarch.cfg:** vulkan, fullscreen, udev joypad, autosave and autoload state (`savestate_auto_save/load`), `autosave_interval = 10`, rewind on. Hotkeys go behind an enable button (Select/Mode) because 6-button pads have no spare buttons. Template: `references/geekom-setup.md`.
7. **Playlists:** write `.lpl` JSON files directly. Each item needs `path`, `label`, `core_path`, `core_name`, `crc32: DETECT`, `db_name`, and the playlist name must be the libretro DB system name. Rebuild them on every launch with a wrapper script plus a `~/.local/share/applications/*.desktop` entry, so new ROMs show up with no in-app scanning.
8. **Smoke test:** run `timeout 12 flatpak run org.libretro.RetroArch --verbose -L <core.so> <rom> > log 2>&1` and grep for `Autoconf .* configured in port`, the Vulkan GPU line, and `Loading content`. Only report systems you actually launched as verified.

## Controller mapping (measure, don't trust)
- **Re-read the pad's VID:PID right before mapping.** Cheap pads switch modes or re-enumerate (a "Switch" HORI ID can turn into a DragonRise `0079:0011` after replug or a mode press), and the button codes change with it. Map whatever identity it reports at measurement time.
- **Community autoconfigs for generic clone IDs are often wrong.** Many different pads share `0079:0011`. Write your own profile with the same `input_device`, `input_vendor_id` and `input_product_id` (decimal), and delete every other autoconfig that matches that VID/PID so RetroArch can't pick the wrong one.
- **Order-proof capture:** run `scripts/gamepad_probe.py /dev/input/eventN <out>` in the background. **Confirm it is alive with `pgrep -af gamepad_probe` before asking the user to press anything**, because a dead logger wastes a round of user effort. Then ask him (via clarify) to press each button a *different number of times* (A x1, B x2, ... Start x8) plus one d-pad tap, and decode with `grep BTN <out> | sort | uniq -c`. Asking for a press order fails because users press in physical-label order or describe a different layout.
- Button index = evdev code minus the first key code (288 for BTN_JOYSTICK pads, 304 for BTN_SOUTH pads). The probe writes the capabilities on its first line. A d-pad that reports on ABS 0/1 maps with `input_*_axis`, while ABS 16/17 is a hat (`h0up`).
- Sega 6-button pads map to RetroPad as bottom A B C -> Y B A and top X Y Z -> L X R. Genesis Plus GX then reads A B C / X Y Z natively, SNES gets Y B A / L X R, and NES/GB use B and C. Set the `*_label` keys to the physical names.

## Pitfalls
- `flatpak install --user` fails if only the system remote exists. Add the user remote in the same command.
- PS1 playlists must list `.cue` (or `.chd`/`.pbp`), never the `.bin` tracks.
- Flag games that depend on hardware the pad lacks (touchscreen/mic for DS, analog sticks for N64/PS1) instead of claiming everything is playable.
