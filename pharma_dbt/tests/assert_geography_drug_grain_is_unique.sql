-- Each year + geography + brand + generic must appear exactly once.
-- Any row returned here is a duplicate, and duplicates double-count prescriptions.

select
    data_year,
    geo_level,
    coalesce(geo_code, 'NATIONAL') as geo_code,
    brand_name,
    generic_name,
    count(*) as row_count
from {{ ref('stg_geography_drug') }}
group by 1, 2, 3, 4, 5
having count(*) > 1