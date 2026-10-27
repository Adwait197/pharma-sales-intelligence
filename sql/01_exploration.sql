-- 1. Which GLP-1 brand/generic names exist in the CMS data?

SELECT DISTINCT brnd_name, gnrc_name
FROM raw.geography_drug
WHERE gnrc_name ILIKE ANY (ARRAY[
    '%semaglutide%', '%dulaglutide%', '%liraglutide%',
    '%exenatide%', '%tirzepatide%', '%lixisenatide%'
])
ORDER BY gnrc_name, brnd_name;

-- 2. Ozempic national TRx, writers and scripts per writer by year

SELECT data_year,
       tot_clms::numeric      AS trx,
       tot_prscrbrs::numeric  AS writers,
       ROUND(tot_clms::numeric / tot_prscrbrs::numeric, 1) AS scripts_per_writer
FROM raw.geography_drug
WHERE prscrbr_geo_lvl = 'National'
  AND brnd_name ILIKE 'ozempic'
ORDER BY data_year;

-- 3. GLP-1 class market share by year (CTE + window function)

WITH glp1 AS (
    SELECT data_year,
           brnd_name,
           SUM(tot_clms::numeric) AS trx
    FROM raw.geography_drug
    WHERE prscrbr_geo_lvl = 'National'
      AND gnrc_name ILIKE ANY (ARRAY[
          '%semaglutide%', '%dulaglutide%', '%liraglutide%',
          '%exenatide%', '%tirzepatide%', '%lixisenatide%'
      ])
    GROUP BY data_year, brnd_name
)
SELECT data_year,
       brnd_name,
       trx,
       ROUND(100 * trx / SUM(trx) OVER (PARTITION BY data_year), 1) AS share_pct
FROM glp1
ORDER BY data_year, trx DESC;