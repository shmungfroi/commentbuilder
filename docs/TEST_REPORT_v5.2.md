# Test report — Music Report Comment Builder v5.2

**Date:** 17 Nov 2026 · **Suite:** `regression_suite.py` (headless Chrome, real UI clicks, drag-and-drop and clipboard; synthetic text only)

| Build | Pass | Fail | n/a |
|---|---|---|---|
| v5.1 original | 33 | 12 | 3 |
| **v5.2** | **52** | **0** | **0** |

"n/a" on v5.1 means the test needs the read-only test hook that v5.2 adds. v5.1 has no character-limit field, so its V07 is recorded as a fail.

## Data integrity

- The embedded bank in v5.2 equals `statement_bank_v5.1.json` exactly: **3,520 records, 0 changed, added or removed**. The `<script id="statement-data">` block is copied byte-for-byte from v5.1 by `build_v52.py`.
- Records changed: **none**.

## Sentence counter comparison (V06 cases)

- **v5.1 regex** `\.\s*(?=[A-Z]|$)` miscounts **2 of 7** cases:
  - "Plays well? Composes well! Listens well.": expected 3, got 1
  - "Plays “well.” Composes well. Listens (carefully.)": expected 3, got 1
- **v5.2 counter:** 0 mismatches.

This was latent in v5.1. Bank text is one clean sentence per record and cannot be edited in the UI.

## Results (before → after)

