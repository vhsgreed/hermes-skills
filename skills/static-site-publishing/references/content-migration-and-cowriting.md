# Content migration and co-writing

## Migrating posts from another site

1. **Inventory first.** List every source post with title, date, word count, draft flag, description (loop over `src/content/blog/*.md` reading front matter). Classify into move / stay / borderline and get Karl's yes on the list before converting.
2. **Check the markdown features used** (tables, code fences, images, blockquotes, MDX imports, internal links) so the converter covers exactly what is present.
3. **Convert with a stdlib `migrate.py`** (no markdown package needed): front-matter parser + line-based converter for headings, paragraphs, lists, tables, fences, blockquotes, hr, inline code/bold/italic/links. Escape before applying inline markup; protect inline code from markup substitution.
4. **Rewrite links:** links to other migrated slugs become local; all other root-relative links become absolute to the source domain (they would 404 on the new site).
5. **Keep originals verbatim.** Each page gets a banner: migrated, not yet reviewed, plus a per-post review note (claims to recheck, merge candidates, authorship labels such as posts written by an agent). Editorial changes come in a second pass as marked proposals Karl approves.
6. **Emit an index data file** (`articles.json`) consumed by `build.py`; run `migrate.py` before `build.py`.
7. **Redirects:** write `redirects-for-<source>.txt` with `/blog/<slug>/ https://<newdomain>/articles/<slug>.html 301`. Check the source's existing `_redirects` for multi-hop chains to the same slugs and repoint them too. Do not deploy until the new domain is live, or links break; until then both copies coexist.
8. Verify every new page returns 200 on the preview and grep output for leftover raw markdown (`**`, `](`, backticks).

## Co-writing loop (low typing effort for Karl)

1. Ask 3-5 short, concrete questions per piece in chat; accept one-line or dictated fragments.
2. Draft in his voice, reusing his phrasing verbatim where possible; mark which sentences are assistant-written.
3. He edits with short notes ("cut para 3", "too soft", "no, I mean X"); never require him to write paragraphs.
4. End each piece with: "Written with an AI assistant; the positions are Karl's."
5. Escalate to voice memos + local transcription only if chat dictation proves too slow.
