# Test report — Music Report Comment Builder v5.3

**Date:** 17 Nov 2026 · **Suite:** `regression_suite.py` (headless Chrome, real UI clicks, drag-and-drop and clipboard; synthetic text only)

| Build | Pass | Fail | n/a | Tests run |
|---|---|---|---|---|
| v5.1 original | 33 | 12 | 3 | 48 (suite before the cross-check tests were added) |
| v5.2 | 52 | 7 | 0 | 59 (fails only X01–X07: no cross-check panel) |
| **v5.3** | **59** | **0** | **0** | **59** |

"—" means the test was not in the suite when that build was run.

## Data integrity

- The embedded bank equals `statement_bank_v5.1.json` exactly: **3,520 records, 0 changed** (D02).
- The data block is copied byte-for-byte by `build_v53.py`.

## Results

| ID | Case | Expected | v5.1 | v5.2 | v5.3 | v5.3 observed |
|---|---|---|---|---|---|---|
| D01 | Load offline | 3520 loaded, no JS errors | ✔ | ✔ | ✔ | 3520 statements loaded · app v5.3 · data 5.1-fixed-stage6 |
| D02 | Embedded bank == statement_bank_v5.1.json | 0 record changes | ✔ | ✔ | ✔ | identical=True; changed records=0 |
| F1 | No Stage: try to mix Stage 4/6/5 in one comment | selection blocked; copy disabled | ✘ | ✔ | ✔ | ['disabled:Choose a Stage first', 'disabled:Choose a Stage first', 'disabled:Choose a Stage first']; copy=False |
| F1b | No Stage: on-screen guidance | notice explains Stage needed | ✘ | ✔ | ✔ | Choose a Stage first — statements can be browsed but not selected until the reporting context is set. |
| F2 | Stage 6, no Course/Level: try to mix M1/M2, Prelim/HSC | selection blocked; copy disabled | ✘ | ✔ | ✔ | ['disabled:Choose Course and Stage Course first', 'disabled:Choose Course and Stage Course first', 'disabled:Choose Course and Stage Course first']; copy=False |
| F2b | Stage 6, Course set but not Stage Course | still blocked | ✘ | ✔ | ✔ | disabled:Choose Course and Stage Course first |
| V03d | Injected Stage 5 record into Stage 4 comment | context check fails; copy disabled | — | ✔ | ✔ | copy=False; ✘ All statements match the reporting context (Stage 4) — slot 3 is Stage 5 |
| V03e | Copy forced on an invalid comment (stale enabled button) | copy-time re-check refuses; clipboard untouched | — | ✔ | ✔ | msg="Not copied — fix the items marked ✘ first."; clipboard='SENTINEL' |
| S04 | Stage 4 Standard, unit Jazz, both outputs | P/C/L; unit filter exact; both copyable | ✔ | ✔ | ✔ | labels=['1. Performance', '2. Composition', '3. Listening']; bank all Jazz=True (60); LS=True STI=True |
| C01 | Clipboard equals preview (Stage 4 STI) | identical | ✔ | ✔ | ✔ | match=True |
| Q1-unit | Stage 4: three different units | allowed + amber warning | ✘ | ✔ | ✔ | copy=True; warning=True |
| Q1-unit2 | Stage 4: change Unit chip after selecting | selections kept (browse filter) | ✔ | ✔ | ✔ | filled=[True, True, True] |
| S05 | Stage 5 Standard, Guitar, both outputs | instrument filter exact; both copyable | ✔ | ✔ | ✔ | bank all Guitar P=True (50); LS=True STI=True |
| S06 | Music 1 Preliminary — Performance | P/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 Preliminary — Composition | C/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 Preliminary — Viva Voce | P/V/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 1 Preliminary — Musicianship | P/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 Preliminary — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Performance | P/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 120 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 HSC — Composition | C/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 120 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 1 HSC — Viva Voce | P/V/G; no leaks; both copyable | ✔ | ✔ | ✔ | 120 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Musicianship | P/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 120 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 1 HSC — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 120 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Performance | P/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 480 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 Preliminary — Composition | C/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 480 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 Preliminary — Viva Voce | P/V/G; no leaks; both copyable | ✔ | ✔ | ✔ | 480 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Musicianship | P/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 480 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 Preliminary — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 480 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Performance | P/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 HSC — Composition | C/M/A; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Composition/Musicology/Aural, LS=True STI=True |
| S06 | Music 2 HSC — Viva Voce | P/V/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Viva Voce/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Musicianship | P/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Performance/Aural/General Musicianship, LS=True STI=True |
| S06 | Music 2 HSC — Composition/Musicianship | C/A/G; no leaks; both copyable | ✔ | ✔ | ✔ | 360 shown, leaks=0, labels=Composition/Aural/General Musicianship, LS=True STI=True |
| Q1-topic | Music 1 Prelim: three different topics | allowed + amber warning | ✘ | ✔ | ✔ | copy=True; warning=True |
| Q1-topic2 | Change Topic chip after selecting | selections kept | ✘ | ✔ | ✔ | filled=[True, True, True] |
| V03 | Change Course / Stage Course / Profile / Stage after selecting | all clear selections | ✔ | ✔ | ✔ | course=[False, False, False] level=[False, False, False] profile=[False, False, False] stage=[False, False, False] |
| V04 | Drop Strategy in Strengths; Composition in Performance zone | both rejected + explained | ✔ | ✔ | ✔ | "That is a "Strategies to Improve" statement — drop it in the Strategies to Improve builder." / "That is a Composition statement — drop it in the Performance zo |
| V02 | Two of three slots | copy disabled | ✔ | ✔ | ✔ | copy=False |
| V01 | Three valid slots | copy enabled, all checks ✔ | ✔ | ✔ | ✔ | copy=True; ✘ count=0 |
| R01 | Reset Filters | selections and Stage kept | ✔ | ✔ | ✔ | LS=[True, True, True] STI=[True, True, True] stage active=True |
| R02 | Clear one output | other unaffected | ✔ | ✔ | ✔ | LS=[False, False, False] STI=[True, True, True] |
| V06 | Sentence counter: ?, !, e.g., decimals, quotes, 4 sentences, missing stop | all counts correct | — | ✔ | ✔ | mismatches=[] |
| V05 | Synthetic policy breaches (pronoun, them, first person, "the student", 2 sentences, missing stop) | each rejected | — | ✔ | ✔ | pronoun: rejected; them: rejected; first person: rejected; the student: rejected; two sentences: rejected; missing stop: rejected |
| V07 | Character count; limit = length−1, then = length; persists on reload | count visible; over → copy disabled; at limit → enabled; limit remembered | — | ✔ | ✔ | "295 characters (no limit set)" → over: copy=False "295 characters / limit 294"; at limit: copy=True; after reload limit=294 |
| V07b | Default limit | blank (no Sentral limit assumed) | — | ✔ | ✔ | "" |
| Q4 | Stage 4 Strategies: General replaces Listening; 2nd General refused | copyable with note; second refused | — | ✔ | ✔ | copy=True; note="General — in place of Listening"; 2nd msg="Only one General strategy per comment — remove the one in slot 3 first." |
| Q4b | Drag General onto Performance slot | accepted as swap | — | ✔ | ✔ | copy=True; filled=[True, True, True] |
| Q4c | Stage 6 Viva Voce (G is a normal slot) | no swap buttons | — | ✔ | ✔ | swap buttons=0 |
| F5 | Stage 4/5 category chip for G | "General" | ✘ | ✔ | ✔ | General |
| F6 | Click the active profile chip | stays selected | ✘ | ✔ | ✔ | active=1 |
| X01 | Stage 5: Strengths Guitar vs Strategies Voice | instrument reminder; both still copyable | — | ✘ | ✔ | panel="⚠ Performance instrument differs (Strengths: Guitar; Strategies: Voice)Reminder only — cop"; LS copy=True STI copy=True; in LS checklist=True |
| X02 | Generic "Instrument" vs Guitar, same tiers | no reminder (generic is compatible) | — | ✘ | ✔ | panel="✔ No instrument, topic/unit or tier inconsistencies found between Strengths and Strategies" |
| X03 | Music 2 Prelim: Strengths Baroque vs Strategies Classical | topic reminder | — | ✘ | ✔ | panel="⚠ Topic differs (Strengths: Baroque Music; Strategies: Classical Music)Reminder only — copying is still allowe" |
| X04 | Stage 4: Strengths Jazz vs Strategies Sound Lab | unit reminder | — | ✘ | ✔ | panel="⚠ Unit differs (Strengths: Jazz; Strategies: Sound Lab)Reminder only — copying is still allowed. Check both co" |
| X05 | Tier gap: P Extensive vs Elementary (2 levels); C Sound vs Thorough (1 level) | P flagged, C not | — | ✘ | ✔ | panel="⚠ Performance tier gap (Strengths: Extensive; Strategies: Elementary)Reminder only — copying is still allowed. Check bot" |
| X06 | General (Basic) swapped into Listening vs Listening strength (Extensive) | not a tier gap (different category) | — | ✘ | ✔ | panel="✔ No instrument, topic/unit or tier inconsistencies found between Strengths and Strategies." |
| X07 | Only Strengths started | cross-check waits for both | — | ✘ | ✔ | panel="Shown once both outputs have at least one statement." |
| A01 | Keyboard: focus Stage chip, Enter selects, Space deselects; aria-pressed | operable | ✘ | ✔ | ✔ | {'tag': 'BUTTON', 'pressed': 'false'}; keyboard ok=True |
| E01 | JavaScript errors during whole run | none | ✔ | ✔ | ✔ | none |

## Not verified

- **Sentral paste** (including the en dash in "1600–1900").
- **Sentral character limits:** the field ships blank.
- **Netlify deploy.**
- **Browsers:** only Chrome was tested.
- **Screen readers:** only keyboard operation and ARIA attributes were checked.
