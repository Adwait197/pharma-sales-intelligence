/* ------------------------------------------------------------
   Is the regional pattern a shift within Eli Lilly's portfolio?
   Prediction 1: Lilly's combined share does NOT differ by region.
   Prediction 2: Mounjaro's share of Lilly's TRx DOES differ by region.
   ------------------------------------------------------------ */
%let year = 2024;

/* 1. Read the CSV */
proc import datafile="~/sas_glp1_state_share.csv"
    out=work.glp1
    dbms=csv
    replace;
    guessingrows=max;
run;

/* 2. One row per state: Lilly's share, and Mounjaro's share of Lilly */
proc sql;
    create table work.lilly as
    select state_abbr,
           census_region,
           sum(case when brand_family in ("Mounjaro", "Trulicity")
                    then trx_share_in_segment else 0 end) * 100
               as lilly_share_pct,
           sum(case when brand_family = "Mounjaro" then trx else 0 end)
             / sum(case when brand_family in ("Mounjaro", "Trulicity")
                        then trx else 0 end) * 100
               as mounjaro_pct_of_lilly
    from work.glp1
    where data_year = &year
    group by state_abbr, census_region;
quit;

/* 3. A reusable block that runs the full regional test on any column */
%macro region_test(var, label);
    title "&label, &year, by Census region";

    proc means data=work.lilly n mean std min max maxdec=1;
        class census_region;
        var &var;
    run;

    proc sgplot data=work.lilly;
        vbox &var / category=census_region;
        yaxis label="&label (%)";
        xaxis label="US Census region";
    run;

    proc glm data=work.lilly;
        class census_region;
        model &var = census_region;
        means census_region / hovtest=levene welch tukey;
    run;
    quit;

    proc npar1way data=work.lilly wilcoxon;
        class census_region;
        var &var;
    run;

    title;
%mend region_test;

/* 4. Run the test twice */
%region_test(lilly_share_pct, Eli Lilly combined share of GLP-1 diabetes TRx)
%region_test(mounjaro_pct_of_lilly, Mounjaro share of Lilly GLP-1 diabetes TRx)