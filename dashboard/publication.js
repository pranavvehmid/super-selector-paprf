"use strict";

const ROLE_TITLES = {
  opener:"Opener", top_order:"Top-order batter", middle_lower:"Middle/lower-order batter",
  late_entrant:"Late entrant", powerplay_bowler:"Powerplay bowler", middle_bowler:"Middle-overs bowler",
  death_bowler:"Death bowler",
};
const FIGURES = [
  ["paprf_role_annual_examples.png", "Annual contextual run residuals", "Runs per ball, annotated with exposure. These examples describe observed trajectories, with partial years and changing opposition as limitations.", "Contextual role profiles", "roles"],
  ["paprf_role_component_heatmaps.png", "Correlation across role metrics", "Spearman correlations expose shared information between runs and boundaries. High correlation motivates the residualised-boundary test.", "Contextual role profiles", "roles"],
  ["paprf_role_forward_validation.png", "Later-window role validation", "Spearman correlation between training ranks and later outcome scores. A blank role lacks adequate common evidence.", "Role validation", "role-validation"],
  ["paprf_pressure_distribution.png", "Delivery pressure by innings and phase", "Bars count delivery events. The first-innings index cannot designate powerplay events as elevated or high under its current formula.", "Pressure definition", "pressure-method"],
  ["paprf_v2_uncertainty.png", "Match-resampling score uncertainty", "The lines span empirical p10 to p90 scores. These are score ranges conditional on observed support.", "v2 uncertainty", "v2"],
  ["paprf_v4_sensitivity.png", "Pressure top-ten sensitivity", "Cell labels show shared players with the primary v4 point top ten. This comparison tests assumptions, with no predictive ranking claim.", "v4 methodology", "v4"],
  ["paprf_forward_validation.png", "Forward validation of pressure ranks", "Each marker family compares earlier rankings with later lift on common eligible players. Correlations change across windows.", "Pressure validation", "forward"],
  ["paprf_split_reliability.png", "Split-half pressure reliability", "Intervals summarize repeatability over whole-match splits and player shuffles within exposure groups.", "Split-half methods", "split"],
];

const GLOSSARY = [
  ["Pressure index and band", "A bounded pre-delivery scoreboard index on 0–1. Low values indicate less scoreboard stress. Below .40 is ordinary, .40 to below .65 elevated and .65 or above high. See the innings equations in the pressure protocol.", "An index of .61 is elevated. It uses earlier balls and not the ball being scored."],
  ["Opportunity", "A counted batter ball faced or a bowler legal ball. Evidence counts are in balls and opportunity-bearing matches.", "120 opportunities give retention of 120/(120+120) = .5 in the unified index."],
  ["Scoring rate and economy", "Batting strike rate is 100 × runs per ball faced. Bowling economy is 6 × conceded runs per legal ball. Role prediction uses the legal-ball bowling numerator, while conventional economy adds illegal-delivery concessions.", "30 runs from 20 balls is a strike rate of 150. Conceding 30 from 24 legal balls gives 7.5 per over."],
  ["Boundary, dot and event rates", "Count qualifying outcomes and divide by role opportunities. Rates range from 0 to 1, or 0% to 100%. Event means striker dismissal for batting or credited wicket for bowling.", "Three flagged and confirmed boundaries in 12 balls is 25%. Dots are diagnostics for the contextual role score."],
  ["Expected outcome and residual", "An earlier-date context forecast with a shrunken opponent adjustment. Residual equals observed minus expected, in runs per opportunity or probability units. Positive conceded-run residuals are worse for bowlers.", "Observed one run against an expectation of 0.8 produces a +0.2 run residual."],
  ["Signed z-score", "Difference from peer mean divided by sample standard deviation, with direction aligned to better performance. Contextual components are capped between −3 and +3.", "A rate 0.2 above a peer mean with SD 0.1 earns +2 before clipping for a batter."],
  ["Role reference and retention", "The normal cumulative function maps the unshrunk weighted role signal to a 0–100 reference. Retention is n/(n+120). The role score moves toward 50 when support is thin.", "Reference 90 and retention .5 give adjusted role score 70. Reference 90 is not a forecast probability."],
  ["Secondary credit", "At most one additional supported role adds 0.10 × relative opportunity × positive excess above 50, with relative opportunity capped at one. The maximum credit is five points.", "A secondary score of 80 with half the primary opportunities adds 1.5 points."],
  ["p10, p90 and top-ten share", "The tenth and ninetieth empirical score percentiles over match draws. Top-ten share is the fraction of historical resamples in which a player makes the top ten.", "499 of 500 draws gives 99.8%. This does not estimate future selection probability."],
  ["Spearman ρ", "Correlation of score ranks on the common eligible pool, from −1 to +1. Positive indicates similar ordering, near zero little monotone association, negative reversed ordering.", "If three players have identical order in both periods, ρ = +1. Shared eligibility affects interpretation."],
  ["Explosiveness and recency", "Explosiveness combines signed run and boundary z-scores in a 60/40 ratio and shrinks by opportunities. Trend slopes use ball-weighted annual residuals. The exploratory two-year half-life halves the recency weight every two years.", "Under the half-life, equal samples from 2024 and 2026 have weights .5 and 1. This does not change unified v1."],
  ["India exposure", "Based on match venue country. India-weighted sensitivity upweights observed India balls by 1.5×. A country split cannot identify the player's home ground, pitch shape or causal suitability.", "Ten India balls and ten other balls give an effective denominator of 25 in the weighted run residual."],
];

