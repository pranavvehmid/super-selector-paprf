"use strict";

const $ = (id) => document.getElementById(id);
const data = globalThis.paprfEvidence;
const number = new Intl.NumberFormat("en");
const fmt = (value, digits = 2) => Number(value).toFixed(digits);
const metricNames = {batter: ["Runs per ball", "Dot rate", "Dismissal rate"], bowler: ["Economy", "Dot rate", "Wicket rate"]};
let selected;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function tile(label, value, className) {
  const node = element("div", undefined, className);
  node.append(element("strong", value), element("span", label));
  return node;
}

function table(headers, records) {
  const node = element("table");
  const head = node.createTHead().insertRow();
  headers.forEach((label) => {
    const cell = element("th", label);
    cell.scope = "col";
    head.append(cell);
  });
  const body = node.createTBody();
  records.forEach((values) => {
    const row = body.insertRow();
    values.forEach((value) => { row.insertCell().textContent = value; });
  });
  const wrapper = element("div", undefined, "scroll");
  wrapper.append(node);
  return wrapper;
}

function renderDistribution() {
  const rows = data.distribution;
  const maximum = Math.max(...rows.map((r) => +r.innings_phase_deliveries));
  const countScale = $("scale").value === "count";
  $("distribution").replaceChildren();
  for (const innings of ["1", "2"]) for (const phase of ["powerplay", "middle", "death"]) {
    const label = `Innings ${innings} · ${phase}`;
    const row = element("div", undefined, "chart-row");
    const track = element("div", undefined, "track");
    rows.filter((r) => r.innings === innings && r.innings_phase === phase).forEach((r) => {
      if (+r.delivery_count === 0) return;
      const content = `${label}, ${r.pressure_band}: ${number.format(r.delivery_count)} / ${number.format(r.innings_phase_deliveries)} deliveries (${fmt(r.pct_within_innings_phase)}% within phase, ${fmt(r.pct_of_all_deliveries)}% of all deliveries).`;
      const segment = element("button", undefined, `segment ${r.pressure_band}`);
      segment.type = "button";
      segment.style.width = `${countScale ? 100 * r.delivery_count / maximum : r.pct_within_innings_phase}%`;
      segment.setAttribute("aria-label", content);
      segment.title = content;
      for (const event of ["click", "focus", "pointerenter"]) {
        segment.addEventListener(event, () => { $("pressure-detail").textContent = content; });
      }
      track.append(segment);
    });
    row.append(element("span", label), track);
    $("distribution").append(row);
  }
}

function renderPlayer(r, role) {
  const panel = $("player");
  panel.replaceChildren();
  if (!r) return;
  const title = element("h3", data.names[r.player_id] || r.player_id);
  const stats = element("div", undefined, "player-grid");
  stats.append(tile("Raw signal", fmt(r.raw_signal, 6)), tile("Shrinkage factor", fmt(r.shrinkage, 6)), tile("Final score", fmt(r.score, 6)));
  panel.append(title, element("p", `Player ID ${r.player_id} · rank ${r.rank} in this scenario`, "note"), stats);
  panel.append(table(["Scenario bucket", "Runs", "Balls", "Dots", role === "batter" ? "Dismissals" : "Wickets", "Matches"],
    ["ordinary", "pressure"].map((key) => [key, ...["runs", "balls", "dots", "events", "matches"].map((m) => r[`${key}_${m}`])])));
  panel.append(table(["Metric", "Pressure − ordinary", "Signed z-score"], metricNames[role].map((name, i) => [
    name, fmt(r[`delta_${i + 1}`], 6), fmt(r[`signed_z_${i + 1}`], 6)
  ])));
  const bands = data.contexts[role].filter((row) => row.player_id === r.player_id);
  if (bands.length) {
    const columns = role === "batter" ? ["runs", "balls_faced", "dot_balls", "dismissals"] : ["runs_conceded", "legal_balls", "dot_balls", "wickets"];
    panel.append(element("h4", "Original v1 pressure-band totals"),
      table(["Band", "Runs", "Balls", "Dots", role === "batter" ? "Dismissal matches" : "Wickets"],
        bands.map((row) => [row.pressure_band, ...columns.map((col) => row[col])])));
  }
}

