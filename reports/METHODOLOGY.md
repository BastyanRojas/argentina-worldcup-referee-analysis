# Methodology & Limitations

## The question

Did Argentina receive open-play penalties at a rate far above what the tournament
baseline predicts, by a margin unlikely to arise from chance alone?

Note the scope. This is a question about **penalty frequency**, not about intent,
corruption, or whether any individual call was correct. Statistics can flag an outlier;
they cannot read a referee's mind.

## The treatment variable: penalties *awarded*, not *converted*

The variable under test is the **referee's decision to award a penalty** — the one
event in this chain the officials control:

```
[referee decides] ──► PENALTY AWARDED ──► [taker shoots] ──► GOAL / MISS
   the "box"            ↑ treatment           taker, keeper,     downstream,
   under audit          variable              luck               out of scope
```

Everything to the right of the whistle — whether the kick is scored — depends on the
taker, the goalkeeper, and chance, none of which a referee controls. So **conversion
carries no information about arbitral treatment**, in either direction:

- A *missed* penalty does **not** weaken the award-rate signal. The referee still
  pointed to the spot; the numerator ("penalties awarded") is unchanged. If anything a
  missed-but-awarded penalty is a *cleaner* observation of the referee decision, undiluted
  by the outcome.
- Whether Argentina "benefited" from a penalty is a separate, outcome-level question that
  this project does not test and cannot answer from award counts. Treating a miss as
  counter-evidence to arbitral favoritism is a category error.

