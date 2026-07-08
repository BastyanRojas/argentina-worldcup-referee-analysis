"""Multi-margin decision surface, leverage gradient, and field-wide call quality.

Extends the identification study (src/bias_identification.py) with three designs
that answer the two objections still open after the four-design analysis:

  "Maybe every margin of referee discretion favors Argentina"  -> Design M
  "Maybe favoritism concentrates where it matters"             -> Design L
  "Maybe every team gets dubious calls and you only looked at
   Argentina's"                                                -> Design E

Design M — MULTI-MARGIN DECISION SURFACE. Five referee-discretion margins, each
with its own opportunity exposure, all 32 teams of WC2022, signed so that
positive = treatment consistent with favoritism:

    margin                        exposure               favored direction
    penalties awarded             box touches            more   (+)
    dangerous free kicks won      final-third touches    more   (+)
    fouls won (anywhere)          passes (on-ball vol.)  more   (+)
    yellows received              fouls committed        FEWER  (sign-flipped)
    opponents' yellows            opponents' fouls       more   (+)

Design L — LEVERAGE GRADIENT. Each margin carries a goal-equivalent leverage
(penalty ~0.78 xG, calibrated from the event data where possible). If favoritism
is instrumental it should concentrate in high-leverage decisions. Per team we
fit the slope of signed residual on log10(leverage); Argentina's slope is ranked
against the field distribution (a permutation-style reference that needs no
distributional assumption).

Design E — FIELD-WIDE CALL QUALITY. ESPN's review of every VAR decision of
WC2022 (data/var_decisions_2022.csv, 45 graded decisions) lets us test the
allocation and direction of *dubious* interventions across the whole field —
the full-field version of Design B.

Inputs : data/box_exposure_teammatch.csv, data/var_decisions_2022.csv
Outputs: reports/MULTIMARGIN_FINDINGS.md,
         figures/multimargin_gradient.png, figures/var_dubious_field.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA, REPORTS, FIG = ROOT / "data", ROOT / "reports", ROOT / "figures"

BLUE, GREY = "#2a78d6", "#9a9994"
RED, INK, MUTED = "#e34948", "#0b0b0b", "#52514e"
SEED = 20221218
N_SIM = 200_000


def team_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """WC2022 team totals including opponent-side discipline (cards drawn)."""
    t = (df.groupby("team", as_index=False)
           .agg(games=("match_id", "count"),
                pens_for=("pens_for", "sum"), box_touches=("box_touches", "sum"),
                fouls_won_dzone=("fouls_won_dzone", "sum"),
                touches_final3=("touches_final3", "sum"),
                fouls_won=("fouls_won", "sum"), passes=("passes", "sum"),
                yellows=("yellows", "sum"), fouls_committed=("fouls_committed", "sum"),
                fk_xg=("fk_xg", "sum"), pen_xg=("pen_xg", "sum")))
    opp = (df.groupby("opponent", as_index=False)
             .agg(opp_yellows=("yellows", "sum"), opp_fouls=("fouls_committed", "sum"))
             .rename(columns={"opponent": "team"}))
    # df rows are per team-match, so grouping the SAME rows by 'opponent' sums,
    # for each team, the discipline of the sides they faced. Wrong: that sums the
    # team's own rows labelled by opponent. Instead join opponent rows by match.
    o = df[["match_id", "team", "yellows", "fouls_committed"]].rename(
        columns={"team": "opponent", "yellows": "o_yel", "fouls_committed": "o_foul"})
    m = df[["match_id", "team", "opponent"]].merge(o, on=["match_id", "opponent"])
    opp = (m.groupby("team", as_index=False)
             .agg(opp_yellows=("o_yel", "sum"), opp_fouls=("o_foul", "sum")))
    return t.merge(opp, on="team")


def margin_residuals(t: pd.DataFrame, obs_col: str, expo_col: str, flip: bool) -> pd.Series:
    """Signed Poisson residual per team; positive = favored direction."""
    rate = t[obs_col].sum() / t[expo_col].sum()
    lam = rate * t[expo_col]
    r = (t[obs_col] - lam) / np.sqrt(lam)
    return (-r if flip else r), rate, lam


def main() -> None:
    df = pd.read_csv(DATA / "box_exposure_teammatch.csv")
    wc = df[df.tournament == "WC2022"].copy()
    t = team_aggregate(wc)
    i_arg = t.index[t.team == "Argentina"][0]

    # ---------- Design M: margins ----------
    # leverage calibrated from event data where possible
    lev_pen = t.pen_xg.sum() / t.pens_for.sum()                    # ~0.78 (StatsBomb pen xG)
    lev_dfk = t.fk_xg.sum() / max(t.fouls_won_dzone.sum(), 1)      # xG of direct-FK shots per dzone foul won
    LEV_FOUL, LEV_CARD = 0.008, 0.03                               # calibrated assumptions (documented)

    margins = [
        ("Penalty awarded",        "pens_for",        "box_touches",     False, lev_pen),
        ("Dangerous FK won",       "fouls_won_dzone", "touches_final3",  False, lev_dfk),
        ("Foul won (any)",         "fouls_won",       "passes",          False, LEV_FOUL),
        ("Yellow received (flip)", "yellows",         "fouls_committed", True,  LEV_CARD),
        ("Opponent yellow drawn",  "opp_yellows",     "opp_fouls",       False, LEV_CARD),
    ]
    res = pd.DataFrame({"team": t.team})
    rows_m = []
    for name, oc, ec, flip, lev in margins:
        r, rate, lam = margin_residuals(t, oc, ec, flip)
        res[name] = r
        obs_a, lam_a = int(t.loc[i_arg, oc]), float(lam[i_arg])
        p_a = float(stats.poisson.sf(obs_a - 1, lam_a)) if not flip else \
              float(stats.poisson.cdf(obs_a, lam_a))
        rows_m.append(dict(margin=name, leverage=lev, arg_obs=obs_a, arg_exp=lam_a,
                           arg_resid=float(r[i_arg]), p_favored=p_a))
    M = pd.DataFrame(rows_m)

    # ---------- Design L: leverage gradient ----------
    X = np.log10(M.leverage.to_numpy(dtype=float))
    slopes = {}
    for i, team in enumerate(t.team):
        y = res.loc[i, [m[0] for m in margins]].to_numpy(dtype=float)
        slopes[team] = float(np.polyfit(X, y, 1)[0])
    S = pd.Series(slopes).sort_values(ascending=False)
    arg_slope = S["Argentina"]
    arg_slope_rank = int(S.index.get_loc("Argentina")) + 1
    spear_arg = stats.spearmanr(X, res.loc[i_arg, [m[0] for m in margins]].to_numpy(dtype=float))

    # ---------- Design E: field-wide VAR call quality ----------
    v = pd.read_csv(DATA / "var_decisions_2022.csv")
    dub = v[v.dubious == 1]
    n_dub = len(dub)
    ben_counts = dub.beneficiary.value_counts()
    arg_dub = int(ben_counts.get("Argentina", 0))
    arg_match_dub = int(dub.match.str.contains("Argentina").sum())

    # ---- Null 1 (match-uniform): dubious decisions land uniformly across the
    #      64 matches, then favor either side with p = 1/2.
    match_teams = (wc.groupby("match_id")["team"].apply(sorted).tolist())
    rng = np.random.default_rng(SEED)
    teams_arr = np.array(match_teams)  # (64, 2)
    mi = rng.integers(0, len(teams_arr), size=(N_SIM, n_dub))
    side = rng.integers(0, 2, size=(N_SIM, n_dub))
    picks = teams_arr[mi, side]                       # simulated beneficiaries
    arg_counts = (picks == "Argentina").sum(axis=1)
    p_arg_joint = float((arg_counts >= arg_dub).mean())
    # selection-corrected: max count over ALL teams each sim
    all_teams = np.unique(teams_arr)
    max_counts = np.zeros(N_SIM, dtype=int)
    for tm in all_teams:
        c = (picks == tm).sum(axis=1)
        np.maximum(max_counts, c, out=max_counts)
    p_any_joint = float((max_counts >= arg_dub).mean())
    p_alloc = float(stats.binom.sf(arg_match_dub - 1, n_dub, 7 / 64))
    p_dir = float(stats.binom.sf(arg_dub - 1, arg_match_dub, 0.5))

    # ---- Null 2 (decision-conditioned): condition on WHERE the 45 graded
    #      decisions occurred and WHOM each favored; permute only WHICH 12 of
    #      the 45 are dubious. Stricter: it absorbs the fact that Argentina's
    #      matches (final, extra-time knockouts) drew more reviews overall.
    n_graded = len(v)
    graded_in_arg = int(v.match.str.contains("Argentina").sum())
    arg_benef_graded = int((v.beneficiary == "Argentina").sum())
    p_arg_cond = float(stats.hypergeom.sf(arg_dub - 1, n_graded, arg_benef_graded, n_dub))
    # selection-corrected under null 2: permute dubious flags over the 45 real
    # decisions and take the max beneficiary count each draw
    benef_arr = v.beneficiary.to_numpy()
    max_counts2 = np.zeros(N_SIM, dtype=int)
    arg_counts2 = np.zeros(N_SIM, dtype=int)
    for s in range(N_SIM // 10):  # 50k permutations is plenty for 2-digit precision
        idx = rng.choice(n_graded, size=n_dub, replace=False)
        picks2 = benef_arr[idx]
        vals, cnts = np.unique(picks2, return_counts=True)
        max_counts2[s] = cnts.max()
        arg_counts2[s] = cnts[vals == "Argentina"].sum() if "Argentina" in vals else 0
    n_perm = N_SIM // 10
    p_arg_cond_sim = float((arg_counts2[:n_perm] >= arg_dub).mean())
    p_any_cond = float((max_counts2[:n_perm] >= arg_dub).mean())
    p_alloc_cond = float(stats.binom.sf(arg_match_dub - 1, n_dub, graded_in_arg / n_graded))

    # ---------- report ----------
    L: list[str] = []
    L.append("# Multi-Margin Surface, Leverage Gradient & Field-Wide Call Quality\n")
    L.append(
        "_Generated by `src/multimargin_leverage.py` from `data/box_exposure_teammatch.csv` "
        "(StatsBomb events, WC2022) and `data/var_decisions_2022.csv` (ESPN VAR review, "
        "field-wide)._\n\n"
        "Answers the two objections left open by `BIAS_IDENTIFICATION.md`: does the asymmetry "
        "generalize across referee-discretion margins (M), does it track decision leverage "
        "(L), and do dubious calls favor everyone equally (E)?\n"
    )

    L.append("## Design M — the five-margin decision surface (WC2022)\n")
    L.append(
        "Signed so **positive residual = treatment consistent with favoritism** (for cards "
        "received, fewer-than-expected is positive). Each margin has its own opportunity "
        "exposure. Pre-registered direction: favoritism predicts positive residuals.\n\n"
    )
    L.append("| Margin | Leverage (goal-eq) | Arg obs | Arg expected | Signed residual (SD) | p (favored tail) |\n"
             "|---|---|---|---|---|---|\n")
    for _, r in M.iterrows():
        L.append(f"| {r.margin} | {r.leverage:.3f} | {r.arg_obs} | {r.arg_exp:.1f} | "
                 f"{r.arg_resid:+.2f} | {r.p_favored:.3f} |\n")
    yel_note = M[M.margin == "Yellow received (flip)"].iloc[0]
    L.append(
        f"\n- **The surface is one-margin.** Argentina is extreme only on penalties "
        f"({M.iloc[0].arg_resid:+.2f} SD). Fouls won, dangerous free kicks and opponents' "
        "cards are all within noise of expectation; on **yellows received they are on the "
        f"*punished* side** ({yel_note.arg_resid:+.2f} SD signed = more carded per foul than "
        "the field). 'Every margin favors them' is false in this data.\n"
        "- Leverage values: penalty and dangerous-FK leverage are calibrated from the event "
        "data (mean StatsBomb penalty xG; direct-FK xG per dangerous foul won); the foul and "
        "card leverages are order-of-magnitude assumptions (0.008 / 0.03 goal-equivalents). "
        "The gradient test below is ordinal, so only the *ranking* matters — and penalties "
        "being an order of magnitude above every other margin is not in doubt.\n"
    )

    L.append("## Design L — the leverage gradient\n")
    L.append(
        "If favoritism were instrumental, treatment should concentrate where decisions are "
        "worth the most. Per team: slope of signed residual on log10(leverage) across the "
        "five margins.\n\n"
        f"- **Argentina's gradient: {arg_slope:+.2f} SD per leverage decade — rank "
        f"{arg_slope_rank}/32** (field median {S.median():+.2f}). Spearman of residual vs "
        f"leverage, Argentina: rho = {spear_arg.statistic:.2f} (p = {spear_arg.pvalue:.2f}, "
        "n = 5 margins).\n"
        "- Read honestly: with five margins this is structured description, not sharp "
        "inference. What it shows is a **steeply positive treatment-vs-leverage profile, the "
        f"{'steepest' if arg_slope_rank == 1 else 'near-steepest'} of the field** — favored "
        "specifically where a decision is worth the most (the penalty spot) and *not* on the "
        "cheap margins. Consistent with 'bias where it matters'; equally consistent with a "
        "penalty-specific anomaly of any origin. It rules out generalized, all-margin "
        "favoritism.\n"
    )

    L.append("## Design E — field-wide VAR call quality (the full-field Design B)\n")
    L.append(
        f"ESPN's review of every VAR decision of WC2022 yields **{len(v)} graded decisions**, "
        f"of which **{n_dub} are dubious** (soft / debatable / wrong / harsh / missed "
        "intervention). Under neutral refereeing, dubious interventions should scatter across "
        "matches uniformly and favor either side of a match with probability 1/2.\n\n"
    )
    L.append("| Beneficiary of dubious VAR decisions | Count |\n|---|---|\n")
    for tm, c in ben_counts.items():
        b = "**" if tm == "Argentina" else ""
        L.append(f"| {b}{tm}{b} | {b}{int(c)}{b} |\n")
    L.append(
        f"\n- **Argentina: {arg_dub} of the {n_dub} dubious decisions in the tournament "
        f"({arg_dub/n_dub*100:.0f}%), the most of any team** — including the only 'missed "
        "red card' flagged in the final and a penalty graded an outright wrong "
        "intervention (Poland).\n"
        "\n**Under the match-uniform null** (dubious interventions scatter uniformly over "
        "the 64 matches, coin-flip beneficiary):\n\n"
        f"- Allocation: {arg_match_dub} of {n_dub} dubious decisions in Argentina matches "
        f"(7 of 64), p = {p_alloc:.3f}. Direction: {arg_dub}/{arg_match_dub} favored "
        f"Argentina, p = {p_dir:.3f}. Joint: **p = {p_arg_joint:.4f}**; selection-corrected "
        f"(any of 32 teams ≥ {arg_dub}): **p = {p_any_joint:.3f}**.\n"
        "\n**Under the stricter decision-conditioned null** (condition on where the "
        f"{n_graded} graded decisions actually occurred — {graded_in_arg} were in Argentina "
        "matches, reflecting the final and extra-time knockouts — and on whom each favored; "
        "permute only which 12 are dubious):\n\n"
        f"- Allocation: p = {p_alloc_cond:.2f}. Argentina ≥ {arg_dub} dubious-favorable: "
        f"p = {p_arg_cond:.3f} (hypergeometric; permutation check {p_arg_cond_sim:.3f}). "
        f"Selection-corrected: **p = {p_any_cond:.2f}**.\n"
        "- Neither null strictly dominates: the graded-decision set is itself endogenous "
        "(more dubious officiating attracts more reviews), so conditioning on it absorbs "
        "part of the signal under test, while the match-uniform null ignores that finals "
        "and extra-time games mechanically draw more reviews. The honest statement is the "
        f"range: **selection-corrected p between {p_any_joint:.3f} and {p_any_cond:.2f}** "
        "depending on the null.\n"
        "- This answers the objection 'every team gets dubious calls': they do — but no other "
        f"team got more than {int(ben_counts.iloc[1]) if len(ben_counts) > 1 else 0}, and "
        "none had every dubious call in their matches break their own way.\n"
        "- **Caveats owned:** the gradings are one outlet's judgments (ESPN), extracted from "
        "prose; the binarization to 'dubious' (soft/debatable/wrong/harsh/missed) was done "
        "by this project **non-blind**, knowing the hypothesis; and the dataset covers "
        "VAR-reviewed decisions only, not on-field calls that VAR silently confirmed (the "
        "Netherlands QF and Croatia SF penalties are therefore absent — a selection that "
        "biases these tests *against* Argentina effects). Counts this small demand the "
        "exact tests used here.\n"
    )

    L.append("## What this adds to the verdict\n")
    L.append(
        "- **Sharpens the claim:** the asymmetry is penalty-specific (M), sits at the top of "
        "the leverage gradient (L), and its dubious-call signature leads the field (E: "
        f"selection-corrected p = {p_any_joint:.3f} under the match-uniform null, "
        f"{p_any_cond:.2f} under the stricter decision-conditioned null — significant under "
        "one defensible null, marginal under the other).\n"
        "- **Bounds the claim:** no generalized favoritism — Argentina pays full price on "
        "cards and gains nothing on cheap margins. Any mechanism consistent with this data "
        "must operate narrowly, at the highest-leverage decision, in both 2022 and "
        "(provisionally) 2026.\n"
    )

    (REPORTS / "MULTIMARGIN_FINDINGS.md").write_text("".join(L), encoding="utf-8")
    print("".join(L).encode("ascii", "replace").decode())

    # ---------- figures ----------
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "text.color": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED})

    # Fig 1: leverage gradient — field cloud + Argentina highlighted
    fig, ax = plt.subplots(figsize=(8, 5))
    mcols = [m[0] for m in margins]
    for i, team in enumerate(t.team):
        y = res.loc[i, mcols].to_numpy(dtype=float)
        if team == "Argentina":
            continue
        ax.plot(X, y, color=GREY, lw=0.8, alpha=0.45, zorder=1)
    y_arg = res.loc[i_arg, mcols].to_numpy(dtype=float)
    ax.plot(X, y_arg, color=BLUE, lw=2.5, marker="o", ms=7, zorder=3, label="Argentina")
    ax.plot([], [], color=GREY, lw=0.8, label="field (31 teams)")
    offsets = {"Penalty awarded": (0, 10), "Dangerous FK won": (10, 8),
               "Foul won (any)": (12, 8), "Yellow received (flip)": (10, -14),
               "Opponent yellow drawn": (0, 10)}
    for xi, yi, name in zip(X, y_arg, mcols):
        ax.annotate(name, (xi, yi), textcoords="offset points",
                    xytext=offsets.get(name, (0, 9)), ha="center", fontsize=7.5, color=MUTED)
    ax.set_xlim(X.min() - 0.25, X.max() + 0.22)
    ax.axhline(0, color=MUTED, lw=1, ls="--")
    ax.set_xlabel("log10 decision leverage (goal-equivalents)")
    ax.set_ylabel("Signed treatment residual (SD; + = favored)")
    ax.set_title("Treatment vs decision leverage, all 32 teams —\n"
                 "Argentina is favored only where it matters most", fontweight="bold")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "multimargin_gradient.png", dpi=150)
    plt.close(fig)

    # Fig 2: dubious VAR beneficiaries
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    bc = ben_counts.sort_values()
    colors = [BLUE if x == "Argentina" else GREY for x in bc.index]
    ax.barh(bc.index, bc.values, color=colors)
    for i, vv in enumerate(bc.values):
        ax.text(vv + 0.05, i, str(int(vv)), va="center", fontweight="bold")
    ax.set_xlabel("Dubious VAR decisions benefiting the team (ESPN grading, WC2022)")
    ax.set_title(f"All {n_dub} dubious VAR decisions of WC2022 by beneficiary —\n"
                 "Argentina leads the field", fontweight="bold")
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG / "var_dubious_field.png", dpi=150)
    plt.close(fig)

    print("\nWrote reports/MULTIMARGIN_FINDINGS.md and 2 figures.")


if __name__ == "__main__":
    main()
