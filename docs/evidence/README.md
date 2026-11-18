# Evidence Register Guide

These registers are deliberately empty templates. An empty cell is not evidence, and a player must not receive a qualitative score merely because a template contains that field.

| Register | What it proves | What it must not be used to infer |
|---|---|---|
| source_register.csv | The origin, date and limitations of a source. | That every claim based on a source is automatically valid. |
| claim_register.csv | One traceable factual or calculated claim. | Broader skill, availability or selection value beyond the claim. |
| candidate_discovery_register.csv | How a candidate entered the future discovery pool. | That the candidate is selected or technically superior. |
| scouting_observation_register.csv | A cited, match-specific technical/tactical observation. | A universal player trait from a single observation. |

Evidence confidence is about confidence in the evidence, not a performance score:

- High: substantial, direct, independently verifiable and recent enough for the claim.
- Medium: useful direct evidence with a clear coverage, sample or recency limit.
- Low: limited, indirect or insufficiently corroborated evidence; record it but do not make a strong selection claim from it.

Lens A is frozen. Set can_affect_lens_a to false for all new external or qualitative records unless a documented future official method revision is explicitly approved; no record may silently alter Lens A v1.
