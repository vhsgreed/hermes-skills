# Sanitising a personal pipeline for a public repo

Open-sourcing here means making the code public, not marketing it. The value is version control plus a portfolio piece; an honest README is enough.

## Checklist, in order

1. **Grep for personal strings first:** `grep -n -i -E "<name>|<own domains>|<email local-part>|<hostnames>|/home/<user>|outreach|hermes" script.py`. Every hit is either config or a comment to rewrite.
2. **Move personal settings to env vars** with a common prefix (`RD_*`): recipient, sender, archive dir, binary paths (`shutil.which` then a sane default), model names, base URLs, the audience line in prompts. Refuse to send when no recipient is set.
3. **Secrets:** read the API key from the environment, else from a dotenv path named by an env var. Never hard-code the agent's own `.env` path, which also leaks the toolchain.
4. **Comments:** keep the mechanism (why cron needs absolute paths, why DMARC fails on a foreign From), drop the business strategy, machine names and incident dates.
5. **User-Agent:** point it at the public repo URL instead of a private brand.
5b. **Optional sibling tools** (indexers, search helpers): skip gracefully when the path does not exist.
6. **Move backups and caches out:** `.bak*`, `__pycache__`, `.dry-run/`, `*.env` into `.gitignore`; move existing `.bak` files to scratch.
7. **License:** copy the MIT text from one of the user's existing repos so the holder line matches.
8. **Secret scan the tree** (gitleaks/trufflehog if installed, else a regex for `sk-or-`, `sk-`, `ghp_`, `AKIA`, `password` plus the personal strings). Start a FRESH repo with one commit so no older history can carry secrets.
9. **Smoke test** the sanitised script in raw/no-model dry-run mode against a scratch dir, and confirm the real archive was not touched.
10. **README:** what is reusable (the method, not the plumbing), the cost and fallback table, the env var table, known weaknesses, and why the author stopped using it if they did. Put the reusable method in `skills/<method>/SKILL.md` so any agent can install it from the repo.
11. **Push** with `gh repo create <owner>/<name> --public --source . --push`, then verify with `gh repo view` and `gh api repos/<owner>/<name>/contents`. Commit author: match the user's other repos and mention it so they can change it.
