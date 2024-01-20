DROP TABLE IF EXISTS portfolio_deduped;
CREATE TABLE portfolio_deduped as
WITH base AS
    (SELECT *,
            ROW_NUMBER() OVER ( PARTITION BY company ORDER BY cleaned_url is null,is_divestment) rn
              FROM portfolio)
SELECT company,sector,country,fund,entry_year,exit_year,url,cleaned_url,is_divestment
FROM base
WHERE rn=1;

DROP TABLE IF EXISTS temp_org_subset;
CREATE TEMPORARY TABLE temp_org_subset AS
SELECT b.*
FROM
    portfolio_deduped a
    INNER JOIN
    organisation b
USING(cleaned_url);

DROP TABLE IF EXISTS organisation_deduped_subset;
CREATE TABLE organisation_deduped_subset AS
WITH base as (
SELECT a.*,b.*,
       row_number() OVER ( PARTITION BY b.cleaned_url ORDER BY
           lower(company) = lower(name) desc,
           num_funding_rounds desc,
           length(homepage_url)) rn
FROM
    portfolio_deduped a
    INNER JOIN
    temp_org_subset b
    USING(cleaned_url)
)
SELECT b.*
FROM
    base a
    INNER join
    temp_org_subset b
USING(uuid)
WHERE rn=1;

DROP TABLE IF EXISTS funding_subset;
CREATE TABLE funding_subset AS
SELECT
    c.org_uuid,
    c.uuid as funding_uuid,
    announced_on,
    investment_type,
    investor_count,
    raised_amount_usd
FROM
    portfolio_deduped a
    INNER JOIN
    organisation_deduped_subset b
    USING(cleaned_url)
INNER JOIN
    funding c
ON
    b.uuid = c.org_uuid;