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

## To strengthen this further (open TODOs)

- Pull all 32 teams' 2022 penalty counts for a full within-tournament permutation test with a
  multiple-comparisons correction (the current record lens uses only the tail).
- Add an exposure model based on box touches / shots, not just games played.
- Backfill 2026 with verified, final numbers once the tournament concludes (counts here are a
  provisional minimum).
