-- ============================================================
-- Q9. SENSITIVITY: DOES THE CONCLUSION SURVIVE A DIFFERENT
-- DENOMINATOR?
-- The monetisation index uses my five-format time sum. The
-- independent all-media measure (published, broader) is a fair
-- challenge to it. If the ranking holds under both, the finding
-- is robust to the weakest assumption in the project.
-- ============================================================
WITH five_format AS (
    SELECT country, SUM(minutes_per_day) * 365.0 / 60 AS hours_5fmt
    FROM time_spend WHERE year = 2025 GROUP BY country
),
both AS (
    SELECT c.country,
           c.screen_economy_usd_bn * 1000.0 / c.population_m AS rev_pc,
           f.hours_5fmt,
           c.total_media_min_day * 365.0 / 60               AS hours_allmedia
    FROM countries c
    JOIN five_format f ON f.country = c.country
)
SELECT
    country,
    ROUND(rev_pc / (hours_5fmt     / 1000.0), 2)  AS usd_per_1000h_5format,
    ROUND(rev_pc / (hours_allmedia / 1000.0), 2)  AS usd_per_1000h_allmedia,
    RANK() OVER (ORDER BY rev_pc / (hours_5fmt     / 1000.0) DESC) AS rank_5format,
    RANK() OVER (ORDER BY rev_pc / (hours_allmedia / 1000.0) DESC) AS rank_allmedia,
    CASE
        WHEN RANK() OVER (ORDER BY rev_pc / (hours_5fmt     / 1000.0) DESC)
           = RANK() OVER (ORDER BY rev_pc / (hours_allmedia / 1000.0) DESC)
        THEN 'stable' ELSE 'RANK MOVES' END       AS rank_stability
FROM both
ORDER BY rank_5format;
