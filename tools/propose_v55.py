"""Builds the PROPOSED v5.5 statement-text changes (A: drop trailing 'as part of
senior music study'; B: neutral wording for placeholder topic labels; C: asset
framing for 22 deficit-worded Learning Strengths). Writes a machine-readable
diff only; it does NOT modify the bank. Usage: python3 -I tools/propose_v55.py"""
import json, re, collections as C
bank = json.load(open('data/statement_bank_v5.1.json', encoding='utf-8'))
S = bank['statements']
TAIL = ' as part of senior music study.'

# --- B: placeholder topic labels -> neutral, still topic-distinct wording
LABEL = [  # (regex for label as it appears, phrase it becomes)
    (r'mandatory and additional topic repertoire', 'the mandatory and additional topics'),
    (r'mandatory topic repertoire', 'the mandatory topic'),
    (r'additional topic repertoire', 'the additional topic'),
    (r'HSC elective topic(?: repertoire)?', 'the HSC topics'),
]
FRAMES = [  # (pattern with {X}, replacement with {Y})
    (r'^Examines {X} with', 'Examines repertoire from {Y} with'),
    (r'^Interprets {X} with', 'Interprets repertoire from {Y} with'),
    (r'^Presents {X} viva voce material with', 'Presents viva voce material on {Y} with'),
    (r'^Recognises features of {X} with', 'Recognises features of repertoire from {Y} with'),
    (r'^Refine {X} analysis by', 'Refine analysis of {Y} by'),
    (r'^Refine recognition of {X} by', 'Refine recognition of repertoire from {Y} by'),
    (r'^Shapes {X} compositional ideas with', 'Shapes compositional ideas for {Y} with'),
    (r'^Strengthen {X} composition tasks by', 'Strengthen composition tasks for {Y} by'),
    (r'^Strengthen {X} performance preparation by', 'Strengthen performance preparation for {Y} by'),
    (r'^Strengthen {X} viva voce preparation by', 'Strengthen viva voce preparation for {Y} by'),
]
def fix_placeholder(t):
    for lab, y in LABEL:
        for pat, rep in FRAMES:
            rx = re.compile(pat.replace('{X}', lab))
            if rx.search(t):
                return rx.sub(rep.replace('{Y}', y), t, count=1), True
    return t, False

# --- C: 22 deficit-worded strengths, rewritten by hand (asset framing, same tier)
C_REWRITES = {
 'P_GUITAR_BAS_01': 'Attempts simple guitar parts with support, building technical control and rhythmic accuracy.',
 'P_GUITAR_BAS_03': 'Demonstrates beginning guitar technique while attempting simple practical tasks with support.',
 'P_VOICE_BAS_02': 'Uses voice in practical tasks with prompting, building rhythmic accuracy.',
 'P_BASS_BAS_03': 'Contributes to bass activities with prompting, building technical control.',
 'P_BASS_BAS_05': 'Demonstrates beginning bass technique while developing confidence in simple practical tasks.',
 'P_SAXOPHONE_BAS_02': 'Plays short saxophone phrases with guidance, building rhythmic accuracy.',
 'P_SAXOPHONE_BAS_03': 'Demonstrates beginning saxophone technique while developing basic breath control.',
 'P_TRUMPET_BAS_02': 'Plays short trumpet phrases with guidance, building rhythmic accuracy.',
 'P_TRUMPET_BAS_03': 'Demonstrates beginning trumpet technique while developing basic breath support.',
 'P_CLARINET_BAS_02': 'Plays short clarinet phrases with guidance, building rhythmic accuracy.',
 'P_CLARINET_BAS_03': 'Demonstrates beginning clarinet technique while developing basic breath control.',
 'P_PIANO_BAS_02': 'Plays short piano patterns with guidance, building rhythmic accuracy.',
 'P_PIANO_BAS_03': 'Demonstrates beginning piano technique while developing basic hand coordination.',
 'P_DRUMS_BAS_02': 'Plays short drum patterns with guidance, building rhythmic accuracy.',
 'P_DRUMS_BAS_03': 'Demonstrates beginning drumming technique while developing basic coordination.',
 'C_ELE_04': 'Creates basic compositions with some organisation and an emerging use of musical contrast.',
 'C_BAS_01': 'Attempts simple compositional ideas with support, beginning to develop structural control.',
 'C_BAS_03': 'Develops simple musical ideas while beginning to apply the elements of music.',
 'L_ELE_02': 'Identifies some musical features by ear using basic terminology.',
 'L_BAS_04': 'Demonstrates emerging listening skills through beginning recognition of rhythm and pitch.',
 'S5_LS_P_BAS_INSTRUMENT_01': 'Attempts simple instrumental parts with support, building technical control and rhythmic accuracy.',
 'S5_LS_P_BAS_INSTRUMENT_03': 'Demonstrates beginning instrumental technique while attempting simple practical tasks with support.',
}

changes = []
byid = {s['id']: s for s in S}
for s in S:
    old = s['text']; new = old; why = []
    if new.endswith(TAIL):
        new = new[:-len(TAIL)] + '.'; why.append('A')
    new2, hit = fix_placeholder(new)
    if hit: new = new2; why.append('B')
    if s['id'] in C_REWRITES:
        new = C_REWRITES[s['id']]; why.append('C')
    if new != old:
        changes.append({'id': s['id'], 'change': '+'.join(why), 'old': old, 'new': new})

# --- checks on every proposed sentence
PRON = re.compile(r'\b(he|she|they|his|her|their|him|them|hers|theirs|himself|herself|themselves)\b', re.I)
problems = []
for c in changes:
    t = c['new']
    if PRON.search(t): problems.append((c['id'], 'pronoun'))
    if not t.endswith('.') or re.search(r'[.!?]\s+\S', t): problems.append((c['id'], 'sentence'))
    if 'the student' in t.lower(): problems.append((c['id'], 'the student'))
    if re.search(r'topic repertoire|HSC elective topic', t): problems.append((c['id'], 'placeholder left'))
newtext = {s['id']: s['text'] for s in S}
for c in changes: newtext[c['id']] = c['new']
ctx = C.defaultdict(list)
for s in S:
    ctx[(s['stage'], s['course'], s['stageCourse'], s['commentType'], s['category'], s['tier'], s['topic'], s['instrument'], s['unit'], newtext[s['id']])].append(s['id'])
oldctx = C.defaultdict(list)
for s in S:
    oldctx[(s['stage'], s['course'], s['stageCourse'], s['commentType'], s['category'], s['tier'], s['topic'], s['instrument'], s['unit'], s['text'])].append(s['id'])
new_dups = [v for v in ctx.values() if len(v) > 1]
old_dups = [v for v in oldctx.values() if len(v) > 1]

summary = C.Counter(c['change'] for c in changes)
json.dump({'from_version': bank['metadata']['version'], 'proposal': 'v5.5 text changes (NOT APPLIED)',
           'counts': summary, 'records_changed': len(changes), 'changes': changes},
          open('proposals/v5.5_text_changes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('records changed', len(changes), dict(summary))
print('problems', problems)
print('same-context duplicates before', len(old_dups), 'after', len(new_dups))
for v in new_dups:
    if v not in old_dups: print('  NEW DUP:', v, '|', newtext[v[0]][:110])
