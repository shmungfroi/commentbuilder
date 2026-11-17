# Audit report — Music Report Comment Builder v5.1 (baseline, no changes made)

**Date:** 17 Nov 2026 · **Baseline:** `Music_Report_Comment_Builder_v5.1_ORIGINAL.html` (sha256 `d44df8bb…7b4817`) · **Data:** `statement_bank_v5.1.json` (sha256 `ea3be673…cd837f`)

**Method:** All six package files were hash-checked against `FILE_MANIFEST.json` (all match). The embedded JSON was extracted from the HTML and compared to the exported bank: they are **identical**. Data checks were run in Python over all 3,520 records. Behaviour checks were run by driving the **real UI** in headless Chrome (clicking chips, Select buttons, drag-and-drop, the copy button and reading the clipboard), using `probe_baseline.py`. No code or data has been modified.

**Not verified:** Sentral paste behaviour, Netlify deployment, mobile browsers and screen readers.

---

## 1. Architecture (how it runs)

The app is one static HTML file (3.7 MB) with three blocks:

| Block | Size | Role |
|---|---|---|
| `<style>` | 9 KB | All CSS (navy/teal palette, three-panel grid) |
| `<script id="statement-data" type="application/json">` | 3.67 MB | `metadata` (24 keys) + `statements` (3,520) |
| `<script>` | 34 KB / 847 lines | One IIFE, no dependencies, no network |

**State model.** There is one `state` object:
- `state.filters` holds 14 keys. Context and browsing filters are all mixed together.
- `state.selected` has the shape `{learning_strength:[s1,s2,s3], strategy_to_improve:[s1,s2,s3]}`.

**Profiles.** `getActiveProfile()` resolves the slot order:
- Stage 6 uses `filters.commentProfile`, falling back to the first Stage 6 profile.
- Anything else (including **no stage chosen**) uses `Stage 4/5 Standard` = P/C/L.

**Flow.** The steps run in this order:
1. A chip click toggles a filter, then runs `renderFilters()` and `renderBank()`.
2. `getFiltered()` applies the active filters. In Stage 6 it also drops categories that are not in the profile.
3. Each card's Select button, or a drag onto a drop zone, calls `selectStatement()`. That places the statement in the slot that matches its category.
4. `renderPreview()` joins the three texts with spaces.
5. `renderValidation()` gates the Copy button.

**What validation checks today:**
- three slots filled;
- a regex sentence count;
- a pronoun regex;
- the phrase "the student";
- a final full stop.

It does **not** check the stage, course, level or topic of the selected records, and it has no character count.

**What clears selections today:**
- Stage change;
- Course or Stage Course change (Stage 6);
- Comment Profile change;
- Topic chip change.

Unit (Stage 4) and Instrument changes do **not** clear selections. Reset Filters clears browsing filters **including Topic** but keeps selections.

---

## 2. Data integrity (3,520 records)

| Check | Result |
|---|---|
| Record count / per stage | 3,520 = Stage 4 **285**, Stage 5 **595**, Stage 6 **2,640** ✔ |
| Unique IDs | 3,520 ✔ |
| Schema | All records have the identical 20-field key set ✔ |
| `tier` ↔ `tierCode` | Consistent ✔ |
| `courseProfile` = `course + stageCourse` | Consistent ✔ |
| Stage 6 `topic` ∈ `stage6TopicMap[course\|level]` | Consistent ✔ |
| Stage 4/5 records carrying Stage 6-only fields | None ✔ |
| `instrument` only on Performance | ✔ (Stage 4 P = generic "Instrument" only; Stage 5 P = 8 instruments + generic, 25 each per type) |
| Stage 6 coverage | **Complete.** Every course × level × profile × type × category × tier × topic cell has exactly **4** candidates (660 cells) ✔ |
| Stage 4 unit coverage | 10 per unit × type × P/C/L ✔ |
| `categoryLabel` matches `metadata.categories` | **90 anomalies**: Stage 4/5 G records are labelled "General" while metadata says G = "General Musicianship" (see F5) |

### Text policy (every record)

| Check | Hits |
|---|---|
| Third-person pronouns (incl. *them*) | 0 |
| First/second person (I, my, we, our, you, your) | 0 |
| "the student" / "student(s)" | 0 |
| Missing final full stop / lowercase start / stray whitespace | 0 |
| More than one sentence in a record | 0 |
| Abbreviations (e.g., i.e., etc.) / `? ! ;` | 0 |
| US spellings (‑ize, color, behavior, center, program) | 0 |
| HSC/ATAR/band predictions | 0 |
| Deficit words (poor, weak, lazy, fail, careless…) | 0 |
| Non-ASCII characters | 50 records, all the en dash in "1600–1900" (**Sentral paste untested**) |

**Lengths.** Single statements are:
- Stage 4: 62–121 characters;
- Stage 5: 60–124 characters;
- Stage 6: 151–219 characters.

A finished three-sentence comment can therefore run:
- Stage 4: **206–345 characters**;
- Stage 5: **192–325 characters**;
- Stage 6: **455–659 characters**.

The Sentral field limit is still unknown, and nothing here assumes one.

### Duplicate text — no records removed, reported only

- **2,423 records (69%) share their exact text with at least one other record**, in 266 groups. No group is a true duplicate: every copy differs in at least one context field.
- Stage 6 has **516 distinct sentences across 2,640 records**.

The groups break down like this:

