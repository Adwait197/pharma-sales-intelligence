-- Intermediate: GLP-1 rows only, labelled with the market basket.
-- Grain: same as staging (one row per year, geography, CMS brand name).

with staging as (

    select * from {{ ref('stg_geography_drug') }}

),

market_basket as (

    select * from {{ ref('market_basket') }}

),

joined as (

    select
        s.data_year,
        s.geo_level,
        s.geo_code,
        s.geo_name,

        -- True only for the 50 states and DC (FIPS 01 to 56).
        -- CASE runs the checks in order, so odd codes never reach the ::int cast.
        case
            when s.geo_level <> 'State' then false
            when s.geo_code ~ '^[0-9]{2}$' then s.geo_code::int <= 56
            else false
        end                                 as is_state_or_dc,

        s.brand_name,
        m.brand_family,
        m.molecule,
        m.manufacturer,
        m.market_segment,

        s.total_claims,
        s.total_30day_fills,
        s.total_drug_cost,
        s.total_prescribers

    from staging as s
    inner join market_basket as m
        on s.brand_name = m.brand_name

)

select * from joined