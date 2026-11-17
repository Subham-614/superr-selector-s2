import os
import pandas as pd
import numpy as np

def run_step1_data_prep(raw_dir: str = "data/raw", out_dir: str = "data/processed") -> pd.DataFrame:
    """
    Step 1: Clean raw CSVs, fix data-engineering traps, and reconstruct 
    exact pre-delivery match states for all 200,999 balls.
    """
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load Raw Datasets
    bbb = pd.read_csv(os.path.join(raw_dir, "ball_by_ball.csv"), low_memory=False)
    matches = pd.read_csv(os.path.join(raw_dir, "matches.csv"))
    comps = pd.read_csv(os.path.join(raw_dir, "competitions.csv"))
    xi = pd.read_csv(os.path.join(raw_dir, "playing_eleven.csv"))

    # 2. Merge Match & Competition Metadata
    matches_clean = matches[[
        "match_id", "comp_id", "match_date", "stage", "venue_id", "venue_country",
        "toss_win_team_id", "toss_opted", "first_inn_revised_overs",
        "second_inn_revised_overs", "revised_target", "knock_out", "win_team_id", "result"
    ]].merge(
        comps[["comp_id", "comp_name", "match_format", "season"]],
        on="comp_id",
        how="left"
    )

    df = bbb.merge(matches_clean, on="match_id", how="left")

    # Separate true IPL seasons from other T20 tournaments (Emerging Asia Cup / Rising Stars) and T20Is
    ipl_comp_ids = [1358, 1715, 2193, 2725, 3298]
    df["comp_tier"] = np.where(
        df["comp_id"].isin(ipl_comp_ids), "IPL",
        np.where(df["match_format"] == "T20I", "T20I", "Other_T20")
    )

    # 3. Sort Chronologically Within Each Match & Innings
    df = df.sort_values(
        ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"]
    ).reset_index(drop=True)

    # 4. Fix Trap #1: True Extra Runs (extras1_runs is an ID code, NOT run count!)
    # Penalty adds 5 runs; wide/Overstep/other/byes/legbyes add 1 + extras_2_runs
    df["extra_runs_team"] = np.where(
        df["extras_type"].isna(), 0,
        np.where(df["extras_type"] == "Penalty", 5, 1 + df["extras_2_runs"].fillna(0))
    )
    df["total_ball_runs"] = df["runs"] + df["extra_runs_team"]

    # Bowler runs conceded excludes byes, legbyes, and penalty extras
    df["bowler_extras"] = np.where(
        df["extras_type"].isin(["wide", "Overstep", "other"]),
        1 + df["extras_2_runs"].fillna(0),
        0
    )
    df["bowler_runs_conceded"] = df["runs"] + df["bowler_extras"]

    # 5. Fix Trap #2: True Legal Balls vs Batter Balls Faced
    # Wides and No-Balls ('Overstep', 'other') do not count as legal balls in the over
    df["is_legal_ball"] = (~df["extras_type"].isin(["wide", "Overstep", "other"])).astype(int)
    # Wides do not count as a ball faced by the striker (No-balls DO count)
    df["is_batter_ball"] = (df["extras_type"] != "wide").astype(int)

    # 6. Fix Trap #3: Wicket Attribution (Team vs Bowler vs Striker)
    df["dismissal_type"] = df["dismissal_type"].replace({
        "Obstracting the field": "Obstructing the field"
    })
    df["is_team_wicket"] = df["is_wicket"].astype(int)

    non_bowler_dismissals = ["RunOut", "Retire Out", "Obstructing the field"]
    df["is_bowler_wicket"] = (
        df["is_wicket"] & (~df["dismissal_type"].isin(non_bowler_dismissals))
    ).astype(int)
    df["is_striker_dismissed"] = (
        df["is_wicket"] & (df["dismissed_player_id"] == df["striker_id"])
    ).astype(int)

    # 7. Reconstruct Pre-Delivery & Post-Delivery Match State
    grp = df.groupby(["match_id", "innings"])

    df["cum_runs_after"] = grp["total_ball_runs"].cumsum()
    df["cum_runs_before"] = df["cum_runs_after"] - df["total_ball_runs"]

    df["cum_wickets_after"] = grp["is_team_wicket"].cumsum()
    df["cum_wickets_before"] = df["cum_wickets_after"] - df["is_team_wicket"]
    df["wickets_in_hand_before"] = (10 - df["cum_wickets_before"]).clip(lower=1)

    df["legal_balls_after"] = grp["is_legal_ball"].cumsum()
    df["legal_balls_before"] = df["legal_balls_after"] - df["is_legal_ball"]

    # Fix Trap #5 & #6: Rain-revised overs columns are already stored in BALLS (e.g. 114, 90, 48)
    df["max_legal_balls"] = np.where(
        df["innings"].isin([3, 4]), 6,
        np.where(
            (df["innings"] == 1) & df["first_inn_revised_overs"].notna(),
            df["first_inn_revised_overs"],
            np.where(
                (df["innings"] == 2) & df["second_inn_revised_overs"].notna(),
                df["second_inn_revised_overs"],
                120
            )
        )
    ).astype(int)

    df["balls_remaining_before"] = (df["max_legal_balls"] - df["legal_balls_before"]).clip(lower=1)
    df["balls_remaining_after"] = (df["max_legal_balls"] - df["legal_balls_after"]).clip(lower=0)

    # 8. First Innings Totals, Target Runs & 2nd Innings Required Run Rate (RRR)
    inn1_totals = (
        df[df["innings"] == 1]
        .groupby("match_id")["cum_runs_after"]
        .max()
        .rename("inn1_total")
    )
    df = df.merge(inn1_totals, on="match_id", how="left")

    df["target_runs"] = np.where(
        df["innings"] == 2,
        np.where(df["revised_target"].notna(), df["revised_target"], df["inn1_total"] + 1),
        np.nan
    )
    df["runs_needed_before"] = np.where(
        df["innings"] == 2,
        (df["target_runs"] - df["cum_runs_before"]).clip(lower=0),
        np.nan
    )

    df["current_run_rate_before"] = np.where(
        df["legal_balls_before"] > 0,
        (df["cum_runs_before"] * 6.0) / df["legal_balls_before"],
        0.0
    )
    df["req_run_rate_before"] = np.where(
        df["innings"] == 2,
        (df["runs_needed_before"] * 6.0) / df["balls_remaining_before"],
        np.nan
    )

    # 9. Innings Phase & Recent Wicket Shock (Wickets Fallen in Last 12 Deliveries)
    df["phase"] = np.where(
        df["innings"].isin([3, 4]), "Super_Over",
        np.where(df["overid"] <= 6, "Powerplay",
        np.where(df["overid"] <= 15, "Middle", "Death"))
    )
    df["recent_wickets_12b"] = grp["is_team_wicket"].transform(
        lambda s: s.shift(1, fill_value=0).rolling(12, min_periods=1).sum()
    )

    # 10. Venue & Competition Par Run Rate Baseline
    venue_stats = df.groupby("venue_id").agg(
        venue_runs=("total_ball_runs", "sum"),
        venue_legal_balls=("is_legal_ball", "sum")
    ).reset_index()
    venue_stats["venue_par_rpo"] = (venue_stats["venue_runs"] * 6.0) / venue_stats["venue_legal_balls"].clip(lower=1)

    tier_stats = df.groupby("comp_tier").agg(
        tier_runs=("total_ball_runs", "sum"),
        tier_legal_balls=("is_legal_ball", "sum")
    ).reset_index()
    tier_stats["tier_par_rpo"] = (tier_stats["tier_runs"] * 6.0) / tier_stats["tier_legal_balls"].clip(lower=1)

    df = df.merge(venue_stats[["venue_id", "venue_legal_balls", "venue_par_rpo"]], on="venue_id", how="left")
    df = df.merge(tier_stats[["comp_tier", "tier_par_rpo"]], on="comp_tier", how="left")

    df["par_rpo"] = np.where(df["venue_legal_balls"] >= 300, df["venue_par_rpo"], df["tier_par_rpo"])
    df["expected_cum_runs_before"] = (df["legal_balls_before"] / 6.0) * df["par_rpo"]
    df["runs_vs_par_before"] = df["cum_runs_before"] - df["expected_cum_runs_before"]

    # 11. Merge Playing XI Role Flags (Captain, Wicketkeeper, Impact Player)
    xi_clean = xi[["match_id", "player_id", "is_captain", "is_wk", "is_impact"]].drop_duplicates(
        subset=["match_id", "player_id"]
    )
    df = df.merge(
        xi_clean.rename(columns={
            "player_id": "striker_id",
            "is_captain": "striker_is_captain",
            "is_wk": "striker_is_wk",
            "is_impact": "striker_is_impact"
        }),
        on=["match_id", "striker_id"],
        how="left"
    )

    out_path = os.path.join(out_dir, "step1_reconstructed_bbb.csv")
    df.to_csv(out_path, index=False)
    print(f"Step 1 complete! Saved {len(df):,} rows to {out_path}")
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_step1_data_prep(
        raw_dir=os.path.join(base_dir, "data", "raw"),
        out_dir=os.path.join(base_dir, "data", "processed")
    )