#!/usr/bin/env python3
"""Log gamepad presses for mapping.
Usage: gamepad_probe.py /dev/input/eventN [outfile] [seconds]
Run in background, confirm alive with pgrep, ask user to press each button a distinct number
of times, then: grep BTN outfile | sort | uniq -c
First line records key codes and abs axes: index base is the lowest key code (288 or 304);
d-pad on abs 0/1 = axis mapping, abs 16/17 = hat."""
import array, fcntl, struct, sys, time

dev = sys.argv[1] if len(sys.argv) > 1 else '/dev/input/event2'
out_path = sys.argv[2] if len(sys.argv) > 2 else 'padlog.txt'
secs = int(sys.argv[3]) if len(sys.argv) > 3 else 600
f = open(dev, 'rb')

def bits(ev, n):
    buf = array.array('B', [0] * ((n + 7) // 8))
    fcntl.ioctl(f, 0x80004520 + ev + (len(buf) << 16), buf, True)
    return [i for i in range(n) if buf[i // 8] >> (i % 8) & 1]

keys = bits(1, 0x300)
out = open(out_path, 'w', buffering=1)
out.write(f'# keys={keys} abs={bits(3, 0x40)}\n')
base = min(keys) if keys else 288
fmt = 'llHHi'
sz = struct.calcsize(fmt)
end = time.time() + secs
while time.time() < end:
    _, _, t, c, v = struct.unpack(fmt, f.read(sz))
    if t == 1 and v == 1:
        out.write(f'BTN {c - base}\n')
    elif t == 3:
        out.write(f'AXIS {c} {v}\n')
