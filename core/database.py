"""SQLite persistence + CSV data loading for the ROI Calculator.

All queries are parameterized. Errors are logged to console (with traceback)
and surfaced to the caller as gracefully-degraded return values so the UI never
crashes on a DB hiccup.
"""
from __future__ import annotations

import json
import os
import sqlite3
import traceback
from datetime import datetime

import pandas as pd

# Paths are resolved relative to the project root (parent of core/).
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH = os.path.join(_BASE_DIR, "data", "roi.db")
_DATA_DIR = os.path.join(_BASE_DIR, "data")


def _connect() -> sqlite3.Connection:
    """Open a SQLite connection with row access by name."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    """Create the queries table if it does not exist. Returns success bool."""
    try:
        with _connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id      TEXT NOT NULL,
                    campaign_filter TEXT,
                    platform_filter TEXT,
                    date_range      TEXT,
                    result_json     TEXT,
                    created_at      TEXT NOT NULL
                )
                """
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[database.init_db] {e}")
        traceback.print_exc()
        return False


def save_query(session_id: str, campaign_filter: str,
               result: dict, platform_filter: str = "",
               date_range: str = "") -> bool:
    """Insert a query history row. Parameterized to prevent SQL injection."""
    try:
        payload = json.dumps(result, default=str)
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO queries
                    (session_id, campaign_filter, platform_filter,
                     date_range, result_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(session_id),
                    str(campaign_filter)[:500],
                    str(platform_filter)[:500],
                    str(date_range)[:100],
                    payload,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[database.save_query] {e}")
        traceback.print_exc()
        return False


def get_history(session_id: str, limit: int = 5) -> list:
    """Return the last `limit` queries for a session as list of dicts."""
    try:
        with _connect() as conn:
            rows = conn.execute(
                """
                SELECT created_at, campaign_filter, platform_filter, date_range
                FROM queries
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (str(session_id), int(limit)),
            ).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        print(f"[database.get_history] {e}")
        traceback.print_exc()
        return []


def get_dummy_data(table: str = "campaigns") -> pd.DataFrame:
    """Load a CSV-backed dataset from the data/ directory as a DataFrame.

    Returns an empty DataFrame if the file is missing or unreadable.
    """
    csv_path = os.path.join(_DATA_DIR, f"{table}.csv")
    try:
        if not os.path.exists(csv_path):
            print(f"[database.get_dummy_data] missing CSV: {csv_path}")
            return pd.DataFrame()
        return pd.read_csv(csv_path)
    except (pd.errors.EmptyDataError, FileNotFoundError) as e:
        print(f"[database.get_dummy_data] {e}")
        traceback.print_exc()
        return pd.DataFrame()
    except Exception as e:  # noqa: BLE001 — last-resort guard for UI safety
        print(f"[database.get_dummy_data] unexpected: {e}")
        traceback.print_exc()
        return pd.DataFrame()
