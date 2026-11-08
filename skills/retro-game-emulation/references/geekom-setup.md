# geekom emulation setup (live state)

Hardware: Ryzen 9 7940HS / Radeon 780M (RADV, Vulkan OK), Ubuntu 26.04 GNOME Wayland, 1440p display.

## Paths
- RetroArch: user Flatpak `org.libretro.RetroArch` (1.22.x), config at `~/.var/app/org.libretro.RetroArch/config/retroarch/` (cores/, info/, autoconfig/udev/, playlists/, retroarch.cfg). The Flatpak has `filesystems=host` and `devices=all`, so ~/Emulation and /dev/input work without overrides.
- Library: `~/Emulation/roms/{nes,snes,megadrive,mastersystem,gamegear,gb,gbc,gba,nds,psx,n64,pcengine,arcade}`, `~/Emulation/{bios,saves,states}`.
- Launcher: `~/Emulation/launch.sh` runs `~/Emulation/refresh_playlists.py` (folder -> core table, rebuilds .lpl, removes empty ones), then `flatpak run`. Desktop entry "Retro Games" is at `~/.local/share/applications/retro-games.desktop`. To add a system, add a row to SYSTEMS in refresh_playlists.py and drop its core into cores/.
- Also installed: system Flatpak Nestopia (redundant with Mesen).

## Karl's pad
A 6-button Sega-style pad: d-pad, A B C, X Y Z, Start, Mode, and only ONE shoulder button (it acts as Mode, there is no left bumper), no analog stick. It enumerates as `SWITCH CO.,LTD. USB Gamepad ` (trailing space), DragonRise `0079:0011` = decimal vendor 121 / product 17. It has also shown up as `0f0d:00c1` "HORIPAD for Nintendo Switch" / "Pro Controller", so re-check before remapping.

Measured indices (code-288): X=0 A=1 B=2 Y=3 C=4 Z=5 Mode=8 Start=9. D-pad on ABS 0/1 (axis, not hat, idle value 128).

Profile: `autoconfig/udev/SWITCH CO.,LTD. USB Gamepad .cfg`. Every other stock cfg with VID 121 / PID 17 was deleted. Re-delete them if the autoconfig set is ever re-copied.

RetroPad mapping: y=1(A) b=2(B) a=4(C) l=0(X) x=3(Y) r=5(Z) select=8(Mode) start=9.

Hotkeys (`input_enable_hotkey_btn = 8`, hold Mode): Start=menu, Z=save state, X=load state, Y=fast forward, A=rewind, C=quit.

## Verified
SNES (snes9x) launch: autoconf matched port 1, Vulkan on the 780M. The other cores are installed but were not launched at setup time.
