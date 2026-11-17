# Baseline technical audit

## Directly verified from recovered source

- Format: **self-contained static HTML** with embedded CSS, data JSON and JavaScript.
- Embedded version: `5.1-fixed-stage6`.
- Source size: **3,719,039 bytes**.
- Statement count: **3,520**, Stage 4 **285**, Stage 5 **595**, Stage 6 **2640**.
- Unique IDs: **3,520** (no duplicate IDs in baseline).
- Profiles and categories are defined in `metadata.commentProfiles` / `metadata.categories`.
- The current `renderValidation()` implementation checks three nonempty slots, a punctuation-based approximation of sentence count, limited pronouns, the phrase “the student”, and final full stop. It does **not** visibly enforce source-record compatibility or a character limit in that function.
- Current copy button eligibility depends on the tests above, so out-of-context selections or excessive text may not be caught at copy time.
- The app uses browser clipboard API with a fallback.

## Known risks to investigate (not demonstrated failures)

- Stage/course/course profile/topic consistency when user switches context after making selections.
- Instrument specificity and generic “Instrument” handling in Stage 5/6.
- Stage 4/5 General strategy records (category G) vs standard P/C/L three-slot profile.
- Browsing reset vs context change and selection persistence.
- Sentence counting for abbreviation, punctuation variants, missing stops, and pasted content.
- Actual maximum character count for the destination Sentral report fields; **not supplied and must not be invented**.
- Semantically contradictory choices, duplicate text, or mismatched achievement tiers.
- Browser compatibility and accessibility on desktop and mobile.

## Verification limits

This package was assembled from a recovered Library HTML source. It has been parsed and metadata and IDs checked, but **browser interaction and Netlify deployment were not executed** during this migration. This is a transfer baseline, not a certification that the app is defect-free.
