"""v5.7 (20 Nov 2026): Stage 4 Sentral limit raised to 200 characters per
comment box (Justin Ossher). The 155 short Stage 4 sentences are rewritten in
Justin's voice: plain, direct, practical musician's language (feel, groove,
by ear, in time, with others), wording that steps down genuinely by tier.
Same IDs, tags and structure; only `text` changes. Every sentence <= 66
characters, so any three sentences + 2 spaces <= 200.
All v5.6 checks still apply (no pronouns, one sentence, Australian spelling,
no deficit wording, Strengths present-tense third person, Strategies imperative,
no duplicates).
Usage:
  python3 -I tools/rewrite_stage4_short_v57.py data/statement_bank_v5.6.json data/statement_bank_v5.7.json
"""
import json, re, sys, collections as C

SRC, OUT = sys.argv[1], sys.argv[2]
LIMIT = 200
MAX = (LIMIT - 2) // 3  # 66
TIERS = ['EXT', 'THR', 'SND', 'ELE', 'BAS']
UNITS = {'Beats and Tunes': 'BT', 'Rocking the Guitar': 'RTG', 'Sound Lab': 'SL', 'Jazz': 'JZ'}

# [unit][LS|STI][category] = five sentences, Extensive -> Basic
T = {
 'Beats and Tunes': {
  'LS': {
   'P': ['Plays rhythm and melody with real control, feel and intent.',
         'Plays rhythms and keyboard melodies accurately and in time.',
         'Plays rhythms and keyboard parts with a steady pulse.',
         'Plays simple rhythms with a pulse that is growing steadier.',
         'Plays simple rhythms when counted in and supported.'],
   'C': ['Composes inventive rhythms that groove and hold together well.',
         'Composes well-organised four-bar rhythms with a clear shape.',
         'Composes four-bar rhythms that sit on a steady pulse.',
         'Composes short rhythms from familiar patterns and note values.',
         'Composes short rhythm patterns with step-by-step support.'],
   'L': ['Hears and describes how the elements work together in a piece.',
         'Picks out musical elements accurately by ear and names each one.',
         'Identifies common musical elements by ear with confidence.',
         'Identifies some musical elements by ear when guided.',
         'Feels and recognises the beat and rhythm with support.']},
  'STI': {
   'P': ['Bring more dynamic contrast and feel to each performance.',
         'Keep faster rhythm passages as accurate as the slower ones.',
         'Practise keyboard parts slowly, then lift the tempo once secure.',
         'Count aloud and move to the beat to keep a steadier pulse.',
         'Clap and say each rhythm before playing it.'],
   'C': ['Push rhythm ideas further with bolder contrast and development.',
         'Mark dynamics and tempo so others can play the composition well.',
         'Use repetition and contrast to give rhythms a clear shape.',
         'Check each bar adds up to the right number of beats.',
         'Build rhythms from familiar note values, one bar at a time.'],
   'L': ['Back up listening answers with precise moments from the music.',
         'Use more specific musical terms to explain what is heard.',
         'Listen for one element at a time, then put the picture together.',
         'Use the elements list as a guide when listening.',
         'Tap the beat while listening, then describe what changes.']}},
 'Rocking the Guitar': {
  'LS': {
   'P': ['Plays riffs and chords fluently, with real feel for the style.',
         'Plays chords and riffs with secure, well-timed changes.',
         'Plays common chords with steady, even strumming.',
         'Plays simple chords, with changes becoming smoother.',
         'Plays simple chord shapes and riffs with support.'],
   'C': ['Writes inventive riffs, notated clearly in TAB and on the staff.',
         'Writes well-shaped riffs that sit neatly over a chord pattern.',
         'Writes a clear riff over the C, Am, G and F progression.',
         'Writes a short riff using familiar notes and patterns.',
         'Writes a short riff in TAB with support.'],
   'L': ['Explains rock styles and the features of each with real depth.',
         'Identifies rock features and instruments accurately by ear.',
         'Identifies common rock features and instruments by ear.',
         'Identifies some rock features by ear when guided.',
         'Recognises a guitar riff in a song with support.']},
  'STI': {
   'P': ['Bring dynamics and feel to Song Ladder songs, not just accuracy.',
         'Keep chord changes clean and in time at full tempo.',
         'Practise chord changes slowly, then build up to song tempo.',
         'Practise moving between two chords until the change is smooth.',
         'Practise one chord shape a day until the fingers find it easily.'],
   'C': ['Develop riffs further with syncopation and variation.',
         'Check the TAB and staff versions of each riff match exactly.',
         'Repeat the riff, then vary it to give the piece structure.',
         'Use notes from each chord to shape the riff.',
         'Start the riff on a chord note and repeat it.'],
   'L': ['Connect rock features to the history and context of the style.',
         'Use precise musical terms to describe rock features.',
         'Listen for the riff, the beat and the chords one at a time.',
         'Name the instruments first, then listen for other features.',
         'Listen for the guitar part and describe what it does.']}},
 'Sound Lab': {
  'LS': {
   'P': ['Performs layered parts in precise time, with a keen ensemble ear.',
         'Holds a part securely while listening to the layers around it.',
         'Keeps a steady part going within a layered texture.',
         'Performs a simple layer with growing steadiness.',
         'Performs a simple layer alongside others with support.'],
   'C': ['Builds rich, purposeful layers in a DAW with a clear musical plan.',
         'Builds clear DAW layers with well-chosen contrasts in texture.',
         'Builds a DAW composition with clear, distinct layers.',
         'Builds simple layers in a DAW when guided.',
         'Builds a short DAW piece with support.'],
   'L': ['Analyses texture and instrumentation in real detail.',
         'Identifies textures and instruments accurately by ear.',
         'Identifies layers and common instruments by ear.',
         'Identifies some layers and instruments when guided.',
         'Recognises thick and thin textures with support.']},
  'STI': {
   'P': ['Balance dynamics within the ensemble so every layer is heard.',
         'Listen across all the layers to lock in timing with others.',
         'Count rests carefully to come in on time.',
         'Practise one layer until it feels steady and secure.',
         'Follow a partner’s part to stay in time.'],
   'C': ['Shape the texture with more deliberate build-ups and drop-outs.',
         'Add a contrasting section so the DAW piece goes somewhere new.',
         'Give each layer a clear job in the music.',
         'Add one new layer at a time and listen back each time.',
         'Start with a beat layer, then add a melody on top.'],
   'L': ['Use evidence from the score to support answers on texture.',
         'Describe textures using precise musical terms.',
         'Count the layers heard in each excerpt.',
         'Listen for which instruments enter and drop out.',
         'Listen for when the music gets thicker or thinner.']}},
 'Jazz': {
  'LS': {
   'P': ['Improvises with confidence and real swing over the 12-bar blues.',
         'Plays the 12-bar blues securely with a relaxed swing feel.',
         'Plays the 12-bar blues with a steady pulse.',
         'Plays sections of the 12-bar blues when guided.',
         'Plays simple blues patterns with support.'],
   'C': ['Creates inventive blues phrases and riffs that sit right in style.',
         'Creates clear, shapely melodies from the blues scale.',
         'Creates short phrases using the blues scale.',
         'Creates simple riffs using some blues notes.',
         'Creates a short blues riff with support.'],
   'L': ['Explains jazz styles and the features of each in real depth.',
         'Identifies swing, the blues and the roles in a jazz band well.',
         'Identifies the 12-bar blues and swing feel by ear.',
         'Identifies some jazz features by ear when guided.',
         'Recognises jazz instruments with support.']},
  'STI': {
   'P': ['Shape improvisations with phrasing, space and dynamics.',
         'Keep the swing feel relaxed and steady right through the form.',
         'Count the 12 bars aloud to stay on track.',
         'Practise the C7, F7 and G7 changes slowly.',
         'Practise the blues scale slowly, a few notes at a time.'],
   'C': ['Develop one motif further each time instead of starting fresh.',
         'Answer each phrase with a contrasting idea, like a conversation.',
         'Repeat and vary short blues-scale phrases.',
         'Start with three or four blues-scale notes and build from there.',
         'Build a riff from two notes of the blues scale.'],
   'L': ['Compare jazz eras using precise musical examples.',
         'Use precise terms for swing feel and band roles.',
         'Listen for the walking bass and the chord changes.',
         'Count along to hear where the 12-bar form starts again.',
         'Listen for the swing feel and tap along.']}},
}

