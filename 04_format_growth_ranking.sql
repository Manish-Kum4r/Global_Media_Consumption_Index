-- ============================================================
-- Q4. WHERE THE MONEY ACTUALLY GREW  (2020 -> 2025)
-- Revenue CAGR by country and format, ranked within each country.
-- Answers: "if I could only own three formats in this market,
-- which three?", and shows how different the answer is by market.
--
-- CAUTION: 2020 is a COVID-depressed base for theatrical, live events and
-- music. Any format showing a very high CAGR off 2020 (e.g. US theatrical at
-- +31%) is partly a recovery, not growth. Read this alongside the 2025 level.
-- ============================================================
WITH growth AS (
    SELECT
        m.country,
        m.format,
        p.revenue_usd_bn                                   AS rev_2020,
        m.revenue_usd_bn                                   AS rev_2025,
        m.revenue_usd_bn - p.revenue_usd_bn                AS rev_delta,
        CASE WHEN p.revenue_usd_bn > 0
             THEN POWER(m.revenue_usd_bn / p.revenue_usd_bn, 1.0 / 5.0) - 1
        END                                                AS cagr_5y,
        m.data_quality
    FROM market_size m
    JOIN market_size p
      ON p.country = m.country
     AND p.format  = m.format
     AND p.year    = 2020
    WHERE m.year = 2025
)
SELECT
    country,
    format,
    ROUND(rev_2020, 2)                                                AS revenue_2020_usd_bn,
    ROUND(rev_2025, 2)                                                AS revenue_2025_usd_bn,
    ROUND(100.0 * cagr_5y, 1)                                         AS cagr_pct,
    RANK() OVER (PARTITION BY country ORDER BY cagr_5y DESC)          AS growth_rank_in_country,
    ROUND(100.0 * rev_2025
          / SUM(rev_2025) OVER (PARTITION BY country), 1)             AS pct_of_country_revenue,
    data_quality
FROM growth
ORDER BY country, growth_rank_in_country;
