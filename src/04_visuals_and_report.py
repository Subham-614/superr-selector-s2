import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as mticker

def run_step4_visuals_and_sensitivity(
    bbb_path: str = "data/processed/step2_pressure_indexed_bbb.csv",
    bat_path: str = "data/processed/all_eligible_batters_ranked.csv",
    bowl_path: str = "data/processed/all_eligible_bowlers_ranked.csv",
    fig_dir: str = "outputs/figures"
):
    """
    Step 4: Generate publication-grade validation & quadrant figures and run
    sensitivity checks across alternative eligibility thresholds.
    """
    os.makedirs(fig_dir, exist_ok=True)

    # --- Global style ---
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": "#CBD5E1",
        "axes.linewidth": 0.9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "#F8FAFC",
        "grid.color": "#E2E8F0",
        "grid.linewidth": 0.6,
    })

    RR_PINK   = "#E63946"
    RR_BLUE   = "#1D3461"
    RR_GOLD   = "#F4A261"
    TEAL      = "#0F766E"
    TEAL_DARK = "#134E4A"
    SLATE     = "#64748B"
    SLATE_DARK= "#1E293B"
    AMBER     = "#D97706"
    AMBER_DARK= "#78350F"

    df  = pd.read_csv(bbb_path, low_memory=False)
    bat = pd.read_csv(bat_path)
    bowl= pd.read_csv(bowl_path)

    top10_bat  = bat[bat["rank"] <= 10].copy()
    top10_bowl = bowl[bowl["rank"] <= 10].copy()
    others_bat = bat[bat["rank"] > 10].copy()
    others_bowl= bowl[bowl["rank"] > 10].copy()

    # =========================================================================
    # Figure 1: Pressure Index Decile Validation
    # =========================================================================
    df["pressure_decile"] = pd.qcut(df["pressure_index"], q=10,
                                     labels=[f"D{i}" for i in range(1, 11)])
    dec = df.groupby("pressure_decile", observed=False).agg(
        bat_runs=("runs", "sum"),
        bat_balls=("is_batter_ball", "sum"),
        legal_balls=("is_legal_ball", "sum"),
        striker_wkts=("is_striker_dismissed", "sum")
    ).reset_index()
    dec["bat_avg"]      = dec["bat_runs"] / dec["striker_wkts"].clip(lower=1)
    dec["wkt_prob_pct"] = (dec["striker_wkts"] * 100.0) / dec["legal_balls"].clip(lower=1)

    fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=300)
    x = np.arange(len(dec))

    # Gradient bar colours — darker for higher pressure deciles
    bar_colours = [plt.cm.Blues(0.35 + 0.05 * i) for i in range(10)]
    bars = ax1.bar(x, dec["bat_avg"], width=0.6, color=bar_colours, zorder=2)

    # Highlight HP zone
    ax1.axvspan(6.5, 9.5, color=RR_GOLD, alpha=0.18, zorder=1,
                label="High-Pressure Zone (D8–D10, top 25%)")
    ax1.text(8.0, 36.0, "HP\nZone", ha="center", va="top", fontsize=8,
             color=AMBER, fontweight="bold")

    ax1.set_ylabel("League Batting Average", color=RR_BLUE, fontweight="bold", fontsize=9)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"D{i}" for i in range(1, 11)], fontsize=8.5)
    ax1.set_ylim(0, 42)
    ax1.yaxis.label.set_color(RR_BLUE)
    ax1.tick_params(axis="y", colors=RR_BLUE)
    ax1.grid(axis="y", zorder=0)

    ax2 = ax1.twinx()
    ax2.plot(x, dec["wkt_prob_pct"], color=RR_PINK, marker="o",
             linewidth=2.2, markersize=5.5, zorder=5, label="Dismissal Prob. (%)")
    ax2.set_ylabel("Dismissal Probability per Ball (%)", color=RR_PINK,
                   fontweight="bold", fontsize=9)
    ax2.set_ylim(0, 12)
    ax2.yaxis.label.set_color(RR_PINK)
    ax2.tick_params(axis="y", colors=RR_PINK)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    ax1.set_xlabel("Pressure Index Decile (D1 = Lowest, D10 = Highest Pressure)", fontsize=9)
    plt.title("Empirical Pressure Validation: Batting Average & Dismissal Rate\nacross 200,999 Deliveries (IPL + T20I 2022–2026)",
              fontweight="bold", fontsize=10, pad=12)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=True,
               framealpha=0.9, edgecolor="#CBD5E1")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig1_pressure_validation.png"), bbox_inches="tight")
    plt.close()
    print("  Saved fig1_pressure_validation.png")

    # =========================================================================
    # Figure 2: Batters — Baseline SR vs. High-Pressure SR (bubble = HP balls)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Size others by HP balls (clamp)
    s_others = (others_bat["hp_balls"] / others_bat["hp_balls"].max() * 60 + 20).clip(20, 80)
    s_top10  = (top10_bat["hp_balls"]  / top10_bat["hp_balls"].max()  * 110 + 55).clip(55, 165)

    ax.scatter(others_bat["base_sr"], others_bat["hp_sr"],
               s=s_others, color=SLATE, alpha=0.45, zorder=2,
               label="Eligible Batters (Rank 11–51)")
    sc = ax.scatter(top10_bat["base_sr"], top10_bat["hp_sr"],
                    s=s_top10, c=top10_bat["superr_rating"],
                    cmap="YlOrRd", edgecolors=AMBER_DARK, linewidths=0.8,
                    zorder=5, label="Top 10 Clutch Batters")
    cbar = plt.colorbar(sc, ax=ax, pad=0.01, shrink=0.75)
    cbar.set_label("SupeRR Rating", fontsize=8)
    cbar.ax.tick_params(labelsize=7.5)

    # Parity / quadrant lines
    xlims = [115, 198]
    ax.plot(xlims, xlims, linestyle="--", color=SLATE, linewidth=1.1, alpha=0.7,
            label="Parity Line (HP SR = Baseline SR)")
    ax.axhline(bat["hp_sr"].mean(), linestyle=":", color=RR_BLUE, alpha=0.55, linewidth=1.1)
    ax.axvline(bat["base_sr"].mean(), linestyle=":", color=RR_BLUE, alpha=0.55, linewidth=1.1)
    # Quadrant text
    ax.text(197, 199, "Elite Hitters\n(high baseline, high HP)",
            ha="right", va="top", fontsize=7, color=SLATE, style="italic")
    ax.text(116, 199, "Pressure Rises\n(lower baseline, high HP)",
            ha="left", va="top", fontsize=7, color=SLATE, style="italic")

    # Annotations — with smart offset to reduce overlap
    offsets = {
        "Namboori Tilak Varma": (-2, +2.5),
        "Andre Russell":        (+1.0, -3.5),
        "Nicholas Pooran":      (+1.0, +1.5),
        "Hardik Pandya":        (-1.5, -3.8),
        "Tim David":            (+1.0, +1.5),
        "Jos Buttler":          (-2.5, +2.0),
        "Marcus Stoinis":       (+1.0, +1.5),
        "Shashank Singh":       (+1.0, -3.5),
        "Dhruv Jurel":          (-2.0, +2.0),
        "Ayush Badoni":         (+1.0, +1.5),
    }
    short = {
        "Namboori Tilak Varma": "Tilak Varma",
        "Andre Russell":        "Russell",
        "Nicholas Pooran":      "Pooran",
        "Hardik Pandya":        "Hardik",
        "Tim David":            "Tim David",
        "Jos Buttler":          "Buttler",
        "Marcus Stoinis":       "Stoinis",
        "Shashank Singh":       "Shashank",
        "Dhruv Jurel":          "Jurel",
        "Ayush Badoni":         "Badoni",
    }
    for _, r in top10_bat.iterrows():
        nm = r["striker_name"]
        dx, dy = offsets.get(nm, (1.0, 1.0))
        sn = short.get(nm, nm.split()[-1])
        ax.annotate(
            f"#{int(r['rank'])} {sn}",
            xy=(r["base_sr"], r["hp_sr"]),
            xytext=(r["base_sr"] + dx, r["hp_sr"] + dy),
            fontsize=7.8, fontweight="bold", color=SLATE_DARK,
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.6),
        )

    ax.set_xlim(115, 198)
    ax.set_ylim(115, 202)
    ax.set_xlabel("Baseline Strike Rate (Standard-Pressure Deliveries)", fontweight="bold", fontsize=9)
    ax.set_ylabel("High-Pressure Strike Rate (Top 25% by Pressure Index)", fontweight="bold", fontsize=9)
    ax.set_title("Batters Under Pressure — Baseline SR vs. High-Pressure SR\n(Bubble size ∝ HP balls faced; Colour = SupeRR Rating)",
                 fontweight="bold", fontsize=10, pad=10)
    ax.legend(loc="lower right", fontsize=8, frameon=True, framealpha=0.9, edgecolor="#CBD5E1")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_top10_batters_quadrant.png"), bbox_inches="tight")
    plt.close()
    print("  Saved fig2_top10_batters_quadrant.png")

    # =========================================================================
    # Figure 3: Bowlers — HP Economy vs. HP Strike Rate (bubble = HP wickets)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    s_ob  = (others_bowl["hp_wickets"] / others_bowl["hp_wickets"].max() * 55 + 18).clip(18, 73)
    s_t10 = (top10_bowl["hp_wickets"]  / top10_bowl["hp_wickets"].max()  * 100 + 50).clip(50, 150)

    ax.scatter(others_bowl["hp_econ"], others_bowl["hp_sr"],
               s=s_ob, color=SLATE, alpha=0.45, zorder=2,
               label="Eligible Bowlers (Rank 11–68)")
    sc2 = ax.scatter(top10_bowl["hp_econ"], top10_bowl["hp_sr"],
                     s=s_t10, c=top10_bowl["superr_rating"],
                     cmap="Greens", edgecolors=TEAL_DARK, linewidths=0.8,
                     zorder=5, label="Top 10 Clutch Bowlers")
    cbar2 = plt.colorbar(sc2, ax=ax, pad=0.01, shrink=0.75)
    cbar2.set_label("SupeRR Rating", fontsize=8)
    cbar2.ax.tick_params(labelsize=7.5)

    ax.axvline(bowl["hp_econ"].mean(), linestyle="--", color=SLATE, alpha=0.6,
               linewidth=1.1, label=f"Peer Mean HP Economy ({bowl['hp_econ'].mean():.2f})")
    ax.axhline(bowl["hp_sr"].mean(), linestyle=":", color=RR_BLUE, alpha=0.6,
               linewidth=1.1, label=f"Peer Mean HP Strike Rate ({bowl['hp_sr'].mean():.1f})")

    # Quadrant shading
    xlim = ax.get_xlim() if ax.get_xlim()[0] != 0.0 else (4.5, 13.5)
    ax.fill_between([4.0, bowl["hp_econ"].mean()],
                    0, bowl["hp_sr"].mean(),
                    alpha=0.06, color=TEAL, zorder=0)
    ax.text(4.6, bowl["hp_sr"].mean() - 0.5, "Elite Zone\n(low Econ + low SR)",
            ha="left", va="top", fontsize=7, color=TEAL, style="italic")

    bowler_offsets = {
        "Sunil Narine":       (+0.08, +0.5),
        "Mohammad Nawaz":     (-0.35, -0.9),
        "Shaheen Afridi":     (+0.08, +0.5),
        "Andre Russell":      (+0.08, +0.5),
        "Kuldeep Yadav":      (+0.08, -0.9),
        "Adam Zampa":         (-0.35, +0.5),
        "Jasprit Bumrah":     (+0.08, +0.5),
        "Varun Chakravarthy": (-0.35, +0.5),
        "Noor Ahmad":         (+0.08, -0.9),
        "Wanindu Hasaranga":  (-0.35, +0.5),
    }
    bowler_short = {
        "Sunil Narine":       "Narine",
        "Mohammad Nawaz":     "Nawaz",
        "Shaheen Afridi":     "Shaheen",
        "Andre Russell":      "Russell",
        "Kuldeep Yadav":      "Kuldeep",
        "Adam Zampa":         "Zampa",
        "Jasprit Bumrah":     "Bumrah",
        "Varun Chakravarthy": "Varun C.",
        "Noor Ahmad":         "Noor Ahmad",
        "Wanindu Hasaranga":  "Hasaranga",
    }
    for _, r in top10_bowl.iterrows():
        nm = r["bowler_name"]
        dx, dy = bowler_offsets.get(nm, (0.08, 0.5))
        sn = bowler_short.get(nm, nm.split()[-1])
        ax.annotate(
            f"#{int(r['rank'])} {sn}",
            xy=(r["hp_econ"], r["hp_sr"]),
            xytext=(r["hp_econ"] + dx, r["hp_sr"] + dy),
            fontsize=7.8, fontweight="bold", color=SLATE_DARK,
            arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.6),
        )

    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.set_xlabel("High-Pressure Economy Rate  ◄ Lower is Better", fontweight="bold", fontsize=9)
    ax.set_ylabel("High-Pressure Bowling Strike Rate  ▲ Lower is Better", fontweight="bold", fontsize=9)
    ax.set_title("Bowlers Under Pressure — Economy (Containment) vs. Strike Rate (Penetration)\n(Bubble size ∝ HP wickets; Colour = SupeRR Rating)",
                 fontweight="bold", fontsize=10, pad=10)
    ax.legend(loc="lower left", fontsize=8, frameon=True, framealpha=0.9, edgecolor="#CBD5E1")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_top10_bowlers_quadrant.png"), bbox_inches="tight")
    plt.close()
    print("  Saved fig3_top10_bowlers_quadrant.png")

    # =========================================================================
    # Sensitivity Check (printed only)
    # =========================================================================
    print("\n--- Sensitivity Check: Top-5 stability across HP-ball cutoffs ---")
    for cutoff in [150, 200, 250]:
        sub_bat  = bat[bat["hp_balls"] >= cutoff].head(10)["striker_name"].tolist()
        sub_bowl = bowl[bowl["hp_legal_balls"] >= cutoff].head(10)["bowler_name"].tolist()
        print(f"  Cutoff >= {cutoff} HP balls | Batters: {sub_bat[:5]} | Bowlers: {sub_bowl[:5]}")

    print(f"\nStep 4 complete. 3 high-resolution figures saved to {fig_dir}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_step4_visuals_and_sensitivity(
        bbb_path  = os.path.join(base_dir, "data", "processed", "step2_pressure_indexed_bbb.csv"),
        bat_path  = os.path.join(base_dir, "data", "processed", "all_eligible_batters_ranked.csv"),
        bowl_path = os.path.join(base_dir, "data", "processed", "all_eligible_bowlers_ranked.csv"),
        fig_dir   = os.path.join(base_dir, "outputs", "figures"),
    )
