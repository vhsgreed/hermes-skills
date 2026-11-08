#!/usr/bin/env python3
"""Vet RSS/Atom/RDF feeds: reachability, item count, items under 24h old.

Usage: feedtest.py URL [URL ...]
Output per feed: OK <items> <fresh<24h> URL | first title, or ERR <reason> URL.
A feed with many items but ~0 fresh is stale: do not add it.
"""
import datetime as dt
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


def age_hours(s):
    try:
        w = parsedate_to_datetime(s)
    except Exception:
        try:
            w = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if w.tzinfo is None:
        w = w.replace(tzinfo=dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - w).total_seconds() / 3600


for u in sys.argv[1:]:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 feedtest/1.0"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
        n, ages, first = 0, [], ""
        for x in root.iter():
            if x.tag.rsplit("}", 1)[-1].lower() not in ("item", "entry"):
                continue
            n += 1
            for c in x:
                k = c.tag.rsplit("}", 1)[-1].lower()
                if k == "title" and not first:
                    first = (c.text or "").strip()[:60]
                if k in ("pubdate", "published", "updated", "date"):
                    a = age_hours((c.text or "").strip())
                    if a is not None:
                        ages.append(a)
                        break
        fresh = sum(1 for a in ages if a < 24)
        print(f"OK  {n:3d} items {fresh:3d} <24h  {u}  | {first}")
    except Exception as e:
        print(f"ERR {type(e).__name__}: {str(e)[:50]}  {u}")
