# .local name resolution (nss-mdns / Avahi)

## Isolate the failing layer

- Avahi without avahi-utils: query the daemon socket directly:
  ```bash
  printf 'RESOLVE-HOSTNAME-IPV4 host.local\n' | python3 -c "import socket,sys;s=socket.socket(socket.AF_UNIX);s.connect('/run/avahi-daemon/socket');s.sendall(sys.stdin.buffer.read());print(s.recv(200))"
  ```
  Or use D-Bus: `gdbus call --system --dest org.freedesktop.Avahi --object-path / --method org.freedesktop.Avahi.Server.ResolveHostName -- -1 0 host.local 0 0`.
- System path: `getent hosts host.local`. If Avahi resolves the name but getent fails, the break is in nss-mdns.
- `strace -f -e trace=connect getent hosts host.local`. If it shows connects to port 53 (resolv.conf nameserver) and none to the Avahi socket, nss-mdns has disabled itself.

## The SOA heuristic (most common cause)

In `minimal` mode, or when `/etc/mdns.allow` is absent, nss-mdns queries unicast DNS for `SOA local.`. If any SOA comes back, it treats `.local` as a real DNS domain and steps aside. This is documented, intended behavior, not a bug: it's in the nss-mdns README, the ArchWiki Avahi page, and Launchpad 327362.

Check where the SOA comes from:
```bash
resolvectl dns <iface>; dig +short @<router> SOA local.; dig +short @<router> version.bind CH TXT; dig +short @1.1.1.1 SOA local.
```
The usual culprit is a router running dnsmasq with its LAN domain set to `local`. It answers `localhost. root.localhost.` and also pushes `search ... local` via DHCP.

## Fixes

1. Router (fixes every device on the network): change the LAN domain name from `local` to `lan` or `home.arpa`.
2. Single host (sudo): create `/etc/mdns.allow` containing `.local.` and `local.`, AND change `mdns4_minimal` to `mdns4` on the `hosts:` line in `/etc/nsswitch.conf`. The minimal variant ignores mdns.allow, so the file alone does nothing.
