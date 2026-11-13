# Findings

## 1. Victoza led the GLP-1 diabetes market in 2018
Grouped by brand family, Victoza held 44.3% of diabetes-segment TRx, ahead of Trulicity (38.6%).
Counted by raw CMS brand names, Trulicity appeared to lead. Brand-family grouping reverses the answer.

## 2. Ozempic's growth shifted from reach to frequency
2018 to 2021: prescribing doctors grew about 9x (13.6k to 122.6k).
2021 to 2024: doctors grew about 2.3x while scripts per doctor rose from 16.4 to 36.3.
Caveat: TRx includes refills, so rising scripts per doctor partly reflects patients staying on therapy.

## 3. Mounjaro's 2024 share is significantly higher in the South
Average state share: South 26.7%, Midwest 22.7%, West 20.8%, Northeast 19.2%.
One-way ANOVA (SAS PROC GLM): F(3, 47) = 6.04, p = 0.0014, R-squared = 0.28.
Levene p = 0.74 (equal variance holds). Welch p = 0.004. Kruskal-Wallis p = 0.003.
Tukey HSD: South > Northeast (+7.5 pts) and South > West (+5.8 pts). No other pair significant.
Limits: neighbouring states are not fully independent; one brand and one year; the test shows where, not why.

## 4. Ozempic's share does not vary by region
Average state share 2024: South 48.7%, West 48.7%, Midwest 48.2%, Northeast 47.4%.
One-way ANOVA: F(3, 47) = 0.20, p = 0.89, R-squared = 0.013. Welch p = 0.91. Kruskal-Wallis p = 0.86. No Tukey pair significant.
Implication: Mounjaro's higher Southern share (finding 3) is not taken from Ozempic. Other GLP-1 brands hold 24.6% in the South against 33.4% in the Northeast, so Mounjaro's Southern gains come mainly at the expense of older brands.

## 5. Trulicity mirrors Mounjaro: stronger in the Northeast
Average state share 2024: Northeast 25.1%, West 21.1%, Midwest 21.0%, South 17.3%.
One-way ANOVA: F(3, 47) = 4.94, p = 0.0046, R-squared = 0.24. Levene p = 0.28. Welch p = 0.017. Kruskal-Wallis p = 0.003.
Tukey: Northeast > South (+7.7 pts), the only significant pair.

## Hypothesis under test: the regional pattern is a shift within Eli Lilly's portfolio
Trulicity and Mounjaro are both Eli Lilly. Their combined regional average share is nearly flat
(South 44.0%, Northeast 44.3%, Midwest 43.7%, West 41.9%), as is Ozempic (~48%).
Prediction: Lilly's combined share shows no regional difference, while Mounjaro's share of Lilly's TRx does.
Test: sas/02_lilly_portfolio_anova.sas

## 6. CONFIRMED: the regional pattern is a shift within Eli Lilly's portfolio
Predictions were written before the tests ran (sas/02_lilly_portfolio_anova.sas).

Prediction 1, Lilly combined share (Mounjaro + Trulicity) does not differ by region: HELD.
Means: Northeast 44.2%, South 44.0%, Midwest 43.6%, West 41.9%.
ANOVA F(3, 47) = 0.47, p = 0.71, R-squared = 0.03. Welch p = 0.81. Kruskal-Wallis p = 0.72. No Tukey pair significant.

Prediction 2, Mounjaro's share of Lilly's GLP-1 TRx differs by region: HELD.
Means: South 60.5%, Midwest 52.3%, West 49.4%, Northeast 43.8%.
ANOVA F(3, 47) = 7.71, p = 0.0003, R-squared = 0.33. Levene p = 0.48. Welch p = 0.0025. Kruskal-Wallis p = 0.001.
Tukey: South > Northeast (+16.7 pts), South > West (+11.1 pts).

Conclusion: Mounjaro's higher Southern share reflects a further-advanced Trulicity-to-Mounjaro mix within Lilly,
not share taken from Ozempic. Limit: state-level aggregates show prescription mix, not individual patient switching.