# Governing specification — Music Report Comment Builder

**Baseline:** Recovered source version `5.1-fixed-stage6` (an HTML title of Music Report Comment Builder). This specification records existing intended behaviour and proposed acceptance criteria; it is not a claim that all are currently implemented.

## Purpose and deployment

Standalone browser-based, Netlify-deployable (static) comment-building app for NSW Music Stage 4–6 reporting. Two distinct Sentral-ready outputs: **Learning Strengths** and **Strategies to Improve**. Preserve the browse/filter/choose and drag-and-drop interaction, previews, review panel, and copy actions.

## Comment construction

- Each output is exactly **three sentences**, with exactly one selected sentence per required category slot, in the active profile's specified order.
- Standard Stage 4/5 slot sequence: **Performance / Composition / Listening**.
- Stage 6 profile slots from source metadata: Performance = P/M/A; Composition = C/M/A; Viva Voce = P/V/G; Musicianship = P/A/G; Composition/Musicianship = C/A/G.
- Use **Australian English**, present tense and suitable impersonal report language. Avoid names, personal pronouns, the phrase “the student”, first-person voice, punitive/deficit language, colloquialisms and HSC performance predictions.
- Selected sentences must be context-compatible and semantically coherent; category and course/profile/topic rules cannot be bypassed by changing filters after selection.
- Report characters visibly for each output, but obtain the institution's actual Sentral character limit before hard-coding it. Never assert compatibility based solely on sentence count.

## Context and browsing distinctions

- **Context**: Stage (4, 5, 6), Stage 6 course (Music 1 or Music 2), Preliminary/HSC, reporting profile, curriculum topic or unit as appropriate.
- **Browsing refinements**: comment type, category, achievement tier (Extensive, Thorough, Sound, Elementary, Basic), instrument, specificity, tags/voice/length if already supported.
- Changes to *context* must invalidate or explicitly revalidate incompatible selections in both outputs. Do not silently allow stale statements to remain selected.
- Ordinary browse-filter reset should not wipe selected sentences or the established reporting context. Separate intentional “clear selection” actions for each output.
- Do not allow a selection to occupy a mismatched category or opposite comment type.

## Data preservation

- `statement_bank_v5.1.json` has 3,520 original records with unique IDs, split across Stage 4, 5, 6. Do not remove, paraphrase, deduplicate, or add records without explicit authorisation and a machine-readable diff.
- Each statement carries context fields such as stage, commentType, category, tier, instrument, course, stageCourse, courseProfile, topic, specificity and tags; nulls must be handled deliberately.
- Course-specific filters must not leak a Music 1 sentence into Music 2, or Preliminary into HSC, except for records explicitly designed as universal in their source data.
- Treat Stage 4/5 general strategy categories and Stage 6 instrument matching as **design questions to test**, not licences to silently discard material.

## Engineering priorities

1. Preserve and establish parity with the baseline app.
2. Harden selection validation against stage, course, stageCourse, courseProfile, topic, instrument, category and commentType mismatch.
3. Improve sentence counting, empty/invalid data handling, pronoun/name checks and copy eligibility; do not overclaim automatic semantic validation.
4. Add robust character counting with a configurable externally verified Sentral limit.
5. Supply reproducible regression tests, audit results, and a changelog.

## Non-goals unless separately requested

No unnecessary framework rewrite, cloud database, authentication, student profiles, analytics, automatic student assessment, AI-generated comments, or external API keys. No real student information in test fixtures.
