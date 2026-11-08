# melonDS DS (RetroArch core `melondsds`)

This core runs DS games with a real mic, mouse touch and gamepad at the same time. No standalone melonDS is needed.

## Core options
File: `<config root>/config/melonDS DS/melonDS DS.opt`
```
melonds_mic_input = "microphone"        # silence | blow | noise | microphone
melonds_mic_input_active = "always"     # hold | toggle | always  (always = just talk)
melonds_touch_mode = "auto"             # joystick | touch(pointer) | auto
melonds_show_cursor = "timeout"
melonds_number_of_screen_layouts = "3"
melonds_screen_layout1 = "top-bottom"
melonds_screen_layout2 = "hybrid-bottom"
melonds_screen_layout3 = "left-right"
melonds_hybrid_small_screen = "both"
melonds_console_mode = "ds"
melonds_sysfile_mode = "builtin"        # native needs clean bios7/bios9/firmware dumps
```
The option keys and values come from the upstream source at `src/libretro/config/constants.hpp` and `definitions/*.hpp` (github.com/JesseTG/melonds-ds). Check them there when you need a new option, instead of guessing.

## Frontend side (retroarch.cfg)
- `microphone_enable = "true"`, `microphone_driver = "pipewire"`. The log should show `[Microphone] [PipeWire] Found Source Node` and then `Enabled microphone`.
- The core binds its extra functions to RetroPad buttons that a 6-button pad lacks: **L3 = Microphone, R3 = Next Screen Layout, L2 = cursor speed/alt controls, R2 = touch with joystick cursor**. Map them to keyboard or mouse:
  - `input_player1_r3 = "tab"`, `input_player1_r3_mbtn = "3"` (middle click cycles layouts)
  - `input_player1_l3 = "v"`, `input_player1_l3_mbtn = "2"` (only matters when mic mode is hold/toggle)

## System files
- With `native`, the core looks in `system/melonDS DS/` first, then `system/`, for `bios7.bin` (md5 df692a80...) and `bios9.bin` (md5 a392174e...).
- If the log shows the line `Corrupted firmware detected` the pack's `firmware.bin` is bad. Use `builtin` unless Karl supplies a clean firmware dump.
- `PCap: init failed` and the Wi-Fi adapter warnings are harmless inside the Flatpak.
