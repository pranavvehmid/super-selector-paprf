# Master-Prompt Intake and Evidence Traceability

**Received:** 18 November 2026  
**Source type:** User-supplied project specification, not an official Round 1 requirement  
**Source location:** C:\Users\ADMIN\.codex\attachments\8360ac83-a7ff-4d74-a6ed-7e455b855b4a\Pasted text.txt  
**SHA-256:** A407F3AE7DAC15F7FC060CEDDC798C6251625C039126EEDE962044AB7E819793  
**Review record:** One complete review plus four complete verification re-reads on 18 November 2026.

## Interpretation boundary

The master prompt is the user's desired standard for a comprehensive scouting system. It does not replace the official Round 1 requirement recorded in docs/00_official_requirements.md: submit reproducible, data-supported top-10 pressure-reliability lists for batters and bowlers. The frozen Lens A v1 rankings remain that official statistical output.

The master prompt is adopted as an evidence and future-work specification. Requirements needing facts not present in the supplied ball-by-ball pack remain unscored until evidence is collected and cited. No technical, tactical, fitness, availability, age, nationality, role or condition claim is inferred merely from a name or ranking.

## Requirement trace

| Master-prompt area | Source lines | Current evidence/status | Next evidence needed |
|---|---:|---|---|
| Audit the existing method | 19–40 | Completed in docs/methodology/master_prompt_methodology_audit.md. | Re-audit once B/C evidence exists. |
| Broad player discovery | 42–84 | Not started; outside the frozen Round 1 statistical list. | Dated candidate universe and source register. |
| Technical/tactical scouting | 86–262 | Not scored: ball-by-ball alone cannot establish technique or tactical intent. | Verified video/scouting notes with source, observer, match and date. |
| Performance quality | 263–294 | Partly represented by pre-delivery pressure and player-vs-own-baseline deltas. | Opposition and venue/condition evidence for a broader quality score. |
| Contextual statistics | 295–354 | Partly implemented: role-specific rates, phase/state and pressure context. | Pace/spin, venue, opposition-strength and recency fields or cited source data. |
| Country/data-availability bias control | 355–383 | Not yet audited for the wider discovery pool. | Candidate-universe country and competition coverage table. |
| Weightage matrices | 384–428 | Proposed for a future scouting overlay only; never retrofitted into Lens A v1. | Role definitions and evidence scale before assigning weights. |
| Evidence confidence | 429–462 | Sample-size reliability is implemented; broader evidence confidence is not. | Per-claim source and recency register. |
| Multi-stage shortlist process | 463–515 | Lens A covers statistical eligibility, validation and ranking only. | Discovery, technical review and independent audit evidence. |
| Player charts and scouting reports | 516–607 | Lens A evidence tables exist; qualitative scouting reports are not yet supported. | Player-level verified scouting evidence. |
| Alternatives and final transparency | 608–733 | Sensitivity tests and limitations are reported for Lens A. | Broader-scouting evidence before comparative claims. |

## Evidence protocol adopted for all subsequent work

Every future factual statement, count, formula, decision or qualitative observation must have an entry or direct pointer containing:

1. Claim or calculation.
2. Evidence type: supplied-data result, official source, reputable external source, analytical interpretation, or assumption.
3. Exact file/table/query/script source and, for external facts, URL plus retrieval date.
4. Population, period and inclusion/exclusion rules.
5. Formula, units and rounding rule where numerical.
6. Known limitation or uncertainty.
7. Whether it can influence Lens A, B or C. Lens C can never alter frozen Lens A scores.

This register is deliberately explicit about unavailable evidence. Missing evidence is recorded as a gap, not filled by plausible-sounding prose.

## Operational templates created

The empty, reviewable intake templates are docs/evidence/source_register.csv, docs/evidence/claim_register.csv, docs/evidence/candidate_discovery_register.csv and docs/evidence/scouting_observation_register.csv. Their schema and confidence definitions are in docs/evidence/README.md. External factual files belong in data/external/ and must follow data/external/README.md.

The first evidence-only discovery artifact is docs/evidence/supplied_data_candidate_universe.md with its ID-keyed output table. It records supplied-data coverage only and does not make a scouting claim.

The proposed evidence-gated scoring rules and role-specific 100% matrices are documented in docs/methodology/broader_scouting_framework_draft.md. They are not yet applied to any player.
