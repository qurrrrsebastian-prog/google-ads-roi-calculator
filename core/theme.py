"""Emerald Fortune theme — CSS injection, loading skeleton, responsive rules.

All colors follow the Emerald Fortune palette:
  bg gradient #022c22 -> #064e3b -> #065f46, gold accent #fbbf24,
  emerald primary #10b981, text #ecfdf5 / #a7f3d0.
"""
from __future__ import annotations

import streamlit as st

_EMERALD_CSS = """
<style>
:root {
  --ef-gold: #fbbf24;
  --ef-gold-hover: #f59e0b;
  --ef-emerald: #10b981;
  --ef-emerald-600: #059669;
  --ef-text: #ecfdf5;
  --ef-text-2: #a7f3d0;
  --ef-card-bg: rgba(255,255,255,0.06);
  --ef-card-border: rgba(251,191,36,0.25);
  --ef-divider: rgba(251,191,36,0.3);
}

/* App background gradient */
.stApp {
  background: linear-gradient(135deg, #022c22 0%, #064e3b 50%, #065f46 100%);
  background-attachment: fixed;
  color: var(--ef-text);
  font-family: sans-serif;
}

/* Headings & text */
h1, h2, h3, h4 { color: var(--ef-text) !important; }
h1 { font-size: 32px !important; font-weight: 700 !important; }
h2 { font-size: 22px !important; font-weight: 600 !important; }
p, label, span, .stMarkdown { color: var(--ef-text); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--ef-text-2) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: rgba(2,44,34,0.85);
  border-right: 1px solid rgba(251,191,36,0.2);
  backdrop-filter: blur(8px);
}
[data-testid="stSidebar"] * { color: var(--ef-text); }
/* Multiselect chips: compact, gold, dark text — readable when many are selected */
[data-testid="stSidebar"] [data-baseweb="tag"] {
  background: var(--ef-gold) !important;
  color: #064e3b !important;
  border-radius: 6px !important;
  font-size: 12px !important;
  max-width: 100% !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #064e3b !important; }
/* Section headers in sidebar get a touch more breathing room */
[data-testid="stSidebar"] h2 { margin-top: 8px; }

/* KPI metric cards — glassmorphism + gold left border */
[data-testid="stMetric"] {
  background: var(--ef-card-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--ef-card-border);
  border-left: 4px solid var(--ef-gold);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: ef-fade-in 0.6s ease both;
  min-height: 132px;            /* equal-height cards */
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}
[data-testid="stMetric"]:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
}
/* KPI value: shrink to fit and wrap so long Rupiah figures are never clipped.
   The inner stMarkdownContainer / <p> is what actually clips, so target it. */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] [data-testid="stMarkdownContainer"],
[data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] p {
  color: var(--ef-text) !important;
  font-size: clamp(16px, 1.4vw, 24px) !important;
  font-weight: 700 !important;
  line-height: 1.2 !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
  margin: 0 !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
  color: var(--ef-text-2) !important;
  font-size: 14px !important;
}
/* delta chip stays compact and on one line */
[data-testid="stMetricDelta"] {
  font-size: 12px !important;
  white-space: nowrap !important;
}

/* Generic containers / dataframes get a glass look */
[data-testid="stDataFrame"] {
  background: var(--ef-card-bg);
  border: 1px solid var(--ef-card-border);
  border-radius: 8px;
  padding: 4px;
}

/* Buttons — primary = gold, secondary = glass */
.stButton > button {
  background: var(--ef-gold);
  color: #064e3b;
  font-weight: 700;
  border: none;
  border-radius: 10px;
  transition: background 0.2s ease, transform 0.1s ease;
}
.stButton > button:hover {
  background: var(--ef-gold-hover);
  color: #064e3b;
  transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.1);
  color: var(--ef-text);
  border: 1px solid rgba(255,255,255,0.2);
}
.stDownloadButton > button {
  background: var(--ef-gold);
  color: #064e3b;
  font-weight: 700;
  border: none;
  border-radius: 10px;
}
.stDownloadButton > button:hover { background: var(--ef-gold-hover); }

/* Tabs — pill style */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
  background: transparent;
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  color: var(--ef-text-2);
  border-radius: 999px;
  padding: 6px 18px;
  border: 1px solid rgba(251,191,36,0.2);
}
.stTabs [aria-selected="true"] {
  background: var(--ef-gold) !important;
  color: #064e3b !important;
  font-weight: 700;
}

/* Dividers */
hr { border-color: var(--ef-divider) !important; }

/* Inputs */
[data-baseweb="input"] input, [data-baseweb="select"] {
  color: var(--ef-text);
}

/* Animations */
@keyframes ef-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes ef-slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.element-container:has(.js-plotly-plot) { animation: ef-slide-up 0.8s ease both; }

@keyframes ef-shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
</style>
"""

_RESPONSIVE_CSS = """
<style>
@media (max-width: 768px) {
  /* KPI 2x2 grid: force metric columns to wrap into halves */
  [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 45% !important;
    min-width: 45% !important;
  }
  h1 { font-size: 24px !important; }
  h2 { font-size: 18px !important; }
  /* Charts full width */
  .js-plotly-plot, .plotly { width: 100% !important; }
  .stTabs [data-baseweb="tab"] { padding: 5px 10px; font-size: 13px; }
}
</style>
"""

_SKELETON_HTML = """
<div style="display:flex;flex-direction:column;gap:12px;margin:8px 0;">
  <div class="ef-skel" style="height:90px;border-radius:16px;"></div>
  <div class="ef-skel" style="height:90px;border-radius:16px;"></div>
  <div class="ef-skel" style="height:90px;border-radius:16px;"></div>
</div>
<style>
.ef-skel {
  background: linear-gradient(90deg,
      rgba(251,191,36,0.10) 25%,
      rgba(251,191,36,0.30) 50%,
      rgba(251,191,36,0.10) 75%);
  background-size: 800px 100%;
  animation: ef-shimmer 1.4s infinite linear;
  border: 1px solid rgba(251,191,36,0.2);
}
@keyframes ef-shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
</style>
"""


def inject_phase2_emerald_theme() -> None:
    """Inject the full Emerald Fortune CSS theme."""
    st.markdown(_EMERALD_CSS, unsafe_allow_html=True)


def show_loading_skeleton() -> None:
    """Render a gold shimmer loading skeleton (3 pulses)."""
    st.markdown(_SKELETON_HTML, unsafe_allow_html=True)


def responsive_css() -> None:
    """Inject mobile (<768px) responsive rules."""
    st.markdown(_RESPONSIVE_CSS, unsafe_allow_html=True)


# Chart palette per Emerald Fortune spec.
CHART_PALETTE = ["#fbbf24", "#34d399", "#10b981", "#6ee7b7", "#a7f3d0"]
