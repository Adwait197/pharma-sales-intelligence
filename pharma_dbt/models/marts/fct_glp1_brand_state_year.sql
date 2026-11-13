-- Mart: GLP-1 volume, cost, writers and share by brand family, state and year.
-- Grain: one row per year, state, brand family.
-- Scope: 50 states and DC. Territories and the 29 unknown-state rows are excluded.

with claims as (

    select * from {{ ref('int_glp1_claims') }}
    where is_state_or_dc

),

regions as (

    select * from {{ ref('state_regions') }}

),

by_family as (

    select
        data_year,
        geo_code                    as state_fips,
        geo_name                    as state_name,
        brand_family,
        molecule,
        manufacturer,
        market_segment,

        sum(total_claims)           as trx,
        sum(total_30day_fills)      as fills_30day,
        sum(total_drug_cost)        as drug_cost,

        -- Writers cannot simply be added up (see notes).
        max(total_prescribers)      as writers_low,
        sum(total_prescribers)      as writers_high,
        count(*)                    as cms_names_combined

    from claims
    group by 1, 2, 3, 4, 5, 6, 7

),

with_share as (

    select
        *,
        round(trx / sum(trx) over (partition by data_year, state_fips, market_segment), 4)
                                    as trx_share_in_segment,
        round(fills_30day / sum(fills_30day) over (partition by data_year, state_fips, market_segment), 4)
                                    as fills_share_in_segment,
        round(drug_cost / nullif(trx, 0), 2)
                                    as cost_per_claim
    from by_family

)

select
    w.*,
    r.state_abbr,
    r.census_region,
    r.census_division
from with_share as w
left join regions as r
    on w.state_fips = r.state_fips