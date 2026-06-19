"""Google Ads ROI Calculator — Emerald Fortune edition.

Author: Avatar Putra Sigit | linkedin.com/in/avatarputrasigit

A campaign analytics dashboard (CSV-backed) plus the original single-campaign
ROI simulator. Themed with the Emerald Fortune palette, hardened with input
sanitization, validation, rate limiting and graceful error fallbacks.
"""
import os
import sys
import traceback

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import init_db, save_query, get_history, get_dummy_data
from core.security import (
    sanitize_input, validate_numeric, validate_select,
    generate_session_id, mask_api_key, format_rupiah,
)
from core.theme import (
    inject_phase2_emerald_theme, show_loading_skeleton, responsive_css,
    CHART_PALETTE,
)

AVG_ORDER_VALUE = 500_000  # Rp, matches the seeder's ROAS assumption
DATE_OPTIONS = ["All Time", "Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"]
RATE_LIMIT = 10


# ───────────────────────── Legacy ROI logic (preserved) ─────────────────────
def calculate_metrics(budget: float, cpc: float, cr: float, aov: float) -> dict:
    """Calculate Google Ads metrics from inputs."""
    try:
        clicks = int(budget / cpc) if cpc > 0 else 0
        conversions = int(clicks * (cr / 100))
        revenue = conversions * aov
        roas = revenue / budget if budget > 0 else 0.0
        profit = revenue - budget
        return {
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "roas": roas,
            "profit": profit,
            "cpa": budget / conversions if conversions > 0 else 0.0,
        }
    except Exception as e:
        st.error(f"Calculation error: {e}")
        return {"clicks": 0, "conversions": 0, "revenue": 0,
                "roas": 0.0, "profit": 0, "cpa": 0.0}


def scenario_analysis(budget: float, aov: float) -> pd.DataFrame:
    """Generate pessimistic, realistic, and optimistic scenarios."""
    try:
        scenarios = []
        for name, cpc, cr in [
            ("Pessimistic", 3500, 1.5),
            ("Realistic", 2500, 3.0),
            ("Optimistic", 1800, 5.5),
        ]:
            m = calculate_metrics(budget, cpc, cr, aov)
            scenarios.append({
                "Scenario": name,
                "CPC": f"Rp {cpc:,.0f}",
                "Conv. Rate": f"{cr}%",
                "Clicks": m["clicks"],
                "Conversions": m["conversions"],
                "Revenue": f"Rp {m['revenue']:,.0f}",
                "ROAS": f"{m['roas']:.2f}x",
                "Profit": f"Rp {m['profit']:,.0f}",
            })
        return pd.DataFrame(scenarios)
    except Exception as e:
        st.error(f"Scenario analysis error: {e}")
        return pd.DataFrame()


