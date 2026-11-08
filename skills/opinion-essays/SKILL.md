---
name: opinion-essays
description: "Use when co-authoring a researched, cited opinion article."
license: MIT
---

# Opinion essays

Long-form pieces the user publishes under their own name: opinionated stance, contemporary-research grounding, the user's voice and accountability. The user writes; the agent researches, fact-checks, cites, edits, and co-builds the content in dialogue.

Companion skills: grounded-citations (ledger, inline ids, Sources block, verify) and humanizer (de-AI pass, voice calibration). Follow them for their mechanics; this skill governs the workflow around them.

## Always-on conventions

- Zero em dashes in prose and chat deliverables. Straight quotes. Convert the author's ad-hoc markup (custom bold/italic/URL markers) to the site's markdown during editing, not at assembly.
- The author's voice wins over tidiness: keep their jokes, asides, named examples, and sentence rhythm; fix grammar and typos silently.
- Push back on wrong claims with a numbered correction list and sources. The author wants challenge, not accommodation; retract a comfortable framing the moment evidence moves against it.
- Every load-bearing claim carries a citation or an explicit [bet] tag; a bet also names its gap (what has to break: capability, cost, law, or reliability).
- When the piece is a list containing bets, the intro states the bet count out loud.
- Publishing is a separate, gated step; the draft stops for the author's review.
- The byline names the model co-author (model name and role), because an opinion piece co-written by a language model carries that model's bias; a sentence whose opinion is the model's rather than the author's says so in the prose. The closing tests the piece's own "AI is powerful" claim against the co-author's incentive to say it.

## Procedure

1. **Interpret before researching.** Restate the premise, who "you" (the audience) is, the epistemic stance, and the shape. Ask one round of questions only where the answer changes the writing: audience, hedging level, structure.
2. **Fact-check the supplied draft before editing it.** Typical errors: wrong company or lab attributions (three events can share one number and get merged), stale prices, miscomputed percentages, impossible complexity bounds, garbled technical terms. Deliver corrections first as a numbered list with citations; grammar fixes stay silent in the rewrite.
3. **Rewrite with citations.** Populate the citation ledger at retrieval time, put inline ids on load-bearing sentences, render the Sources block mechanically, run the verify gate.
4. **Build long content in passes of about ten items.** Each pass is researched and anchored before it reaches the author. The author answers with kills and swaps by number; only then start the next pass. Each batch file ends with batch notes: source-quality flags (vendor, trade, or secondhand anchors to re-check at assembly), anchor-age warnings, and the pass's own editorial decisions (candidates killed and why), so the audit and assembly inherit the reasoning.
5. **Kill duplicates at batch stage.** No item may paraphrase another item or a bet. If two cover the same capability, merge or cut. Re-run the duplicate check at assembly across every batch including late top-ups: the same item rephrased in a later pass beats a within-batch check.
6. **Run the filler-or-kill audit before assembly.** Every item gets one verdict: keep, rewrite, merge, or kill. Kill items whose only anchor is vendor marketing; rewrite items that already pass the bar today (the item survives as the honest remainder of the capability, not the capability itself); merge overlaps instead of letting both live; keep-and-flag weak-source items. Then rule on the count: when the inventory falls short of a number the title promises, close the gap with one more real sourcing round, never filler; if real anchored items cannot be found, retitle to the honest count. The author delegates this judgment to the agent; report the verdicts as a table.
7. **Assemble late.** Global numbering, section order, and the intro's bet count wait for final assembly; top-up batches rejoin their home themes here and their provisional labels are discarded. Rewrite internal cross-references at the same time (items cite each other and the bets by provisional label): build the label-to-final-number map from the assembly order and replace every reference, watching for labels that collide with real tokens in prose (a bet called M5 meets an M5 Pro chip), which a blind regex replace silently corrupts.
8. **Primary-source pass before publishing.** Trace every claim the preamble and closing lean on (government actions, incidents, headline research results, the statistics repeated across items) to its primary: the order on the government site, the company's own postmortem, the paper, the wire report. Re-read the item text against it; primaries regularly reverse a secondary's framing of cause or scope, and a hostile reader checks the most-reused example first. Recheck relative dates ("two days ago") on every rebuild.
9. **Verify and deliver.** Citation verify gate (per batch: no unknown ids; full gate at assembly), drafts saved under the project's sources directory, and the rewrite or batch shown in chat.
10. **Report the running count from the files.** When the author asks how long the list is, count items per batch file in code (regex on the item labels) and show a per-batch table plus remaining-to-target; never total from memory. Labels carrying a parenthetical theme tag (like `G1 (physical).`) do not match a `^Xn\. ` pattern; use a looser label regex or the count under-reports. Sections that are not list items (for example a graded-prompts section) are reported separately from the count.

## Item anatomy (list pieces)

Grounded item: capability in concrete "you can X" terms; today's honest state anchored to the best current product, price, or study; what is missing; blocker tag (capability, cost, law, reliability). Bet item: the same plus [bet] and the named gap. The moonshot budget is fixed in advance and never grows mid-piece. Starter shapes: templates/list-item.md.

