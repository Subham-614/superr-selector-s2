# SupeRR Selector Season 2 — Methodology, Dashboard & Submission

**Hackathon:** Rajasthan Royals / Unstop — SupeRR Selector Season 2  
**Objective:** Rank the top 10 T20 batters and top 10 T20 bowlers who perform best under pressure  
**Dataset:** 200,999 deliveries | 883 matches | 141 tournaments (IPL + T20I 2022–2026)  
**Interactive Dashboard:** Streamlit + Plotly interactive analytics app (`app.py`)

---

## 🏆 Final Rankings

### Top 10 Clutch Batters

| Rank | Player | HP Balls | HP SR | Baseline SR | SR Delta | SupeRR Rating |
|------|--------|----------|-------|-------------|----------|---------------|
| 1 | Namboori Tilak Varma | 579 | 162.9 | 137.0 | +25.8 | 98.0 |
| 2 | Andre Russell | 461 | 173.8 | 166.5 | +7.2 | 97.1 |
| 3 | Nicholas Pooran | 392 | 161.5 | 155.9 | +5.6 | 96.6 |
| 4 | Hardik Pandya | 542 | 155.4 | 136.3 | +19.1 | 96.2 |
| 5 | Tim David | 556 | 173.2 | 181.3 | -8.1 | 96.1 |
| 6 | Jos Buttler | 208 | 191.8 | 152.5 | +39.3 | 95.8 |
| 7 | Marcus Stoinis | 375 | 174.4 | 144.6 | +29.8 | 95.4 |
| 8 | Shashank Singh | 234 | 162.0 | 161.3 | +0.6 | 95.4 |
| 9 | Dhruv Jurel | 283 | 164.0 | 144.3 | +19.7 | 94.9 |
| 10 | Ayush Badoni | 380 | 152.1 | 134.1 | +18.0 | 94.8 |

### Top 10 Clutch Bowlers

| Rank | Player | HP Balls | HP Wkts | HP Economy | Base Economy | Econ Saved | HP SR | SupeRR Rating |
|------|--------|----------|---------|------------|--------------|------------|-------|---------------|
| 1 | Sunil Narine | 379 | 26 | 5.37 | 7.34 | 1.97 | 14.6 | 98.0 |
| 2 | Mohammad Nawaz | 220 | 21 | 5.56 | 7.56 | 2.00 | 10.5 | 97.7 |
| 3 | Shaheen Afridi | 247 | 25 | 7.24 | 8.16 | 0.92 | 9.9 | 97.7 |
| 4 | Andre Russell | 240 | 25 | 9.55 | 11.51 | 1.96 | 9.6 | 97.6 |
| 5 | Kuldeep Yadav | 544 | 47 | 6.95 | 8.44 | 1.49 | 11.6 | 97.5 |
| 6 | Adam Zampa | 310 | 28 | 7.12 | 8.81 | 1.69 | 11.1 | 96.5 |
| 7 | Jasprit Bumrah | 483 | 34 | 6.97 | 7.26 | 0.29 | 14.2 | 93.3 |
| 8 | Varun Chakravarthy | 586 | 41 | 6.42 | 8.60 | 2.18 | 14.3 | 92.7 |
| 9 | Noor Ahmad | 386 | 31 | 6.34 | 8.49 | 2.15 | 12.5 | 89.5 |
| 10 | Wanindu Hasaranga | 556 | 46 | 7.26 | 8.17 | 0.91 | 12.1 | 88.8 |

> **Note on scope:** Rankings cover all players in the provided dataset — IPL and T20 Internationals 2022–2026. Rajasthan Royals is the competition organiser, not a nationality filter. T20I-only players (Nawaz, Shaheen, Noor Ahmad, Hasaranga) qualified by playing in high-opposition-weight matches (opp_weight ≥ 0.97) against top-tier teams.

---

## 🚀 Interactive Streamlit Dashboard (`app.py`)

A full-fledged, publication-grade web dashboard built specifically for Rajasthan Royals scouts and hackathon evaluators.

### Key Dashboard Modules:
1. **🏆 Top 10 SupeRR Leaderboards**: Interactive horizontal bar charts, sortable player tables, and direct CSV exports.
2. **🎯 2D Quadrant Matrix**: Plotly scatter matrices decoupling baseline capability from high-pressure execution (*Elite Clutch*, *Pressure Surfers*, *Baseline Merchants*, *Strugglers*).
3. **🔬 Player Profiler & Spider Radar**: 6-dimensional clutch radar profiles + Powerplay/Middle/Death and Pace/Spin performance breakdowns.
4. **⚔️ Head-to-Head Clutch Duel**: Compare any two players side-by-side with dual radar charts and delta winning scorecards.
5. **⚡ Live Match Pressure Simulator & Replay**:
   - Interactive needle gauge simulating the Continuous Pressure Index (0–100) based on match state inputs (Innings, Target, Overs, Wickets, Par RPO).
   - Delivery-by-delivery Win Probability and Pressure trajectory explorer for iconic matches in the dataset.
6. **📈 Empirical Validation & Methodology**: Decile-by-decile proof of pressure validity (Batting Avg drops 48%, Dismissal Prob surges 69%) + 1-click download of the 12-page Methodology Report PDF.

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run app.py
```

---

## 🌐 Deploying to Streamlit Community Cloud (Step-by-Step)

Follow these exact steps to push this repository to GitHub and get your live shareable URL to submit to Unstop:

### Step 1: Initialize Git and Commit
Open PowerShell or your terminal inside `D:\superr_selector_s2`:

```bash
# Initialize git
git init

