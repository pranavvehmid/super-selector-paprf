"use strict";

const atlasPages = {
  home: ["Home", "home", "home-findings"],
  dataset: ["Dataset Explorer", "dataset"],
  framework: ["Mathematical Framework", "pipeline", "method", "glossary"],
  pressure: ["Pressure Analysis", "pressure", "rankings"],
  players: ["Player Performance", "unified"],
  roles: ["Role-Based Leaderboards", "role-profiles"],
  "top-ten": ["Ultimate Top 10", "unified"],
  compare: ["Comparative Analysis", "compare-players", "figures"],
  validation: ["Model Validation", "research"],
  documentation: ["Research Documentation", "documents", "progress"],
  about: ["About", "about"],
};

const atlasSections = [...document.querySelectorAll("main > section")];
const unifiedHeading = $("unified").querySelector("h2");
const atlasNav = [...document.querySelectorAll("#atlas-nav [data-route]")];

function showAtlasPage(route, anchor = "", focus = false) {
  const safe = Object.hasOwn(atlasPages, route) ? route : "home";
  const [title, ...sections] = atlasPages[safe];
  atlasSections.forEach((section) => { section.hidden = !sections.includes(section.id); });
  atlasNav.forEach((a) => {
    if (a.dataset.route === safe) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  unifiedHeading.textContent = safe === "players" ? "Searchable player profiles" : "Ultimate top ten by discipline";
  document.title = `${title} · PAPRF research atlas`;
  const target = anchor && sections.includes(anchor) ? document.getElementById(anchor) : document.getElementById(sections[0]);
  if (focus) {
    const heading = target.querySelector("h1,h2");
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); }
  }
  if (anchor && anchor !== sections[0]) target.scrollIntoView({behavior: "instant"});
  else window.scrollTo({top: 0, behavior: "instant"});
}

function atlasRouteFromLocation() {
  const url = new URL(location.href);
  const anchor = url.hash.slice(1);
  const route = url.searchParams.get("page") || (anchor === "unified" ? "top-ten" :
    Object.keys(atlasPages).find(key => atlasPages[key].slice(1).includes(anchor))) || "home";
  return [route, anchor];
}

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const url = new URL(link.href);
  if (url.origin !== location.origin || url.pathname !== location.pathname) return;
  const anchor = url.hash.slice(1);
  const route = link.dataset.route || url.searchParams.get("page") ||
    (anchor === "unified" ? "top-ten" : Object.keys(atlasPages).find(key => atlasPages[key].slice(1).includes(anchor)));
  if (!route || !Object.hasOwn(atlasPages, route)) return;
  event.preventDefault();
  const key = `?page=${encodeURIComponent(route)}${anchor ? "#" + anchor : ""}`;
  if (location.search + location.hash !== key) history.pushState({}, "", key);
  showAtlasPage(route, anchor, true);
});
window.addEventListener("popstate", () => showAtlasPage(...atlasRouteFromLocation()));
showAtlasPage(...atlasRouteFromLocation());

function pressureCurve() {
  const balls = +$("curve-balls").value;
  const wickets = +$("curve-wickets").value;
  $("curve-balls-value").value = balls;
  $("curve-wickets-value").value = wickets;
  const canvas = $("pressure-curve");
  const ctx = canvas.getContext("2d");
  const css = getComputedStyle(document.documentElement);
  const ink = css.getPropertyValue("--ink").trim();
  const accent = css.getPropertyValue("--accent").trim();
  const grid = css.getPropertyValue("--line").trim();
  const [left, right, top, bottom] = [76, 960, 22, 258];
  const x = (requiredRate) => left + (right-left) * requiredRate / 18;
  const y = (pressure) => bottom - (bottom-top) * pressure;
  const p = (rate) => .55*Math.min(1,Math.max(0,(rate-7)/5)) + .25*wickets/10 + .20*balls/120;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = "17px system-ui";
  ctx.strokeStyle = grid;
  ctx.fillStyle = ink;
  for (const band of [0, .4, .65, 1]) {
    ctx.setLineDash(band === 0 || band === 1 ? [] : [6, 5]);
    ctx.beginPath(); ctx.moveTo(left,y(band)); ctx.lineTo(right,y(band)); ctx.stroke();
    ctx.fillText(fmt(band, 2), 22, y(band)+5);
  }
  ctx.setLineDash([]);
  for (const rate of [0, 3, 6, 9, 12, 15, 18]) ctx.fillText(String(rate), x(rate)-6, bottom+24);
  ctx.fillText("Required runs per over", 410, bottom+50);
  ctx.fillText("Pre-delivery index", left, 17);
  ctx.strokeStyle = accent;
  ctx.lineWidth = 3;
  ctx.beginPath();
  for (const [i, rate] of [0,7,12,18].entries()) {
    if (i === 0) ctx.moveTo(x(rate),y(p(rate)));
    else ctx.lineTo(x(rate),y(p(rate)));
  }
  ctx.stroke();
  ctx.lineWidth = 1;
  $("pressure-curve-alt").textContent = `At ${balls} balls and ${wickets} wickets lost, the index is ${fmt(p(7),3)} at seven runs per over and ${fmt(p(12),3)} at twelve. The required-rate component caps at twelve. Dashed lines mark the .40 and .65 band boundaries. Source: implemented chase-pressure equation.`;
}
for (const control of ["curve-balls","curve-wickets"]) $(control).addEventListener("input", pressureCurve);
new MutationObserver(pressureCurve).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});
pressureCurve();

