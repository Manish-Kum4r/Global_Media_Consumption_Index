# Building GMCI in Power BI Desktop

Power BI Desktop is a free download for Windows. Everything below can be built in about 90 minutes.

The repository already contains the data, the queries and the colour theme. This guide turns them
into a `.pbix` you actually own, so if an interviewer says "open the file", you open a real report.

---

## 0. Before you start

1. Install **Power BI Desktop** (Microsoft Store or powerbi.microsoft.com).
2. In Desktop, go to **File → Options and settings → Options → Preview features** and confirm
   **Power BI Project (.pbip)** is on if you want a text-diffable project folder. Optional.
3. Import the theme first: **View → Themes → Browse for themes** and pick
   `powerbi/theme_GMCI.json`. Every visual you add afterwards inherits the styling, which is why
   the report will look consistent without fighting the format pane.

---

## 1. Load the data

**Home → Get data → Text/CSV**, then import these five files from `data/`:

| File | Becomes | Grain |
|---|---|---|
| `countries.csv` | `countries` | one row per market |
| `time_spend.csv` | `time_spend` | market × format × year |
| `market_size.csv` | `market_size` | market × format × year |
| `streaming.csv` | `streaming` | market × year |
| `offline_physical.csv` | `offline_physical` | market × metric |
| `sources.csv` | `sources` | one row per source |
| `format_map.csv` | `format_map` | bridge: time format to revenue format |

In the preview dialog use **Transform Data** (not Load) so you can set types: `year` as Whole Number,
the money and time columns as Decimal Number, everything else as Text. Then **Close & Apply**.

## 2. Model the relationships

Open the **Model view** and create these. All are one-to-many, single direction.

| From | To | Column |
|---|---|---|
| `countries` | `time_spend` | country |
| `countries` | `market_size` | country |
| `countries` | `streaming` | country |
| `countries` | `offline_physical` | country |
| `sources` | `time_spend` | source_id (inactive) |
| `sources` | `market_size` | source_id (inactive) |
| `format_map` | `market_size` | money_format → format (inactive) |

The source relationships stay inactive by default. Activate them only if you want to trace a
figure back to its source in a drill-through page.

**Create a date table?** Not needed. The model has two discrete years, not a time series, so a
date dimension would add complexity without adding analysis.

## 3. The DAX measures

Create a new table called `_Measures` (Home → Enter Data, one dummy column, then hide it) and put
every measure in there. Keeping measures out of the fact tables makes the field list readable.

```dax
-- Country count in scope, used by card visuals
Countries in scope = DISTINCTCOUNT ( countries[country] )

Revenue 2025 =
CALCULATE ( SUM ( market_size[revenue_usd_bn] ), market_size[year] = 2025 )

Revenue 2020 =
CALCULATE ( SUM ( market_size[revenue_usd_bn] ), market_size[year] = 2020 )

Revenue CAGR 5Y =
VAR R20 = [Revenue 2020]
VAR R25 = [Revenue 2025]
RETURN
    IF ( R20 > 0, DIVIDE ( R25, R20 ) ^ ( 1 / 5 ) - 1 )

Revenue per Capita =
DIVIDE (
    SUM ( countries[screen_economy_usd_bn] ) * 1000,
    SUM ( countries[population_m] )
)

Attention Hours 2025 =
DIVIDE (
    CALCULATE ( SUM ( time_spend[minutes_per_day] ), time_spend[year] = 2025 ) * 365,
    60
)

-- The headline measure
Monetisation Index =
VAR RevPC = [Revenue per Capita]
VAR Hrs   = [Attention Hours 2025]
RETURN
    DIVIDE ( RevPC, DIVIDE ( Hrs, 1000 ) )

-- Indexed so the US = 100
Monetisation Index US = 100 =
VAR Current_ = [Monetisation Index]
VAR US_ =
    CALCULATE (
        [Monetisation Index],
        REMOVEFILTERS ( countries ),
        countries[country] = "United States"
    )
RETURN
    DIVIDE ( Current_, US_ ) * 100

Yield Rank =
RANKX ( ALL ( countries[country] ), [Monetisation Index], , DESC, DENSE )

Attention Share =
VAR Total_ = CALCULATE ( [Attention Hours 2025], REMOVEFILTERS ( countries ) )
RETURN
    DIVIDE ( [Attention Hours 2025], Total_ )

Revenue Share =
VAR Total_ = CALCULATE ( [Revenue 2025], REMOVEFILTERS ( countries ) )
RETURN
    DIVIDE ( [Revenue 2025], Total_ )

Divergence pp = ( [Revenue Share] - [Attention Share] ) * 100

Paid OTT Subscriptions = SUM ( streaming[paid_ott_subs_m] )

Paid Subs per 100 =
DIVIDE ( SUM ( streaming[paid_ott_subs_m] ), SUM ( countries[population_m] ) ) * 100

Implied Revenue per Subscription =
DIVIDE ( SUM ( streaming[ott_revenue_usd_bn] ) * 1000, SUM ( streaming[paid_ott_subs_m] ) )

Time Delta (mins) =
VAR Y25 = CALCULATE ( SUM ( time_spend[minutes_per_day] ), time_spend[year] = 2025 )
VAR Y20 = CALCULATE ( SUM ( time_spend[minutes_per_day] ), time_spend[year] = 2020 )
RETURN
    Y25 - Y20

Revenue Delta =
VAR R25 = [Revenue 2025]
VAR R20 = [Revenue 2020]
RETURN
    R25 - R20

Pct Reported =
DIVIDE (
    CALCULATE ( COUNTROWS ( market_size ), market_size[data_quality] = "Reported" ),
    COUNTROWS ( market_size )
)
```

