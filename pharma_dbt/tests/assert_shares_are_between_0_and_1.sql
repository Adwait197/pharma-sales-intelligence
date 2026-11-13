-- Market shares must sit between 0 and 1. Any row returned is impossible.
select data_year, state_fips, brand_family, trx_share_in_segment, fills_share_in_segment
from {{ ref('fct_glp1_brand_state_year') }}
where trx_share_in_segment not between 0 and 1
   or fills_share_in_segment not between 0 and 1