CREATE OR REPLACE VIEW subset AS
SELECT
    t.date,
    t.store_nbr,
    t.family,
    t.sales,
    t.onpromotion,
    s.city,
    s.state,
    s.type,
    s.cluster,
    o.dcoilwtico
FROM train t
JOIN stores s USING (store_nbr)
LEFT JOIN oil o USING(date)
WHERE t.store_nbr IN (44, 3, 51, 11, 24)
    AND t.family IN ('GROCERY I', 'BEVERAGES', 'PRODUCE', 'CLEANING', 'DAIRY')
    AND t.date >= '2015-08-16';