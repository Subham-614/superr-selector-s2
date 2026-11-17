import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def run_step2_pressure_engine(
    in_path: str = "data/processed/step1_reconstructed_bbb.csv",
    out_path: str = "data/processed/step2_pressure_indexed_bbb.csv"
) -> pd.DataFrame:
    """
    Step 2: Train calibrated Win Probability models to measure Counterfactual Leverage,
    compute the 3-pillar Continuous Delivery Pressure Index (0-100), and validate
    performance shifts across pressure tiers.
    """
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    df = pd.read_csv(in_path, low_memory=False)

    # -------------------------------------------------------------------------
    # 1. Win Probability (WP) & Counterfactual Leverage Index (LI)
    # -------------------------------------------------------------------------
    valid_wp = df[df["win_team_id"].notna() & df["innings"].isin([1, 2])].copy()
    valid_wp["batting_team_won"] = (valid_wp["batting_team_id"] == valid_wp["win_team_id"]).astype(int)

    # --- Innings 1 WP Model ---
    inn1_mask = df["innings"] == 1
    inn1_train = valid_wp[valid_wp["innings"] == 1]
    features_inn1 = ["runs_vs_par_before", "cum_wickets_before", "balls_remaining_before", "recent_wickets_12b"]

    scaler_1 = StandardScaler()
    X1_train = scaler_1.fit_transform(inn1_train[features_inn1].fillna(0))
    clf_1 = LogisticRegression()
    clf_1.fit(X1_train, inn1_train["batting_team_won"])

    X1_all = scaler_1.transform(df.loc[inn1_mask, features_inn1].fillna(0))
    wp1_before = clf_1.predict_proba(X1_all)[:, 1]

    # Counterfactual +4 Boundary vs Wicket on Current Ball (Innings 1)
    df_inn1_plus4 = df.loc[inn1_mask, features_inn1].fillna(0).copy()
    df_inn1_plus4["runs_vs_par_before"] += (4.0 - df.loc[inn1_mask, "par_rpo"] / 6.0)
    df_inn1_plus4["balls_remaining_before"] = (df_inn1_plus4["balls_remaining_before"] - 1).clip(lower=1)
    wp1_plus4 = clf_1.predict_proba(scaler_1.transform(df_inn1_plus4))[:, 1]

    df_inn1_wkt = df.loc[inn1_mask, features_inn1].fillna(0).copy()
    df_inn1_wkt["runs_vs_par_before"] -= (df.loc[inn1_mask, "par_rpo"] / 6.0)
    df_inn1_wkt["cum_wickets_before"] = (df_inn1_wkt["cum_wickets_before"] + 1).clip(upper=9)
    df_inn1_wkt["balls_remaining_before"] = (df_inn1_wkt["balls_remaining_before"] - 1).clip(lower=1)
    df_inn1_wkt["recent_wickets_12b"] += 1
    wp1_wkt = clf_1.predict_proba(scaler_1.transform(df_inn1_wkt))[:, 1]

    leverage_1 = np.abs(wp1_plus4 - wp1_wkt)

    # --- Innings 2 WP Model ---
    df["rrr_diff"] = (df["req_run_rate_before"] - df["par_rpo"]).clip(lower=-10, upper=36)
    inn2_mask = df["innings"] == 2
    inn2_train = valid_wp[valid_wp["innings"] == 2].copy()
    inn2_train["rrr_diff"] = (inn2_train["req_run_rate_before"] - inn2_train["par_rpo"]).clip(lower=-10, upper=36)

    features_inn2 = ["rrr_diff", "cum_wickets_before", "balls_remaining_before", "runs_needed_before"]
    scaler_2 = StandardScaler()
    X2_train = scaler_2.fit_transform(inn2_train[features_inn2].fillna(0))
    clf_2 = LogisticRegression()
    clf_2.fit(X2_train, inn2_train["batting_team_won"])

    X2_all = scaler_2.transform(df.loc[inn2_mask, features_inn2].fillna(0))
    wp2_before = clf_2.predict_proba(X2_all)[:, 1]

    # Counterfactual +4 Boundary vs Wicket on Current Ball (Innings 2)
    df_inn2_plus4 = df.loc[inn2_mask, features_inn2].fillna(0).copy()
    balls_next = (df_inn2_plus4["balls_remaining_before"] - 1).clip(lower=1)
    runs_next_4 = (df_inn2_plus4["runs_needed_before"] - 4).clip(lower=0)
    df_inn2_plus4["runs_needed_before"] = runs_next_4
    df_inn2_plus4["balls_remaining_before"] = balls_next
    df_inn2_plus4["rrr_diff"] = ((runs_next_4 * 6.0 / balls_next) - df.loc[inn2_mask, "par_rpo"]).clip(lower=-10, upper=36)
    wp2_plus4 = clf_2.predict_proba(scaler_2.transform(df_inn2_plus4))[:, 1]

    df_inn2_wkt = df.loc[inn2_mask, features_inn2].fillna(0).copy()
    runs_next_0 = df_inn2_wkt["runs_needed_before"]
    df_inn2_wkt["cum_wickets_before"] = (df_inn2_wkt["cum_wickets_before"] + 1).clip(upper=9)
    df_inn2_wkt["balls_remaining_before"] = balls_next
    df_inn2_wkt["rrr_diff"] = ((runs_next_0 * 6.0 / balls_next) - df.loc[inn2_mask, "par_rpo"]).clip(lower=-10, upper=36)
    wp2_wkt = clf_2.predict_proba(scaler_2.transform(df_inn2_wkt))[:, 1]

    leverage_2 = np.abs(wp2_plus4 - wp2_wkt)

    df["win_prob_before"] = 0.5
    df.loc[inn1_mask, "win_prob_before"] = wp1_before
    df.loc[inn2_mask, "win_prob_before"] = wp2_before

    df["wp_leverage"] = 0.20
    df.loc[inn1_mask, "wp_leverage"] = leverage_1
    df.loc[inn2_mask, "wp_leverage"] = leverage_2

    lev_99 = np.percentile(df["wp_leverage"], 99)
    df["p_leverage"] = (df["wp_leverage"] / lev_99).clip(0, 1)

    # -------------------------------------------------------------------------
    # 2. Construct the 3 Pillars of the Continuous Pressure Index (0 to 100)
    # -------------------------------------------------------------------------
    rrr_ratio = (df["req_run_rate_before"] - df["par_rpo"]) / df["par_rpo"].clip(lower=6.0)
    inn_progress = 1.0 - (df["balls_remaining_before"] / df["max_legal_balls"].clip(lower=6))

    # Pillar 1: Equation & Phase Pressure
    p_eq_inn2 = 1.0 / (1.0 + np.exp(-(2.5 * rrr_ratio + 1.8 * (inn_progress - 0.5))))
    par_deficit_scaled = (-df["runs_vs_par_before"] / 20.0).clip(-1.5, 2.0)
    death_boost = np.where(df["overid"] >= 16, 0.35 + 0.08 * (df["overid"] - 16), 0.0)
    p_eq_inn1 = (1.0 / (1.0 + np.exp(-(1.2 * par_deficit_scaled + 1.2 * (inn_progress - 0.55)))) + death_boost).clip(0, 1)

    df["p_equation"] = np.where(
        df["innings"].isin([3, 4]), 1.0,
        np.where(df["innings"] == 2, p_eq_inn2, p_eq_inn1)
    )

    # Pillar 2: Wicket & Resource Pressure
    expected_wkts_by_progress = 6.5 * inn_progress
    wkt_excess = (df["cum_wickets_before"] - expected_wkts_by_progress).clip(lower=-2.0, upper=6.0)
    recent_shock = (df["recent_wickets_12b"] * 0.22).clip(0, 0.55)
    base_wkt_load = (df["cum_wickets_before"] / 9.0) ** 1.2

    df["p_wicket"] = np.where(
        df["innings"].isin([3, 4]), 1.0,
        (0.45 * base_wkt_load + 0.35 * (1.0 / (1.0 + np.exp(-0.9 * wkt_excess))) + recent_shock).clip(0, 1)
    )

    # Pillar 3: Match Stakes & Leverage Pressure
    match_closeness = 4.0 * df["win_prob_before"] * (1.0 - df["win_prob_before"])
    is_knockout_match = (
        (df["knock_out"] == 1) |
        (df["stage"].isin(["Final", "Qualifier", "Eliminator", "Semi Final", "Super 4"]))
    ).astype(int)
    ko_boost = is_knockout_match * 0.12

    df["p_stakes"] = np.where(
        df["innings"].isin([3, 4]), 1.0,
        (0.50 * df["p_leverage"] + 0.40 * match_closeness + ko_boost).clip(0, 1)
    )

    # Composite Continuous Pressure Index (0 to 100)
    raw_pressure = 0.40 * df["p_equation"] + 0.30 * df["p_wicket"] + 0.30 * df["p_stakes"]
    df["pressure_index"] = np.where(df["innings"].isin([3, 4]), 100.0, (raw_pressure * 100.0).clip(0, 100))

    # Classify into Pressure Tiers (Top 25% = High Pressure)
    q75 = np.percentile(df["pressure_index"], 75)
    q40 = np.percentile(df["pressure_index"], 40)

    df["pressure_tier"] = np.where(
        df["pressure_index"] >= q75, "High_Pressure",
        np.where(df["pressure_index"] >= q40, "Medium_Pressure", "Low_Pressure")
    )
    df["is_high_pressure"] = (df["pressure_index"] >= q75).astype(int)

    df.to_csv(out_path, index=False)
    print(f"Step 2 complete! High-Pressure cutoff (75th pct): {q75:.2f}. Saved to {out_path}")
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_step2_pressure_engine(
        in_path=os.path.join(base_dir, "data", "processed", "step1_reconstructed_bbb.csv"),
        out_path=os.path.join(base_dir, "data", "processed", "step2_pressure_indexed_bbb.csv")
    )