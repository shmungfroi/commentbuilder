# Full audit — Music Report Comment Builder v5.3

**Date:** 17 Nov 2026 · **App:** v5.3 · **Data:** `5.1-fixed-stage6` (3,520 records, unchanged)

## What it was checked against

1. **The RBSC comment rules embedded in the bank** (`metadata.rules`):
   - three sentences;
   - no name, no pronouns, not "the student", no first person;
   - present tense;
   - impersonal third-person, Australian English;
   - no casual language, no HSC predictions, no punitive or deficit wording;
   - the combine rule;
   - order P/C/L;
   - **performance instrument filter required**.
2. **`GOVERNING_SPEC.md`** from the migration package.
3. **The RBSC scope, sequence and assessment schedule** on file: Years 7–12 units, Stage 6 topics, task structures.

## Methods

- Automated checks over all 3,520 sentences.
- Assembled three-sentence comments simulated for each profile.
- The live app driven in headless Chrome (desktop and a 390 px phone width).
- **Not done:** a human read of all 3,520 sentences, a Sentral paste test, and any change to the data.

---

## Passes (no action needed)

| Rule | Result |
|---|---|
| No names, no pronouns, no "the student", no first or second person | 0 breaches |
| Australian English | 0 US spellings. Every dictionary "unknown" is correct AU usage (organise, analyse, colour, behaviour…). Practise (verb) and practice (noun) are used correctly in all 135 verb cases. |
| Spelling | No typos found |
| Present tense | No past or future tense. Learning Strengths all open with a present-tense verb ("Performs…"). Strategies use the imperative ("Refine…"), which is standard report convention for strategies. |
| Casual language | 0 |
| HSC predictions (band, ATAR, marks, "on track", "likely") | 0 |
| One sentence per record, ends with a full stop | All 3,520 |
| Metadata counts vs actual records | All match |
| Stage 6 coverage | Every course × level × profile × type × category × tier × topic cell has 4 options |
| Profiles vs RBSC tasks | Fit well. Viva Voce (P/V/G) matches Year 11 Task 1 in both courses (performance + viva voce). Composition (C/M/A) matches Music 1 Year 11 Task 2 and Music 2 Year 11 Task 2 (composition + portfolio analysis). Performance / Musicianship cover the perf + aural / musicology tasks. |
| App: context lock, validation, cross-check, copy | 59/59 regression tests (see `TEST_REPORT_v5.3.md`) |

---

## Findings

### HIGH — text that would appear on a real report

**H1. Placeholder topic names are written into 250 Stage 6 sentences.**
- The topic label is inserted verbatim, so parents would read, for example:
  - "Interprets **HSC elective topic** repertoire with confident attention to style…" (Music 1 HSC, 50 sentences);
  - "Interprets **mandatory and additional topic repertoire**…", "**mandatory topic repertoire**", "**additional topic repertoire**" (Music 2 HSC, 200 sentences).
- These read as template text, not report language.
- **Fix (data change, needs approval):** use the real RBSC topic names, or neutral wording ("Interprets elective repertoire…"). See H5 for the topic list.

**H2. "…as part of senior music study" ends 2,265 of the 2,640 Stage 6 sentences (86%).**
- A typical Stage 6 comment says it **two or three times**.
- **110 sentences say it twice in one sentence**, e.g. "Approaches senior music study with … organisation … as part of senior music study."
- It also adds about 30 characters per sentence. Stage 6 comments run 455–659 characters, roughly double Stage 4/5.
- **Fix (mechanical data change, needs approval):** remove the trailing phrase from every sentence. This needs a machine diff, and nothing else changes. Stage 6 comments would shrink by about 60–90 characters.

**H3. Stage 6 tiers differ by only one word.**
- **All 264 Stage 6 Learning Strength sets** read word-for-word the same from Extensive to Basic except one adjective (sophisticated → secure → sound → emerging → foundational).
- A **Basic** report therefore still claims "…stylistic understanding and expressive detail, demonstrating careful attention to tone, phrasing, musical shape and communication".
- Two side effects:
  - **Repetition:** one tier word appears in all three sentences ("secure … secure … secure").
  - **Self-contradiction:** some Extensive sentences pair "sophisticated organisation" with "a developing sense of artistic responsibility".
- Stage 4/5 do this properly. For example, Stage 5 Composition reads:
  - Extensive: "sophisticated compositional ideas with clear structure, purposeful contrast and strong musical direction";
  - Basic: "simple compositional ideas with support".
