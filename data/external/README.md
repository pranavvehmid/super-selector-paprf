# External data (user-supplied or sourced)

Header-only templates. Fill from the user's spreadsheets or from cited public sources.
Every row must have `source_url` (or "user spreadsheet: <filename>") and `retrieved_on` (YYYY-MM-DD). Never invent values.
Join key is `player_id` from the hackathon data pack; where unavailable, add a name match and log it in `docs/factors/name_match_log.md`.
