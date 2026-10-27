-- Staging: typed and renamed CMS geography-and-drug data.
-- One row per year, geography, brand name and generic name.
-- Rule: rename and retype only. No rows are removed here.

with source as (

    select * from {{ source('raw', 'geography_drug') }}

),

renamed as (

    select
        -- When and where
        data_year::int                                   as data_year,
        trim(prscrbr_geo_lvl)                            as geo_level,
        nullif(trim(prscrbr_geo_cd), '')                 as geo_code,
        nullif(trim(prscrbr_geo_desc), '')               as geo_name,

        -- What drug
        trim(brnd_name)                                  as brand_name,
        trim(gnrc_name)                                  as generic_name,

        -- Volume and cost (text to numbers)
        nullif(trim(tot_prscrbrs), '')::numeric          as total_prescribers,
        nullif(trim(tot_clms), '')::numeric              as total_claims,
        nullif(trim(tot_30day_fills), '')::numeric       as total_30day_fills,
        nullif(trim(tot_drug_cst), '')::numeric          as total_drug_cost,
        nullif(trim(tot_benes), '')::numeric             as total_beneficiaries,
        coalesce(trim(tot_benes), '') = ''               as is_beneficiaries_suppressed,

        -- Patients aged 65 and over
        nullif(trim(ge65_sprsn_flag), '')                as ge65_suppression_flag,
        nullif(trim(ge65_tot_clms), '')::numeric         as ge65_total_claims,
        nullif(trim(ge65_tot_30day_fills), '')::numeric  as ge65_total_30day_fills,
        nullif(trim(ge65_tot_drug_cst), '')::numeric     as ge65_total_drug_cost,
        nullif(trim(ge65_bene_sprsn_flag), '')           as ge65_bene_suppression_flag,
        nullif(trim(ge65_tot_benes), '')::numeric        as ge65_total_beneficiaries,

        -- Patient cost share: low-income subsidy vs everyone else
        nullif(trim(lis_bene_cst_shr), '')::numeric      as lis_beneficiary_cost_share,
        nullif(trim(nonlis_bene_cst_shr), '')::numeric   as nonlis_beneficiary_cost_share,

        -- Drug type flags (Y/N to true/false)
        trim(opioid_drug_flag) = 'Y'                     as is_opioid,
        trim(opioid_la_drug_flag) = 'Y'                  as is_long_acting_opioid,
        trim(antbtc_drug_flag) = 'Y'                     as is_antibiotic,
        trim(antpsyct_drug_flag) = 'Y'                   as is_antipsychotic,

        -- Lineage
        source_file,
        loaded_at

    from source

)

select * from renamed