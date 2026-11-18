"""Build chronological context/opposition benchmarks and role leaderboards."""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import TABLES, midranks, save
from run_paprf_phase2 import INPUT, ROOT, digest, rows

WARMUP_END = "2023-04-03"
WEIGHTS = {
    "opener": (.45, .30, .25), "top_order": (.40, .20, .40),
    "middle_lower": (.40, .25, .35), "late_entrant": (.50, .35, .15),
    "powerplay_bowler": (.35, .20, .45), "middle_bowler": (.35, .20, .45),
    "death_bowler": (.50, .25, .25),
}
METRICS = ("runs", "boundary", "dots", "event", "six")
PRIOR = np.array([1., .15, .35, .04, .05])
SELECT = [0, 1, 3]


@dataclass
class Pool:
    n: int = 0
    total: np.ndarray = field(default_factory=lambda: np.zeros(5))

    def add(self, value):
        self.n += 1
        self.total += value

    def estimate(self, prior, k):
        return (self.total + k * prior) / (self.n + k)


@dataclass
class Summary:
    raw: Pool = field(default_factory=Pool)
    scored: Pool = field(default_factory=Pool)
    matches: set = field(default_factory=set)
    innings: set = field(default_factory=set)
    scored_matches: set = field(default_factory=set)
    illegal_runs: int = 0

    def add(self, actual, residual, match, innings):
        self.raw.add(actual)
        self.matches.add(match)
        self.innings.add((match, innings))
        if residual is not None:
            self.scored.add(residual)
            self.scored_matches.add(match)


def batting_role(order, entered):
    if order <= 2:
        return "opener"
    if order <= 4:
        return "top_order"
    return "late_entrant" if entered == "death" else "middle_lower"


def make_events(data, metadata, audit):
    seen = {}
    names = {}
    for r in data:
        day, family, india = metadata[r["match_id"]]
        match, innings, phase = r["match_id"], r["innings"], r["innings_phase"]
        striker, bowler = r["striker_id"], r["bowler_id"]
        names[striker] = r["striker_name"]
        names[bowler] = r["bowler_name"]
        for player in (striker, r["non_striker_id"]):
            seen.setdefault((match, innings, player), phase)
        bat_role = batting_role(int(r["batting_order"]), seen[match, innings, striker])
        runs = int(r["batter_runs_attributed"])
        four = r["is_four"] == "true"
        six = r["is_six"] == "true"
        boundary = (four and runs == 4) or (six and runs == 6)
        if r["batter_ball_faced"] == "true":
            audit["four_flag_disagreements"] += four != (runs == 4)
            audit["six_flag_disagreements"] += six != (runs == 6)
            value = (runs, boundary, r["batter_dot"] == "true",
                     r["is_wicket"] == "true" and r["dismissed_player_id"] == striker, six and runs == 6)
            yield day, family, india, match, innings, phase, r["pressure_band"], "batter", bat_role, striker, bowler, r["bowling_team_id"], r["pace_or_spin"], value, names[striker]
        if r["bowler_legal_ball"] == "true":
            value = (int(r["bowler_runs_conceded"]), boundary, r["bowler_dot"] == "true",
                     r["bowler_wicket"] == "true", six and runs == 6)
        else:
            value = int(r["bowler_runs_conceded"])
            if not value:
                continue
        yield day, family, india, match, innings, phase, r["pressure_band"], "bowler", phase + "_bowler", bowler, striker, r["batting_team_id"], r["batting_type"], value, names[bowler]


