# Changelog — Music Report Comment Builder

## v5.4 — 17 Nov 2026

**Statement bank: unchanged.** The data block is byte-identical. All changes are app logic and markup.

### Added

- **Student's instrument rule (Stage 5).** This enforces the bank's own `performanceInstrumentFilterRequired` rule.
  - Performance statements can only be selected once the student's instrument is chosen. "Instrument" is the choice for generic wording.
  - Until then the bank shows "Choose the student's instrument first", and an amber prompt explains why.
  - The instrument now narrows **Performance statements only**, to that instrument plus generic ones. Composition, Listening and General statements stay visible.
  - The checklist confirms that the Performance sentence matches the instrument. Changing the instrument afterwards flags the mismatch and disables Copy.
- **Next student button.**
  - It clears both comments, plus the tier, instrument, category and other per-student filters.
  - It keeps the class context: Stage, Course, Stage Course, Comment Profile, Topic and Unit.

### Fixed

- **Stage 4 instrument chips.** Guitar, Voice and the other specific instruments led to an empty bank, because Stage 4 Performance statements are all generic. Those chips are now disabled in Stage 4.
- **Reset Filters** now keeps the student's instrument. It is context, not a browsing filter.
- **Choosing a non-Performance category** no longer silently clears the instrument.

### Tests

- 5 new tests: I01–I04 and N01.
- Stage 5 tests now choose an instrument first.
- X01 now confirms that a mismatched-instrument strategy is prevented, where before it was only warned.
- 64/64 pass.

### Proposed, not applied

- `docs/PROPOSED_TEXT_CHANGES_v5.5.md` and `proposals/v5.5_text_changes.json` cover 2,407 statement-text changes in three separately approvable groups (A, B, C), awaiting approval.

## v5.3 — 17 Nov 2026

**Statement bank: unchanged.** The data block is byte-for-byte identical to v5.1/v5.2.

### Added

**Strengths ↔ Strategies cross-check**, agreed 17 Nov 2026.

These are reminders only: amber, never blocking Copy. They appear in two places:
- in each builder's checklist, as "Cross-check with …";
- in a new **Strengths ↔ Strategies cross-check** block in the Review & Tone Check panel.

The panel waits until both outputs have at least one statement. It then flags:

- **Instrument:** the Performance slots name different instruments (e.g. a Guitar strength with a Voice strategy). The generic "Instrument" counts as compatible with any instrument.
- **Topic (Stage 6) / Unit (Stage 4):** a topic or unit is used in one output but not the other.
- **Tier gap:** the same slot is two or more tiers apart between outputs (e.g. an Extensive Performance strength with an Elementary Performance strategy).
  - A one-level gap is not flagged.
  - A General strategy swapped into a slot is not compared, because it is a different category.

When nothing is flagged, the panel shows a green "no inconsistencies" line.

### Changed

- Both builders' checklists now refresh when either output changes, because the cross-check depends on both.

### Tests

- 7 new tests (X01–X07). v5.3 passes all 59.

## v5.2 — 17 Nov 2026

**Statement bank: unchanged.** All 3,520 records are identical to v5.1 (`5.1-fixed-stage6`), and the embedded data block is byte-for-byte the same. App logic, CSS and four small HTML hooks were changed. There is no backend, no accounts, no network calls and no student data.

### Decisions applied (agreed 17 Nov 2026)

| Question | Decision |
|---|---|
| Mixed topics (Stage 6) / units (Stage 4) in one comment | **Allow, with an amber warning** |
| Mixed tiers in one comment | **Allow freely** |
| Stage 4/5 General strategies (90 records) | **Optional slot swap:** a General strategy may replace one of P/C/L in Strategies to Improve |
| Sentral character limit | **Not set.** Live count only, until a verified figure is entered |

### Fixed

