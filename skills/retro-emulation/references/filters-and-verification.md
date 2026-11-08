# Filters (shaders, sprite flicker) and audio/graphics verification

## Per-core shader presets (auto-applied)
Write `config/<Core Name>/<Core Name>.slangp` containing one line:
`#reference "/app/share/libretro/shaders/shaders_slang/<path>.slangp"`
Use the `/app/...` path, which is the Flatpak's in-sandbox view of the bundled shaders. Set `video_shader_enable = "true"` and `auto_shaders_enable = "true"` in retroarch.cfg. Look for `Specific shader preset found` in the `--verbose` log to confirm it loaded.

| Core(s) | Preset | Why |
|---|---|---|
| Genesis Plus GX | crt/crt-guest-advanced-ntsc | NTSC blending turns Genesis dither stripes into the intended transparency |
| Mesen, Snes9x, Beetle PCE Fast, FinalBurn Neo, SwanStation | crt/crt-guest-advanced-fast | scanlines plus glow, cheap on the 780M |
| mGBA, Gambatte | handheld/lcd-grid-v2 | LCD pixel grid |
| melonDS DS | none | keep it sharp for mouse touch |

## Flicker core options (`config/<Core>/<Core>.opt`, regex replace-or-append)
- `genesis_plus_gx_no_sprite_limit = "enabled"` (Genesis/SMS/GG), `mesen_nospritelimit = "enabled"`, `snes9x_reduce_sprite_flicker = "enabled"`.
- `mgba_interframe_blending = "mix_smart"`, `mgba_color_correction = "Auto"`, `gambatte_mix_frames = "accurate"`: these blend 30 Hz flicker effects the way slow LCDs did.
- Removing the sprite limit fixes multiplex flicker only. Deliberate flashing such as invincibility frames or 30 Hz transparency is part of the game. Rarely it exposes sprites that were meant to be hidden; if so, turn the limit back on for that one game with a per-game override.

## Volume
`audio_volume` is in dB (0 = unity). A literal "half" request means -6 dB, which halves amplitude; -10 dB is perceived as half as loud. Say which one you applied.

## Verify audio + graphics (not just "it loads")
Run each system windowed for about 25 s while recording the default sink's monitor, then screenshot the last frame:
```
SINK=$(wpctl inspect @DEFAULT_AUDIO_SINK@ | sed -n 's/.*node.name = "\(.*\)"/\1/p')
pw-record -P stream.capture.sink=true --target "$SINK" --rate 48000 --channels 2 --format s16 out.wav &
timeout 60 flatpak run org.libretro.RetroArch --verbose --appendconfig=test.cfg \
  --max-frames=1500 --max-frames-ss --max-frames-ss-path=$PWD/out.png -L <core.so> <rom> > out.log 2>&1
kill %1
```
- `test.cfg` sets fullscreen, `savestate_auto_save/load` and `config_save_on_exit` to false, so the test doesn't touch Karl's states or config.
- Measure RMS and peak of the WAV with the `wave` and `array` modules. `audioop` is gone in Python 3.13+.
- Tile the PNGs with ffmpeg `hstack`/`vstack` (same `scale` per tile, every labelled output consumed) and inspect the sheet with vision. Crop and zoom with `flags=neighbor` to check whether scanlines or the LCD grid are visible.
- Report untested systems (no ROMs) as untested.
