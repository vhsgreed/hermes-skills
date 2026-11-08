# Publication figures for experiment write-ups

The rules that make figures reproducible, honest, and readable on the first try.

## Budget and set

- Aim for about 5 figures + 4 tables. Put the full per-group data in a CSV linked from the article instead of a giant table.
- A useful default set for a predictor study:
  1. Outcome distribution per main factor (log-scale box plot with the mean marked). Shows skew.
  2. One forest-style plot of every hypothesis's effect ratio vs the registered bar, using the held-out numbers exactly as the scorer wrote them. This is the headline figure.
  3. Confidence level vs interval width around the median. Answers the "how wide at p=0.5 / p=0.9" question.
  4. A Lorenz-style concentration curve (share of units vs share of outcome).
  5. A ceiling figure: spread left even with hindsight variables.
- Tables: the hypotheses with bar, verdict and commit; per-factor summary; the top-N groups; the descriptive reference table.

## Build

- Use one `figures.py` committed to the repo. It rebuilds every figure + CSV from data files, and its docstring states which figures are in-sample (descriptive) and which are held-out. Never hand-edit images.
- Write both SVG (for the static site) and PNG (for review). Use `matplotlib.use("Agg")`, `svg.fonttype="none"` and theme colors as constants.
- Read held-out results from the scorer's JSON/out files. Do not recompute them in the figure script, since that risks a second, different implementation.
- Scorer-only venvs often lack matplotlib, and uv-created venvs have no pip inside: `uv pip install --python .venv/bin/python matplotlib` is the fix that works for both.

## Layout pitfalls (fix before showing the user)

- Save with `bbox_inches="tight"`. Without it, long titles and x-labels are clipped at the figure edge.
- Split titles into a title line plus a subtitle line (`\n`). One-line takeaways overflow at a 7.5in width.
- On log axes, set `FixedLocator` + `FuncFormatter(lambda v,_: f"{v:g}")` and `NullFormatter` for minor ticks. The default shows mixed `4x10^-1` labels.
- Put reference-line labels (e.g. "bar 0.8") inside the axes at the top with explicit ylim headroom, not at the title position. They collide with the title or the data otherwise.
- Annotations near a diagonal or curve: place the text in empty space and use a leader line (`arrowprops`). White bbox patches over lines still read as collisions.
- Point labels at the plot edge: flip `ha` for the first and last points and set xlim/ylim padding.
- Explain every color and marker encoding in the axis label or caption. Make the color mean the full criterion (e.g. CI upper below bar), not just the point estimate, or readers take it as a pass.

## Verify

- Run `vision_analyze` on each PNG asking only for "clipped text, overlapping labels, text colliding with data; say none if clean". Iterate until every figure returns none. One round is rarely enough, so budget 2-3.

## Honesty

- When an in-sample figure reproduces a number reported earlier from a held-out or smaller sample and the values differ, say so explicitly to the user and in the article, with the reason. Never silently replace the old number.
- Surface uncomfortable patterns the figure exposes (e.g. a "passed" hypothesis whose groups are often worse than baseline) rather than letting the pass count stand alone.