def calculate(data, metadata):
    overall, parents, contexts, people, teams = [defaultdict(Pool) for _ in range(5)]
    profiles, audit, losses, dates, names = defaultdict(Summary), Counter(), defaultdict(Pool), defaultdict(list), {}
    for event in make_events(data, metadata, audit):
        dates[event[0]].append(event)
    tier_counts = Counter()
    for date, events in sorted(dates.items()):
        updates = []
        for day, family, india, match, innings, phase, band, discipline, role, player, opponent, team, style, v, name in events:
            names[player] = name
            region = "India" if india else "Outside India"
            scope = "pressure" if band != "ordinary" else "ordinary"
            base_dimensions = [("overall", "all"), ("year", day[:4]), ("venue_country_group", region), ("pressure", scope),
                               ("phase", phase), ("opposition_style", style), ("competition_family", family)]
            if isinstance(v, int):
                for dimension, group in base_dimensions:
                    profiles[discipline, role, player, dimension, group].illegal_runs += v
                continue
            if discipline == "bowler" and v[0] > 8:
                audit["legal_bowling_runs_above_clip"] += 1
            actual = np.asarray(v, dtype=float)
            parent = (discipline, role, phase, family)
            context = parent + (innings, india, band, style)
            context_mean = contexts[context].estimate(parents[parent].estimate(
                overall[discipline].estimate(PRIOR, 120), 120), 120)
            person = people[discipline, opponent]
            individual = person.estimate(0, 120)
            tier_signal = (-1 if discipline == "batter" else 1) * individual[0]
            tier = ("unknown" if person.n < 120 else "strong" if tier_signal >= .1 else
                    "weaker" if tier_signal <= -.1 else "average")
            predicted = np.clip(context_mean + .75 * individual + .25 * teams[discipline, family, team].estimate(0, 360),
                                0, [6 if discipline == "batter" else 8, 1, 1, 1, 1])
            residual = None if day < WARMUP_END else actual - predicted
            if residual is not None:
                for model, expected in (("context", context_mean), ("opposition", predicted)):
                    losses[discipline, model].add((actual - expected) ** 2)
                tier_counts[discipline, tier] += 1
            for dimension, group in base_dimensions + [("opposition_tier", tier)]:
                profiles[discipline, role, player, dimension, group].add(actual, residual, match, innings)
            updates.append((discipline, parent, context, opponent, family, team, actual, actual - context_mean))
        for discipline, parent, context, opponent, family, team, actual, residual in updates:
            overall[discipline].add(actual)
            parents[parent].add(actual)
            contexts[context].add(actual)
            people[discipline, opponent].add(residual)
            teams[discipline, family, team].add(residual)
    return profiles, names, audit, losses, tier_counts


def split_row(key, profile, names):
    discipline, role, player, dimension, group = key
    n = profile.raw.n
    raw = profile.raw.total
    factor = 100 if discipline == "batter" else 6
    return dict(discipline=discipline, role=role, player_id=player, player_name=names[player], dimension=dimension,
                group=group, balls=n, matches=len(profile.matches), innings=len(profile.innings), scored_balls=profile.scored.n,
                scored_matches=len(profile.scored_matches), runs=int(raw[0]) + profile.illegal_runs,
                illegal_conceded_runs=profile.illegal_runs, boundaries=int(raw[1]), dots=int(raw[2]),
                events=int(raw[3]), sixes=int(raw[4]), strike_rate_or_economy=(raw[0] + profile.illegal_runs) * factor / n if n else None,
                boundary_pct=raw[1] * 100 / n if n else None, dot_pct=raw[2] * 100 / n if n else None,
                event_pct=raw[3] * 100 / n if n else None, six_pct=raw[4] * 100 / n if n else None,
                balls_per_boundary=n / raw[1] if raw[1] else None,
                **{f"{m}_residual": profile.scored.total[i] / profile.scored.n if profile.scored.n else None
                   for i, m in enumerate(METRICS)})


