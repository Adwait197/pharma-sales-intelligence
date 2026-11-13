/* ------------------------------------------------------------
   Does a brand's GLP-1 diabetes market share differ by US region?
   Data: CMS Medicare Part D, GLP-1 diabetes segment, by state.
   Change the two lines below to test another brand or year.
   ------------------------------------------------------------ */
%let brand = Mounjaro;
%let year  = 2024;

title "&brand, &year: share of GLP-1 diabetes prescriptions by Census region";

/* 1. Read the CSV */
proc import datafile="~/sas_glp1_state_share.csv"
    out=work.glp1
    dbms=csv
    replace;
    guessingrows=max;
run;

/* 2. Keep one brand in one year, share as a percent */
data work.analysis;
    set work.glp1;
    where data_year = &year and brand_family = "&brand";
    share_pct = trx_share_in_segment * 100;
run;

/* 3. Describe each region */
proc means data=work.analysis n mean std min max maxdec=1;
    class census_region;
    var share_pct;
run;

/* 4. Box plot per region */
proc sgplot data=work.analysis;
    vbox share_pct / category=census_region;
    yaxis label="&brand share of GLP-1 diabetes prescriptions (%)";
    xaxis label="US Census region";
run;

/* 5. One-way ANOVA, spread check, Welch, Tukey pairs */
proc glm data=work.analysis;
    class census_region;
    model share_pct = census_region;
    means census_region / hovtest=levene welch tukey;
run;
quit;

/* 6. Rank-based check (Kruskal-Wallis) */
proc npar1way data=work.analysis wilcoxon;
    class census_region;
    var share_pct;
run;

title;