G = {  # Strategies to Improve, General (swap-in), Extensive -> Basic
 'WORK_ETHIC': ['Take more initiative in refining work beyond what is asked.',
                'Act on feedback promptly and independently.',
                'Stay focused through to the end of each task.',
                'Ask for help early when a task is unclear.',
                'Complete each step of a task before moving on.'],
 'CLASSROOM_BEHAVIOUR': ['Model focused, respectful music-making for others.',
                         'Listen respectfully when others are playing or speaking.',
                         'Settle quickly and be ready to play at the start of each lesson.',
                         'Follow instructions promptly during practical work.',
                         'Follow class routines with teacher support.'],
 'ORGANISATION': ['Plan rehearsal time with clear goals before each task.',
                  'Prepare instruments and materials before each activity.',
                  'Keep notes and digital files organised and easy to find.',
                  'Bring required materials to every lesson.',
                  'Use a checklist to get ready for each lesson.'],
 'PARTICIPATION': ['Lead group tasks with more confidence and initiative.',
                   'Share ideas more often in class discussion and rehearsal.',
                   'Contribute regularly to group music-making.',
                   'Join in practical tasks more readily.',
                   'Take part in each activity with support.'],
 'TASK_COMPLETION': ['Extend finished work through independent refinement.',
                     'Check work carefully before submitting.',
                     'Complete tasks fully by the due date.',
                     'Break tasks into smaller steps and tick each one off.',
                     'Finish tasks by following guided steps.'],
 'HOME_PRACTICE': ['Set one clear goal for each home practice session.',
                   'Practise at home several times each week.',
                   'Practise class material at home each week.',
                   'Practise for ten minutes at home on a regular basis.',
                   'Practise one short task at home each week.'],
 'MUSIC_PRACTICE': ['Target tricky passages first when practising.',
                    'Use a metronome to build accuracy and control.',
                    'Practise slowly before increasing speed.',
                    'Repeat short sections until each one feels secure.',
                    'Practise short sections with teacher guidance.'],
}

