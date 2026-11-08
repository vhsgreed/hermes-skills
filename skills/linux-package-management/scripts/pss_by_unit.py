#!/usr/bin/python3
"""Sum PSS per systemd cgroup so memory can be attributed to units, not PIDs.

RSS double-counts shared pages (every Chromium/Electron child adds the same
library pages), which makes a fat service look fatter than it is and a lean one
look equal to it. PSS splits each shared page by the number of sharers.

Usage:
  pss_by_unit.py              # system.slice + user@<uid> units, top 25
  pss_by_unit.py --all        # every cgroup, including app scopes
  pss_by_unit.py --grep gnome # only units matching a substring
"""
import os
import re
import sys
from collections import Counter

PSS_RE = re.compile(r"^Pss:\s+(\d+)", re.M)


def pss_kib(pid):
    try:
        with open(f"/proc/{pid}/smaps_rollup") as f:
            m = PSS_RE.search(f.read())
        return int(m.group(1)) if m else 0
    except (OSError, ValueError):
        return 0


def unit_of(pid):
    try:
        with open(f"/proc/{pid}/cgroup") as f:
            return f.read().strip().split("/")[-1] or "?"
    except OSError:
        return "?"


def main(argv):
    show_all = "--all" in argv
    needle = None
    if "--grep" in argv:
        i = argv.index("--grep")
        needle = argv[i + 1] if len(argv) > i + 1 else None

    totals = Counter()
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        unit = unit_of(entry)
        # Processes outside a unit live in the session root (user@1000.service).
        if not show_all and not ("system.slice" in unit or unit.count(".") == 1 or "@" in unit):
            continue
        if needle and needle not in unit:
            continue
        kib = pss_kib(entry)
        if kib:
            totals[unit] += kib

    for unit, kib in totals.most_common(25):
        print(f"{kib // 1024:6d} MB  {unit}")
    print(f"{sum(totals.values()) // 1024:6d} MB  TOTAL ({len(totals)} units)")


if __name__ == "__main__":
    main(sys.argv[1:])
