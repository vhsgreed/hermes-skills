#!/usr/bin/env python3
"""Log gamepad button presses and axis moves from an evdev node for mapping.

Usage: python3 padlog.py [/dev/input/eventN] [outfile] [seconds]
Find the node via: ls -l /dev/input/by-id/ | grep -i joy
Run in background, verify with `pgrep -af padlog.py`, have the user press
button k exactly k times, then: grep BTN out | sort | uniq -c
BTN index printed relative to 288 (BTN_JOYSTICK); for BTN_GAMEPAD pads
(codes 304+) subtract another 16 to get RetroArch's index.
"""
import struct
import sys
import time

dev = sys.argv[1] if len(sys.argv) > 1 else '/dev/input/event2'
out_path = sys.argv[2] if len(sys.argv) > 2 else 'padlog.txt'
secs = int(sys.argv[3]) if len(sys.argv) > 3 else 600

fmt = 'llHHi'
sz = struct.calcsize(fmt)
with open(dev, 'rb') as f, open(out_path, 'w', buffering=1) as out:
    end = time.time() + secs
    while time.time() < end:
        _, _, etype, code, val = struct.unpack(fmt, f.read(sz))
        if etype == 1 and val == 1:
            out.write(f'BTN {code - 288} (code {code})\n')
        elif etype == 3:
            out.write(f'AXIS {code} {val}\n')