new_text = {}
for unit, code in UNITS.items():
    for ct, cats in T[unit].items():
        for cat, five in cats.items():
            assert len(five) == 5, (unit, ct, cat)
            for tc, text in zip(TIERS, five):
                new_text[f'S4S_{ct}_{cat}_{tc}_{code}'] = text
for sub, five in G.items():
    assert len(five) == 5, sub
    for tc, text in zip(TIERS, five):
        new_text[f'S4S_STI_G_{tc}_{sub}'] = text

bank = json.load(open(SRC, encoding='utf-8'))
byid = {s['id']: s for s in bank['statements']}
short = [s for s in bank['statements'] if s['stage'] == 'Stage 4' and s.get('statementLength') == 'short']
assert set(new_text) == {s['id'] for s in short}, (set(new_text) ^ {s['id'] for s in short})

# ---------- checks (as v5.6, with the new length cap) ----------
PRON = re.compile(r'\b(he|she|they|his|her|their|him|them|hers|theirs|himself|herself|themselves|I|me|my|we|our|you|your)\b', re.I)
problems = []
texts = C.Counter(new_text.values())
others = {s['text'] for s in bank['statements'] if s['id'] not in new_text}
for id_, t in new_text.items():
    ct = byid[id_]['commentType']
    if len(t) > MAX: problems.append((id_, f'{len(t)} chars'))
    if PRON.search(t): problems.append((id_, 'pronoun: ' + PRON.search(t).group()))
    if not t.endswith('.') or re.search(r'[.!?]\s+\S', t): problems.append((id_, 'not one sentence'))
    if not t[0].isupper(): problems.append((id_, 'capital'))
    if re.search(r'\b(limited|poor|weak|fail|lazy|careless)\b', t, re.I): problems.append((id_, 'deficit'))
    if re.search(r'ize\b|izing|color|center\b', t): problems.append((id_, 'US spelling'))
    if texts[t] > 1 or t in others: problems.append((id_, 'duplicate text'))
    if ct == 'learning_strength' and not t.split()[0].endswith('s'): problems.append((id_, 'strength not 3rd-person'))
    if ct == 'strategy_to_improve' and t.split()[0].endswith('s') and t.split()[0] not in ('Focus',): problems.append((id_, 'strategy not imperative'))
if problems:
    for p in problems: print('PROBLEM', p)
    sys.exit(1)

changes = []
for id_, t in new_text.items():
    if byid[id_]['text'] != t:
        changes.append({'id': id_, 'old': byid[id_]['text'], 'new': t})
        byid[id_]['text'] = t

meta = bank['metadata']
meta['version'] = '5.7'
meta['sentralCharLimits']['Stage 4'] = {'perOutput': LIMIT, 'source': 'Justin Ossher, 20 Nov 2026 (was 150)'}
meta['changeNote'] = (meta.get('changeNote', '') + ' v5.7 (20 Nov 2026): Stage 4 Sentral limit raised to 200; '
                      'the 155 short Stage 4 sentences rewritten in Justin\'s voice (<=66 characters each); IDs and tags unchanged.').strip()
json.dump(bank, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(changes, open('data/diffs/v5.6_to_v5.7.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

L = [len(t) for t in new_text.values()]
worst = 0
for ct in ('LS', 'STI'):
    for unit, code in UNITS.items():
        pass
# worst case over any three P/C/L sentences (+ General swap) in one box
for ctype in ('learning_strength', 'strategy_to_improve'):
    pool = [s for s in short if s['commentType'] == ctype]
    by = {c: max((len(new_text[s['id']]) for s in pool if s['category'] == c), default=0) for c in 'PCLG'}
    w = by['P'] + by['C'] + by['L'] + 2
    if ctype == 'strategy_to_improve':
        w = max(w, by['G'] + sorted([by['P'], by['C'], by['L']])[-1] + sorted([by['P'], by['C'], by['L']])[-2] + 2)
    worst = max(worst, w)
print(f'rewrote {len(changes)} of {len(new_text)}; lengths {min(L)}-{max(L)}; worst-case comment {worst} (limit {LIMIT})')
