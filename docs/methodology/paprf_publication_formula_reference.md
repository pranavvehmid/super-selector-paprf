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

## M07. Frozen Lens A score

$$
\begin{aligned}
\delta_j &= x_{j,P}-x_{j,O}\\
z_j &= \frac{\delta_j-\bar\delta_j}{s_j}\\
L &= \frac{n_P}{n_P+60}\frac{\sum_j d_jz_j}{3}
\end{aligned}
$$

$x_{j,P}$ and $x_{j,O}$ are pressure and ordinary rates. The eligible discipline peers provide the mean gap $\bar\delta_j$ and sample spread $s_j$. Signs $d_j$ are $(+1,-1,-1)$ for batting runs per ball, dots and dismissals, and $(-1,+1,+1)$ for bowling economy, dots and wickets. Each group needs 60 opportunities and six matches. This is a signed, unitless lift score. For signed components 1.2, 0.6 and 0.3 over 120 pressure opportunities, the average 0.7 is multiplied by 2/3 to give approximately 0.467. Pooled rates can reflect different phase mixes. See the [archived formula ledger](lens_a_formula_ledger.md).

## M08. Matched cells and pressure share

$$
\begin{aligned}
\bar\Delta &= \frac{\sum_c n_{c,P}\Delta_c}{\sum_c n_{c,P}}\\
\mathrm{share}_{g,b} &= 100\,\frac{N_{g,b}}{\sum_b N_{g,b}}
\end{aligned}
$$

$c$ identifies a matched cell, $n_{c,P}$ is its pressure opportunity count and $\Delta_c$ is its within-cell pressure-minus-ordinary rate. This weights cells by observed pressure exposure. Cells with lifts 0.2 and −0.1 and pressure counts 30 and 10 yield 0.125. Refinements change cell definitions or regularisation as described in M03. For the pressure bars, $N_{g,b}$ counts delivery events in band $b$ and innings-phase group $g$. For 18 elevated events out of 60 in that group, the share is 30%. Whole-sample percentages use all retained events as the denominator.

## M09. Signed standardisation and role score

$$
\begin{aligned}
z_{ij} &= \operatorname{clip}_{[-3,3]}\left(d_j\frac{x_{ij}-\bar x_j}{s_j}\right)\\
C_i &= \frac{n_i}{n_i+120}\sum_j w_j z_{ij}
\end{aligned}
$$

$x_{ij}$ is the player's mean outcome residual in the role, compared with eligible peers' mean $\bar x_j$ and sample spread $s_j$. Zero spread gives zero. Batting runs, boundaries and dismissals use signs +, +, −. Bowling conceded runs, boundaries and credited wickets use −, −, +. The role leaderboard uses $C_i$. The discipline reference in M05 normalises the unshrunk sum first. With opener weights 45%, 30%, 25%, components 2, 1, −0.4 and 120 balls, the weighted sum is 1.10 and the role score is 0.55. Clipping caps individual extremes; correlated run and boundary components still share information.

## M10. India sensitivity and boundary residualisation

$$
\begin{aligned}
\bar e^{\,*} &= \frac{A+0.5 A_{\mathrm{India}}}{n+0.5 n_{\mathrm{India}}}\\
y^{\,*} &= y-\beta(x-\bar x)\\
\beta &= \frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sum_i(x_i-\bar x)^2}
\end{aligned}
$$

$A$ and $n$ are the total residual sum and scored balls; the subscripted values select India venues. For total residual sum 12 in 100 balls, of which 8 came from 40 India balls, the sensitivity average is $(12+0.5(8))/(100+0.5(40))=0.1333$. In the alternate boundary score, $x$ and $y$ are peer run and boundary residual means. The slope is zero for a flat run component. This tests dependence on a shared linear signal. These settings are sensitivity comparisons.

## M11. Coverage and resample share

$$
\begin{aligned}
\mathrm{missing}\% &= 100\,N_{\mathrm{blank}}/N_{\mathrm{rows}}\\
\mathrm{top10\ share}\% &= 100\,D_{\mathrm{top10}}/D\\
\operatorname{E}|A\cap B| &= \frac{100}{N}
\end{aligned}
$$

The dataset share divides field blanks by all rows of that file, so 6/100 is 6%. The role top-ten share divides appearances by the 500 historical whole-match draws, so 375 appearances correspond to 75%. The last formula uses two independent uniform ten-member sets from $N\ge10$ common players. At $N=40$, chance overlap is 2.5 names. In the split-half tests, within-exposure shuffles supply the more specific comparison.
