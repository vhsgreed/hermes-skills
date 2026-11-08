---
name: retro-emulation
description: Use when setting up or fixing game emulation (RetroArch).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [emulation, retroarch, gaming, controller]
    related_skills: []
---

# Retro emulation (RetroArch on geekom)

## When to Use
Use this skill when Karl asks about emulators, ROMs, BIOS files, RetroArch cores, controller mapping, or getting a console's games running on geekom.

Karl wants to play, not configure. Run the whole setup end to end, then report what works, what was tested, and anything he must do himself (only root actions such as `sudo snap remove`).

## Current layout (geekom)
- RetroArch is the Flathub Flatpak, installed with `--user` (system installs need sudo). Config root: `~/.var/app/org.libretro.RetroArch/config/retroarch/` (retroarch.cfg, cores/, info/, autoconfig/udev/, playlists/, `config/<Core Name>/<Core Name>.opt`).
- Library: `~/Emulation/{roms/<system>,bios,saves,states}`. `~/Emulation/launch.sh` runs `refresh_playlists.py` and then RetroArch. The desktop entry is "Retro Games". Playlists are rebuilt from folder contents on every launch, so adding a game means dropping the file into `roms/<system>/`.
- To add a system, add a row to the `SYSTEMS` dict in `refresh_playlists.py` (folder -> playlist name, core, display name) and drop its `.so` + `.info` into cores/ and info/.
- Standalone emulators are unwanted. Keep everything in RetroArch unless a system really needs a standalone (PS2/GC and newer).
- `launch.sh` also runs `~/Emulation/fix_menu_keys.py`, a regex replace-or-append that re-asserts the settings RetroArch tends to lose on exit: Escape = menu, F12 = quit, the `/app/share/libretro/...` asset/database/overlay/shader paths, and `video_shader_enable`/`auto_shaders_enable = true`. Any setting Karl must always have goes into that script's dict, not only into retroarch.cfg.
- Dock/sidebar: `~/.local/share/applications/retro-games.desktop` is pinned in `org.gnome.shell favorite-apps` and carries `StartupWMClass=com.libretro.RetroArch`, the Wayland app_id the Flatpak window reports. The Flatpak's own `org.libretro.RetroArch.desktop` is shadowed by a user copy with `NoDisplay=true` and `Exec=launch.sh`, so there is one entry and the window groups under it.

## Procedure
1. **Inventory first:** run `lsusb`, `/proc/bus/input/devices`, `ls ~/Downloads`, `flatpak list`, `snap list`. ROMs and BIOS packs arrive in `~/Downloads` as zip/7z/rar.
2. **Cores:** fetch them from `https://buildbot.libretro.com/nightly/linux/x86_64/latest/<core>_libretro.so.zip` and the info files from `https://buildbot.libretro.com/assets/frontend/info.zip`. Copy both into the config root. The defaults are mesen, snes9x, genesis_plus_gx, gambatte, mgba, melondsds, swanstation, mupen64plus_next, mednafen_pce_fast and fbneo.
3. **Archives:** if the host has no 7z/unrar, download the static `7zz` from `https://www.7-zip.org/a/7z<ver>-linux-x64.tar.xz` into scratch. It reads zip, 7z and rar. Use `7zz e -aos ... -r` to flatten a romset into `roms/<system>/`. Extract BIOS packs with `cp -rn` into `~/Emulation/bios`. Move the processed archives to `~/Downloads/emu-leftovers/` and tell Karl he can delete them.
4. **Controller:** follow the mapping procedure below. Never trust the stock autoconfig.
5. **Smoke test each touched core** with `timeout 15 flatpak run org.libretro.RetroArch --verbose -L <core.so> <rom> > log 2>&1`. Then grep for `Autoconf`, `Vulkan`, `Microphone`, `firmware|bios|corrupt`, `error`. In the report, say "launched, log clean" rather than "works" unless Karl has actually played it.

