# Cloning a commercial food product from its label

Use when the user wants a home version of a packaged food (protein bar, sauce,
snack) that matches the original. The label is the only hard data: ingredient
order (descending by weight under EU rules), declared percentages, and the
nutrition table per 100 g. Everything else is inference and must be called so.

## Procedure
1. **Pin the exact current product.** Fetch the brand's own product page (curl +
   strip tags works on most Swedish brand sites; save text to the source dir).
   Look for "Nytt recept"/"New recipe" on the pack image and compare article
   numbers and pack weight across retailers: brands reuse the flavour name for
   a reformulated bar, and retailer pages often still carry the old recipe.
   State which version you are cloning and that the other one differs.
2. **Separate the part being cloned.** If the user withholds a component
   (coating, glaze, topping), include it in the fit as its own ingredient with
   a typical composition, then report the remainder renormalised to 100 g.
3. **Back-calculate** with `scripts/label_backcalc.py <spec.json>`: constrained
   least squares (sum = 100, label order as x[i] >= x[i+1], declared % fixed)
   against protein, fat, saturated fat, carbohydrate, sugars, fibre, salt and
   kcal. Weight salt up (x3) because it is a near-pure single-ingredient signal.
4. **Run the sensitivity sweep** (`--sweep`): vary the uncertain compositions
   (protein powder purity, coating fat/sugar, chocolate fat) and report the
   min/median/max share per ingredient across scenarios that fit within
   ~1.5 g. Give the user ranges, not one falsely precise formula.
5. **Fit home ingredients** to the inferred filling using real Swedish retail
   labels (Hemköp JSON endpoint, brand pages; see `product-price-monitor`
   `references/swedish-grocery-apis.md`). Add a small penalty pulling toward
   the inferred ingredient ratios so the fit preserves function (texture,
   humectancy), not only macros. Report per-macro deviation, cost per unit and
   per-unit macros.
6. **Deliver**: batch table in grams, method, why-each-ingredient (cited),
   tuning table (too hard / too soft / too sweet), and an explicit statement
   that a "99% match" is checkable on paper for macros only; texture needs
   2-3 test batches.

## Composition facts that change the fit
- **Glycerol counts as carbohydrate on EU labels** but carries 2.4 kcal/g; use
  that in the kcal check or the fit overshoots energy.
- **EU syrup names encode fructose share**: glucose syrup <5% fructose,
  glucose-fructose syrup 5-49.9%, fructose(-glucose) syrup >=50%. Agave syrup
  (~79 g sugars/100 g, mostly fructose) is the retail stand-in for fructose
  syrup; Dansukker glykossirap is 77 g carbohydrate, 23 g sugars per 100 g.
- **"Mjölkprotein" = milk protein concentrate/isolate** (~80% casein / 20%
  whey); Tyngre Kasein Naturell is that product at retail (81 g protein).
  Unflavoured hydrolysed collagen is ~91 g protein/100 g.
- **Low declared fibre with a chocolate flavour** means little cocoa outside
  the coating: the filling is pale and the flavour comes from a few % chocolate
  plus aroma.

## Protein bar texture rules (cited sources in the session write-up)
- Intact whey isolate alone hardens badly in storage (protein/sugar phase
  separation); blend with hydrolysed protein (collagen) or casein for a soft,
  chewy bar.
- Glycerol lowers water activity and keeps bars pliable; added water softens
  but makes them sticky and less liked, so add no water.
- No-bake: warm syrups to 40-50 C only; heat speeds Maillard browning and
  hardening. Rest 12-24 h before cutting. Without a water-activity meter, store
  refrigerated and give a conservative shelf life (~2 weeks).
- Generic ratio for any home bar: 40-50% protein powder, 35-45% liquid
  sweetener + humectant, 5-10% fat, no water.
