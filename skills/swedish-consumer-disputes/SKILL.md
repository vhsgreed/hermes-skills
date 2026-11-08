---
name: swedish-consumer-disputes
description: "Use when a Swedish purchase, return, or refund is disputed."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [consumer-rights, angerratt, reklamation, klarna, arn, returns, sweden]
    related_skills: [grounded-citations]
---

# Swedish consumer disputes

## When to Use

For a refused return, a refused complaint, a payment-provider dispute (Klarna, card), or a trade/resale used to get out of a bad purchase. Separate legal rights from store policy, draft the written notice, compare exit routes in kronor. Load `grounded-citations` too: cite the store's own terms and Konsumentverket/ARN pages, since the user may paste the answer back to the store.

## Procedure

1. **Pin the facts that decide the case before arguing law.** Ask only for what is missing:
   - Channel: bought on the web (distance contract, lagstadgad ångerrätt) vs in store or Boka&Hämta paid in store (no ångerrätt, only store policy).
   - Delivery date: the 14-day ångerfrist runs from the day after delivery. Compute the deadline date and state it.
   - Is the item defective (reklamation) or just wrong for the buyer (ångerrätt)? Check the product page and spec sheet: if the item is plainly described as it is, there is no defect.
   - Payment method (Klarna invoice, card) and whether anything was said in writing.
2. **Read the store's current terms page** (web_extract; the long middle is truncated, so read_file the cache path for the ångerrätt section). Quote the exact wording that matters. Stores often require original packaging only for their voluntary öppet köp, while the ångerrätt section says "om möjligt". Konsumentverket: broken or missing packaging does not void ångerrätt; the store's remedy is a värdeminskning deduction, not refusal.
3. **Split the two regimes in a table**: lagstadgad ångerrätt vs the store's öppet köp/prova-på (who sets it, packaging requirement, category exclusions such as kitchens/vitvaror). A refusal from customer service is almost always a öppet köp answer applied to an ångerrätt case.
4. **Kill the store's stated objection with a practical offer**, not only law. E.g. "need packaging for transport": offer an in-store return (most terms allow it) or self-packing with cardboard, corner guards and stretch film.
5. **Draft the written notice** (Swedish, copy-paste ready, placeholders in [BRACKETS]): invoke ångerrätt explicitly, cite the clause, offer the practical route, accept their right to a value deduction but not refusal, request a written reply. Tell the user to send it in writing and save a copy: a phone/chat refusal is not binding, and the written notice is what meets the deadline.
6. **Escalation order**: written refusal from the store, then Klarna "rapportera retur"/dispute with the correspondence attached, plus ARN (free) and kommunal konsumentvägledning. Present the payment provider as leverage, not the main route: Klarna decides at its own discretion and accepts the merchant's "policy not followed".
6b. **Private seller on a marketplace (Tradera, Blocket, cross-border).** Consumer law (konsumentköplagen, ARN) does not apply between private persons; the köplag hidden-defect rule does, and notice must come within a reasonable time of discovering the fault, so draft the notice the same day. The real levers, in order: the marketplace's buyer protection (window depends on payment method; check the live help page), the payment provider's own window (Klarna is longer than card/Swish), then the seller's reputation (rating, "top seller" status). Give the user a window table by payment method with concrete dates, then an English draft for a foreign seller offering two outcomes (partial refund for the faulty part on return, or full refund for all) plus any manufacturer-warranty route only the original buyer can use. Attach the technical evidence (test result photo, stock settings, fault timeline from first use).
6c. **User (private person) sold or traded to a dealer, dealer later claims a defect.** Köplagen applies, not konsumentköplagen. The buyer (dealer) carries the burden of proof that the fault existed at risk transfer (21 §; Lawline cites NJA 2013 s. 524 p. 10, with p. 24 shifting it if the complaint comes very soon after receipt). Even quantum in the worst case: repair/price reduction for the faulty part, no indirect loss (40, 67 §§). ARN is closed to both sides (only consumers can file, and only against a business); the dealer's real route is tingsrätt småmål, which costs them a fee and puts the burden on them. 31 § (dealer's duty to inspect) only moves the 32 § complaint clock; it supports the case but is not the knock-out. Read the thread for who pays the mellanskillnad before arguing: users misread the direction.
7. **If the user considers an alternative exit** (trade-in, private resale, keeping it and adapting the house), put every route in a kronor table: what goes out, what value comes back, what they end up owning, warranty. Then give a floor price/counteroffer and a decision date that leaves margin before the ångerfrist ends.

## Rules

- **Never advise claiming a defect that does not exist** (e.g. Klarna "rapportera ett fel" for a correctly described item). The merchant rebuts it with the spec, the provider can refuse to pause the invoice for misuse, and it damages credibility at ARN. Route through the right that actually applies.
- **Do not send the ånger notice before an alternative deal is settled** if the user is still negotiating one: the notice commits them to returning the item. Give a decide-by date a few days before the deadline instead.
- **Verify the replacement fits before endorsing a swap.** Appliance model numbers often exist in multiple electrical variants (the same stove model in 230V and 400V); search `"<model>" 230V` and `"<model>" 400V` (spare-parts shops list both) and make the seller confirm the variant in writing.
- **Push back on the user's own math** when it is wrong: compute both routes. Return-route costs are usually capped by the store's terms (freight) plus a small deduction for an unused item, which typically beats a straight swap for an older used unit.
- **Tone when the user is frustrated** (venting one-liners): two or three lines, one concrete next action, no re-explaining the law, offer to finish the draft if they send the missing details.
- **Language**: answer in the language of the user's latest message (they switch between Swedish and English); drafts aimed at Swedish companies stay in Swedish. No em dashes, including in rendered Sources blocks.

Domain specifics (Elgiganten terms, Klarna flow, 400V/230V stove electrics, valuing a trade-in): `references/retailer-and-appliance-notes.md`.