function renderRankings() {
  const role = $("role").value;
  const scenario = $("scenario").value;
  const limit = $("limit").value;
  const query = $("search").value.trim().toLowerCase();
  const summary = data.model.roles[role].scenarios[scenario];
  const replay = data.ledger.filter((r) => r.role === role && r.scenario === "v1_equal");
  const v1Ranks = new Map(replay.map((r) => [r.player_id, r.rank]));
  const matching = data.ledger.filter((r) => r.role === role && r.scenario === scenario &&
    (!query || `${data.names[r.player_id] || ""} ${r.player_id}`.toLowerCase().includes(query)));
  const shown = limit === "all" ? matching : matching.slice(0, Number(limit));
  if (!shown.some((r) => r.player_id === selected)) selected = shown[0]?.player_id;
  const promoted = data.model.exposure.filter((r) => r.role === role && r.bucket === "promoted").reduce((sum, r) => sum + r.deliveries, 0);
  $("scenario-summary").textContent = `${scenario === "v1_equal" ? "Frozen ranking" : "Exploratory scenario"} · ${summary.eligible} eligible · ${summary.overlap_of_10}/10 shared with v1 · weights ${summary.weight_parts.join(":")}${scenario === "role_rule_equal" ? ` · ${number.format(promoted)} additional pressure events` : ""} · ${matching.length} matching rows`;
  const tbody = $("rank-rows");
  tbody.replaceChildren();
  shown.forEach((r) => {
    const tr = tbody.insertRow();
    tr.insertCell().textContent = r.rank;
    const button = element("button", data.names[r.player_id] || r.player_id, "player-link");
    button.setAttribute("aria-pressed", String(selected === r.player_id));
    button.addEventListener("click", () => {
      selected = r.player_id;
      for (const other of tbody.querySelectorAll("button")) other.setAttribute("aria-pressed", String(other === button));
      renderPlayer(r, role);
    });
    tr.insertCell().append(button);
    [fmt(r.score, 6), r.pressure_balls, r.pressure_matches, v1Ranks.get(r.player_id) || "—"].forEach((v) => {
      tr.insertCell().textContent = v;
    });
  });
  if (!shown.length) {
    const cell = tbody.insertRow().insertCell();
    cell.colSpan = 6;
    cell.textContent = "No eligible players match this search.";
  }
  renderPlayer(shown.find((r) => r.player_id === selected), role);
}

