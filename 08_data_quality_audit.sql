-- ============================================================
-- Q8. DATA QUALITY AUDIT
-- What proportion of this database is actually reported, versus
-- derived or estimated? Run this before quoting any number.
-- ============================================================
WITH all_cells AS (
    SELECT 'time_spend'       AS table_name, country, data_quality FROM time_spend
    UNION ALL
    SELECT 'market_size',       country, data_quality FROM market_size
    UNION ALL
    SELECT 'offline_physical',  country, data_quality FROM offline_physical
    UNION ALL
    SELECT 'streaming',         country, data_quality FROM streaming
    UNION ALL
    SELECT 'countries',         country, data_quality FROM countries
),
summary AS (
    SELECT table_name,
           COUNT(*)                                                    AS cells,
           SUM(CASE WHEN data_quality = 'Reported'  THEN 1 ELSE 0 END)  AS reported,
           SUM(CASE WHEN data_quality = 'Derived'   THEN 1 ELSE 0 END)  AS derived,
           SUM(CASE WHEN data_quality = 'Estimated' THEN 1 ELSE 0 END)  AS estimated,
           ROUND(100.0 * SUM(CASE WHEN data_quality = 'Reported' THEN 1 ELSE 0 END)
                 / COUNT(*), 1)                                        AS pct_reported,
           0                                                           AS is_total
    FROM all_cells
    GROUP BY table_name

    UNION ALL

    SELECT 'DATABASE TOTAL',
           COUNT(*),
           SUM(CASE WHEN data_quality = 'Reported'  THEN 1 ELSE 0 END),
           SUM(CASE WHEN data_quality = 'Derived'   THEN 1 ELSE 0 END),
           SUM(CASE WHEN data_quality = 'Estimated' THEN 1 ELSE 0 END),
           ROUND(100.0 * SUM(CASE WHEN data_quality = 'Reported' THEN 1 ELSE 0 END)
                 / COUNT(*), 1),
           1
    FROM all_cells
)
SELECT table_name, cells, reported, derived, estimated, pct_reported
FROM summary
ORDER BY is_total, pct_reported DESC;
