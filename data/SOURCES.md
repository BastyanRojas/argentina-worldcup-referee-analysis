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

## StatsBomb open data (primary source for the full-field analysis — highest confidence)

`data/statsbomb_team_stats_2022.csv` is aggregated directly from StatsBomb's free open
event data (all 64 competitive matches of the 2022 World Cup — Group Stage + knockouts, no
friendlies). Penalty shootouts (period 5) are excluded, so counts reflect penalties awarded
in play. Independently reproduces the headline facts: **total penalties = 23; Argentina = 5
for / 2 against in 7 games.**

- StatsBomb open-data: https://github.com/statsbomb/open-data (competition_id 43, season_id
  106 = FIFA World Cup 2022)
- Per-team fields derived: non-penalty shots, non-penalty xG, penalties for/against, fouls
  won/committed, yellow/red cards.

**Competitive tournaments since 2022 (the conspiracy window):**
- `data/statsbomb_team_stats_copa2024.csv` — Copa America 2024 (competition 223, season 282),
  all 32 matches, from StatsBomb open data. **Argentina 2024: 1 penalty for, 1 against, 6
  games — 1.07x the field per-game rate, ranked 4th of 16. They won the tournament.**
- `data/argentina_competitive_2022plus.csv` — Argentina's per-tournament competitive record
  since 2022 (WC 2022 + Copa America 2024 from StatsBomb; 2026 WC provisional). Competitive
  matches only — no friendlies/exhibitions (these are tournament event-data feeds).

**Historical StatsBomb seasons (for the structural-break test):**
- `data/statsbomb_team_stats_2018.csv` — 2018 World Cup (season_id 3), all 64 matches. Confirms
  the reported 29 total penalties. **Argentina 2018: 1 penalty for, 2 against, 4 games — 1.10x
  the field per-game rate, ranked 19th of 32.**
- `data/argentina_penalty_history.csv` — Argentina's per-tournament penalty timeline. 2018 &
  2022 rows are StatsBomb (high confidence); 2010/2014 are approximate (web, low confidence);
  2026 is provisional. 1986 (season_id 54) open data is only partial (3 matches) and is not used.

## Box-exposure dataset (bias identification — highest confidence)

`data/box_exposure_teammatch.csv` — built by `src/build_box_exposure.py` directly from
StatsBomb open event data: WC2018 (64 matches), WC2022 (64), Copa América 2024 (32), one
row per team-match with box touches, box entries, fouls won in the final third, defensive
box contests, penalties for/against (shootouts excluded), shots, xG, and the match referee.
Sanity-checked on rebuild: reproduces WC2018 = 29 total penalties, WC2022 = 23, and
Argentina 2022 = 5 for / 2 against in 7 games.

## Penalty decision quality (Design B — medium confidence, judgment layer)

`data/argentina_2022_penalty_quality.csv` — independent contemporaneous grading of all 7
penalty decisions involving Argentina at WC2022. Verdicts for 5 of 7 come from ESPN's VAR
review (soft / wrong / correct, quoted); the Netherlands QF call (widely accepted) and the
Croatia SF call (pundits split — graded *debatable*) from contemporaneous reporting:

- ESPN — VAR review, every 2022 decision analysed: https://www.espn.com/soccer/story/_/id/37634070/var-review-every-decision-world-cup-analysed
- All Football — Shearer on the Croatia penalty: https://m.allfootballapp.com/news/Headline/Alan-Shearer-insists-it-was-the-RIGHT-decision-to-give-Argentina-an-early-penalty-against-Croatia/2982745
- Eurosport — Modrić: referee "a disaster": https://www.eurosport.com/football/world-cup/2022/luka-modric-says-referee-was-a-disaster-in-croatia-s-world-cup-semi-final-loss-to-argentina-wishes-l_sto9273047/story.shtml
- Football Italia — Dumfries penalty vs Argentina: https://football-italia.net/world-cup-dumfries-gives-away-penalty-in-netherlands-argentina/

The gradings are a judgment layer over reporting — the sign test in
`reports/BIAS_IDENTIFICATION.md` flags this explicitly.

