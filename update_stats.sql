-- CptS 451 Milestone 2
-- Kwadwo Afriyie
-- UPDATE.sql
-- Recalculates num_checkins, review_count, and reviewrating for every business.
-- Uses a temp table + single join UPDATE (per the spec's suggestion) instead of
-- correlated subqueries, since those would re-scan Review/Checkin per business row.

BEGIN;

-- ---------------------------------------------------------
-- 1. Pre-aggregate checkins per business
-- ---------------------------------------------------------
CREATE TEMP TABLE checkin_totals AS
SELECT business_id, SUM(count) AS total_checkins
FROM Checkin
GROUP BY business_id;

-- ---------------------------------------------------------
-- 2. Pre-aggregate review count + avg rating per business
-- ---------------------------------------------------------
CREATE TEMP TABLE review_totals AS
SELECT business_id,
       COUNT(*)      AS total_reviews,
       AVG(stars)    AS avg_rating
FROM Review
GROUP BY business_id;

-- ---------------------------------------------------------
-- 3. Update num_checkins
-- Businesses with no checkin rows keep 0 (already the default;
-- LEFT JOIN would be needed only if we wanted to reset non-matches,
-- so we just update the matching rows here).
-- ---------------------------------------------------------
UPDATE Business b
SET num_checkins = c.total_checkins
FROM checkin_totals c
WHERE b.business_id = c.business_id;

-- ---------------------------------------------------------
-- 4. Update review_count and reviewrating together
-- ---------------------------------------------------------
UPDATE Business b
SET review_count = r.total_reviews,
    reviewrating = r.avg_rating
FROM review_totals r
WHERE b.business_id = r.business_id;

-- ---------------------------------------------------------
-- 5. Clean up temp tables
-- ---------------------------------------------------------
DROP TABLE checkin_totals;
DROP TABLE review_totals;

COMMIT;