def break_even_data(budget: float, cpc: float, aov: float) -> pd.DataFrame:
    """Generate break-even analysis at different conversion rates."""
    try:
        rates = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
        data = []
        for cr in rates:
            m = calculate_metrics(budget, cpc, cr, aov)
            data.append({
                "Conv Rate": f"{cr}%",
                "Revenue": m["revenue"],
                "Budget": budget,
                "Profit": m["profit"],
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Break-even analysis error: {e}")
        return pd.DataFrame()


def scaling_roadmap(roas: float, target_roas: float, budget: float) -> str:
    """Generate scaling recommendation based on ROAS."""
    try:
        if roas < 1.0:
            return "🔴 STOP: ROAS < 1.0 — Anda rugi. Fix conversion rate atau turunkan CPC dulu."
        elif roas < target_roas:
            return f"🟡 HOLD: ROAS {roas:.2f}x di bawah target {target_roas:.1f}x. Optimasi landing page & audience."
        else:
            scale_pct = int((roas - 1) * 50)
            return f"🟢 SCALE: Naikkan budget {scale_pct}% per minggu. ROAS {roas:.2f}x sudah profitable."
    except Exception as e:
        return f"Scaling roadmap error: {e}"


def monthly_projection(budget: float, cpc: float, cr: float, aov: float,
                       months: int = 12) -> pd.DataFrame:
    """Project revenue growth with 10% monthly budget scaling if profitable."""
    try:
        data = []
        current_budget = budget
        for i in range(1, months + 1):
            m = calculate_metrics(current_budget, cpc, cr, aov)
            data.append({
                "Month": f"Month {i}",
                "Budget": current_budget,
                "Revenue": m["revenue"],
                "Profit": m["profit"],
                "ROAS": round(m["roas"], 2),
            })
            if m["roas"] > 1.5:
                current_budget *= 1.10
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Projection error: {e}")
        return pd.DataFrame()


# ───────────────────────── Data loading ─────────────────────────────────────
@st.cache_data(ttl=3600)
def load_campaigns() -> pd.DataFrame:
    """Load campaigns.csv, seeding it on first run. Cached for 1 hour."""
    df = get_dummy_data("campaigns")
    if df.empty:
        try:
            from data.seeder import seed
            seed(force=True)
            df = get_dummy_data("campaigns")
        except Exception as e:
            print(f"[load_campaigns] seeding failed: {e}")
            traceback.print_exc()
    return df


def filter_campaigns(df: pd.DataFrame, campaigns: list,
                     platforms: list, date_range: str) -> pd.DataFrame:
    """Apply sidebar filters to the campaign DataFrame."""
    out = df.copy()
    if campaigns:
        out = out[out["campaign_name"].isin(campaigns)]
    if platforms:
        out = out[out["platform"].isin(platforms)]
    if date_range and date_range != "All Time":
        out = out[out["date_range"] == date_range]
    return out


# ───────────────────────── KPI cards ────────────────────────────────────────
def render_kpis(df: pd.DataFrame) -> None:
    """Render 4 glassmorphism KPI cards."""
    total_budget = float(df["budget"].sum()) if not df.empty else 0.0
    total_spend = float(df["spend"].sum()) if not df.empty else 0.0
    avg_roas = float(df["roas"].mean()) if not df.empty else 0.0
    total_conv = float(df["conversions"].sum()) if not df.empty else 0.0
    spend_pct = (total_spend / total_budget * 100) if total_budget else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Budget", format_rupiah(total_budget),
              delta=f"{len(df)} campaigns")
    c2.metric("💸 Total Spend", format_rupiah(total_spend),
              delta=f"-{spend_pct:.0f}% of budget", delta_color="inverse")
    c3.metric("🎯 Avg ROAS", f"{avg_roas:.2f}x",
              delta=f"{avg_roas - 1:+.2f} vs break-even")
    c4.metric("👥 Total Conversions", f"{total_conv:,.0f}",
              delta=f"{total_conv / max(len(df),1):.0f} avg/campaign")


# ───────────────────────── Charts (with fallbacks) ──────────────────────────
def chart_roas_bar(df: pd.DataFrame) -> None:
    """Bar chart: ROAS per campaign, gold gradient."""
    try:
        if df.empty:
            st.warning("No data to chart.")
            return
        d = df.sort_values("roas", ascending=False).head(15)
        fig = px.bar(d, x="campaign_name", y="roas",
                     color="roas", color_continuous_scale=["#065f46", "#fbbf24"],
                     labels={"roas": "ROAS", "campaign_name": "Campaign"})
        fig.update_layout(_plotly_layout())
        st.plotly_chart(fig, width="stretch")
    except (ValueError, KeyError) as e:
        print(f"[chart_roas_bar] {e}")
        st.dataframe(df[["campaign_name", "roas"]], width="stretch")


def chart_budget_pie(df: pd.DataFrame) -> None:
    """Pie chart: budget allocation by platform."""
    try:
        if df.empty:
            st.warning("No data to chart.")
            return
        agg = df.groupby("platform", as_index=False)["budget"].sum()
        fig = px.pie(agg, names="platform", values="budget", hole=0.45,
                     color_discrete_sequence=CHART_PALETTE)
        fig.update_layout(_plotly_layout())
        st.plotly_chart(fig, width="stretch")
    except (ValueError, KeyError) as e:
        print(f"[chart_budget_pie] {e}")
        st.dataframe(df.groupby("platform")["budget"].sum(),
                     width="stretch")


def chart_trend_line(df: pd.DataFrame) -> None:
    """Line chart: spend vs conversions over the quarters."""
    try:
        if df.empty:
            st.warning("No data to chart.")
            return
        order = ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"]
        agg = (df.groupby("date_range", as_index=False)
                 .agg(spend=("spend", "sum"), conversions=("conversions", "sum")))
        agg["date_range"] = pd.Categorical(agg["date_range"], categories=order,
                                           ordered=True)
        agg = agg.sort_values("date_range")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=agg["date_range"], y=agg["spend"],
                                 name="Spend", mode="lines+markers",
                                 line=dict(color="#fbbf24", width=3)))
        fig.add_trace(go.Scatter(x=agg["date_range"], y=agg["conversions"],
                                 name="Conversions", mode="lines+markers",
                                 yaxis="y2",
                                 line=dict(color="#34d399", width=3)))
        layout = _plotly_layout()
        layout["yaxis2"] = dict(overlaying="y", side="right",
                                showgrid=False, color="#a7f3d0")
        fig.update_layout(layout)
        st.plotly_chart(fig, width="stretch")
    except (ValueError, KeyError) as e:
        print(f"[chart_trend_line] {e}")
        st.dataframe(df, width="stretch")


