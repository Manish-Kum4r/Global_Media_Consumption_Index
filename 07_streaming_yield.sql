-- ============================================================
-- Q7. STREAMING YIELD
-- Who has the paying base, and who has the price?
-- India has the 3rd-largest subscription base in the world and
-- one of the smallest revenue pools per subscriber.
--
-- NOTE ON TWO ARPU DEFINITIONS, read before quoting:
--   * PwC publishes India OTT ARPU at USD 7.3 per subscription per year.
--   * This query computes an IMPLIED number (~USD 10) by dividing total
--     OTT video revenue by paid subscriptions.
--   They differ because the revenue numerator and the subscription universe
--   are defined differently (AVOD vs SVOD, bundled vs direct). Both are
--   defensible; what matters is stating which definition you are using.
-- ============================================================
SELECT
    s.country,
    ROUND(c.population_m, 0)                                             AS population_m,
    ROUND(s.paid_ott_subs_m, 1)                                          AS paid_ott_subs_m,
    ROUND(100.0 * s.paid_ott_subs_m / c.population_m, 1)                 AS paid_subs_per_100_people,
    ROUND(s.ott_revenue_usd_bn, 2)                                       AS ott_revenue_usd_bn,
    ROUND(s.ott_revenue_usd_bn * 1000.0 / NULLIF(s.paid_ott_subs_m, 0), 2) AS implied_revenue_per_sub_usd_yr,
    ROUND(s.netflix_subs_m, 1)                                           AS netflix_subs_m,
    ROUND(100.0 * s.netflix_subs_m / c.population_m, 1)                  AS netflix_per_100_people,
    RANK() OVER (ORDER BY s.ott_revenue_usd_bn * 1000.0
                 / NULLIF(s.paid_ott_subs_m, 0) DESC)                    AS yield_rank,
    RANK() OVER (ORDER BY s.paid_ott_subs_m DESC)                        AS base_rank
FROM streaming s
JOIN countries c ON c.country = s.country
ORDER BY implied_revenue_per_sub_usd_yr DESC;
