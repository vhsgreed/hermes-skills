---
name: backup-and-recovery
description: Use when backing up machines or recovering lost data.
version: 1.0.0
author: Karl Sundström
license: MIT
metadata:
  hermes:
    tags: [ops, backup, disaster-recovery, rsync, postgres, verification]
    related_skills: [agent-security-posture]
---
Make backups trustworthy, then recover from loss. A backup that logs success is not a backup until its artifact has been opened and checked.

## When to Use

- Setting up, repairing, or auditing a backup job on any machine.
- Something was deleted, wiped, corrupted, or is believed lost.
- A log line claims a backup or export succeeded and the result must be trusted.
- Changing what a mirror copies, where it writes, or how often it runs.
- Before any destructive repair on a machine that may still hold the data.

Do not use for one-off copies of a working file, or for shipping a deliverable to a user.

## Always-on gates (every instance)

1. **Verify the artifact, never the log.** Open the produced file and confirm it is what it claims to be (magic bytes, entry count, an actual restore-list). A job can print `OK (N bytes)` and the artifact can be gone one second later. The log records intent; the artifact records fact.
2. **Recover before you repair.** Before accepting a loss or running anything destructive, establish what is still recoverable and where. Most reported data loss is a reset or a move, not an erasure. The emotional cost of a loss is almost never proportional to the bytes, and checking first is cheap.
3. **Establish the architecture before judging a job.** Confirm which machine each job runs on and whose home directory it copies. A path that looks identical across hosts (`/home/karl`) is not the same tree.
4. **Nothing destructive against a recovery copy until it is preserved or confirmed redundant.** A mirror with `--delete` aimed at the only surviving copy of lost data will destroy it.

## Procedure

1. **Map the topology first.** For every job record: which host runs it, the source path, the destination path, the schedule, the transport (local, ssh, sudo), and what it excludes. Write it down as a table before changing anything. Topology errors are the costliest and the least visible.
2. **Find the log that the job actually writes.** Jobs with near-identical names often write to different files. Read the script, not the filename, to learn where its log lands.
3. **Check the job is reaching its destination at all.** Compare file count and total size of source and destination, then diff the top-level entry names. A destination that is a small fraction of the source has never completed a full pass.
4. **Test the exclusions against the failure the job reports.** An unreadable source path forces a partial-transfer exit and, with `--delete` in play, silently disables deletion for that run. The mirror then accumulates stale copies without ever noticing.
5. **Run the job manually and read the log tail.** Assert the exit code is 0 AND the artifact exists AND the artifact validates. All three.
6. **Schedule on a cadence matched to what would be lost.** A machine holding the only copy of working data is not a weekly job.

## Pitfalls

- **An IO error during rsync silently disables `--delete`.** rsync reports `IO error encountered -- skipping file deletion` and still exits non-zero, but the real damage is that the destination stops mirroring and starts accumulating. Fix the unreadable path or exclude it explicitly; do not accept the exit code as the only signal.
- **Never write a generated artifact inside the mirror's destination tree.** The same `--delete` pass will remove it because it does not exist in the source. Dump targets, checksums, and manifests live beside the mirror, not inside it.
- **A passwordless sudoers rule scoped to an exact command does not permit the checks around it.** A pre-flight probe with a different binary fails and makes the real step look unavailable forever. Either grant the probe too, or skip the probe and let the real command report its own outcome.
- **Never mirror a live database data directory.** It produces a torn copy that cannot be restored, and container-owned directories are often unreadable to the invoking user. Use a logical dump, and confirm it is a real archive before trusting it.
- **Exclude transient churn from mirrors.** Rolling config snapshots and socket files vanish mid-run and raise vanishing-file warnings that mask real failures. A quiet log is a diagnostic asset.
- **`--delete` against the only copy of recovered data is the one mistake that makes the loss real.** Preserve it first, then mirror.
- **Dry-run the mirror (`rsync -an --delete --itemize-changes`) before adding retention or changing a job.** Count `*deleting` lines per top-level dir: a large pending deletion (a source dir already gone) means the next nightly run wipes the only copy. Snapshot it first, then ask the user whether the deletion was intended.
- **Keep the longer-retention copies on a different physical drive from the daily mirror,** and promote only from a clean (exit 0) daily, so a partial run never becomes the weekly.

## Verifying an artifact is genuine

| Artifact | Check |
|---|---|
| PostgreSQL custom dump | magic bytes `PGDMP`; list its contents with a restore tool |
| Plain SQL dump | contains `CREATE TABLE` / `COPY` statements, not an error page |
| File-tree mirror | file count and total size within expected range of source; spot-check three paths that changed today |
| Archive | opens and lists entries without error |
| SQLite copy | `PRAGMA integrity_check` returns `ok` |

Any artifact that passes the log but fails this table was never produced.

## References

- `references/multi-machine-backup-map.md` — how to lay out a backup map across several machines, and the topology mistakes that make a job silently back up the wrong tree.
