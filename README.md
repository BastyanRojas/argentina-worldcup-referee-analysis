# Does Argentina Get Favorable Treatment From World Cup Referees?

A small, reproducible data project testing a popular claim: that Argentina is favored
by referees — especially on penalty kicks — at the FIFA World Cup. Focus: **2022 (Qatar,
complete)** and **2026 (ongoing, provisional data)**.

## Design

**Subject:** Argentina in 2022 + 2026. **Control:** the rest of World Cup history.
The question is how extreme Argentina's penalty haul is against that historical baseline.

## TL;DR

- **All-time record:** Argentina's **5 penalties in 2022 is the most ever awarded to a
  single team in one World Cup** — no team in ~90 years had exceeded 4 (Netherlands 1978,
  Portugal 1966). That's the 100th percentile of the whole historical distribution.
- **Within 2022:** those 5 were **21.7% of the 23 penalties in the entire tournament** —
  to one of 32 teams.
- **Rate test vs the VAR-era baseline (0.20 penalties/team/match):**
  - 2022 → 3.5× expected, **p = 0.015** (significant)
  - 2026 (provisional) → 2.0× expected, p = 0.27 (not significant; only 5 games)
  - **2022 + 2026 pooled → 2.9× expected, p = 0.013** (significant)
- **The 2026 twist:** Argentina were awarded ≥2 penalties again — but **Messi missed both**,
  the first player ever to miss two in a single World Cup. "Gets the calls" ≠ "always benefits."
- **Counter-evidence (2022):** the same refs booked them **16 times in 7 games** and put
  them in the most-carded match in World Cup history. Not "teacher's pet."

This repo is built to be **credible under scrutiny**, not to win an argument. The
counter-evidence is reported alongside the headline, because on LinkedIn the comment
section will find it anyway. **Significance is not intent** — an outlier this size can also
come from a possession-heavy side that lives in the opponent's box.

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/analyze.py             # 2022 single-tournament deep-dive
python src/baseline_comparison.py # Argentina (2022+2026) vs World Cup history
```

Outputs regenerate `reports/FINDINGS.md`, `reports/BASELINE_FINDINGS.md`, and charts in `figures/`.

## Repo layout

| Path | What it is |
|------|-----------|
| `data/argentina_2022_matches.csv` | Argentina's 7 matches: penalties for/against, results |
| `data/tournament_baseline_2022.csv` | 2022 tournament totals used as the single-tournament baseline |
| `data/tournament_penalty_totals.csv` | Per-tournament penalty totals (VAR-era control group) |
| `data/team_tournament_penalty_records.csv` | All-time "most penalties to one team" record holders |
| `data/argentina_subject.csv` | Argentina 2022 + 2026 penalty counts (the subject) |
| `data/argentina_2026_incidents_provisional.csv` | Best-effort 2026 refereeing incidents (provisional) |
| `data/SOURCES.md` | Every figure's provenance and confidence level |
| `src/analyze.py` | 2022 single-tournament Poisson test → `FINDINGS.md` + figures |
| `src/baseline_comparison.py` | Argentina (2022+2026) vs World Cup history → `BASELINE_FINDINGS.md` + figures |
| `reports/FINDINGS.md` / `reports/BASELINE_FINDINGS.md` | Auto-generated results |
| `reports/METHODOLOGY.md` | How the tests work and their limits |
| `reports/linkedin_post.md` | Drafted posts, ready to adapt |

## A note on honesty

The point of the project was to test a claim, not to launder a conclusion. The 2022
penalty finding is real and holds up. The framing throughout is deliberately careful:
an outlier is evidence worth discussing, not proof of intent. See
[`reports/METHODOLOGY.md`](reports/METHODOLOGY.md) for the caveats.

**2026 data is provisional** — collected from live reporting while the tournament is
ongoing and should be re-verified before publication.
