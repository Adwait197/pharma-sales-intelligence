-- Mart: GLP-1 national volume, cost, writers, share and growth by brand family and year.
-- Grain: one row per year, brand family. Uses CMS national rows directly.

with claims as (

    select * from {{ ref('int_glp1_claims') }}
    where geo_level = 'National'

),

by_family as (

    select
        data_year,
        brand_family,
        molecule,
        manufacturer,
        market_segment,

        sum(total_claims)           as trx,
        sum(total_30day_fills)      as fills_30day,
        sum(total_drug_cost)        as drug_cost,
        max(total_prescribers)      as writers_low,
        sum(total_prescribers)      as writers_high,
        count(*)                    as cms_names_combined

    from claims
    group by 1, 2, 3, 4, 5

)

select
    *,
    round(trx / sum(trx) over (partition by data_year, market_segment), 4)
                                    as trx_share_in_segment,
    round(fills_30day / sum(fills_30day) over (partition by data_year, market_segment), 4)
                                    as fills_share_in_segment,
    lag(trx) over (partition by brand_family order by data_year)
                                    as trx_prior_year,
    round(trx / nullif(lag(trx) over (partition by brand_family order by data_year), 0) - 1, 4)
                                    as trx_growth_yoy
from by_family