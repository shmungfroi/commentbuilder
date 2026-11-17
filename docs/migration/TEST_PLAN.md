# Claude QA / acceptance tests

Use controlled synthetic examples only. Record expected/actual results and screenshots or machine test output.

| ID | Case | Expected |
|---|---|---|
| D01 | Load unmodified baseline offline | All UI renders; bank count 3520; no JS exceptions |
| D02 | Extract bank, reload it | Record IDs and text unchanged, 3520 records |
| S04 | Stage 4 Standard | P/C/L strengths and strategies, proper tier/unit filtering |
| S05 | Stage 5 Standard | P/C/L both outputs; instrument filters respected |
| S06-1 | Music 1 Preliminary Performance | P/M/A; correct course and topic only |
| S06-2 | Music 2 Preliminary Composition | C/M/A; correct course and topic only |
| S06-3 | Music 1 HSC Viva Voce | P/V/G; excludes incompatible course/level statements |
| S06-4 | Music 2 HSC Musicianship | P/A/G; category labels and filters match |
| S06-5 | Composition/Musicianship | C/A/G sequence and separate outputs |
| V01 | Select all three valid slots | Copy permitted only after all validation passes |
| V02 | Select only two slots | Copy disabled |
| V03 | Switch stage/course/topic/profile after selecting | Incompatible choices cleared or flagged, never silently copied |
| V04 | Select strength for strategy or wrong category | Rejected and explained |
| V05 | Insert pronouns, “the student”, first-person | Validator flags policy breaches |
| V06 | Insert 2/4 sentences, missing period, abbreviated music terms | Robust count, appropriate rejection, no false guarantees |
| V07 | Over configurable character limit | Visible count and copy disabled |
| R01 | Reset browse filters | Existing reporting context/selections preserved |
| R02 | Clear one output | Other output unaffected |
| C01 | Copy valid preview | Clipboard exactly matches preview |
| A01 | Keyboard navigation / screen reader labels | Filters, selections, copy actions operable |

Before shipping, compare unchanged baseline statement IDs and text using an automated diff. Any changes must be enumerated explicitly.
