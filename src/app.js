

(function(){
  "use strict";

  // ---------- Load data ----------
  const DATA = JSON.parse(document.getElementById('statement-data').textContent);
  const statements = DATA.statements;
  const TIERS = DATA.metadata.tiers;
  const INSTRUMENTS = DATA.metadata.instruments; // includes "Instrument" as first entry
  const TOP_LEVEL_STAGES = DATA.metadata.topLevelStages; // ["Stage 4","Stage 5","Stage 6"]
  const COMMENT_TYPES = DATA.metadata.commentTypes; // { learning_strength: "...", strategy_to_improve: "..." }
  const CATEGORIES = DATA.metadata.categories; // { P, C, L, G, M, A, V }
  const UNITS = DATA.metadata.units || []; // Stage 4 units, e.g. "Beats and Tunes"
  const SPECIFICITY_OPTIONS = DATA.metadata.specificityOptions || []; // ["unit_specific","generalisable","topic_specific"]
  const GENERAL_SUBCATEGORIES = DATA.metadata.generalSubcategories || [];
  const COURSES = DATA.metadata.courses || []; // ["Music 1","Music 2"]
  const STAGE_COURSES = DATA.metadata.stageCourses || []; // ["Preliminary","HSC"]
  const VOICE_TAGS = DATA.metadata.voiceTags || [];
  const STATEMENT_LENGTH_OPTIONS = DATA.metadata.statementLengthOptions || [];
  const TOPICS = DATA.metadata.topics || [];
  const COMMENT_PROFILES = DATA.metadata.commentProfiles || {}; // { "Stage 6 Performance": ["P","M","A"], ... }
  const CATEGORY_LABEL_OVERRIDES = DATA.metadata.categoryLabelOverrides || {};

  const APP_VERSION = '5.3';
  document.getElementById('data-status').textContent =
    `${statements.length} statements loaded · app v${APP_VERSION} · data ${DATA.metadata.version}`;

  // ---------- Constants ----------
  const CAT_LABELS = CATEGORIES;
  const COMMENT_TYPE_ORDER = ['learning_strength','strategy_to_improve'];
  const COMMENT_TYPE_SHORT = { learning_strength: 'Strength', strategy_to_improve: 'Strategy' };
  const BUILDER_PREFIX = { learning_strength: 'LS', strategy_to_improve: 'STI' };
  const SPECIFICITY_LABELS = { unit_specific: 'Unit-specific', generalisable: 'Generalisable', topic_specific: 'Topic-specific' };
  const VOICE_TAG_LABELS = {
    standard: 'Standard', topic_specific: 'Topic-specific', artistry: 'Artistry',
    craft: 'Craft', foundational_practice: 'Foundational Practice'
  };
  const STATEMENT_LENGTH_LABELS = { standard: 'Standard', expanded: 'Expanded' };
  const GENERAL_SUBCATEGORY_LABELS = {
    work_ethic: 'Work Ethic', classroom_behaviour: 'Classroom Behaviour', organisation: 'Organisation',
    participation: 'Participation', task_completion: 'Task Completion', home_practice: 'Home Practice',
    music_practice: 'Music Practice'
  };

  const STANDARD_PROFILE_NAME = 'Stage 4/5 Standard';
  const STAGE6_PROFILE_NAMES = Object.keys(COMMENT_PROFILES).filter(p => p !== STANDARD_PROFILE_NAME);
  const DEFAULT_STAGE6_PROFILE = STAGE6_PROFILE_NAMES[0] || null;

  const SLOT_ORDER = [1, 2, 3];

  // ---------- State ----------
  const state = {
    filters: {
      stage: null,           // "Stage 4" | "Stage 5" | "Stage 6"
      course: null,          // Stage 6: "Music 1" | "Music 2"
      stageCourse: null,     // Stage 6: "Preliminary" | "HSC"
      commentProfile: null,  // Stage 6: one of STAGE6_PROFILE_NAMES
      commentType: null,
      category: null,
      tier: null,
      unit: null,
      specificity: null,
      generalSubcategory: null,
      topic: null,
      voiceTag: null,
      statementLength: null,
      instrument: null
    },
    // selected[commentType] = [slot1, slot2, slot3]; each slot is
    // { statement, category } | null. The category recorded in the slot is
    // fixed at selection time so it stays valid even if the active profile
    // later changes (though profile changes clear selections anyway).
    selected: {
      learning_strength: [null, null, null],
      strategy_to_improve: [null, null, null]
    }
  };

  // ---------- Profile resolution ----------
  // Returns { name, categories: [c1,c2,c3], labels: {cat: label} }
  function getActiveProfile(){
    if (state.filters.stage === 'Stage 6'){
      const name = state.filters.commentProfile || DEFAULT_STAGE6_PROFILE;
      const categories = COMMENT_PROFILES[name] || ['P','M','A'];
      const labels = CATEGORY_LABEL_OVERRIDES[name] || {};
      return { name, categories, labels };
    }
    const categories = COMMENT_PROFILES[STANDARD_PROFILE_NAME] || ['P','C','L'];
    const labels = CATEGORY_LABEL_OVERRIDES[STANDARD_PROFILE_NAME] || {};
    return { name: STANDARD_PROFILE_NAME, categories, labels };
  }

  // v5.2: In Stage 4/5 the code "G" means General (work ethic, behaviour,
  // organisation, practice), not Stage 6 "General Musicianship".
  const STAGE45_G_LABEL = 'General';
  function categoryLabelForProfile(profile, cat){
    if (profile.name === STANDARD_PROFILE_NAME && cat === 'G') return STAGE45_G_LABEL;
    return profile.labels[cat] || CAT_LABELS[cat] || cat;
  }

  // ---------------------------------------------------------------------
  // LEGACY FALLBACK ONLY: automatic generic-instrument word substitution.
  // This was the primary mechanism in v2. As of v3, "Instrument" is a real,
  // purpose-written instrument value in the data bank, so this function is
  // no longer used in the main selection flow. It is retained only as a
  // fallback for any older data that might not yet have an "Instrument"
  // variant, and is not wired into any UI control.
  // ---------------------------------------------------------------------
  const GENERIC_RULES = [
    [/\bdrum kit\b/gi, 'instrument'],
    [/\bdrumming\b/gi, 'playing'],
    [/\bdrums\b/gi, 'the instrument'],
    [/\bdrum\b/gi, 'instrument'],
    [/\bvocal lines\b/gi, 'instrumental lines'],
    [/\bvocal technique\b/gi, 'instrumental technique'],
    [/\bvocal material\b/gi, 'instrumental material'],
    [/\bvocal activities\b/gi, 'instrumental activities'],
    [/\bvocal\b/gi, 'instrumental'],
    [/\bvocally\b/gi, 'on the instrument'],
    [/\bsings\b/gi, 'performs'],
    [/\bsinging\b/gi, 'performance'],
    [/\bsing\b/gi, 'perform'],
    [/\bvoice\b/gi, 'instrument'],
    [/\bguitar\b/gi, 'instrument'],
    [/\bbass\b/gi, 'instrument'],
    [/\bsaxophone\b/gi, 'instrument'],
    [/\btrumpet\b/gi, 'instrument'],
    [/\bclarinet\b/gi, 'instrument'],
    [/\bpiano\b/gi, 'instrument']
  ];

  function legacyGenericiseInstrument(text){
    let out = text;
    GENERIC_RULES.forEach(([pattern, repl]) => {
      out = out.replace(pattern, repl);
    });
    if (text.length && out.length){
      const origFirst = text.charAt(0);
      const newFirst = out.charAt(0);
      if (origFirst === origFirst.toUpperCase() && origFirst !== origFirst.toLowerCase()
          && newFirst === newFirst.toLowerCase() && newFirst !== newFirst.toUpperCase()){
        out = newFirst.toUpperCase() + out.slice(1);
      }
    }
    return out;
  }

  // ---------- Build filter chips ----------
  const NO_DESELECT = new Set(['commentProfile']);
  function buildChipRow(containerId, values, filterKey, getLabel, extraClass, onChange){
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    container.setAttribute('role', 'group');
    values.forEach(val => {
      // v5.2: real buttons so chips are keyboard- and screen-reader-operable.
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'chip';
      chip.setAttribute('aria-pressed', String(state.filters[filterKey] === val));
      if (extraClass){
        const cls = extraClass(val);
        if (cls) chip.classList.add(cls);
      }
      chip.textContent = getLabel ? getLabel(val) : val;
      chip.dataset.value = val;
      chip.addEventListener('click', () => {
        if (state.filters[filterKey] === val){
          // v5.2: the active Stage 6 comment profile cannot be switched off
          // (a default profile would otherwise stay in force invisibly).
          if (NO_DESELECT.has(filterKey)) return;
          state.filters[filterKey] = null;
        } else {
          state.filters[filterKey] = val;
          if (filterKey === 'category' && val !== 'P'){
            state.filters.instrument = null;
          }
        }
        if (onChange) onChange(val);
        renderFilters();
        renderBank();
        refreshBuilders();
      });
      container.appendChild(chip);
    });
  }

  // Re-build the Category chip row to match the categories available for the
  // currently active profile/stage. Called whenever stage or commentProfile
  // changes, since the valid category set differs.
  function rebuildCategoryChips(){
    const profile = getActiveProfile();
    let cats;
    if (state.filters.stage === 'Stage 6'){
      cats = profile.categories.slice();
    } else {
      cats = ['P','C','L','G'];
    }
    // If the currently-active category filter is no longer valid, clear it.
    if (state.filters.category && cats.indexOf(state.filters.category) === -1){
      state.filters.category = null;
    }
    buildChipRow('filter-category', cats, 'category',
      v => categoryLabelForProfile(profile, v),
      v => v === 'G' ? 'chip-general' : '');
  }

  // Rebuild the Comment Profile chip row (Stage 6 only).
  function rebuildCommentProfileChips(){
    buildChipRow('filter-commentProfile', STAGE6_PROFILE_NAMES, 'commentProfile',
      v => v.replace(/^Stage 6 /, ''),
      () => '',
      () => {
        // Profile changed: category set changes, so clear stale selections.
        clearAllSelections();
        rebuildCategoryChips();
        renderDropzoneLabels();
        renderBank();
      });
  }

  // Build Stage 6 topic choices dynamically from the selected
  // Course + Stage Course context, rather than showing stale topics that
  // belong to another course/year.
  function availableStage6Topics(){
    const values = [];
    statements.forEach(s => {
      if (s.stage !== 'Stage 6') return;
      if (state.filters.course && s.course !== state.filters.course) return;
      if (state.filters.stageCourse && s.stageCourse !== state.filters.stageCourse) return;
      if (s.topic && values.indexOf(s.topic) === -1){
        values.push(s.topic);
      }
    });
    return values;
  }

  function syncStage6TopicFilter(){
    if (state.filters.stage !== 'Stage 6') return;
    const validTopics = availableStage6Topics();
    if (state.filters.topic && validTopics.indexOf(state.filters.topic) === -1){
      state.filters.topic = null;
    }
  }

  function rebuildStage6TopicChips(){
    const topics = state.filters.stage === 'Stage 6' ? availableStage6Topics() : TOPICS;
    syncStage6TopicFilter();
    // v5.2: Topic is a browsing refinement. Mixed topics inside one comment
    // are allowed but flagged with an amber warning in validation, so a
    // topic change no longer wipes the builders.
    buildChipRow('filter-topic', topics, 'topic', v => v, null, null);
  }

  function stage6ContextChanged(){
    if (state.filters.stage === 'Stage 6'){
      syncStage6TopicFilter();
      rebuildStage6TopicChips();
      clearAllSelections();
      rebuildCategoryChips();
      renderDropzoneLabels();
    }
  }

  // When stage changes, the set of valid categories (and dropzone meanings)
  // changes, so clear all current selections to avoid stale mismatches.
  function clearAllSelections(){
    COMMENT_TYPE_ORDER.forEach(ct => {
      state.selected[ct] = [null, null, null];
      renderDropzones(ct);
      renderPreview(ct);
    });
    renderReview();
  }

  function onStageChange(){
    // Reset Stage-6-only and Stage-4/5-only filters that no longer apply.
    if (state.filters.stage !== 'Stage 6'){
      state.filters.course = null;
      state.filters.stageCourse = null;
      state.filters.commentProfile = null;
      state.filters.topic = null;
      state.filters.voiceTag = null;
      state.filters.statementLength = null;
    } else {
      if (!state.filters.commentProfile){
        state.filters.commentProfile = DEFAULT_STAGE6_PROFILE;
      }
      syncStage6TopicFilter();
      rebuildStage6TopicChips();
    }

    if (state.filters.stage !== 'Stage 4'){
      state.filters.unit = null;
      state.filters.specificity = null;
    }

    state.filters.generalSubcategory = null;
    state.filters.category = null;
    state.filters.instrument = null;
    rebuildCategoryChips();
    if (state.filters.stage === 'Stage 6'){
      rebuildCommentProfileChips();
    }
    clearAllSelections();
    renderDropzoneLabels();
  }

  function renderFilters(){
    const isStage6 = state.filters.stage === 'Stage 6';
    const isStage4 = state.filters.stage === 'Stage 4';

    document.querySelectorAll('#filter-stage .chip').forEach(chip => {
      chip.classList.toggle('active', state.filters.stage === chip.dataset.value);
    });

    // ---- Stage 6 only groups ----
    ['course-group','stageCourse-group','commentProfile-group','topic-group','voiceTag-group','statementLength-group'].forEach(id => {
      document.getElementById(id).style.display = isStage6 ? '' : 'none';
    });
    if (isStage6){
      syncStage6TopicFilter();
      rebuildStage6TopicChips();
      document.querySelectorAll('#filter-course .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.course === chip.dataset.value);
      });
      document.querySelectorAll('#filter-stageCourse .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.stageCourse === chip.dataset.value);
      });
      document.querySelectorAll('#filter-commentProfile .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.commentProfile === chip.dataset.value);
      });
      document.querySelectorAll('#filter-topic .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.topic === chip.dataset.value);
      });
      document.querySelectorAll('#filter-voiceTag .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.voiceTag === chip.dataset.value);
      });
      document.querySelectorAll('#filter-statementLength .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.statementLength === chip.dataset.value);
      });
    }

    // ---- Stage 4 only groups (Unit / Specificity) ----
    document.getElementById('unit-group').style.display = isStage4 ? '' : 'none';
    document.getElementById('specificity-group').style.display = isStage4 ? '' : 'none';
    if (isStage4){
      document.querySelectorAll('#filter-unit .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.unit === chip.dataset.value);
      });
      document.querySelectorAll('#filter-specificity .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.specificity === chip.dataset.value);
      });
    }

    // ---- General Subcategory (Stage 4/5, Strategies + General category only) ----
    const generalSubcatVisible = !isStage6 && state.filters.commentType === 'strategy_to_improve' && state.filters.category === 'G';
    document.getElementById('generalSubcategory-group').style.display = generalSubcatVisible ? '' : 'none';
    if (generalSubcatVisible){
      document.querySelectorAll('#filter-generalSubcategory .chip').forEach(chip => {
        chip.classList.toggle('active', state.filters.generalSubcategory === chip.dataset.value);
      });
    }

    // ---- Comment Type ----
    document.querySelectorAll('#filter-commentType .chip').forEach(chip => {
      chip.classList.toggle('active', state.filters.commentType === chip.dataset.value);
    });

    // ---- Category ----
    document.querySelectorAll('#filter-category .chip').forEach(chip => {
      chip.classList.toggle('active', state.filters.category === chip.dataset.value);
    });

    // ---- Tier ----
    document.querySelectorAll('#filter-tier .chip').forEach(chip => {
      chip.classList.toggle('active', state.filters.tier === chip.dataset.value);
    });

    // ---- Instrument (Performance only; mainly relevant for Stage 4/5) ----
    const instrumentDisabled = state.filters.category && state.filters.category !== 'P';
    document.getElementById('instrument-group').style.display = isStage6 ? 'none' : '';
    document.querySelectorAll('#filter-instrument .chip').forEach(chip => {
      chip.classList.toggle('active', state.filters.instrument === chip.dataset.value);
      chip.classList.toggle('disabled', instrumentDisabled);
    });
    document.getElementById('instrument-group').style.opacity = instrumentDisabled ? '0.45' : '1';

    // v5.2: keep assistive-technology state in step with the visual state.
    document.querySelectorAll('#filter-panel .chip').forEach(chip => {
      chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
      if (chip.classList.contains('disabled')) chip.setAttribute('aria-disabled', 'true');
      else chip.removeAttribute('aria-disabled');
    });
    renderContextNotice();
  }

  buildChipRow('filter-stage', TOP_LEVEL_STAGES, 'stage', null, null, onStageChange);
  buildChipRow('filter-course', COURSES, 'course', null, null, stage6ContextChanged);
  buildChipRow('filter-stageCourse', STAGE_COURSES, 'stageCourse', null, null, stage6ContextChanged);
  buildChipRow('filter-commentType', COMMENT_TYPE_ORDER, 'commentType',
    v => COMMENT_TYPES[v],
    v => v === 'strategy_to_improve' ? 'chip-strategy' : '',
    () => renderFilters());
  // Category chips are rebuilt dynamically by rebuildCategoryChips(); seed
  // with the Stage 4/5 standard set initially.
  buildChipRow('filter-category', ['P','C','L','G'], 'category',
    v => v === 'G' ? STAGE45_G_LABEL : CAT_LABELS[v],
    v => v === 'G' ? 'chip-general' : '',
    () => renderFilters());
  buildChipRow('filter-tier', TIERS, 'tier');
  buildChipRow('filter-unit', UNITS, 'unit');
  buildChipRow('filter-specificity', SPECIFICITY_OPTIONS, 'specificity',
    v => SPECIFICITY_LABELS[v] || v);
  buildChipRow('filter-generalSubcategory', GENERAL_SUBCATEGORIES, 'generalSubcategory',
    v => GENERAL_SUBCATEGORY_LABELS[v] || v);
  rebuildStage6TopicChips();
  buildChipRow('filter-voiceTag', VOICE_TAGS, 'voiceTag',
    v => VOICE_TAG_LABELS[v] || v);
  buildChipRow('filter-statementLength', STATEMENT_LENGTH_OPTIONS, 'statementLength',
    v => STATEMENT_LENGTH_LABELS[v] || v);
  buildChipRow('filter-instrument', INSTRUMENTS, 'instrument',
    v => v,
    v => v === 'Instrument' ? 'chip-instrument-generic' : '');

  document.getElementById('reset-filters').addEventListener('click', () => {
    // Reset Filters clears only the "browsing" filters used to narrow the
    // statement bank. It deliberately preserves Stage / Course / Stage
    // Course / Comment Profile / Comment Type (the active context) and does
    // NOT clear any statements already selected in the builders.
    state.filters.category = null;
    state.filters.tier = null;
    state.filters.unit = null;
    state.filters.specificity = null;
    state.filters.generalSubcategory = null;
    state.filters.topic = null;
    state.filters.voiceTag = null;
    state.filters.statementLength = null;
    state.filters.instrument = null;
    rebuildCategoryChips();
    renderFilters();
    renderBank();
    refreshBuilders();
  });

  // ---------- v5.2 Context lock & placement rules ----------
  // Reporting context must be fully chosen before anything can be placed,
  // so one comment can never mix stages, courses or Preliminary/HSC.
  function contextBlocker(){
    if (!state.filters.stage) return 'Choose a Stage first';
    if (state.filters.stage === 'Stage 6' && (!state.filters.course || !state.filters.stageCourse)){
      return 'Choose Course and Stage Course first';
    }
    return null;
  }

  function renderContextNotice(){
    const el = document.getElementById('context-notice');
    if (!el) return;
    const block = contextBlocker();
    el.textContent = block ? `${block} — statements can be browsed but not selected until the reporting context is set.` : '';
    el.style.display = block ? '' : 'none';
  }

  // Stage 4/5 only: a General strategy may stand in for one of P/C/L in the
  // Strategies to Improve builder (at most one per comment).
  function isGeneralSwap(s){
    return state.filters.stage !== 'Stage 6' && s.category === 'G' && s.commentType === 'strategy_to_improve';
  }

  // Returns null if statement s may occupy slot idx of its builder under the
  // current context; otherwise a plain-English reason.
  function placementProblem(s, idx){
    const block = contextBlocker();
    if (block) return block + '.';
    if (s.stage !== state.filters.stage){
      return `That is a ${s.stage} statement; the current Stage is ${state.filters.stage}.`;
    }
    if (state.filters.stage === 'Stage 6'){
      if (s.course !== state.filters.course){
        return `That is a ${s.course} statement; the current Course is ${state.filters.course}.`;
      }
      if (s.stageCourse !== state.filters.stageCourse){
        return `That is a ${s.stageCourse} statement; the current Stage Course is ${state.filters.stageCourse}.`;
      }
    }
    const profile = getActiveProfile();
    if (idx < 0 || idx > 2) return 'That category is not used by the current profile.';
    const expected = profile.categories[idx];
    if (s.category === expected) return null;
    if (isGeneralSwap(s)){
      const other = state.selected[s.commentType].findIndex((sl, i) => i !== idx && sl && sl.statement.category === 'G');
      if (other !== -1){
        return `Only one General strategy per comment — remove the one in slot ${other + 1} first.`;
      }
      return null;
    }
    const expectedLabel = categoryLabelForProfile(profile, expected);
    const actualLabel = categoryLabelForProfile(profile, s.category);
    const article = /^[aeiou]/i.test(actualLabel) ? 'an' : 'a';
    return `That is ${article} ${actualLabel} statement — drop it in the ${expectedLabel} zone.`;
  }

  // ---------- Bank rendering ----------
  function getFiltered(){
    return statements.filter(s => {
      if (state.filters.stage && s.stage !== state.filters.stage) return false;
      if (state.filters.course && s.course !== state.filters.course) return false;
      if (state.filters.stageCourse && s.stageCourse !== state.filters.stageCourse) return false;
      if (state.filters.commentType && s.commentType !== state.filters.commentType) return false;
      if (state.filters.category && s.category !== state.filters.category) return false;
      if (state.filters.tier && s.tier !== state.filters.tier) return false;
      if (state.filters.unit && s.unit !== state.filters.unit) return false;
      if (state.filters.specificity && s.specificity !== state.filters.specificity) return false;
      if (state.filters.generalSubcategory && s.subcategory !== state.filters.generalSubcategory) return false;
      if (state.filters.topic && s.topic !== state.filters.topic) return false;
      if (state.filters.voiceTag && s.voiceTag !== state.filters.voiceTag) return false;
      if (state.filters.statementLength && s.statementLength !== state.filters.statementLength) return false;
      if (state.filters.instrument){
        if (s.category !== 'P') return false; // instrument filter only applies to Performance
        if (s.instrument !== state.filters.instrument) return false;
      }
      // Stage 6: only show statements belonging to a category that's part
      // of the active profile, so the bank stays aligned with the dropzones.
      if (state.filters.stage === 'Stage 6'){
        const profile = getActiveProfile();
        if (profile.categories.indexOf(s.category) === -1) return false;
      }
      return true;
    });
  }

  function makeBadge(text, cls){
    const span = document.createElement('span');
    span.className = 'badge ' + cls;
    span.textContent = text;
    return span;
  }

  function renderBank(){
    const grid = document.getElementById('bank-grid');
    grid.innerHTML = '';
    const filtered = getFiltered();
    document.getElementById('bank-count').textContent =
      `Showing ${filtered.length} of ${statements.length} statements`;

    filtered.forEach(s => {
      const card = document.createElement('div');
      card.className = 'card';
      card.draggable = true;
      card.dataset.id = s.id;

      const badges = document.createElement('div');
      badges.className = 'badges';
      badges.appendChild(makeBadge(COMMENT_TYPE_SHORT[s.commentType], 'ct-' + s.commentType));
      badges.appendChild(makeBadge(s.category, 'cat-' + s.category));
      if (s.subcategoryLabel){
        badges.appendChild(makeBadge(s.subcategoryLabel, 'cat-G'));
      }
      badges.appendChild(makeBadge(s.tier, 'tier'));
      if (s.instrument){
        badges.appendChild(makeBadge(s.instrument, 'instrument'));
      }
      if (s.unit){
        badges.appendChild(makeBadge(s.unit, 'unit'));
      }
      if (s.specificity){
        badges.appendChild(makeBadge(SPECIFICITY_LABELS[s.specificity] || s.specificity, 'specificity'));
      }
      if (s.course){
        badges.appendChild(makeBadge(s.course, 'course'));
      }
      if (s.stageCourse){
        badges.appendChild(makeBadge(s.stageCourse, 'stageCourse'));
      }
      if (s.topic){
        badges.appendChild(makeBadge(s.topic, 'topic'));
      }
      if (s.voiceTag){
        badges.appendChild(makeBadge(VOICE_TAG_LABELS[s.voiceTag] || s.voiceTag, 'voiceTag'));
      }
      badges.appendChild(makeBadge(s.stage, 'stage'));
      card.appendChild(badges);

      const p = document.createElement('p');
      p.textContent = s.text;
      card.appendChild(p);

      const btn = document.createElement('button');
      btn.type = 'button';
      const isStrategy = s.commentType === 'strategy_to_improve';
      const isGeneral = s.category === 'G';
      btn.className = 'select-btn' + (isStrategy ? ' strategy-btn' : '') + (isGeneral ? ' general-btn' : '');

      const profile = getActiveProfile();
      const slotIndex = profile.categories.indexOf(s.category);
      const block = contextBlocker();

      if (block){
        // v5.2: context lock — browsing allowed, selecting not.
        btn.textContent = block;
        btn.disabled = true;
        card.draggable = false;
        card.classList.add('locked');
      } else if (slotIndex === -1 && isGeneralSwap(s)){
        // v5.2: Stage 4/5 General strategy — choose which slot it replaces.
        btn.dataset.skip = '1';
        const cap = document.createElement('div');
        cap.className = 'swap-caption';
        cap.textContent = 'Strategies to Improve — use in place of:';
        card.appendChild(cap);
        const row = document.createElement('div');
        row.className = 'swap-row';
        profile.categories.forEach((cat, idx) => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'swap-btn';
          const lbl = categoryLabelForProfile(profile, cat);
          b.textContent = `Replace ${lbl}`;
          b.setAttribute('aria-label', `Use this General strategy in place of ${lbl} in Strategies to Improve`);
          b.addEventListener('click', () => selectStatement(s, idx));
          row.appendChild(b);
        });
        card.appendChild(row);
      } else if (slotIndex === -1){
        // This statement's category isn't part of the active profile, so it
        // can't be placed in either builder right now.
        if (isGeneral){
          btn.textContent = s.subcategoryLabel
            ? `General — ${s.subcategoryLabel} (not used by current profile)`
            : 'General (not used by current profile)';
        } else {
          btn.textContent = `${CAT_LABELS[s.category]} (not used by current profile)`;
        }
        btn.disabled = true;
      } else {
        const label = categoryLabelForProfile(profile, s.category);
        btn.textContent = s.subcategoryLabel
          ? `Select for ${COMMENT_TYPES[s.commentType]} — ${label} (${s.subcategoryLabel})`
          : `Select for ${COMMENT_TYPES[s.commentType]} — ${label}`;
        btn.addEventListener('click', () => selectStatement(s));
      }
      if (!btn.dataset.skip) card.appendChild(btn);

      card.addEventListener('dragstart', e => {
        e.dataTransfer.setData('text/plain', s.id);
        card.classList.add('dragging');
      });
      card.addEventListener('dragend', () => card.classList.remove('dragging'));

      grid.appendChild(card);
    });
  }

  // ---------- Selection ----------
  // Determine which slot (0-based index) a statement's category occupies
  // under the currently active profile. Returns -1 if not part of the
  // profile.
  function slotIndexForCategory(category){
    const profile = getActiveProfile();
    return profile.categories.indexOf(category);
  }

  // v5.2: every placement path (button, swap button, drag-and-drop) goes
  // through placementProblem(), so nothing out of context can be placed.
  function selectStatement(s, slotIdx){
    const idx = (typeof slotIdx === 'number') ? slotIdx : slotIndexForCategory(s.category);
    const problem = placementProblem(s, idx);
    if (problem){
      showCopyMsg(s.commentType, problem, true);
      return false;
    }
    state.selected[s.commentType][idx] = { statement: s, category: s.category, swap: s.category !== getActiveProfile().categories[idx] };
    renderDropzones(s.commentType);
    renderPreview(s.commentType);
    renderReview();
  }

  function clearSelectionCell(commentType, slotIdx){
    state.selected[commentType][slotIdx] = null;
    renderDropzones(commentType);
    renderPreview(commentType);
    renderReview();
  }

  function clearBuilder(commentType){
    state.selected[commentType] = [null, null, null];
    renderDropzones(commentType);
    renderPreview(commentType);
    renderReview();
  }

  function getStatementText(sel){
    if (!sel) return '';
    return sel.statement.text;
  }

  // Update the slot labels (e.g. "1. Performance") for both builders to
  // reflect the categories required by the active profile.
  function renderDropzoneLabels(){
    const profile = getActiveProfile();
    COMMENT_TYPE_ORDER.forEach(commentType => {
      const prefix = BUILDER_PREFIX[commentType];
      SLOT_ORDER.forEach((slotNum, idx) => {
        const cat = profile.categories[idx];
        const label = categoryLabelForProfile(profile, cat);
        const labelEl = document.getElementById(`dz-label-${prefix}-${slotNum}`);
        labelEl.textContent = `${slotNum}. ${label}`;
        const dz = document.getElementById(`dz-${prefix}-${slotNum}`);
        dz.setAttribute('role', 'region');
        dz.setAttribute('aria-label', `${COMMENT_TYPES[commentType]}, slot ${slotNum}: ${label}`);
      });
      const profileLabelEl = document.getElementById(`profile-label-${prefix}`);
      if (state.filters.stage === 'Stage 6'){
        const catLabels = profile.categories.map(c => categoryLabelForProfile(profile, c)).join(' + ');
        profileLabelEl.textContent = `Profile: ${profile.name} (${catLabels})`;
      } else {
        profileLabelEl.textContent = '';
      }
    });
  }

  function renderDropzones(commentType){
    const prefix = BUILDER_PREFIX[commentType];
    const profile = getActiveProfile();
    SLOT_ORDER.forEach((slotNum, idx) => {
      const dz = document.getElementById(`dz-${prefix}-${slotNum}`);
      const content = dz.querySelector('.dz-content');
      const sel = state.selected[commentType][idx];
      const cat = profile.categories[idx];
      content.innerHTML = '';
      if (sel){
        const s = sel.statement;
        dz.classList.add('filled');
        const cardDiv = document.createElement('div');
        cardDiv.className = 'dz-card';

        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-btn';
        removeBtn.textContent = '✕';
        removeBtn.title = 'Remove';
        removeBtn.addEventListener('click', () => clearSelectionCell(commentType, idx));
        cardDiv.appendChild(removeBtn);

        removeBtn.type = 'button';
        removeBtn.setAttribute('aria-label', `Remove statement from slot ${slotNum}`);

        if (sel.swap){
          const note = document.createElement('div');
          note.className = 'swap-note';
          note.textContent = `General — in place of ${categoryLabelForProfile(profile, cat)}`;
          cardDiv.appendChild(note);
        }

        const textNode = document.createElement('div');
        textNode.style.marginTop = '4px';
        textNode.textContent = s.text;
        cardDiv.appendChild(textNode);

        const badgeRow = document.createElement('div');
        badgeRow.className = 'badges';
        badgeRow.style.marginTop = '6px';
        badgeRow.appendChild(makeBadge(s.tier, 'tier'));
        if (s.instrument){
          badgeRow.appendChild(makeBadge(s.instrument, 'instrument'));
        }
        if (s.unit){
          badgeRow.appendChild(makeBadge(s.unit, 'unit'));
        }
        if (s.subcategoryLabel){
          badgeRow.appendChild(makeBadge(s.subcategoryLabel, 'cat-G'));
        }
        badgeRow.appendChild(makeBadge(s.stage, 'stage'));
        cardDiv.appendChild(badgeRow);

        content.appendChild(cardDiv);
      } else {
        dz.classList.remove('filled');
        const placeholder = document.createElement('span');
        placeholder.className = 'dz-placeholder';
        const label = categoryLabelForProfile(profile, cat);
        placeholder.textContent = `Drag or select a ${COMMENT_TYPES[commentType]} — ${label} statement.`;
        content.appendChild(placeholder);
      }
    });
  }

  // Drag & drop on dropzones
  COMMENT_TYPE_ORDER.forEach(commentType => {
    const prefix = BUILDER_PREFIX[commentType];
    SLOT_ORDER.forEach((slotNum, idx) => {
      const dz = document.getElementById(`dz-${prefix}-${slotNum}`);
      dz.addEventListener('dragover', e => {
        e.preventDefault();
        dz.classList.add('dragover');
      });
      dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
      dz.addEventListener('drop', e => {
        e.preventDefault();
        dz.classList.remove('dragover');
        const id = e.dataTransfer.getData('text/plain');
        const s = statements.find(st => st.id === id);
        if (!s) return;

        if (s.commentType !== commentType){
          showCopyMsg(commentType,
            `That is a "${COMMENT_TYPES[s.commentType]}" statement — drop it in the ${COMMENT_TYPES[s.commentType]} builder.`,
            true);
          return;
        }
        // Context, category and General-swap rules are all in placementProblem().
        selectStatement(s, idx);
      });
    });
  });

  // ---------- Preview & validation ----------
  const PRONOUNS = /\b(he|she|they|his|her|their|him|them|hers|theirs|himself|herself|themselves|themself)\b/i;
  const FIRST_SECOND_PERSON = /\b(I|me|my|mine|myself|we|us|our|ours|ourselves|you|your|yours|yourself)\b/;

  // v5.2: sentence counter that copes with ? and !, closing quotes or
  // brackets, common abbreviations and decimals. It is a backstop only:
  // comment text comes from the bank, which is one sentence per record.
  const ABBREVIATIONS = /\b(e\.g|i\.e|etc|vs|approx|cf|Mr|Mrs|Ms|Dr|St|No)\./gi;
  function countSentences(text){
    const masked = text
      .replace(ABBREVIATIONS, m => m.replace(/\./g, '§'))
      .replace(/(\d)\.(\d)/g, '$1§$2');
    return (masked.match(/[.!?]+["'”’)]*(?=\s|$)/g) || []).length;
  }

  // ---------- v5.2 Character limits (per output, stored in this browser) ----------
  // No Sentral limit is assumed. A limit applies only once the user enters
  // a verified figure; until then the live count is informational.
  const LIMIT_KEY = { learning_strength: 'rbscCommentBuilder.charLimit.LS', strategy_to_improve: 'rbscCommentBuilder.charLimit.STI' };
  function getCharLimit(commentType){
    let v = null;
    try { v = window.localStorage.getItem(LIMIT_KEY[commentType]); } catch (e) { v = null; }
    if (v === null || v === undefined) v = charLimitMemory[commentType];
    const n = parseInt(v, 10);
    return Number.isFinite(n) && n > 0 ? n : null;
  }
  const charLimitMemory = { learning_strength: null, strategy_to_improve: null };
  function setCharLimit(commentType, raw){
    const n = parseInt(raw, 10);
    const val = Number.isFinite(n) && n > 0 ? String(n) : null;
    charLimitMemory[commentType] = val;
    try {
      if (val) window.localStorage.setItem(LIMIT_KEY[commentType], val);
      else window.localStorage.removeItem(LIMIT_KEY[commentType]);
    } catch (e) { /* storage unavailable: keep in memory for this session */ }
  }

  function renderCharCount(commentType, comment){
    const prefix = BUILDER_PREFIX[commentType];
    const el = document.getElementById(`charcount-${prefix}`);
    if (!el) return;
    const n = comment ? comment.length : partialText(commentType).length;
    const limit = getCharLimit(commentType);
    const label = comment ? `${n} characters` : `${n} characters so far`;
    el.textContent = limit ? `${label} / limit ${limit}` : `${label} (no limit set)`;
    el.classList.toggle('over', !!(limit && n > limit));
  }

  function partialText(commentType){
    return state.selected[commentType].filter(Boolean).map(getStatementText).join(' ');
  }

  function buildComment(commentType){
    const sel = state.selected[commentType];
    if (!sel[0] || !sel[1] || !sel[2]) return null;
    return [getStatementText(sel[0]), getStatementText(sel[1]), getStatementText(sel[2])].join(' ');
  }

  function renderPreview(commentType){
    const prefix = BUILDER_PREFIX[commentType];
    const box = document.getElementById(`preview-${prefix}`);
    const comment = buildComment(commentType);
    const copyBtn = document.getElementById(`copy-${prefix}`);
    const profile = getActiveProfile();
    const catLabels = profile.categories.map(c => categoryLabelForProfile(profile, c));

    if (!comment){
      box.textContent = `Select one ${catLabels[0]}, one ${catLabels[1]} and one ${catLabels[2]} ${COMMENT_TYPES[commentType]} statement.`;
      copyBtn.disabled = true;
    } else {
      box.textContent = comment;
    }

    renderCharCount(commentType, comment);
    renderValidation(commentType, comment);
  }

  // v5.2: validation re-checks every selected record against the CURRENT
  // reporting context, so stale or out-of-context text can never be copied,
  // whatever path put it there.
  function validateComment(commentType){
    const comment = buildComment(commentType);
    const sel = state.selected[commentType];
    const profile = getActiveProfile();
    const catLabels = profile.categories.map(c => categoryLabelForProfile(profile, c));
    const checks = [];   // blocking
    const warnings = []; // amber, non-blocking

    const swapAllowed = state.filters.stage !== 'Stage 6' && commentType === 'strategy_to_improve';
    checks.push({
      label: `One ${catLabels[0]}, one ${catLabels[1]} and one ${catLabels[2]} ${COMMENT_TYPES[commentType]} statement selected` +
        (swapAllowed ? ' (General may replace one)' : ''),
      pass: sel.every(slot => !!slot)
    });
    if (!comment) return { comment, checks, warnings, allPass: false };

    // Context: stage, course, stage course
    const ctxProblems = [];
    sel.forEach((slot, i) => {
      const s = slot.statement;
      if (s.stage !== state.filters.stage) ctxProblems.push(`slot ${i + 1} is ${s.stage}`);
      if (state.filters.stage === 'Stage 6'){
        if (s.course !== state.filters.course) ctxProblems.push(`slot ${i + 1} is ${s.course || 'no course'}`);
        if (s.stageCourse !== state.filters.stageCourse) ctxProblems.push(`slot ${i + 1} is ${s.stageCourse || 'no stage course'}`);
      }
    });
    const ctxLabel = state.filters.stage === 'Stage 6'
      ? `${state.filters.stage}, ${state.filters.course || '—'} ${state.filters.stageCourse || '—'}`
      : (state.filters.stage || 'no Stage chosen');
    checks.push({
      label: `All statements match the reporting context (${ctxLabel})` + (ctxProblems.length ? ` — ${ctxProblems.join('; ')}` : ''),
      pass: !!state.filters.stage && !contextBlocker() && ctxProblems.length === 0
    });

    // Slot / type integrity
    const slotProblems = [];
    let generalCount = 0;
    sel.forEach((slot, i) => {
      const s = slot.statement;
      if (s.commentType !== commentType) slotProblems.push(`slot ${i + 1} is a ${COMMENT_TYPES[s.commentType]} statement`);
      if (s.category === profile.categories[i]) return;
      if (swapAllowed && s.category === 'G'){ generalCount++; return; }
      slotProblems.push(`slot ${i + 1} holds ${categoryLabelForProfile(profile, s.category)}, expected ${catLabels[i]}`);
    });
    if (generalCount > 1) slotProblems.push('more than one General strategy');
    checks.push({
      label: 'Each statement is in the correct slot and builder' + (slotProblems.length ? ` — ${slotProblems.join('; ')}` : ''),
      pass: slotProblems.length === 0
    });

    const texts = sel.map(slot => slot.statement.text);
    checks.push({ label: 'No statement repeated', pass: new Set(texts).size === texts.length });

    const sentenceCount = countSentences(comment);
    checks.push({ label: `Exactly three sentences (found ${sentenceCount})`, pass: sentenceCount === 3 });

    checks.push({ label: 'No third-person pronouns (he/she/they/his/her/their/them, etc.)', pass: !PRONOUNS.test(comment) });
    checks.push({ label: 'No first- or second-person words (I/my/we/our/you/your)', pass: !FIRST_SECOND_PERSON.test(comment) });
    checks.push({ label: 'Does not contain the phrase "the student"', pass: !/\bthe student\b/i.test(comment) });
    checks.push({ label: 'Comment ends with a full stop', pass: comment.trim().endsWith('.') });

    const limit = getCharLimit(commentType);
    if (limit){
      checks.push({ label: `Within the character limit (${comment.length} / ${limit})`, pass: comment.length <= limit });
    }

    // v5.3: Strengths <-> Strategies cross-check reminders (non-blocking)
    crossCheckWarnings().forEach(w => warnings.push(`Cross-check with ${COMMENT_TYPES[otherType(commentType)]}: ${w}`));

    // Amber warnings (allowed, but worth a second look)
    if (state.filters.stage === 'Stage 6'){
      const topics = [...new Set(sel.map(slot => slot.statement.topic).filter(Boolean))];
      if (topics.length > 1) warnings.push(`Mixed topics in one comment: ${topics.join(', ')}`);
    }
    if (state.filters.stage === 'Stage 4'){
      const units = [...new Set(sel.map(slot => slot.statement.unit).filter(Boolean))];
      if (units.length > 1) warnings.push(`Mixed units in one comment: ${units.join(', ')}`);
    }

    return { comment, checks, warnings, allPass: checks.every(c => c.pass) };
  }

  function renderValidation(commentType, comment){
    const prefix = BUILDER_PREFIX[commentType];
    const container = document.getElementById(`validation-${prefix}`);
    const copyBtn = document.getElementById(`copy-${prefix}`);
    container.innerHTML = '';

    if (!comment){
      copyBtn.disabled = true;
      return;
    }

    const result = validateComment(commentType);
    const ul = document.createElement('ul');
    result.checks.forEach(chk => {
      const li = document.createElement('li');
      li.className = chk.pass ? 'ok' : 'fail';
      li.textContent = (chk.pass ? '✔ ' : '✘ ') + chk.label;
      ul.appendChild(li);
    });
    result.warnings.forEach(w => {
      const li = document.createElement('li');
      li.className = 'warn';
      li.textContent = '⚠ ' + w + ' (allowed — check this is intended)';
      ul.appendChild(li);
    });
    container.appendChild(ul);

    copyBtn.disabled = !result.allPass;
  }

  // ---------- Review / tone-check panel ----------
  // ---------- v5.3 Strengths <-> Strategies cross-check ----------
  // Reminders only: compares the two outputs for the same student and flags
  // likely inconsistencies. Never blocks copying.
  function otherType(commentType){
    return commentType === 'learning_strength' ? 'strategy_to_improve' : 'learning_strength';
  }

  function crossCheckWarnings(){
    const ls = state.selected.learning_strength;
    const sti = state.selected.strategy_to_improve;
    if (!ls.some(Boolean) || !sti.some(Boolean)) return [];
    const out = [];
    const profile = getActiveProfile();

    // Instrument: compare the Performance slots. The generic "Instrument"
    // value is compatible with any specific instrument.
    const pIdx = profile.categories.indexOf('P');
    if (pIdx !== -1 && ls[pIdx] && sti[pIdx]){
      const a = ls[pIdx].statement.instrument, b = sti[pIdx].statement.instrument;
      if (a && b && a !== b && a !== 'Instrument' && b !== 'Instrument'){
        out.push(`Performance instrument differs (Strengths: ${a}; Strategies: ${b})`);
      }
    }

    // Topic (Stage 6) / Unit (Stage 4): any value used in one output but not the other.
    const field = state.filters.stage === 'Stage 6' ? 'topic' : (state.filters.stage === 'Stage 4' ? 'unit' : null);
    if (field){
      const vals = arr => [...new Set(arr.filter(Boolean).map(sl => sl.statement[field]).filter(Boolean))];
      const a = vals(ls), b = vals(sti);
      const onlyA = a.filter(v => b.indexOf(v) === -1), onlyB = b.filter(v => a.indexOf(v) === -1);
      if (a.length && b.length && (onlyA.length || onlyB.length)){
        const noun = field === 'topic' ? 'Topic' : 'Unit';
        out.push(`${noun} differs (Strengths: ${a.join(', ')}; Strategies: ${b.join(', ')})`);
      }
    }

    // Tier: same slot, two or more levels apart (e.g. Extensive strength
    // with an Elementary strategy for the same area).
    profile.categories.forEach((cat, i) => {
      const a = ls[i], b = sti[i];
      if (!a || !b || b.swap) return;
      const ta = TIERS.indexOf(a.statement.tier), tb = TIERS.indexOf(b.statement.tier);
      if (ta !== -1 && tb !== -1 && Math.abs(ta - tb) >= 2){
        out.push(`${categoryLabelForProfile(profile, cat)} tier gap (Strengths: ${a.statement.tier}; Strategies: ${b.statement.tier})`);
      }
    });
    return out;
  }

  function renderCrossCheck(){
    const el = document.getElementById('crosscheck');
    if (!el) return;
    const ws = crossCheckWarnings();
    el.innerHTML = '';
    const ls = state.selected.learning_strength.some(Boolean), sti = state.selected.strategy_to_improve.some(Boolean);
    if (!ls || !sti){
      el.textContent = 'Shown once both outputs have at least one statement.';
      el.className = 'review-text empty';
      return;
    }
    el.className = 'review-text' + (ws.length ? ' crosscheck-warn' : ' crosscheck-ok');
    if (!ws.length){
      el.textContent = '✔ No instrument, topic/unit or tier inconsistencies found between Strengths and Strategies.';
      return;
    }
    const ul = document.createElement('ul');
    ws.forEach(w => { const li = document.createElement('li'); li.textContent = '⚠ ' + w; ul.appendChild(li); });
    el.appendChild(ul);
    const note = document.createElement('div');
    note.className = 'crosscheck-note';
    note.textContent = 'Reminder only — copying is still allowed. Check both comments describe the same student.';
    el.appendChild(note);
  }

  function renderReview(){
    // v5.3: a change in either output can change the cross-check, so
    // re-run both builders' validation lists.
    COMMENT_TYPE_ORDER.forEach(ct => renderValidation(ct, buildComment(ct)));
    renderCrossCheck();
    COMMENT_TYPE_ORDER.forEach(commentType => {
      const prefix = BUILDER_PREFIX[commentType];
      const el = document.getElementById(`review-${prefix}`);
      const comment = buildComment(commentType);
      if (comment){
        el.textContent = comment;
        el.classList.remove('empty');
      } else {
        el.textContent = 'Not yet complete.';
        el.classList.add('empty');
      }
    });
  }

  function showCopyMsg(commentType, msg, isError){
    const prefix = BUILDER_PREFIX[commentType];
    const el = document.getElementById(`copy-msg-${prefix}`);
    el.textContent = msg;
    el.style.color = isError ? '#C0392B' : '#2e7d32';
    setTimeout(() => { el.textContent = ''; }, 2500);
  }

  function copyComment(commentType){
    const comment = buildComment(commentType);
    if (!comment) return;
    // v5.2: re-validate at the moment of copying, not only when rendering.
    if (!validateComment(commentType).allPass){
      showCopyMsg(commentType, 'Not copied — fix the items marked ✘ first.', true);
      renderPreview(commentType);
      return;
    }
    const label = COMMENT_TYPES[commentType];
    navigator.clipboard.writeText(comment).then(() => {
      showCopyMsg(commentType, `${label} copied to clipboard — ready to paste into Sentral.`);
    }).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = comment;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showCopyMsg(commentType, `${label} copied to clipboard — ready to paste into Sentral.`);
    });
  }

  // v5.2: validation depends on the current context, so re-run it whenever
  // a filter changes.
  function refreshBuilders(){
    COMMENT_TYPE_ORDER.forEach(ct => renderPreview(ct));
  }

  // ---------- Buttons ----------
  COMMENT_TYPE_ORDER.forEach(commentType => {
    const prefix = BUILDER_PREFIX[commentType];
    document.getElementById(`copy-${prefix}`).addEventListener('click', () => copyComment(commentType));
    document.getElementById(`clear-${prefix}`).addEventListener('click', () => clearBuilder(commentType));
    const limitInput = document.getElementById(`charlimit-${prefix}`);
    if (limitInput){
      const current = getCharLimit(commentType);
      limitInput.value = current ? String(current) : '';
      limitInput.addEventListener('input', () => {
        setCharLimit(commentType, limitInput.value);
        renderPreview(commentType);
      });
    }
  });

  // ---------- Init ----------
  renderFilters();
  renderDropzoneLabels();
  renderBank();
  // Expose read-only hooks for automated regression tests (no UI effect).
  window.__commentBuilderTest = { countSentences, validateComment, crossCheckWarnings, state, APP_VERSION };
  COMMENT_TYPE_ORDER.forEach(commentType => {
    renderDropzones(commentType);
    renderPreview(commentType);
  });
  renderReview();
})();
