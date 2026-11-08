# Household alkaline extracts: buffer budget, dilution, improvised indicators

Depth for protocols built on a base-buffered household product (tobacco or
chewed-tobacco extract plus NaOH/K2CO3, soap making, alkaline cleaners).

## Buffer budget: predict pH instead of refusing to

Constants worth memorising: **1 g NaOH = 25 mmol**; 1 g K2CO3 = 7.2 mmol;
1 g Na2CO3 = 9.4 mmol; nicotine MW 162, pKa1 = 8.0.

1. Sum the base added in mmol.
2. Sum the proton donors that can give up a proton **going upward from the
   product's own pH** (not its total acid content):
   - protonated amine present at that pH, `f = 1/(1+10^(pH-pKa))`
   - bicarbonate present at that pH (carbonic pKa2 = 10.3)
   - protein side chains with pKa between the start pH and target (Lys 10.5,
     Tyr 10.1, Cys 8.3), typically 1-3 mmol for tens of grams of plant material
3. Excess = base added - proton donors. Convert to `[OH-] = excess / volume`,
   then `pH = 14 - pOH`. Report a range from pessimistic and optimistic donor
   assumptions; the answer is usually insensitive because the base dominates.

Worked shape: 25 mmol NaOH against 3-8 mmol of donors leaves 17-22 mmol free in
1.5 L, i.e. 11-15 mM, pH ~12.0-12.2. The product's own buffer absorbed under a
third of the base, so "the matrix buffers it" was the wrong reassurance.

## Dilution law

For a hydroxide-dominated solution, `pH_after = pH_before - log10(dilution)`:
3x dilution costs ~0.48 units, 10x costs 1.0. Diluting a pH 12 batch 1:2 lands
near 11.6, still caustic and still >99% free base. Only measured acid addition
or a genuinely buffering substrate (peat, soil, compost) neutralises it.

Stoichiometric neutralisation with household vinegar: 6% acetic acid is ~1 M,
12% is ~2 M. To take 20 mmol of excess OH- down to pH ~9 needs ~20 ml of 6% or
~10 ml of 12%, and stopping at pH 9 keeps ~91% of a pKa 8.0 amine in free base
while removing the handling hazard. State the error band: undershoot leaves it
as it was, overshoot drops free base toward 50%, both benign.

## Improvised indicators: what each can and cannot say

| Test | Reads | Cannot read |
|---|---|---|
| Turmeric / curcumin in ethanol | single switch: yellow below ~7.5-8, red-brown above ~8.5-9 | pH 9 vs 11 vs 12 (all deep red); not usable in a dark extract without spotting on white porcelain or diluting ~1:30 |
| Red cabbage juice | blue-purple ~6, blue-green ~8-9, green ~10-11, yellow ~12+ | finer than ~1 unit; fades in strong base |
| Vinegar fizz | carbonate / bicarbonate content | alkalinity: NaOH + acetic acid gives no gas at all, so no fizz does not mean neutral |
| Skin saponification feel | only pH ~12+ and only after tens of seconds | everything below 12; a 3-second touch is uninformative |

Rules: one improvised indicator = one bit, so use it as a yes/no gate ("has the
excess base been consumed?") and never as a measurement. Validate against two
standards made from reagents already on the bench (dilute acid = yellow,
pinhead of NaOH in water = red) before trusting it on the real batch. Curcumin
degrades in strong alkali, so read within minutes.

## Reading an indicator in a dark matrix

Tobacco and coffee extracts are opaque brown. Two workarounds: spot 3-4 drops of
indicator on white porcelain and add one drop of sample (compare the mixed drop,
not the sample), or dilute the sample ~1:30 with water to pale tan. Dilution
compresses readings toward the buffer's pKa, so treat the diluted reading as a
band, not a value.
