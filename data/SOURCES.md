# Data Sources & Provenance

All figures were gathered from public reporting in July 2026. Penalty counts for 2022
are high-confidence and cross-checked; disciplinary and 2026 figures are labeled by
confidence. **Verify every number against primary sources before publishing.**

## 2022 World Cup (high confidence)

- Argentina awarded **5 open-play penalties** — reported as the most by any single team
  in one World Cup edition. Match-by-match: vs Saudi Arabia (scored), vs Poland (missed),
  vs Netherlands QF (scored), vs Croatia SF (scored), vs France Final (scored).
- Argentina **conceded 2 penalties**, both to France in the final (Mbappé).
- Tournament total: **23 open-play penalties** across 64 matches.
- Argentina: **16 yellow cards, 0 red cards** across 7 matches.
- Argentina vs Netherlands set the World Cup record for most yellow cards in a match (18).

Reference reporting:
- beIN Sports — Argentina's penalties in Qatar 2022: https://www.beinsports.com/en-us/soccer/fifa-world-cup-2026/articles-video/argentina-s-penalties-in-qatar-2022-refereeing-decisions-that-divided-opinion-2026-06-05
- ESPN — 2022 World Cup VAR review, every decision: https://www.espn.com/soccer/story/_/id/37634070/var-review-every-decision-world-cup-analysed
- 2022 FIFA World Cup Final — Wikipedia: https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_final
- Statbunker penalties awarded 2022: https://www.statbunker.com/competitions/ForPenalty?comp_id=727
- Guinness World Records — most yellow cards in a WC match: https://www.guinnessworldrecords.com/world-records/730722-most-yellow-cards-issued-in-a-fifa-world-cup-match

## Historical baseline / control group (high confidence)

Used by `src/baseline_comparison.py` to place Argentina against World Cup history.

- **2018 World Cup: 29 penalties awarded** across 64 matches — the record tournament
  total, following VAR's debut.
- **2022 World Cup: 23 penalties awarded** across 64 matches.
- **All-time team record:** Argentina's 5 penalties in 2022 is the most ever awarded to a
  single team in one World Cup. The previous record was 4, shared by the Netherlands
  (1978) and Portugal (1966).

Reference reporting:
- The18 — Argentina break record for most penalties awarded to one team: https://the18.com/en/soccer-news/world-cup-2022/argentina-awarded-most-penalty-kicks-in-world-cup-history
- Cryptobriefing — World Cup penalty statistics, record 29 in 2018: https://cryptobriefing.com/fifa-world-cup-penalty-statistics-2018-record/
- Statbunker penalties awarded 2018: https://www.statbunker.com/competitions/ForPenalty?comp_id=607
- Wego — World Cup penalty records: https://blog.wego.com/world-cup-penalty-records/

## 2026 World Cup (PROVISIONAL — outside model training data, tournament ongoing)

Collected from live web reporting. Treat as provisional; the bracket/date details
across sources were not fully consistent and must be re-verified.

- Argentina Group J: def. Algeria 3-0, Austria 2-0 (VAR penalty), Jordan 3-1.
- Knockout: def. Cape Verde 3-2 aet (R32), def. Egypt 3-2 (R16, Jul 7).
- **Penalties awarded to Argentina in 2026: at least 2** (vs Austria, vs Egypt),
  **both missed by Messi** — the first player to miss two penalties in a single World
  Cup. Count is a confirmed minimum; treat as provisional.
- Argentina had played **5 matches** as of 2026-07-07.

Reference reporting:
- Al Jazeera — most controversial VAR decisions, group stage: https://www.aljazeera.com/sports/2026/6/28/world-cup-2026-most-controversial-var-officiating-decisions-in-group-stage
- Al Jazeera — Argentina vs Egypt controversy: https://www.aljazeera.com/sports/2026/7/7/why-was-the-second-half-of-the-argentina-vs-egypt-world-cup-game-controversial
- ESPN — World Cup 2026 VAR review: https://www.espn.com/soccer/story/_/id/49027532/world-cup-2026-var-review-red-card-penalty-handball-goal-line-technology
- Cryptobriefing — Argentina awarded penalty after VAR vs Austria: https://cryptobriefing.com/argentina-awarded-penalty-after-var-review-in-world-cup-match-against-austria/
- 2026 FIFA World Cup Group J — Wikipedia: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_J
- TNT Sports — Messi first to miss two penalties in a single World Cup: https://www.tntsports.co.uk/football/world-cup/2026/lionel-messi-first-player-to-miss-two-penalties-same-tournament-egypt_sto23317332/story.shtml
- ESPN — 2026 World Cup MD22 recap (Argentina 3-2 Cape Verde, etc.): https://www.espn.com/espn/story/_/id/49262413/2026-fifa-world-cup-recap-argentina-cape-verde-egypt-australia-colombia-ghana
- FOX Sports — Egypt goal disallowed after VAR foul on L. Martinez: https://www.foxsports.com/watch/fmc-ybved5vdk5xh2ieq
