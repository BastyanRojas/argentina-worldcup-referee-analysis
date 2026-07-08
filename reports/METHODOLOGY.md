# Methodology & Limitations

## The question

Did Argentina receive open-play penalties at a rate far above what the tournament
baseline predicts, by a margin unlikely to arise from chance alone?

Note the scope. This is a question about **penalty frequency**, not about intent,
corruption, or whether any individual call was correct. Statistics can flag an outlier;
they cannot read a referee's mind.

## The test

We treat penalties awarded to a team as a count process and model it as **Poisson**,
which is standard for rare, independent-ish events over a fixed exposure.

1. **Baseline rate.** 23 open-play penalties were awarded across 64 matches = 128
   team-match observations, so the average is `23 / 128 = 0.180` penalties per
   team-match.
2. **Exposure adjustment.** Argentina played 7 matches (they reached the final). A team
   that plays more games gets more penalty *chances*, so we scale: expected penalties
   `= 0.180 × 7 = 1.26`.
3. **Surprise.** Under `Poisson(λ = 1.26)`, the probability of seeing **5 or more**
   penalties is `p ≈ 0.009`. Argentina got ~4× their expected count.

At α = 0.05 this is significant: the penalty haul is a real outlier, not noise.

## Why we do NOT stop there

A single significant test on a team we singled out *because* it looked extreme is exactly
the setup that produces false positives. Three honest caveats:

- **Selection / multiple comparisons.** With 32 teams, someone leads the penalty table by
  chance. We chose Argentina after noticing they were high — that inflates apparent
  significance. A fully rigorous version would test all 32 teams and correct for it.
- **Style-of-play confounder.** Penalties are partly *earned*. A team that dominates
  possession and attacks inside the box will draw more fouls there. Per-game
  normalization helps but does not isolate "favoritism" from "lots of dangerous touches."
- **Small samples.** Seven games is a short series. Two or three penalty calls swing the
  whole result.

## The counter-evidence (reported, not buried)

- Argentina **conceded 2 penalties** (both in the final) — a rate slightly *above*
  baseline, so they were not shielded defensively.
- They drew **16 yellow cards in 7 games** and featured in the most-carded match in World
  Cup history. Referees were not uniformly lenient toward them.

## Honest conclusion

The penalty-frequency outlier is real and worth discussing. It is **not**, on its own,
proof that referees favored Argentina. The defensible claim is narrow and true; the
sweeping claim is neither. Keep the post on the narrow one.

## Second analysis: subject vs. historical baseline (`baseline_comparison.py`)

A stronger framing that treats **Argentina in 2022 + 2026 as the subject** and **the rest of
World Cup history as the control**:

- **Rate lens.** Compare Argentina's penalties-per-game to the pooled **VAR-era** baseline
  (2018 + 2022 = 52 penalties over 256 team-matches = 0.203/team-match). Using the modern,
  multi-tournament rate is deliberately conservative — it is a *higher* bar than the 2022-only
  rate, so it makes Argentina look *less* extreme, not more. 2022 still clears it
  (3.5×, p = 0.015); 2026 alone does not (small sample); pooled does (2.9×, p = 0.013).
- **Record lens.** Place Argentina in the all-time distribution of "most penalties to one team
  in a single World Cup." Their 5 (2022) is the outright record; the prior max was 4. This is a
  distribution-free statement — no model assumptions — and it is the single most persuasive fact.

The two lenses agree, which matters: a parametric test and a raw historical ranking both put
2022 in the extreme tail.

## Third analysis: exposure, scorecard, placebo (`exposure_and_scorecard.py`)

This is what moves the project past a single penalty count.

- **Exposure model.** The key confounder is attacking volume. We control for it with the
  cleanest available matched comparison: **France, the other 2022 finalist** (same 7 games).
  France took *more* shots (92 vs 76) for *equal* xG (11.5 vs 11.8) yet drew 2.5x fewer
  penalties. Penalties-per-shot, per-xG, and per-game all show Argentina at ~2.5–3x France.
  A team that attacked *more* getting *fewer* penalties is direct evidence the surplus is not
  a volume artifact. (Confounder acknowledged: Argentina's xG/shot was ~15% higher — better
  chance locations — but that cannot account for a 3x penalty gap.)
- **Scorecard.** We report Argentina across seven refereeing-relevant metrics, not just
  penalties, so the nuance is explicit: favored on penalties, *neutral* on shots (France had
  more), and *punished* on discipline (16 yellows, 2 penalties conceded). The defensible claim
  is deliberately narrow.
- **Placebo control.** We run the identical Poisson outlier test on France. It flags Argentina
  (p = 0.015) but not France (p = 0.42) — proof the method isn't just detecting "good teams."
  Historically, no team ever exceeded 4 penalties in an edition, so the placebo also holds
  across all of World Cup history.

**Data-quality note.** Full 32-team shot data is paywalled/blocked (FBref returns 403 to
scrapers), so the exposure model is anchored on the two finalists, whose shot/xG/penalty
figures are individually sourced (xgscore.io). This is the strongest *matched* control but not
a full-field regression — see TODOs.

## Fourth analysis: full 32-team exposure regression (`fullfield_regression.py`)

The definitive version, on real StatsBomb event data (all 64 competitive 2022 matches;
shootouts excluded).

- **Model.** Penalties are Poisson with attacking volume (shots) as exposure: each team's
  expected penalties = (23 total penalties / 1,430 total shots) × its own shots. Fit and
  test all 32 teams at once.
- **Result.** Argentina has the largest positive Pearson residual of the field (+2.78 SD,
  rank 1/32); its shots-adjusted rate is 5.2 penalties/100 shots vs a 1.6 field average.
  The verdict is identical with **xG** as the exposure instead of shots (robustness check).
- **Multiple comparisons — reported straight.** Argentina's raw p = 0.021 (the only team
  under 0.05). But testing 32 teams inflates false positives, so we correct: Bonferroni and
  Benjamini-Hochberg both push Argentina to p ≈ 0.66 — **not significant.** With only five
  penalty events, no single-tournament rate test can survive the strictest correction. We do
  not hide this.
- **Why the conclusion still stands.** It rests on *convergence*, not one number: (1) the
  largest shots- and xG-adjusted residual of all 32 teams; (2) a matched control (France
  attacked *more* for fewer penalties); (3) an all-time record no small-sample fluke
  reproduces. Three independent signals, one direction.

This is the honest ceiling: **a real, field-leading anomaly that the innocent explanations
do not cover — not a proof of intent.**

## To strengthen this further (open TODOs)

- ~~Pull all 32 teams' 2022 penalty counts for a full within-tournament test with a
  multiple-comparisons correction.~~ **Done** — `fullfield_regression.py` (StatsBomb).
- ~~Add an exposure model based on shots, not just games played.~~ **Done** — shots and xG
  exposure, all 32 teams.
- Extend the exposure regression to 2018 + 1990 + 1986 (also in StatsBomb open data) for a
  multi-tournament, mixed-effects version — the natural next escalation.
- Add box-entry / final-third touch exposure (StatsBomb 360 freeze-frames) for an even
  tighter "time spent in dangerous areas" control.
- Backfill 2026 with verified, final numbers once the tournament concludes (counts here are a
  provisional minimum).
