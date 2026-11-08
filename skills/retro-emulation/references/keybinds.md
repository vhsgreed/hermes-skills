# RetroArch keybinds on geekom (as configured)

Keyboard (no hotkey-enable key needed on keyboard):

| Key | Action |
|---|---|
| Esc | Menu toggle (remapped from F1; F1 still works too) |
| F12 | Quit RetroArch (remapped from Esc) |
| F2 / F4 | Save / load state |
| F6 / F7 | Previous / next state slot |
| Space | Fast forward toggle |
| L (hold) | Fast forward |
| E (hold) | Slow motion |
| R (hold) | Rewind |
| P | Pause |
| K | Frame advance (while paused) |
| H | Reset |
| F | Fullscreen toggle |
| F8 | Screenshot |
| F9 | Mute |
| Numpad + / - | Volume |
| , | Shader on/off (persists on exit, launcher re-enables) |
| M / N | Next / previous shader |
| F3 | FPS counter |
| F11 | Grab mouse (useful for DS touch) |
| Tab | Next DS screen layout (melonDS DS binding) |
| Scroll Lock | Game focus mode: disables ALL keyboard hotkeys; press again if keys stop working |

Pad (hold Mode, then): Start menu, Z save, X load, Y fast-forward, A rewind, C quit. In the menu: d-pad moves, C selects, B goes back.

Config keys: `input_menu_toggle`, `input_exit_emulator` (keyboard), `*_btn` for pad indices. Set the remaps in `fix_menu_keys.py` so they survive exits.
