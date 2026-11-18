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
}
