# Writing up and reviewing an experiment article

Use when turning a lab record (PLAN.md + scorer outputs) into an article, revising it after review, or preparing the repo for publication.

## Drafting

1. Draft in `journal/<topic>-draft.md` inside the lab repo, marked DRAFT with a version and "written by the assistant; author to rewrite in own voice". Belief/voice text is the user's; ship nothing until they rewrite.
   - Voice-pass scope: the author's decisions are the title (offer 3-4 alternatives), "in short", the abstract's framing sentences, the introduction's argumentative stance, discussion interpretation, and the disclosures byline. Method, results, statistics, hypotheses table and change log are transcription from committed outputs: the author verifies them, never rewrites them. Hand the author a section-by-section map so a voice pass reads as yes/no on wording, not a rewrite.
   - Calibrate to the author's own writing before rewriting in their register: their published pieces, plus unpublished drafts in their site tree (these are the honest voice, unedited by reviewers). Match sentence rhythm, number handling and disclaimer habits; carry their punctuation conventions even where a generic style guide would differ.
   - For agentrecourse.org the house article format is: Version line, Author (accountable), Contributions (the AI agent's role under direction; agents are never authors on research articles), TL;DR; `## Sources` as `[n] url - title` lines with a `.tiers.json` beside the source file.
2. Structure: one-paragraph "in short", abstract, introduction, terms (define every coined word at first use: run, trigger, group, range, width, lower bound, tail, estimated size), hypotheses table (claim, bar, registering commit, ID prefixes explained), method, results, discussion with limits as bullets, disclosures, data/code, change log, open items for the author.
3. Every number must trace to a committed output file. Before writing a number from memory or an earlier chat message, re-run or grep the `.out` file: earlier summaries drift (e.g. a count of groups worse than baseline was off by one). Run-output directories are usually gitignored for size; force-add the scorer's small machine-readable outputs anyway (`git add -f out/*/score.json`) so every article number resolves in the public repo.
4. Report EVERY registered hypothesis in Results with its numbers, including failed and exploratory ones. A hypothesis mentioned only in passing in Discussion reads as buried.
5. Abstract claims must match the registered verdicts exactly. A secondary/amended analysis never appears as a replication success; "not evaluable" stays "not evaluable".
6. Scope claims to what was tested: "none of the tested inputs narrowed it out of sample", never "the information does not exist". Pair every ceiling/bound number with its exact condition and say which numbers are in-sample (optimistic) vs held-out.
7. Name the measured quantity honestly: list-price-equivalent cost (with price snapshot date), estimated tokens (never converted to dollars), a 90% lower bound (not a "floor"/guarantee).
   - Validate the pricing model against real billing when any billed data exists: Hermes `agent.log` lines carry `id=gen-...` per OpenRouter call; `GET https://openrouter.ai/api/v1/generation?id=<gen>` (management key in `~/.secrets/OPENROUTER_MANAGEMENT_KEY`) returns billed `usage` plus `native_tokens_prompt/completion/cached`. Pre-register a bar (median billed/estimate in [0.95,1.05], >=90% within 10%), require exact native-token match as the join check, split by cache share, keep per-call rows local, publish aggregates only, and scope the claim (validates the pricing model on that model/account, not other price entries).
8. Put n=1 material (the user's own logs) in a labelled box, not the evidence chain.
9. Convert pass counts into coverage: "5/15 groups" -> share of test sessions and spend those groups cover. Compare a grouped bound against model-only and global baselines both pooled and per group; grouping often helps per-group calibration, not pooled coverage.
10. One sentence on multiplicity: expected chance passes under the null vs observed; 0/N fails need no correction.
11. Search for adjacent published work before finalizing and cite it (arXiv + the datasets used); a missing related-work section is the first thing both LLM and human reviewers flag. Check that claims contradicting or matching published papers say so explicitly.

## Responding to a review (including LLM-generated reviews)

- Treat an LLM review as a checklist, not a verdict: verify each factual claim against the data before acting. Typical errors: misreading a tail rate as an overall rate, demanding sensitivity analyses that are invariant by construction, "leakage" that is the intended design.
- Sort points into: drafting errors (fix), analyses on data on disk (run, label post-hoc in PLAN.md), new analysis (run only if it changes a claim), and rejects (state why in the change log).
- Log supplementary analyses in PLAN.md as POST-HOC, descriptive, before writing them into the article.
- End the revision with a change log mapping each review point to what changed, including the points not changed and why.
- Two LLMs (writer + reviewer) share blind spots; the remedy is re-running numbers from scripts and real review by people who can run the code, which requires publishing the repo.

## Preparing the repo for publication

1. Create the GitHub remote PRIVATE first (`gh repo create <owner>/<repo> --private --source . --remote origin --push`); the user approves going public.
2. Add README (what each file is, environment, exact run order, what is not reproducible from public data), pinned `requirements.txt` from the venv's actual versions, LICENSE.
3. Scan full history for secrets: `git log --all -p | grep -E -i "sk-or-|sk-ant|ghp_|password|BEGIN (RSA|OPENSSH)|api[_-]?key\s*[:=]"`.
   - Pitfall: when files must be stripped from history (personal logs), run git-filter-repo WHILE the repo is still private, then remap every commit hash cited in docs from `.git/filter-repo/commit-map` and verify each resolves (`git cat-file -e <hash>`) — the cited hashes ARE the pre-registration evidence, and a rewrite silently invalidates every one.
4. List every committed file (`git ls-files`) and check derived files for data rows or message text; disclose derived samples in the README.
5. Before going public, raise with the user: author email in commit history (`git log --format='%an <%ae>' | sort | uniq -c`; offer a noreply rewrite while still private), and scripts that reveal the structure of their personal logs.
6. Fill the article's data/code section with URL + commit hash only after the push.
7. Updating a published article: bump the version line, append a change-log entry saying what changed, update the registry's cited commit (the repo hash whose text the page shows), rebuild, redeploy. The cited commit is evidence; an updated article pointing at the old hash is a broken reproduction path.
8. A new registered round after publication changes the summary layer too: add the hypotheses-table row and results section, AND update abstract, TL;DR, discussion, limits, and the listing summary/test count. A result added only as a section leaves the headline telling the old story. Grep the draft for the round ID and for the old test count before redeploying.

## Preprint (arXiv) packaging

When the article crosses over to arXiv (or another preprint venue):

1. A box with no TeX toolchain: `python3 -m venv ~/.venvs/arxiv && ~/.venvs/arxiv/bin/pip install pypandoc_binary` ships pandoc, and the tectonic release binary (musl build, ~20 MB) compiles LaTeX with no TeX Live install.
2. `pandoc --standalone --toc --number-sections -V geometry:margin=1in -V fontsize=11pt --resource-path=. main.md -o main.tex`, figure PNGs copied next to the .tex so `\includegraphics` resolves; compile `tectonic main.tex`; sanity-check page count and figure count before packaging.
3. Submit the LaTeX SOURCE tarball (main.tex + figures), not the PDF alone: arXiv auto-compiles TeX and treats PDF-only submissions as second class.
4. Metadata defaults for these studies: primary category cs.CL with cs.LG cross-list, license CC BY 4.0 (matches the repo's data licence), comments field carrying the repo URL + article URL.
- Pitfall: the arXiv title and abstract must match the published article's exactly; a drifted abstract creates two citable versions of the same claim.
