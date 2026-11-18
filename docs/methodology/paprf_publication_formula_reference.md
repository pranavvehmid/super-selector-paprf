# Publication formula reference

The numbered identifiers below map the presentation to the implemented algorithms. The comparison tables distinguish pressure lift from contextual role effectiveness. In all formula entries, missing inputs exclude the relevant observation or make a ratio unavailable. A blank display never substitutes for measured zero.

## M01. Conventional rate benchmarks

$$
\mathrm{SR}=100R/B,\qquad \mathrm{Econ}=6C/L
$$

$R$ denotes attributed batting runs, $B$ counted balls faced, $C$ attributed conceded runs and $L$ legal balls. Batting strike rate is runs per 100 counted balls; bowling economy is runs per six legal balls. Both are nonnegative when defined. Higher strike rate means faster scoring, while lower economy means stronger run prevention. The pressure and contextual score conventions treat extras differently, so compare numerator scope before interpreting any gap. For example, 30 from 20 gives a strike rate of 150. 30 from 24 legal bowling deliveries gives economy 7.5. Batting average, bowling average and bowling strike rate use dismissals or credited wickets as specified in the LaTeX report. These conventional comparator ratios are not the unified index.

## M02. Pressure exposure

$$
P_1=0.70g((\ell-72)/48)+0.30g(w/10)
$$

$$
P_2=0.55g((6r/\max(1,b)-7)/5)+0.25g(w/10)+0.20g(\ell/120)
$$

$g(x)=\min(1,\max(0,x))$ clamps a component. Here $\ell$ is legal balls completed, $w$ is wickets lost, $r$ is runs required, and $b$ is balls remaining. State precedes the rated ball. The unitless index is bounded by zero and one. The band gates are 0.40 and 0.65. At 90 balls completed, four wickets lost and twelve required runs per over, the chase index is 0.80. This corresponds to the high band. The pressure curve in the website uses the same formula. First-innings powerplay events cannot cross the elevated threshold. The [pressure protocol](pressure_definition.md) documents this conditional design.

## M03. Regularised pressure lift

$$
\theta=d\frac{ab}{ab+12(a+b)}
$$

Use positive ordinary and pressure opportunity counts $a,b$ and let $d$ be the observed pressure-minus-ordinary rate. $\theta$ has the same units as the input. This factor reduces uncertain cell differences toward zero. For $a=6$, $b=4$ and $d=-2.583333$ runs per ball, $\theta=-0.430556$. V4 averages cell lifts with pressure opportunity weights. Role-oriented z-scores feed a composite with pressure-ball shrinkage and whole-match resampling. Sensitivity uses ridge strengths 6 and 24. A nonlinear resampling interval does not establish temporal persistence. See the [v4 derivation](paprf_v4_reanalysis.md).

## M04. Context and opponent expectations

$$
\hat{y}=\operatorname{clip}\left(\frac{A+120\mu}{n+120}
+0.75\bar e_{\rm player}+0.25\bar e_{\rm team}\right)
$$

$A$ is the historical context sum, $n$ the context opportunity count and $\mu$ the parent mean. $\bar e_{\rm player}$ and $\bar e_{\rm team}$ are prior residual means shrunk with counts 120 and 360, respectively. Clip to the metric's declared allowed range. The residual is outcome minus predicted outcome. It has the units of the outcome; boundary and event probabilities lie in [0,1]. One run against an expectation of 0.8 yields +0.2. Positive conceded-run residuals are worse for bowlers. Estimates freeze within each date and use only earlier dates. Opponent quality is a historical proxy and can reflect schedule effects. The [contextual role protocol](paprf_contextual_role_profiles.md) records the complete hierarchy, weights and alternatives.

## M05. Discipline index

$$
c=\sum_j w_jz_j,\qquad Q=100\Phi((c-\mu_r)/\sigma_r),\qquad
S=50+\frac{n}{n+120}(Q-50).
$$

$z_j$ denotes a role-oriented clipped metric on the interval [−3,3]; $w_j$ are nonnegative role weights summing to one. $\mu_r$ and $\sigma_r$ are the eligible role centre and sample spread. A flat role cohort takes $Q=50$. The normal reference is not an empirical percentile or forecast probability. $n$ denotes scored opportunities. At $Q=90$ and $n=120$, $S=70$. Within each discipline, the most-supported role is primary. At most one secondary gives credit $0.10\min(1,n_s/n_p)\max(0,S_s-50)$. The final index is bounded at 100. The worked player trace and ranking eligibility appear in the [role index derivation](paprf_unified_ranking.md) and [discipline rerun](paprf_discipline_rankings_v2.md).

## M06. Rank agreement and uncertainty

$$
\rho=\mathrm{Corr}(\mathrm{midrank}(x),\mathrm{midrank}(y)),\qquad
J(A,B)=\frac{|A\cap B|}{|A\cup B|}
$$

$x,y$ are score vectors on common eligible IDs. Spearman $\rho$ ranges from −1 to 1, with undefined correlation when a rank vector is constant. $A$ and $B$ are top-ten membership sets. Jaccard overlap ranges from 0 to 1. Two lists sharing nine names have $J=9/11$. The core evidence reports shared names as a count out of ten. Empirical p10 and p90 denote uncertainty quantiles over clustered match draws conditional on the fitted method. The [forward](paprf_forward_validation.md), [split-half](paprf_split_reliability.md) and [role](paprf_role_profile_validation.md) tests report coverage and weak points. No significance or causality is implied by these summaries.
