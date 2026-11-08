---
name: linux-package-management
description: "Use when managing Ubuntu apps across apt, snap, Flatpak."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [apt, snap, flatpak, ubuntu, gnome-software, discover, packagekit, pkexec]
    related_skills: [linux-crash-diagnosis, computer-use]
---

# Linux package management (apt + snap + Flatpak)

Use this skill on Karl's Ubuntu desktops (geekom runs Ubuntu 26.04 GNOME on Wayland) when he wants an app installed, removed, updated, or de-duplicated, or wants one tool to manage every package format.

## Procedure

1. **Inventory every format in one batched call** before you say anything:
   ```bash
   dpkg -l | grep -Ei '<app>'; snap list 2>&1 | grep -Ei '<app>|Name'
   flatpak list --columns=application,version,installation; flatpak remotes
   apt-cache policy <app>        # on Ubuntu, some debs are only transitional snap installers (version like 1snap1)
   ```
2. **For duplicates, work out which copy is older and where the user data lives:**
   - Install age: `snap info <snap> | grep -E 'installed|refresh-date'`, `flatpak info <id> | grep Date`, and `stat -c %w /var/lib/flatpak/app/<id>` (creation time of the Flatpak install).
   - Data: snaps keep it in `~/snap/<snap>/`, Flatpaks in `~/.var/app/<id>/`. Check with `du -sh`. If the folder is missing, that copy has never been launched.
   - Default handlers: `xdg-settings get default-web-browser`, `gsettings get org.gnome.shell favorite-apps`.
3. **Ask before removing** whenever the copy you're removing holds the profile. Offer three options: migrate the data, keep that copy, or remove it and start fresh. Tell Karl the size and what is inside (bookmarks, logins). Never remove profile data without his explicit choice.
4. **Get root through a desktop prompt.** `sudo -n` fails because sudo needs interactive authentication. Use `pkexec`, and tell Karl a password prompt is about to appear before you run it:
   ```bash
   export DISPLAY=${DISPLAY:-:0}; timeout 170 pkexec /usr/bin/snap remove --purge <snap>
   timeout 580 pkexec env DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -y --no-install-recommends <pkgs>
   ```
   Wrap pkexec in `timeout` so a prompt nobody answers can't hang the turn. Give the absolute binary path. `snap remove --purge` also deletes `~/snap/<snap>`.
5. **Repair integration after a removal.** Run `xdg-settings set default-web-browser <id>.desktop` for browsers, and update the dock favourites if the removed app was pinned.
6. **Verify, then report.** Run `snap list <x>` / `flatpak list` / `dpkg -l`. In the report, say plainly which data was deleted.
7. **Keep Flatpaks updating automatically.** Karl considers Flatpak indispensable. Any setup where his main GUI doesn't cover Flatpak needs the daily timers in `templates/flatpak-update-timers.md`: a system unit with `--system`, plus a user unit with `--user`, because user-installation Flatpaks (RetroArch, some runtimes) are skipped by the system unit. Install the system unit with one `pkexec` call, start both services once, and confirm "Nothing to do" or a clean run in `journalctl` before reporting.

## Diagnosing "frontend X doesn't show format Y"

Work from the bottom up before you recommend replacing a frontend. Each layer takes one command:
1. Is the daemon right? `curl -s --unix-socket /run/snapd.socket http://localhost/v2/snaps` (count results), `flatpak list`, `dpkg -l`.
2. Is the library right? Use the system Python (`/usr/bin/python3`, because the Hermes venv has no `gi`): `gi.require_version('Snapd','2'); Snapd.Client().get_snaps_sync(Snapd.GetSnapsFlags.NONE,None,None)`.
3. Does the frontend's own harness see it **on the same path the GUI uses**? For GNOME Software that means `--refine-flags origin` (see `references/frontends.md`).
4. Only after all three, check the GUI itself (or have Karl look) and read the plugin source for the release that's installed.
If layers 1 and 2 are healthy, suspect your test before the plugin. A test harness that skips a step the GUI always runs will "prove" a bug that doesn't exist, and that is how Karl was sent to install and then purge a 169-package replacement.

## Unified management (one GUI for all three)

See `references/frontends.md`. It has a decision table (GNOME Software, App Center, Update Manager, KDE Discover), the commands for verifying each frontend, and a CLI one-liner that updates everything. In short: GNOME Software, which is already installed, covers deb, snap and Flatpak, and it's the default recommendation. KDE Discover also covers all three, but pulls in about 169 KDE packages (Karl tried it and had it purged). App Center covers only snap and deb. Ubuntu shows one entry per app, and the source (Flathub, Snap, Ubuntu) is chosen from a dropdown on the app page, so seeing a single Firefox entry does not mean the other sources are missing.

## Trimming startup and background services

Karl asks "what is this process, can we disable it, where is the fat" periodically. Answer with measurements and roles, never with a service name alone.

