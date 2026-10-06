-- ============================================================
-- Q2. ATTENTION SHARE vs REVENUE SHARE
-- Does a market's share of the world's attention match its share
-- of the world's money? The divergence column is the finding.
-- ============================================================
WITH attention AS (
    SELECT country, SUM(minutes_per_day) AS mins
    FROM time_spend WHERE year = 2025 GROUP BY country
),
revenue AS (
    SELECT country, SUM(revenue_usd_bn) AS rev
    FROM market_size WHERE year = 2025 GROUP BY country
),
totals AS (
    SELECT (SELECT SUM(mins) FROM attention) AS total_mins,
           (SELECT SUM(rev)  FROM revenue)   AS total_rev
)
SELECT
    a.country,
    ROUND(100.0 * a.mins / t.total_mins, 1)                       AS attention_share_of6_pct,
    ROUND(100.0 * r.rev  / t.total_rev,  1)                       AS revenue_share_of6_pct,
    ROUND(100.0 * r.rev / t.total_rev - 100.0 * a.mins / t.total_mins, 1) AS divergence_pp,
    CASE
        WHEN 100.0 * r.rev / t.total_rev - 100.0 * a.mins / t.total_mins >  5 THEN 'Monetises above its attention weight'
        WHEN 100.0 * r.rev / t.total_rev - 100.0 * a.mins / t.total_mins < -5 THEN 'Monetises below its attention weight'
        ELSE 'Broadly matched'
    END                                                            AS verdict
FROM attention a
JOIN revenue r ON r.country = a.country
CROSS JOIN totals t
ORDER BY divergence_pp DESC;