def rank_roles(profiles, names):
    output, top, report = [], [], {}
    for role, weights in WEIGHTS.items():
        available = [(d, pid, g) for (d, r, pid, dim, _), g in profiles.items() if r == role and dim == "overall"
                     and g.scored.n >= 60 and len(g.scored_matches) >= 6]
        discipline = available[0][0]
        role_scores = {}
        candidates = []
        for scenario, india_extra, used_weights in (("primary", 0, weights), ("india_1_5", .5, weights),
                                                       ("equal_weights", 0, (1/3, 1/3, 1/3)),
                                                       ("orthogonal_boundary", 0, weights)):
            adjusted = []
            for _, pid, g in available:
                india = profiles.get((discipline, role, pid, "venue_country_group", "India"), Summary()).scored
                adjusted.append((g.scored.total + india_extra * india.total) / (g.scored.n + india_extra * india.n))
            metric_values = np.asarray(adjusted)[:, SELECT]
            boundary_slope = None
            if scenario == "orthogonal_boundary":
                x = metric_values[:, 0] - metric_values[:, 0].mean()
                y = metric_values[:, 1] - metric_values[:, 1].mean()
                boundary_slope = float(x @ y / (x @ x)) if x @ x else 0.0
                metric_values[:, 1] -= boundary_slope * x
            means, sds = metric_values.mean(axis=0), metric_values.std(axis=0, ddof=1)
            signs = (1, 1, -1) if discipline == "batter" else (-1, -1, 1)
            z = np.clip(np.divide(metric_values - means, sds, out=np.zeros_like(metric_values), where=sds > 0) * signs, -3, 3)
            ranks = []
            for i, (_, pid, g) in enumerate(available):
                n = g.scored.n
                w = n / (n + 120)
                score = round(float(z[i] @ used_weights) * w, 6)
                ordinary = profiles.get((discipline, role, pid, "pressure", "ordinary"), Summary()).scored
                pressure = profiles.get((discipline, role, pid, "pressure", "pressure"), Summary()).scored
                lift = (pressure.total / pressure.n - ordinary.total / ordinary.n) if min(ordinary.n, pressure.n) >= 30 else [None] * 5
                ranks.append(dict(role=role, scenario=scenario, player_id=pid, name=names[pid], scored_balls=n,
                                  scored_matches=len(g.scored_matches), india_scored_balls=profiles.get(
                                      (discipline, role, pid, "venue_country_group", "India"), Summary()).scored.n,
                                  score=score, explosiveness=float(z[i, :2] @ (.6, .4)) * w if discipline == "batter" else None,
                                  rate_residual=metric_values[i, 0], boundary_residual=metric_values[i, 1],
                                  event_residual=metric_values[i, 2], signed_z_rate=z[i, 0], signed_z_boundary=z[i, 1],
                                  signed_z_event=z[i, 2], shrinkage=w, ordinary_balls=ordinary.n, pressure_balls=pressure.n,
                                  pressure_rate_lift=lift[0], pressure_boundary_lift=lift[1], pressure_event_lift=lift[3]))
            ranks.sort(key=lambda r: (-r["score"], int(r["player_id"])))
            for i, row in enumerate(ranks, 1):
                row["rank"] = i
            output.extend(ranks)
            ids = [r["player_id"] for r in ranks[:10]]
            role_scores[scenario] = dict(eligible=len(ranks), top10_ids=ids,
                                         means=means.tolist(), sample_sds=sds.tolist())
            if boundary_slope is not None:
                role_scores[scenario]["boundary_on_runs_slope"] = boundary_slope
            if scenario == "primary":
                top.extend(ranks[:10])
                candidates = ranks[:10]
                ranks_by_component = [midranks(column.tolist()) for column in metric_values.T]
                role_scores[scenario]["spearman_components"] = np.corrcoef(ranks_by_component).tolist()
        role_scores["top10"] = candidates
        primary = set(role_scores["primary"]["top10_ids"])
        for scenario in ("india_1_5", "equal_weights", "orthogonal_boundary"):
            role_scores[scenario]["shared_with_primary"] = len(primary & set(role_scores[scenario]["top10_ids"]))
        report[role] = role_scores
    return output, top, report


def trends(profiles, names):
    grouped = defaultdict(list)
    for (discipline, role, pid, dim, year), value in profiles.items():
        if dim == "year" and value.scored.n >= 60:
            grouped[discipline, role, pid].append((int(year), value.scored.n, value.scored.total[0] / value.scored.n))
    for (discipline, role, pid), values in sorted(grouped.items()):
        if len(values) < 3:
            continue
        x, n, y = np.array(sorted(values)).T
        xbar, ybar = np.average(x, weights=n), np.average(y, weights=n)
        slope = np.sum(n * (x-xbar) * (y-ybar)) / np.sum(n * (x-xbar)**2)
        yield dict(discipline=discipline, role=role, player_id=pid, player_name=names[pid], years=len(x),
                   scored_balls=int(sum(n)), first_year=int(min(x)), last_year=int(max(x)), annual_rate_residual_slope=slope,
                   all_year_rate_residual=ybar, recent_weighted_rate_residual=np.average(y, weights=n * 2 ** (-(2026-x)/2)))