If you want a measure that reads the labels in the data model rather than hard-coded strings:

```dax
-- requires a small disconnected table made with Enter Data:
--   Class[data_quality] = Reported / Derived / Estimated
Rows by Class =
VAR ThisClass = SELECTEDVALUE ( Class[data_quality] )
RETURN
    CALCULATE (
        COUNTROWS ( 'market_size' ),
        'market_size'[data_quality] = ThisClass
    )
```

## 4. Report pages

Five pages, mirroring the web version in `dashboard/index.html`. Page size: **16:9**.

### Page 1: Overview

| Visual | Type | Fields |
|---|---|---|
| Four KPI cards | Card | `[Monetisation Index]` filtered to India, to US; the ratio as a measure; `[Implied Revenue per Subscription]` |
| Monetisation index | Clustered bar (horizontal) | Axis `countries[country]`, value `[Monetisation Index]`. Conditional colour: India orange, US navy, rest teal |
| Attention vs revenue | Clustered column | Axis `countries[country]`, two series `[Attention Share]` and `[Revenue Share]` |
| Detail table | Table | `countries[country]`, `[Revenue per Capita]`, `[Attention Hours 2025]`, `[Monetisation Index]`, `[Yield Rank]` |
| Country slicer | Slicer (dropdown) | `countries[country]`, multi-select |

Turn on **data labels** for both charts. Format the table's numeric columns to one decimal and
right-align. In Format → Visual → Edit interactions, set the bar chart to **Filter** the other
visuals so clicking a country cross-filters the page, exactly like a published report.

### Page 2: Attention

| Visual | Type | Fields |
|---|---|---|
| Time spent by format | Stacked column | Axis `countries[country]`, legend `time_spend[format]`, value `SUM(minutes_per_day)` with `time_spend[year] = 2025` |
| Change in time spent | Clustered bar | Axis `time_spend[format]`, value `[Time Delta (mins)]`, filter to India |
| Time shift matrix | Matrix | Rows `countries[country]`, columns `time_spend[format]`, values `SUM(minutes_per_day)` filtered to 2025, plus `[Time Delta (mins)]` |

### Page 3: Revenue & formats

| Visual | Type | Fields |
|---|---|---|
| Revenue CAGR by format | Bar chart + data labels, or a Table with **Data bars** on the CAGR column | Axis `market_size[format]`, value `[Revenue CAGR 5Y]`, small multiple by country |
| Double growth quadrant | Scatter | X `[Time Delta (mins)]`, Y `[Revenue Delta]`, details `time_spend[country]`. Import `results/06_double_growth_formats.csv` as a flat table if you want the quadrant label as a legend |
| Revenue matrix | Matrix with conditional formatting | Rows `countries[country]`, columns `market_size[format]`, values `[Revenue 2025]`. Apply a **background colour scale** per column |

### Page 4: India

Cards for the India headline numbers, the India vs US multiple table (`results/03_head_to_head_india_us.csv`
imports cleanly for this one), and the streaming scatter (`[Paid Subs per 100]` against
`[Implied Revenue per Subscription]`).

### Page 5: Data quality

Stacked bar of row counts by `data_quality` per table, the `[Pct Reported]` card, and the source
register table straight from `sources`.

## 5. Finishing touches that make it look native

- **Alt text on every visual.** Format → General → Alt text. Screen-reader text is also what a
  reviewer reads when they inspect the file, so it doubles as documentation. This is a genuine
  accessibility practice, and it is a fair thing to be asked about.
- **Tooltips.** Use the default report-page tooltip on the charts. On the index bar chart, add
  `[Revenue per Capita]` and `[Attention Hours 2025]` to the tooltip well.
- **Edit interactions.** On every page, set the primary chart to filter the rest. That cross-filter
  behaviour is the single most recognisable feature of a Power BI report.
- **Title text.** Use full sentences, not topic labels: "One American hour of attention is worth
  86x an Indian hour", not "Monetisation index".
- **Sync slicers.** View → Sync slicers, then sync the country slicer across all five pages so the
  filter carries through when a reader changes page.

## 6. Publish and export

- **File → Export → Export to PDF** gives a static version for a CV attachment.
- **Publish to web** (Home → Publish) needs a work or school account and is public, so only use it
  if you are comfortable with that. Otherwise keep the `.pbix` local and share screenshots.
- Save the file as `GMCI_Media_Consumption_Index.pbix` and drop it in this folder so the repository
  contains both the source data and the built report.

## 7. Why this is worth the 90 minutes

The repository already had the analysis. Rebuilding it in Power BI proves three things to a
reviewer that a static file cannot: that you can model data (relationships, a proper measure
table), that you write DAX rather than pasting numbers, and that you finish work to a standard
somebody else can open. For a role that lists Excel, PowerPoint and analytical tools, that is the
part of the story the workbook does not tell.
