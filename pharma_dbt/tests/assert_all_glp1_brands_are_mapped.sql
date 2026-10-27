-- Every GLP-1 brand in the CMS data must appear in the market_basket seed.
-- Any row returned here is a brand that would silently drop out of the market.

select distinct
    s.brand_name,
    s.generic_name
from {{ ref('stg_geography_drug') }} as s
left join {{ ref('market_basket') }} as m
    on s.brand_name = m.brand_name
where m.brand_name is null
  and (
        s.generic_name ilike '%semaglutide%'
     or s.generic_name ilike '%dulaglutide%'
     or s.generic_name ilike '%liraglutide%'
     or s.generic_name ilike '%exenatide%'
     or s.generic_name ilike '%tirzepatide%'
     or s.generic_name ilike '%lixisenatide%'
  )