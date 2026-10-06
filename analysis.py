#!/usr/bin/env python3
"""
Analysis runner
---------------
Executes every .sql file in ../sql/ against media_consumption.db, prints the
result to the console as a formatted table, and writes it to
../results/<query_name>.csv so the output can be checked without rerunning
the database.

The queries live in .sql files rather than inside this script so they can be
read, reviewed or ported to Postgres/Snowflake without touching Python.

Usage:  python3 analysis.py            # all queries
        python3 analysis.py 01 07      # only queries whose filename starts with these
"""
from __future__ import annotations

import csv
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "media_consumption.db")
SQL_DIR = os.path.join(ROOT, "sql")
OUT_DIR = os.path.join(ROOT, "results")


def format_cell(value, width):
    if value is None:
        text = "-"
    elif isinstance(value, float):
        text = f"{value:,.2f}".rstrip("0").rstrip(".")
    else:
        text = str(value)
    if len(text) > width:
        text = text[: width - 1] + "~"
    return text.rjust(width)


def print_table(columns, rows, max_rows=40) -> None:
    if not rows:
        print("   (no rows)")
        return
    widths = []
    for i, col in enumerate(columns):
        longest = max([len(str(col))] + [len(format_cell(r[i], 999)) for r in rows[:max_rows]])
        widths.append(min(max(longest, 6), 34))

    print("   " + " | ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    print("   " + "-+-".join("-" * w for w in widths))
    for row in rows[:max_rows]:
        print("   " + " | ".join(format_cell(v, w) for v, w in zip(row, widths)))
    if len(rows) > max_rows:
        print(f"   ... {len(rows) - max_rows} more rows (see CSV output)")


def run_query(conn: sqlite3.Connection, path: str) -> tuple[list[str], list[tuple]]:
    with open(path, encoding="utf-8") as fh:
        sql = fh.read()
    cur = conn.execute(sql)
    columns = [d[0] for d in cur.description]
    return columns, cur.fetchall()


def main() -> None:
    if not os.path.exists(DB):
        raise SystemExit("media_consumption.db not found, run etl.py first.")

    wanted = sys.argv[1:]
    os.makedirs(OUT_DIR, exist_ok=True)

    files = sorted(f for f in os.listdir(SQL_DIR)
                   if f.endswith(".sql") and f != "schema.sql"
                   and (not wanted or any(f.startswith(w) for w in wanted)))

    conn = sqlite3.connect(DB)
    try:
        print(f"\nRunning {len(files)} queries against media_consumption.db\n" + "=" * 78)
        for filename in files:
            path = os.path.join(SQL_DIR, filename)
            print(f"\n### {filename.replace('.sql', '').replace('_', ' ').upper()}")
            columns, rows = run_query(conn, path)
            print_table(columns, rows)

            out = os.path.join(OUT_DIR, filename.replace(".sql", ".csv"))
            with open(out, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(columns)
                writer.writerows(rows)
            print(f"   -> results/{os.path.basename(out)}  ({len(rows)} rows)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