function datasetView() {
  const file = data.datasets[$("dataset-file").value];
  const filtered = Object.entries(file.blank_counts).filter(([, n]) => $("dataset-fields").value !== "missing" || n > 0);
  $("dataset-missing").replaceChildren(element("p", `${number.format(file.row_count)} rows · ${file.column_count} fields · ${file.exact_duplicate_row_count} exact duplicate rows`),
    filtered.length ? table(["Field", "Blank rows", "Share"], filtered.map(([field, n]) =>
      [field, number.format(n), file.row_count ? `${fmt(100*n/file.row_count, 2)}%` : "—"])) : element("p", "No blank fields recorded."));
}

function comparisonOptions() {
  const rows = data.disciplines.lists[$("compare-discipline").value].ranked;
  for (const [offset, id] of ["compare-a", "compare-b"].entries()) {
    $(id).replaceChildren(...rows.map((r) => {
      const option = element("option", `${r.rank}. ${r.name}`);
      option.value = r.player_id;
      return option;
    }));
    $(id).selectedIndex = offset;
  }
  comparisonView();
}

function comparisonView() {
  const model = data.disciplines.lists[$("compare-discipline").value];
  const subjects = ["compare-a", "compare-b"].map(id => model.ranked.find(r => r.player_id === $(id).value));
  if (subjects.some(r => !r)) return;
  const partition = [["Primary role", r => ROLE_TITLES[r.primary_role]], ["Primary opportunities", r => r.primary_balls],
    ["Primary matches", r => r.primary_matches], ["Observed role reference", r => fmt(r.primary_reference, 3)],
    ["Evidence-adjusted primary", r => fmt(r.primary_adjusted, 3)], ["Secondary credit", r => fmt(r.secondary_credit, 3)],
    ["Final contextual index", r => fmt(r.score, 3)]];
  const annual = (r) => model.profiles[r.player_id].find(p => p.role === r.primary_role).annual;
  const recent = subjects.map(r => annual(r).at(-1));
  const lines = partition.map(([label, get]) => [label, ...subjects.map(get)]);
  lines.push(["Latest conventional annual rate", ...recent.map(x => x?.raw_rate == null ? "—" : `${fmt(x.raw_rate, 2)} (${x.year})`)]);
  lines.push(["Latest annual observed balls", ...recent.map(x => x?.balls ?? "—")]);
  $("compare-matrix").replaceChildren(table(["Measure", ...subjects.map(r => r.name)], lines),
    element("p", "Conventional rate is batting strike rate (runs per 100 balls) or bowling economy (runs per six legal balls). The reported calendar year may differ between players.", "note"));
}

for (const tag of document.querySelectorAll("[data-author]")) tag.textContent = paprfAuthor[tag.dataset.author];
for (const [key, label] of [["email", "Public email"], ["linkedin", "LinkedIn"], ["github", "GitHub"], ["repository", "Project repository"]]) {
  const value = paprfAuthor[key];
  if (!value || value.startsWith("[")) continue;
  const a = document.createElement("a");
  a.textContent = label;
  a.href = key === "email" ? `mailto:${value}` : value;
  const p = document.createElement("p"); p.append(a); $("author-links").append(p);
}
if (globalThis.paprfEvidence?.datasets) {
  $("dataset-summary").append(table(["Scope", "Count"], [
    ["Source delivery events", number.format(data.datasets["ball_by_ball.csv"].row_count)],
    ["Retained delivery events", number.format(data.audit.delivery_rows)],
    ["Retained matches", number.format(data.audit.distinct_match_ids)],
  ]));
  for (const filename of Object.keys(data.datasets)) {
    const opt = element("option", filename); opt.value = filename; $("dataset-file").append(opt);
  }
  $("dataset-file").addEventListener("change", datasetView);
  $("dataset-fields").addEventListener("change", datasetView);
  datasetView();
  $("compare-discipline").addEventListener("change", comparisonOptions);
  for (const id of ["compare-a", "compare-b"]) $(id).addEventListener("change", comparisonView);
  comparisonOptions();
  const {batter, bowler} = data.disciplines.lists;
  $("home-preview").append(table(["Rank", "Contextual batter", "Index / 100", "Contextual bowler", "Index / 100"],
    batter.top10.slice(0, 3).map((r, i) => [r.rank, r.name, fmt(r.score, 3), bowler.top10[i].name, fmt(bowler.top10[i].score, 3)])));
  $("publication-run").textContent = `Evidence run ${data.publication.run_id} · ${data.publication.independently_rebuilt_files} rebuilt artifacts verified`;
  $("publication-pdf").closest("li").hidden = !data.publication.pdf_available;
}
