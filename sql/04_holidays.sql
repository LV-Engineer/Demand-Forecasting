CREATE OR REPLACE VIEW holiday_flags AS
WITH h AS (
    SELECT *,
           type IN ('Holiday', 'Transfer', 'Additional', 'Bridge') AS is_holiday
    FROM holidays
    WHERE NOT transferred
      AND type <> 'Work Day'
)
SELECT
    h.date,
    s.store_nbr,
    bool_or(h.is_holiday AND h.locale = 'National') AS holiday_national,
    bool_or(h.is_holiday AND h.locale = 'Regional') AS holiday_regional,
    bool_or(h.is_holiday AND h.locale = 'Local')    AS holiday_local,
    bool_or(h.type = 'Event')                       AS is_event
FROM h
JOIN stores s
  ON h.locale = 'National'
   OR (h.locale = 'Regional' AND h.locale_name = s.state)
   OR (h.locale = 'Local'    AND h.locale_name = s.city)
GROUP BY h.date, s.store_nbr;

CREATE OR REPLACE VIEW subset_full AS
SELECT
  sb.*,
    COALESCE(f.holiday_national, FALSE) AS holiday_national,
    COALESCE(f.holiday_regional, FALSE) AS holiday_regional,
    COALESCE(f.holiday_local,    FALSE) AS holiday_local,
    COALESCE(f.is_event,         FALSE) AS is_event
FROM subset sb
LEFT JOIN holiday_flags f
  ON f.date = sb.date AND f.store_nbr = sb.store_nbr;