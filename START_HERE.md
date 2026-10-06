# Global Media Consumption Index, project folder

Analyst application project (Media & Entertainment / TMT). Built over roughly three weeks.

## Start with these three

1. **`Global_Media_Consumption_Index/dashboard/index.html`**, double-click and it opens in any
   browser. No install, no login. This is the fastest way to see the whole project.
2. **`Global_Media_Consumption_Index/Global_Media_Consumption_Index_Deck.pptx`**, 12 slides.
   The write-up of the analysis.
3. **`Global_Media_Consumption_Index/Global_Media_Consumption_Index.xlsx`**, 13 sheets with the
   underlying database, the India deep dive, and a source register.

## The finding

India earns about **$3.56** of screen revenue per 1,000 hours its population spends consuming media.
The US earns about **$306.69**. India has 216.5 million paid OTT subscriptions, the third largest
paying base in the world, but each is worth only **$7.30** a year.

The constraint is price, not audience.

## Folder contents

| Path | What it is |
|---|---|
| `Global_Media_Consumption_Index/data/` | 6 CSVs, 188 rows, one observation per row |
| `Global_Media_Consumption_Index/sql/` | Schema (6 tables) + 9 analytical queries |
| `Global_Media_Consumption_Index/python/` | ETL, query runner, charts, dashboard builder |
| `Global_Media_Consumption_Index/results/` | 9 query outputs (CSV) + 6 charts (PNG) |
| `Global_Media_Consumption_Index/dashboard/` | `index.html` (five-page interactive report) and `clean_style.html` (single-page version) |
| `Global_Media_Consumption_Index/powerbi/` | Power BI theme file, build guide with all DAX measures, and the format bridge table |
| `Global_Media_Consumption_Index/media_consumption.db` | SQLite database, 188 rows |
| `Perspective_Attention_is_Global_Money_is_Local.md` | Article version, for LinkedIn/Medium |
| `my_prep_notes.md` | Personal interview prep. Not part of the deliverable. |
| `extras/` | Second project: India M&E profit-pool model, plus earlier planning notes |

## Running the pipeline

```bash
cd Global_Media_Consumption_Index/python
python3 etl.py              # builds and validates the database
python3 analysis.py         # runs the 9 queries -> console + results/*.csv
python3 charts.py           # renders charts (needs matplotlib)
python3 build_dashboard.py            # rebuilds the single-page dashboard
python3 build_powerbi_dashboard.py    # rebuilds the five-page report
```

Python 3.9+. ETL and analysis are standard library only.

## Still to do before sending this to anyone

- [ ] Replace `[Your name]` and `[Month Year]` in: slide 1 of the deck, `README.md`,
      `Perspective_...md`, and `my_prep_notes.md`
- [ ] Export the deck to PDF as well. Recruiters usually can't open PPTX on a phone.
- [ ] Check the two numbers on slide 4 by hand: $3.56 and $306.69. If I can't reproduce them on a
      calculator, I can't defend them in an interview.
- [ ] Rehearse the walkthrough in `my_prep_notes.md` out loud, three times, timed.
- [ ] Recheck the digital-ad split (global platforms vs Indian media) in the extras folder. It's an
      estimate and it drives a conclusion. Either rebuild it from GroupM/WPP data or state it as a
      range.
- [ ] Decide how to describe the dashboard. The HTML report looks and behaves like a Power BI
      report but was not built in Power BI. If I want to say "built in Power BI", build it, it takes
      about 90 minutes with the guide in `powerbi/`.

## Sources

All 20 sources are listed with dates and URLs in `data/sources.csv` and on sheet 12 of the workbook.
Every row in the database carries a source ID and a data quality flag (Reported / Derived /
Estimated). Nothing in this project is unattributed.
