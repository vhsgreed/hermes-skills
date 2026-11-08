# Multi-machine backup map

A map is the deliverable of the first step, not a nicety. Draw it before touching a
single job.

## The table to produce

| Job | Runner host | Source | Destination | Transport | Schedule | Excludes |
|---|---|---|---|---|---|---|
| e.g. server tree | server | /home/svc | /mnt/bk1/home-svc | local sudo | daily 02:15 | caches, live db dirs |
| e.g. workstation tree | workstation | /home/me | server:/mnt/bk2/workstation | ssh | daily 03:45 | caches, transient snapshots |

Fill it from the crontabs and the scripts themselves. Two jobs with similar names and
similar destinations routinely back up different trees on different hosts.

## Topology mistakes that make a job silently back up the wrong tree

- **Same path, different host.** `/home/karl` on the server is the server's home, not
  the workstation's. A job that appears to back up "the workspace" may be copying the
  host it runs on. Confirm with a file count: a few thousand entries against a source
  with a hundred thousand means the job is pointed at the wrong tree.
- **Destination naming that implies a source it does not hold.** If the destination
  directory is named after one machine but a job on another machine writes to a
  sibling directory, one of them goes stale the moment both run. Name destinations
  after what they contain and make the mapping explicit in the table.
- **Two jobs writing to the same destination.** Last writer wins with `--delete`, and
  whichever job's source is smaller eats the other's history.

## Choosing the schedule

Rate is set by what would have to be redone, not by how often the machine changes.

- Machine holding the only copy of work in progress: daily, offset from the other jobs
  so they do not contend for the same disk or link.
- Machine whose data also lives elsewhere and is rebuildable: daily is still cheap;
  weekly is only defensible when nothing unique is on it.
- Database dumps: daily at minimum, with a retention count (7 is a sane floor) and a
  `latest` symlink for scripted restores.

## Mount reliability

Network and external drives are often not mounted when a scheduled job fires. A job
that silently writes to an unmounted path fills the root filesystem and destroys the
run. Keep the mount check, but make the skip unmissable in the log and treat a skip as
a failure worth acting on. Prefer fixed mount entries with a `nofail` option so boot
proceeds without the drive, and verify the drive is present at the job's hour.

## Reading the log

A mirror job should produce exactly one terminal line per run: `DONE ... exit=0`, or a
`FAIL` line that names the exit code and says to investigate. Anything that reports a
non-zero code as `DONE` has hidden a failure. Transient vanishing-file warnings are
noise caused by churn directories and should be excluded rather than tolerated.
