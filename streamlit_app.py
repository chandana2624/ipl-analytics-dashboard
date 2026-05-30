import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PYODIDE / STLITE PATCH FOR PLOTLY ---
# Pyodide's pyarrow is incomplete and missing ChunkedArray. 
# Plotly's new narwhals dependency crashes when it checks for it.
try:
    import pyarrow as pa
    if not hasattr(pa, 'ChunkedArray'):
        pa.ChunkedArray = type('ChunkedArray', (), {})
    if not hasattr(pa, 'Table'):
        pa.Table = type('Table', (), {})
except Exception:
    pass
# -----------------------------------------


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="IPL Analytics Dashboard", layout="wide", page_icon="🏏")

# =====================================================
# THEME DETECTION
# =====================================================
# Streamlit exposes the active theme via st.get_option
_bg = st.get_option("theme.backgroundColor") or "#ffffff"
# Simple heuristic: if background luminance is dark, it's dark mode
_is_dark = False
try:
    _hex = _bg.lstrip("#")
    _r, _g, _b = int(_hex[0:2],16), int(_hex[2:4],16), int(_hex[4:6],16)
    _is_dark = (0.299*_r + 0.587*_g + 0.114*_b) < 128
except:
    pass

# Theme-aware colors
if _is_dark:
    BG_PAGE   = "#0e1117"
    BG_CARD   = "#1a1d23"
    BG_PLOT   = "#1a1d23"
    TEXT_MAIN  = "#e6eaf0"
    TEXT_DIM   = "#8899aa"
    TEXT_SUB   = "#667788"
    GRID_CLR   = "#2a2f38"
    BAR_BG     = "#2a2f38"
    SHADOW     = "rgba(0,0,0,0.35)"
    PLOTLY_TPL = "plotly_dark"
else:
    BG_PAGE   = "#f0f2f6"
    BG_CARD   = "#ffffff"
    BG_PLOT   = "#ffffff"
    TEXT_MAIN  = "#1a1a2e"
    TEXT_DIM   = "#999999"
    TEXT_SUB   = "#bbbbbb"
    GRID_CLR   = "#f0f0f0"
    BAR_BG     = "#eeeeee"
    SHADOW     = "rgba(0,0,0,0.07)"
    PLOTLY_TPL = "plotly_white"

