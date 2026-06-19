"""Generate 50 dummy Google Ads campaigns and write data/campaigns.csv.

Run directly:  python data/seeder.py
Imported:      from data.seeder import seed; seed()
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

_DATA_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_DATA_DIR, "campaigns.csv")

PLATFORMS = ["Google Search", "Display", "YouTube", "Shopping"]
QUARTERS = ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"]
AVG_ORDER_VALUE = 500_000  # Rp — used for ROAS revenue estimate

# Themed campaign name fragments for readable dummy data.
_PRODUCTS = ["Sepatu", "Tas", "Kopi", "Gadget", "Fashion", "Skincare",
             "Furnitur", "Mainan", "Buku", "Elektronik", "Herbal", "Kamera"]
_GOALS = ["Promo", "Brand", "Retarget", "Launch", "Sale", "Awareness", "Lead"]


def _build_dataframe(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(50):
        product = _PRODUCTS[rng.integers(0, len(_PRODUCTS))]
        goal = _GOALS[rng.integers(0, len(_GOALS))]
        platform = PLATFORMS[rng.integers(0, len(PLATFORMS))]
        date_range = QUARTERS[rng.integers(0, len(QUARTERS))]

        budget = int(rng.integers(5_000_000, 50_000_001))
        # Spend is between 60% and 100% of budget, capped to the 3jt-45jt range.
        spend = int(np.clip(budget * rng.uniform(0.6, 1.0), 3_000_000, 45_000_000))
        impressions = int(rng.integers(1_000, 50_001))
        clicks = int(min(rng.integers(100, 5_001), impressions))
        conversions = int(min(rng.integers(5, 501), clicks))

        rows.append({
            "campaign_name": f"{product} {goal} #{i + 1:02d}",
            "platform": platform,
            "budget": budget,
            "spend": spend,
            "clicks": clicks,
            "impressions": impressions,
            "conversions": conversions,
            "date_range": date_range,
        })

    df = pd.DataFrame(rows)

    # Derived metrics (guard against divide-by-zero).
    df["ctr"] = (df["clicks"] / df["impressions"]).round(4)
    df["cpc"] = (df["spend"] / df["clicks"].replace(0, np.nan)).round(0)
    df["cpa"] = (df["spend"] / df["conversions"].replace(0, np.nan)).round(0)
    df["roas"] = ((df["conversions"] * AVG_ORDER_VALUE) /
                  df["spend"].replace(0, np.nan)).round(2)
    df["conversion_rate"] = (df["conversions"] / df["clicks"].replace(0, np.nan)).round(4)

    df = df.fillna(0)
    return df


def seed(force: bool = False, path: str = _CSV_PATH) -> str:
    """Write campaigns.csv. If it exists and not force, leave it. Returns path."""
    if os.path.exists(path) and not force:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = _build_dataframe()
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    out = seed(force=True)
    print(f"Seeded 50 campaigns -> {out}")