## Evidence choice for "can you do X" claims

Prefer studies of people using the tool (randomized or preregistered user studies, field tests by reviewers) over model-alone benchmarks. The two diverge sharply: a model can score near-perfect alone while its users do no better than a control group. When both exist, cite both and present the gap; it is usually a stronger finding than either number, and repeated instances of it across sections belong in the closing argument.

## Popularity claims and the author's own scans

Any section that calls something popular, viral, or trending (graded meme prompts, discourse topics) needs measured volume behind each entry: scrape it (see apify-store-scraping), keep entries with real counts, and cut zero-support candidates even when they feel famous, listing the cuts in a method note. Cite the author's own scan through that method note: publish the actor or tool names, exact queries, date, and aggregate counts; never publish the raw scraped posts, which are other people's content. Cap such sections (ten entries) and grade each entry against the list's own bar so the section stays argument, not a meme dump.

## Harms and counterpoint sections

When the author supplies a list of negative implications, treat it like any supplied draft: source each point, correct mechanism and terminology errors (for example, guardrail removal on open models is fine-tuning or abliteration, distillation is a different leak), upgrade "could happen" to "already exists" when the evidence supports the stronger claim, and convert pure speculation into an explicitly marked question. Offer a few additions of your own, labelled as additions. Keep abuse-material points short and statistical, with no description. Place the section outside the list count: these are things done to the reader, not things the reader can do.

## Personal essays distilled from a conversation

When the author asks to turn a long chat session (a lament, a journal-style exchange) into an essay, the raw material is mostly the agent's prose. Procedure and gates: references/personal-essays.md. Always-on rules:

- Draft in the author's voice from their own phrases and examples; flag in the delivery which passages are agent-written so the author's voice pass knows what to rewrite.
- Where the agent pushed back in the session, the essay attributes that counterargument to the model in the prose, and the author's acknowledged holes stay visible as seams with the counter beside them; never smooth them into agreement.
- Wrap health, diagnosis, drug, legal, or relationship disclosures in `<!-- DISCLOSURE START/END -->` comments, and write the essay so it still stands with those blocks cut.
- Before scoping, name the permanence once: personal medical history used as evidence becomes searchable under the author's name on the domain they use professionally. One caveat, then it is the author's call; record the decision as open in the ledger if the piece is parked.
- Gate publication: disclosure blocks get a read by someone who knows the author's situation (their therapist when they have one) before anything ships, and a strong late-night urge to publish something personal is a reason to draft, not to publish; set a no-publish-before date and record it as the blocker in the project ledger.

## Placement integrity

A piece that cannot meet a publication section's stated standard (for example, pre-registered hypotheses and reproducible numbers for a research journal) must not be published under it. Let each section keep its promise.

Opinion on agentrecourse.org is the author's light-hearted, human-centric personal journal for their own thoughts. Factual or analytical pieces (paper reviews, "can an agent audit X" framings) are not opinion pieces even when they carry a verdict: route them to a pre-registered Journal study (see pre-registered-experiments) or hold them, rather than dressing them as opinion. A topic off the site's agent focus needs an angle that connects or a reason the author gives.

## Pitfalls

- Editing a supplied draft without fact-checking launders its errors into print under the author's name; verify claims before touching prose.
- Corrections calm a draft's rhythm. When the rewrite runs too evenly, recommend a read-aloud pass and stop polishing; a tidied voice is the machine tell.
- Keyword homonyms silently swap meanings (a policy program and a sci-fi future can share one word); read what the term means in the cited source before building an argument on it.
- "Cannot do today" is falsified by one reader's anecdote. State the bar in the intro (usable standard, ordinary cost, one person acting alone) so items survive contact with a specialist.
- Law-gapped items accumulate unnoticed (they clustered twice in one piece: five of fifteen bets, three of ten grounded items). Surface the pattern to the author; it is usually the piece's real finding.
- Paraphrase strength must not exceed the source's scope. When the author seizes on a striking claim, re-read the exact source wording, report its stated limits (minority share, confounds the source names), fix the item in place, and attach verbatim quotes to the ledger for it; a dramatic overstatement is the claim a hostile reader checks first.
- Numbers the author supplies without a source get cut, not softened; offer the nearest sourced figure instead and leave an editorial note saying why the original went.
- Disclose self-citation in the item: the author's own published study, or the agent citing its own vendor's misuse or safety reports, must be marked as such in the prose.
- When the author offers an outside model's review of the draft (or of a pasted chat transcript), accept it, then triage each point as still valid, already fixed, or wrong, with reasons; never apply it wholesale. A model that saw only the transcript inherits every claim the agent has since retracted (check its candidate theses against later corrections) and often flips who corrected whom; re-read the transcript before building a hook on "the author conceded X". Also cut its proposed length to the author's bet cap: word counts from an outside reviewer ignore exam season and stake limits.
- A moonshot reframed from a hype headline into the underlying capability survives review; the headline version reads as a scam and takes the piece's credibility with it.