- **Fix (rewrite, needs your input):** rewrite the Sound / Elementary / Basic Stage 6 strengths so the *claims* scale down, not just the adjective. This is the largest job. I'd draft one course/profile for your approval first.

**H4. Deficit wording in 22 Stage 5 Learning Strengths** (breaches `noPunitiveOrDeficitWording`).
- Mostly Basic-tier Performance:
  - "Demonstrates **limited** guitar technique while attempting simple practical tasks with support";
  - "…**limited** rhythmic accuracy";
  - "Develops **limited** musical ideas…".
- A strength that states a limitation reads as a deficit. Stage 6 Basic uses asset framing instead ("with support", "foundational").
- **Fix (small data change, needs approval):** rewrite the 22 with asset framing, e.g. "Plays short guitar phrases with guidance, building rhythmic accuracy."

### MEDIUM — curriculum fit (RBSC scope and sequence vs the bank)

**H5. Topic and unit coverage against RBSC's current programs**

| RBSC course | RBSC units / topics | In the bank | Gap |
|---|---|---|---|
| Year 8 (Stage 4) | Beats & Tunes; Rockin' the Guitar; Sound Lab; Jazz It Up | Beats and Tunes; Rocking the Guitar; Sound Lab; Jazz | Names differ slightly ("Rocking" is spelled out in 30 sentences) |
| Year 7 (Stage 4) | Beats & Tunes T1–2; T3–4 not yet set | Beats and Tunes | none yet |
| Years 9–10 (Stage 5) | Groove Expedition; Jazz (Handy to Hiromi); Music of the Solar System; Australian Perspectives; Kagemusha; Other Voices; Depth Study | **No unit tags or unit-specific sentences** (all 595 are generic or instrument-based) | All Stage 5 units |
| Music 1 Year 11 | Baroque; Popular Music; **Music for Small Ensembles** | Popular; Baroque; **Classical** | Small Ensembles missing; Classical not taught in Music 1 at RBSC (harmless) |
| Music 1 Year 12 | An Instrument and its Repertoire; Music for Radio, Film, TV & Multimedia; Music of the 20th & 21st Centuries | "HSC elective topic" (placeholder) | All three topics unnamed (H1) |
| Music 2 Year 11 | Music 1600–1900: Baroque, Classical, Romantic + **Additional Topic (student's choice)** | 1600–1900; Baroque; Classical; Romantic | Additional Topic |
| Music 2 Year 12 | Music of the Last 25 Years (Australian focus); Music of a Culture | "mandatory / additional topic repertoire" (placeholders) | Both topics unnamed (H1) |
| Music Extension | Performance specialisation | — | Not covered |

Generalisable sentences still work for every gap. Only the topic-specific options are missing.

### MEDIUM — app

**A1. The bank's own rule `performanceInstrumentFilterRequired` is not enforced.** In Stage 5, a Performance sentence can be chosen without choosing the student's instrument first. **Fix (app):** in Stage 5, require an instrument before Performance selection. "Instrument" (generic) counts as a valid choice.

**A2. Stage 4 instrument chips lead to an empty bank.** Stage 4 Performance sentences only use the generic "Instrument", so choosing Guitar, Voice and so on shows **0 statements**. **Fix (app):** in Stage 4, show only "Instrument", or hide the instrument filter.

### LOW / suggestions

- **L1. Readability.** Stage 6 sentences average 25 words (very dense); Stage 4/5 average 11–13. H2 alone shortens every Stage 6 sentence.
- **L2. Strategies identical across tiers.** 829 records were already reported in the v5.1 audit. Tier only changes the wording of Learning Strengths.
- **L3. Workflow speed (app).**
  - A **Next student** button would clear both outputs but keep the context; at present that takes two Clear clicks.
  - An optional **search box** over the visible bank.
  - A **set tiers once per area** shortcut.
- **L4. Phones.** The layout works and the Select buttons work. Drag-and-drop doesn't work on touch screens, and the builders sit well below the bank.
- **L5. Minor.** "artform" could be written "art form" (found in sentence text).

---

## Proposed order of work (each step separate, diffed, tested)

1. **App only (no data change):** A1, A2, plus "Next student" from L3.
2. **Mechanical data fix:** H2, remove "as part of senior music study" (machine diff).
3. **Wording fixes:** H1 (placeholder topics) and H4 (22 deficit strengths), as a proposed-text diff for your approval.
4. **Rewrite:** H3 (Stage 6 tier ladder). Draft one course/profile first for approval.
5. **New content:** H5 topic and unit sentences, only if you want them.

Steps 2–5 change statement text. The spec requires your explicit authorisation and a machine-readable diff for each one.
