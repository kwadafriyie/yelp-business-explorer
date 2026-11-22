-- analysis_queries.sql
-- Builds the tables behind the "popular" and "successful" metrics.
-- Run after the data load and update_stats.sql.

-- POPULARITY
-- Goal: compare each business to its peers (same zipcode and category)
-- instead of using raw counts.

-- Step 1: average check-ins and reviews for every (zipcode, category) peer group
CREATE TABLE zip_category_stats AS
SELECT b.zipcode, bc.category_id,
       AVG(b.num_checkins) AS avg_checkins,
       AVG(b.review_count) AS avg_reviews,
       COUNT(*)            AS business_count
FROM Business b
JOIN Business_Category bc ON b.business_id = bc.business_id
GROUP BY b.zipcode, bc.category_id;

-- Step 2: expected check-ins and reviews per business,
-- averaged across all categories the business belongs to
CREATE TABLE business_expected_stats AS
SELECT b.business_id,
       AVG(zcs.avg_checkins) AS expected_checkins,
       AVG(zcs.avg_reviews)  AS expected_reviews
FROM Business b
JOIN Business_Category bc ON b.business_id = bc.business_id
JOIN zip_category_stats zcs
     ON zcs.zipcode = b.zipcode AND zcs.category_id = bc.category_id
GROUP BY b.business_id;

-- Step 3: popularity score (ranking query, not stored)
-- Relative difference from expected check-ins plus relative difference
-- from expected reviews. NULLS LAST keeps businesses with a zero-average
-- peer group (NULL score) out of the top of the list.
SELECT b.business_id, b.name, b.zipcode, b.num_checkins, b.review_count,
       (b.num_checkins - bes.expected_checkins) / NULLIF(bes.expected_checkins, 0)
     + (b.review_count - bes.expected_reviews)  / NULLIF(bes.expected_reviews, 0)
       AS popularity_score
FROM Business b
JOIN business_expected_stats bes ON b.business_id = bes.business_id
ORDER BY popularity_score DESC NULLS LAST;

-- SUCCESS
-- Goal: reward businesses that last a long time and attract
-- established, engaged reviewers.

-- Step 4: longevity, the span between a business's first and last review
CREATE TABLE business_longevity AS
SELECT business_id,
       MAX(date::date) - MIN(date::date) AS longevity_days
FROM Review
GROUP BY business_id;

-- Step 5: reviewer quality (original version, all businesses)
CREATE TABLE business_reviewer_quality AS
SELECT r.business_id,
       AVG(u.fans)         AS avg_reviewer_fans,
       AVG(u.review_count) AS avg_reviewer_review_count
FROM Review r
JOIN Yelp_User u ON r.user_id = u.user_id
GROUP BY r.business_id;

-- Step 5b: reviewer quality restricted to businesses with at least 10 reviews,
-- so a few high-fan reviewers cannot dominate the average
CREATE TABLE business_reviewer_quality_min10 AS
SELECT r.business_id,
       AVG(u.fans)         AS avg_reviewer_fans,
       AVG(u.review_count) AS avg_reviewer_review_count,
       COUNT(*)            AS review_count_used
FROM Review r
JOIN Yelp_User u ON r.user_id = u.user_id
GROUP BY r.business_id
HAVING COUNT(*) >= 10;

-- Step 6: success score (ranking query, not stored)
-- Each component is min-max normalized to 0-1 over the filtered population,
-- then the three are summed.
SELECT bl.business_id, b.name, bl.longevity_days,
       rq.avg_reviewer_fans, rq.avg_reviewer_review_count,
       (bl.longevity_days - MIN(bl.longevity_days) OVER())
         / NULLIF(MAX(bl.longevity_days) OVER() - MIN(bl.longevity_days) OVER(), 0)
     + (rq.avg_reviewer_fans - MIN(rq.avg_reviewer_fans) OVER())
         / NULLIF(MAX(rq.avg_reviewer_fans) OVER() - MIN(rq.avg_reviewer_fans) OVER(), 0)
     + (rq.avg_reviewer_review_count - MIN(rq.avg_reviewer_review_count) OVER())
         / NULLIF(MAX(rq.avg_reviewer_review_count) OVER() - MIN(rq.avg_reviewer_review_count) OVER(), 0)
       AS success_score
FROM business_longevity bl
JOIN business_reviewer_quality_min10 rq ON bl.business_id = rq.business_id
JOIN Business b ON b.business_id = bl.business_id
ORDER BY success_score DESC;