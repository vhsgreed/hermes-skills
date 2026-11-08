# Genre market research (Steam)

Use when Karl asks "what do the top N games in genre X have in common" or brings a genre.

## Recipe: rank a genre's top titles
1. Steam's tag search sorted by reviews (`store.steampowered.com/search/results/?tags=<id>&sort_by=Reviews_DESC&infinite=1`)
   is polluted by loosely tagged games (desktop pets, hidden-object) for niche tags like
   Incremental. Do not use it as the ranking.
2. Tag ids: `store.steampowered.com/tagdata/populartags/english` (Incremental 560542,
   Idler 615955, Automation 255534).
3. SteamSpy: `steamspy.com/api.php?request=tag&tag=<Name>` for each related tag (Idler,
   Clicker, Incremental), merge by appid, take the top ~220 by positive+negative, then
   `request=appdetails&appid=N` (4 threads, retry) to get weighted player tags.
4. Keep a title only if a genre tag is in its TOP 5 player tags; rank by total reviews.
   SteamSpy tag lists also contain wrong hits (GTA IV under Incremental), which this filter removes.
5. Tally per tier (5/10/20/all): F2P share, median paid price, median % positive, most
   common side tags. Save a CSV under `~/research/<topic>/`.
6. State the biases: review count favours old games; SteamSpy owners are coarse bands;
   release_date often empty in appdetails.

## Reading the tiers
- Top 5-10 are usually incumbents (pre-Steam browser/mobile hits, F2P live service, IP).
  Say they are not copyable. The copyable tier is where cheap paid solo titles appear.

## Incremental genre findings (2026-10, re-verify)
- Top 5: Cookie Clicker, Clicker Heroes, AdVenture Capitalist, Leaf Blower Revolution,
  Cell to Singularity: 4/5 F2P, endless, multi-layer prestige, 5+ years of updates.
- Top 98: 43% F2P, paid median $4.79, median 87% positive.
- Copyable wave: Nodebuster, (the) Gnorp Apologue, Digseum, Tower Wizard, The Farmer Was
  Replaced, Rusty's Retirement: $3-5, 2-8 h with an ending, one active verb, one twist
  (roguelite / programming / desktop overlay), readable clips, no ads/energy/pay-to-skip,
  96-98% positive.
- Adjacent incumbents checked: Sandustry (solo falling-sand factory, ~12.5K peak CCU, 97%,
  $13); AI Learns To Drive (neural-net racer, 16 reviews/30 days, weak demand); Voxel
  Breakers (voxel teardown incremental, Steam demo).

## Design principles to cite
- New mechanic every 10-20 min; prestige must feel like a reward and later layers change
  rules; next upgrade always visible and near; offline progress; an ending.
- Psych sources (verified): goal-gradient (Kivetz et al. 2006), endowed progress (Nunes &
  Dreze 2006), SDT in games (Ryan, Rigby & Przybylski 2006), flow (Csikszentmihalyi),
  suboptimal choice with win signals in pigeons (Stagner & Zentall 2010; Zentall & Stagner
  2011: 20% x 10 pellets vs sure 3; preference needs an immediate win cue), enrichment
  reduces it (Pattison, Laude & Zentall 2013), losses disguised as wins (Dixon et al. 2010).
  Common errors in pasted summaries: Skinner never measured dopamine (Schultz, 1990s);
  his "superstition" pigeons were on fixed-time food; slots use variable-ratio.