| ID | Case | Expected | v5.1 | v5.2 | v5.2 observed |
|---|---|---|---|---|---|
| D01 | Load offline | 3520 loaded, no JS errors | ✔ pass | ✔ pass | 3520 statements loaded · app v5.2 · data 5.1-fixed-stage6 |
| D02 | Embedded bank == statement_bank_v5.1.json | 0 record changes | ✔ pass | ✔ pass | identical=True; changed records=0 |
| F1 | No Stage: try to mix Stage 4/6/5 in one comment | selection blocked; copy disabled | ✘ fail | ✔ pass | ['disabled:Choose a Stage first', 'disabled:Choose a Stage first', 'disabled:Choose a Stage first']; copy=False |
| F1b | No Stage: on-screen guidance | notice explains Stage needed | ✘ fail | ✔ pass | Choose a Stage first — statements can be browsed but not selected until the reporting context is set. |
| F2 | Stage 6, no Course/Level: try to mix M1/M2, Prelim/HSC | selection blocked; copy disabled | ✘ fail | ✔ pass | ['disabled:Choose Course and Stage Course first', 'disabled:Choose Course and Stage Course first', 'disabled:Choose Course and Stage Course first']; copy=False |
| F2b | Stage 6, Course set but not Stage Course | still blocked | ✘ fail | ✔ pass | disabled:Choose Course and Stage Course first |
| V03d | Injected Stage 5 record into Stage 4 comment | context check fails; copy disabled | n/a | ✔ pass | copy=False; ✘ All statements match the reporting context (Stage 4) — slot 3 is Stage 5 |
| V03e | Copy forced on an invalid comment (stale enabled button) | copy-time re-check refuses; clipboard untouched | n/a | ✔ pass | msg="Not copied — fix the items marked ✘ first."; clipboard='SENTINEL' |
| S04 | Stage 4 Standard, unit Jazz, both outputs | P/C/L; unit filter exact; both copyable | ✔ pass | ✔ pass | labels=['1. Performance', '2. Composition', '3. Listening']; bank all Jazz=True (60); LS=True STI=True |
| C01 | Clipboard equals preview (Stage 4 STI) | identical | ✔ pass | ✔ pass | match=True |
| Q1-unit | Stage 4: three different units | allowed + amber warning | ✘ fail | ✔ pass | copy=True; warning=True |
| Q1-unit2 | Stage 4: change Unit chip after selecting | selections kept (browse filter) | ✔ pass | ✔ pass | filled=[True, True, True] |
| S05 | Stage 5 Standard, Guitar, both outputs | instrument filter exact; both copyable | ✔ pass | ✔ pass | bank all Guitar P=True (50); LS=True STI=True |
| S06 | Music 1 Preliminary — Performance | P/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 Preliminary — Composition | C/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 Preliminary — Viva Voce | P/V/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 1 Preliminary — Musicianship | P/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 Preliminary — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Performance | P/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 120 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 HSC — Composition | C/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 120 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 HSC — Viva Voce | P/V/G; no leaks; both copyable | ✔ pass | ✔ pass | 120 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Musicianship | P/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 120 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 120 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Performance | P/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 480 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 Preliminary — Composition | C/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 480 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 Preliminary — Viva Voce | P/V/G; no leaks; both copyable | ✔ pass | ✔ pass | 480 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Musicianship | P/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 480 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 480 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Performance | P/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 HSC — Composition | C/M/A; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 HSC — Viva Voce | P/V/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Musicianship | P/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ pass | ✔ pass | 360 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| Q1-topic | Music 1 Prelim: three different topics | allowed + amber warning | ✘ fail | ✔ pass | copy=True; warning=True |
| Q1-topic2 | Change Topic chip after selecting | selections kept | ✘ fail | ✔ pass | filled=[True, True, True] |
| V03 | Change Course / Stage Course / Profile / Stage after selecting | all clear selections | ✔ pass | ✔ pass | course=[False, False, False] level=[False, False, False] profile=[False, False, False] stage=[False, False, False] |
| V04 | Drop Strategy in Strengths; Composition in Performance zone | both rejected + explained | ✔ pass | ✔ pass | "That is a "Strategies to Improve" statement — drop it in the Strategies to Improve builder." / "That is a Composition statement — drop it in the Performance zone." |
| V02 | Two of three slots | copy disabled | ✔ pass | ✔ pass | copy=False |
| V01 | Three valid slots | copy enabled, all checks ✔ | ✔ pass | ✔ pass | copy=True; ✘ count=0 |
| R01 | Reset Filters | selections and Stage kept | ✔ pass | ✔ pass | LS=[True, True, True] STI=[True, True, True] stage active=True |
| R02 | Clear one output | other unaffected | ✔ pass | ✔ pass | LS=[False, False, False] STI=[True, True, True] |
| V06 | Sentence counter: ?, !, e.g., decimals, quotes, 4 sentences, missing stop | all counts correct | n/a | ✔ pass | mismatches=[] |
| V05 | Synthetic policy breaches (pronoun, them, first person, "the student", 2 sentences, missing stop) | each rejected | n/a | ✔ pass | pronoun: rejected; them: rejected; first person: rejected; the student: rejected; two sentences: rejected; missing stop: rejected |
| V07 | Character count; limit = length−1, then = length; persists on reload | count visible; over → copy disabled; at limit → enabled; limit remembered | ✘ fail | ✔ pass | "295 characters (no limit set)" → over: copy=False "295 characters / limit 294"; at limit: copy=True; after reload limit=294 |
| V07b | Default limit | blank (no Sentral limit assumed) | n/a | ✔ pass | "" |
| Q4 | Stage 4 Strategies: General replaces Listening; 2nd General refused | copyable with note; second refused | ✘ fail | ✔ pass | copy=True; note="General — in place of Listening"; 2nd msg="Only one General strategy per comment — remove the one in slot 3 first." |
| Q4b | Drag General onto Performance slot | accepted as swap | n/a | ✔ pass | copy=True; filled=[True, True, True] |
| Q4c | Stage 6 Viva Voce (G is a normal slot) | no swap buttons | n/a | ✔ pass | swap buttons=0 |
| F5 | Stage 4/5 category chip for G | "General" | ✘ fail | ✔ pass | General |
| F6 | Click the active profile chip | stays selected | ✘ fail | ✔ pass | active=1 |
| A01 | Keyboard: focus Stage chip, Enter selects, Space deselects; aria-pressed | operable | ✘ fail | ✔ pass | {'tag': 'BUTTON', 'pressed': 'false'}; keyboard ok=True |
| E01 | JavaScript errors during whole run | none | ✔ pass | ✔ pass | none |

## Not verified

- **Sentral paste** (including the en dash in "1600–1900").
- **Sentral character limits:** none is assumed. The limit field ships blank.
- **Netlify deploy.**
- **Safari, Firefox and mobile browsers:** only Chrome was tested.
- **Screen-reader output:** only keyboard operation and ARIA attributes were checked.
