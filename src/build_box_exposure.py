"""Build team-match box-exposure dataset from StatsBomb open event data.

Purpose: the existing analyses use shots/xG as the penalty-opportunity denominator.
That is a weak proxy — penalties are born from *presence and contests inside the
opponent's box*, not from shooting. This script builds the correct denominator at
the team-match level, for three tournaments:

    World Cup 2018   (competition 43, season 3)    64 matches
    World Cup 2022   (competition 43, season 106)  64 matches
    Copa America 2024 (competition 223, season 282) 32 matches

Per team-match we extract:
  - box_touches      : on-ball events by the team inside the opponent box
                       (passes originating in box, ball receipts, carries ending
                       in box, dribbles, non-penalty shots)
  - box_entries      : completed passes into the box + carries into the box
  - fouls_won_final3 : fouls won in the attacking final third (x >= 80)
  - def_box_contests : the team's *defensive* contested actions inside its OWN box
                       (duels, tackles via duel, fouls committed, blocks, clearances,
                       interceptions) — the symmetric exposure for penalties conceded
  - pens_for / pens_against (open play, periods 1-4 only; shootouts excluded)
  - shots, xg (non-penalty), possession share proxy (pass count share)
  - referee, stage, opponent, score

Output: data/box_exposure_teammatch.csv  (one row per team-match, all 3 tournaments)

Pitch coords: StatsBomb 120x80. Opponent box: x >= 102, 18 <= y <= 62.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TOURNAMENTS = [
    ("WC2018", 43, 3),
    ("WC2022", 43, 106),
    ("Copa2024", 223, 282),
]

BOX_X, BOX_Y_LO, BOX_Y_HI = 102.0, 18.0, 62.0
FINAL3_X = 80.0


def fetch_json(url: str, retries: int = 4) -> object:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - retry on any transient failure
            if attempt == retries - 1:
                raise
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError("unreachable")


def in_opp_box(loc) -> bool:
    return bool(loc) and loc[0] >= BOX_X and BOX_Y_LO <= loc[1] <= BOX_Y_HI


def in_own_box(loc) -> bool:
    # StatsBomb flips coordinates per team: each team always attacks x=120,
    # so a team's OWN box is x <= 18 from its own perspective.
    return bool(loc) and loc[0] <= 120 - BOX_X and BOX_Y_LO <= loc[1] <= BOX_Y_HI


def in_final3(loc) -> bool:
    return bool(loc) and loc[0] >= FINAL3_X


CARD_YELLOWS = {"Yellow Card", "Second Yellow"}
CARD_REDS = {"Red Card", "Second Yellow"}
DZONE_X = 96.0  # dangerous free-kick zone: within ~8m of the box edge


def aggregate_match(events: list, home: str, away: str) -> dict:
    teams = {home, away}
    stats = {
        t: dict(
            box_touches=0, box_entries=0, fouls_won_final3=0, def_box_contests=0,
            pens_for=0, pens_against=0, shots=0, xg=0.0, passes=0,
            # multi-margin decision surface
            fouls_won=0, fouls_committed=0, yellows=0, reds=0, duels=0,
            touches_final3=0, fouls_won_dzone=0,
            fk_shots=0, fk_xg=0.0, pen_xg=0.0,
        )
        for t in teams
    }
    for ev in events:
        period = ev.get("period", 1)
        if period == 5:  # penalty shootout — not referee decisions in play
            continue
        etype = ev["type"]["name"]
        team = ev.get("team", {}).get("name")
        if team not in teams:
            continue
        opp = away if team == home else home
        loc = ev.get("location")

        if etype == "Pass":
            stats[team]["passes"] += 1
            if in_opp_box(loc):
                stats[team]["box_touches"] += 1
            if in_final3(loc):
                stats[team]["touches_final3"] += 1
            end = ev["pass"].get("end_location")
            complete = "outcome" not in ev["pass"]  # SB convention: no outcome = complete
            if complete and end and in_opp_box(end) and not in_opp_box(loc):
                stats[team]["box_entries"] += 1
        elif etype == "Ball Receipt*":
            if "outcome" not in ev.get("ball_receipt", {}):
                if in_opp_box(loc):
                    stats[team]["box_touches"] += 1
                if in_final3(loc):
                    stats[team]["touches_final3"] += 1
        elif etype == "Carry":
            end = ev["carry"].get("end_location")
            if end and in_opp_box(end):
                stats[team]["box_touches"] += 1
                if not in_opp_box(loc):
                    stats[team]["box_entries"] += 1
            if end and in_final3(end):
                stats[team]["touches_final3"] += 1
        elif etype == "Dribble":
            if in_opp_box(loc):
                stats[team]["box_touches"] += 1
            if in_final3(loc):
                stats[team]["touches_final3"] += 1
        elif etype == "Shot":
            shot = ev["shot"]
            stype = shot.get("type", {}).get("name")
            if stype == "Penalty":
                stats[team]["pens_for"] += 1
                stats[opp]["pens_against"] += 1
                stats[team]["pen_xg"] += shot.get("statsbomb_xg", 0.0)
            else:
                stats[team]["shots"] += 1
                stats[team]["xg"] += shot.get("statsbomb_xg", 0.0)
                if in_opp_box(loc):
                    stats[team]["box_touches"] += 1
                if in_final3(loc):
                    stats[team]["touches_final3"] += 1
                if stype == "Free Kick":
                    stats[team]["fk_shots"] += 1
                    stats[team]["fk_xg"] += shot.get("statsbomb_xg", 0.0)
        elif etype == "Foul Won":
            stats[team]["fouls_won"] += 1
            if in_final3(loc):
                stats[team]["fouls_won_final3"] += 1
            if loc and loc[0] >= DZONE_X and not in_opp_box(loc):
                stats[team]["fouls_won_dzone"] += 1
        elif etype == "Foul Committed":
            stats[team]["fouls_committed"] += 1
            card = ev.get("foul_committed", {}).get("card", {}).get("name")
            if card in CARD_YELLOWS:
                stats[team]["yellows"] += 1
            if card in CARD_REDS:
                stats[team]["reds"] += 1
            if in_own_box(loc):
                stats[team]["def_box_contests"] += 1
        elif etype == "Bad Behaviour":
            card = ev.get("bad_behaviour", {}).get("card", {}).get("name")
            if card in CARD_YELLOWS:
                stats[team]["yellows"] += 1
            if card in CARD_REDS:
                stats[team]["reds"] += 1
        elif etype == "Duel":
            stats[team]["duels"] += 1
            if in_own_box(loc):
                stats[team]["def_box_contests"] += 1
        elif etype in ("Block", "Clearance", "Interception"):
            if in_own_box(loc):
                stats[team]["def_box_contests"] += 1
    return stats


def main() -> None:
    rows = []
    for tname, comp, season in TOURNAMENTS:
        matches = fetch_json(f"{BASE}/matches/{comp}/{season}.json")
        print(f"{tname}: {len(matches)} matches")
        for i, m in enumerate(matches, 1):
            mid = m["match_id"]
            home = m["home_team"]["home_team_name"]
            away = m["away_team"]["away_team_name"]
            events = fetch_json(f"{BASE}/events/{mid}.json")
            stats = aggregate_match(events, home, away)
            ref = (m.get("referee") or {}).get("name", "")
            stage = m["competition_stage"]["name"]
            for team, s in stats.items():
                opp = away if team == home else home
                rows.append(dict(
                    tournament=tname, match_id=mid, match_date=m["match_date"],
                    stage=stage, referee=ref, team=team, opponent=opp, **s,
                ))
            if i % 8 == 0:
                print(f"  {tname} {i}/{len(matches)} done")
    df = pd.DataFrame(rows)
    out = DATA / "box_exposure_teammatch.csv"
    df.to_csv(out, index=False)
    print(f"\nWrote {out} ({len(df)} team-match rows)")
    # sanity check against known facts
    for tname, expect in [("WC2018", 29), ("WC2022", 23)]:
        tot = df.loc[df.tournament == tname, "pens_for"].sum()
        print(f"  sanity {tname}: total penalties = {tot} (expected {expect})")
    arg22 = df[(df.tournament == "WC2022") & (df.team == "Argentina")]
    print(f"  sanity Argentina WC2022: pens_for={arg22.pens_for.sum()} (expected 5), "
          f"pens_against={arg22.pens_against.sum()} (expected 2), games={len(arg22)} (expected 7)")
    print(f"  sanity Argentina WC2022 discipline: yellows={arg22.yellows.sum()} "
          f"(~16 reported on-pitch), reds={arg22.reds.sum()} (expected 0), "
          f"fouls_committed={arg22.fouls_committed.sum()}, fouls_won={arg22.fouls_won.sum()}")


if __name__ == "__main__":
    main()