## Controller mapping (measure, don't guess)
- Run `lsusb` right before mapping. The same pad can enumerate under different VID:PID in different modes (seen: HORIPAD 0f0d:00c1, then DragonRise 0079:0011). RetroArch matches on the IDs reported at play time.
- Use `scripts/padlog.py`. Start it in the background, then confirm it is alive with `pgrep -af padlog.py` before asking Karl to press anything. A logger that dies silently wastes a round of his button presses.
- Order-proof capture: ask Karl to press each button a *different number of times* (A x1, B x2, C x3, ...). Then `sort | uniq -c` maps counts to indices regardless of the order he pressed in. Button index = evdev code minus 288 (BTN_JOYSTICK range) or minus 304 (BTN_GAMEPAD range).
- Ask what physical buttons actually exist before assuming a layout. Karl's "Sega" pad has A B C / X Y Z, Start, and a single shoulder button that is really **Mode**. It has no left shoulder and no analog stick.
- The recorded mapping below is one measurement, not a standing fact. Karl swaps pads (a 6-button Sega-style pad with no sticks, and a dual-stick 8BitDo SN30 Pro), and the same ROM set is only partly playable on one and fully playable on the other. Re-measure whenever `lsusb` reports a different VID:PID, then re-derive the playability notes from the pad actually connected before recommending anything.
- Write `autoconfig/udev/<exact input_device name>.cfg` (the name keeps any trailing space) with the measured indices. **Delete every other cfg sharing the same vendor/product id**. Otherwise a wrong community profile can win the match.
- Karl's pad (DragonRise 0079:0011): physical A=1 B=2 C=4 X=0 Y=3 Z=5 Mode=8 Start=9, d-pad on axes 0/1. RetroPad mapping: bottom row A B C -> Y B A, top row X Y Z -> L X R, Mode -> Select, and also the hotkey enable. Hotkeys are Mode+Start menu, +Z save, +X load, +Y fast-forward, +A rewind, +C quit. Autosave and auto-load are on.

## Filters, flicker and verification
Karl wants filters on by default: CRT for TV consoles, LCD grid for handhelds, sprite limit removed. When he asks whether things "work with audio and correct gfx", run the record-plus-screenshot check rather than claiming success from a log. Presets, option keys and the test harness are in `references/filters-and-verification.md`.

## Pitfalls
- Romsets (for example the Genesis 7z) mix `[BIOS] ...` files in with the games. After extracting, move them to `~/Emulation/bios/<pack>-bios/` so they don't show up as games.
- Never log into ROM sites or download ROMs, even when Karl offers his credentials. Decline once in a single line and keep sorting whatever he downloads himself.
- RetroArch rewrites `retroarch.cfg` on exit (`config_save_on_exit`). Edit keys with a regex replace-or-append script rather than rewriting the whole file after first launch, or you lose generated defaults. Check `pgrep -x retroarch` first: edits made while it runs are overwritten when Karl quits, so put them in `fix_menu_keys.py` (applied on next launch) and tell him to restart from Retro Games.
- A global toggle pressed in-game is persisted on exit. Pressing `,` saves `video_shader_enable = "false"`, so every core loses its filter, not just the one Karl was playing; that is why the launcher re-asserts it. When a filter "disappears", check that key before the per-core preset.
- **Menu icons render as white boxes** when `assets_directory` points at the empty config-root `assets/` folder. The Flatpak bundles assets at `/app/share/libretro/assets` (host view: `~/.local/share/flatpak/app/org.libretro.RetroArch/current/active/files/share/libretro/`). Point assets, `content_database_path` (`database/rdb`), cursors, cheats, overlays and `video_shader_dir` there too; the same empty-folder defaults break all of them.
- Generic `.desktop` entries for Flatpak apps often set `StartupWMClass` to the binary name. On Wayland GNOME matches the window's app_id instead, so the running window shows as a separate generic icon. Read the real app_id from the binary (`strings .../bin/retroarch | grep -i libretro`) and set it.
- Keyboard defaults Karl should know about are in `references/keybinds.md`; give that table when he asks about keybinds.
- Downloaded BIOS packs often include a DS `firmware.bin` that melonDS DS flags as corrupted. Set the core to built-in system files. See `references/melonds-ds.md`.
- Removing snaps needs root. Hand Karl the exact `sudo` command instead of trying again. Use `sudo snap remove --purge <snap>` when the snap owns a large data directory: without `--purge`, snapd first copies that whole directory into `/var/lib/snapd/snapshots`, so removing a snap that holds 24 GB needs 24 GB of free space before it frees anything. `apt install gnome-software-plugin-snap` puts a snap tab in GNOME Software when he would rather not use the terminal.
- Check the connected pad against each console's input needs before recommending games, and state the mismatches in the report. This is per-pad, not per-console, and it changes when the pad does: twin-stick games need two sticks, N64 C-buttons map to the right stick, and GC or PS2 titles that read analog triggers (gradual acceleration, pressure-sensitive weapons, water cannons) are unplayable on a pad whose L2/R2 are digital. Touch- and mic-driven DS games need the mouse and mic whatever the pad.

## References
- `references/filters-and-verification.md`: shader presets per core, flicker options, volume in dB, audio/graphics test harness.
- `references/melonds-ds.md`: DS setup with mic, mouse touch and gamepad together (core option keys and values, hidden-button bindings).
- `references/keybinds.md`: keyboard and pad hotkeys as configured, with the Scroll Lock gotcha.
- `scripts/padlog.py`: evdev button logger for controller mapping.
