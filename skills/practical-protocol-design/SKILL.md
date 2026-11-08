---
name: practical-protocol-design
description: "Use when turning research into a dosed hands-on protocol."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, protocols, experiments, dosing, safety, formulations]
    category: research
    related_skills: [grounded-citations, pre-registered-experiments, spike]
---

# Practical Protocol Design

Turn literature into a protocol the user can execute first try with the tools
they actually have. The deliverable is a quantity table, dosed steps mapped to
listed tools, and a bounded safety envelope, not a literature summary. Ground
dose anchors in sources with `grounded-citations` conventions (register, cite
inline, render the Sources block).

## When to Use

Use when the deliverable is something the user will physically execute: a
dosing or formulation recipe, a treatment schedule, a lab or kitchen-bench
experiment, a soil/plant/grow treatment plan, or a protocol assembled from
literature plus the user's real constraints (reagent spec, tools on hand,
budget). Skip for code experiments (`spike`) and dataset experiments
(`pre-registered-experiments`).

## Procedure

① **Fix the endpoint before designing.** Absolute goals ("kill all X", "get rid
of it") become measurable endpoints: counts at named timepoints plus a cheap
verification method the user can run at home. State what one application can
and cannot achieve (overlapping pest generations, degradation of the active),
and give the escalation path if the endpoint is missed.

② **Anchor every dose twice**: the literature dose window (mg active per L or
per area) and the user's actual reagent spec (label content, purity, product
page). Express treatment strength in active-ingredient units, never in units of
product. Show a quantity table: reagent, active per unit, amount for target
concentration, final volume. Mark derived numbers as your own calculation.

③ **Correct mechanistic premises before writing steps.** When a proposed step
conflates mechanisms (extraction yield vs bioavailability, solubility vs
potency, concentration vs dose), explain the correct chemistry first, then give
the bounded version if the user still wants the step.

④ **Map every step to the tools the user listed.** When a step needs a device
they lack (pH strips, thermometer, syringe), name it as a required addition.
Never give fixed doses of reactive chemicals (strong bases, strong acids) into
an unknown matrix without a measurement endpoint. When the user will dose anyway,
compute the buffer budget instead of only refusing: total the mmol of proton
donors that can accept base at the product's own starting pH (protonated amine,
bicarbonate, protein side chains) and compare it with the mmol of base added. If
the base exceeds that total, pH is set by free hydroxide and is computable
without a meter; give the number with a range and the assumptions behind it.

⑤ **List confounders in consumer-grade reagents**: additives, humectants,
sugars that feed the target pest, salt load, biological contamination of the
source material. Where feasible add a matrix control; at minimum name the
confounder in the design.

⑥ **State the safety envelope once**: total active in the batch in hazard terms
(compare to a toxic threshold), PPE, container labeling, spill response, local
poison information number. Do not repeat safety prose at every step.

⑦ **Build the schedule from persistence data**: application intervals matched
to the active's half-life in the target matrix, plus the intervention that
covers the stage the treatment misses (e.g. traps for flying adults of a soil
pest).

⑧ **Offer a printable one-page protocol file** (quantity table, steps,
schedule, safety block).

**Cloning a packaged food ("make X at home", "match product Y")**: follow
`references/food-product-cloning.md` (pin the current recipe version,
back-calculate shares from label order + nutrition table with
`scripts/label_backcalc.py --sweep`, then fit real retail ingredients). If the
user has a salt budget (medical or dietary), flag per-portion salt against it.

**Base-buffered household products** (extracts, cleaners, soap): follow
`references/household-alkaline-extract.md` for the mmol buffer budget, the
dilution-law correction, and what each improvised indicator can actually report.

**Indoor pests** (soil gnats, pantry beetles, flies): follow
`references/indoor-pest-control.md` for the stage-to-vulnerability mapping, the
moisture thresholds that actually kill each stage, the bait-slice assay, and the
published efficacy table for barriers and biologicals.

**Numeric fits belong in code.** Any recipe, dose or formulation that must hit
several targets at once is a constrained least-squares problem; solve it with
scipy in a scratch venv and report per-target deviation, never hand-tune in
prose.

## Pitfalls

