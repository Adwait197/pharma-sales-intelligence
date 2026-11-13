-- One row per year, state and brand family. Any row returned is a duplicate.
select data_year, state_fips, brand_family, count(*) as row_count
from {{ ref('fct_glp1_brand_state_year') }}
group by 1, 2, 3
having count(*) > 1