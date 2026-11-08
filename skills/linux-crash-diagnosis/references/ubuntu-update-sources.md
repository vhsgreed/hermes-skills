# "Why so many system updates?" (Ubuntu)

Answer from logs, then give options; change nothing without the user's pick.

## Evidence

```bash
grep -E "^(Start-Date|Commandline|Requested-By)" /var/log/apt/history.log | tail -60   # who triggered each run
awk '/Start-Date: YYYY-MM-DD/,/End-Date/' /var/log/apt/history.log                     # what one run installed
zcat -f /var/log/apt/history.log* | awk '/^Start-Date/{d=$2} /^(Upgrade|Install):/{n=gsub(/\),/,"&"); c[d]+=n+1} END{for(k in c) print k,c[k]}' | sort   # packages/day
cat /var/lib/PackageKit/prepared-update            # batch already queued for the NEXT reboot
cat /var/lib/PackageKit/offline-update-competed    # result of the last offline update
apt list --upgradable; apt-get -s upgrade | grep -i phas
gsettings get org.gnome.software download-updates
cat /etc/apt/apt.conf.d/20auto-upgrades; ls /etc/apt/sources.list.d/
dpkg -l 'linux-image-[0-9]*' | grep ^ii
```

## Sources to name

- `Commandline: /usr/bin/unattended-upgrade` = silent daily security updates (~06:00, apt-daily-upgrade.timer).
- `packagekit role='update-packages'` with no Requested-By = GNOME Software offline update (install-on-reboot screen, `pk-offline-update` in journal, followed by a second reboot).
- Third-party repos in sources.list.d (Chrome, PPAs, NodeSource, Tailscale) release often and inflate counts.
- One kernel bump = ~8 packages (image, modules, headers x2, tools x2, zfs, v4l2loopback + meta) — usually the bulk of a "long" list.
- A huge single day is usually the release upgrade; judge the steady-state per-day rate after it.

## Options to offer

A: `sudo apt upgrade` the prepared batch now so the next reboot is normal. B: `gsettings set org.gnome.software download-updates false` (security still auto-installs). C: `sudo apt autoremove` for old kernels (~500 MB each).

Ask what is actually bothering the user before going deep: the update question can be a proxy for a different symptom (e.g. display glitches they suspect updates caused).