function renderResearch() {
  const role = $("research-role").value;
  const reliability = data.split_reliability;
  const range = (items) => `${fmt(items[1], 3)} (${fmt(items[0], 3)} to ${fmt(items[2], 3)})`;
  $("research-reliability").replaceChildren(table(
    ["Per-context gate", "Median common players", "Observed ρ (p10–p90)", "Shuffle ρ (p10–p90)", "Above own shuffle p90"],
    Object.entries(reliability.roles[role]).map(([gate, r]) => [
      gate === "primary" ? "30 balls / 3 matches" : "60 balls / 6 matches",
      r.summary_p10_p50_p90.common_players[1], range(r.summary_p10_p50_p90.composite_rho),
      range(r.shuffle_rho_p10_p50_p90), `${r.splits_above_own_null_p90}/${reliability.splits}`,
    ])));
  $("research-forward").replaceChildren(table(
    ["Test period", "Common players", "v4 p10 ρ", "v4 point ρ", "Pooled ρ", "Volume ρ", "v4 assessable", "Chance overlap"],
    data.forward.folds.map((fold) => {
      const stats = fold.roles[role];
      const scores = ["v4_p10", "v4_point", "pooled_point", "pressure_volume"].map((key) => {
        const rho = stats.predictors[key].spearman;
        return rho === null ? "—" : fmt(rho, 3);
      });
      return [`${fold.test_start} to ${fold.test_end}`, stats.common_players, ...scores,
        `${stats.predictors.v4_p10.original_top10_assessable}/10`, fmt(stats.chance_top10_overlap)];
    })));
  if ($("research-version").value === "v4") {
    const run = data.regularised;
    const stats = run.roles[role];
    $("research-note").textContent = `PAPRF v4 · ${stats.eligible_bootstrap} eligible · ${run.draws} draws · ${stats.shared_with_v3}/10 shared with v3 · temporal Spearman ${fmt(stats.temporal.spearman, 3)}`;
    $("research-top").replaceChildren(table(["v4 rank", "Player", "v3 top-10 rank", "Point rank", "v4 score (p10)", "p90", "Valid draws"],
      stats.top10.map((r) => [r.research_rank, r.name, r.v3_top10_rank ?? "—", r.point_rank,
        fmt(r.p10, 6), fmt(r.p90, 6), `${r.valid_draws}/${run.draws}`])));
    $("research-movements").replaceChildren(table(["Player", "v3 rank", "Reason"],
      stats.v3_departures.map((r) => [r.name, r.v3_rank, r.reason])));
    const labels = {primary:"Primary",lambda6:"Regularisation 6",lambda24:"Regularisation 24",
      uncapped:"Uncapped components",no_event_component:"Without dismissal / wicket component",
      historical_dismissals:"Historical dismissal attribution"};
    $("research-thresholds").replaceChildren(table(["Scenario", "Point eligible", "Shared with primary point top ten"],
      Object.entries(stats.tests).map(([key, item]) => [labels[key], item.eligible, `${item.overlap}/10`])));
    return;
  }
  if ($("research-version").value === "v3") {
    const run = data.granularity;
    const stats = run.designs.phase_family_v3[role];
    $("research-note").textContent = `PAPRF v3 · ${stats.bootstrap_eligible} eligible · ${run.draws} draws · ${stats.shared_with_v2}/10 shared with v2`;
    $("research-top").replaceChildren(table(["v3 rank", "Player", "v2 top-10 rank", "Matched point rank", "v3 score (p10)", "p90", "Valid draws"],
      stats.top10.map((r) => [r.research_rank, r.name, r.v2_rank ?? "—", r.rank,
        fmt(r.p10, 6), fmt(r.p90, 6), `${r.valid_draws}/${run.draws}`])));
    $("research-movements").replaceChildren(table(["Player", "v2 rank", "Reason"],
      stats.v2_departures.map((r) => [r.name, r.v2_rank, r.reason])));
    const labels = {fine_v2: "Fine v2", phase_family_v3: "Phase + family v3", innings_phase: "Innings + phase"};
    $("research-thresholds").replaceChildren(table(["Design", "Matched", "Bootstrap eligible", "Common across time", "Spearman ρ"],
      Object.entries(run.designs).map(([key, roles]) => [labels[key], roles[role].matched_eligible,
        roles[role].bootstrap_eligible, roles[role].temporal.common_eligible, fmt(roles[role].temporal.spearman, 3)])));
    return;
  }
  const run = data.research;
  const stats = run.roles[role];
  const statuses = {
    outside_top10: "Qualified outside the top ten",
    insufficient_resample_support: "Fewer than 95% valid draws",
    insufficient_matched_support: "Insufficient matched opportunities or matches",
  };
  $("research-note").textContent = `PAPRF v2 · ${stats.resample_qualified} eligible after resampling · ${run.draws} draws · ${stats.shared_with_v1.length}/10 shared with frozen v1`;
  $("research-top").replaceChildren(table(["v2 rank", "Player", "v1 top-10 rank", "Matched point rank", "v2 score (p10)", "p90", "Valid draws"],
    stats.top10.map((r) => [r.research_rank, r.name, r.v1_frozen_rank ?? "—", r.matched_point_rank,
      fmt(r.p10, 6), fmt(r.p90, 6), `${r.valid_draws}/${run.draws}`])));
  $("research-movements").replaceChildren(table(["Player", "v1 rank", "v2 rank", "Status"],
    stats.left_v1_top10.map((r) => [r.name, r.rank, r.research_rank ?? "—", statuses[r.status]])));
  $("research-thresholds").replaceChildren(table(["Balls per cell and context", "Matched eligible", "Point top-ten overlap with 12 balls"],
    Object.entries(stats.threshold_sensitivity).map(([threshold, r]) => [threshold, r.eligible, `${r.shared_with_cutoff_12}/10`])));
}

