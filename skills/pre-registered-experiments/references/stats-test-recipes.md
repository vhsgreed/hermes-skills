# Stats and clustering recipes

Used by pre-registered-experiments step 1-3 scoring scripts.

## Group vs baseline width test (typical shape)

Per group (>= sample-size floor in train AND test): train p10-p90 dollar width `gw`, baseline (e.g. dominant model) train width `mw`. All three clauses usually registered:

1. Point: `gw <= threshold * mw` (threshold typically 0.8).
2. Ratio CI: bootstrap the unit (repos) 200 times, each resample recomputing both widths, ratio `gw_b/mw_b`; the 95th percentile (upper bound of a 90% two-sided CI) must be below `threshold`. Require >= 30 rows on each side inside every resample; skip empty resamples.
3. Coverage: fraction of held-out rows inside the train interval; bootstrap membership flags 500 times; 5th-95th percentile interval must contain the target (e.g. 80%).
4. Multi-baseline comparisons: select the reference baseline from the pooled point estimates and keep that same reference in every bootstrap resample. Choosing the better baseline per resample biases the ratio toward 1 and contradicts the headline ratio.

Pass counted only if ALL clauses hold. Verdict rule (e.g. >= 2 groups) is registered up front too.

## Batch break-even markup (risk premium for fixed-price products)

Question shape: a seller quotes a fixed price per task from a forecast `f(r)` fitted on fit units; true cost `C(r)` is heavy-tailed. How much markup `m` keeps the seller whole?

- Batch break-even: `m_b = sum(C) / sum(f) - 1` over a batch of N tasks. `m_0` on the whole test set is pure forecast bias (no risk premium).
- `m95(N)` = 95th percentile of `m_b` over ~2,000 batches of N drawn with replacement (`rng.integers(0, n, size=(nb, N))`, vectorised). Report N = 1, 10, 100, 1,000: the premium falls roughly with sqrt(N), and that curve is usually the headline (volume, not information, does the work).
- Compare pricing rules (flat per type vs conditioned on a pre-run feature) by the ratio of their m95(N) at a registered N; bootstrap over the split unit for the CI, never refitting prices on resampled test data.
- Use means, not medians, for the price: a price must cover expected cost.
- Descriptive: share of single tasks that still lose money at the batch markup, and Spearman of the feature vs cost (if it is ~0, the conditioned rule cannot beat flat pricing).
- State the unmodelled limit: adverse selection (buyers who know their tasks are expensive choose fixed price), so the measured markups are lower bounds. The batch curve alone is textbook pooling; the adverse-selection test below is the non-obvious part.

## Adverse selection (lemons) test on repeated runs

Needs data with >= 2 runs per task per group.

1. Private share: ICC(1) of log cost (one-way random effects, `n0 = (N - sum n_i^2/N)/(k-1)`), bootstrap over tasks. ICC = share of variation that is about the task, knowable to a repeat buyer.
2. Public share: out-of-sample R^2 of per-task mean log cost on seller-visible features (repo, description-length decile, difficulty) via a cell-mean table with fallback to coarser cells (min 5 fit tasks per cell), split by task id. Private share = ICC x (1 - R^2).
3. Market: buyer estimate = one earlier run (k = 1) or oracle (mean of other runs); buyer takes fixed price p if p <= (1 + lambda) x estimate; iterate p = mean actual cost of takers from (1 + lambda) x pooled mean to a fixed point. Report p*/mean and uptake at lambda in {0, 0.1, 0.3}.
4. Null: shuffle runs across tasks within the group and rerun the market. With a noisy k = 1 estimate uptake drops to ~40-50% on pure noise, so bar the hypothesis on p*/mean (e.g. >= 1.25; null gives ~1.00), not on uptake.

Evidence (SWE-bench Verified, 8 models x 4 runs; own SWE sets): ICC ~0.5-0.6, public R^2 <= 0.18, k = 1 buyer forces p* to 1.4-1.9x mean, oracle buyer unravels the market (~1% uptake).

## Quantiles and band shape

- Use one shared `quantile(xs, q)` helper (sort-based) everywhere; never mix interpolation schemes between scripts.
- Report dollar bands (product numbers) AND multiple bands (x/2 to 2x style). Dollar percentages look lopsided on heavy-tailed cost while multiples look roughly symmetric; both views are true and the discrepancy is itself a finding to state, not smooth over.
- When mean and median diverge materially, say so: the tail is the product-relevant part (caps, warnings), the median is the counter-relevant part.

## k-means at scale

- k-means++ seeding: accumulate `d2 = np.minimum(d2, ((X - c)**2).sum(1))` per chosen center. `min(generator of arrays)` raises an ambiguous-truth ValueError.
- Assignment: never broadcast `(X[:, None, :] - C[None, :, :])**2` for large n — the n x k x d intermediate exhausts RAM. Use the expansion `||x||^2 + ||c||^2 - 2 x.c` with one matmul.
- Fix the flavor explicitly and match the plan's wording: plain (Euclidean, unnormalized centroids) k-means on L2-normalized embeddings is NOT spherical k-means (cosine, centroids renormalized each iteration). Assignment math differs; a silent switch invalidates comparison with earlier runs.
- Determinism: seed the init (`np.random.default_rng(SEED)`), the iterations, and the repo split separately and record them.

## Embeddings via local Ollama

POST `http://127.0.0.1:11434/api/embed` with `{"model": ..., "input": [texts...]}`, batches of 64; single prompts run ~10 ms on CPU, batch throughput ~90/s — live interactive matching is feasible. Checkpoint vectors to `.npz` every few batches keyed by row id so an interrupted embedding run resumes instead of restarting. Normalize vectors once after collection, and check for zero-length vectors before normalizing.
