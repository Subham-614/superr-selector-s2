import os
import glob
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# 1. PAGE CONFIGURATION & STYLING (Rajasthan Royals Aesthetic)
# =============================================================================
st.set_page_config(
    page_title="SupeRR Selector S2 | Rajasthan Royals Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Royal Pink / Navy / Gold Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Top banner */
    .rr-header {
        background: linear-gradient(135deg, #0A192F 0%, #1D3461 50%, #D91A5B 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(217, 26, 91, 0.18);
    }
    .rr-title {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .rr-subtitle {
        font-size: 15px;
        color: #E2E8F0;
        margin-top: 6px;
        font-weight: 500;
    }
    
    /* Stat cards */
    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #D91A5B;
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .stat-label {
        font-size: 12px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-val {
        font-size: 24px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }
    .stat-sub {
        font-size: 12px;
        color: #10B981;
        font-weight: 600;
        margin-top: 2px;
    }
    
    /* Pills & badges */
    .badge-hp {
        background: #FEF2F2;
        color: #DC2626;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid #FCA5A5;
    }
    .badge-gold {
        background: #FEF3C7;
        color: #92400E;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid #FCD34D;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. DATA LOADERS & CACHING
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_leaderboards():
    bat_top10 = pd.read_csv(os.path.join(BASE_DIR, "data/processed/final_top10_batters.csv"))
    bowl_top10 = pd.read_csv(os.path.join(BASE_DIR, "data/processed/final_top10_bowlers.csv"))
    bat_all = pd.read_csv(os.path.join(BASE_DIR, "data/processed/all_eligible_batters_ranked.csv"))
    bowl_all = pd.read_csv(os.path.join(BASE_DIR, "data/processed/all_eligible_bowlers_ranked.csv"))
    return bat_top10, bowl_top10, bat_all, bowl_all

@st.cache_data
def load_deciles():
    dec_path = os.path.join(BASE_DIR, "data/processed/decile_validation.csv")
    if os.path.exists(dec_path):
        return pd.read_csv(dec_path)
    return None

@st.cache_data
def load_player_splits():
    bp_path = os.path.join(BASE_DIR, "data/processed/batter_phase_splits.parquet")
    bt_path = os.path.join(BASE_DIR, "data/processed/batter_type_splits.parquet")
    bw_path = os.path.join(BASE_DIR, "data/processed/bowler_phase_splits.parquet")
    
    bp = pd.read_parquet(bp_path) if os.path.exists(bp_path) else None
    bt = pd.read_parquet(bt_path) if os.path.exists(bt_path) else None
    bw = pd.read_parquet(bw_path) if os.path.exists(bw_path) else None
    return bp, bt, bw

@st.cache_data
def load_delivery_sample_or_full():
    parquet_path = os.path.join(BASE_DIR, "data/processed/step2_pressure_indexed_bbb.parquet")
    csv_path = os.path.join(BASE_DIR, "data/processed/step2_pressure_indexed_bbb.csv")
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        return pd.read_csv(csv_path, low_memory=False)
    return None

# Load core datasets
try:
    bat_top10, bowl_top10, bat_all, bowl_all = load_leaderboards()
    dec_df = load_deciles()
    bat_phase_df, bat_type_df, bowl_phase_df = load_player_splits()
    df_bbb = load_delivery_sample_or_full()
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# =============================================================================
# 3. TOP BANNER & HIGH LEVEL METRICS
# =============================================================================
st.markdown("""
<div class="rr-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div class="rr-title">🏏 SupeRR Selector Season 2</div>
            <div class="rr-subtitle">Rajasthan Royals Hackathon | Identifying the Most Reliable T20 Players Under Pressure (2022–2026)</div>
        </div>
        <div>
            <span class="badge-gold">👑 RR Analytics</span> &nbsp;
            <span class="badge-hp">⚡ Continuous Pressure Index</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top KPI Row
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-label">Deliveries Analyzed</div>
        <div class="stat-val">200,999</div>
        <div class="stat-sub">883 Matches | 141 Comps</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="stat-card" style="border-left-color: #EF4444;">
        <div class="stat-label">High-Pressure Deliveries</div>
        <div class="stat-val">50,250 <span style="font-size:14px; color:#DC2626;">(Top 25%)</span></div>
        <div class="stat-sub" style="color:#DC2626;">Cutoff: Pressure Index ≥ 59.73</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="stat-card" style="border-left-color: #F59E0B;">
        <div class="stat-label">#1 Clutch Batter</div>
        <div class="stat-val" style="font-size:20px;">{bat_top10.iloc[0]['striker_name']}</div>
        <div class="stat-sub" style="color:#B45309;">SupeRR Rating: 98.0 | HP SR: 162.9 (+25.8)</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="stat-card" style="border-left-color: #10B981;">
        <div class="stat-label">#1 Clutch Bowler</div>
        <div class="stat-val" style="font-size:20px;">{bowl_top10.iloc[0]['bowler_name']}</div>
        <div class="stat-sub" style="color:#047857;">SupeRR Rating: 98.0 | HP Econ: 5.37 (Save: 1.97)</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# 4. TABS NAVIGATION
# =============================================================================
tabs = st.tabs([
    "🏆 Top 10 Leaderboards",
    "🎯 2D Quadrant Matrix",
    "🔬 Player Profiler",
    "⚔️ Head-to-Head Duel",
    "⚡ Live Pressure Simulator",
    "📈 Empirical Validation & Methodology"
])

# -----------------------------------------------------------------------------
# TAB 1: TOP 10 LEADERBOARDS
# -----------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🏆 SupeRR Selector Official Rankings")
    st.caption("Standardized SupeRR Rating (0–100) combining High-Pressure RAAE (55%), Pressure Uplift Delta (25%), and Innings Consistency (20%) with Empirical Bayes shrinkage.")
    
    subtab_bat, subtab_bowl, subtab_pool = st.tabs(["🏏 Top 10 Clutch Batters", "🎯 Top 10 Clutch Bowlers", "🔍 Complete Player Pool"])
    
    # --- Batters Subtab ---
    with subtab_bat:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            # Bar chart of top 10 batters
            bat_plot = bat_top10.sort_values(by="superr_rating", ascending=True)
            fig_bat = px.bar(
                bat_plot,
                x="superr_rating",
                y="striker_name",
                orientation="h",
                text="superr_rating",
                color="sr_delta",
                color_continuous_scale="Viridis",
                labels={"superr_rating": "SupeRR Rating", "striker_name": "Batter", "sr_delta": "SR Delta (+/-)"},
                title="<b>Top 10 Batters: SupeRR Rating & Pressure Uplift</b>"
            )
            fig_bat.update_traces(texttemplate='%{text:.1f}', textposition='inside')
            fig_bat.update_layout(height=450, margin=dict(l=0, r=20, t=40, b=20), xaxis_range=[90, 100])
            st.plotly_chart(fig_bat, use_container_width=True)
            
        with c2:
            st.markdown("#### 🌟 Key Analytical Highlights")
            st.markdown("""
            * **#1 Namboori Tilak Varma (98.0)**: Elite middle-order finisher. Under high pressure, his strike rate surges from **137.0 to 162.9 (+25.8 uplift)** while maintaining a stellar **39.3 average**.
            * **#2 Andre Russell (97.1)**: Devastating firepower under pressure (**173.8 HP SR**, 27.1% boundaries), outperforming his already high baseline.
            * **#3 Nicholas Pooran (96.6)**: Peerless consistency (72.0% qualified innings success) and **161.5 HP SR**.
            * **#6 Jos Buttler (95.8)**: Highest high-pressure strike rate (**191.8**) with an extraordinary **+39.3 SR surge** over baseline!
            """)
            st.download_button(
                label="📥 Download Top 10 Batters CSV",
                data=bat_top10.to_csv(index=False),
                file_name="final_top10_batters.csv",
                mime="text/csv"
            )
            
        # Batters Table
        st.markdown("#### 📋 Detailed Top 10 Batters Statistics")
        show_bat = bat_top10[['rank', 'striker_name', 'hp_balls', 'hp_runs', 'hp_sr', 'base_sr', 'sr_delta', 'hp_avg', 'hp_boundary_pct', 'superr_rating']].copy()
        show_bat.columns = ['Rank', 'Player', 'HP Balls', 'HP Runs', 'HP SR', 'Base SR', 'SR Delta', 'HP Avg', 'Boundary %', 'SupeRR Rating']
        show_bat['HP SR'] = show_bat['HP SR'].round(1)
        show_bat['Base SR'] = show_bat['Base SR'].round(1)
        show_bat['SR Delta'] = show_bat['SR Delta'].apply(lambda x: f"+{x:.1f}" if x >= 0 else f"{x:.1f}")
        show_bat['HP Avg'] = show_bat['HP Avg'].round(1)
        show_bat['Boundary %'] = (show_bat['Boundary %']).round(1).astype(str) + "%"
        show_bat['SupeRR Rating'] = show_bat['SupeRR Rating'].round(1)
        st.dataframe(show_bat, use_container_width=True, hide_index=True)

    # --- Bowlers Subtab ---
    with subtab_bowl:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            bowl_plot = bowl_top10.sort_values(by="superr_rating", ascending=True)
            fig_bowl = px.bar(
                bowl_plot,
                x="superr_rating",
                y="bowler_name",
                orientation="h",
                text="superr_rating",
                color="econ_saved_vs_base",
                color_continuous_scale="Teal",
                labels={"superr_rating": "SupeRR Rating", "bowler_name": "Bowler", "econ_saved_vs_base": "Econ Saved (rpo)"},
                title="<b>Top 10 Bowlers: SupeRR Rating & Economy Suppression</b>"
            )
            fig_bowl.update_traces(texttemplate='%{text:.1f}', textposition='inside')
            fig_bowl.update_layout(height=450, margin=dict(l=0, r=20, t=40, b=20), xaxis_range=[85, 100])
            st.plotly_chart(fig_bowl, use_container_width=True)
            
        with c2:
            st.markdown("#### 🌟 Key Analytical Highlights")
            st.markdown("""
            * **#1 Sunil Narine (98.0)**: Unrivaled pressure containment. Under top-25% pressure, his economy drops to a microscopic **5.37 RPO** (saving **1.97 RPO** vs baseline) with **26 wickets**.
            * **#2 Mohammad Nawaz (97.7)**: Exceptional T20I control facing top-ranked international teams (**5.56 HP Econ**, **10.5 HP Strike Rate**).
            * **#3 Shaheen Afridi (97.7)**: Lethal strike bowler in high-leverage powerplay and death overs (**9.9 balls per wicket**).
            * **#5 Kuldeep Yadav (97.5)** & **#7 Jasprit Bumrah (93.3)**: High-volume pillars maintaining sub-7.0 economies across 500+ pressure balls.
            """)
            st.download_button(
                label="📥 Download Top 10 Bowlers CSV",
                data=bowl_top10.to_csv(index=False),
                file_name="final_top10_bowlers.csv",
                mime="text/csv"
            )

        # Bowlers Table
        st.markdown("#### 📋 Detailed Top 10 Bowlers Statistics")
        show_bowl = bowl_top10[['rank', 'bowler_name', 'hp_legal_balls', 'hp_wickets', 'hp_econ', 'base_econ', 'econ_saved_vs_base', 'hp_sr', 'hp_dot_pct', 'superr_rating']].copy()
        show_bowl.columns = ['Rank', 'Player', 'HP Balls', 'HP Wkts', 'HP Econ', 'Base Econ', 'Econ Saved', 'HP SR', 'Dot %', 'SupeRR Rating']
        show_bowl['HP Econ'] = show_bowl['HP Econ'].round(2)
        show_bowl['Base Econ'] = show_bowl['Base Econ'].round(2)
        show_bowl['Econ Saved'] = show_bowl['Econ Saved'].apply(lambda x: f"+{x:.2f}" if x >= 0 else f"{x:.2f}")
        show_bowl['HP SR'] = show_bowl['HP SR'].round(1)
        show_bowl['Dot %'] = (show_bowl['Dot %']).round(1).astype(str) + "%"
        show_bowl['SupeRR Rating'] = show_bowl['SupeRR Rating'].round(1)
        st.dataframe(show_bowl, use_container_width=True, hide_index=True)

    # --- Pool Explorer Subtab ---
    with subtab_pool:
        st.markdown("#### 🔍 Filter & Explore All Eligible Players")
        role_choice = st.radio("Select Player Role:", ["Batters (48 eligible)", "Bowlers (68 eligible)"], horizontal=True)
        col_f1, col_f2 = st.columns(2)
        
        if "Batters" in role_choice:
            with col_f1:
                min_b = st.slider("Minimum HP Balls Faced:", 200, int(bat_all["hp_balls"].max()), 200, step=25)
            with col_f2:
                search_q = st.text_input("Search Batter Name:", "")
            
            filtered = bat_all[bat_all["hp_balls"] >= min_b].copy()
            if search_q:
                filtered = filtered[filtered["striker_name"].str.contains(search_q, case=False, na=False)]
            
            st.write(f"Showing **{len(filtered)}** qualified batters:")
            st.dataframe(
                filtered[['rank', 'striker_name', 'hp_balls', 'hp_runs', 'hp_sr', 'base_sr', 'sr_delta', 'hp_avg', 'superr_rating']].round(2),
                use_container_width=True, hide_index=True
            )
        else:
            with col_f1:
                min_b = st.slider("Minimum HP Legal Balls Bowled:", 200, int(bowl_all["hp_legal_balls"].max()), 200, step=25)
            with col_f2:
                search_q = st.text_input("Search Bowler Name:", "")
            
            filtered = bowl_all[bowl_all["hp_legal_balls"] >= min_b].copy()
            if search_q:
                filtered = filtered[filtered["bowler_name"].str.contains(search_q, case=False, na=False)]
            
            st.write(f"Showing **{len(filtered)}** qualified bowlers:")
            st.dataframe(
                filtered[['rank', 'bowler_name', 'hp_legal_balls', 'hp_wickets', 'hp_econ', 'base_econ', 'econ_saved_vs_base', 'hp_sr', 'superr_rating']].round(2),
                use_container_width=True, hide_index=True
            )

# -----------------------------------------------------------------------------
# TAB 2: 2D QUADRANT MATRIX
# -----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 🎯 2D Quadrant Matrix: Baseline vs. High-Pressure Execution")
    st.caption("Decoupling standard match output from clutch performance across 200,999 deliveries.")
    
    mat_type = st.radio("Select Matrix View:", ["Batters: Baseline SR vs. High-Pressure SR", "Bowlers: High-Pressure Economy vs. Strike Rate"], horizontal=True)
    
    if "Batters" in mat_type:
        fig_quad = go.Figure()
        
        # Others
        others = bat_all[bat_all["rank"] > 10]
        fig_quad.add_trace(go.Scatter(
            x=others["base_sr"],
            y=others["hp_sr"],
            mode="markers",
            marker=dict(size=others["hp_balls"] / 15, color="#94A3B8", opacity=0.6, line=dict(width=0.5, color="#64748B")),
            text=others["striker_name"],
            customdata=np.stack((others["rank"], others["hp_balls"], others["sr_delta"], others["superr_rating"]), axis=-1),
            hovertemplate="<b>%{text}</b> (Rank #%{customdata[0]})<br>Base SR: %{x:.1f}<br>HP SR: %{y:.1f}<br>SR Delta: +%{customdata[2]:.1f}<br>HP Balls: %{customdata[1]}<br>SupeRR: %{customdata[3]:.1f}<extra></extra>",
            name="Eligible Batters (Rank 11–48)"
        ))
        
        # Top 10
        top10 = bat_all[bat_all["rank"] <= 10]
        fig_quad.add_trace(go.Scatter(
            x=top10["base_sr"],
            y=top10["hp_sr"],
            mode="markers+text",
            marker=dict(size=top10["hp_balls"] / 12, color=top10["superr_rating"], colorscale="YlOrRd", showscale=True,
                        colorbar=dict(title="SupeRR Rating", thickness=15), line=dict(width=1.5, color="#78350F")),
            text=[f"#{int(r['rank'])} {r['striker_name'].split()[-1]}" for _, r in top10.iterrows()],
            textposition="top center",
            customdata=np.stack((top10["rank"], top10["hp_balls"], top10["sr_delta"], top10["superr_rating"]), axis=-1),
            hovertemplate="<b>%{text}</b><br>Base SR: %{x:.1f}<br>HP SR: %{y:.1f}<br>SR Delta: +%{customdata[2]:.1f}<br>HP Balls: %{customdata[1]}<br>SupeRR: %{customdata[3]:.1f}<extra></extra>",
            name="Top 10 Clutch Batters"
        ))
        
        # Parity Line (y = x)
        fig_quad.add_trace(go.Scatter(
            x=[115, 195], y=[115, 195],
            mode="lines", line=dict(dash="dash", color="#64748B", width=1.5),
            name="Parity Line (HP SR = Base SR)"
        ))
        
        # Quadrant annotations
        fig_quad.add_annotation(x=190, y=198, text="🔥 Elite Finishers<br>(High Base + High HP)", showarrow=False, font=dict(color="#D97706", size=11, family="Inter"))
        fig_quad.add_annotation(x=125, y=190, text="⚡ Pressure Surfers<br>(Surges under pressure)", showarrow=False, font=dict(color="#2563EB", size=11, family="Inter"))
        
        fig_quad.update_layout(
            title="<b>Batting Matrix: Baseline Strike Rate vs. High-Pressure Strike Rate</b>",
            xaxis_title="Baseline Strike Rate (Standard Pressure)",
            yaxis_title="High-Pressure Strike Rate (Top 25% Pressure)",
            height=580,
            template="plotly_white",
            legend=dict(yanchor="bottom", y=0.02, xanchor="right", x=0.98)
        )
        st.plotly_chart(fig_quad, use_container_width=True)
        
    else:
        fig_quad_b = go.Figure()
        
        # Others
        others_b = bowl_all[bowl_all["rank"] > 10]
        fig_quad_b.add_trace(go.Scatter(
            x=others_b["hp_econ"],
            y=others_b["hp_sr"],
            mode="markers",
            marker=dict(size=others_b["hp_wickets"] * 2.2, color="#94A3B8", opacity=0.6, line=dict(width=0.5, color="#64748B")),
            text=others_b["bowler_name"],
            customdata=np.stack((others_b["rank"], others_b["hp_wickets"], others_b["econ_saved_vs_base"], others_b["superr_rating"]), axis=-1),
            hovertemplate="<b>%{text}</b> (Rank #%{customdata[0]})<br>HP Econ: %{x:.2f}<br>HP SR: %{y:.1f}<br>Econ Saved: %{customdata[2]:.2f}<br>HP Wkts: %{customdata[1]}<br>SupeRR: %{customdata[3]:.1f}<extra></extra>",
            name="Eligible Bowlers (Rank 11–68)"
        ))
        
        # Top 10
        top10_b = bowl_all[bowl_all["rank"] <= 10]
        fig_quad_b.add_trace(go.Scatter(
            x=top10_b["hp_econ"],
            y=top10_b["hp_sr"],
            mode="markers+text",
            marker=dict(size=top10_b["hp_wickets"] * 2.5, color=top10_b["superr_rating"], colorscale="Teal", showscale=True,
                        colorbar=dict(title="SupeRR Rating", thickness=15), line=dict(width=1.5, color="#044E54")),
            text=[f"#{int(r['rank'])} {r['bowler_name'].split()[-1]}" for _, r in top10_b.iterrows()],
            textposition="top center",
            customdata=np.stack((top10_b["rank"], top10_b["hp_wickets"], top10_b["econ_saved_vs_base"], top10_b["superr_rating"]), axis=-1),
            hovertemplate="<b>%{text}</b><br>HP Econ: %{x:.2f}<br>HP SR: %{y:.1f}<br>Econ Saved: %{customdata[2]:.2f}<br>HP Wkts: %{customdata[1]}<br>SupeRR: %{customdata[3]:.1f}<extra></extra>",
            name="Top 10 Clutch Bowlers"
        ))
        
        # Peer Averages
        mean_econ = bowl_all["hp_econ"].mean()
        mean_sr = bowl_all["hp_sr"].mean()
        fig_quad_b.add_vline(x=mean_econ, line=dict(dash="dash", color="#64748B", width=1), annotation_text=f"Mean Econ ({mean_econ:.2f})")
        fig_quad_b.add_hline(y=mean_sr, line=dict(dash="dash", color="#64748B", width=1), annotation_text=f"Mean SR ({mean_sr:.1f})")
        
        # Reverse axes because lower econ and lower SR are better
        fig_quad_b.update_xaxes(autorange="reversed", title="High-Pressure Economy Rate (Lower = Better ◀)")
        fig_quad_b.update_yaxes(autorange="reversed", title="High-Pressure Bowling Strike Rate (Lower = Better ▲)")
        
        fig_quad_b.add_annotation(x=5.8, y=10.0, text="🛡️ Elite Clutch Fortress<br>(Sub-7.0 Econ + Sub-12 SR)", showarrow=False, font=dict(color="#0F766E", size=11, family="Inter"))
        
        fig_quad_b.update_layout(
            title="<b>Bowling Matrix: Economy Rate (Containment) vs. Bowling Strike Rate (Penetration)</b>",
            height=580,
            template="plotly_white",
            legend=dict(yanchor="bottom", y=0.02, xanchor="left", x=0.02)
        )
        st.plotly_chart(fig_quad_b, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: PLAYER DEEP-DIVE & RADAR PROFILER
# -----------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🔬 Player Deep-Dive & Multi-Dimensional Radar Profiler")
    
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        p_role = st.radio("Choose Role:", ["Batter", "Bowler"], horizontal=True)
    with col_sel2:
        if p_role == "Batter":
            player_list = bat_all["striker_name"].tolist()
            chosen_p = st.selectbox("Select Player:", player_list, index=0)
            p_data = bat_all[bat_all["striker_name"] == chosen_p].iloc[0]
        else:
            player_list = bowl_all["bowler_name"].tolist()
            chosen_p = st.selectbox("Select Player:", player_list, index=0)
            p_data = bowl_all[bowl_all["bowler_name"] == chosen_p].iloc[0]

    # Player Header Cards
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Overall Rank", f"#{int(p_data['rank'])}")
    with p2:
        st.metric("SupeRR Rating", f"{p_data['superr_rating']:.1f} / 100")
    with p3:
        if p_role == "Batter":
            st.metric("HP Strike Rate", f"{p_data['hp_sr']:.1f}", delta=f"{p_data['sr_delta']:.1f} vs Base")
        else:
            st.metric("HP Economy", f"{p_data['hp_econ']:.2f}", delta=f"-{p_data['econ_saved_vs_base']:.2f} rpo", delta_color="inverse")
    with p4:
        st.metric("Opposition Quality Weight", f"{p_data['mean_opp_weight']:.3f}x", help="1.00 = ICC Top-Tier Opponents")

    st.markdown("---")
    
    # Visual Breakdown: Radar Chart + Phase Splits
    col_rad, col_splits = st.columns([1, 1.2])
    
    with col_rad:
        st.markdown(f"#### 🕸️ 6-Dimensional Clutch Radar Profile")
        if p_role == "Batter":
            categories = ["HP Strike Rate", "Baseline SR", "Pressure Uplift", "HP Avg / Dismissal", "Boundary %", "Innings Consistency"]
            # Min-Max scaled values across pool for radar
            v1 = np.clip((p_data["hp_sr"] - 110) / 80 * 100, 10, 100)
            v2 = np.clip((p_data["base_sr"] - 110) / 80 * 100, 10, 100)
            v3 = np.clip((p_data["sr_delta"] + 15) / 55 * 100, 10, 100)
            v4 = np.clip((p_data["hp_avg"] - 15) / 35 * 100, 10, 100)
            v5 = np.clip((p_data["hp_boundary_pct"] - 10) / 25 * 100, 10, 100)
            v6 = np.clip((p_data["hp_consistency_rate"]) * 100, 10, 100)
            values = [v1, v2, v3, v4, v5, v6]
        else:
            categories = ["HP Economy (Containment)", "Baseline Economy", "Economy Saved", "HP Wicket Strike Rate", "Dot Ball %", "Spell Consistency"]
            v1 = np.clip((12.0 - p_data["hp_econ"]) / 7.0 * 100, 10, 100)
            v2 = np.clip((11.0 - p_data["base_econ"]) / 6.0 * 100, 10, 100)
            v3 = np.clip((p_data["econ_saved_vs_base"] + 1.0) / 3.5 * 100, 10, 100)
            v4 = np.clip((25.0 - p_data["hp_sr"]) / 17.0 * 100, 10, 100)
            v5 = np.clip((p_data["hp_dot_pct"] - 25) / 30 * 100, 10, 100)
            v6 = np.clip((p_data["hp_spell_success_rate"]) * 100, 10, 100)
            values = [v1, v2, v3, v4, v5, v6]
            
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(217, 26, 91, 0.25)',
            line=dict(color='#D91A5B', width=2),
            name=chosen_p
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=380,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_splits:
        st.markdown(f"#### 📊 Phase-by-Phase Performance Splits")
        if p_role == "Batter" and bat_phase_df is not None:
            sub_p = bat_phase_df[bat_phase_df["striker_name"] == chosen_p].copy()
            if not sub_p.empty:
                sub_p["Pressure Zone"] = np.where(sub_p["is_high_pressure"] == 1, "High Pressure", "Standard Pressure")
                fig_phase = px.bar(
                    sub_p,
                    x="phase",
                    y="sr",
                    color="Pressure Zone",
                    barmode="group",
                    color_discrete_map={"High Pressure": "#D91A5B", "Standard Pressure": "#1D3461"},
                    labels={"phase": "Match Phase", "sr": "Strike Rate"},
                    text_auto=".1f",
                    title="<b>Strike Rate Across Match Phases</b>"
                )
                fig_phase.update_layout(height=360, margin=dict(l=0, r=20, t=40, b=20))
                st.plotly_chart(fig_phase, use_container_width=True)
            else:
                st.info("No phase split records found for this player.")
        elif p_role == "Bowler" and bowl_phase_df is not None:
            sub_b = bowl_phase_df[bowl_phase_df["bowler_name"] == chosen_p].copy()
            if not sub_b.empty:
                sub_b["Pressure Zone"] = np.where(sub_b["is_high_pressure"] == 1, "High Pressure", "Standard Pressure")
                fig_phase_b = px.bar(
                    sub_b,
                    x="phase",
                    y="econ",
                    color="Pressure Zone",
                    barmode="group",
                    color_discrete_map={"High Pressure": "#0F766E", "Standard Pressure": "#1D3461"},
                    labels={"phase": "Match Phase", "econ": "Economy Rate (RPO)"},
                    text_auto=".2f",
                    title="<b>Economy Rate Across Match Phases</b>"
                )
                fig_phase_b.update_layout(height=360, margin=dict(l=0, r=20, t=40, b=20))
                st.plotly_chart(fig_phase_b, use_container_width=True)
            else:
                st.info("No phase split records found for this player.")

# -----------------------------------------------------------------------------
# TAB 4: HEAD-TO-HEAD CLUTCH DUEL
# -----------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### ⚔️ Head-to-Head Clutch Duel")
    st.caption("Compare two players across all high-pressure metrics to settle selection debates.")
    
    duel_role = st.radio("Duel Role:", ["Batters", "Bowlers"], horizontal=True, key="duel_role")
    
    col_p1, col_p2 = st.columns(2)
    if duel_role == "Batters":
        bat_names = bat_all["striker_name"].tolist()
        with col_p1:
            p1_name = st.selectbox("Select Player 1 (Red/Pink):", bat_names, index=0)
        with col_p2:
            p2_name = st.selectbox("Select Player 2 (Blue):", bat_names, index=1 if len(bat_names) > 1 else 0)
            
        r1 = bat_all[bat_all["striker_name"] == p1_name].iloc[0]
        r2 = bat_all[bat_all["striker_name"] == p2_name].iloc[0]
        
        # Dual Radar Chart
        cats = ["HP Strike Rate", "Baseline SR", "Pressure Uplift", "HP Avg", "Boundary %", "Innings Consistency"]
        v1_list = [
            np.clip((r1["hp_sr"] - 110) / 80 * 100, 10, 100),
            np.clip((r1["base_sr"] - 110) / 80 * 100, 10, 100),
            np.clip((r1["sr_delta"] + 15) / 55 * 100, 10, 100),
            np.clip((r1["hp_avg"] - 15) / 35 * 100, 10, 100),
            np.clip((r1["hp_boundary_pct"] - 10) / 25 * 100, 10, 100),
            np.clip((r1["hp_consistency_rate"]) * 100, 10, 100)
        ]
        v2_list = [
            np.clip((r2["hp_sr"] - 110) / 80 * 100, 10, 100),
            np.clip((r2["base_sr"] - 110) / 80 * 100, 10, 100),
            np.clip((r2["sr_delta"] + 15) / 55 * 100, 10, 100),
            np.clip((r2["hp_avg"] - 15) / 35 * 100, 10, 100),
            np.clip((r2["hp_boundary_pct"] - 10) / 25 * 100, 10, 100),
            np.clip((r2["hp_consistency_rate"]) * 100, 10, 100)
        ]
        
        fig_duel = go.Figure()
        fig_duel.add_trace(go.Scatterpolar(r=v1_list + [v1_list[0]], theta=cats + [cats[0]], fill='toself', fillcolor='rgba(217, 26, 91, 0.3)', line=dict(color='#D91A5B', width=2), name=p1_name))
        fig_duel.add_trace(go.Scatterpolar(r=v2_list + [v2_list[0]], theta=cats + [cats[0]], fill='toself', fillcolor='rgba(29, 52, 97, 0.3)', line=dict(color='#1D3461', width=2), name=p2_name))
        fig_duel.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420, margin=dict(l=40, r=40, t=30, b=30))
        
        st.plotly_chart(fig_duel, use_container_width=True)
        
        # Metric comparison table
        comp_df = pd.DataFrame({
            "Metric": ["SupeRR Rating", "Rank", "High-Pressure SR", "Baseline SR", "SR Uplift Delta", "High-Pressure Avg", "Boundary %", "HP Balls Faced"],
            p1_name: [f"{r1['superr_rating']:.1f}", f"#{int(r1['rank'])}", f"{r1['hp_sr']:.1f}", f"{r1['base_sr']:.1f}", f"+{r1['sr_delta']:.1f}", f"{r1['hp_avg']:.1f}", f"{r1['hp_boundary_pct']:.1f}%", f"{int(r1['hp_balls'])}"],
            p2_name: [f"{r2['superr_rating']:.1f}", f"#{int(r2['rank'])}", f"{r2['hp_sr']:.1f}", f"{r2['base_sr']:.1f}", f"+{r2['sr_delta']:.1f}", f"{r2['hp_avg']:.1f}", f"{r2['hp_boundary_pct']:.1f}%", f"{int(r2['hp_balls'])}"],
            "Winner": [
                p1_name if r1['superr_rating'] > r2['superr_rating'] else p2_name,
                p1_name if r1['rank'] < r2['rank'] else p2_name,
                p1_name if r1['hp_sr'] > r2['hp_sr'] else p2_name,
                p1_name if r1['base_sr'] > r2['base_sr'] else p2_name,
                p1_name if r1['sr_delta'] > r2['sr_delta'] else p2_name,
                p1_name if r1['hp_avg'] > r2['hp_avg'] else p2_name,
                p1_name if r1['hp_boundary_pct'] > r2['hp_boundary_pct'] else p2_name,
                p1_name if r1['hp_balls'] > r2['hp_balls'] else p2_name,
            ]
        })
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
    else:
        bowl_names = bowl_all["bowler_name"].tolist()
        with col_p1:
            p1_name = st.selectbox("Select Bowler 1 (Teal):", bowl_names, index=0)
        with col_p2:
            p2_name = st.selectbox("Select Bowler 2 (Navy):", bowl_names, index=1 if len(bowl_names) > 1 else 0)
            
        r1 = bowl_all[bowl_all["bowler_name"] == p1_name].iloc[0]
        r2 = bowl_all[bowl_all["bowler_name"] == p2_name].iloc[0]
        
        # Dual Radar Chart
        cats = ["HP Economy", "Baseline Economy", "Econ Saved", "HP Strike Rate", "Dot Ball %", "Spell Consistency"]
        v1_list = [
            np.clip((12.0 - r1["hp_econ"]) / 7.0 * 100, 10, 100),
            np.clip((11.0 - r1["base_econ"]) / 6.0 * 100, 10, 100),
            np.clip((r1["econ_saved_vs_base"] + 1.0) / 3.5 * 100, 10, 100),
            np.clip((25.0 - r1["hp_sr"]) / 17.0 * 100, 10, 100),
            np.clip((r1["hp_dot_pct"] - 25) / 30 * 100, 10, 100),
            np.clip((r1["hp_spell_success_rate"]) * 100, 10, 100)
        ]
        v2_list = [
            np.clip((12.0 - r2["hp_econ"]) / 7.0 * 100, 10, 100),
            np.clip((11.0 - r2["base_econ"]) / 6.0 * 100, 10, 100),
            np.clip((r2["econ_saved_vs_base"] + 1.0) / 3.5 * 100, 10, 100),
            np.clip((25.0 - r2["hp_sr"]) / 17.0 * 100, 10, 100),
            np.clip((r2["hp_dot_pct"] - 25) / 30 * 100, 10, 100),
            np.clip((r2["hp_spell_success_rate"]) * 100, 10, 100)
        ]
        
        fig_duel_b = go.Figure()
        fig_duel_b.add_trace(go.Scatterpolar(r=v1_list + [v1_list[0]], theta=cats + [cats[0]], fill='toself', fillcolor='rgba(15, 118, 110, 0.3)', line=dict(color='#0F766E', width=2), name=p1_name))
        fig_duel_b.add_trace(go.Scatterpolar(r=v2_list + [v2_list[0]], theta=cats + [cats[0]], fill='toself', fillcolor='rgba(29, 52, 97, 0.3)', line=dict(color='#1D3461', width=2), name=p2_name))
        fig_duel_b.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=420, margin=dict(l=40, r=40, t=30, b=30))
        
        st.plotly_chart(fig_duel_b, use_container_width=True)
        
        comp_df_b = pd.DataFrame({
            "Metric": ["SupeRR Rating", "Rank", "High-Pressure Economy", "Baseline Economy", "Economy Saved", "HP Strike Rate", "Dot %", "HP Balls Bowled"],
            p1_name: [f"{r1['superr_rating']:.1f}", f"#{int(r1['rank'])}", f"{r1['hp_econ']:.2f}", f"{r1['base_econ']:.2f}", f"+{r1['econ_saved_vs_base']:.2f}", f"{r1['hp_sr']:.1f}", f"{r1['hp_dot_pct']:.1f}%", f"{int(r1['hp_legal_balls'])}"],
            p2_name: [f"{r2['superr_rating']:.1f}", f"#{int(r2['rank'])}", f"{r2['hp_econ']:.2f}", f"{r2['base_econ']:.2f}", f"+{r2['econ_saved_vs_base']:.2f}", f"{r2['hp_sr']:.1f}", f"{r2['hp_dot_pct']:.1f}%", f"{int(r2['hp_legal_balls'])}"],
            "Winner": [
                p1_name if r1['superr_rating'] > r2['superr_rating'] else p2_name,
                p1_name if r1['rank'] < r2['rank'] else p2_name,
                p1_name if r1['hp_econ'] < r2['hp_econ'] else p2_name,
                p1_name if r1['base_econ'] < r2['base_econ'] else p2_name,
                p1_name if r1['econ_saved_vs_base'] > r2['econ_saved_vs_base'] else p2_name,
                p1_name if r1['hp_sr'] < r2['hp_sr'] else p2_name,
                p1_name if r1['hp_dot_pct'] > r2['hp_dot_pct'] else p2_name,
                p1_name if r1['hp_legal_balls'] > r2['hp_legal_balls'] else p2_name,
            ]
        })
        st.dataframe(comp_df_b, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TAB 5: LIVE PRESSURE SIMULATOR & MATCH REPLAY
# -----------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### ⚡ Live Match Pressure Simulator & Historic Match Replay")
    
    sim_mode = st.radio("Mode:", ["Live Match Equation Simulator", "Historic Match Pressure Trajectory"], horizontal=True)
    
    if sim_mode == "Live Match Equation Simulator":
        st.markdown("#### 🎛️ Configure Match Situation")
        c_s1, c_s2, c_s3 = st.columns(3)
        with c_s1:
            inn = st.selectbox("Innings:", [2, 1], index=0)
            overs_done = st.slider("Overs Completed:", 0.0, 19.5, 15.0, step=0.1)
            balls_bowled = int(overs_done) * 6 + int(round((overs_done % 1) * 10))
            balls_rem = max(1, 120 - balls_bowled)
        with c_s2:
            score = st.number_input("Current Runs Scored:", min_value=0, max_value=300, value=145)
            wickets = st.slider("Wickets Lost:", 0, 9, 4)
            wkts_in_hand = 10 - wickets
        with c_s3:
            if inn == 2:
                target = st.number_input("Target Score (Innings 2):", min_value=50, max_value=300, value=185)
                runs_needed = max(0, target - score)
                rrr = (runs_needed * 6.0) / balls_rem
            else:
                target = None
                runs_needed = None
                rrr = None
            venue_par = st.slider("Venue Par RPO:", 7.0, 10.5, 8.5, step=0.1)
            is_ko = st.checkbox("Knockout / Playoff Match (+12% Stakes)", value=True)

        # Calculate 3 Pillars live
        progress = 1.0 - (balls_rem / 120.0)
        
        # Pillar 1
        if inn == 2:
            rrr_ratio = (rrr - venue_par) / max(6.0, venue_par)
            p_eq = 1.0 / (1.0 + np.exp(-(2.5 * rrr_ratio + 1.8 * (progress - 0.5))))
        else:
            par_runs_now = venue_par * (balls_bowled / 6.0)
            par_deficit = (par_runs_now - score) / 20.0
            death_boost = 0.35 + 0.08 * (overs_done - 16) if overs_done >= 16 else 0.0
            p_eq = np.clip(1.0 / (1.0 + np.exp(-(1.2 * par_deficit + 1.2 * (progress - 0.55)))) + death_boost, 0, 1)
            
        # Pillar 2
        exp_wkts = 6.5 * progress
        wkt_excess = np.clip(wickets - exp_wkts, -2.0, 6.0)
        base_wkt_load = (wickets / 9.0) ** 1.2
        p_wkt = np.clip(0.45 * base_wkt_load + 0.35 * (1.0 / (1.0 + np.exp(-0.9 * wkt_excess))), 0, 1)
        
        # Pillar 3 (Estimated leverage)
        est_wp = 0.50
        if inn == 2 and rrr is not None:
            est_wp = 1.0 / (1.0 + np.exp(0.45 * (rrr - venue_par)))
        match_closeness = 4.0 * est_wp * (1.0 - est_wp)
        ko_boost = 0.12 if is_ko else 0.0
        p_stakes = np.clip(0.50 * 0.45 + 0.40 * match_closeness + ko_boost, 0, 1)
        
        # Continuous Pressure Index
        raw_pressure = 0.40 * p_eq + 0.30 * p_wkt + 0.30 * p_stakes
        calc_pressure = np.clip(raw_pressure * 100.0, 0, 100)
        
        st.markdown("---")
        
        g1, g2 = st.columns([1, 1.2])
        with g1:
            # Pressure Index Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=calc_pressure,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "<b>Continuous Pressure Index (0–100)</b>", 'font': {'size': 18, 'color': '#0F172A'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
                    'bar': {'color': "#D91A5B" if calc_pressure >= 59.73 else "#1D3461"},
                    'steps': [
                        {'range': [0, 40], 'color': "#ECFDF5"},
                        {'range': [40, 59.73], 'color': "#FEF3C7"},
                        {'range': [59.73, 100], 'color': "#FEE2E2"}
                    ],
                    'threshold': {
                        'line': {'color': "#DC2626", 'width': 4},
                        'thickness': 0.75,
                        'value': 59.73
                    }
                }
            ))
            fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with g2:
            st.markdown("#### 🔬 Pillar Decomposition Breakdown")
            is_hp = calc_pressure >= 59.73
            status_badge = "🔥 <b>HIGH PRESSURE ZONE (Top 25%)</b>" if is_hp else "🟢 <b>STANDARD PRESSURE ZONE</b>"
            st.markdown(f"<div style='font-size:16px; margin-bottom:12px;'>Status: {status_badge}</div>", unsafe_allow_html=True)
            
            p_df = pd.DataFrame({
                "Pillar": ["Pillar 1: Equation Difficulty", "Pillar 2: Resource Depletion", "Pillar 3: Stakes & Leverage", "Composite Pressure Index"],
                "Formula Weight": ["40%", "30%", "30%", "100%"],
                "Score (0–100)": [f"{p_eq*100:.1f}", f"{p_wkt*100:.1f}", f"{p_stakes*100:.1f}", f"<b>{calc_pressure:.1f}</b>"],
                "Driver Context": [
                    f"RRR: {rrr:.2f} vs Par {venue_par:.1f}" if inn==2 else f"Score: {score} at Ov {overs_done}",
                    f"{wickets} down ({wkts_in_hand} in hand)",
                    "Playoff Stakes Closeness" if is_ko else "Standard Match Closeness",
                    "Qualifies for High-Pressure Evaluation" if is_hp else "Baseline Delivery Evaluation"
                ]
            })
            st.dataframe(p_df, use_container_width=True, hide_index=True)
            
    else:
        # Match Replay Trajectory
        st.markdown("#### 🎬 Over-by-Over Pressure & Win Probability Trajectory")
        if df_bbb is not None:
            # Get list of exciting matches
            match_summary = df_bbb.groupby(['match_id', 'comp_name', 'match_date']).agg(
                balls=('match_id', 'count'),
                max_pressure=('pressure_index', 'max')
            ).reset_index().sort_values(by='max_pressure', ascending=False)
            
            match_options = match_summary.head(30)
            chosen_m_id = st.selectbox(
                "Select Match:",
                match_options["match_id"].tolist(),
                format_func=lambda x: f"Match #{x} - {match_options[match_options['match_id']==x]['comp_name'].iloc[0]} ({match_options[match_options['match_id']==x]['match_date'].iloc[0]}) | Max Pressure: {match_options[match_options['match_id']==x]['max_pressure'].iloc[0]:.1f}"
            )
            
            m_balls = df_bbb[df_bbb["match_id"] == chosen_m_id].sort_values(by=["innings", "innings_ball_num"])
            
            # Line chart of Pressure and Win Probability
            fig_traj = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_traj.add_trace(
                go.Scatter(
                    x=np.arange(len(m_balls)),
                    y=m_balls["pressure_index"],
                    name="Pressure Index (0–100)",
                    line=dict(color="#D91A5B", width=2)
                ),
                secondary_y=False
            )
            
            fig_traj.add_trace(
                go.Scatter(
                    x=np.arange(len(m_balls)),
                    y=m_balls["win_prob_before"] * 100,
                    name="Win Probability (%)",
                    line=dict(color="#1D3461", width=2, dash="dot")
                ),
                secondary_y=True
            )
            
            # Add HP Threshold line
            fig_traj.add_hline(y=59.73, line=dict(dash="dash", color="#DC2626", width=1), secondary_y=False, annotation_text="High Pressure Threshold (59.73)")
            
            fig_traj.update_layout(
                title=f"<b>Match #{chosen_m_id} Delivery Timeline: Pressure Index vs. Win Probability</b>",
                xaxis_title="Delivery Number in Match",
                template="plotly_white",
                height=450
            )
            fig_traj.update_yaxes(title_text="Pressure Index (0–100)", secondary_y=False, range=[0, 105])
            fig_traj.update_yaxes(title_text="Win Probability (%)", secondary_y=True, range=[0, 100])
            st.plotly_chart(fig_traj, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 6: EMPIRICAL VALIDATION & METHODOLOGY
# -----------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 📈 Empirical Validation & Mathematical Methodology")
    
    # Decile Validation Chart
    if dec_df is not None:
        st.markdown("#### 🧪 Decile-by-Decile Empirical Validation across 200,999 Deliveries")
        st.caption("Proof that higher Pressure Index values capture objectively harder cricket situations.")
        
        fig_dec = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_dec.add_trace(
            go.Bar(
                x=dec_df["pressure_decile"],
                y=dec_df["bat_avg"],
                name="Batting Average",
                marker_color="#1D3461",
                text=dec_df["bat_avg"].round(1),
                textposition="inside"
            ),
            secondary_y=False
        )
        
        fig_dec.add_trace(
            go.Scatter(
                x=dec_df["pressure_decile"],
                y=dec_df["wkt_prob_pct"],
                name="Dismissal Rate per Ball (%)",
                marker=dict(color="#DC2626", size=8),
                line=dict(color="#DC2626", width=2.5)
            ),
            secondary_y=True
        )
        
        fig_dec.update_layout(
            title="<b>Empirical Proof: Batting Average Collapses by 48% while Dismissal Probability Surges by 69% from D1 to D10</b>",
            xaxis_title="Pressure Index Decile (D1 = Lowest Pressure, D10 = Highest Pressure)",
            template="plotly_white",
            height=420,
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02)
        )
        fig_dec.update_yaxes(title_text="League Batting Average", secondary_y=False, range=[0, 38])
        fig_dec.update_yaxes(title_text="Dismissal Probability (%)", secondary_y=True, range=[0, 11])
        st.plotly_chart(fig_dec, use_container_width=True)

    # Core Mathematical Formulations
    st.markdown("---")
    st.markdown("#### 📐 Mathematical Architecture")
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
        **1. Three-Pillar Continuous Pressure Index (0–100)**
        $$\\text{Pressure} = 0.40 \\cdot P_{\\text{equation}} + 0.30 \\cdot P_{\\text{wicket}} + 0.30 \\cdot P_{\\text{stakes}}$$
        * **$P_{\\text{equation}}$ (40%)**: Sigmoid scaling of Required Run Rate gap against venue/tier par RPO amplified as remaining balls decrease.
        * **$P_{\\text{wicket}}$ (30%)**: Resource depletion combining remaining wickets, ball-in-hand load, and recent collapse shocks (wickets lost in prior 12 balls).
        * **$P_{\\text{stakes}}$ (30%)**: Counterfactual Win-Probability Leverage $|\\Delta WP|$ from calibrated logistic models, playoff leverage boosts, and match closeness.
        * **Cutoff**: 75th percentile ($59.73$) isolates the top 25% most pressured balls.
        """)
    with m2:
        st.markdown("""
        **2. Runs Above Average Expectation (RAAE) & SupeRR Rating**
        $$\\text{RAAE} = (\\text{Runs Scored} - \\text{Expected Par Runs}) \\times \\text{Opp Weight}$$
        $$\\text{EB\\_RAAE} = \\frac{n}{n + \\lambda} \\cdot \\bar{x} + \\frac{\\lambda}{n + \\lambda} \\cdot \\mu_{\\text{prior}}$$
        * **Empirical Bayes Regularization**: Batting shrinkage $\\lambda=12$ and Bowling $\\lambda=16$ shrink small sample flukes back to peer means.
        * **Composite SupeRR Rating**:
        $$\\text{SupeRR} = 0.55 \\cdot z(\\text{EB\\_HP}) + 0.25 \\cdot z(\\text{EB\\_Delta}) + 0.20 \\cdot z(\\text{Consistency})$$
        * Normalized to a 0–100 scale with Rank #1 set to 98.0.
        """)

    # Download Methodology Report PDF
    st.markdown("---")
    st.markdown("#### 📑 Official Methodology Report PDF")
    pdf_path = os.path.join(BASE_DIR, "outputs/superr_selector_s2_methodology_report.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📥 Download Full 12-Page Methodology Report (PDF)",
            data=pdf_bytes,
            file_name="superr_selector_s2_methodology_report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Methodology report PDF not found in outputs directory.")

# =============================================================================
# 5. FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 13px; padding-bottom: 20px;">
    <b>SupeRR Selector Season 2</b> — Rajasthan Royals Analytics Hackathon Submission | Powered by Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
