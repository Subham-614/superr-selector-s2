import os
import pandas as pd
import numpy as np

def run_step3_player_rankings(
    in_path: str = "data/processed/step2_pressure_indexed_bbb.csv",
    teams_path: str = "data/raw/teams.csv",
    out_dir: str = "data/processed"
):
    """
    Step 3: Compute context-adjusted RAAE, opposition-tier weights, baseline vs.
    high-pressure deltas, and Empirical Bayes smoothed rankings for batters & bowlers.
    """
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(in_path, low_memory=False)
    teams_df = pd.read_csv(teams_path)[["team_id", "team_name"]].drop_duplicates(subset=["team_id"])

    # -------------------------------------------------------------------------
    # 1. Opposition Quality Tier Mapping (Fair IPL & T20I Comparisons)
    # -------------------------------------------------------------------------
    df = df.merge(
        teams_df.rename(columns={"team_id": "batting_team_id", "team_name": "batting_team_name"}),
        on="batting_team_id", how="left"
    ).merge(
        teams_df.rename(columns={"team_id": "bowling_team_id", "team_name": "bowling_team_name"}),
        on="bowling_team_id", how="left"
    )

    ipl_teams = {
        "Chennai Super Kings", "Mumbai Indians", "Rajasthan Royals", "Punjab Kings",
        "Royal Challengers Bengaluru", "Delhi Capitals", "Kolkata Knight Riders",
        "Sunrisers Hyderabad", "Gujarat Titans", "Lucknow Super Giants"
    }
    elite_t20i = {
        "India", "Australia", "England", "South Africa", "New Zealand",
        "West Indies", "Pakistan", "Sri Lanka", "Afghanistan"
    }
    full_member_2 = {"Bangladesh", "Ireland", "Zimbabwe", "Netherlands", "Scotland"}

    def get_opp_weight(team_name: str) -> float:
        if team_name in ipl_teams:
            return 1.15
        elif team_name in elite_t20i:
            return 1.05
        elif team_name in full_member_2:
            return 0.85
        return 0.60

    df["opp_bowling_weight"] = df["bowling_team_name"].apply(get_opp_weight)
    df["opp_batting_weight"] = df["batting_team_name"].apply(get_opp_weight)

    # -------------------------------------------------------------------------
    # 2. Contextual Par Expectations (Competition Tier x Innings x Phase x Pace/Spin)
    # -------------------------------------------------------------------------
    df["pace_or_spin_clean"] = df["pace_or_spin"].fillna("Pace")
    ctx_cols = ["comp_tier", "innings", "phase", "pace_or_spin_clean"]

    ctx_stats = df.groupby(ctx_cols).agg(
        ctx_bat_runs=("runs", "sum"),
        ctx_bat_balls=("is_batter_ball", "sum"),
        ctx_bowler_runs=("bowler_runs_conceded", "sum"),
        ctx_legal_balls=("is_legal_ball", "sum"),
        ctx_striker_wkts=("is_striker_dismissed", "sum"),
        ctx_bowler_wkts=("is_bowler_wicket", "sum")
    ).reset_index()

    ctx_stats["exp_bat_runs_pb"] = ctx_stats["ctx_bat_runs"] / ctx_stats["ctx_bat_balls"].clip(lower=1)
    ctx_stats["exp_striker_wkt_pb"] = ctx_stats["ctx_striker_wkts"] / ctx_stats["ctx_bat_balls"].clip(lower=1)
    ctx_stats["exp_bowl_runs_pb"] = ctx_stats["ctx_bowler_runs"] / ctx_stats["ctx_legal_balls"].clip(lower=1)
    ctx_stats["exp_bowl_wkt_pb"] = ctx_stats["ctx_bowler_wkts"] / ctx_stats["ctx_legal_balls"].clip(lower=1)

    df = df.merge(
        ctx_stats[ctx_cols + ["exp_bat_runs_pb", "exp_striker_wkt_pb", "exp_bowl_runs_pb", "exp_bowl_wkt_pb"]],
        on=ctx_cols, how="left"
    )

    # Venue flatness adjustment
    venue_mult = (df["par_rpo"] / df["tier_par_rpo"].clip(lower=6.0)).clip(0.80, 1.25)
    df["exp_bat_runs_adj"] = df["exp_bat_runs_pb"] * venue_mult
    df["exp_bowl_runs_adj"] = df["exp_bowl_runs_pb"] * venue_mult

    # Continuous High-Pressure Intensity Weight (1.0 at 75th pct up to 2.0 at P=100)
    p_cutoff = np.percentile(df["pressure_index"], 75)
    df["hp_intensity"] = np.where(
        df["is_high_pressure"] == 1,
        1.0 + ((df["pressure_index"] - p_cutoff) / (100.0 - p_cutoff)).clip(0, 1),
        1.0
    )

    # Balanced Run-vs-Wicket Value (LAMBDA_BAT = 12.0 balances SR and survival; LAMBDA_BOWL = 16.0 balances Economy and Wickets)
    df["bat_raae"] = np.where(
        df["is_batter_ball"] == 1,
        ((df["runs"] - df["exp_bat_runs_adj"]) - 12.0 * (df["is_striker_dismissed"] - df["exp_striker_wkt_pb"]))
        * df["opp_bowling_weight"] * df["hp_intensity"],
        0.0
    )

    df["bowl_raae"] = np.where(
        df["is_legal_ball"] == 1,
        ((df["exp_bowl_runs_adj"] - df["bowler_runs_conceded"]) + 16.0 * (df["is_bowler_wicket"] - df["exp_bowl_wkt_pb"]))
        * df["opp_batting_weight"] * df["hp_intensity"],
        -df["bowler_runs_conceded"] * df["opp_batting_weight"] * df["hp_intensity"]
    )

    # Non-striker dismissals for accurate batting average
    non_striker_ro = df[(df["is_wicket"] == True) & (df["dismissed_player_id"] != df["striker_id"])]
    ns_base = non_striker_ro[non_striker_ro["is_high_pressure"] == 0].groupby("dismissed_player_id").size().rename("ns_base_outs")
    ns_hp = non_striker_ro[non_striker_ro["is_high_pressure"] == 1].groupby("dismissed_player_id").size().rename("ns_hp_outs")

    # -------------------------------------------------------------------------
    # 3. Batter Aggregation & Empirical Bayes Ranking
    # -------------------------------------------------------------------------
    bat_df = df[df["is_batter_ball"] == 1].copy()
    bat_df["is_boundary"] = bat_df["runs"].isin([4, 6]).astype(int)
    bat_df["is_dot_bat"] = (bat_df["runs"] == 0).astype(int)

    bat_base = bat_df[bat_df["is_high_pressure"] == 0].groupby(["striker_id", "striker_name"]).agg(
        base_balls=("is_batter_ball", "sum"),
        base_runs=("runs", "sum"),
        base_striker_outs=("is_striker_dismissed", "sum"),
        base_boundaries=("is_boundary", "sum"),
        base_dots=("is_dot_bat", "sum"),
        base_raae_sum=("bat_raae", "sum")
    ).reset_index()

    bat_hp = bat_df[bat_df["is_high_pressure"] == 1].groupby(["striker_id", "striker_name"]).agg(
        hp_matches=("match_id", "nunique"),
        hp_balls=("is_batter_ball", "sum"),
        hp_runs=("runs", "sum"),
        hp_striker_outs=("is_striker_dismissed", "sum"),
        hp_boundaries=("is_boundary", "sum"),
        hp_dots=("is_dot_bat", "sum"),
        hp_raae_sum=("bat_raae", "sum"),
        mean_pressure_faced=("pressure_index", "mean"),
        mean_opp_weight=("opp_bowling_weight", "mean")
    ).reset_index()

    hp_bat_par = bat_df[bat_df["is_high_pressure"] == 1]["bat_raae"].mean()
    bat_inn = bat_df[bat_df["is_high_pressure"] == 1].groupby(["striker_id", "match_id", "innings"]).agg(
        inn_balls=("is_batter_ball", "sum"),
        inn_raae=("bat_raae", "sum")
    ).reset_index()
    bat_inn_q = bat_inn[bat_inn["inn_balls"] >= 6].copy()
    bat_inn_q["pos_inn"] = (bat_inn_q["inn_raae"] > bat_inn_q["inn_balls"] * hp_bat_par).astype(int)
    bat_cons = bat_inn_q.groupby("striker_id").agg(
        qual_hp_innings=("match_id", "count"),
        hp_consistency_rate=("pos_inn", "mean")
    ).reset_index()

    bat_sum = (
        bat_hp.merge(bat_base, on=["striker_id", "striker_name"], how="left")
        .merge(bat_cons, on="striker_id", how="left")
        .merge(ns_base, left_on="striker_id", right_index=True, how="left")
        .merge(ns_hp, left_on="striker_id", right_index=True, how="left")
    )

    bat_sum["base_outs"] = bat_sum["base_striker_outs"] + bat_sum["ns_base_outs"].fillna(0)
    bat_sum["hp_outs"] = bat_sum["hp_striker_outs"] + bat_sum["ns_hp_outs"].fillna(0)
    bat_sum["total_balls"] = bat_sum["hp_balls"] + bat_sum["base_balls"].fillna(0)

    bat_sum["base_sr"] = (bat_sum["base_runs"] * 100.0) / bat_sum["base_balls"].clip(lower=1)
    bat_sum["hp_sr"] = (bat_sum["hp_runs"] * 100.0) / bat_sum["hp_balls"].clip(lower=1)
    bat_sum["sr_delta"] = bat_sum["hp_sr"] - bat_sum["base_sr"]

    bat_sum["base_avg"] = bat_sum["base_runs"] / bat_sum["base_outs"].clip(lower=1)
    bat_sum["hp_avg"] = bat_sum["hp_runs"] / bat_sum["hp_outs"].clip(lower=1)
    bat_sum["avg_delta"] = bat_sum["hp_avg"] - bat_sum["base_avg"]
    bat_sum["hp_boundary_pct"] = (bat_sum["hp_boundaries"] * 100.0) / bat_sum["hp_balls"].clip(lower=1)
    bat_sum["hp_dot_pct"] = (bat_sum["hp_dots"] * 100.0) / bat_sum["hp_balls"].clip(lower=1)

    bat_sum["base_raae_pb"] = bat_sum["base_raae_sum"] / bat_sum["base_balls"].clip(lower=1)
    bat_sum["hp_raae_pb"] = bat_sum["hp_raae_sum"] / bat_sum["hp_balls"].clip(lower=1)
    bat_sum["raae_delta_pb"] = bat_sum["hp_raae_pb"] - bat_sum["base_raae_pb"]

    elig_bat = bat_sum[
        (bat_sum["hp_balls"] >= 200) &
        (bat_sum["total_balls"] >= 400) &
        (bat_sum["mean_opp_weight"] >= 0.97)
    ].copy()

    C_BAT = 150.0
    p_raae, p_delt, p_cons = elig_bat["hp_raae_pb"].mean(), elig_bat["raae_delta_pb"].mean(), elig_bat["hp_consistency_rate"].mean()
    elig_bat["eb_hp_raae"] = (elig_bat["hp_balls"] * elig_bat["hp_raae_pb"] + C_BAT * p_raae) / (elig_bat["hp_balls"] + C_BAT)
    elig_bat["eb_raae_delta"] = (elig_bat["hp_balls"] * elig_bat["raae_delta_pb"] + C_BAT * p_delt) / (elig_bat["hp_balls"] + C_BAT)
    elig_bat["eb_consistency"] = (
        (elig_bat["qual_hp_innings"].fillna(0) * elig_bat["hp_consistency_rate"].fillna(p_cons) + 10.0 * p_cons)
        / (elig_bat["qual_hp_innings"].fillna(0) + 10.0)
    )

    for col in ["eb_hp_raae", "eb_raae_delta", "eb_consistency"]:
        elig_bat[f"z_{col}"] = (elig_bat[col] - elig_bat[col].mean()) / elig_bat[col].std()

    elig_bat["raw_score"] = 0.55 * elig_bat["z_eb_hp_raae"] + 0.25 * elig_bat["z_eb_raae_delta"] + 0.20 * elig_bat["z_eb_consistency"]
    elig_bat["superr_rating"] = 50.0 + 48.0 * (elig_bat["raw_score"] - elig_bat["raw_score"].min()) / (elig_bat["raw_score"].max() - elig_bat["raw_score"].min())
    elig_bat = elig_bat.sort_values("superr_rating", ascending=False).reset_index(drop=True)
    elig_bat["rank"] = elig_bat.index + 1

    # -------------------------------------------------------------------------
    # 4. Bowler Aggregation & Empirical Bayes Ranking
    # -------------------------------------------------------------------------
    bowl_df = df.copy()
    bowl_df["is_dot_bowl"] = ((bowl_df["bowler_runs_conceded"] == 0) & (bowl_df["is_legal_ball"] == 1)).astype(int)
    bowl_df["is_boundary_conceded"] = bowl_df["runs"].isin([4, 6]).astype(int)

    bowl_base = bowl_df[bowl_df["is_high_pressure"] == 0].groupby(["bowler_id", "bowler_name"]).agg(
        base_legal_balls=("is_legal_ball", "sum"),
        base_runs_conceded=("bowler_runs_conceded", "sum"),
        base_wickets=("is_bowler_wicket", "sum"),
        base_dots=("is_dot_bowl", "sum"),
        base_boundaries=("is_boundary_conceded", "sum"),
        base_raae_sum=("bowl_raae", "sum")
    ).reset_index()

    bowl_hp = bowl_df[bowl_df["is_high_pressure"] == 1].groupby(["bowler_id", "bowler_name"]).agg(
        hp_matches=("match_id", "nunique"),
        hp_legal_balls=("is_legal_ball", "sum"),
        hp_runs_conceded=("bowler_runs_conceded", "sum"),
        hp_wickets=("is_bowler_wicket", "sum"),
        hp_dots=("is_dot_bowl", "sum"),
        hp_boundaries=("is_boundary_conceded", "sum"),
        hp_raae_sum=("bowl_raae", "sum"),
        mean_pressure_bowled=("pressure_index", "mean"),
        mean_opp_weight=("opp_batting_weight", "mean")
    ).reset_index()

    hp_bowl_par = bowl_df[bowl_df["is_high_pressure"] == 1]["bowl_raae"].mean()
    bowl_spell = bowl_df[bowl_df["is_high_pressure"] == 1].groupby(["bowler_id", "match_id"]).agg(
        spell_balls=("is_legal_ball", "sum"),
        spell_raae=("bowl_raae", "sum")
    ).reset_index()
    bowl_spell_q = bowl_spell[bowl_spell["spell_balls"] >= 6].copy()
    bowl_spell_q["pos_spell"] = (bowl_spell_q["spell_raae"] > bowl_spell_q["spell_balls"] * hp_bowl_par).astype(int)
    bowl_cons = bowl_spell_q.groupby("bowler_id").agg(
        qual_hp_spells=("match_id", "count"),
        hp_spell_success_rate=("pos_spell", "mean")
    ).reset_index()

    bowl_sum = bowl_hp.merge(bowl_base, on=["bowler_id", "bowler_name"], how="left").merge(bowl_cons, on="bowler_id", how="left")
    bowl_sum["total_legal_balls"] = bowl_sum["hp_legal_balls"] + bowl_sum["base_legal_balls"].fillna(0)

    bowl_sum["base_econ"] = (bowl_sum["base_runs_conceded"] * 6.0) / bowl_sum["base_legal_balls"].clip(lower=1)
    bowl_sum["hp_econ"] = (bowl_sum["hp_runs_conceded"] * 6.0) / bowl_sum["hp_legal_balls"].clip(lower=1)
    bowl_sum["econ_saved_vs_base"] = bowl_sum["base_econ"] - bowl_sum["hp_econ"]

    bowl_sum["base_sr"] = bowl_sum["base_legal_balls"] / bowl_sum["base_wickets"].clip(lower=1)
    bowl_sum["hp_sr"] = bowl_sum["hp_legal_balls"] / bowl_sum["hp_wickets"].clip(lower=1)
    bowl_sum["hp_dot_pct"] = (bowl_sum["hp_dots"] * 100.0) / bowl_sum["hp_legal_balls"].clip(lower=1)

    bowl_sum["base_raae_pb"] = bowl_sum["base_raae_sum"] / bowl_sum["base_legal_balls"].clip(lower=1)
    bowl_sum["hp_raae_pb"] = bowl_sum["hp_raae_sum"] / bowl_sum["hp_legal_balls"].clip(lower=1)
    bowl_sum["raae_delta_pb"] = bowl_sum["hp_raae_pb"] - bowl_sum["base_raae_pb"]

    elig_bowl = bowl_sum[
        (bowl_sum["hp_legal_balls"] >= 200) &
        (bowl_sum["total_legal_balls"] >= 400) &
        (bowl_sum["mean_opp_weight"] >= 0.97)
    ].copy()

    C_BOWL = 150.0
    pb_raae, pb_delt, pb_cons = elig_bowl["hp_raae_pb"].mean(), elig_bowl["raae_delta_pb"].mean(), elig_bowl["hp_spell_success_rate"].mean()
    elig_bowl["eb_hp_raae"] = (elig_bowl["hp_legal_balls"] * elig_bowl["hp_raae_pb"] + C_BOWL * pb_raae) / (elig_bowl["hp_legal_balls"] + C_BOWL)
    elig_bowl["eb_raae_delta"] = (elig_bowl["hp_legal_balls"] * elig_bowl["raae_delta_pb"] + C_BOWL * pb_delt) / (elig_bowl["hp_legal_balls"] + C_BOWL)
    elig_bowl["eb_consistency"] = (
        (elig_bowl["qual_hp_spells"].fillna(0) * elig_bowl["hp_spell_success_rate"].fillna(pb_cons) + 10.0 * pb_cons)
        / (elig_bowl["qual_hp_spells"].fillna(0) + 10.0)
    )

    for col in ["eb_hp_raae", "eb_raae_delta", "eb_consistency"]:
        elig_bowl[f"z_{col}"] = (elig_bowl[col] - elig_bowl[col].mean()) / elig_bowl[col].std()

    elig_bowl["raw_score"] = 0.55 * elig_bowl["z_eb_hp_raae"] + 0.25 * elig_bowl["z_eb_raae_delta"] + 0.20 * elig_bowl["z_eb_consistency"]
    elig_bowl["superr_rating"] = 50.0 + 48.0 * (elig_bowl["raw_score"] - elig_bowl["raw_score"].min()) / (elig_bowl["raw_score"].max() - elig_bowl["raw_score"].min())
    elig_bowl = elig_bowl.sort_values("superr_rating", ascending=False).reset_index(drop=True)
    elig_bowl["rank"] = elig_bowl.index + 1

    # Save outputs
    elig_bat.to_csv(os.path.join(out_dir, "all_eligible_batters_ranked.csv"), index=False)
    elig_bowl.to_csv(os.path.join(out_dir, "all_eligible_bowlers_ranked.csv"), index=False)
    elig_bat.head(10).to_csv(os.path.join(out_dir, "final_top10_batters.csv"), index=False)
    elig_bowl.head(10).to_csv(os.path.join(out_dir, "final_top10_bowlers.csv"), index=False)
    print("Step 3 complete! Saved Top 10 and full ranked CSVs.")
    return elig_bat, elig_bowl

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_step3_player_rankings(
        in_path=os.path.join(base_dir, "data", "processed", "step2_pressure_indexed_bbb.csv"),
        teams_path=os.path.join(base_dir, "data", "raw", "teams.csv"),
        out_dir=os.path.join(base_dir, "data", "processed")
    )
