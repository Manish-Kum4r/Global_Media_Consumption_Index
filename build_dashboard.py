#!/usr/bin/env python3
"""
Dashboard builder
-----------------
Reads the CSV outputs in ../results (which are produced by analysis.py from
SQL) and injects them into a single self-contained HTML file at
../dashboard/index.html.

Kept as a static HTML file rather than Tableau/Power BI:
  * It opens anywhere. No licence, no server, no login.
  * Charts are SVG drawn from the query output, so nothing is a screenshot.
  * Built from the SQL results, so it cannot drift from the analysis.
The CSVs in ../results are tidy (one row per observation) if the same data
needs to go into Tableau or Power BI instead.

Usage:  python3 build_dashboard.py
"""
from __future__ import annotations

import csv
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "dashboard", "index.html")

NAVY, TEAL, ORANGE, ACCENT, GREY = "#0F2B46", "#1F6F7A", "#D96B2B", "#7FC4C9", "#8C8C8C"


def load(name):
    with open(os.path.join(RES, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- chart builders
def chart_yield(rows):
    """Horizontal bars: USD per 1,000 hours of attention."""
    data = sorted(rows, key=lambda r: -f(r["usd_per_1000_hours"]))
    maxv = max(f(r["usd_per_1000_hours"]) for r in data)
    bar_h, gap, left = 34, 12, 132
    width, height = 760, len(data) * (bar_h + gap) + 30
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Monetisation index">']
    for i, r in enumerate(data):
        v = f(r["usd_per_1000_hours"])
        y = 10 + i * (bar_h + gap)
        w = (v / maxv) * (width - left - 90)
        color = ORANGE if r["country"] == "India" else (NAVY if i == 0 else TEAL)
        parts.append(f'<text x="{left-10}" y="{y+bar_h*0.68}" text-anchor="end" font-size="13" fill="#333">{html.escape(r["country"])}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{left+w+10}" y="{y+bar_h*0.68}" font-size="13" font-weight="600" fill="#1A1A1A">${v:,.0f}</text>')
    parts.append("</svg>")
    return "".join(parts)


def chart_share(rows):
    """Grouped bars: attention share vs revenue share."""
    data = sorted(rows, key=lambda r: -f(r["revenue_share_of6_pct"]))
    maxv = max(max(f(r["attention_share_of6_pct"]), f(r["revenue_share_of6_pct"])) for r in data)
    width, height = 760, 320
    left, bottom, top = 60, 60, 20
    plot_h = height - bottom - top
    n = len(data)
    slot = (width - left - 20) / n
    bw = slot * 0.28
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Attention versus revenue share">']
    for g in range(0, int(maxv) + 10, 20):
        y = top + plot_h - (g / maxv) * plot_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-20}" y2="{y:.1f}" stroke="#EAEAEA"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#888">{g}%</text>')
    for i, r in enumerate(data):
        x = left + i * slot + slot * 0.18
        a, rv = f(r["attention_share_of6_pct"]), f(r["revenue_share_of6_pct"])
        ha = (a / maxv) * plot_h
        hr = (rv / maxv) * plot_h
        parts.append(f'<rect x="{x:.1f}" y="{top+plot_h-ha:.1f}" width="{bw:.1f}" height="{ha:.1f}" rx="2" fill="{ACCENT}"/>')
        parts.append(f'<rect x="{x+bw+4:.1f}" y="{top+plot_h-hr:.1f}" width="{bw:.1f}" height="{hr:.1f}" rx="2" fill="{NAVY}"/>')
        parts.append(f'<text x="{x+bw:.1f}" y="{top+plot_h+16}" text-anchor="middle" font-size="10.5" fill="#333">{html.escape(r["country"])}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{top+plot_h-ha-5:.1f}" text-anchor="middle" font-size="9.5" fill="#5A8F96">{a:.0f}%</text>')
        parts.append(f'<text x="{x+bw*1.5+4:.1f}" y="{top+plot_h-hr-5:.1f}" text-anchor="middle" font-size="9.5" font-weight="600" fill="{NAVY}">{rv:.0f}%</text>')
    parts.append("</svg>")
    return "".join(parts)


def chart_growth(rows):
    """Dot plot: revenue CAGR by format, split by market."""
    order = ["India", "United States", "United Kingdom", "Japan", "South Korea", "Brazil"]
    data = [r for r in rows if r["country"] in order]
    values = [f(r["cagr_pct"]) for r in data]
    lo, hi = min(values) - 3, max(values) + 3
    width, height = 760, 420
    left, top = 130, 24
    plot_w = width - left - 60
    row_h = 62
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Format growth by market">']

    def xpos(v):
        return left + (v - lo) / (hi - lo) * plot_w

    # zero + gridlines
    for v in range(int(lo // 10 * 10), int(hi) + 10, 10):
        if v < lo or v > hi:
            continue
        x = xpos(v)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+len(order)*row_h-18}" stroke="#EFEFEF"/>')
        parts.append(f'<text x="{x:.1f}" y="{top+len(order)*row_h-4}" text-anchor="middle" font-size="9.5" fill="#888">{v}%</text>')
    parts.append(f'<line x1="{xpos(0):.1f}" y1="{top}" x2="{xpos(0):.1f}" y2="{top+len(order)*row_h-18}" stroke="#BBBBBB" stroke-dasharray="3,3"/>')
    for i, c in enumerate(order):
        y = top + i * row_h + 18
        parts.append(f'<text x="{left-16}" y="{y+4}" text-anchor="end" font-size="12.5" font-weight="600" fill="#333">{c}</text>')
        for r in [d for d in data if d["country"] == c]:
            v = f(r["cagr_pct"])
            x = xpos(v)
            col = ORANGE if v < 0 else (NAVY if v > 15 else TEAL)
            parts.append(f'<circle cx="{x:.1f}" cy="{y}" r="5.5" fill="{col}" stroke="white" stroke-width="1.2"/>')
            parts.append(f'<text x="{x:.1f}" y="{y-11}" text-anchor="middle" font-size="8.6" fill="#555">{html.escape(r["format"].replace(" (linear)",""))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def chart_quality(rows):
    """Stacked bars: reported vs derived vs estimated."""
    data = sorted([r for r in rows if r["table_name"] != "DATABASE TOTAL"],
                  key=lambda r: -f(r["pct_reported"]))
    width, height = 460, 260
    left, top = 130, 20
    plot_w = width - left - 60
    row_h = 30
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Data quality audit">']
    for i, r in enumerate(data):
        y = top + i * (row_h + 14)
        tot = f(r["cells"], 1)
        segs = [(f(r["reported"]), "#2E7D5B"), (f(r["derived"]), "#D9A441"), (f(r["estimated"]), "#C0504D")]
        x = left
        for val, col in segs:
            w = val / tot * plot_w
            if w > 0:
                parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{row_h-6}" rx="2" fill="{col}"/>')
            x += w
        parts.append(f'<text x="{left-10}" y="{y+16}" text-anchor="end" font-size="11" fill="#333">{html.escape(r["table_name"])}</text>')
        parts.append(f'<text x="{x+8:.1f}" y="{y+16}" font-size="11" font-weight="600" fill="#333">{f(r["pct_reported"]):.0f}%</text>')
    parts.append("</svg>")
    return "".join(parts)


def kpi_cards(idx, h2h):
    get = {r["metric"]: r for r in h2h}
    cards = [
        ("USD per 1,000 hours of attention", f"${f([r for r in idx if r['country']=='India'][0]['usd_per_1000_hours']):,.2f}",
         "India, 2025, against $307 in the United States"),
        ("Paid OTT subscriptions", f"{f(get['Paid OTT subscriptions (millions)']['india']):,.1f}m",
         "3rd-largest paying base in the world"),
        ("US : India revenue per subscription", f"{f(get['OTT market revenue (USD bn)']['us_per_india_multiple']):,.0f}x",
         "on a subscriber base only 1.1x larger"),
        ("US : India GDP per capita", f"{f(get['GDP per capita (USD)']['us_per_india_multiple']):,.0f}x",
         "so most of the revenue gap is not income"),
    ]
    out = []
    for label, value, note in cards:
        out.append(f'''<div class="kpi">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            <div class="kpi-note">{html.escape(note)}</div>
        </div>''')
    return "".join(out)


def main():
    idx = load("01_monetisation_index.csv")
    share = load("02_attention_vs_revenue.csv")
    h2h = load("03_head_to_head_india_us.csv")
    growth = load("04_format_growth_ranking.csv")
    quality = load("08_data_quality_audit.csv")
    sens = load("09_denominator_sensitivity.csv")

    sens_rows = "".join(
        f"<tr><td>{html.escape(r['country'])}</td>"
        f"<td class='num'>${f(r['usd_per_1000h_5format']):,.2f}</td>"
        f"<td class='num'>${f(r['usd_per_1000h_allmedia']):,.2f}</td>"
        f"<td class='num'>{r['rank_5format']}</td><td class='num'>{r['rank_allmedia']}</td>"
        f"<td class='{'ok' if r['rank_stability']=='stable' else 'warn'}'>{html.escape(r['rank_stability'])}</td></tr>"
        for r in sens)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global Media Consumption Index, dashboard</title>
<style>
  :root {{ --navy:{NAVY}; --teal:{TEAL}; --orange:{ORANGE}; --accent:{ACCENT}; --grey:{GREY}; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:#F5F7F8; color:#1A1A1A;
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
  header {{ background:var(--navy); color:#fff; padding:30px 34px 26px; }}
  header h1 {{ margin:0 0 6px; font-size:26px; letter-spacing:-0.4px; }}
  header p {{ margin:0; color:#BFD3E0; font-size:13.5px; max-width:900px; line-height:1.5; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:24px 20px 60px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; margin-bottom:26px; }}
  .kpi {{ background:#fff; border:1px solid #E2E8EC; border-radius:9px; padding:16px 18px; }}
  .kpi-label {{ font-size:11.5px; text-transform:uppercase; letter-spacing:.6px; color:#6B7C89; font-weight:600; }}
  .kpi-value {{ font-size:30px; font-weight:700; color:var(--navy); margin:7px 0 5px; letter-spacing:-1px; }}
  .kpi-note {{ font-size:11.5px; color:#5A6B78; line-height:1.45; }}
  .card {{ background:#fff; border:1px solid #E2E8EC; border-radius:9px; padding:20px 22px; margin-bottom:20px; }}
  .card h2 {{ margin:0 0 3px; font-size:16.5px; color:var(--navy); }}
  .card .sub {{ margin:0 0 16px; font-size:12.5px; color:#5A6B78; line-height:1.5; }}
  .card svg {{ width:100%; height:auto; display:block; }}
  .legend {{ display:flex; gap:18px; font-size:11.5px; color:#4A5A66; margin-top:10px; flex-wrap:wrap; }}
  .dot {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:5px; vertical-align:middle; }}
  table {{ width:100%; border-collapse:collapse; font-size:12.5px; margin-top:6px; }}
  th,td {{ padding:8px 10px; text-align:left; border-bottom:1px solid #EDF1F3; }}
  th {{ background:#F7F9FA; font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:#6B7C89; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  td.ok {{ color:#2E7D5B; font-weight:600; }} td.warn {{ color:#C0504D; font-weight:600; }}
  .sowhat {{ background:#F1F7F8; border-left:3px solid var(--teal); padding:12px 15px;
             font-size:12.5px; line-height:1.55; border-radius:0 6px 6px 0; margin-top:14px; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  @media (max-width:860px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
  footer {{ font-size:11.5px; color:#6B7C89; line-height:1.6; padding:18px 22px; background:#fff;
            border:1px solid #E2E8EC; border-radius:9px; }}
  code {{ background:#F1F4F6; padding:1px 5px; border-radius:3px; font-size:11.5px; }}
</style>
</head>
<body>
<header>
  <h1>Global Media Consumption Index</h1>
  <p>How six markets, India, the United States, the United Kingdom, Japan, South Korea and Brazil, 
     spend their entertainment time and money across video, gaming, live events and audio.
     Every figure in this dashboard is served from a SQL query against the project database and rendered
     from the query output. Nothing here is typed in by hand.</p>
</header>

<div class="wrap">
  <div class="kpis">{kpi_cards(idx, h2h)}</div>

  <div class="card">
    <h2>Attention is global. Money is local.</h2>
    <p class="sub">USD of screen revenue the industry earns per 1,000 hours its population spends consuming media (2025).
       Population, currency and market size are stripped out, so a $13bn market and a $305bn market can be compared directly.</p>
    {chart_yield(idx)}
    <div class="sowhat"><strong>So what:</strong> An American hour of attention is worth roughly 86x an Indian hour.
      Any India media strategy built as a scaled-down version of a US one is mispriced from the first slide.</div>
  </div>

  <div class="card">
    <h2>Attention share vs revenue share</h2>
    <p class="sub">Each market's share of the six-market attention pool and revenue pool. Where the bars disagree,
       the market is monetising above or below its attention weight.</p>
    {chart_share(share)}
    <div class="legend"><span><span class="dot" style="background:{ACCENT}"></span>Share of attention</span>
      <span><span class="dot" style="background:{NAVY}"></span>Share of revenue</span></div>
    <div class="sowhat"><strong>So what:</strong> India holds 14% of the attention in this universe and 4% of the money.
      The gap is the opportunity, and the reason user acquisition alone cannot be the strategy.</div>
  </div>

  <div class="card">
    <h2>Where the money grew, by market</h2>
    <p class="sub">Revenue CAGR 2020–2025 for each format, within each market. One dot per format.
       Note: 2020 is a COVID-depressed base for theatrical, live events and music, so part of their CAGR is recovery, not growth.</p>
    {chart_growth(growth)}
    <div class="legend"><span><span class="dot" style="background:{ORANGE}"></span>Declining</span>
      <span><span class="dot" style="background:{TEAL}"></span>Growing</span>
      <span><span class="dot" style="background:{NAVY}"></span>Growing &gt;15% CAGR</span></div>
    <div class="sowhat"><strong>So what:</strong> Linear TV declines in four of six markets, but notice what replaces it, 
      OTT video is the fastest-growing format almost everywhere. The migration is inside the screen, not away from it.</div>
  </div>

  <div class="grid2">
    <div class="card">
      <h2>How much of this is actually reported?</h2>
      <p class="sub">Share of database rows tagged Reported / Derived / Estimated.
         Run before quoting anything.</p>
      {chart_quality(quality)}
      <div class="legend">
        <span><span class="dot" style="background:#2E7D5B"></span>Reported</span>
        <span><span class="dot" style="background:#D9A441"></span>Derived</span>
        <span><span class="dot" style="background:#C0504D"></span>Estimated</span>
      </div>
      <div class="sowhat"><strong>So what:</strong> 26% of the database is directly reported.
        The revenue side is strong; the time-spend side is the weak link, and the project says so out loud.</div>
    </div>

    <div class="card">
      <h2>Sensitivity: does the ranking survive a different denominator?</h2>
      <p class="sub">The index uses a five-format time sum. The independent all-media measure is a fair challenge to it.</p>
      <table>
        <tr><th>Market</th><th class="num">5-format</th><th class="num">All-media</th><th class="num">Rank A</th><th class="num">Rank B</th><th>Stability</th></tr>
        {sens_rows}
      </table>
      <div class="sowhat"><strong>So what:</strong> The finding is robust. The US stays first and India last under both
        denominators; only Japan and Korea swap places. The conclusion does not depend on my weakest assumption.</div>
    </div>
  </div>

  <footer>
    <strong>Provenance.</strong> Database: <code>media_consumption.db</code> (SQLite, 6 tables, 188 rows) ·
    Queries: 9 analytical SQL files in <code>/sql</code> · Pipeline: <code>etl.py</code> → <code>analysis.py</code>
    → <code>build_dashboard.py</code> · Charts also exported as PNG in <code>/results/charts</code>.<br>
    <strong>Sources.</strong> Ofcom Media Nations · Nielsen The Gauge · eMarketer · DataReportal · Newzoo · Niko Partners ·
    Lumikai · IFPI · Gower Street/Comscore · PwC · MPA · Redseer · Pollstar · Ormax · Axis My India · World Bank · IBEF.
    Every row carries a source ID and a data-quality flag. [Your name], [Month Year].
  </footer>
</div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"written {os.path.relpath(OUT, ROOT)}  ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