## Field-wide VAR decision dataset (Design E — medium confidence, judgment layer)

`data/var_decisions_2022.csv` — all 45 VAR decisions of WC2022 as graded by ESPN's
tournament-wide audit (the same article as the Argentina-only gradings above),
structured into: match, decision type, team affected, beneficiary, verdict, dubious
flag. Beneficiary semantics: for "awarded" types the listed team is the recipient;
for "disallowed/rejected/cancelled" types the beneficiary is the opponent of the team
affected. Covers VAR-reviewed decisions only — on-field calls VAR silently confirmed
(e.g., Argentina's Netherlands QF and Croatia SF penalties) are absent by
construction. Gradings are one outlet's judgments extracted from prose; treat the
"dubious" flag (soft/debatable/wrong/harsh/missed) as a judgment layer.

Aggregate cross-check from the article: 25 overturns, 10 VAR-awarded penalties
(6 missed), 1 penalty cancelled, 1 retake, 8 offside disallowances.

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
- **Penalty count independently verified (2026-07-07):** TNT Sports confirms both
  penalties — vs Austria (group, VAR-awarded) and vs Egypt (R16: Hassan foul on
  Tagliafico, three minutes after Egypt's opener). Count of 2 stands.
- **2026 field baseline to date (`data/wc2026_field_provisional.csv`): 18 penalties
  awarded in play across 92 matches** (11 in the group stage; 14 converted, 77.8%) =
  0.098/team-match — **roughly half the VAR-era rate**. Reporting notes a "notable
  decline in penalties" this tournament. PROVISIONAL — re-verify at tournament end.
- **Call-quality note:** no independent gradings exist yet for the two 2026 Argentina
  penalties (ESPN's 2026 VAR review does not grade them). The disallowed Egypt goal
  (R16, Attia foul on L. Martínez before Zico's finish) WAS graded: **correct
  intervention** per ESPN. Design B therefore remains 2022-only.

Additional 2026 references:
- Statbunker — penalties awarded WC2026: https://statbunker.com/competitions/ForPenalty?comp_id=790
- YSscores — notable decline in penalty kicks at the 2026 World Cup: https://www.ysscores.com/en/news/13988720/notable-decline-in-penalty-kicks-at-the-2026-world-cup
- FOX Sports — Egypt goal vs Argentina disallowed after VAR check: https://www.foxsports.com/stories/soccer/egypts-goal-vs-argentina-disallowed-after-var-check-not-why-var-brought-game

Reference reporting:
- Al Jazeera — most controversial VAR decisions, group stage: https://www.aljazeera.com/sports/2026/6/28/world-cup-2026-most-controversial-var-officiating-decisions-in-group-stage
- Al Jazeera — Argentina vs Egypt controversy: https://www.aljazeera.com/sports/2026/7/7/why-was-the-second-half-of-the-argentina-vs-egypt-world-cup-game-controversial
- ESPN — World Cup 2026 VAR review: https://www.espn.com/soccer/story/_/id/49027532/world-cup-2026-var-review-red-card-penalty-handball-goal-line-technology
- Cryptobriefing — Argentina awarded penalty after VAR vs Austria: https://cryptobriefing.com/argentina-awarded-penalty-after-var-review-in-world-cup-match-against-austria/
- 2026 FIFA World Cup Group J — Wikipedia: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_J
- TNT Sports — Messi first to miss two penalties in a single World Cup: https://www.tntsports.co.uk/football/world-cup/2026/lionel-messi-first-player-to-miss-two-penalties-same-tournament-egypt_sto23317332/story.shtml
- ESPN — 2026 World Cup MD22 recap (Argentina 3-2 Cape Verde, etc.): https://www.espn.com/espn/story/_/id/49262413/2026-fifa-world-cup-recap-argentina-cape-verde-egypt-australia-colombia-ghana
- FOX Sports — Egypt goal disallowed after VAR foul on L. Martinez: https://www.foxsports.com/watch/fmc-ybved5vdk5xh2ieq
