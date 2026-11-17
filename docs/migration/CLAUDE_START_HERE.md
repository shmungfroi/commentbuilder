# Claude migration — RBSC Music Report Comment Builder

## First instruction to Claude

You are taking over development of an existing **standalone Music Report Comment Builder**, NOT starting a new app. Read `GOVERNING_SPEC.md`, `TECHNICAL_AUDIT.md`, and the original working `Music_Report_Comment_Builder_v5.1_ORIGINAL.html` before writing code. The authoritative complete statement corpus is also exported in `statement_bank_v5.1.json`. Preserve all existing statements, metadata, and workflow unless a specific change is agreed. Work in small, reversible increments and deliver a downloadable complete HTML file and changelog after each change. Do not claim browser or Sentral validation unless performed. Do not introduce a backend, accounts, personal student data, or paid services.

## Suggested first Claude task

1. Open and explain the original app's current architecture and running behaviour.
2. Run an integrity audit on the 3,520 statements; report actual duplicates, schema anomalies, stale context retention, and filtering/validation bugs without changing data.
3. Implement targeted validation improvements while preserving UI and functionality. Add explicit character limit configuration rather than guessing a Sentral limit.
4. Supply before/after tests for Stage 4, Stage 5 and every Stage 6 profile.
5. Return a complete, runnable single-file HTML deliverable, plus test report and change log.

## Handover order

1. `GOVERNING_SPEC.md` — requirements and invariant behaviours.
2. `TECHNICAL_AUDIT.md` — verified facts and items requiring investigation.
3. `Music_Report_Comment_Builder_v5.1_ORIGINAL.html` — recovered standalone source; open directly in browser.
4. `statement_bank_v5.1.json` — exact extracted copy of embedded data.
5. `TEST_PLAN.md` — acceptance test matrix.
6. `FILE_MANIFEST.json` — file hashes.

Keep Stage 6 Music 1 and Music 2 distinct, including Preliminary and HSC settings. Give priority to current Year 11 Preliminary workflows. Do not infer unprovided policy, maximum character counts, or school-specific reporting requirements.
