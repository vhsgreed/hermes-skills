# Daily Flatpak auto-update (system + user)

You need both units: `flatpak update --system` skips user-installation refs, and `--user` skips system refs. `Persistent=true` catches up after the machine was off. No polkit rule is needed: the system unit runs as root, and the user unit only touches `~/.local/share/flatpak`.

`flatpak-update.service` (system; the user copy swaps `--system` for `--user`):
```ini
[Unit]
Description=Update system-wide Flatpaks
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/flatpak update --system -y --noninteractive
Nice=10
IOSchedulingClass=idle
```

`flatpak-update.timer` (the user copy uses `WantedBy=default.target`):
```ini
[Unit]
Description=Daily system-wide Flatpak update

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

Install (write both files to `$TMPDIR/fpk/` first):
```bash
mkdir -p ~/.config/systemd/user
sed -e 's/system-wide/per-user/;s/--system/--user/' $TMPDIR/fpk/flatpak-update.service > ~/.config/systemd/user/flatpak-update-user.service
sed -e 's/system-wide/per-user/;s/timers.target/default.target/' $TMPDIR/fpk/flatpak-update.timer > ~/.config/systemd/user/flatpak-update-user.timer
systemctl --user daemon-reload && systemctl --user enable --now flatpak-update-user.timer
export DISPLAY=${DISPLAY:-:0}; timeout 170 pkexec /bin/sh -c "install -m644 $TMPDIR/fpk/flatpak-update.service $TMPDIR/fpk/flatpak-update.timer /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now flatpak-update.timer && systemctl start flatpak-update.service"
systemctl --user start flatpak-update-user.service
```

Verify:
```bash
systemctl list-timers flatpak-update.timer --no-pager; systemctl --user list-timers --no-pager | grep flatpak
journalctl -u flatpak-update.service -n 4 -o cat; journalctl --user -u flatpak-update-user.service -n 4 -o cat
```
Either "Nothing to do." or a list of updated refs, followed by "Deactivated successfully", means the unit works.

On geekom these are installed as `/etc/systemd/system/flatpak-update.{service,timer}` and `~/.config/systemd/user/flatpak-update-user.{service,timer}`.