| Fields that differ within the group | Groups |
|---|---|
| course + stageCourse + topic | 125 |
| course only | 80 |
| stage only (Stage 4 vs 5 General strategies) | 24 |
| tier only | 16 |
| course + stageCourse + tier + topic | 13 (55 records each) |
| instrument only (e.g. Saxophone/Clarinet fingering) | 4 |
| course + tier | 4 |

What this means in practice:
- **The course, level and topic distinctions in Stage 6 are mostly metadata labels, not different wording.** About 79% of topic-tagged Stage 6 records never name their topic in the text. For example, the same Performance-craft strategy appears as Music 1 Preliminary Baroque, Music 2 HSC mandatory repertoire, and so on. This is not a leak bug, but it is worth knowing before you rely on "topic-specific" filtering.
- **33 groups (829 records) use identical text across different tiers. All of them are Strategies, none are Strengths.** Strategy wording does not change between Extensive and Basic for these. Learning Strengths are fully tier-differentiated.

---

## 3. Behaviour findings (confirmed in the real UI)

| ID | Finding | Severity | Evidence |
|---|---|---|---|
| **F1** | **With no Stage chosen, a single comment can mix stages.** The test built Stage 4 Performance + Stage 6 Music 2 HSC Composition + Stage 5 Listening, and Copy was **enabled**. | High | B1 |
| **F2** | **With Stage 6 chosen but Course/Stage Course unset, one comment can mix Music 1 Prelim + Music 2 Prelim + Music 2 HSC.** Copy was **enabled**. Both default to unset, so this is the out-of-the-box state. | High | B2 |
| F3 | Stage 4 Unit change does not clear or flag selections. The spec lists unit as context. | Medium | B8 |
| F4 | Reset Filters clears Topic, which is treated as context everywhere else. Selections survive. This is harmless now, but the two rules are inconsistent. | Low | R01 |
| F5 | Stage 4/5 Category chip "G" is labelled **"General Musicianship"**. Those 90 records are work ethic, behaviour, organisation and home practice ("General"). The same code G means two different things in Stage 4/5 and Stage 6. | Low | B10 |
| F6 | Clicking the active Comment Profile chip deselects it visually, but the default profile silently stays in force. | Low | B13 |
| F7 | No character count anywhere. | Medium (spec item) | V07 |
| F8 | Filter chips are `<div>`s with no tabindex or role, so they cannot be reached by keyboard or screen reader. Card Select buttons are real buttons. | Medium | A01 |
| F9 | Sentence-count regex `\.\s*(?=[A-Z]\|$)` ignores `?`/`!` and would miscount "e.g. The". It is **latent only**: comment text comes solely from the bank, which is clean, and cannot be edited in the UI. | Low | code read |
| F10 | `statementLength` filter has one value in use ("expanded", all Stage 6), so it is a no-op chip. `legacyGenericiseInstrument()` is dead code. | Cosmetic | data/code |

**Working as intended (passed):**
- Load with 3,520 records and no JS errors.
- Course change clears selections.
- Wrong-type drop rejected with a message.
- Wrong-category drop rejected with a message.
- Copy is disabled with 2 of 3 slots and enabled with 3 of 3.
- Clipboard text exactly matches the preview.
- Clearing one output leaves the other intact.
- Reset Filters keeps selections.

---

## 4. Design questions (need a decision, not a fix)

| ID | Question | Current behaviour |
|---|---|---|
| Q1 | Should one comment be allowed to mix **topics** (Stage 6) or **units** (Stage 4)? | Allowed |
| Q2 | Should one comment be allowed to mix **tiers** (e.g. Extensive P + Basic C)? | Allowed. Real students are often uneven across areas. |
| Q3 | Should Strengths and Strategies be cross-checked against each other (same instrument / topic / course)? | No cross-check |
| Q4 | **90 Stage 4/5 General strategies** (work ethic, behaviour, organisation, home practice, music practice) can never be placed: P/C/L has no G slot. Should they stay as browse-only, or get a way in (e.g. an optional Stage 4/5 profile variant)? | Shown, button disabled |
| Q5 | **Sentral character limit** for each field. | Unknown. It will be a configurable setting, left blank until you supply the real figure. |

---

## 5. Proposed change set for v5.2 (awaiting approval)

All changes are app logic only. **Zero changes to the 3,520 records.** The test suite will diff every ID and text against baseline before release.

1. **Context lock (fixes F1, F2).** Selection requires a Stage. Stage 6 also requires Course and Stage Course before Select or drop is enabled. Until then the bank still browses, and the buttons read "Choose Course and Stage Course first".
2. **Record-level validation.** `renderValidation()` re-checks every selected record against the current context: stage, course, stageCourse, category in the right slot, and commentType. A mismatch fails a named check and disables Copy, so stale text can never be copied whatever path produced it.
3. **Unit as context (F3)**, plus Topic handled consistently (F4). Behaviour follows your answer to Q1.
4. **Character counter** on each output. It shows "X characters" and adds an optional limit field, saved in the browser. Copy is disabled only when a limit has been entered and exceeded.
5. **Accessibility (F8).** Chips become real `<button>`s with `aria-pressed`, and drop zones get labels. The look stays the same.
6. **Small fixes.** F5 (label G "General" in Stage 4/5), F6 (profile chip cannot be deselected), F9 (sentence counter handles `?`/`!`/abbreviations).
7. **Deliverables.** `Music_Report_Comment_Builder_v5.2.html` (single file), `CHANGELOG.md`, `TEST_REPORT.md` (before/after for Stage 4, Stage 5 and all five Stage 6 profiles across all four course/level combinations), and a data diff showing 0 changes.