def chart_scatter(df: pd.DataFrame) -> None:
    """Scatter: CPC vs CTR, size by conversions, color by platform."""
    try:
        if df.empty:
            st.warning("No data to chart.")
            return
        fig = px.scatter(df, x="cpc", y="ctr", size="conversions",
                         color="platform", hover_name="campaign_name",
                         color_discrete_sequence=CHART_PALETTE,
                         labels={"cpc": "CPC (Rp)", "ctr": "CTR"})
        fig.update_layout(_plotly_layout())
        st.plotly_chart(fig, width="stretch")
    except (ValueError, KeyError) as e:
        print(f"[chart_scatter] {e}")
        st.dataframe(df[["campaign_name", "cpc", "ctr", "conversions"]],
                     width="stretch")


@st.cache_resource
def _plotly_layout() -> dict:
    """Shared dark Emerald layout for plotly charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ecfdf5", family="sans-serif"),
        xaxis=dict(color="#a7f3d0", gridcolor="rgba(251,191,36,0.12)"),
        yaxis=dict(color="#a7f3d0", gridcolor="rgba(251,191,36,0.12)"),
        legend=dict(font=dict(color="#ecfdf5")),
        margin=dict(l=10, r=10, t=30, b=10),
    )


# ───────────────────────── Main app ─────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title="Google Ads ROI Calculator",
                       layout="wide", page_icon="💰")
    inject_phase2_emerald_theme()
    init_db()

    # Session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    if "calc_count" not in st.session_state:
        st.session_state.calc_count = 0

    df = load_campaigns()
    if df.empty:
        st.title("💰 Google Ads ROI Calculator")
        st.error("Data campaign tidak tersedia. Jalankan `python data/seeder.py`.")
        return

    all_campaigns = sorted(df["campaign_name"].unique().tolist())
    all_platforms = sorted(df["platform"].unique().tolist())

    # ───── Sidebar ─────
    with st.sidebar:
        st.header("🎛️ Campaign Filter")
        campaign_filter = st.multiselect(
            "Campaign", all_campaigns, default=all_campaigns[:5])
        platform_filter = st.multiselect(
            "Platform", all_platforms, default=all_platforms)
        date_range = st.selectbox("Period", DATE_OPTIONS)

        analyze = st.button("📊 Analyze ROI", type="primary",
                            width="stretch")

        if analyze:
            try:
                validate_select(date_range, DATE_OPTIONS)
                for p in platform_filter:
                    validate_select(p, all_platforms)
            except ValueError as e:
                st.error(f"Validasi gagal: {e}")
                st.stop()

            st.session_state.calc_count += 1
            if st.session_state.calc_count > RATE_LIMIT:
                st.error(f"Rate limit: maksimum {RATE_LIMIT} kalkulasi per sesi.")
                st.stop()

            skeleton = st.empty()
            with skeleton:
                show_loading_skeleton()
            progress = st.progress(0, text="Analyzing campaigns...")
            status = st.info("⏳ Calculating ROI metrics...")

            filtered = filter_campaigns(df, campaign_filter,
                                        platform_filter, date_range)
            progress.progress(60, text="Aggregating metrics...")

            result = {
                "campaigns": len(filtered),
                "total_budget": float(filtered["budget"].sum()),
                "total_spend": float(filtered["spend"].sum()),
                "avg_roas": float(filtered["roas"].mean()) if not filtered.empty else 0.0,
                "total_conversions": int(filtered["conversions"].sum()),
            }
            progress.progress(100, text="Done")
            skeleton.empty()
            status.success("Analysis complete!")

            save_query(st.session_state.session_id,
                       sanitize_input(str(campaign_filter)),
                       result,
                       platform_filter=sanitize_input(str(platform_filter)),
                       date_range=date_range)
            st.session_state.result = filtered

        st.divider()
        st.header("🕒 Recent Analysis")
        history = get_history(st.session_state.session_id)
        if history:
            for h in history:
                st.caption(f"🕘 {h['created_at']} — {h['date_range']}")
        else:
            st.caption("Belum ada analisis. Klik **Analyze ROI**.")

        st.divider()
        st.caption(f"🔐 Session: `{mask_api_key(st.session_state.session_id + '00000000')}`")
        st.info("💡 Tip: ROAS > 1 = profitable. ROAS > 4 = scale aggressively.")

    # ───── Main ─────
    st.title("💰 Google Ads ROI Calculator")
    st.caption("Analyze campaign performance & optimize budget allocation")

    # Empty-state when nothing selected and no analysis run yet
    if "result" not in st.session_state:
        if not campaign_filter and not analyze:
            st.markdown(
                "<div style='text-align:center;padding:60px 20px;"
                "background:rgba(255,255,255,0.06);border:1px solid "
                "rgba(251,191,36,0.25);border-radius:16px;'>"
                "<div style='font-size:64px;'>📊</div>"
                "<h2>Select campaigns to analyze ROI</h2>"
                "<p style='color:#a7f3d0;'>Pilih campaign di sidebar lalu klik "
                "<b>Analyze ROI</b>.</p></div>",
                unsafe_allow_html=True,
            )
            return
        st.session_state.result = df.head(10)

    result_df = st.session_state.result

    render_kpis(result_df)
    st.divider()

    t1, t2, t3, t4 = st.tabs([
        "📊 ROI Overview", "📈 Performance",
        "💰 Budget Breakdown", "🧮 ROI Simulator",
    ])

    with t1:
        st.subheader("ROAS per Campaign")
        chart_roas_bar(result_df)
        st.subheader("Budget Allocation by Platform")
        chart_budget_pie(result_df)

    with t2:
        st.subheader("Spend vs Conversions Trend")
        chart_trend_line(result_df)
        st.subheader("CPC vs CTR (size = conversions)")
        chart_scatter(result_df)

    with t3:
        st.subheader("Campaign Metrics")
        if result_df.empty:
            st.warning("Tidak ada data untuk ditampilkan.")
        else:
            st.dataframe(result_df, height=400, width="stretch")
            try:
                csv_data = result_df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", csv_data,
                                   "roi_analysis.csv", "text/csv")
            except Exception as e:
                print(f"[download] {e}")
                st.json(result_df.head(20).to_dict(orient="records"))

    with t4:
        st.subheader("Single Campaign ROI Simulator")
        st.caption("Hitung proyeksi ROI dari satu set parameter campaign.")
        sc1, sc2 = st.columns(2)
        with sc1:
            budget = st.number_input("Monthly Budget (Rp)", min_value=100_000,
                                     value=5_000_000, step=500_000)
            cpc = st.number_input("CPC — Cost Per Click (Rp)", min_value=100,
                                  value=2_500, step=100)
            cr = st.number_input("Conversion Rate (%)", min_value=0.1,
                                 max_value=100.0, value=3.0, step=0.1)
        with sc2:
            aov = st.number_input("Average Order Value (Rp)", min_value=0,
                                  value=AVG_ORDER_VALUE, step=50_000)
            target_roas = st.number_input("Target ROAS", min_value=1.0,
                                          value=4.0, step=0.5)

        try:
            validate_numeric(budget, min_val=0)
            validate_numeric(cpc, min_val=0)
        except ValueError as e:
            st.error(f"Input tidak valid: {e}")
            st.stop()

        m = calculate_metrics(budget, cpc, cr, aov)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Clicks", f"{m['clicks']:,}")
        k2.metric("Conversions", f"{m['conversions']:,}")
        k3.metric("Revenue", format_rupiah(m["revenue"]))
        k4.metric("ROAS", f"{m['roas']:.2f}x")

        st.markdown(f"### {scaling_roadmap(m['roas'], target_roas, budget)}")

        st.subheader("Scenario Analysis")
        st.dataframe(scenario_analysis(budget, aov), width="stretch")

        st.subheader("Break-even by Conversion Rate")
        df_be = break_even_data(budget, cpc, aov)
        if not df_be.empty:
            st.bar_chart(df_be.set_index("Conv Rate")[["Revenue", "Budget"]])

        st.subheader("12-Month Projection")
        df_proj = monthly_projection(budget, cpc, cr, aov)
        if not df_proj.empty:
            st.line_chart(df_proj.set_index("Month")[["Revenue", "Budget"]])

    responsive_css()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001 — top-level UI guard
        st.error(f"App error: {e}")
        print(traceback.format_exc())