- **Blind dosing of reactive chemicals.** Never hand out fixed gram amounts of
  strong bases or acids for an unknown matrix; buffering capacity is
  unpredictable, and the protocol must require a measurement device instead.
  Where the user has already dosed, back-calculate the mmol budget and predict
  the pH rather than restating the objection.
- **Dilution is not neutralization.** A hydroxide-dominated solution falls only
  log10(dilution factor) in pH, so 3x dilution is ~0.5 units and the batch stays
  caustic and fully free-base. Diluting to hit a contact dose fixes the dose,
  not the handling hazard; advise on the two separately.
- **Matrix buffering is one-directional.** Acids already deprotonated at the
  product's own pH absorb acid, not base, so "the matrix will buffer it" is
  false once the addition exceeds the product's own titration window. Check
  which side of the buffer the addition lands on before reassuring the user.
- **Improvised indicators report one bit.** Turmeric, vinegar and skin tests
  each cross a single threshold and none can return a numeric pH; see
  `references/household-alkaline-extract.md` before designing a test around one.
- **Trap counts lag the treatment.** Sticky traps catch the generation already
  pupating before the first application, so a week-one spike is consistent with
  both success and failure. Read the trend from the first full generation, and
  pair it with a direct assay of the stage actually being killed.
- **Doses in product units** (pouches, cans, scoops). Product specs span orders
  of magnitude in active content, so the protocol becomes untestable and the
  next batch behaves differently. Convert to active-ingredient units.
- **Eradication promises.** Overlapping generations and short persistence mean
  a schedule, not one treatment. Say counts-over-time, and note which pest
  stage the treatment cannot reach (a soil drench does not kill flying adults).
- **Treating only the symptomatic subset.** Mobile pests reinfest from missed
  reservoirs; treat the whole room or collection and name likely reservoirs.
- **Full-batch first application.** Test phytotoxicity or matrix tolerance on
  the hardiest subset first, wait one observation window, then treat sensitive
  specimens.
- **Promising a percentage match.** A "99% match" to a commercial product is
  checkable only on paper (macros); texture depends on unpublished raw
  materials and process. Say so and plan 2-3 test batches with a tuning table.
- **Cloning the wrong version.** Brands reformulate under the same flavour
  name; retailer pages lag. Take the recipe from the brand page and the pack
  image ("Nytt recept"), and name the version you cloned.
- **Silent novelty.** When the target pest has no direct literature for the
  proposed mechanism, say the protocol is novel data and set expectations
  accordingly; that is often exactly why the experiment is worth running.
- **Physical controls need published efficacy, not physical intuition.** A
  coarse-grit cap looks like it should block a 2 mm fly, but sand and
diatomaceous earth layers are documented ineffective against fungus gnats at
3-6 mm thickness, and fine sand is actively worse because it wicks moisture up
from the medium and crusts into an attractive damp surface. The plausible
mechanism is often not the operating one; check the control against a trial
before recommending it, and when a user proposes a finer grade to close smaller
gaps, explain why the mechanism is not mesh size.
- **Discount efficacy against reproduction rate.** A 69-90% kill sounds decisive,
  but against 50-300 eggs per female and a 17-day generation it reaches
  equilibrium rather than extinction. Convert any quoted efficacy into expected
  survivors per generation before telling the user a treatment is sufficient.
- **Container and material compatibility is governed by concentration, not pH.**
  A pH 12 solution at 0.05% NaOH is fine in PET for days; the same polymer is
  attacked by the 1-30% NaOH the compatibility charts actually rate. Read the
  chart for the grade it specifies and compare moles of the aggressive species,
  not pH. A past failure with a concentrated solution does not predict the
  dilute case.
- **Calendar dosing is not prevention.** When the active's residual in the
  matrix is days and the pest's generation is weeks, a fixed-interval
  prophylactic dose protects only the first few days and wets the substrate on a
  schedule, which can favour the pest. Dose on a monitoring trigger, not a
  calendar, and say plainly that the residual cannot bridge the gap.
- **An experiment without measurement is an impression.** When the user proposes
  to skip the assay because the techniques are already proven, restate that
  proven means 70-90% and give the cheapest assay (bait slice, fixed-area trap
  count, weekly number) rather than arguing about it.
