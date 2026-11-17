# Music Report Comment Builder (RBSC)

A standalone, offline, single-file web app for building Sentral-ready **Learning Strengths** and **Strategies to Improve** report comments for NSW Music, Stages 4–6. The app makes no network calls, needs no accounts and stores no student data.

**Live app:** `index.html`. Open it directly in a browser, or deploy the repo root as a static site (e.g. Netlify, with no build step).

## Using it

1. **Set the reporting context.**
   - Choose a **Stage**.
   - For Stage 6, also choose **Course** (Music 1 / Music 2), **Stage Course** (Preliminary / HSC) and a **Comment Profile**.
   - In Stage 5, also choose the **student's instrument** ("Instrument" for generic wording) before picking a Performance sentence.
   - Statements can be browsed before this, but not selected.
2. **Fill both outputs.**
   - Each output takes three sentences, one per slot (e.g. Performance / Composition / Listening).
   - Use **Select** or drag a card into its slot.
   - In Stage 4/5 Strategies, a **General** strategy can replace one slot.
3. **Check the warnings.**
   - The ✔/✘ checklist must be all ✔ before **Copy** is enabled.
   - Amber ⚠ lines are reminders only (e.g. mixed topics, or a Strengths ↔ Strategies cross-check).
4. **Character count.** It shows under each preview. **Stage 4 is fixed at 150 characters per box**, and its bank shows only the short sentence set, which always fits. For Stages 5 and 6, enter the verified Sentral limit in the **Sentral limit** box. It is remembered in your browser and blank by default.
5. **Copy** each output and paste it into Sentral.
6. **Next student** clears both comments and the per-student filters, but keeps the class context.

## Repository layout

| Path | What |
|---|---|
| `index.html` | The built app (current version) |
| `data/statement_bank_v5.6.json` | **Current** statement bank: 3,520 records plus metadata (identical to the data embedded in the app) |
| `data/statement_bank_v5.1.json` | Original v5.1 bank, kept unchanged for reference |
| `data/diffs/v5.1_to_v5.5.json` | Every approved text change: id, change group, old and new text |
| `data/statement_bank_v5.5.json` | Bank before the short Stage 4 set was added (v5.6 adds records only) |
| `src/app.js` | App logic (the script block of `index.html`) |
| `src/base/Music_Report_Comment_Builder_v5.1_ORIGINAL.html` | Recovered v5.1 baseline. It supplies the page shell for builds. |
| `tools/build.py` | Rebuilds `index.html` from the baseline shell, `src/app.js` and the current bank |
| `tools/verify_diff.py` | Confirms two banks differ only by the listed, approved text changes |
| `tests/regression_suite.py` | Headless-Chrome regression suite that drives the real UI |
| `tests/results/` | Recorded results per version |
| `docs/` | Audit report, test reports, and the original migration package |
| `CHANGELOG.md` | Version history |

## Build and test

```bash
# Rebuild the app
python3 -I tools/build.py src/base/Music_Report_Comment_Builder_v5.1_ORIGINAL.html src/app.js index.html data/statement_bank_v5.6.json

# Run the regression suite (needs Python Playwright and Chrome/Chromium)
python3 -I tests/regression_suite.py "$PWD/index.html" data/statement_bank_v5.6.json local tests/results/local.json

# Confirm the bank differs from v5.1 only by the approved changes
python3 -I tools/verify_diff.py data/statement_bank_v5.1.json data/statement_bank_v5.6.json data/diffs/v5.1_to_v5.5.json
```

`tests/regression_suite.py` expects Chrome at `/usr/bin/google-chrome`. Edit `executable_path` if yours is elsewhere.

## Ground rules

- **Statement text changes only with approval and a machine-readable diff.** Each build checks that the embedded bank matches the data file, and `tools/verify_diff.py` confirms only approved changes were made.
- **Sentral character limits:** Stage 4 is 150 per comment box (confirmed). No limit is assumed for Stages 5 and 6 until confirmed.
- See `docs/migration/GOVERNING_SPEC.md` for the governing specification.

## Not yet verified

- Pasting into Sentral (including the en dash in "1600–1900").
- Netlify deployment.
- Browsers other than Chrome.
- Screen-reader output.
