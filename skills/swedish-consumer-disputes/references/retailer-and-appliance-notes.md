# Retailer, payment and appliance notes

Re-verify against the live pages before quoting; terms change. Check the "gäller från" date on the terms page.

## Elgiganten (elgiganten.se/kundtjanst/kopvillkor-elgiganten-se)

- Section 5 Öppet köp: 30/50 days unopened in original packaging; 14-day "prova på" for opened items requires original packaging; kitchens excluded. This is voluntary policy.
- Section 8 Ångerrätt: notify within 14 days of receipt in writing (ångerblankett, mail, sms) with the order number; return within 14 days of the notice; return "om möjligt i originalemballaget"; buyer pays return freight, for bulky goods (vitvaror) normally 500 to 1000 kr, capped at 1000 kr per item; value deduction = cost to restore to original state. Returns accepted in store.
- Boka&Hämta paid in store has no ångerrätt.
- Their "Uppackning och återvinning av emballage" delivery service removes the packaging; use that as an argument against a packaging-based refusal.
- Disputes: ARN named in their own terms (section 10).

## Klarna (klarna.com/se/returinstruktioner)

- "Rapportera en retur" pauses the invoice while the case runs; needs return proof (tracking number or in-store return receipt).
- If the merchant objects, Klarna decides at its own discretion on the evidence; misuse of the function lets Klarna refuse the pause.
- Attach the store's written refusal and the ånger notice. Open it only after the store has refused in writing.

## Tradera (tradera.com/support/se, posts on köparskydd)

- Köparskydd is mandatory on purchases over 200 kr from private sellers; covers non-delivery and "felaktigt beskriven vara"; excludes regret and faults disclosed in the listing.
- Window: 30 days from payment for Swish/card/Trustly/Apple Pay/Google Pay; Klarna payments go through Klarna with up to 120 days. Confirm the user's payment method first: it decides whether any formal route is still open.
- Past the window: goodwill only; a verified top seller's rating is the leverage.
- Branded RAM/SSD warranty (Crucial, etc.) needs original-buyer proof of purchase; ask the seller to claim it.

## Stoves: 400V vs 230V (Norwesco/Perilex)

- Get max connected power and fuse from the manufacturer product sheet (retailer CDNs host it; Elon links the Electrolux DSPDF and manual PDFs; `curl -sL ... -o x.pdf && pdftotext -layout x.pdf x.txt`, grep "Säkring", "anslutningseffekt", "Spänning").
- Single-phase current = W / 230. A 9 kW stove on one phase is about 40 A, far beyond a normal 230V stove outlet; flag converting such a stove as unlikely and leave the call to an electrician.
- The realistic alternative is often the reverse: if three phases already reach the kitchen, an electrician swaps the outlet to Perilex. Ask for a quote and compare it to the return cost.
- Many older/used models exist in both 230V and 400V variants under the same model number; confirm the variant from the rating plate.

## Valuing a trade-in for a new, boxless, unused item

- Anchor the user's item at the current lowest new price (PriceRunner) minus a no-box discount (roughly 10 to 15 percent), not their purchase price.
- Anchor the dealer's used unit at what other refurb dealers charge for the same model (search the model number across dealers/marketplaces).
- Counteroffer: cash back plus free delivery/installation and taking the old item; set a floor below which the return route wins.