- **F1 Cross-stage comments.** With no Stage chosen, one comment could combine Stage 4, 5 and 6 sentences and still be copied. Selecting now requires a Stage. The bank can still be browsed, and an amber banner explains why.
- **F2 Music 1 / Music 2 and Preliminary / HSC mixing.** With Stage 6 chosen but Course or Stage Course unset (the default), one comment could combine courses and levels. Stage 6 selection now requires both.
- **F5 Stage 4/5 Category chip** read "General Musicianship" for the work ethic / behaviour / practice strategies. It now reads "General". Stage 6 "General Musicianship" is unchanged.
- **F6 Clicking the active Comment Profile chip** deselected it while the default profile silently stayed in force. The active profile can no longer be switched off; choose another profile instead.
- **F8 Accessibility.** Filter chips are now real buttons with `aria-pressed`, so they can be reached with Tab and toggled with Enter or Space. Other changes:
  - Drop zones, remove buttons, preview boxes and the character count have accessible labels or live regions.
  - A visible focus ring has been added.
- **F9 Sentence counter** now handles `?` / `!`, closing quotes and brackets, common abbreviations (e.g., i.e., etc.) and decimals.

### Added

- **Record-level validation.** Every time either output renders, and again at the moment of copying, each selected record is re-checked against the current Stage, Course and Stage Course, its slot, and its builder. Out-of-context or stale text cannot be copied, even if it reached a slot by some unexpected path.
- **New blocking checks:**
  - no repeated statement;
  - no first- or second-person words (I / my / we / our / you / your);
  - "them" and "themself" added to the pronoun check.
- **Amber warnings (non-blocking)** for mixed topics (Stage 6) or mixed units (Stage 4) within one comment.
- **General slot swap (Stage 4/5, Strategies to Improve only).** General cards show **Replace Performance / Replace Composition / Replace Listening** buttons, or can be dragged onto any Strategies slot.
  - At most one General strategy is allowed per comment.
  - The filled slot is tagged "General — in place of …".
  - Learning Strengths and Stage 6 are unchanged.
- **Character count and optional Sentral limit** for each output, separately.
  - The count shows while building ("N characters so far").
  - Enter a verified limit in the **Sentral limit** box. Copy is then disabled if the comment exceeds it.
  - The limit is remembered in this browser only. It ships blank.
- **Version display.** The header now shows the app version and the data version.
- **Read-only test hook** `window.__commentBuilderTest`, used by the regression suite. It has no visible effect.

### Changed behaviour (by design)

- **Topic and Unit are now browsing refinements.** Changing either no longer wipes the builders. This also resolves the v5.1 inconsistency where the Topic chip cleared selections but Reset Filters did not.
- **Stage, Course, Stage Course and Comment Profile changes still clear both builders**, as before.

### Unchanged

- **Data.** Every statement, ID and metadata field is unchanged.
- **Workflow.** The three-sentence, one-per-slot workflow and its slot orders are unchanged:
  - Stage 4/5: P/C/L;
  - Stage 6 Performance: P/M/A;
  - Stage 6 Composition: C/M/A;
  - Stage 6 Viva Voce: P/V/G;
  - Stage 6 Musicianship: P/A/G;
  - Stage 6 Composition/Musicianship: C/A/G.
- **Interface.** Filters, bank cards, drag-and-drop, previews, the review panel, Clear buttons, Reset Filters and clipboard copy with fallback all work as before.
- **Look.** The visual design and palette are unchanged.

### Known limits / still open

- The Sentral character limit for each field is still to be confirmed. Enter it in the app once known.
- Sentral paste of the en dash in "1600–1900" has not been tested.
- *(Resolved in v5.3: Strengths ↔ Strategies cross-check.)*
- Only Chrome was tested. Netlify deployment and mobile browsers have not been verified.
- In the data, 33 Stage 6/Stage 4 strategy sentences repeat word-for-word across tiers. About 79% of topic-tagged Stage 6 records do not name their topic in the text. Both are reported in `AUDIT_REPORT_v5.1.md` and were deliberately left untouched.

## v5.1-fixed-stage6 — baseline

Recovered source received via the migration package. See `AUDIT_REPORT_v5.1.md`.
