-- The state mart covers the 50 states and DC only.
-- Any year returned has more than 51 states, which means territories leaked in.
select data_year, count(distinct state_fips) as state_count
from {{ ref('fct_glp1_brand_state_year') }}
group by data_year
having count(distinct state_fips) > 51