function describe(text, explanation) {
  const node = element("span", text);
  node.title = explanation;
  return node;
}

function selectedDiscipline() {
  return data.disciplines.lists[$("unified-discipline").value];
}

function renderUnifiedPlayer(player) {
  const target = $("unified-player");
  target.replaceChildren();
  if (!player) return;
  const profiles = selectedDiscipline().profiles[player.player_id];
  const primary = profiles.find((r) => r.role === player.primary_role);
  const weights = data.role_profiles.weights[player.primary_role];
  const head = element("div", undefined, "analysis-head");
  head.append(element("h3", player.name), element("p", `Rank ${player.rank} · Player ID ${player.player_id} · ${ROLE_TITLES[player.primary_role]}`, "note"));
  target.append(head);
  const bridge = element("figure", undefined, "contribution");
  const chart = element("div", undefined, "bridge");
  for (const [label, left, width, end] of [
    ["Neutral reference", 0, 50, 50],
    ["Primary evidence adjustment", Math.min(50, player.primary_adjusted), Math.abs(player.primary_adjusted - 50), player.primary_adjusted],
    ["Secondary credit", player.primary_adjusted, Math.min(player.secondary_credit, 100-player.primary_adjusted), player.score],
  ]) {
    const row = element("div", undefined, "bridge-row");
    const track = element("div", undefined, "bridge-track");
    const line = element("span");
    line.style.left = `${left}%`;
    line.style.width = `${width}%`;
    track.append(line);
    row.append(element("span", label), track, element("strong", fmt(end, 3)));
    chart.append(row);
  }
  bridge.append(chart, element("figcaption", "Score contributions on a 0–100 reference scale. Labels show the running total. Source: unified score ledger and equations (1)–(3)."));
  target.append(bridge);
  const details = element("details");
  details.open = true;
  details.append(element("summary", "Trace the calculation"),
    element("p", `Role assignment: ${player.primary_balls} scored balls, ${player.primary_matches} scored matches and ${fmt(player.primary_share * 100, 1)}% of this player's scored opportunities within this discipline in their primary role.`),
    table(["Primary metric", "Signed z", "Weight", "Weighted contribution"],
      ["Runs", "Boundaries", "Dismissals or wickets"].map((label, i) =>
        [label, fmt(primary.signed_z[i], 4), `${fmt(weights[i]*100, 0)}%`, fmt(weights[i]*primary.signed_z[i], 4)])),
    element("p", `The sum is ${fmt(primary.unshrunk, 6)}. The role-normalised z is ${fmt(primary.role_z, 6)}, giving Q = ${fmt(player.primary_reference, 6)}. With R = ${fmt(player.primary_retention, 6)}, S = 50 + R(Q − 50) = ${fmt(player.primary_adjusted, 6)}.`),
    element("p", player.secondary_role ? `${ROLE_TITLES[player.secondary_role]} supplies ${fmt(player.secondary_credit, 6)} points from ${player.secondary_balls} balls and a supported-role score of ${fmt(player.secondary_adjusted, 6)}. Unified index: ${fmt(player.score, 6)}.`
      : `No secondary role met the support gate. Unified index: ${fmt(player.score, 6)}.`));
  target.append(details);
  const contextual = element("details");
  contextual.append(element("summary", "Compare roles, geography and pressure"),
    table(["Role", "Balls", "India balls", "Adjusted /100", "Pressure run lift", "Historical top-ten resample share"],
      profiles.map(r => [ROLE_TITLES[r.role], r.balls, r.india_balls, fmt(r.adjusted, 3),
        r.pressure_rate_lift === null ? "Insufficient support" : fmt(r.pressure_rate_lift, 4),
        r.bootstrap_top10_share === null ? "—" : `${fmt(r.bootstrap_top10_share * 100, 1)}%`])),
    element("p", "Pressure run lift is residual runs per opportunity in pressure minus ordinary. A negative conceded-run lift favours bowlers. The count gate is 30 in both contexts. These columns provide context for the index."),
    table(["Primary role venue group", "Scored balls", "Run residual per opportunity"],
      Object.entries(primary.geography).map(([region, r]) => [region, r.balls, r.run_residual === null ? "—" : fmt(r.run_residual, 4)])));
  target.append(contextual);
  const trajectory = element("details");
  trajectory.append(element("summary", "Annual evidence in the primary role"),
    table(["Year", "Observed balls", "Scored balls", primary.role.endsWith("_bowler") ? "Economy" : "Strike rate", "Runs above expectation / ball"],
      primary.annual.map(r => [r.year, r.balls, r.scored_balls, r.raw_rate === null ? "—" : fmt(r.raw_rate, 2),
        r.run_residual === null ? "Warm-up / no scored balls" : fmt(r.run_residual, 4)])));
  if (primary.trend) trajectory.append(element("p", `Ball-weighted annual slope: ${fmt(primary.trend.annual_rate_residual_slope, 4)} runs per ball per year. More negative slopes favour bowlers.`));
  target.append(trajectory);
}

