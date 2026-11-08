# Driving a Windows laptop node from the Hermes host over SSH

Use when a task needs to run or test something on Karl's Windows 11 laptop (a Tailscale node, OpenSSH for Windows on port 22). This is plain remote exec, not a Hermes gateway link.

## Access

1. Check it is online first: `tailscale status | grep -i windows`. It is often offline; say so instead of retrying.
2. Key: `~/.ssh/id_ed25519_laptop` (comment `hermes->laptop`). Always pass `-i ~/.ssh/id_ed25519_laptop -o IdentitiesOnly=yes -o BatchMode=yes -o LogLevel=ERROR`; LogLevel hides the harmless post-quantum KEX warning.
3. If the key is refused, never ask for or type the Windows password. Hand Karl an elevated PowerShell block that appends the pubkey to BOTH `C:\ProgramData\ssh\administrators_authorized_keys` (with `icacls ... /inheritance:r /grant Administrators:F /grant SYSTEM:F`, because Windows sshd ignores the per-user file for admin accounts and rejects a loosely permissioned admin file) AND `%USERPROFILE%\.ssh\authorized_keys`, and prints `$env:USERNAME`. Tell him what the key grants and how to revoke it (delete the line).
4. Seed known_hosts with `ssh-keyscan -T 5 <ip> >> ~/.ssh/known_hosts` once; `Host key verification failed` before that is expected.

## Running things

- **Never inline non-trivial PowerShell through ssh.** The remote shell is cmd, which mangles `$_`, `['...']` and nested quotes. Write a `.ps1` locally, `scp` it, run `powershell -NoProfile -ExecutionPolicy Bypass -File %USERPROFILE%\<dir>\x.ps1`.
- **SSH sessions are non-interactive (hidden desktop).** To start a GUI app on Karl's visible desktop: `schtasks /create /tn <name> /tr "<exe>" /sc once /st 23:59 /it /f` then `schtasks /run /tn <name>`. Confirm with `Get-Process <name> | Select Id,SessionId` (SessionId 1 = console). Delete the task afterwards.
- **`/it` tasks can silently not run.** Sometimes `schtasks /run` returns SUCCESS and `Last Result: 0`, but no process ever appears. In that state even a PowerShell wrapper that only writes a log file never runs, although the desktop is unlocked and Karl is active in session 1. Don't keep retrying. Run CLI/engine checks from the SSH session (`Start-Process -PassThru` works there, and loopback ports are shared), and ask Karl to double-click the exe for the visible-desktop part.
- The laptop's cmd output is Swedish (e.g. `Det går inte att hitta filen.` = file not found).
- Copy files with `scp ... file karl@<ip>:<relative-path-under-home>` and verify with `Get-FileHash` against local `sha256sum`.
- Probe local HTTP services with `Invoke-WebRequest -UseBasicParsing` and listeners with `Get-NetTCPConnection -State Listen -LocalPort <p>`.
- Things only Karl can verify: tray icons, window appearance, speaker output. Ask him for those explicitly instead of claiming them.

## Cleanup

Remove the scheduled task and any helper scripts when done; leave the app he is using running. Report what stays (the key, the binary).
