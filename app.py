"""Google Ads ROI Calculator. Author: Avatar Putra Sigit | linkedin.com/in/avatarputrasigit"""
import streamlit as st
import pandas as pd
import numpy as np

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
            "cpa": budget / conversions if conversions > 0 else 0.0
        }
    except Exception as e:
        st.error(f"Calculation error: {e}")
        return {"clicks": 0, "conversions": 0, "revenue": 0, "roas": 0.0, "profit": 0, "cpa": 0.0}

def scenario_analysis(budget: float, aov: float) -> pd.DataFrame:
    """Generate pessimistic, realistic, and optimistic scenarios."""
    try:
        scenarios = []
        for name, cpc, cr in [
            ("Pessimistic", 3500, 1.5),
            ("Realistic", 2500, 3.0),
            ("Optimistic", 1800, 5.5)
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
                "Profit": f"Rp {m['profit']:,.0f}"
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
                "Profit": m["profit"]
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

def monthly_projection(budget: float, cpc: float, cr: float, aov: float, months: int = 12) -> pd.DataFrame:
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
                "ROAS": round(m["roas"], 2)
            })
            if m["roas"] > 1.5:
                current_budget *= 1.10
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Projection error: {e}")
        return pd.DataFrame()

def main() -> None:
    """Main Streamlit app."""
    try:
        st.set_page_config(page_title="Google Ads ROI Calculator", layout="wide")
        st.title("📊 Google Ads ROI Calculator")
        st.markdown("Kalkulator ROI untuk campaign Google Ads — buat marketer & UMKM Indonesia")

        with st.sidebar:
            st.header("⚙️ Input Campaign")
            budget = st.number_input("Monthly Budget (Rp)", min_value=0, value=5_000_000, step=500_000)
            cpc = st.number_input("CPC — Cost Per Click (Rp)", min_value=100, value=2_500, step=100)
            cr = st.number_input("Conversion Rate (%)", min_value=0.1, max_value=100.0, value=3.0, step=0.1)
            aov = st.number_input("Average Order Value (Rp)", min_value=0, value=500_000, step=50_000)
            target_roas = st.number_input("Target ROAS", min_value=1.0, value=4.0, step=0.5)

        metrics = calculate_metrics(budget, cpc, cr, aov)

        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Clicks", f"{metrics['clicks']:,}")
        c2.metric("Conversions", f"{metrics['conversions']:,}")
        c3.metric("Revenue", f"Rp {metrics['revenue']:,.0f}")
        c4.metric("ROAS", f"{metrics['roas']:.2f}x")

        st.markdown("---")

        t1, t2, t3, t4 = st.tabs(["📋 Scenario Analysis", "📈 Break-even Chart", "🚀 Scaling Roadmap", "📅 Monthly Projection"])

        with t1:
            st.subheader("3 Scenario: Pessimistic vs Realistic vs Optimistic")
            df_scenario = scenario_analysis(budget, aov)
            st.dataframe(df_scenario, use_container_width=True)

        with t2:
            st.subheader("Break-even Analysis by Conversion Rate")
            df_be = break_even_data(budget, cpc, aov)
            st.bar_chart(df_be.set_index("Conv Rate")[["Revenue", "Budget"]])

        with t3:
            st.subheader("Rekomendasi Scaling")
            rec = scaling_roadmap(metrics["roas"], target_roas, budget)
            st.markdown(f"### {rec}")
            st.markdown(f"**Break-even ROAS:** 1.0x | **Target ROAS:** {target_roas:.1f}x | **Actual ROAS:** {metrics['roas']:.2f}x")

        with t4:
            st.subheader("12-Month Projection (10% Budget Scaling if Profitable)")
            df_proj = monthly_projection(budget, cpc, cr, aov)
            st.line_chart(df_proj.set_index("Month")[["Revenue", "Budget"]])
            st.dataframe(df_proj, use_container_width=True)

        st.sidebar.markdown("---")
        st.sidebar.info("💡 Tip: ROAS > 1 = profitable. ROAS > 4 = scale aggressively.")
    except Exception as e:
        st.error(f"App error: {e}")

if __name__ == "__main__":
    main()
