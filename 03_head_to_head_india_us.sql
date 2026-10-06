-- ============================================================
-- Q3. THE HEAD-TO-HEAD: INDIA vs UNITED STATES
-- The comparison that frames the whole project. Every metric the
-- deck quotes, with its ratio in the last column.
-- ============================================================
WITH metrics AS (
    -- revenue per capita
    SELECT 'Screen revenue per capita (USD)' AS metric, country AS side,
           screen_economy_usd_bn * 1000.0 / population_m AS value
    FROM countries WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'Digital ad spend per capita (USD)', country, digital_ad_per_capita_usd
    FROM countries WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'GDP per capita (USD)', country, gdp_per_capita_usd
    FROM countries WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'Total media time (minutes/day)', country, total_media_min_day
    FROM countries WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'Paid OTT subscriptions (millions)', country, paid_ott_subs_m
    FROM streaming WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'OTT market revenue (USD bn)', country, ott_revenue_usd_bn
    FROM streaming WHERE country IN ('India','United States')

    UNION ALL
    SELECT 'Gaming market (USD bn)', country, revenue_usd_bn
    FROM market_size WHERE format = 'Gaming' AND year = 2025
      AND country IN ('India','United States')
),
pivoted AS (
    SELECT metric,
           MAX(CASE WHEN side = 'India'         THEN value END) AS india,
           MAX(CASE WHEN side = 'United States' THEN value END) AS united_states
    FROM metrics
    GROUP BY metric
)
SELECT
    metric,
    ROUND(india, 2)                                        AS india,
    ROUND(united_states, 2)                                AS united_states,
    ROUND(united_states / NULLIF(india, 0), 1)             AS us_per_india_multiple
FROM pivoted
ORDER BY us_per_india_multiple DESC;
