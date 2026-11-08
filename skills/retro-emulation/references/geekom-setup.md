# Geekom emulation setup (built 2026-10-12)

State of Karl's machine; read before touching it.

- RetroArch = user Flatpak `org.libretro.RetroArch`. Config: `~/.var/app/org.libretro.RetroArch/config/retroarch/` (`$R`). Cores downloaded manually into `$R/cores`, `$R/info`.
- Library: `~/Emulation/{roms/<system>,bios,saves,states}`. `~/Emulation/refresh_playlists.py` rebuilds .lpl per system (nes->mesen, snes->snes9x, megadrive/mastersystem/gamegear->genesis_plus_gx, gb/gbc->gambatte, gba->mgba, nds->melondsds, psx->swanstation, n64->mupen64plus_next, pcengine->mednafen_pce_fast, arcade->fbneo).
- Launcher: dock entry `retro-games.desktop` -> `~/Emulation/launch.sh` (refresh playlists, run `~/Emulation/fix_menu_keys.py`, start RetroArch). Plain `org.libretro.RetroArch.desktop` override is NoDisplay and also uses launch.sh.

## Pitfalls
- RetroArch saves retroarch.cfg on exit (config_save_on_exit), so edits made while it runs are overwritten, and toggles like `,` (shader off) persist globally. Fix: settings that must stick live in `fix_menu_keys.py`, re-applied every launch (Esc=menu, F12=quit, shader enable, asset/db/overlay/shader dirs).
- Flatpak white-box menu icons: `assets_directory` pointed at an empty config dir. Point it (and database/overlay/shader dirs) at `/app/share/libretro/...`.
- GNOME dock grouping: Wayland app_id is `com.libretro.RetroArch`; set `StartupWMClass=com.libretro.RetroArch`.
- Controller is a DragonRise clone (autoconfig vendor 121 / product 17, custom cfg `SWITCH CO.,LTD. USB Gamepad .cfg`; competing stock 121/17 profiles deleted). Layout: d-pad, A B C, X Y Z, Start, Mode (right shoulder; NO left bumper). Buttons A=1 B=2 C=4 X=0 Y=3 Z=5 Mode=8 Start=9. Hotkey = hold Mode.
- melonDS DS: BIOS-pack firmware is 'corrupted' -> `melonds_sysfile_mode = builtin`. Mic via pipewire.
- Filters: per-core `.slangp` presets with `#reference` into `/app/share/libretro/shaders/shaders_slang` (Genesis crt-guest-advanced-ntsc, other TV cores crt-guest-advanced-fast, GB/GBC/GBA lcd-grid-v2, DS none). Sprite-limit off on GPGX/Mesen/Snes9x; mGBA mix_smart + color correction; Gambatte mix_frames accurate.
- Volume `audio_volume = -6` dB. Unpacker for rar/7z: bundled `7zz` (no system 7z).
- Verify headless-ish: `--max-frames=N --max-frames-ss --max-frames-ss-path=...` gives a last-frame screenshot; `pw-record` on the sink monitor proves audio.
- Never download ROMs from ROM sites (declined theromdepot); only sort files Karl provides.
