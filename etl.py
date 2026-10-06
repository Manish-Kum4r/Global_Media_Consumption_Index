#!/usr/bin/env python3
"""
ETL: CSV -> SQLite
------------------
Loads the six source CSVs in ../data into media_consumption.db, using the
schema in ../sql/schema.sql.

Notes:
  * stdlib only (csv, sqlite3). No pandas needed for a dataset this size.
  * The schema lives in schema.sql rather than in this file, so the database
    definition can be read without reading Python.
  * Foreign keys are enforced, and the load fails loudly instead of writing
    partial rows.

Usage:  python3 etl.py
"""
from __future__ import annotations

import csv
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
SQL = os.path.join(ROOT, "sql")
DB = os.path.join(ROOT, "media_consumption.db")

# csv file -> (table, columns)
TABLES = {
    "sources.csv": ("sources",
                    ["source_id", "name", "publisher", "date", "url", "what_to_pull"]),
    "countries.csv": ("countries",
                      ["country", "region", "population_m", "internet_users_m",
                       "gdp_per_capita_usd", "screen_economy_usd_bn",
                       "digital_ad_per_capita_usd", "total_media_min_day",
                       "data_quality", "source_id", "all_sources"]),
    "time_spend.csv": ("time_spend",
                       ["country", "format", "year", "minutes_per_day",
                        "data_quality", "source_id", "all_sources"]),
    "market_size.csv": ("market_size",
                        ["country", "format", "year", "revenue_usd_bn",
                         "data_quality", "source_id", "all_sources", "definition"]),
    "offline_physical.csv": ("offline_physical",
                             ["country", "metric", "year", "value", "unit",
                              "data_quality", "source_id", "all_sources", "note"]),
    "streaming.csv": ("streaming",
                      ["country", "year", "netflix_subs_m", "paid_ott_subs_m",
                       "ott_revenue_usd_bn", "data_quality", "source_id", "all_sources"]),
}

# load order respects foreign keys: sources and countries first
LOAD_ORDER = ["sources.csv", "countries.csv", "time_spend.csv",
              "market_size.csv", "offline_physical.csv", "streaming.csv"]


def apply_schema(conn: sqlite3.Connection) -> None:
    with open(os.path.join(SQL, "schema.sql"), encoding="utf-8") as fh:
        conn.executescript(fh.read())


def load_table(conn: sqlite3.Connection, filename: str) -> int:
    table, columns = TABLES[filename]
    path = os.path.join(DATA, filename)
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    placeholders = ", ".join("?" for _ in columns)
    statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    payload = [tuple(r[c] if r[c] != "" else None for c in columns) for r in rows]
    conn.executemany(statement, payload)
    return len(payload)


def validate(conn: sqlite3.Connection) -> None:
    """Fail loudly if the database is not safe to analyse."""
    problems: list[str] = []

    # 1. every row must point at a real source
    for table, col in [("time_spend", "source_id"), ("market_size", "source_id"),
                       ("streaming", "source_id"), ("offline_physical", "source_id"),
                       ("countries", "source_id")]:
        orphan = conn.execute(
            f"SELECT COUNT(*) FROM {table} t "
            f"LEFT JOIN sources s ON s.source_id = t.{col} "
            f"WHERE s.source_id IS NULL").fetchone()[0]
        if orphan:
            problems.append(f"{table}: {orphan} rows reference a missing source")

    # 2. both years present for every country/format pair
    for table in ("time_spend", "market_size"):
        gaps = conn.execute(
            f"SELECT COUNT(*) FROM (SELECT country, format FROM {table} "
            f"GROUP BY country, format HAVING COUNT(DISTINCT year) <> 2)").fetchone()[0]
        if gaps:
            problems.append(f"{table}: {gaps} country/format pairs missing a year")

    # 3. no negative times; no nonsensical populations
    bad_time = conn.execute(
        "SELECT COUNT(*) FROM time_spend WHERE minutes_per_day < 0").fetchone()[0]
    if bad_time:
        problems.append(f"time_spend: {bad_time} negative values")
    bad_pop = conn.execute(
        "SELECT COUNT(*) FROM countries WHERE population_m <= 0").fetchone()[0]
    if bad_pop:
        problems.append(f"countries: {bad_pop} invalid populations")

    if problems:
        raise SystemExit("VALIDATION FAILED:\n  - " + "\n  - ".join(problems))


def main() -> None:
    if os.path.exists(DB):
        os.remove(DB)

    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        apply_schema(conn)
        total = 0
        print(f"Loaded into {os.path.relpath(DB, ROOT)}")
        for filename in LOAD_ORDER:
            n = load_table(conn, filename)
            total += n
            print(f"  {TABLES[filename][0]:<18} {n:>4} rows")
        conn.commit()
        validate(conn)
        print(f"  {'TOTAL':<18} {total:>4} rows   (validation passed)")
    except sqlite3.Error as exc:
        conn.rollback()
        print(f"SQL error: {exc}", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
