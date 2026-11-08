---
name: swedish-small-business-finance
description: "Use when advising on Swedish tax, moms, or entity choice."
version: 1.0.0
author: Karl Sundström
license: MIT
metadata:
  hermes:
    tags: [tax, sweden, business, enskild-firma, finance, moms]
---

# Swedish small-business finance

## When to Use

Advising on enskild firma / aktiebolag taxation, moms (VAT), deductions, entity
choice, revenue set-aside, or how founder money leaves the business. Karl runs an
enskild firma whose product domain is company financials, so these questions recur
and wrong answers are expensive. Deliver numbers with the income year attached.

## Always-on rules

1. **Numbers over moods.** Never answer with "it depends" alone: show the computation
   chain with figures and state the income year the rates are valid for.
2. **The chain is stable, the rates are not.** Percentages and brytpunkter change every
   year; verify each one at Skatteverket for the year in question before quoting it.
   The order of the computation below never changes.
3. **One line of disclaimer, not a paragraph:** recommend a redovisningsbyrå confirms
   the first real filing, then move on.
4. **Moms is never revenue.** It is collected on behalf of Skatteverket: segregate it,
   never count it toward burn, MRR, profit, or spending power.
5. **Check the entity before answering.** Enskild firma means the person IS the firm:
   no dividends (utdelning), no retained company pot, money out is uttag of
   already-taxed income. Dividends and profit carryover require an aktiebolag. A plan
   built on dividends is structurally impossible under enskild firma; say so plainly.
6. **Never mix tax systems in one comparison.** Enskild firma: egenavgifter on
   överskott plus personal income tax. AB: arbetsgivaravgifter on salary, corporate
   tax on profit, 30% capital-income tax on dividends. Comparing raw rates across the
   two systems without the full chain is how people pick the wrong entity.

## Procedure (compute in this order)

1. **Resultat** = intäkter minus kostnader. Business costs are deductible: API and
   hosting, domains, hardware (data equipment is typically fully deductible in the
   purchase year), home office under its own rules.
2. **Överskott** = resultat minus schablonavdrag (25% of resultat).
3. **Egenavgifter** on överskott (around 29%, 7 karensdagar), with a percentage
   reduction above a profit floor and a cap. This is the sole trader's pension and
   social insurance: there is no employer paying in.
4. **Income tax** on överskott: kommunal inkomstskatt (low 30s percent, varies by
   kommun), plus statlig inkomstskatt (20%) above the year's brytpunkt.
5. **Moms in parallel:** 25% on Swedish services (reduced rates on some goods),
   reported on the registered period. Turnover under the small-scale threshold (about
   80,000 kr per 12 months) allows momsbefrielse instead of registration.
6. **Rule of thumb that holds:** total tax on profit lands near 45-50%, so "set aside
   half the profit for tax and never touch the moms pot" is sound practice.
7. **Mechanics:** F-skatt means you pay preliminärskatt yourself, quarterly; the NE
   bilaga rides with the inkomstdeklaration each spring; bookkeeping is retained 7
   years.

## Deferrals and other pockets

- **Expansionsfond** lets profit stay in the firm with deferred tax (expansionsfondsskatt
  on later withdrawal). This is the sole-trader answer to "leave money in the company".
- **Private crypto** gains are capital income, 30% on profit, reported in K4. Large
  active trading can be reclassified as business income; flag the boundary, do not
  adjudicate it.
- Student loans and stipends are not taxable income; do not net them against business
  figures.

## Pitfalls

- Never quote a rate from memory or from a search snippet without the income year
  attached; last year's brytpunkt used for this year's planning is a wrong answer
  wearing a right format.
- Never treat a billing setup gap as a tax question: invoicing provider choice is
  operations, keep it out of the tax computation.
- Never let a set-aside rule silently include moms; splitting "tax + moms" into one
  percentage hides that moms was never the founder's money.
