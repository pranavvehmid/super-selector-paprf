# Assumptions and interpretations

| ID | Assumption / interpretation | Why | Status |
|---|---|---|---|
| A-001 | "PLS" in the user's request means **Partial Least Squares** regression (Lens B). | User wrote "By PLS" alongside a statistical analysis; PLS is a standard multivariate method for many correlated predictors. | Working interpretation only; deferred in D-002 and not active in the primary workflow. |
| A-002 | "IP and retention list" means the **IPL** retention list for the upcoming (2027) season; "RS" means **RR** (Rajasthan Royals). | Context of the request. | To be confirmed |
| A-003 | Lens A is the planned submission method; a future PLS method may be supplementary only if D-002 is confirmed. | The official report must be transparent and reproducible, and the user has not yet confirmed PLS. | Decided in D-003 |
| A-004 | Official scoring is on pressure reliability from the supplied data; squad factors are supplementary (event briefing asks for squad-fit explanation). | Official PDF says rankings must be data-supported. | Open |
| A-005 | Raw data is kept out of Git by default (see `.gitignore`). | The data pack may carry usage restrictions. | User may change |
| A-006 | A 7-run required rate marks the start of second-innings rate stress, and the pressure band thresholds are 0.40 and 0.65. | The supplied brief leaves the pressure definition to the participant; these transparent values will be tested in Step 9. | Active proposed method |
