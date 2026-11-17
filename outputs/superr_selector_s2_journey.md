# 🏏 Behind the Scenes: Building the SupeRR Selector Season 2 Analytical Engine
### *Decoding T20 Clutch DNA: 200,999 Deliveries, 3 Pillars of Pressure, and Empirical Bayes Regularization*

**Participant:** Subham ([GitHub: Subham-614](https://github.com/Subham-614/superr-selector-s2))  
**Competition:** Rajasthan Royals — SupeRR Selector Season 2 (Unstop)  
**Deliverables:** Ranked Top 10 Dropdowns | 12-Page Methodology Report | Live Streamlit Dashboard  

---

## 🎯 The Hook: What Really Happens When the Match is on the Line?

In modern T20 cricket, traditional stats lie. 

A strike rate of 150 against a 5th bowler with 60 runs needed off 60 balls looks great on a scorecard, but what happens when it’s **24 needed off 12 balls in an IPL Playoff**, or when **3 wickets fall inside the powerplay**? 

When Rajasthan Royals launched the **SupeRR Selector Season 2** hackathon, the mission was crystal clear:  
> *Move past superficial reputation and build an objective, mathematical framework to find the 10 most reliable batters and 10 most reliable bowlers under high-leverage match pressure across IPL and T20Is (2022–2026).*

Here is the story of how our analytical engine and interactive scouting dashboard came to life.

---

## 🔬 The "War Room" Analytical Process

Our 4-step data pipeline processed **200,999 deliveries across 883 matches and 141 tournaments**. Here is how we tackled the core challenges:

### 1. Rejecting Binary Cutoffs → The Continuous Pressure Index (0–100)
Most analysts lazily define pressure as "overs 16–20". But an over 18 chase with 10 runs needed is low pressure, whereas Over 4 after losing 3 early wickets is high pressure. 

We formulated a continuous, delivery-by-delivery **Pressure Index (0–100)** built on three objective pillars:
- **Pillar 1: Equation & Phase Pressure (40%)** — Measures RRR deficit against venue and tournament tier par, amplified as balls tick down.
- **Pillar 2: Resource Depletion Pressure (35%)** — Combines wickets lost, ball scarcity, and recent collapse shocks (wickets falling in the prior 12 balls).
- **Pillar 3: Win Probability Leverage (25%)** — Measures counterfactual win-probability sensitivity $|\Delta WP|$ from calibrated logistic models.

 deliveries crossing the **75th percentile (Pressure Index ≥ 59.73)** were isolated into the **High-Pressure (HP) Zone** (50,250 deliveries).

### 2. Empirical Validation: Does the Index Actually Work?
Before evaluating players, we tested our pressure metric across deciles (D1 to D10). The data spoke loud and clear:
* **League Batting Average:** Collapsed from **31.1 in D1 down to 16.2 in D10** — a **48% decline**.
* **Dismissal Probability:** Surged from **4.95% per ball in D1 to 8.37% in D10** — a **69% increase in lethality**.
* **Conclusion:** The index reliably isolates high-stakes, pressure-cooker cricket.

### 3. Context RAAE & Empirical Bayes Regularization
Raw averages are distorted by minnow teams and small sample sizes. We engineered:
* **Context-Adjusted RAAE (Runs Above Average Expectation):** Controlling for venue par, innings phase, pace vs spin, and opponent team strength ($Mean\ Opp\ Weight \ge 0.97$).
* **Empirical Bayes Shrinkage ($\lambda=12$ batters, $\lambda=16$ bowlers):** Shrinking small-sample hot streaks back toward peer baselines to ensure only sustained excellence surfaces.

---

## 🌟 The Player Picks I'm Backing

### 👑 The #1 Clutch Batter: Namboori Tilak Varma (SupeRR Rating: 98.0)
* **The Story:** While fans look at pure boundary-hitters, Tilak Varma is the ultimate T20 chameleon.
* **The Evidence:** Under high pressure, his baseline strike rate of **137.0 surges to 162.9 (+25.8 uplift)** while maintaining an extraordinary **39.3 average** across 579 pressure deliveries! In death overs under pressure, his strike rate reaches **175.3**. He doesn't just survive pressure — he accelerates through it.

### 🛡️ The #1 Clutch Bowler: Sunil Narine (SupeRR Rating: 98.0)
* **The Story:** When batting teams go into all-out attack mode, Narine creates an impenetrable fortress.
* **The Evidence:** Across 379 high-pressure deliveries, Narine concedes just **5.37 runs per over** — saving **1.97 RPO** compared to standard match situations, while taking **26 wickets**. In death overs under pressure, his economy remains an unbelievable **5.48 RPO**!

---

## 💻 Taking it Beyond Code: The Interactive Streamlit Dashboard

To give franchise coaches and scouts instant visual access, we developed and deployed an interactive Streamlit application featuring:
1. **Top 10 Leaderboards**: Instant sorting, rating distributions, and CSV exports.
2. **2D Quadrant Matrix**: Plotly scatter plots separating baseline performers from genuine clutch finishers.
3. **6-Dimensional Spider Radar**: Visualizing power, consistency, dot-ball control, and phase splits.
4. **Head-to-Head Duel**: Comparing players side-by-side with automated winning badges.
5. **Live Pressure Simulator**: A real-time pressure gauge calculating match stakes as overs and wickets change.

---

## 🔗 Project Links

* **Live GitHub Repository:** [https://github.com/Subham-614/superr-selector-s2](https://github.com/Subham-614/superr-selector-s2)
* **Interactive Streamlit App:** Deployed on Streamlit Cloud
* **12-Page Methodology Report:** Available in the repo (`outputs/superr_selector_s2_methodology_report.pdf`)

---

*Special thanks to @rajasthanroyals and @unstop.world for curating such a rich, realistic, and challenging analytics hackathon!*
