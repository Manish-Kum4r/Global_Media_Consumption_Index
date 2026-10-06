-- ============================================================
-- GLOBAL MEDIA CONSUMPTION INDEX, database schema
-- Engine: SQLite 3 (portable to PostgreSQL / Snowflake with minor edits)
-- Author: [Your name] | Data: 6 markets, 2020 & 2025
-- ============================================================
-- Notes
--   1. Every measured row carries data_quality and source_id, so no number in
--      this database is unattributed.
--   2. Time and money sit in separate tables. They come from different
--      measurement systems and are not additive across sources, so any join
--      between them is a deliberate choice rather than a default.
--   3. country is the natural key (6 rows), so there are no surrogate keys.
-- ============================================================

DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS streaming;
DROP TABLE IF EXISTS offline_physical;
DROP TABLE IF EXISTS market_size;
DROP TABLE IF EXISTS time_spend;
DROP TABLE IF EXISTS countries;

-- ---------------------------------------------------------- countries
CREATE TABLE countries (
    country                  TEXT PRIMARY KEY,
    region                   TEXT NOT NULL,
    population_m             REAL NOT NULL,
    internet_users_m         REAL NOT NULL,
    gdp_per_capita_usd       INTEGER NOT NULL,
    screen_economy_usd_bn    REAL NOT NULL,   -- MPA: TV + online video only
    digital_ad_per_capita_usd INTEGER NOT NULL,
    total_media_min_day      INTEGER NOT NULL, -- published all-media measure
    data_quality             TEXT NOT NULL CHECK (data_quality IN ('Reported','Derived','Estimated')),
    source_id                TEXT NOT NULL REFERENCES sources(source_id),  -- primary source (FK-enforced)
    all_sources              TEXT                                          -- full citation list, incl. secondary sources
);

-- ---------------------------------------------------------- time_spend
-- minutes per person per day, by market / format / year
CREATE TABLE time_spend (
    country          TEXT NOT NULL REFERENCES countries(country),
    format           TEXT NOT NULL CHECK (format IN
                       ('TV (linear)','Streaming video','Social & short video','Gaming','Music & audio')),
    year             INTEGER NOT NULL CHECK (year IN (2020, 2025)),
    minutes_per_day  REAL NOT NULL,
    data_quality     TEXT NOT NULL CHECK (data_quality IN ('Reported','Derived','Estimated')),
    source_id        TEXT NOT NULL REFERENCES sources(source_id),
    all_sources      TEXT,
    PRIMARY KEY (country, format, year)
);

-- ---------------------------------------------------------- market_size
-- industry revenue in USD billion, by market / format / year
CREATE TABLE market_size (
    country        TEXT NOT NULL REFERENCES countries(country),
    format         TEXT NOT NULL,
    year           INTEGER NOT NULL CHECK (year IN (2020, 2025)),
    revenue_usd_bn REAL NOT NULL,
    data_quality   TEXT NOT NULL CHECK (data_quality IN ('Reported','Derived','Estimated')),
    source_id      TEXT NOT NULL REFERENCES sources(source_id),
    all_sources    TEXT,
    definition     TEXT NOT NULL,   -- what is inside the number (ad + subs, etc.)
    PRIMARY KEY (country, format, year)
);

-- ---------------------------------------------------------- offline_physical
-- out-of-home formats: the ones time-use panels systematically under-count
CREATE TABLE offline_physical (
    country      TEXT NOT NULL REFERENCES countries(country),
    metric       TEXT NOT NULL,
    year         INTEGER NOT NULL,
    value        REAL NOT NULL,
    unit         TEXT NOT NULL,
    data_quality TEXT NOT NULL,
    source_id    TEXT NOT NULL REFERENCES sources(source_id),
    all_sources  TEXT,
    note         TEXT,
    PRIMARY KEY (country, metric, year)
);

-- ---------------------------------------------------------- streaming
CREATE TABLE streaming (
    country           TEXT NOT NULL REFERENCES countries(country),
    year              INTEGER NOT NULL,
    netflix_subs_m    REAL,
    paid_ott_subs_m   REAL,
    ott_revenue_usd_bn REAL,
    data_quality      TEXT NOT NULL,
    source_id         TEXT NOT NULL REFERENCES sources(source_id),
    all_sources       TEXT,
    PRIMARY KEY (country, year)
);

-- ---------------------------------------------------------- sources
CREATE TABLE sources (
    source_id     TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    publisher     TEXT NOT NULL,
    date          TEXT NOT NULL,
    url           TEXT NOT NULL,
    what_to_pull  TEXT
);

-- ---------------------------------------------------------- indexes
CREATE INDEX idx_time_country_year  ON time_spend(country, year);
CREATE INDEX idx_mkt_country_year   ON market_size(country, year);
CREATE INDEX idx_mkt_format         ON market_size(format);