def plot_trends(profiles, ranked, trend_rows):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    qualified = {(row["role"], row["player_id"]) for row in trend_rows}
    for role, axis in zip(("opener", "death_bowler"), axes):
        leader = next(r for r in ranked[role]["top10"] if (role, r["player_id"]) in qualified)
        discipline = "batter" if role == "opener" else "bowler"
        profile = [(int(y), value) for (d, r, pid, dim, y), value in profiles.items()
                   if (d, r, pid, dim) == (discipline, role, leader["player_id"], "year") and value.scored.n >= 60]
        points = [(y, value.scored.total[0] / value.scored.n * (1 if discipline == "batter" else -1),
                   value.scored.n) for y, value in sorted(profile)]
        years, performance, counts = zip(*points)
        axis.plot(years, performance, color="#af0067", marker="o")
        for x, y, n in points:
            axis.annotate(f"{n} balls", (x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)
        axis.axhline(0, color="#888888", linewidth=.8)
        axis.set(title=f"{leader['name']} · {role.replace('_', ' ')}", xticks=years, xlabel="Year",
                 ylabel="Runs above expected per ball" if discipline == "batter" else "Runs prevented per legal ball")
        axis.margins(y=.25)
        axis.grid(axis="y", alpha=.2)
    fig.suptitle("Scored annual trajectories · highest-ranked exemplars with three qualifying years")
    fig.savefig(ROOT / "outputs/figures/paprf_role_annual_examples.png", dpi=160)
    plt.close(fig)


def main():
    match_file, comp_file = ROOT / "data/raw/matches.csv", ROOT / "data/raw/competitions.csv"
    competitions = {r["comp_id"]: r for r in rows(comp_file)}
    metadata = {r["match_id"]: (r["match_date"], "T20I" if competitions[r["comp_id"]]["match_format"] == "T20I" else
                                           "IPL" if competitions[r["comp_id"]]["comp_name"].startswith("IPL ") else "other",
                                           r["venue_country"].casefold() == "india") for r in rows(match_file)}
    data = list(rows(INPUT))
    matches = {r["match_id"] for r in data}
    if any(metadata[m][1] == "other" for m in matches):
        raise ValueError("Unexpected competition in the retained population")
    profiles, names, audit, losses, counts = calculate(data, metadata)
    ledger, top, ranked = rank_roles(profiles, names)
    save("paprf_role_profile_splits.csv", [split_row(k, v, names) for k, v in sorted(profiles.items())])
    trend_rows = list(trends(profiles, names))
    save("paprf_role_profile_trends.csv", trend_rows)
    save("paprf_role_profile_scores.csv", ledger)
    save("../rankings/paprf_contextual_role_top10_v1.csv", top)
    stats = dict(input_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in (INPUT, match_file, comp_file)},
                 matches=len(matches), warmup_matches=sum(metadata[m][0] < WARMUP_END for m in matches),
                 scored_period_start=WARMUP_END, audit=dict(audit), weights=WEIGHTS,
                 opponent_tier_counts=[dict(discipline=d, tier=t, balls=n) for (d, t), n in sorted(counts.items())],
                 errors=[dict(discipline=d, model=m, balls=v.n, mse=dict(zip(METRICS, (v.total / v.n).tolist())))
                         for (d, m), v in sorted(losses.items())], roles=ranked)
    (ROOT / "work/paprf_contextual_roles.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(2, 4, figsize=(12, 6), layout="constrained")
    for axis, (role, result) in zip(axes.flat, ranked.items()):
        grid = result["primary"]["spearman_components"]
        mesh = axis.imshow(grid, cmap="PuOr", vmin=-1, vmax=1)
        axis.set(xticks=range(3), yticks=range(3), xticklabels=["Runs", "Bdry", "Event"],
                 yticklabels=["Runs", "Bdry", "Event"], title=role.replace("_", " ").title())
        for i in range(3):
            for j in range(3):
                axis.text(j, i, f"{grid[i][j]:+.2f}", ha="center", va="center",
                          color="white" if abs(grid[i][j]) > .65 else "#25172c")
    axes.flat[-1].axis("off")
    fig.colorbar(mesh, ax=list(axes.flat), label="Spearman correlation")
    fig.suptitle("Contextual role profiles · component redundancy")
    fig.savefig(ROOT / "outputs/figures/paprf_role_component_heatmaps.png", dpi=160)
    plt.close(fig)
    plot_trends(profiles, ranked, trend_rows)
    print("Wrote chronological forecasts, role rankings, splits, trends and redundancy audit.")


if __name__ == "__main__":
    main()
