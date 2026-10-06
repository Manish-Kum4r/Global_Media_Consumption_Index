# Global Media Consumption Index

A cross-market study of how six countries spend their entertainment time and money, and why the
money doesn't sit where the audience does.

Markets: India, the United States, the United Kingdom, Japan, South Korea, Brazil.
Formats tracked: linear TV, streaming video, social and short video, gaming, music and audio.

## The headline

India earns about **$3.56** of screen revenue for every 1,000 hours its population spends consuming
media. The United States earns about **$306.69**. The income gap between the two countries is about
11x, but the revenue-per-hour gap is closer to 86x.

India already has 216.5 million paid OTT subscriptions, the third largest paying base in the world.
Each one is worth $7.30 a year.

## What's in here

```
data/          6 CSVs, 188 rows, one observation per row
sql/           schema.sql plus 9 analytical queries
python/        etl.py, analysis.py, charts.py, build_dashboard.py
results/       9 query outputs (CSV) and 6 charts (PNG)
dashboard/     index.html - five-page interactive report, open in any browser
powerbi/       theme file, DAX build guide, format bridge table
media_consumption.db   SQLite database, built by etl.py
```

Also in the folder: the 13-sheet workbook (`Global_Media_Consumption_Index.xlsx`) and a 12-slide
deck (`Global_Media_Consumption_Index_Deck.pptx`), which are the write-ups of the same analysis.

## Running it

Python 3.9 or above. ETL and analysis use the standard library only.

```bash
cd python
python3 etl.py              # builds media_consumption.db, validates it
python3 analysis.py         # runs the 9 queries, prints them, writes results/*.csv
python3 charts.py           # renders charts to results/charts/*.png  (needs matplotlib)
python3 build_dashboard.py            # writes dashboard/clean_style.html
python3 build_powerbi_dashboard.py    # writes dashboard/index.html
```

`analysis.py` takes a filter if you only want some queries, e.g. `python3 analysis.py 06 09`.

## Method

The index is revenue per hour of attention: screen economy per capita divided by annual media
consumption per person. Dividing by attention makes markets of very different sizes directly
comparable, which is the point of building it.

Three things about how the data is structured:

**Time and money are in separate tables.** They come from different measurement systems (audience
panels on one side, financial reporting on the other) and they can't be added together across
sources. Any join between them is a choice I made, not a default.

**Every row carries a data quality flag and a source ID.** Rows are tagged Reported, Derived or
Estimated. Running `08_data_quality_audit.sql` shows that 25.6% of the database is directly
reported. The revenue side is solid. The time-spend side is the weak part.

**The weakest assumption gets tested.** `09_denominator_sensitivity.sql` re-runs the whole index on
a different denominator (published total media time rather than my five-format sum). The US stays
first and India stays last either way. Japan and South Korea swap places, which is the honest limit
of the finding.

## Where this is weak

- Time-spend figures come from panels that measure different things. Ofcom measures in-home
  viewing on TV sets, Nielsen measures the TV screen, DataReportal is self-reported internet time.
  The direction is reliable, the levels are not.
- The screen economy numerator (MPA) covers TV and online video only. Gaming and publishing are
  outside it. It is applied the same way to all six markets so the comparison holds, but it is not
  total entertainment and media revenue.
- 2020 was a bad base year for cinema, live events and music because of COVID. Their five-year
  CAGRs are partly recovery rather than growth. Noted in `04_format_growth_ranking.sql`.
- Live events revenue outside India and the US is scaled from estimates, not measured.

## The report

`dashboard/index.html` is a five-page report with a service-style chrome, a filter pane, working
country slicers, cross-filtering on click, and hover tooltips. It is hand-built HTML and SVG driven
by the same SQL output as everything else, not a Power BI file.

If the report needs to exist as an actual Power BI workbook, `powerbi/POWERBI_BUILD_GUIDE.md` has the
full build: relationships, every DAX measure written out, a visual-by-visual page spec, and
`theme_GMCI.json` to import so the styling matches. About 90 minutes in Power BI Desktop, which is
free to install.

## Sources

Ofcom Media Nations, Nielsen The Gauge, eMarketer Asia-Pacific, DataReportal Digital 2025, Newzoo,
Niko Partners, Lumikai, IFPI, Gower Street / Comscore, PwC (global and India E&M outlooks), FICCI-EY,
MPA screen economy, Redseer, Pollstar, Ormax, Axis My India, World Bank, IBEF, The Drum.

Dates and URLs for all 20 are in `data/sources.csv` and on sheet 12 of the workbook.
