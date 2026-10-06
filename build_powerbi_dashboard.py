#!/usr/bin/env python3
"""
Power BI-style dashboard builder
--------------------------------
Generates dashboard/index.html: a single self-contained page that reproduces the
look and behaviour of a published Power BI report (service chrome, filter pane,
page tabs, cross-filtering, hover tooltips).

All figures come from the CSVs in ../results, which are produced by analysis.py
from SQL. Nothing is typed in by hand.

Usage:  python3 build_powerbi_dashboard.py
"""
from __future__ import annotations

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "dashboard", "index.html")
OUT_CLEAN = os.path.join(ROOT, "dashboard", "clean_style.html")


def load(name):
    with open(os.path.join(RES, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def build_data() -> dict:
    countries = [r for r in load("01_monetisation_index.csv")]
    share = load("02_attention_vs_revenue.csv")
    h2h = load("03_head_to_head_india_us.csv")
    growth = load("04_format_growth_ranking.csv")
    shift = load("05_time_shift_lag.csv")
    quad = load("06_double_growth_formats.csv")
    stream = load("07_streaming_yield.csv")
    quality = load("08_data_quality_audit.csv")
    sens = load("09_denominator_sensitivity.csv")

    data = {
        "index": [{
            "country": r["country"],
            "revPc": f(r["revenue_per_capita_usd"]),
            "hours": f(r["attention_hours_year"]),
            "index": f(r["usd_per_1000_hours"]),
            "rank": int(f(r["yield_rank"])),
        } for r in countries],
        "share": [{
            "country": r["country"],
            "attention": f(r["attention_share_of6_pct"]),
            "revenue": f(r["revenue_share_of6_pct"]),
            "divergence": f(r["divergence_pp"]),
        } for r in share],
        "head2head": [{
            "metric": r["metric"],
            "india": f(r["india"]),
            "us": f(r["united_states"]),
            "multiple": f(r["us_per_india_multiple"]),
        } for r in h2h],
        "growth": [{
            "country": r["country"],
            "format": r["format"],
            "rev2020": f(r["revenue_2020_usd_bn"]),
            "rev2025": f(r["revenue_2025_usd_bn"]),
            "cagr": f(r["cagr_pct"]),
            "rank": int(f(r["growth_rank_in_country"])),
            "pctOf": f(r["pct_of_country_revenue"]),
            "quality": r["data_quality"],
        } for r in growth],
        "shift": [{
            "country": r["country"],
            "format": r["format"],
            "m2020": f(r["mins_2020"]),
            "m2025": f(r["mins_2025"]),
            "delta": f(r["delta_mins"]),
            "shiftPp": f(r["share_shift_pp"]),
        } for r in shift],
        "quadrant": [{
            "country": r["country"],
            "format": r["time_format"],
            "timeDelta": f(r["time_delta_mins"]),
            "revDelta": f(r["revenue_delta_usd_bn"]),
            "quadrant": r["quadrant"],
        } for r in quad],
        "streaming": [{
            "country": r["country"],
            "paidSubs": f(r["paid_ott_subs_m"]),
            "subsPer100": f(r["paid_subs_per_100_people"]),
            "ottRev": f(r["ott_revenue_usd_bn"]),
            "arpu": f(r["implied_revenue_per_sub_usd_yr"]),
            "netflix": f(r["netflix_subs_m"]),
        } for r in stream],
        "quality": [{
            "table": r["table_name"],
            "cells": int(f(r["cells"])),
            "reported": int(f(r["reported"])),
            "derived": int(f(r["derived"])),
            "estimated": int(f(r["estimated"])),
            "pctReported": f(r["pct_reported"]),
        } for r in quality],
        "sens": [{
            "country": r["country"],
            "five": f(r["usd_per_1000h_5format"]),
            "all": f(r["usd_per_1000h_allmedia"]),
            "rankA": int(f(r["rank_5format"])),
            "rankB": int(f(r["rank_allmedia"])),
            "stable": r["rank_stability"].strip().lower() == "stable",
        } for r in sens],
    }
    return data


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GMCI - Global Media Consumption Index</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --sev:#252423; --sev2:#3B3A39; --line:#E1DFDD; --line2:#EDEBE9;
  --txt:#252423; --sub:#605E5C; --canvas:#F3F2F1; --card:#fff;
  --theme:#1F6F7A; --navy:#0F2B46; --orange:#D96B2B; --teal:#7FC4C9;
  --pbi-blue:#118DFF;
}
html,body{height:100%}
body{
  font-family:"Segoe UI","Segoe UI Web (West European)",-apple-system,BlinkMacSystemFont,Roboto,"Helvetica Neue",Arial,sans-serif;
  font-size:13px;color:var(--txt);background:#000;overflow:hidden;
}
.app{display:flex;flex-direction:column;height:100vh}

/* ---------- service top bar ---------- */
.svc{height:44px;background:#1B1A19;display:flex;align-items:center;gap:14px;
     padding:0 12px;color:#fff;flex-shrink:0}
.svc .logo{display:flex;align-items:center;gap:8px;font-weight:600;font-size:13.5px}
.svc .glyph{width:18px;height:18px}
.svc .sep{width:1px;height:20px;background:#3B3A39}
.svc .bc{font-size:12.5px;color:#C8C6C4}
.svc .bc b{color:#fff;font-weight:600}
.svc .spacer{flex:1}
.svc .icons{display:flex;gap:16px;align-items:center;color:#D2D0CE;font-size:15px}
.svc .avatar{width:26px;height:26px;border-radius:50%;background:#118DFF;color:#fff;
    display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600}

/* ---------- body ---------- */
.body{flex:1;display:flex;min-height:0;background:#F0F0F0}

/* left rail */
.rail{width:52px;background:#252423;display:flex;flex-direction:column;
      align-items:center;padding-top:10px;gap:4px;flex-shrink:0;color:#C8C6C4}
.rail .r{width:36px;height:36px;display:flex;align-items:center;justify-content:center;
         border-radius:5px;font-size:15px;cursor:pointer}
.rail .r:hover{background:#3B3A39;color:#fff}
.rail .r.on{background:#3B3A39;color:#fff;box-shadow:inset 2px 0 0 #118DFF}
.rail .r svg{width:16px;height:16px;fill:currentColor}

/* content column */
.content{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0}

.canvasrow{flex:1;display:flex;min-height:0}
.canvas{flex:1;background:var(--canvas);overflow:auto;padding:14px 16px 8px;min-width:0}

/* filter pane */
.filters{width:236px;background:#fff;border-left:1px solid var(--line);
         display:flex;flex-direction:column;flex-shrink:0}
.filters .fh{display:flex;justify-content:space-between;align-items:center;
             padding:10px 12px;border-bottom:1px solid var(--line2)}
.filters .fh span{font-size:13.5px;font-weight:600}
.filters .fh .x{color:var(--sub);cursor:pointer;font-size:15px}
.filters .fc{padding:10px 12px;border-bottom:1px solid var(--line2)}
.filters .fct{display:flex;justify-content:space-between;align-items:center;
              font-size:12.5px;font-weight:600;margin-bottom:8px}
.filters .fct .chev{color:var(--sub);font-size:10px}
.fchip{display:flex;justify-content:space-between;align-items:center;
       border:1px solid var(--line);border-radius:3px;padding:5px 8px;
       font-size:12px;margin-bottom:5px;background:#fff;cursor:pointer}
.fchip:hover{border-color:#8A8886}

/* page tabs */
.tabs{height:34px;background:var(--canvas);display:flex;align-items:flex-end;
      gap:2px;padding:0 16px;border-top:1px solid var(--line);flex-shrink:0}
.tab{padding:6px 14px;font-size:12.5px;color:var(--sub);cursor:pointer;
     border-radius:4px 4px 0 0;border-bottom:2px solid transparent;white-space:nowrap}
.tab:hover{background:#E8E8E8}
.tab.on{color:var(--txt);font-weight:600;background:#fff;border-bottom:2px solid var(--navy)}

/* ---------- visuals grid ---------- */
.page{display:none}
.page.on{display:block}
.grid{display:grid;gap:12px;grid-template-columns:repeat(12,1fr)}
.v{grid-column:span 12;background:var(--card);border:1px solid var(--line);
   border-radius:4px;display:flex;flex-direction:column;min-height:0;
   box-shadow:0 1px 2px rgba(0,0,0,.05);position:relative}
.v:hover .dots{opacity:1}
.vh{display:flex;justify-content:space-between;align-items:center;padding:8px 12px 4px}
.vh .t{font-size:12.5px;font-weight:600;color:var(--navy)}
.vh .s{font-size:11px;color:var(--sub);font-weight:400;margin-left:6px}
.dots{opacity:0;color:var(--sub);font-size:13px;letter-spacing:1px;cursor:pointer;transition:opacity .12s}
.vb{padding:4px 10px 12px;flex:1;min-height:0}
.sp2{grid-column:span 2}.sp3{grid-column:span 3}.sp4{grid-column:span 4}
.sp5{grid-column:span 5}.sp6{grid-column:span 6}.sp7{grid-column:span 7}
.sp8{grid-column:span 8}.sp9{grid-column:span 9}.sp12{grid-column:span 12}

/* KPI cards */
.kpi{background:#fff;border:1px solid var(--line);border-radius:4px;padding:12px 14px;
     box-shadow:0 1px 2px rgba(0,0,0,.05);display:flex;flex-direction:column;justify-content:center}
.kpi .lab{font-size:11.5px;color:var(--sub);margin-bottom:6px;line-height:1.3}
.kpi .val{font-size:27px;font-weight:600;color:var(--navy);line-height:1.1;letter-spacing:-.5px}
.kpi .note{font-size:10.5px;color:var(--sub);margin-top:5px;line-height:1.35}
.kpi.accent .val{color:var(--orange)}

/* tables */
table.pbi{width:100%;border-collapse:collapse;font-size:12px}
table.pbi th{text-align:left;font-weight:600;color:var(--sub);font-size:11px;
   text-transform:uppercase;letter-spacing:.3px;padding:6px 8px;
   border-bottom:1px solid var(--line);background:#FAFAFA;white-space:nowrap}
table.pbi td{padding:6px 8px;border-bottom:1px solid var(--line2)}
table.pbi tbody tr:nth-child(even){background:#FCFCFC}
table.pbi tbody tr:hover{background:#F0F6F7}
table.pbi td.n,table.pbi th.n{text-align:right;font-variant-numeric:tabular-nums}
table.pbi td.b{font-weight:600}
.bar{height:9px;border-radius:2px;background:var(--theme);display:inline-block;vertical-align:middle}
.bar.neg{background:#C0504D}
.barwrap{display:flex;align-items:center;gap:8px;justify-content:flex-end}

/* slicer */
.slicers{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.slicer{background:#fff;border:1px solid var(--line);border-radius:4px;
        padding:6px 10px;display:flex;align-items:center;gap:8px;font-size:12px;
        box-shadow:0 1px 2px rgba(0,0,0,.05)}
.slicer .sl{font-weight:600;color:var(--sub);font-size:11px}
.chip{border:1px solid var(--line);border-radius:11px;padding:2px 9px;cursor:pointer;
      font-size:11.5px;user-select:none;background:#fff;white-space:nowrap}
.chip:hover{border-color:#8A8886}
.chip.on{background:var(--navy);border-color:var(--navy);color:#fff;font-weight:600}
.clear{color:var(--theme);cursor:pointer;font-size:11.5px;text-decoration:underline}

/* tooltip */
#tip{position:fixed;pointer-events:none;background:#252423;color:#fff;font-size:11.5px;
     padding:7px 10px;border-radius:3px;opacity:0;transition:opacity .1s;z-index:99;
     line-height:1.5;max-width:260px;box-shadow:0 4px 12px rgba(0,0,0,.3)}
#tip b{color:#fff}
#tip .r{display:flex;justify-content:space-between;gap:14px}
#tip .r span:last-child{font-weight:600}

svg text{font-family:"Segoe UI",-apple-system,BlinkMacSystemFont,Roboto,Arial,sans-serif}
.hint{font-size:11px;color:var(--sub);padding:2px 12px 6px}
.footer{font-size:11px;color:var(--sub);padding:10px 2px 4px;line-height:1.6}
</style>
</head>
<body>
<div class="app">

  <div class="svc">
    <div class="logo">
      <svg class="glyph" viewBox="0 0 24 24"><rect x="2" y="9" width="4" height="12" rx="1" fill="#F2C811"/><rect x="8" y="5" width="4" height="16" rx="1" fill="#F2C811"/><rect x="14" y="2" width="4" height="19" rx="1" fill="#F2C811"/><rect x="20" y="12" width="2" height="9" rx="1" fill="#F2C811"/></svg>
      Power BI
    </div>
    <div class="sep"></div>
    <div class="bc">Media Insights <span style="color:#605E5C">/</span> <b>GMCI &ndash; Global Media Consumption Index</b></div>
    <div class="spacer"></div>
    <div class="icons">
      <span title="Refresh">&#8635;</span><span title="Export">&#8681;</span><span title="Share">&#9755;</span>
      <span title="Comment">&#128172;</span>
    </div>
    <div class="avatar">AN</div>
  </div>

  <div class="body">
    <nav class="rail">
      <div class="r on" title="Report"><svg viewBox="0 0 16 16"><path d="M1 1h6v6H1zM9 1h6v4H9zM9 7h6v8H9zM1 9h6v6H1z"/></svg></div>
      <div class="r" title="Data"><svg viewBox="0 0 16 16"><path d="M8 1c3 0 5 .9 5 2v10c0 1.1-2 2-5 2s-5-.9-5-2V3c0-1.1 2-2 5-2zm0 1.4C5.9 2.4 4.5 3 4.5 3.4S5.9 4.4 8 4.4s3.5-.6 3.5-1S10.1 2.4 8 2.4z"/></svg></div>
      <div class="r" title="Model"><svg viewBox="0 0 16 16"><path d="M8 1l6 3.5v7L8 15l-6-3.5v-7L8 1zm0 1.7L3.7 5 8 7.3 12.3 5 8 2.7z"/></svg></div>
      <div class="r" title="Lineage"><svg viewBox="0 0 16 16"><path d="M3 2h4v4H3zM9 10h4v4H9zM5 6v2h4v2h-1V9H4V6z"/></svg></div>
    </nav>

    <div class="content">
      <div class="canvasrow">
        <div class="canvas" id="canvas">

          <!-- ============ PAGE 1: OVERVIEW ============ -->
          <div class="page on" id="p-overview">
            <div class="slicers">
              <div class="slicer"><span class="sl">Country</span><span id="slicer-country"></span></div>
              <div class="slicer"><span class="sl">Reset</span><span class="clear" onclick="resetAll()">clear all filters</span></div>
            </div>
            <div class="grid">
              <div class="kpi sp3" id="k1"></div>
              <div class="kpi sp3" id="k2"></div>
              <div class="kpi sp3" id="k3"></div>
              <div class="kpi sp3 accent" id="k4"></div>
              <div class="v sp7"><div class="vh"><span class="t">Monetisation index<span class="s">USD of screen revenue per 1,000 hours of attention &middot; 2025</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-index"></div><div class="hint">Click a bar to cross-filter the page.</div></div>
              <div class="v sp5"><div class="vh"><span class="t">Attention vs revenue share<span class="s">share of the six-market total</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-share"></div><div class="hint">&nbsp;</div></div>
              <div class="v sp12"><div class="vh"><span class="t">Monetisation detail<span class="s">revenue per capita, attention and yield, with a second denominator as a robustness check</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-sens"></div></div>
            </div>
            <div class="footer" id="foot1"></div>
          </div>

          <!-- ============ PAGE 2: ATTENTION ============ -->
          <div class="page" id="p-attention">
            <div class="grid">
              <div class="v sp7"><div class="vh"><span class="t">Time spent by format<span class="s">minutes per person per day, 2025</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-time"></div></div>
              <div class="v sp5"><div class="vh"><span class="t">Change in time spent, 2020-2025<span class="s">minutes per person per day</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-shift"></div></div>
              <div class="v sp12"><div class="vh"><span class="t">Time shift matrix<span class="s">share of each market's tracked attention, 2020 vs 2025</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-shiftmatrix"></div></div>
            </div>
            <div class="footer">Time-spent data is measured differently in each market (Ofcom, Nielsen, eMarketer, DataReportal). Direction is reliable; levels are not directly comparable.</div>
          </div>

          <!-- ============ PAGE 3: REVENUE ============ -->
          <div class="page" id="p-revenue">
            <div class="grid">
              <div class="v sp7"><div class="vh"><span class="t">Revenue CAGR by format, 2020-2025<span class="s">ranked within each market</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-growth"></div></div>
              <div class="v sp5"><div class="vh"><span class="t">Double growth quadrant<span class="s">attention and revenue both rising</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-quad"></div></div>
              <div class="v sp12"><div class="vh"><span class="t">Revenue by market and format<span class="s">USD bn, 2025 &middot; colour scale by column</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-matrix"></div></div>
            </div>
            <div class="footer">2020 is a COVID-depressed base for theatrical, live events and music. Part of their five-year CAGR is recovery rather than growth.</div>
          </div>

          <!-- ============ PAGE 4: INDIA ============ -->
          <div class="page" id="p-india">
            <div class="grid">
              <div class="kpi sp3" id="i1"></div>
              <div class="kpi sp3" id="i2"></div>
              <div class="kpi sp3" id="i3"></div>
              <div class="kpi sp3 accent" id="i4"></div>
              <div class="v sp6"><div class="vh"><span class="t">India vs United States<span class="s">multiple on each metric</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-h2h"></div></div>
              <div class="v sp6"><div class="vh"><span class="t">Streaming: scale vs yield<span class="s">paid subscriptions per 100 people vs revenue per subscription</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-stream"></div></div>
              <div class="v sp12"><div class="vh"><span class="t">India: the numbers behind the argument<span class="s">2025 unless stated</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-indiatable"></div></div>
            </div>
            <div class="footer">Sources: FICCI-EY 2026, PwC India E&amp;M Outlook 2026-30, MPA, Redseer, Lumikai, Ormax.</div>
          </div>

          <!-- ============ PAGE 5: DATA QUALITY ============ -->
          <div class="page" id="p-quality">
            <div class="grid">
              <div class="v sp6"><div class="vh"><span class="t">Data quality by table<span class="s">rows by source classification</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-quality"></div></div>
              <div class="v sp6"><div class="vh"><span class="t">How much of this is reported?<span class="s">percentage of rows directly reported</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-quality2"></div></div>
              <div class="v sp12"><div class="vh"><span class="t">Source register<span class="s">20 sources, each row in the model traced to one of these</span></span><span class="dots">&#8943;</span></div><div class="vb" id="v-sources"></div></div>
            </div>
            <div class="footer">Rows are classified Reported (published figure), Derived (computed from a published figure) or Estimated (scaled or inferred).</div>
          </div>

        </div>

        <aside class="filters">
          <div class="fh"><span>Filters</span><span class="x" title="Collapse">&#10005;</span></div>
          <div class="fc">
            <div class="fct"><span>Page level</span><span class="chev">&#9650;</span></div>
            <div id="fp-country"></div>
            <div id="fp-format"></div>
          </div>
          <div class="fc">
            <div class="fct"><span>Data notes</span><span class="chev">&#9660;</span></div>
          </div>
          <div class="fc" style="border-bottom:none">
            <div class="fct"><span>Source</span><span class="chev">&#9660;</span></div>
          </div>
        </aside>
      </div>

      <div class="tabs">
        <div class="tab on" onclick="go('overview',this)">Overview</div>
        <div class="tab" onclick="go('attention',this)">Attention</div>
        <div class="tab" onclick="go('revenue',this)">Revenue &amp; formats</div>
        <div class="tab" onclick="go('india',this)">India</div>
        <div class="tab" onclick="go('quality',this)">Data quality</div>
      </div>
    </div>
  </div>
</div>
<div id="tip"></div>

<script>
const DATA = __DATA__;
const C = {navy:'#0F2B46', teal:'#1F6F7A', orange:'#D96B2B', accent:'#7FC4C9', grey:'#8A8886',
           line:'#E1DFDD', sub:'#605E5C', blue:'#118DFF'};
const FMT_COL = {'TV (linear)':'#0F2B46','Streaming video':'#1F6F7A',
                 'Social & short video':'#D96B2B','Gaming':'#7FC4C9','Music & audio':'#C8C6C4'};
const ALL_COUNTRIES = DATA.index.map(d=>d.country);
let state = {countries: ALL_COUNTRIES.slice(), clicked:null};

/* ---------- helpers ---------- */
const $ = id => document.getElementById(id);
const m = (n,d=0) => n.toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d});
const money = n => '$'+n.toLocaleString(undefined,{minimumFractionDigits:n<1000?2:0,maximumFractionDigits:n<1000?2:0});
const pct = n => (n>=0?'+':'')+n.toFixed(1)+'%';
const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

const tip = $('tip');
function showTip(e,html){ tip.innerHTML=html; tip.style.opacity=1; moveTip(e); }
function moveTip(e){
  const pad=14, w=tip.offsetWidth, h=tip.offsetHeight;
  let x=e.clientX+pad, y=e.clientY+pad;
  if(x+w>innerWidth-8) x=e.clientX-w-pad;
  if(y+h>innerHeight-8) y=e.clientY-h-pad;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}
function hideTip(){ tip.style.opacity=0; }
document.addEventListener('mousemove', e=>{ if(tip.style.opacity==1) moveTip(e); });

const active = () => state.clicked ? [state.clicked] : state.countries;
const inScope = c => active().includes(c);
const scoped = arr => arr.filter(r => inScope(r.country));

function svg(w,h,inner){
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" style="height:auto;display:block" preserveAspectRatio="xMidYMid meet">${inner}</svg>`;
}
function axisText(x,y,t,anchor='middle',size=10.5,color=C.sub,bold=false){
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="${size}" fill="${color}"${bold?' font-weight="600"':''}>${esc(t)}</text>`;
}
function gridLines(x0,x1,yTop,yBot,min,max,steps,fmtf){
  let out='';
  for(let i=0;i<=steps;i++){
    const v = min + (max-min)*i/steps;
    const y = yBot - (yBot-yTop)*i/steps;
    out += `<line x1="${x0}" y1="${y.toFixed(1)}" x2="${x1}" y2="${y.toFixed(1)}" stroke="${C.line}" stroke-width="1" stroke-dasharray="2,3"/>`;
    out += axisText(x0-6, y+3.5, fmtf(v), 'end');
  }
  return out;
}

/* ---------- visual: monetisation index ---------- */
function renderIndex(){
  const rows = DATA.index.slice().sort((a,b)=>b.index-a.index);
  const max = Math.max(...rows.map(r=>r.index));
  const W=430, H=34+rows.length*38, L=104, R=58;
  let s='';
  rows.forEach((r,i)=>{
    const y = 16 + i*38, h=22;
    const w = Math.max(2,(r.index/max)*(W-L-R));
    const dim = !inScope(r.country);
    const col = r.country==='India' ? C.orange : (i===0?C.navy:C.teal);
    s += `<g class="mk" style="cursor:pointer;opacity:${dim?0.25:1}"
        onclick="pick('${r.country}')"
        onmouseover="showTip(event,'<b>${esc(r.country)}</b><div class=\\'r\\'><span>Revenue per capita</span><span>${money(r.revPc)}</span></div><div class=\\'r\\'><span>Attention</span><span>${m(r.hours)} hrs/yr</span></div><div class=\\'r\\'><span>USD per 1,000 hrs</span><span>${money(r.index)}</span></div>')"
        onmouseout="hideTip()">
      ${axisText(L-10, y+h/2+4, r.country, 'end', 11.5, dim?C.sub:C.navy)}
      <rect x="${L}" y="${y}" width="${w.toFixed(1)}" height="${h}" rx="2" fill="${col}"/>
      ${axisText(L+w+9, y+h/2+4, money(r.index), 'start', 11.5, C.navy, true)}
    </g>`;
  });
  $('v-index').innerHTML = svg(W,H,s);
  const us = DATA.index.find(r=>r.country==='United States').index;
  const ind = DATA.index.find(r=>r.country==='India').index;
  $('foot1').innerHTML = `Monetisation index = screen economy per capita divided by annual media hours per person.
     Where a country bar is dimmed it sits outside the current filter selection.
     The United States earns ${(us/ind).toFixed(0)}x what India earns per hour of attention.`;
}

/* ---------- visual: attention vs revenue share ---------- */
function renderShare(){
  const rows = DATA.share.slice().sort((a,b)=>b.revenue-a.revenue);
  const max = Math.max(...rows.map(r=>Math.max(r.attention,r.revenue)));
  const W=390,H=220,L=34,B=44,T=14;
  const ph=H-B-T, n=rows.length, slot=(W-L-12)/n, bw=slot*0.3;
  let s = gridLines(L,W-12,T,T+ph,0,max*1.15,4, v=>v.toFixed(0)+'%');
  rows.forEach((r,i)=>{
    const x = L + i*slot + slot*0.16;
    const dim = !inScope(r.country);
    const ha=(r.attention/(max*1.15))*ph, hr=(r.revenue/(max*1.15))*ph;
    s += `<g opacity="${dim?0.25:1}">
      <rect x="${x.toFixed(1)}" y="${(T+ph-ha).toFixed(1)}" width="${bw.toFixed(1)}" height="${ha.toFixed(1)}" rx="2" fill="${C.accent}"
        onmouseover="showTip(event,'<b>${esc(r.country)}</b><div class=\\'r\\'><span>Attention share</span><span>${r.attention.toFixed(1)}%</span></div>')" onmouseout="hideTip()"/>
      <rect x="${(x+bw+4).toFixed(1)}" y="${(T+ph-hr).toFixed(1)}" width="${bw.toFixed(1)}" height="${hr.toFixed(1)}" rx="2" fill="${C.navy}"
        onmouseover="showTip(event,'<b>${esc(r.country)}</b><div class=\\'r\\'><span>Revenue share</span><span>${r.revenue.toFixed(1)}%</span></div>')" onmouseout="hideTip()"/>
      ${axisText(x+bw, H-B+15, r.country.replace('United ','U.').replace('South ','S.'), 'middle', 9.5)}
    </g>`;
  });
  // legend
  s += `<rect x="${L}" y="${H-14}" width="9" height="9" rx="2" fill="${C.accent}"/>${axisText(L+13,H-6,'Attention','start',10.5)}`;
  s += `<rect x="${L+80}" y="${H-14}" width="9" height="9" rx="2" fill="${C.navy}"/>${axisText(L+93,H-6,'Revenue','start',10.5)}`;
  $('v-share').innerHTML = svg(W,H,s);
}

/* ---------- visual: sensitivity table ---------- */
function renderSens(){
  const rows = DATA.sens.filter(r=>inScope(r.country));
  let h = `<table class="pbi"><thead><tr>
    <th>Market</th><th class="n">USD / 1,000 hrs (5-format)</th><th class="n">USD / 1,000 hrs (all-media)</th>
    <th class="n">Rank A</th><th class="n">Rank B</th><th>Rank stability</th></tr></thead><tbody>`;
  rows.forEach(r=>{
    h += `<tr><td class="b">${esc(r.country)}</td><td class="n">${money(r.five)}</td><td class="n">${money(r.all)}</td>
      <td class="n">${r.rankA}</td><td class="n">${r.rankB}</td>
      <td style="color:${r.stable?'#107C10':'#C0504D'};font-weight:600">${r.stable?'Stable':'Rank moves'}</td></tr>`;
  });
  h += `</tbody></table>`;
  $('v-sens').innerHTML = h;
}

/* ---------- visual: time spent by format ---------- */
function renderTime(){
  const countries = DATA.index.map(r=>r.country).filter(inScope);
  const formats = ['TV (linear)','Streaming video','Social & short video','Gaming','Music & audio'];
  const get = (c,f)=>{const r=DATA.shift.find(x=>x.country===c&&x.format===f); return r?r.m2025:0;};
  const totals = countries.map(c=>formats.reduce((a,f)=>a+get(c,f),0));
  const max = Math.max(...totals,1);
  const W=470,H=270,L=40,B=52,T=16;
  const ph=H-B-T, slot=(W-L-16)/Math.max(countries.length,1), bw=Math.min(slot*0.55,46);
  let s = gridLines(L,W-16,T,T+ph,0,max*1.1,4, v=>v.toFixed(0));
  countries.forEach((c,i)=>{
    const x = L + i*slot + (slot-bw)/2;
    let acc=0;
    formats.forEach(f=>{
      const v=get(c,f); if(!v) return;
      const h=(v/(max*1.1))*ph, y=T+ph-acc-h;
      s += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="${FMT_COL[f]}"
        onmouseover="showTip(event,'<b>${esc(c)}</b><div class=\\'r\\'><span>${esc(f)}</span><span>${v} min/day</span></div>')" onmouseout="hideTip()"/>`;
      acc+=h;
    });
    s += axisText(x+bw/2, T+ph-acc-5, m(totals[i]), 'middle', 10.5, C.navy, true);
    s += axisText(x+bw/2, H-B+15, c.replace('United ','U.').replace('South ','S.'), 'middle', 9.5);
  });
  let lx=L;
  formats.forEach(f=>{ s += `<rect x="${lx}" y="${H-16}" width="9" height="9" rx="2" fill="${FMT_COL[f]}"/>`
    + axisText(lx+13,H-8,f.replace(' & short','/short'),'start',9); lx += f.length*4.6+26; });
  $('v-time').innerHTML = svg(W,H,s);
}

/* ---------- visual: change in time spent ---------- */
function renderShift(){
  const rows = DATA.shift.filter(r=>r.country==='India').sort((a,b)=>b.delta-a.delta);
  const W=370,H=250,L=118,B=34,T=14;
  const ph=H-B-T, maxAbs=Math.max(...rows.map(r=>Math.abs(r.delta)))*1.35;
  const zero = L + (W-L-30)/2;
  const scale = (W-L-30)/2/maxAbs;
  let s = `<line x1="${zero}" y1="${T}" x2="${zero}" y2="${T+ph}" stroke="#B3B0AD"/>`;
  rows.forEach((r,i)=>{
    const y = T + i*(ph/rows.length) + 6, h=(ph/rows.length)-14;
    const w = Math.abs(r.delta)*scale;
    const x = r.delta>0 ? zero : zero-w;
    const col = r.delta>0 ? C.orange : C.navy;
    s += `<g onmouseover="showTip(event,'<b>India - ${esc(r.format)}</b><div class=\\'r\\'><span>2020</span><span>${r.m2020} min/day</span></div><div class=\\'r\\'><span>2025</span><span>${r.m2025} min/day</span></div><div class=\\'r\\'><span>Change</span><span>${r.delta>0?'+':''}${r.delta} min</span></div>')" onmouseout="hideTip()">
      ${axisText(L-10,y+h/2+4,r.format,'end',10.5)}
      <rect x="${x.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="${h}" rx="2" fill="${col}"/>
      ${axisText(r.delta>0?x+w+7:x-7, y+h/2+4, (r.delta>0?'+':'')+r.delta, r.delta>0?'start':'end', 11, col, true)}
    </g>`;
  });
  s += axisText(W/2,H-8,'minutes per person per day, 2020 to 2025','middle',10);
  $('v-shift').innerHTML = svg(W,H,s);
}

/* ---------- visual: shift matrix ---------- */
function renderShiftMatrix(){
  const fmts = ['TV (linear)','Streaming video','Social & short video','Gaming','Music & audio'];
  const countries = DATA.index.map(r=>r.country);
  let h = `<table class="pbi"><thead><tr><th>Market</th>`;
  fmts.forEach(f=>h+=`<th class="n">${esc(f.replace(' & short','/short'))}<br><span style="font-weight:400;text-transform:none">share 2025</span></th>`);
  h += `<th class="n">Total (min/day)</th></tr></thead><tbody>`;
  countries.forEach(c=>{
    if(!inScope(c)) return;
    const rows = fmts.map(f=>DATA.shift.find(x=>x.country===c&&x.format===f)).filter(Boolean);
    const tot = rows.reduce((a,r)=>a+r.m2025,0);
    h += `<tr><td class="b">${esc(c)}</td>`;
    rows.forEach(r=>{
      const sh = (r.m2025/tot*100), shift=r.shiftPp;
      const col = shift>0 ? '#1F6F7A' : '#C0504D';
      h += `<td class="n">${sh.toFixed(1)}%
        <span style="color:${col};font-size:10.5px;font-weight:600">${shift>0?'+':''}${shift.toFixed(1)}pp</span></td>`;
    });
    h += `<td class="n b">${tot.toFixed(0)}</td></tr>`;
  });
  h += `</tbody></table>`;
  $('v-shiftmatrix').innerHTML = h;
}

/* ---------- visual: growth bars ---------- */
function renderGrowth(){
  const countries = DATA.index.map(r=>r.country).filter(inScope);
  let h = `<table class="pbi"><thead><tr><th>Market</th><th>Format</th>
    <th class="n">2020</th><th class="n">2025</th><th style="width:120px" class="n">CAGR</th>
    <th class="n">Share of market</th></tr></thead><tbody>`;
  countries.forEach(c=>{
    const rows = DATA.growth.filter(r=>r.country===c).sort((a,b)=>a.rank-b.rank);
    rows.forEach((r,i)=>{
      const max=25, w=Math.min(Math.abs(r.cagr)/max,1)*86;
      h += `<tr><td class="b">${i===0?esc(c):''}</td><td>${esc(r.format.replace(' (linear)',''))}</td>
        <td class="n">${r.rev2020.toFixed(1)}</td><td class="n">${r.rev2025.toFixed(1)}</td>
        <td class="n"><span class="barwrap"><span class="bar${r.cagr<0?' neg':''}" style="width:${w.toFixed(0)}px"></span>
        <span style="min-width:44px;text-align:right">${r.cagr>=0?'+':''}${r.cagr.toFixed(1)}%</span></span></td>
        <td class="n">${r.pctOf.toFixed(1)}%</td></tr>`;
    });
  });
  h += `</tbody></table>`;
  $('v-growth').innerHTML = h;
}

/* ---------- visual: quadrant scatter ---------- */
function renderQuad(){
  const rows = DATA.quadrant.filter(r=>inScope(r.country));
  const W=370,H=270,L=52,B=44,T=16,R=14;
  const xs = rows.map(r=>r.timeDelta), ys = rows.map(r=>r.revDelta);
  const xmin = Math.min(-10,...xs)-8, xmax = Math.max(...xs)+10;
  const ymin = Math.min(0,...ys)-4, ymax = Math.max(...ys)+10;
  const X = v => L + (v-xmin)/(xmax-xmin)*(W-L-R);
  const Y = v => T + (ymax-v)/(ymax-ymin)*(H-B-T);
  let s='';
  s += `<rect x="${X(0)}" y="${T}" width="${W-R-X(0)}" height="${Y(0)-T}" fill="#EAF4F0"/>`;
  for(let i=0;i<=4;i++){
    const v=ymin+(ymax-ymin)*i/4, y=Y(v);
    s += `<line x1="${L}" y1="${y.toFixed(1)}" x2="${W-R}" y2="${y.toFixed(1)}" stroke="${C.line}" stroke-dasharray="2,3"/>`
       + axisText(L-6,y+3.5,v.toFixed(0),'end');
  }
  s += `<line x1="${L}" y1="${Y(0).toFixed(1)}" x2="${W-R}" y2="${Y(0).toFixed(1)}" stroke="#B3B0AD"/>`;
  s += `<line x1="${X(0).toFixed(1)}" y1="${T}" x2="${X(0).toFixed(1)}" y2="${H-B}" stroke="#B3B0AD"/>`;
  rows.forEach(r=>{
    const isD = r.timeDelta>0 && r.revDelta>0;
    s += `<circle cx="${X(r.timeDelta).toFixed(1)}" cy="${Y(r.revDelta).toFixed(1)}" r="${isD?6:4}"
      fill="${isD?C.orange:C.grey}" stroke="#fff" stroke-width="1.2"
      onmouseover="showTip(event,'<b>${esc(r.country)} - ${esc(r.format)}</b><div class=\\'r\\'><span>Time change</span><span>${r.timeDelta>0?'+':''}${r.timeDelta} min/day</span></div><div class=\\'r\\'><span>Revenue change</span><span>$${r.revDelta.toFixed(2)}bn</span></div><div class=\\'r\\'><span>Classification</span><span>${esc(r.quadrant)}</span></div>')" onmouseout="hideTip()"/>`;
  });
  s += axisText((L+W-R)/2, H-6, 'change in minutes per day, 2020-2025','middle',10);
  s += `<text x="${L-38}" y="${(T+H-B)/2}" font-size="10" fill="${C.sub}" text-anchor="middle" transform="rotate(-90 ${L-38} ${(T+H-B)/2})">change in revenue (USD bn)</text>`;
  s += axisText(W-R-6, T+14, 'DOUBLE GROWTH', 'end', 10, C.orange, true);
  $('v-quad').innerHTML = svg(W,H,s);
}

/* ---------- visual: revenue matrix ---------- */
function renderMatrix(){
  const fmts = ['TV (linear)','OTT video','Digital advertising','Gaming','Recorded music','Live events','Theatrical'];
  const get = (c,fu)=>DATA.growth.find(r=>r.country===c&&r.format===fu);
  const countries = DATA.index.map(r=>r.country).filter(inScope);
  const maxByFmt = {};
  fmts.forEach(fu=>{ maxByFmt[fu]=Math.max(...DATA.index.map(r=>{const g=get(r.country,fu); return g?g.rev2025:0;})); });
  const shade = v => {
    const t = Math.min(v/1,1);
    const r=31+Math.round((255-31)*(1-t)), g=111+Math.round((255-111)*(1-t)), b=122+Math.round((255-122)*(1-t));
    return `rgb(${r},${g},${b})`;
  };
  let h = `<table class="pbi"><thead><tr><th>Market</th>`;
  fmts.forEach(fu=>h+=`<th class="n">${esc(fu.replace(' (linear)',''))}</th>`);
  h += `<th class="n">Total</th></tr></thead><tbody>`;
  countries.forEach(c=>{
    let tot=0;
    let cells='';
    fmts.forEach(fu=>{
      const g=get(c,fu); const v=g?g.rev2025:0; tot+=v;
      const t = maxByFmt[fu]? v/maxByFmt[fu] : 0;
      const bg = shade(t);
      const fg = t>0.55 ? '#fff' : '#252423';
      cells += `<td class="n" style="background:${bg};color:${fg};font-weight:${t>0.55?600:400}">${v.toFixed(1)}</td>`;
    });
    h += `<tr><td class="b">${esc(c)}</td>${cells}<td class="n b">${tot.toFixed(1)}</td></tr>`;
  });
  h += `</tbody></table>`;
  $('v-matrix').innerHTML = h;
}

/* ---------- visual: head to head ---------- */
function renderH2H(){
  const rows = DATA.head2head.slice().sort((a,b)=>a.multiple-b.multiple);
  let h = `<table class="pbi"><thead><tr><th>Metric</th><th class="n">India</th>
    <th class="n">United States</th><th class="n">US / India</th></tr></thead><tbody>`;
  rows.forEach(r=>{
    const hi = r.multiple>50;
    h += `<tr><td>${esc(r.metric)}</td><td class="n">${m(r.india, r.india<100?2:0)}</td>
      <td class="n">${m(r.us, r.us<100?2:0)}</td>
      <td class="n b" style="color:${hi?C.orange:'inherit'}">${r.multiple.toFixed(1)}x</td></tr>`;
  });
  h += `</tbody></table>`;
  $('v-h2h').innerHTML = h;
}

/* ---------- visual: streaming scatter ---------- */
function renderStream(){
  const rows = DATA.streaming.filter(r=>inScope(r.country));
  const W=370,H=250,L=52,B=42,T=18,R=20;
  const xmax = Math.max(...DATA.streaming.map(r=>r.subsPer100))*1.15;
  const ymax = Math.max(...DATA.streaming.map(r=>r.arpu))*1.15;
  const X = v => L + v/xmax*(W-L-R);
  const Y = v => T + (1 - v/ymax)*(H-B-T);
  let s='';
  for(let i=0;i<=4;i++){
    const y = T + (H-B-T)*i/4;
    s += `<line x1="${L}" y1="${y.toFixed(1)}" x2="${W-R}" y2="${y.toFixed(1)}" stroke="${C.line}" stroke-dasharray="2,3"/>`
       + axisText(L-6, y+3.5, (ymax*(1-i/4)).toFixed(0), 'end');
  }
  rows.forEach(r=>{
    const isI = r.country==='India';
    s += `<g opacity="${inScope(r.country)?1:0.25}">
      <circle cx="${X(r.subsPer100).toFixed(1)}" cy="${Y(r.arpu).toFixed(1)}" r="${isI?7:5.5}"
        fill="${isI?C.orange:C.teal}" stroke="#fff" stroke-width="1.3"
        onmouseover="showTip(event,'<b>${esc(r.country)}</b><div class=\\'r\\'><span>Paid subs / 100 people</span><span>${r.subsPer100.toFixed(1)}</span></div><div class=\\'r\\'><span>Revenue per subscription</span><span>${money(r.arpu)}/yr</span></div><div class=\\'r\\'><span>OTT market</span><span>$${r.ottRev.toFixed(1)}bn</span></div>')" onmouseout="hideTip()"/>
      ${axisText(X(r.subsPer100)+ (isI?-9:9), Y(r.arpu)+(isI?16:4), r.country.replace('United ','U.').replace('South ','S.'), isI?'end':'start', 10)}
    </g>`;
  });
  s += axisText((L+W-R)/2, H-8, 'paid OTT subscriptions per 100 people','middle',10);
  s += `<text x="${L-40}" y="${(T+H-B)/2}" font-size="10" fill="${C.sub}" text-anchor="middle" transform="rotate(-90 ${L-40} ${(T+H-B)/2})">revenue per subscription (USD/yr)</text>`;
  $('v-stream').innerHTML = svg(W,H,s);
}

/* ---------- visual: india table ---------- */
function renderIndiaTable(){
  const rows = [
    ['M&E sector revenue 2025', 'INR 2.78 trillion', '+9% YoY', 'FICCI-EY 2026'],
    ['Total advertising', 'INR 1,500 bn', '+13.5%, 0.41% of GDP', 'FICCI-EY 2026'],
    ['Digital advertising', 'INR 947 bn', '63% of all ad spend, +26%', 'FICCI-EY 2026'],
    ['Linear TV advertising', 'INR 263 bn', '\u221210% in 2025', 'FICCI-EY 2026'],
    ['Connected TV advertising', 'INR 99 bn', '+42%, CTV units 40m', 'FICCI-EY 2026'],
    ['Pay TV households', '\u221211 million', 'structural decline', 'FICCI-EY 2026'],
    ['OTT users', '601 million', '216.5m paid subscriptions', 'Ormax / PwC'],
    ['OTT ARPU', '$7.30 / year', 'the number that defines the market', 'PwC India 2026'],
    ['Smartphone screen time', '1.23 trillion hours', '59% of it is entertainment', 'FICCI-EY 2026'],
    ['Screen economy per capita', '$8.4', 'Japan $283, Korea $253, US $889', 'MPA 2026'],
    ['Digital ad spend per capita', '$8', 'US ~$1,000, China ~$120', 'Redseer 2026'],
    ['Gamers', '555 million', 'down from 609m after the RMG ban', 'Lumikai 2026'],
    ['Real-money gaming', 'Banned', 'from 22 Aug 2025', 'Online Gaming Act 2025'],
    ['Filmed entertainment', 'INR 205 bn', 'record year, +14-16% theatrical', 'FICCI-EY 2026'],
    ['Organised live events', '$1.55 bn', '+44% in one year', 'FICCI-EY 2026'],
    ['Paid music subscriptions', '14.4 million', 'against 5.98 trillion streams', 'FICCI-EY 2026'],
  ];
  let h = `<table class="pbi"><thead><tr><th>Metric</th><th>Value</th><th>Context</th><th>Source</th></tr></thead><tbody>`;
  rows.forEach(r=>h+=`<tr><td class="b">${esc(r[0])}</td><td>${esc(r[1])}</td><td style="color:#605E5C">${esc(r[2])}</td><td style="color:#8A8886;font-size:11px">${esc(r[3])}</td></tr>`);
  h += `</tbody></table>`;
  $('v-indiatable').innerHTML = h;
}

/* ---------- visual: quality ---------- */
function renderQuality(){
  const rows = DATA.quality.filter(r=>r.table!=='DATABASE TOTAL');
  const W=390,H=210,L=98,B=34,T=12,R=46;
  const ph=H-B-T, rowH=ph/rows.length;
  let s='';
  rows.forEach((r,i)=>{
    const y=T+i*rowH+5, h=rowH-12;
    const tot=r.cells||1;
    const segs=[['reported',r.reported,'#2E7D5B'],['derived',r.derived,'#D9A441'],['estimated',r.estimated,'#C0504D']];
    let x=L;
    segs.forEach(([k,v,col])=>{
      const w=v/tot*(W-L-R);
      if(w>0) s+=`<rect x="${x.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="${h}" fill="${col}"
        onmouseover="showTip(event,'<b>${esc(r.table)}</b><div class=\\'r\\'><span>${k}</span><span>${v} rows</span></div>')" onmouseout="hideTip()"/>`;
      x+=w;
    });
    s += axisText(L-8, y+h/2+4, r.table, 'end', 10.5);
    s += axisText(W-R+8, y+h/2+4, r.pctReported.toFixed(0)+'%', 'start', 11, C.navy, true);
  });
  s += `<rect x="${L}" y="${H-14}" width="9" height="9" fill="#2E7D5B"/>${axisText(L+13,H-6,'Reported','start',10)}`;
  s += `<rect x="${L+78}" y="${H-14}" width="9" height="9" fill="#D9A441"/>${axisText(L+91,H-6,'Derived','start',10)}`;
  s += `<rect x="${L+156}" y="${H-14}" width="9" height="9" fill="#C0504D"/>${axisText(L+169,H-6,'Estimated','start',10)}`;
  $('v-quality').innerHTML = svg(W,H,s);
}
function renderQuality2(){
  const tot = DATA.quality.find(r=>r.table==='DATABASE TOTAL');
  const cells=[[tot.reported,'Reported','#2E7D5B'],[tot.derived,'Derived','#D9A441'],[tot.estimated,'Estimated','#C0504D']];
  let h = `<table class="pbi"><thead><tr><th>Classification</th><th class="n">Rows</th><th class="n">Share</th><th>Meaning</th></tr></thead><tbody>`;
  const meaning={Reported:'published figure, cited',Derived:'computed from a published figure',Estimated:'scaled or inferred, treat as a range'};
  cells.forEach(([v,k,col])=>{
    h += `<tr><td><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${col};margin-right:7px"></span>${k}</td>
      <td class="n b">${v}</td><td class="n">${(v/tot.cells*100).toFixed(1)}%</td>
      <td style="color:#605E5C">${meaning[k]}</td></tr>`;
  });
  h += `<tr><td class="b">Total</td><td class="n b">${tot.cells}</td><td class="n">100%</td><td></td></tr></tbody></table>`;
  $('v-quality2').innerHTML = h;
}
function renderSources(){
  const rows = [
    ['Ofcom','Media Nations UK 2025 / 2026','UK video time, linear vs on-demand'],
    ['Nielsen','The Gauge (US)','US TV time and streaming share'],
    ['eMarketer','Asia-Pacific Time Spent With Media','Japan and Korea TV time'],
    ['DataReportal','Digital 2025','internet and social time by country'],
    ['Newzoo','Global Games Market Report 2025','gaming revenue by market'],
    ['Niko Partners','India games market','India gaming revenue and ARPU'],
    ['Lumikai','State of India Interactive Media','India gaming post-RMG ban'],
    ['IFPI','Global Music Report 2026','recorded music by market'],
    ['Gower Street / Comscore','worldwide box office 2025','theatrical by territory'],
    ['PwC','Global & India E&M Outlook','OTT, advertising, market size'],
    ['FICCI-EY','India M&E Report 2026','India segment revenue and trends'],
    ['MPA','screen economy by country','per-capita screen revenue'],
    ['Redseer','India advertising','digital ad spend per capita'],
    ['Pollstar','live music 2025','live events revenue'],
    ['Ormax','India OTT audience','OTT users and subscriptions'],
    ['Axis My India','Consumer Sentiment Index','India self-reported media time'],
    ['World Bank','GDP per capita 2025','income benchmarks'],
    ['IBEF','Media & Entertainment India','content and short-form context'],
    ['The Drum','global media consumption','total media hours per person'],
  ];
  let h = `<table class="pbi"><thead><tr><th>Publisher</th><th>Publication</th><th>Used for</th></tr></thead><tbody>`;
  rows.forEach(r=>h+=`<tr><td class="b">${esc(r[0])}</td><td>${esc(r[1])}</td><td style="color:#605E5C">${esc(r[2])}</td></tr>`);
  h += `</tbody></table>`;
  $('v-sources').innerHTML = h;
}

/* ---------- KPI cards ---------- */
function kpi(el,label,value,note,accent){
  const node = $(el);
  node.className = 'kpi sp3' + (accent ? ' accent' : '');
  node.innerHTML = `<div class="lab">${label}</div><div class="val">${value}</div><div class="note">${note}</div>`;
}
function renderKpis(){
  const idx = DATA.index;
  const ind = idx.find(r=>r.country==='India');
  const us = idx.find(r=>r.country==='United States');
  const indS = DATA.streaming.find(r=>r.country==='India');
  kpi('k1','Monetisation index, India', money(ind.index), 'USD of screen revenue per 1,000 hours of attention');
  kpi('k2','Monetisation index, United States', money(us.index), 'the benchmark in this study');
  kpi('k3','Yield gap, US over India', (us.index/ind.index).toFixed(0)+'x', 'against an 11x GDP per capita gap');
  kpi('k4','India OTT revenue per subscription', money(indS.arpu), indS.paidSubs.toFixed(1)+'m paid subscriptions, 3rd largest base globally', true);

  kpi('i1','India screen economy per capita','$8.40','US $889, Japan $283, Korea $253');
  kpi('i2','India paid OTT subscriptions', indS.paidSubs.toFixed(1)+'m','3rd largest paying base in the world');
  kpi('i3','India OTT market',  '$'+indS.ottRev.toFixed(1)+'bn','US OTT video is $113.3bn on a base 1.1x larger');
  kpi('i4','India OTT ARPU', money(indS.arpu)+' / yr','the number that defines the market', true);
}

/* ---------- slicers / cross-filter ---------- */
function renderSlicers(){
  $('slicer-country').innerHTML = ALL_COUNTRIES.map(c=>{
    const on = state.countries.includes(c);
    return `<span class="chip${on?' on':''}" onclick="toggle('${c}')">${c.replace('United States','US').replace('United Kingdom','UK').replace('South Korea','Korea')}</span>`;
  }).join(' ');
  $('fp-country').innerHTML = ALL_COUNTRIES.map(c=>{
    const on = state.countries.includes(c);
    return `<div class="fchip" onclick="toggle('${c}')"><span>${esc(c)}</span><span style="color:#605E5C">${on?'\u2713':''}</span></div>`;
  }).join('');
  $('fp-format').innerHTML = ['TV (linear)','Streaming video','Social & short video','Gaming','Music & audio']
    .map(f=>`<div class="fchip"><span>${esc(f)}</span><span style="color:#605E5C">\u2713</span></div>`).join('');
}
function toggle(c){
  const i = state.countries.indexOf(c);
  if(i>=0){ if(state.countries.length>1) state.countries.splice(i,1); }
  else state.countries.push(c);
  state.clicked = null;
  renderAll();
}
function pick(c){
  state.clicked = (state.clicked===c) ? null : c;
  renderAll();
}
function resetAll(){ state.countries = ALL_COUNTRIES.slice(); state.clicked=null; renderAll(); }

/* ---------- router + render ---------- */
function go(id,el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  $('p-'+id).classList.add('on');
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  el.classList.add('on');
}
function renderAll(){
  renderSlicers();
  renderIndex(); renderShare(); renderSens();
  renderTime(); renderShift(); renderShiftMatrix();
  renderGrowth(); renderQuad(); renderMatrix();
  renderH2H(); renderStream(); renderIndiaTable();
  renderQuality(); renderQuality2(); renderSources();
  renderKpis();
}
renderAll();
</script>
</body>
</html>
"""


def main():
    data = build_data()
    html = HTML.replace("__DATA__", json.dumps(data, separators=(",", ":")))

    # keep the older, plainer dashboard as an alternative
    if os.path.exists(OUT) and not os.path.exists(OUT_CLEAN):
        os.rename(OUT, OUT_CLEAN)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"written {os.path.relpath(OUT, ROOT)}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
