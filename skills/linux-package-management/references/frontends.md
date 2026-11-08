# Package-management frontends on Ubuntu GNOME

## Coverage table

| Frontend | deb | snap | Flatpak | Updates all three | Notes |
|---|---|---|---|---|---|
| GNOME Software + `gnome-software-plugin-{deb,snap,flatpak}` | yes (PackageKit) | yes | yes | yes (snaps also self-refresh via snapd) | Already installed, needs no extra packages. One entry per app, with a source dropdown on the app page. Set format order with `gsettings set org.gnome.software packaging-format-preference "['flatpak','snap','deb']"` |
| Ubuntu App Center (snap `snap-store`) | yes | yes | **no** | no | Monolithic Flutter app with no plugin system. Flatpak is only an open upstream request. Pair it with the Flatpak timers if Karl wants it |
| Update Manager | apt only | no | no | no | update-notifier still pops up on GNOME |
| KDE Discover (`plasma-discover plasma-discover-backend-flatpak plasma-discover-backend-snap`, `--no-install-recommends`) | yes (packagekit-backend) | yes | yes | yes | About 169 packages / 126 MB on GNOME. Its update notifier doesn't autostart on GNOME. Karl rejected it for its weight |
| bauh | yes | yes | yes | yes | Unmaintained: its last release predates Python 3.14, and it has open bugs about failing to start and about snaps not showing. Don't recommend it |
| mintinstall / Pamac | - | - | - | - | Mint and Arch only |

CLI that updates everything (no extra tool needed):
```bash
sudo apt update && sudo apt full-upgrade && sudo snap refresh && flatpak update -y
```
For unattended Flatpak updates, use `../templates/flatpak-update-timers.md`.

## Checking GNOME Software without the GUI

```bash
gnome-software --quit; sleep 2          # a running service instance hides cmd output
/usr/libexec/gnome-software-cmd --show-results --refine-flags origin installed > inst.txt
grep '^bundle-kind' inst.txt | sort | uniq -c    # expect flatpak, package AND snap
/usr/libexec/gnome-software-cmd --show-results --refine-flags origin search firefox | grep -E '^(unique-id|state)'
```
- The verbs are `installed`, `updates`, `search`, `sources`, `refresh`, `get-alternates` (not `get-installed`). Without `--show-results` the command prints nothing.
- **Always pass `--refine-flags origin`.** Without it, no refine step runs (the log says `No apps to refine`), snaps and debs never get an installed state, and they are dropped as `app invalid as state unknown`. Only Flatpaks survive. That looks exactly like a broken snap plugin but is a harness artifact, because the GUI always refines. `--refine-flags id` also returns nothing; `origin` works.
- `updates` printing nothing while `apt list --upgradable` is non-empty is the same artifact, so don't read it as "updates broken".
- Normal log noise: `disabling dpkg as conflicts with packagekit`, `packagekit failed to list apps: Unsupported query`, `updates-shell: failed to get upgrades: no plugin could handle listing distro upgrades`.
- Plugin source for the installed release: `https://gitlab.gnome.org/GNOME/gnome-software/-/raw/<version>/plugins/snap/gs-plugin-snap.c`. In that file, `list_apps` only builds bare apps (`snap_to_app`). Installed/available state is set later, in the refine path (`get_snaps_cb`).
- Open-issue search: `curl -s 'https://gitlab.gnome.org/api/v4/projects/GNOME%2Fgnome-software/issues?search=snap&state=opened&per_page=40'`. Ubuntu-side bugs are tracked at `bugs.launchpad.net/ubuntu/+source/gnome-software`.

## Checking Discover

```bash
plasma-discover --listbackends            # expect snap-, packagekit-, flatpak-backend
timeout 25 plasma-discover --mode Update  # smoke launch; rc=124 (timeout) = it stayed up
```
Ignore these launch messages: `Couldn't find the backend: "kns-backend"`, `No distro component found for "com.ubuntu.ubuntu"`, and the portal's `Could not register app ID`.