function renderUnified() {
  const model = selectedDiscipline();
  const query = $("unified-search").value.trim().toLowerCase();
  const matches = (r) => `${r.name} ${r.player_id}`.toLowerCase().includes(query);
  const rows = query ? model.ranked.filter(matches).slice(0, 25) : model.top10;
  $("unified-coverage").textContent = `Historical contextual index · ${model.eligible} of ${model.observed} observed players qualify · ${model.pressure_submission_overlap}/10 shared with the archived Round 1 pressure list.`;
  const rankTable = table(["Rank", "Player", "Primary role", "Scored balls", "Index / 100"], rows.map(r =>
    [r.rank, r.name, ROLE_TITLES[r.primary_role], r.primary_balls, fmt(r.score, 3)]));
  const body = rankTable.querySelector("tbody");
  rows.forEach((r, i) => {
    const button = element("button", r.name, "player-link");
    button.type = "button";
    button.title = "Open the role assignment, formula and source counts";
    button.addEventListener("click", () => renderUnifiedPlayer(r));
    body.rows[i].cells[1].replaceChildren(button);
  });
  const output = $("unified-table");
  output.replaceChildren(rows.length ? rankTable : element("p", "No ranked players match this search."));
  const unranked = query ? model.unranked.filter(matches).slice(0, 25) : [];
  if (unranked.length) {
    output.append(element("h3", "Observed players below the evidence gate"),
      table(["Player", "ID", "Primary role", "Scored balls", "Scored matches", "Reason"],
        unranked.map(r => [r.name, r.player_id, ROLE_TITLES[r.primary_role], r.primary_balls, r.primary_matches, r.reason])));
  }
  renderUnifiedPlayer(rows[0]);
  const methodLabels = {primary_only:"No secondary credit", india_1_5:"India observations × 1.5", residualised_boundary:"Residualised boundary metric"};
  const names = new Map(model.ranked.map((r) => [r.player_id, r.name]));
  $("unified-sensitivity").replaceChildren(table(["Alternative", "Top-ten overlap", "Largest eligible rank shift", "Entered", "Left", "Leader"],
    Object.entries(methodLabels).map(([key, description]) => {
      const r = model.methods[key];
      return [description, `${r.overlap}/10`, r.max_rank_shift, r.entered.join(", ") || "—",
        r.left.join(", ") || "—", names.get(r.top10_ids[0])];
    })));
}

function renderFigure() {
  const index = Number($("figure-select").value);
  const [path, title, note, source, anchor] = FIGURES[index];
  const img = $("figure-image");
  img.src = "figures/" + path;
  img.alt = title;
  const link = element("a", source);
  link.href = "library.html#" + anchor;
  $("figure-caption").replaceChildren(element("strong", `Figure ${index + 1}. ${title}. `),
    document.createTextNode(note + " Source: "), link);
}

if (globalThis.paprfEvidence?.disciplines) {
  document.querySelectorAll("[data-tex]").forEach((node) => {
    if (globalThis.katex) globalThis.katex.render(node.dataset.tex, node, {displayMode: true, throwOnError: false});
  });
  $("unified-search").addEventListener("input", renderUnified);
  $("unified-discipline").addEventListener("change", () => {
    $("unified-search").value = "";
    renderUnified();
  });
  renderUnified();
  FIGURES.forEach((record, i) => {
    const opt = element("option", record[1]);
    opt.value = i;
    $("figure-select").append(opt);
  });
  $("figure-select").addEventListener("change", renderFigure);
  renderFigure();
  for (const [term, definition, example] of GLOSSARY) {
    const entry = element("details");
    entry.append(element("summary"), element("p", definition), element("p", example, "note"));
    entry.firstElementChild.append(describe(term, definition));
    $("metric-glossary").append(entry);
  }
}