function renderRoleProfiles() {
  const stats = data.role_profiles.roles[$("profile-role").value];
  const weights = data.role_profiles.weights[$("profile-role").value];
  $("profile-summary").textContent = `${stats.primary.eligible} eligible · weights ${weights.map((w) => fmt(w * 100, 0) + "%").join(" / ")} · India sensitivity ${stats.india_1_5.shared_with_primary}/10 · equal weights ${stats.equal_weights.shared_with_primary}/10 · boundary residualisation ${stats.orthogonal_boundary.shared_with_primary}/10`;
  const batting = $("profile-role").value.endsWith("_bowler") === false;
  $("profile-results").replaceChildren(table(["Rank", "Player", "Role score", "Scored balls", "India balls",
    batting ? "Explosiveness" : "Legal-ball runs above expectation"],
    stats.top10.map((row) => [row.rank, row.name, fmt(row.score, 6), row.scored_balls, row.india_scored_balls,
      fmt(batting ? row.explosiveness : row.rate_residual, 4)])));
}

if (!data) {
  $("load-error").hidden = false;
} else {
  const bands = data.audit.band_totals;
  const percentage = 100 * (bands.elevated + bands.high) / data.audit.delivery_rows;
  $("summary").append(tile("Validated matches", number.format(data.audit.distinct_match_ids), "stat"),
    tile("Delivery events", number.format(data.audit.delivery_rows), "stat"),
    tile("Eligible batters", number.format(data.model.roles.batter.scenarios.v1_equal.eligible), "stat"),
    tile("Eligible bowlers", number.format(data.model.roles.bowler.scenarios.v1_equal.eligible), "stat"));
  $("pressure-summary").append(tile("Ordinary events", number.format(bands.ordinary), "stat"),
    tile("Elevated events", number.format(bands.elevated), "stat"),
    tile("High-pressure events", number.format(bands.high), "stat"),
    tile("Elevated or high", `${fmt(percentage)}%`, "stat"));
  for (const role of ["batter", "bowler"]) {
    const leader = data.rankings[role][0];
    const card = element("a", undefined, "leader");
    card.href = "#rankings";
    const label = element("span", `Frozen v1 · Top ${role}`, "leader-label");
    const player = element("strong", leader.player_name);
    const score = element("span", fmt(leader.reliability_signal, 3), "leader-score");
    card.append(label, player, score);
    card.addEventListener("click", () => {
      $("role").value = role;
      $("scenario").value = "v1_equal";
      $("search").value = "";
      selected = leader.player_id;
      renderRankings();
    });
    $("featured").append(card);
  }
  $("scale").addEventListener("change", renderDistribution);
  for (const id of ["role", "scenario", "limit"]) $(id).addEventListener("change", renderRankings);
  $("search").addEventListener("input", renderRankings);
  $("research-role").addEventListener("change", renderResearch);
  $("research-version").addEventListener("change", renderResearch);
  $("profile-role").addEventListener("change", renderRoleProfiles);
  $("sensitivity").append(table(["Sensitivity check", "Batters shared with v1", "Bowlers shared with v1"],
    [...[30, 90].map((prior) => [`Shrinkage prior = ${prior} balls`,
      ...["batter", "bowler"].map((role) => `${data.robustness.roles[role].prior_top10_overlap_with_60[prior]}/10`)]),
    ["High pressure only", ...["batter", "bowler"].map((role) => `${data.robustness.roles[role].high_only_top10_overlap_with_base}/10`)]]));
  const contextAudit = data.context_audit;
  $("context-audit").append(element("p",
    `Match-date split: ${contextAudit.split_date} · ${contextAudit.early_matches} earlier matches · ${contextAudit.late_matches} later matches`),
    table(["Role", "Matched eligible", "Frozen top 10 still eligible", "Matched top 10 overlap", "Eligible in both periods", "Spearman ρ"],
      ["batter", "bowler"].map((role) => {
        const audit = contextAudit.roles[role];
        return [role, audit.scenarios.matched.eligible, `${audit.frozen_ids_still_eligible_matched.length}/10`,
          `${audit.matched_overlap_ids.length}/10`, audit.common_period_eligible_ids.length,
          audit.spearman === null ? "Unavailable" : fmt(audit.spearman, 3)];
      })));
  renderDistribution();
  renderRankings();
  renderResearch();
  renderRoleProfiles();
}