1. **Attribute memory per unit, not per PID**: `scripts/pss_by_unit.py` sums PSS from `/proc/*/smaps_rollup` by cgroup. Use PSS, not RSS: RSS charges every shared page to every sharer, so Electron/Chromium children inflate the total several-fold.
2. **Identify each named thing before recommending anything.** A process name in the startup list is often not a process: `gnome-software-local-file-*.desktop` entries are MIME handlers for opening a `.snap` file, and the real 200 MB+ process is `gnome-software --gapplication-service`, started by `gnome-session-services.target` (`systemctl --user list-dependencies`).
3. **Check the dependency before masking.** `goa-daemon` (GNOME Online Accounts) costs single-digit MB and is D-Bus activated, so blocking it only breaks Settings > Online Accounts. Small and load-bearing: leave it and say why.
4. **Per-user autostart is the reversible lever**: copy the `/etc/xdg/autostart/*.desktop` entry into `~/.config/autostart/` and append `Hidden=true` + `X-GNOME-Autostart-enabled=false`, rather than editing or deleting the system file.
5. **Say what still delivers the removed feature.** Before disabling an updater frontend, name the replacements (unattended-upgrades + update-notifier, the Flatpak timers, snapd) so the answer is not "no more updates".
6. **Verify the app still works** by launching it once after masking its service, then report launchers as "opens, exits clean", not "works".
7. **Report before/after in one number each** (available RAM, per-unit PSS). Karl wants the delta, not the process of measuring it.

## Pitfalls

- Before you call an install "older" or "duplicate", check `apt-cache policy`. On Ubuntu the `firefox` deb is a transitional package that installs the snap, so `apt install firefox` brings the snap back.
- `ubuntu-desktop-minimal` recommends `firefox`. Removing the snap is safe (it's a recommends, not a depends), but a later upgrade with recommends enabled can reinstall it. Offer an apt pin if Karl wants it permanently gone.
- Simulate large installs first: `apt-get -s install --no-install-recommends ... | grep -c ^Inst`, plus a size estimate from `--print-uris`. Put the package count and size in the question to Karl. KDE tools on GNOME pull about 170 Qt/KF6 packages.
- If a GUI was only launched and its screens were never checked, report it as "launches without error", not "works". `computer_use` sees no windows on Wayland unless the gateway was started with Wayland support enabled, so ask Karl to check the screen himself.
- When Karl asks to "build a plugin" for a frontend, first check whether the frontend has a plugin architecture at all. Ubuntu App Center (snap `snap-store`) is a monolithic Flutter app that talks to snapd/PackageKit directly, so Flatpak support would mean maintaining a fork. Say so and give the cost instead of starting.
- To purge a frontend completely, run `apt-get purge --autoremove <pkgs>` (one pkexec call), then remove its home-dir state (for Discover: `~/.config/discoverrc`, `~/.cache/discover`) and its dock entry.
- GNOME Software merges sources into one entry only when the AppStream IDs match. A snap with no `common-id` gets the fallback ID `io.snapcraft.<name>-<snap-id>` and shows up as a separate entry. Firefox's snap has none (snapd `/v2/find?name=firefox` returns `common-ids: null`), so Flathub Firefox and the snap appear twice. That's expected behavior, not a GS bug. The fix belongs upstream in canonical/firefox-snap (`common-id: org.mozilla.firefox`). That repo has GitHub issues disabled. Reported as PR canonical/firefox-snap#183 (vhsgreed, base `nightly`, opened 2026-10-30). Check its status before re-raising. That repo's README asks for PRs against `nightly`, not the default `stable` branch.
- To test GNOME Software search merging, compare a raw search (`gnome-software-cmd --show-results --refine-flags origin search <q>`, which does no dedupe, so look at the `id:` lines) with the deduped shell provider (`gdbus call --session --dest org.gnome.Software --object-path /org/gnome/Software/SearchProvider --method org.gnome.Shell.SearchProvider2.GetInitialResultSet "['<q>']"`). GIMP is the reference case where the IDs match. After about 20 store queries in a few minutes, the Snap Store starts returning `too many requests` or timeouts, so space out snap searches and don't loop over many app names.
- **Stopping GNOME Software's background service (~225 MB)** is set up as: `systemctl --user mask gnome-software.service` (the session target `Wants=` it), a copy of `org.gnome.Software.desktop` in `~/.local/share/applications` with `DBusActivatable=false` so the app still opens directly, and its search provider listed in `org.gnome.desktop.search-providers disabled`. Updates still arrive through unattended-upgrades + update-notifier, the Flatpak timers and snapd. `gnome-software-local-file-*.desktop` entries are just MIME handlers, not processes. To undo: `systemctl --user unmask`, then remove the desktop copy.
- Karl is gear- and tool-averse ("Mr Gadget"). Fix or reuse what is installed before you suggest adding a new tool such as topgrade, and give the cost when you do suggest one.

## References

- `references/frontends.md`: what each GUI frontend covers, other all-in-one candidates, and the commands to check them.
- `scripts/pss_by_unit.py`: PSS per systemd unit — finds which services are actually fat.
- `templates/flatpak-update-timers.md`: systemd units for daily system and user Flatpak updates, with install and verify commands.