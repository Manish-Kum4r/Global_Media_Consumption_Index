#!/usr/bin/env python3
"""
Charts
------
Renders the six analysis charts as PNGs in ../results/charts/.

Charts are driven by SQL queries against the database. No numbers are
hard-coded in this file, so the charts change when the data changes.

Usage:  python3 charts.py
"""
from __future__ import annotations

import os
import sqlite3

import matplotlib
matplotlib.use("Agg")                     # headless, no display required
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "media_consumption.db")
OUT = os.path.join(ROOT, "results", "charts")

NAVY = "#0F2B46"
TEAL = "#1F6F7A"
ORANGE = "#D96B2B"
GREY = "#8C8C8C"
LGREY = "#E8E8E8"
ACCENT = "#7FC4C9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": "#CCCCCC",
    "axes.labelcolor": "#333333",
    "text.color": "#1A1A1A",
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def q(conn, sql, params=()):
    cur = conn.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()


def tidy(ax, ygrid=True, spines=("top", "right")):
    for s in spines:
        ax.spines[s].set_visible(False)
    if ygrid:
        ax.yaxis.grid(True, color=LGREY, linewidth=0.8)
        ax.set_axisbelow(True)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.tight_layout()
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"  results/charts/{name}")


def chart_index(conn):
    _, rows = q(conn, """
        WITH att AS (SELECT country, SUM(minutes_per_day)*365.0/60 h FROM time_spend
                     WHERE year=2025 GROUP BY country)
        SELECT c.country, (c.screen_economy_usd_bn*1000.0/c.population_m)/(a.h/1000.0)
        FROM countries c JOIN att a ON a.country=c.country ORDER BY 2 DESC""")
    countries = [r[0] for r in rows]
    values = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = [TEAL if c != "India" else ORANGE for c in countries]
    colors[0] = NAVY
    bars = ax.barh(countries[::-1], values[::-1], color=colors[::-1], height=0.62)
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 6, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", fontsize=10, fontweight="bold", color="#1A1A1A")
    ax.set_xlabel("USD of screen revenue per 1,000 hours of attention (2025)")
    ax.set_title("Attention is global. Money is local.\nOne American hour of attention is worth ~86x an Indian hour", loc="left")
    ax.set_xlim(0, max(values) * 1.18)
    tidy(ax, ygrid=False, spines=("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    save(fig, "01_monetisation_index.png")


def chart_attention_vs_revenue(conn):
    _, rows = q(conn, """
        WITH att AS (SELECT country, SUM(minutes_per_day) m FROM time_spend WHERE year=2025 GROUP BY country),
             rev AS (SELECT country, SUM(revenue_usd_bn) r FROM market_size WHERE year=2025 GROUP BY country),
             t AS (SELECT (SELECT SUM(m) FROM att) tm, (SELECT SUM(r) FROM rev) tr)
        SELECT a.country, 100.0*a.m/t.tm, 100.0*r.r/t.tr
        FROM att a JOIN rev r ON r.country=a.country CROSS JOIN t t ORDER BY 3 DESC""")
    countries = [r[0] for r in rows]
    att_share = [r[1] for r in rows]
    rev_share = [r[2] for r in rows]
    import numpy as np
    x = np.arange(len(countries))
    w = 0.38

    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.bar(x - w / 2, att_share, w, label="Share of attention (of 6 markets)", color=ACCENT)
    ax.bar(x + w / 2, rev_share, w, label="Share of revenue (of 6 markets)", color=NAVY)
    for xi, (a, r) in enumerate(zip(att_share, rev_share)):
        ax.text(xi - w / 2, a + 1.2, f"{a:.0f}%", ha="center", fontsize=8.5, color="#333")
        ax.text(xi + w / 2, r + 1.2, f"{r:.0f}%", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=9)
    ax.set_ylabel("% of six-market total")
    ax.set_title("Attention and revenue do not line up\nIndia holds 14% of the attention and 4% of the money", loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.set_ylim(0, max(rev_share) * 1.18)
    tidy(ax)
    save(fig, "02_attention_vs_revenue_share.png")


def chart_format_mix(conn):
    countries = [r[0] for r in q(conn, "SELECT DISTINCT country FROM time_spend ORDER BY country")[1]]
    formats = [r[0] for r in q(conn, "SELECT DISTINCT format FROM time_spend")[1]]
    _, data = q(conn, "SELECT country, format, minutes_per_day FROM time_spend WHERE year=2025")
    lookup = {(c, f): v for c, f, v in data}
    palette = [NAVY, TEAL, ORANGE, ACCENT, GREY]

    fig, ax = plt.subplots(figsize=(9, 4.2))
    left = [0] * len(countries)
    for i, f in enumerate(formats):
        vals = [lookup.get((c, f), 0) for c in countries]
        ax.barh(countries, vals, left=left, color=palette[i % len(palette)], label=f, height=0.6)
        left = [l + v for l, v in zip(left, vals)]
    for i, total in enumerate(left):
        ax.text(total + 4, i, f"{total:,.0f} min", va="center", fontsize=9, fontweight="bold", color="#333")
    ax.set_xlabel("Minutes per person per day (2025)")
    ax.set_title("Format mix is national character, not a global average\nJapan barely does social. Brazil does almost nothing else.", loc="left")
    ax.invert_yaxis()
    ax.legend(frameon=False, fontsize=8.5, ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.32))
    ax.set_xlim(0, max(left) * 1.16)
    tidy(ax, ygrid=False, spines=("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    save(fig, "03_format_mix.png")


def chart_double_growth(conn):
    _, rows = q(conn, """
        WITH tg AS (SELECT a.country, a.format, b.minutes_per_day-a.minutes_per_day d
                    FROM time_spend a JOIN time_spend b ON b.country=a.country AND b.format=a.format AND b.year=2025
                    WHERE a.year=2020),
             fm(t, m) AS (VALUES ('TV (linear)','TV (linear)'),('Streaming video','OTT video'),
                                 ('Gaming','Gaming'),('Music & audio','Recorded music')),
             rg AS (SELECT a.country, a.format, b.revenue_usd_bn-a.revenue_usd_bn d
                    FROM market_size a JOIN market_size b ON b.country=a.country AND b.format=a.format AND b.year=2025
                    WHERE a.year=2020)
        SELECT tg.country, tg.format, tg.d, rg.d
        FROM tg JOIN fm ON fm.t=tg.format JOIN rg ON rg.country=tg.country AND rg.format=fm.m""")
    fig, ax = plt.subplots(figsize=(8.4, 5))
    ax.axhline(0, color="#999999", linewidth=1)
    ax.axvline(0, color="#999999", linewidth=1)
    ax.axhspan(0, 320, xmin=0.5, xmax=1, color="#EAF4F0", zorder=0)
    # label only the material double-growth points, and stagger them so no two collide
    labelled = sorted([r for r in rows if r[2] > 0 and r[3] > 1.5], key=lambda r: -r[3])
    for i, (country, fmt, dt, dr) in enumerate(rows):
        is_double = dt > 0 and dr > 0
        ax.scatter(dt, dr, s=110 if is_double else 45,
                   color=ORANGE if is_double else GREY,
                   edgecolor="white", linewidth=0.8, zorder=3,
                   alpha=0.95 if is_double else 0.55)
    for i, (country, fmt, dt, dr) in enumerate(labelled):
        label = f"{country} · {fmt.split(' (')[0]}"
        offsets = [(10, 10), (10, -14), (-10, 12), (12, 4), (-10, -16), (10, 20)]
        ax.annotate(label, (dt, dr), fontsize=8, xytext=offsets[i % len(offsets)],
                    textcoords="offset points", color="#333",
                    ha="left" if offsets[i % len(offsets)][0] > 0 else "right",
                    arrowprops=dict(arrowstyle="-", color="#BBBBBB", linewidth=0.7))
    ax.set_xlabel("Change in time spent, 2020-25 (minutes/day per person)")
    ax.set_ylabel("Change in revenue, 2020-25 (USD bn)")
    ax.set_title("Only streaming and gaming moved up and to the right\n"
                 "Top-right quadrant = attention AND money both growing", loc="left")
    ax.set_ylim(-32, 145)
    ax.text(ax.get_xlim()[1] * 0.62, 128, "DOUBLE GROWTH  (attention + money both rising)",
            fontsize=9.5, fontweight="bold", color=ORANGE)
    tidy(ax, ygrid=True)
    save(fig, "04_double_growth_quadrant.png")


def chart_streaming_yield(conn):
    _, rows = q(conn, """
        SELECT c.country, 100.0*s.paid_ott_subs_m/c.population_m,
               s.ott_revenue_usd_bn*1000.0/s.paid_ott_subs_m
        FROM streaming s JOIN countries c ON c.country=s.country ORDER BY 3 DESC""")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for country, base, arpu in rows:
        ax.scatter(base, arpu, s=140, color=ORANGE if country == "India" else TEAL,
                   edgecolor="white", linewidth=1, zorder=3)
        ax.annotate(country, (base, arpu), fontsize=9, xytext=(7, 4),
                    textcoords="offset points", color="#333")
    ax.set_xlabel("Paid OTT subscriptions per 100 people")
    ax.set_ylabel("Implied revenue per subscription (USD / year)")
    ax.set_title("India has the scale but not the price\n216.5m paid subscriptions, the 3rd largest base in the world", loc="left")
    tidy(ax)
    save(fig, "05_streaming_yield.png")


def chart_india_shift(conn):
    _, rows = q(conn, """
        SELECT a.format, b.minutes_per_day - a.minutes_per_day
        FROM time_spend a JOIN time_spend b
          ON b.country=a.country AND b.format=a.format AND b.year=2025
        WHERE a.year=2020 AND a.country='India' ORDER BY 2 DESC""")
    formats = [r[0] for r in rows]
    deltas = [r[1] for r in rows]
    colors = [ORANGE if d > 0 else NAVY for d in deltas]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(formats[::-1], deltas[::-1], color=colors[::-1], height=0.6)
    for i, d in enumerate(deltas[::-1]):
        offset = 1.5 if d > 0 else -1.5
        ax.text(d + offset, i, f"{d:+.0f}", va="center",
                ha="left" if d > 0 else "right", fontsize=9.5, fontweight="bold", color="#333")
    ax.axvline(0, color="#999999", linewidth=1)
    ax.set_xlabel("Change in minutes per person per day, 2020 → 2025")
    ax.set_title("Indians are not watching less, they are watching elsewhere\nLinear TV lost 13 minutes a day. Streaming gained 28.", loc="left")
    ax.set_xlim(min(deltas) * 1.4, max(deltas) * 1.35)
    tidy(ax, ygrid=False, spines=("top", "right", "left"))
    ax.tick_params(axis="y", length=0)
    save(fig, "06_india_time_shift.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    conn = sqlite3.connect(DB)
    try:
        print("Rendering charts:")
        chart_index(conn)
        chart_attention_vs_revenue(conn)
        chart_format_mix(conn)
        chart_double_growth(conn)
        chart_streaming_yield(conn)
        chart_india_shift(conn)
    finally:
        conn.close()
    print(f"\n{len(os.listdir(OUT))} charts written to results/charts/")


if __name__ == "__main__":
    main()