# Add all files (the included .gitignore automatically protects against GitHub's 100MB limit by tracking the 16MB parquet while ignoring 100MB+ raw CSVs)
git add .

# Initial commit
git commit -m "SupeRR Selector Season 2: Analytical Pipeline & Streamlit Dashboard"
```

### Step 2: Push to GitHub
1. Go to [github.com](https://github.com) and create a **new public repository** (e.g., `superr-selector-s2`).
2. Run the commands shown by GitHub:

```bash
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/superr-selector-s2.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud (1-Click)
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository: `<YOUR_GITHUB_USERNAME>/superr-selector-s2`.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Click **"Deploy!"**.

Within 1–2 minutes, your interactive dashboard will be live at a public URL (e.g., `https://superr-selector-s2.streamlit.app`) that you can submit alongside your PDF report!

---

## 📁 Project Structure

```
superr_selector_s2/
│
├── app.py                    # Streamlit Interactive Web Dashboard
├── requirements.txt          # Python dependencies (streamlit, plotly, pyarrow, etc.)
├── .gitignore                # Protects against GitHub 100MB file limit
├── README.md                 # Project documentation & run guide
│
├── data/
│   ├── raw/                  # Original competition CSVs (read-only)
│   │   ├── ball_by_ball.csv               (200,999 rows × 33 cols)
│   │   ├── competition_team_player_mapping.csv
│   │   ├── competitions.csv               (141 tournaments)
│   │   ├── matches.csv                    (883 matches)
│   │   ├── playing_eleven.csv
│   │   └── teams.csv
│   │
│   └── processed/            # Pipeline outputs & dashboard inputs
│       ├── final_top10_batters.csv
│       ├── final_top10_bowlers.csv
│       ├── all_eligible_batters_ranked.csv   (48 eligible batters)
│       ├── all_eligible_bowlers_ranked.csv   (68 eligible bowlers)
│       ├── step2_pressure_indexed_bbb.parquet (16.2 MB - fast delivery data)
│       ├── batter_phase_splits.parquet
│       ├── bowler_phase_splits.parquet
│       ├── batter_type_splits.parquet
│       └── decile_validation.csv
│
├── src/                      # 4-step modular analytical pipeline
│   ├── 01_data_prep.py          Step 1: Data cleaning & state reconstruction
│   ├── 02_pressure_engine.py    Step 2: Win Probability model & Pressure Index
│   ├── 03_player_rankings.py    Step 3: Context RAAE, Empirical Bayes & SupeRR Ratings
│   └── 04_visuals_and_report.py Step 4: 300 DPI figures & sensitivity checks
│
└── outputs/
    ├── figures/
    │   ├── fig1_pressure_validation.png
    │   ├── fig2_top10_batters_quadrant.png
    │   └── fig3_top10_bowlers_quadrant.png
    ├── methodology_report_tables/
    │   ├── table1_top10_batters.md & .csv
    │   └── table2_top10_bowlers.md & .csv
    └── superr_selector_s2_methodology_report.pdf  ← PDF REPORT FOR UNSTOP
```

---

## ⚙️ How to Run Analytical Pipeline (Full Reproducibility)

Run each step from the project root (`D:\superr_selector_s2`):

```powershell
# Step 1 — Data cleaning, trap fixes, state reconstruction (~2 min)
python src/01_data_prep.py

# Step 2 — Win Probability model & Pressure Index (~3 min)
python src/02_pressure_engine.py

# Step 3 — RAAE calculation, Empirical Bayes, SupeRR Rankings (~1 min)
python src/03_player_rankings.py

# Step 4 — Generate 300 DPI figures & sensitivity checks (~2 min)
python src/04_visuals_and_report.py
```

---

## 🧠 Methodology Summary

### Pressure Index (Continuous, 0–100)

| Pillar | Weight | Description |
|--------|--------|-------------|
| Equation Pressure | 40% | RRR vs par RPO, amplified by balls remaining |
| Wicket & Resource | 35% | Remaining wickets + ball-in-hand scarcity |
| Win Probability Leverage | 25% | \|WP change per run\| from logistic regression model |

* **High-Pressure cutoff:** 59.73 (75th percentile = top 25% deliveries).

### SupeRR Rating Formula

$$\text{SupeRR} = 0.55 \cdot z(\text{EB\_HP\_RAAE}) + 0.25 \cdot z(\text{EB\_RAAE\_Delta}) + 0.20 \cdot z(\text{Consistency})$$

Normalized so Rank #1 = 98.0.
Empirical Bayes shrinkage ($\lambda=12$ batters, $\lambda=16$ bowlers) regularizes small-sample noise.

---

## 📄 Submission Checklist

- [x] Top 10 Batters (Unstop Dropdowns)
- [x] Top 10 Bowlers (Unstop Dropdowns)
- [x] 12-page Methodology Report PDF (`outputs/superr_selector_s2_methodology_report.pdf`)
- [x] Publication-Grade 300 DPI Figures (`outputs/figures/`)
- [x] Interactive Streamlit Dashboard (`app.py`) for live web deployment
