-- ============================================================
-- Q1. THE MONETISATION INDEX
-- How many USD of screen revenue does one market earn for every
-- 1,000 hours its population spends consuming media?  (2025)
-- This is the headline number of the project.
-- ============================================================
WITH attention AS (
    SELECT country,
           SUM(minutes_per_day) * 365.0 / 60 AS hours_per_year
    FROM time_spend
    WHERE year = 2025
    GROUP BY country
),
revenue AS (
    SELECT country,
           screen_economy_usd_bn * 1000.0 / population_m AS revenue_per_capita_usd
    FROM countries
),
index_calc AS (
    SELECT r.country,
           r.revenue_per_capita_usd,
           a.hours_per_year,
           r.revenue_per_capita_usd / (a.hours_per_year / 1000.0) AS usd_per_1000_hours
    FROM revenue r
    JOIN attention a ON a.country = r.country
)
SELECT
    country,
    ROUND(revenue_per_capita_usd, 2)                                   AS revenue_per_capita_usd,
    ROUND(hours_per_year, 0)                                           AS attention_hours_year,
    ROUND(usd_per_1000_hours, 2)                                       AS usd_per_1000_hours,
    ROUND(100.0 * usd_per_1000_hours
          / (SELECT usd_per_1000_hours FROM index_calc WHERE country = 'United States'), 1) AS index_us_eq_100,
    RANK() OVER (ORDER BY usd_per_1000_hours DESC)                     AS yield_rank
FROM index_calc
ORDER BY usd_per_1000_hours DESC;
