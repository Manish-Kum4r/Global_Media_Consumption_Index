-- ============================================================
-- Q6. THE DOUBLE-GROWTH QUERY
-- The only formats where BOTH attention and money grew between
-- 2020 and 2025, i.e. where a consumer is spending more time
-- AND more money, which is what an investor actually wants.
-- ============================================================
WITH time_growth AS (
    SELECT a.country, a.format,
           a.minutes_per_day AS mins_2020,
           b.minutes_per_day AS mins_2025,
           b.minutes_per_day - a.minutes_per_day AS time_delta
    FROM time_spend a
    JOIN time_spend b
      ON b.country = a.country AND b.format = a.format AND b.year = 2025
    WHERE a.year = 2020
),
-- map time formats to the closest revenue format so the two can be joined
format_map(fmt_time, fmt_money) AS (
    VALUES
        ('TV (linear)',          'TV (linear)'),
        ('Streaming video',      'OTT video'),
        ('Gaming',               'Gaming'),
        ('Music & audio',        'Recorded music')
),
revenue_growth AS (
    SELECT a.country, a.format,
           a.revenue_usd_bn AS rev_2020,
           b.revenue_usd_bn AS rev_2025,
           b.revenue_usd_bn - a.revenue_usd_bn AS rev_delta
    FROM market_size a
    JOIN market_size b
      ON b.country = a.country AND b.format = a.format AND b.year = 2025
    WHERE a.year = 2020
)
SELECT
    t.country,
    t.format                                   AS time_format,
    r.format                                   AS revenue_format,
    ROUND(t.mins_2020, 0)                      AS mins_2020,
    ROUND(t.mins_2025, 0)                      AS mins_2025,
    ROUND(t.time_delta, 0)                     AS time_delta_mins,
    ROUND(r.rev_2020, 2)                       AS rev_2020_usd_bn,
    ROUND(r.rev_2025, 2)                       AS rev_2025_usd_bn,
    ROUND(r.rev_delta, 2)                      AS revenue_delta_usd_bn,
    CASE
        WHEN t.time_delta > 0 AND r.rev_delta > 0 THEN 'DOUBLE GROWTH'
        WHEN t.time_delta > 0 AND r.rev_delta <= 0 THEN 'attention rising, money falling'
        WHEN t.time_delta <= 0 AND r.rev_delta > 0 THEN 'attention falling, money rising'
        ELSE 'double decline'
    END                                        AS quadrant
FROM time_growth t
JOIN format_map m       ON m.fmt_time = t.format
JOIN revenue_growth r   ON r.country  = t.country AND r.format = m.fmt_money
ORDER BY
    CASE WHEN t.time_delta > 0 AND r.rev_delta > 0 THEN 0 ELSE 1 END,
    t.country, t.format;