Every statistical test in this repo uses **penalties awarded** (`pens_for`), never
penalties converted. Conversion figures (e.g. Messi's two 2026 misses) appear only as
descriptive color and are deliberately kept out of every inferential claim.

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

## Fifth analysis — the structural break (`structural_break.py`) — the one that adds new information

Every other analysis is a 2022 cross-section, so at best it re-expresses the already-known
fact "Argentina got the most penalties in 2022." This test asks the different, thesis-relevant
question: **did their treatment change in 2022?**

- **Argentina as their own control, measured relative to the field each tournament.** The
  field-relative ratio cancels the VAR/era effect (VAR lifted penalties for all teams), leaving
  only the Argentina-specific component.
- **Result (StatsBomb, high confidence):** 2018 → 1 penalty in 4 games = 1.10× the field,
  ranked 19th of 32, Poisson p = 0.60 (indistinguishable from the field). 2022 → 5 in 7 = 4.0×
  the field, ranked 1st, p = 0.009. The advantage **switches on in 2022**, under identical rules.
- **Confounder control.** "They attack a lot / they're elite" is held constant — Argentina were
  elite finalists in 2014 and a strong side in 2018, and drew ~0–1 penalties. Attacking didn't
  change in 2022; the penalty rate did.
- **Honesty flags.** The rigorous claim uses only the two StatsBomb years. Pre-VAR counts
  (2010/2014) are approximate corroboration; 2026 is provisional. The contrast is 5-vs-1, small
  counts — so this shows a *break*, not a proven mechanism, and certainly not intent.

Why this one matters: it is the first result that is **not** common knowledge restated. "Argentina
always got these calls" is falsified — they were the 19th-most-penalized team as recently as 2018.

## Sixth analysis — the conspiracy window (`conspiracy_window.py`) — the scope test

The thesis is "rigged since 2022," so this restricts to 2022→present and widens from World
Cups to *all* competitive tournaments StatsBomb covers in that window (WC 2022 + Copa América
2024; 2026 WC provisional). Friendlies/exhibitions are excluded by construction (these are
tournament event feeds, not warm-ups). Each tournament is measured against its own field,
which cancels competition-specific refereeing tendencies.

- **Result.** 2022 World Cup: 4.0× the field, #1 of 32 (p = 0.009). Copa América 2024: **1.1×
  — dead average**, 1 penalty in 6 games, ranked 4th (p = 0.61), *despite winning the trophy*.
  2026 World Cup (provisional): ~2×.
- **Interpretation, reported straight.** The blanket claim "Argentina is rigged in every
  competitive match" is **false** in this data — Copa América 2024 is ordinary. The supported
  claim is narrower and stronger: **the penalty anomaly is specific to the FIFA World Cup**
  (2022, and again 2026), and absent at the CONMEBOL-run Copa América.
- **Why we keep the Copa result front-and-centre.** It is the honest control. A version that
  omitted it would be cherry-picking; including it is what lets the World-Cup-specific contrast
  survive scrutiny.

This reframes the entire project's takeaway: not "Argentina is favoured," but "since 2022
Argentina has drawn ~4× the field's penalties *at the World Cup* while being completely average
elsewhere competitive." Striking, and true.

## Seventh analysis — bias identification (`bias_identification.py`) — testing bias, not just anomaly

Every prior analysis flags an *anomaly* and stops at "this does not prove bias." That
stopping point conflated two meanings of "bias." **Intent** (a referee *meaning* to favor a
team) is unidentifiable from outcome data — that limit stands. But **bias as a behavioral
asymmetry in decisions** — the estimand of the refereeing-bias literature (Price & Wolfers
2010; Garicano, Palacios-Huerta & Prendergast 2005) — is empirically identifiable, and this
analysis tests it directly with four designs on raw StatsBomb event data (160 matches,
`data/box_exposure_teammatch.csv` built by `build_box_exposure.py`):

- **A. Opportunity-conditioned rate.** Replaces shots with the correct denominator — touches
  in the opponent's box (referee-independent, unlike fouls). Exact multinomial inference, plus
  an exact Westfall-Young family-wise test that replaces Bonferroni.
- **B. Decision-quality asymmetry.** Independent contemporaneous grading of all 7 penalty
  decisions involving Argentina (ESPN VAR review + pundit consensus): do *dubious* calls
  break one way? (4/4 did.)
- **C. Difference-in-differences.** Poisson GLM, tournament fixed effects, box-touch offsets,
  Argentina × WC2022 interaction — Argentina's own 2018 and Copa 2024 as their control.
- **D. Symmetry test.** A real bias should also shield the defense. It does not — reported
  against ourselves.

The verdict **forks on pre-registration**: treating 2022 as a fishing expedition, the
family-wise exact p ≈ 0.30 on frequency. Treating "Argentina" as the documented standing
accusation (Modrić Dec 2022; van Gaal's 'premeditated', Sept 2023 — strictly before Copa
2024 and all 2026 data), the combined evidence reaches p ≈ 0.016 under the primary
specification — with every conservative variant (exposure-conditioned quality null,
VAR-era 2026 baseline, ~5-accusation multiplicity) landing between 0.03 and 0.05 —
and **favorable treatment on penalty awards is demonstrated as a behavioral asymmetry**,
while intent remains out of scope. Both branches are reported in
`reports/BIAS_IDENTIFICATION.md`; the fork itself is the honest answer.

## Eighth analysis — multi-margin surface, leverage gradient, field-wide call quality (`multimargin_leverage.py`)

Closes the two objections the identification study left open. **Design M** tests five
referee-discretion margins (penalties, dangerous FKs, fouls won, cards received per foul,
opponents' cards), each with its own exposure: the asymmetry is **penalty-only** —
generalized favoritism is false in this data. **Design L** ranks margins by goal-equivalent
leverage (penalty ≈ 0.78, calibrated from event data): Argentina's treatment-vs-leverage
gradient ranks 3/32 — favored precisely where a decision is worth the most. **Design E**
structures ESPN's full VAR audit (45 graded decisions) into `data/var_decisions_2022.csv`:
Argentina benefited from **4 of the tournament's 12 dubious decisions** (most of any team;
no other team above 2), joint exact p = 0.003 under the match-uniform null, and **selection-corrected p between
0.021 and 0.05** depending on the allocation null (match-uniform vs decision-conditioned —
neither dominates; both reported). The only full-field multiplicity-corrected evidence in
the project. Caveats: one outlet's gradings, binarized non-blind; covers VAR-reviewed
decisions only (excludes Argentina's two on-field knockout penalties — a bias *against*
the finding). Results in `reports/MULTIMARGIN_FINDINGS.md`.

## Methodological references (design → statistical lineage)

**Domain (referee bias):**
- Price & Wolfers (2010), *QJE* — racial bias among NBA referees; the estimand template.
- Garicano, Palacios-Huerta & Prendergast (2005), *REStat* — favoritism under social pressure.
- Pope & Pope (2015), *Economic Inquiry* — own-nationality bias in Champions League referees.
- Dohmen & Sauermann (2016), *J. Economic Surveys* — survey of the referee-bias literature.

**Design A (opportunity-conditioned rates):**
- Breslow & Day (1987), IARC Vol. II — the observed/expected construction is a standardized
  incidence ratio; exact conditional Poisson tests.
- Westfall & Young (1993) — resampling-based multiple testing (the min-p family-wise test).
- Garwood (1936), *Biometrika* — exact Poisson confidence intervals.

**Designs B/E (decision-quality grading):**
- Sutter & Kocher (2004), *J. Economic Psychology* — home bias tested against the *Kicker*
  expert panel's grading of whether awarded penalties were justified.
- Dohmen (2008), *Economic Inquiry* — graded goal/penalty decisions + multi-margin strategy
  (stoppage time, goals, penalties) — also the precedent for Design M.
- Erikstad & Johansen (2020), *Frontiers Sports Act. Living* — conditioning on independently
  identified "potential penalty situations".

**Design C (difference-in-differences):**
- Angrist & Pischke (2009) — DiD identification. McCullagh & Nelder (1989) — Poisson GLM
  with offsets. Conley & Taber (2011), *REStat* — inference with a small number of treated
  units (why C triangulates rather than carries the inference).

**Design D (defensive symmetry):**
- Lipsitch, Tchetgen Tchetgen & Cohen (2010), *Epidemiology* — negative control outcomes
  for detecting confounding; Design D is exactly this.

**Designs M/L (specificity & gradient):**
- Hill (1965), *Proc. R. Soc. Med.* — the specificity and (dose-)gradient criteria for
  causal claims from observational data.
- Parsons, Sulaeman, Yates & Hamermesh (2011), *AER* — umpire bias concentrated in
  high-discretion, low-scrutiny calls; the signature Design L tests for.

**Combination & pre-registration:**
- Fisher (1925) — combination of independent p-values.
- Nosek, Ebersole, DeHaven & Mellor (2018), *PNAS* — the pre-registration framework behind
  the registered predictions P1–P4.

## Pre-registered predictions (registered 2026-07-07, tournament ongoing)

Because the 2026 World Cup is still in progress, the paper registers falsifiable
predictions NOW — the git history timestamps them, making the end-of-tournament tests
ex-ante by construction (see `latex/main.tex`, Section "Future work"):

- **P1 — verification:** the provisional 2026 quantities (Argentina 2 pens / 5 games;
  field 18 / 92 matches) survive event-data verification within one penalty.
- **P2 — frequency (direction only):** Argentina's remaining 2026 matches continue at or
  above the concurrent field penalty rate.
- **P3 — quality (the sharp one):** end-of-tournament VAR audits will show dubious
  decisions in Argentina matches disproportionately favoring Argentina, leading or
  co-leading the field — the out-of-sample replication of Design E. This dataset does not
  exist yet, so the prediction is fully open.
- **P4 — falsifiers registered:** blind re-grading rating the calls predominantly correct
  collapses Designs B/E; a penalty excess at Copa América 2028 breaks WC-specificity; a
  ~1x box-touch-adjusted 2026 fold leaves 2022 as a one-tournament anomaly.

## To strengthen this further (open TODOs)

- ~~Pull all 32 teams' 2022 penalty counts for a full within-tournament test with a
  multiple-comparisons correction.~~ **Done** — `fullfield_regression.py` (StatsBomb).
- ~~Add an exposure model based on shots, not just games played.~~ **Done** — shots and xG
  exposure, all 32 teams.
- ~~Extend the exposure regression to multiple tournaments for a mixed-effects version.~~
  **Done** — `bias_identification.py` Design C (WC2018 + WC2022 + Copa 2024 DiD).
- ~~Add box-entry / final-third touch exposure for a tighter "time spent in dangerous areas"
  control.~~ **Done** — `build_box_exposure.py` + `bias_identification.py` Design A
  (box touches, box entries, and fouls-won exposures).
- ~~Extend Design B (call-quality grading) to the full field.~~ **Done for VAR-reviewed
  decisions** — `multimargin_leverage.py` Design E (45 ESPN-graded decisions). Remaining:
  a *blind*, multi-assessor grading that also covers on-field non-reviewed calls and
  major non-calls — that removes the outlet dependence and the reviewed-only selection.
- Referee-assignment analysis: FIFA appointment records to test whether penalty-generous
  officials were disproportionately assigned to Argentina matches.
- Backfill 2026 with verified, final numbers once the tournament concludes (counts here are a
  provisional minimum).
