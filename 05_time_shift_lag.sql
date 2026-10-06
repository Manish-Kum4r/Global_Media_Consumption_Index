-- ============================================================
-- Q5. MIGRATION, NOT GROWTH  (2020 -> 2025)
-- What happened to each format's time share inside each market?
-- The finding: total attention is roughly stable; the mix moves.
-- ============================================================
WITH shifted AS (
    SELECT
        a.country,
        a.format,
        a.minutes_per_day                                    AS mins_2020,
        b.minutes_per_day                                    AS mins_2025,
        b.minutes_per_day - a.minutes_per_day                AS delta_mins,
        b.all_sources                                        AS sources,
        b.data_quality
    FROM time_spend a
    JOIN time_spend b
      ON b.country = a.country
     AND b.format  = a.format
     AND b.year    = 2025
    WHERE a.year = 2020
),
totals AS (
    SELECT country,
           SUM(CASE WHEN year = 2020 THEN minutes_per_day END) AS total_2020,
           SUM(CASE WHEN year = 2025 THEN minutes_per_day END) AS total_2025
    FROM time_spend
    GROUP BY country
)
SELECT
    s.country,
    s.format,
    ROUND(s.mins_2020, 0)                                             AS mins_2020,
    ROUND(s.mins_2025, 0)                                             AS mins_2025,
    ROUND(s.delta_mins, 0)                                            AS delta_mins,
    ROUND(100.0 * s.mins_2020 / t.total_2020, 1)                      AS share_2020_pct,
    ROUND(100.0 * s.mins_2025 / t.total_2025, 1)                      AS share_2025_pct,
    ROUND(100.0 * s.mins_2025 / t.total_2025
          - 100.0 * s.mins_2020 / t.total_2020, 1)                    AS share_shift_pp,
    ROUND(100.0 * (t.total_2025 - t.total_2020) / t.total_2020, 1)    AS market_total_time_growth_pct,
    s.data_quality
FROM shifted s
JOIN totals t ON t.country = s.country
ORDER BY s.country, s.delta_mins DESC;
