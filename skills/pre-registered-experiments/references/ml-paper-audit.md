# Auditing a published ML method paper (review + weight-level check)

Use when the user asks for a research/review/feedback report on a published method (quantization, pruning, architecture trick) whose authors released code but not checkpoints or full data. The deliverable is a cited report first; a pre-registered Journal study is a second, separate step.

## Source sweep (do all of it before drafting)

1. **Every paper version and successor.** Fetch arXiv HTML for the original AND any follow-up (`/html/<id>vN`), normalize to text in scratch. Follow-ups often state the original's weaknesses more plainly than critics do (e.g. admitting it trailed a baseline).
2. **Code forensics.** `gh api` for repo stats, LICENSE, tree (`?recursive=1`, filter for `.cu|.cuh|.cpp|.triton` to confirm whether a claimed kernel ships), commit history per key file, every issue with comments, merged PRs with diffs. Issues carry the practitioner feedback a bot-walled forum hides.
3. **Peer review.** OpenReview forum: reviews, rebuttals, decision. Build a table: point raised -> authors' answer -> present in camera-ready? Grep the final version for each rebuttal promise (token counts, FLOPs tables, reframed lemmas). Unkept rebuttal promises are a concrete, citable finding.
4. **Competitors' papers for the target's missing numbers.** A rival's comparison table often reports the target's training data size and GPU-hours when the target paper never did. Search the rival's HTML for the target's name.
5. **Company blog / poster pages** for headline numbers (end-to-end tok/s, "Nx smaller") that the paper scopes more narrowly; record which model the headline uses.

## Checks that decide the verdict

- **Headline scope.** Recompute total footprint from each model's `config.json` (vocab, hidden, layers, intermediate, kv heads, tied embeddings): body at the claimed bpw plus FP16 embeddings/lm_head. Headline ratios on small-vocab models collapse on 128k-150k-vocab models; tabulate across current families.
- **Near-chance accuracy.** Compute the chance floor of the reported task mix and report retained accuracy above chance, not raw averages.
- **Train/eval overlap.** Check whether QAT data includes the perplexity eval corpus; note when it is inherited protocol (field-wide, not the authors' trick).
- **Variance.** Grep both papers for seed/std/error bar; small wins with no variance are "cannot tell", not "within noise".
- **Bug claims.** Before printing an implementation-bug claim: read the fix diff, emulate the pre-fix line on random data to quantify the damage, trace the call path (is it on the official load/eval path?), and scope it honestly (blocks outside reproduction vs. affected the published numbers).
- **Reviewer-raised vs new.** Tag every criticism as raised in review (and only partly resolved) or new; never present a reviewer's point as your discovery.

## Weight-level mechanism check (CPU, $0)

- Pull single tensors without downloading the model: read the safetensors index, HTTP range-request the 8-byte header length + JSON header, then range-request the tensor's `data_offsets`; `np.frombuffer(..., float16).astype(float32)`.
- Reimplement the method's initialization from the paper's appendix code, match budgets with the paper's own bits-per-weight formula, compare against the natural baseline (e.g. tiny-rank FP16) at each budget. Report relative Frobenius error and energy captured (1 - err^2).
- Compute the full SVD once per matrix and cache it; a 4096x4096 SVD is minutes on CPU, recomputing it per setting turns one run into hours. Write results line by line so partial output survives a kill.
- State scope plainly: initialization only, N layers, one seed. It checks the mechanism, not end-to-end quality.

## Confirmatory weight-level study (the Journal step)

- **Run the method through the authors' own class**, vendored at a pinned commit, not a reimplementation; a reimplementation that skips one step (e.g. the scaling vectors) produces errors tens of times too large that look like a finding. Patch only import-order breakage, never math.
- **Validation gate before any confirmatory number:** our wrapper must reproduce the authors' released code output (and the paper's synthetic figure, e.g. a break-even point within a registered tolerance) before anything counts.
- **Two arms:** arm A = released recipe verbatim (e.g. randomized `svd_lowrank`, niter=2); arm B = the same code with one registered deviation (exact truncated SVD). Put the paper-reproduction bar on arm A and the primary results on arm B.
- **Speed-only caches are allowed post-freeze** if keyed by value (shape + a few element checksums) and bit-identical: the authors' code often recomputes the same SVD per budget/arm/seed. Log it as tooling-only.
- **Baselines at the method's ACTUAL effective bits**, not the nominal budget: FP16 tiny-rank and int8/4/3/2-quantized low-rank factors. A win over FP16 alone is a weak claim; the int baselines decide whether "best in extreme regimes" survives.
- **Every layer of every registered model**, models and their HF commit SHAs pinned in one `units.py`; pilot layers declared and excluded from counts. Time one real unit per matrix shape before quoting a compute estimate (seeds + arms multiply it), and put the revised estimate in the change log.
- Pull tensors by safetensors range request with the SHA in the URL and retries; no full model download needed.

## Costing a full reproduction

Price end-to-end retraining from a published GPU-hour figure (the target's or a rival's table) times rental rate before quoting the user any number; QAT on a 7B model runs to ~100+ H100-hours, far above a per-action cap. Offer the smallest supported model as the affordable variant and ask before spending.

## Report shape

Bottom line (what is real / overstated / usable today / verdict) -> coverage note (one line per blocked source) -> reviewer table -> method -> reported results -> own check -> strengths / weaknesses -> code and reproducibility table -> competitors -> feedback to authors and to practitioners. Competitor claims that rest only on vendor announcements are labelled as vendor claims; cross-report benchmark comparisons with different shot counts are footnotes, not head-to-heads.

## From report to Journal piece

The report itself is a literature review, not a Journal article. The Journal version pre-registers falsifiable hypotheses about the method's central theory on models the authors did not test (e.g. per-layer break-even holds in >= 95% of layers across 4 current families), runs them, and demotes the review to related work. Send the authors a right-of-reply email (user approves the draft) before publishing a named critique.
