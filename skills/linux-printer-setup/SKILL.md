---
name: linux-printer-setup
description: "Use when a printer won't work on Linux (CUPS, mDNS)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cups, printer, ipp, airprint, avahi, mdns, ubuntu, linux]
    related_skills: [systematic-debugging, upstream-bug-reporting]
---

# Linux printer setup and diagnosis

## When to Use

A printer doesn't show up, can't be added, or won't print on a Linux host. Also covers `.local` hostnames that won't resolve.

Network printers fail on Linux at one of four layers: device, discovery, name resolution, or CUPS queue. Check each in one batched command before changing anything. USB is rarely needed; prefer the network path.

## Procedure

1. **State snapshot (one call):**
   ```bash
   systemctl is-active cups cups-browsed avahi-daemon; lpstat -t; lpinfo -v; ip -4 addr | grep inet
   ```
   `lpinfo -v` lists discovered `dnssd://` / `socket://<ip>` URIs; that gives the printer's IP and model. `lpstat: No destinations added` means discovery works but no queue exists.
2. **Device health:** ping the IP, probe ports 631/9100, then
   ```bash
   ipptool -tv ipp://<ip>/ipp/print get-printer-attributes.test | grep -iE 'status|state|document-format|urf|make-and-model'
   ```
   `image/urf`, `application/PCLm` or `pwg-raster` in document-format-supported means IPP Everywhere / AirPrint works, so no vendor driver is needed.
3. **Permissions:** `id`. Membership in `lpadmin` lets you run `lpadmin` without sudo, so you can create the queue yourself.
4. **Add the queue (driverless):**
   ```bash
   lpadmin -p NAME -D "Desc" -E -v 'ipp://<host-or-ip>/ipp/print' -m everywhere && lpadmin -d NAME
   lpoptions -p NAME -l | head   # confirms PPD was generated
   ```
   Try the dnssd/`.local` URI first. If lpadmin fails with `Unable to connect to <x>.local:631: Name or service not known`, name resolution is broken: use the IP URI so printing works now, then diagnose resolution (see reference). Tell the user to reserve the IP in the router's DHCP, because the IP-based queue stops working if the printer's address changes.
5. **Verify:** `echo test | lp -d NAME`, then `lpstat -W completed -o NAME`. "Completed" only proves CUPS handed the job off. Ask the user to confirm that paper actually came out.

## Pitfalls

- `cups-brf must be called as root` and `hpfax: Failed to create /var/spool/cups/tmp/.hplip` in the logs are noise from `lpinfo` backend scans. Don't chase them.
- A running `cups-browsed` that never creates a queue usually points to the same `.local` resolution failure. Say this is unverified unless you actually tested it.
- With the SOA heuristic active, a `dnssd://` queue URI is accepted by lpadmin but the job then stalls with `Unable to locate printer "X.local"`. Avahi D-Bus still resolves the name, so don't trust lpadmin's acceptance; send a test job.
- When the router can't do DHCP reservations, the durable fix is the mdns.allow + `mdns4` host fix plus a `dnssd://` URI. That survives IP changes.
- Fixing nss/mDNS config needs sudo. When sudo isn't available, ship the IP workaround and give the user the exact commands to run, rather than stopping.

## References

- `references/mdns-resolution.md`: why `getent hosts X.local` fails while Avahi resolves it, and the fixes.