# =====================================================
# GLOBAL CSS (Theme-aware)
# =====================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {BG_PAGE}; }}
    .block-container {{ padding-top: 1.5rem !important; }}

    .kpi-card {{
        background: {BG_CARD};
        border-radius: 12px;
        padding: 18px 22px 14px 22px;
        box-shadow: 0 2px 10px {SHADOW};
        border-top: 4px solid #ccc;
        height: 100%;
    }}
    .kpi-card.orange {{ border-top-color: #FF6B35; }}
    .kpi-card.purple {{ border-top-color: #7B2FBE; }}
    .kpi-card.green  {{ border-top-color: #2ECC71; }}
    .kpi-card.blue   {{ border-top-color: #3498DB; }}

    .kpi-label {{
        font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
        color: {TEXT_DIM}; text-transform: uppercase; margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 30px; font-weight: 800; color: {TEXT_MAIN}; line-height: 1.1;
    }}
    .kpi-sub {{ font-size: 12px; color: {TEXT_SUB}; margin-top: 4px; }}

    .section-header {{
        font-size: 11px; font-weight: 700; letter-spacing: 0.1em;
        color: {TEXT_DIM}; text-transform: uppercase;
        margin: 18px 0 10px 0;
        border-left: 3px solid #3498DB;
        padding-left: 10px;
    }}

    .chart-title {{
        font-size: 13px; font-weight: 700; color: {TEXT_MAIN};
        margin-bottom: 2px;
    }}
    .chart-sub {{
        font-size: 11px; color: {TEXT_DIM}; margin-bottom: 0px;
    }}

    .fullwidth-card {{
        background: {BG_CARD};
        border-radius: 12px;
        padding: 18px 20px 10px 20px;
        box-shadow: 0 2px 10px {SHADOW};
        margin-bottom: 16px;
    }}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    import os
    # Works both locally and on Streamlit Cloud
    csv_path = os.path.join(os.path.dirname(__file__), "ball_by_ball_data.csv")
    try:
        df = pd.read_csv(csv_path)
        df.drop_duplicates(inplace=True)
        return df
    except Exception as e:
        st.error(f"Could not load data. Please check path: {csv_path}")
        return pd.DataFrame()

df = load_data()

if not df.empty:

    # =====================================================
    # TITLE CARD + FILTER
    # =====================================================
    title_col, filter_col = st.columns([4, 1])
    with title_col:
        st.markdown(f"""
        <div class='kpi-card' style='border-top: 4px solid {TEXT_MAIN}; padding: 22px 28px 18px 28px;'>
            <div style='display:flex; align-items:center; gap:12px;'>
                <span style='font-size:36px;'>🏏</span>
                <div>
                    <div style='font-size:24px; font-weight:800; color:{TEXT_MAIN}; line-height:1.2;'>IPL Analytics Dashboard</div>
                    <div style='font-size:12px; color:{TEXT_DIM}; margin-top:3px; letter-spacing:0.03em;'>Ball-by-ball analysis across all IPL seasons from 2008 to 2025</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with filter_col:
        st.markdown(f"""
        <div class='kpi-card' style='border-top: 4px solid #3498DB; padding: 14px 18px 8px 18px;'>
            <div class='kpi-label'>Filter by Season</div>
        </div>
        """, unsafe_allow_html=True)
        seasons = ["All Seasons"] + list(sorted(df["season_id"].unique()))
        selected_season = st.selectbox("🗓️ Select Season", seasons, label_visibility="collapsed")

    filtered_df = df if selected_season == "All Seasons" else df[df["season_id"] == selected_season]
    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # KPI CARDS (with All Seasons comparison)
    # =====================================================
    st.markdown("<div class='section-header'>Overview</div>", unsafe_allow_html=True)

    all_runs      = int(df['total_runs'].sum())
    all_wickets   = int(df['is_wicket'].sum())
    all_matches   = df['match_id'].nunique()
    all_players   = df['batter'].nunique()

    sel_runs      = int(filtered_df['total_runs'].sum())
    sel_wickets   = int(filtered_df['is_wicket'].sum())
    sel_matches   = filtered_df['match_id'].nunique()
    sel_players   = filtered_df['batter'].nunique()

    def pct(val, total):
        return round((val / total) * 100, 1) if total else 0

    def kpi_card(color, icon, label, sel_val, all_val, unit=""):
        p = pct(sel_val, all_val)
        bar_color = {"orange":"#FF6B35","purple":"#7B2FBE","green":"#2ECC71","blue":"#3498DB"}.get(color,"#ccc")
        return f"""
        <div class='kpi-card {color}'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div class='kpi-label'>{label}</div>
                <span style='font-size:20px'>{icon}</span>
            </div>
            <div class='kpi-value'>{sel_val:,}{unit}</div>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-top:6px;'>
                <div class='kpi-sub'>All Seasons: <b style='color:{TEXT_MAIN}'>{all_val:,}{unit}</b></div>
                <div class='kpi-sub' style='color:{bar_color};font-weight:700;'>{p}%</div>
            </div>
            <div style='background:{BAR_BG};border-radius:4px;height:4px;margin-top:6px;'>
                <div style='background:{bar_color};width:{p}%;height:4px;border-radius:4px;'></div>
            </div>
        </div>"""

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(kpi_card("orange","🏏","Total Runs", sel_runs, all_runs), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("purple","🎯","Total Wickets", sel_wickets, all_wickets), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("green","🏟️","Matches Played", sel_matches, all_matches), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("blue","👤","Total Players", sel_players, all_players), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # SEASONALITY (FULL WIDTH)
    # =====================================================
    st.markdown("<div class='section-header'>Season-over-Season Performance</div>", unsafe_allow_html=True)

    season_stats = df.groupby('season_id').agg(
        Total_Runs=('total_runs', 'sum'), Matches=('match_id', 'nunique')
    ).reset_index()
    season_stats['Avg_Runs_Per_Match'] = season_stats['Total_Runs'] / season_stats['Matches']

    fig_s = go.Figure()
    fig_s.add_trace(go.Bar(x=season_stats['season_id'], y=season_stats['Total_Runs'],
                           name='Total Runs', marker_color='#a8c7fa', yaxis='y'))
    fig_s.add_trace(go.Scatter(x=season_stats['season_id'], y=season_stats['Avg_Runs_Per_Match'],
                               name='Avg Runs/Match', mode='lines+markers',
                               marker_color='#00c49f', line=dict(width=2.5), yaxis='y2'))
    fig_s.update_layout(
        template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT, height=300,
        font=dict(color=TEXT_MAIN),
        yaxis=dict(title='Total Runs', showgrid=True, gridcolor=GRID_CLR),
        yaxis2=dict(title='Avg Runs/Match', side='right', overlaying='y', showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(color=TEXT_DIM)),
        margin=dict(t=10, b=40, l=40, r=40)
    )
    fig_s.update_xaxes(type='category', showgrid=False)

    st.markdown(f"""<div class='fullwidth-card'>
        <div class='chart-title'>📊 Runs & Average per Match Trend</div>
        <div class='chart-sub'>Total Runs (bars) vs Average Runs Per Match (line) — dual-axis view</div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(fig_s, use_container_width=True)

    # =====================================================
    # ROW 1: Orange Cap + Purple Cap
    # =====================================================
    st.markdown("<div class='section-header'>Batting & Bowling Performance</div>", unsafe_allow_html=True)
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.markdown("<div class='chart-title'>🟠 Top Run Scorers (Orange Cap)</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Top 10 batters by total runs scored</div>", unsafe_allow_html=True)
        top_runs = filtered_df.groupby("batter")["batter_runs"].sum().reset_index().sort_values("batter_runs", ascending=False).head(10)
        fig_r = px.bar(top_runs, x="batter", y="batter_runs", color="batter_runs", color_continuous_scale="Oranges")
        fig_r.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT,
                            showlegend=False, font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=60,l=20,r=10), height=290, coloraxis_showscale=False,
                            yaxis=dict(showgrid=True, gridcolor=GRID_CLR), xaxis=dict(showgrid=False))
        st.plotly_chart(fig_r, use_container_width=True)

    with r1c2:
        st.markdown("<div class='chart-title'>🟣 Top Wicket Takers (Purple Cap)</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Top 10 bowlers by total wickets — horizontal bar</div>", unsafe_allow_html=True)
        top_w = filtered_df[filtered_df["is_wicket"] == True].groupby("bowler").size().reset_index(name="wickets").sort_values("wickets", ascending=True).tail(10)
        fig_w = px.bar(top_w, x="wickets", y="bowler", orientation='h', color="wickets", color_continuous_scale="Purples")
        fig_w.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT,
                            showlegend=False, font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=20,l=10,r=10), height=290, coloraxis_showscale=False,
                            yaxis=dict(showgrid=False), xaxis=dict(showgrid=True, gridcolor=GRID_CLR))
        st.plotly_chart(fig_w, use_container_width=True)

    # =====================================================
    # ROW 2: Waterfall Sixes + Pie Fours
    # =====================================================
    st.markdown("<div class='section-header'>Boundaries Analysis</div>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.markdown("<div class='chart-title'>🔥 Most Sixes</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Cumulative contribution of Top 10 six hitters</div>", unsafe_allow_html=True)
        top_6 = filtered_df[filtered_df["batter_runs"] == 6].groupby("batter").size().reset_index(name="Sixes").sort_values("Sixes", ascending=False).head(10)
        fig_6 = go.Figure(go.Waterfall(
            orientation="v", measure=["relative"] * len(top_6),
            x=top_6['batter'], y=top_6['Sixes'],
            textposition="outside", text=top_6['Sixes'].astype(str),
            connector={"line": {"color": "rgba(63,63,63,0.3)"}},
            increasing={"marker": {"color": "#FF4B4B"}},
        ))
        fig_6.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT,
                            showlegend=False, font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=60,l=20,r=10), height=290,
                            yaxis=dict(showgrid=True, gridcolor=GRID_CLR), xaxis=dict(showgrid=False))
        st.plotly_chart(fig_6, use_container_width=True)

    with r2c2:
        st.markdown("<div class='chart-title'>⚡ Most Fours</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Top 10 boundary hitters by four count</div>", unsafe_allow_html=True)
        fours = filtered_df[filtered_df["batter_runs"] == 4].groupby("batter").size().reset_index(name="Fours").sort_values("Fours", ascending=False).head(10)
        fig_4 = px.pie(fours, names="batter", values="Fours", hole=0.3, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_4.update_traces(textposition='inside', textinfo='percent+label')
        fig_4.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT,
                            font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=10,l=10,r=10), height=290,
                            legend=dict(font=dict(size=10, color=TEXT_DIM)))
        st.plotly_chart(fig_4, use_container_width=True)

    # =====================================================
    # ROW 3: Bubble + Donut
    # =====================================================
    st.markdown("<div class='section-header'>Team & Run Distribution</div>", unsafe_allow_html=True)
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.markdown("<div class='chart-title'>🏟️ Team Runs</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Bubble size = number of matches played</div>", unsafe_allow_html=True)
        team = filtered_df.groupby("team_batting").agg(total_runs=('total_runs','sum'), matches=('match_id','nunique')).reset_index()
        fig_t = px.scatter(team, x="team_batting", y="total_runs", size="matches",
                           color="team_batting", hover_name="team_batting", size_max=40)
        fig_t.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT,
                            showlegend=False, font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=60,l=20,r=10), height=290,
                            yaxis=dict(showgrid=True, gridcolor=GRID_CLR), xaxis=dict(showgrid=False))
        st.plotly_chart(fig_t, use_container_width=True)

    with r3c2:
        st.markdown("<div class='chart-title'>🍩 Run Distribution</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-sub'>Breakdown of runs scored off the bat</div>", unsafe_allow_html=True)
        run_dist = filtered_df[filtered_df["batter_runs"].isin([1,2,3,4,6])]
        run_counts = run_dist["batter_runs"].value_counts().reset_index()
        run_counts.columns = ["Run Type","Count"]
        run_counts["Run Type"] = run_counts["Run Type"].astype(str) + "s"
        fig_d = px.pie(run_counts, values="Count", names="Run Type", hole=0.65,
                       color_discrete_sequence=px.colors.sequential.Plasma)
        fig_d.update_traces(textposition='inside', textinfo='percent+label')
        fig_d.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT,
                            font=dict(color=TEXT_MAIN),
                            margin=dict(t=5,b=10,l=10,r=10), height=290,
                            legend=dict(font=dict(size=11, color=TEXT_DIM)))
        st.plotly_chart(fig_d, use_container_width=True)

    # =====================================================
    # FULL WIDTH: Runs Per Season
    # =====================================================
    st.markdown("<div class='section-header'>Historical Trend</div>", unsafe_allow_html=True)
    st.markdown(f"""<div class='fullwidth-card'>
        <div class='chart-title'>📈 Total Runs Per Season (All Time)</div>
        <div class='chart-sub'>Historical scoring trend across all IPL seasons</div>
    </div>""", unsafe_allow_html=True)

    rps = df.groupby("season_id")["total_runs"].sum().reset_index()
    fig_trend = px.line(rps, x="season_id", y="total_runs", markers=True)
    fig_trend.update_traces(line_color='#3498DB', marker=dict(color='#3498DB', size=8))
    fig_trend.update_layout(template=PLOTLY_TPL, paper_bgcolor=BG_PLOT, plot_bgcolor=BG_PLOT,
                            font=dict(color=TEXT_MAIN),
                            margin=dict(t=10,b=40,l=40,r=40), height=250,
                            yaxis=dict(showgrid=True, gridcolor=GRID_CLR),
                            xaxis=dict(showgrid=False, type='category'))
    st.plotly_chart(fig_trend, use_container_width=True)
