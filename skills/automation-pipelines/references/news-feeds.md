# News feed candidates by beat

Feeds go stale or die without notice. Re-run `scripts/feedtest.py` on any URL before relying on it; this list says what was worth testing, not what is guaranteed live.

## Markets / macro
- Fresh and dense: Google News Business topic RSS (`news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en`, aggregates Reuters/FT/Bloomberg/WSJ), `feeds.bloomberg.com/markets/news.rss`, `feeds.bloomberg.com/economics/news.rss`, `ft.com/markets?format=rss`, CNBC top news (`cnbc.com/id/100003114/device/rss/rss.html`).
- Also fresh: BBC/Guardian business, di.se (Swedish), investing.com news.
- Low volume, good for a central-bank sub-beat: Fed `federalreserve.gov/feeds/press_all.xml`, ECB `ecb.europa.eu/rss/press.html`.
- Tested stale: WSJ `RSSMarketsMain`, MarketWatch marketpulse, CNBC sub-section feeds, Economist finance. Yahoo Finance rss URLs returned 404.
- MarketWatch top stories mixes in personal-finance advice columns; the user prefers it excluded.

## Non-Western / cross-angle outlets
The user wants to compare framing across blocs, not just collect more news. They want the model to retrieve and set side by side what each bloc says, not to do analysis for them: quote the headline wording and describe the differences, with no verdicts and no long reasoning chains. Label each feed with country and ownership (state / public / private).
- Fresh: TASS `tass.com/rss/v2.xml` (Russia, state), CGTN `cgtn.com/subscribe/rss/section/world.xml` (China, state), Press TV `presstv.ir/rss.xml` (Iran, state), Anadolu `aa.com.tr/en/rss/default?cat=world` (Turkey, state), Al Jazeera `aljazeera.com/xml/rss/all.xml`, The Hindu international, Dawn `dawn.com/feeds/world`, SCMP `scmp.com/rss/91/feed`, africanews.
- Stale feeds: Global Times outbrain.xml, Xinhua english worldrss. Use CGTN for the Chinese state line.
- RT and Sputnik are EU-sanctioned; the home router's DNS may refuse them while public resolvers answer. Bypassing that is the user's decision, never a silent workaround. TASS carries the Russian state line meanwhile.
- Western baseline for comparison: BBC world, Guardian world, DW.
