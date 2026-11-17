"""v5.6: adds a SHORT Stage 4 statement set (approved 17 Nov 2026: Sentral limit
150 characters per comment box for all of Stage 4; keep three sentences P/C/L).
Every sentence <= 48 characters, so any three sentences + 2 spaces <= 146.
Existing records are not modified. Usage:
  python3 -I tools/add_stage4_short.py data/statement_bank_v5.5.json data/statement_bank_v5.6.json
"""
import json, re, sys, collections as C

SRC, OUT = sys.argv[1], sys.argv[2]
MAX = 48
TIERS = ['Extensive', 'Thorough', 'Sound', 'Elementary', 'Basic']
TCODE = {'Extensive': 'EXT', 'Thorough': 'THR', 'Sound': 'SND', 'Elementary': 'ELE', 'Basic': 'BAS'}
UNITS = {'Beats and Tunes': 'BT', 'Rocking the Guitar': 'RTG', 'Sound Lab': 'SL', 'Jazz': 'JZ'}
CATLABEL = {'P': 'Performance', 'C': 'Composition', 'L': 'Listening', 'G': 'General'}

# [unit][commentType][category] = five sentences, Extensive -> Basic
T = {
 'Beats and Tunes': {
  'learning_strength': {
   'P': ['Performs rhythm and melody with assured control.',
         'Performs rhythms and keyboard parts accurately.',
         'Performs rhythms and keyboard parts steadily.',
         'Performs simple rhythms with some steadiness.',
         'Performs simple rhythms with support.'],
   'C': ['Composes inventive rhythms with clear structure.',
         'Composes well-organised four-bar rhythms.',
         'Composes four-bar rhythms with a steady pulse.',
         'Composes short rhythms using familiar patterns.',
         'Composes short rhythms with support.'],
   'L': ['Describes music insightfully using the elements.',
         'Identifies musical elements accurately by ear.',
         'Identifies common musical elements by ear.',
         'Identifies some musical elements with guidance.',
         'Recognises beat and rhythm with support.']},
  'strategy_to_improve': {
   'P': ['Add more expressive detail to performances.',
         'Refine accuracy in faster rhythm passages.',
         'Practise keyboard parts slowly, then speed up.',
         'Count aloud to keep a steadier pulse.',
         'Clap and say each rhythm before playing it.'],
   'C': ['Develop rhythm ideas with more contrast.',
         'Add dynamics and tempo markings to compositions.',
         'Use repetition and contrast to shape rhythms.',
         'Check each bar has the right number of beats.',
         'Build rhythms from familiar note values.'],
   'L': ['Support listening answers with precise detail.',
         'Use more specific terms to describe music.',
         'Listen for one element at a time.',
         'Use the elements list to guide answers.',
         'Listen for the beat and clap along.']}},
 'Rocking the Guitar': {
  'learning_strength': {
   'P': ['Plays guitar riffs and chords fluently in style.',
         'Plays chords and riffs with secure changes.',
         'Plays common chords with steady strumming.',
         'Plays simple chords with some smooth changes.',
         'Plays simple guitar parts with support.'],
   'C': ['Writes inventive riffs in TAB and on the staff.',
         'Writes well-shaped riffs over a chord pattern.',
         'Writes a clear riff over C, Am, G and F.',
         'Writes a short riff using familiar notes.',
         'Writes a short riff with support.'],
   'L': ['Explains rock styles and features in detail.',
         'Identifies rock features and instruments well.',
         'Identifies common rock features by ear.',
         'Identifies some rock features with guidance.',
         'Recognises guitar riffs with support.']},
  'strategy_to_improve': {
   'P': ['Add dynamics and feel to Song Ladder songs.',
         'Smooth chord changes at full tempo.',
         'Practise chord changes slowly, then speed up.',
         'Practise two chords at a time until smooth.',
         'Practise one chord shape at a time each day.'],
   'C': ['Develop riffs with syncopation and variation.',
         'Check TAB and staff versions match exactly.',
         'Repeat and vary the riff to build structure.',
         'Use notes from the chord to shape the riff.',
         'Start the riff on a chord note and repeat it.'],
   'L': ['Link rock features to historical context.',
         'Use precise terms to describe rock features.',
         'Listen for the riff, beat and chords separately.',
         'Name the instruments before other features.',
         'Listen for the guitar part and describe it.']}},
 'Sound Lab': {
  'learning_strength': {
   'P': ['Performs layered parts with precise timing.',
         'Holds a part securely within layered textures.',
         'Keeps a steady part within a layered texture.',
         'Performs a simple layer with some steadiness.',
         'Performs a simple layer with support.'],
   'C': ['Builds rich, purposeful layers in a DAW.',
         'Builds clear layers with contrasting textures.',
         'Builds a DAW composition with clear layers.',
         'Builds simple layers in a DAW with guidance.',
         'Builds a short DAW piece with support.'],
   'L': ['Analyses texture and orchestration in detail.',
         'Identifies textures and instruments accurately.',
         'Identifies layers and common instruments by ear.',
         'Identifies some layers and instruments.',
         'Recognises thick and thin textures with support.']},
  'strategy_to_improve': {
   'P': ['Balance dynamics carefully within the ensemble.',
         'Listen across layers to lock in timing.',
         'Count rests carefully to enter on time.',
         'Practise one layer until it is steady.',
         'Follow a partner’s part to keep in time.'],
   'C': ['Shape the texture with more deliberate contrast.',
         'Add a contrasting section to the DAW piece.',
         'Give each layer a clear role in the music.',
         'Add one new layer at a time and listen back.',
         'Start with a beat layer, then add a melody.'],
   'L': ['Use score evidence to support texture answers.',
         'Describe textures with precise terminology.',
         'Count the layers heard in each excerpt.',
         'Listen for which instruments enter and leave.',
         'Listen for when the music gets thicker.']}},
 'Jazz': {
  'learning_strength': {
   'P': ['Improvises confidently over the 12-bar blues.',
         'Plays the 12-bar blues securely with swing feel.',
         'Plays the 12-bar blues with a steady pulse.',
         'Plays parts of the 12-bar blues with guidance.',
         'Plays simple blues patterns with support.'],
   'C': ['Creates inventive blues phrases and riffs.',
         'Creates clear melodies from the blues scale.',
         'Creates short phrases using the blues scale.',
         'Creates simple riffs with some blues notes.',
         'Creates a short blues riff with support.'],
   'L': ['Explains jazz styles and features in detail.',
         'Identifies swing, blues and band roles well.',
         'Identifies the 12-bar blues and swing by ear.',
         'Identifies some jazz features with guidance.',
         'Recognises jazz instruments with support.']},
  'strategy_to_improve': {
   'P': ['Shape improvisations with phrasing and dynamics.',
         'Keep the swing feel steady through the form.',
         'Count the 12 bars aloud to stay on track.',
         'Practise the C7, F7 and G7 changes slowly.',
         'Practise the blues scale slowly each day.'],
   'C': ['Develop motifs further when improvising.',
         'Answer each phrase with a contrasting idea.',
         'Repeat and vary short blues-scale phrases.',
         'Start with three or four blues-scale notes.',
         'Build a riff from two notes of the blues scale.'],
   'L': ['Compare jazz eras using precise examples.',
         'Use precise terms for swing and band roles.',
         'Listen for the walking bass and chord changes.',
         'Count along to hear the 12-bar form.',
         'Listen for the swing feel and tap along.']}},
}

G = {  # Strategies to Improve, General (swap-in), Extensive -> Basic
 'work_ethic': ['Take more initiative when refining tasks.',
                'Act on feedback promptly and independently.',
                'Stay focused for the whole of each task.',
                'Ask for help early when a task is unclear.',
                'Complete each step of a task before moving on.'],
 'classroom_behaviour': ['Model focused, respectful learning for others.',
                         'Listen respectfully during group work.',
                         'Settle quickly at the start of each lesson.',
                         'Follow instructions promptly in practical work.',
                         'Follow class routines with teacher support.'],
 'organisation': ['Plan rehearsal time before each task.',
                  'Prepare materials before each activity.',
                  'Keep notes and digital files in order.',
                  'Bring required materials to every lesson.',
                  'Use a checklist to prepare for each lesson.'],
 'participation': ['Lead group tasks with more confidence.',
                   'Share ideas more often in class discussion.',
                   'Contribute regularly to group activities.',
                   'Join in practical tasks more readily.',
                   'Take part in each activity with support.'],
 'task_completion': ['Extend tasks through independent refinement.',
                     'Check work carefully before submitting.',
                     'Complete tasks fully by the due date.',
                     'Break tasks into smaller steps.',
                     'Finish tasks by following guided steps.'],
 'home_practice': ['Set a clear goal for each home practice session.',
                   'Practise at home several times each week.',
                   'Practise class material at home weekly.',
                   'Practise for ten minutes at home regularly.',
                   'Practise one short task at home each week.'],
 'music_practice': ['Refine practice by targeting tricky passages.',
                    'Use a metronome to build accuracy.',
                    'Practise slowly before increasing speed.',
                    'Repeat short sections until secure.',
                    'Practise short sections with teacher guidance.'],
}

bank = json.load(open(SRC, encoding='utf-8'))
meta = bank['metadata']
subcat_label = {s['subcategory']: s['subcategoryLabel'] for s in bank['statements'] if s.get('subcategory')}

def rec(id_, ct, cat, tier, unit, text, sub=None):
    tags = [ct, 'stage4', 'year7', 'year8', cat, CATLABEL[cat].lower(), tier.lower(), 'short']
    if unit: tags += [unit.lower().replace(' ', '_'), 'unit_specific']
    if cat == 'P': tags.append('instrument')
    if sub: tags.append(sub)
    return {
        'id': id_, 'stage': 'Stage 4', 'commentType': ct, 'category': cat,
        'categoryLabel': meta['categories'].get(cat, CATLABEL[cat]) if cat != 'G' else 'General',
        'subcategory': sub, 'subcategoryLabel': subcat_label.get(sub) if sub else None,
        'tier': tier, 'tierCode': TCODE[tier],
        'instrument': 'Instrument' if cat == 'P' else None,
        'unit': unit, 'specificity': 'unit_specific' if unit else None,
        'course': None, 'stageCourse': None, 'courseProfile': None, 'topic': None,
        'voiceTag': None, 'statementLength': 'short', 'text': text, 'tags': tags}

new = []
for unit, code in UNITS.items():
    for ct, cats in T[unit].items():
        for cat, five in cats.items():
            assert len(five) == 5, (unit, ct, cat)
            for tier, text in zip(TIERS, five):
                new.append(rec(f"S4S_{'LS' if ct == 'learning_strength' else 'STI'}_{cat}_{TCODE[tier]}_{code}",
                               ct, cat, tier, unit, text))
for sub, five in G.items():
    assert len(five) == 5, sub
    for tier, text in zip(TIERS, five):
        new.append(rec(f"S4S_STI_G_{TCODE[tier]}_{sub.upper()}", 'strategy_to_improve', 'G', tier, None, text, sub))

# ---------- checks ----------
PRON = re.compile(r'\b(he|she|they|his|her|their|him|them|hers|theirs|himself|herself|themselves|I|me|my|we|our|you|your)\b', re.I)
problems = []
ids = set(s['id'] for s in bank['statements'])
texts = C.Counter(n['text'] for n in new)
for n in new:
    t = n['text']
    if len(t) > MAX: problems.append((n['id'], f'{len(t)} chars'))
    if PRON.search(t): problems.append((n['id'], 'pronoun: ' + PRON.search(t).group()))
    if not t.endswith('.') or re.search(r'[.!?]\s+\S', t): problems.append((n['id'], 'not one sentence'))
    if not t[0].isupper(): problems.append((n['id'], 'capital'))
    if re.search(r'\b(limited|poor|weak|fail|lazy|careless)\b', t, re.I): problems.append((n['id'], 'deficit'))
    if re.search(r'ize\b|izing|color|center\b', t): problems.append((n['id'], 'US spelling'))
    if n['id'] in ids: problems.append((n['id'], 'id clash'))
    if texts[t] > 1: problems.append((n['id'], 'duplicate text'))
    if n['commentType'] == 'learning_strength' and not t.split()[0].endswith('s'): problems.append((n['id'], 'strength not 3rd-person'))
    if n['commentType'] == 'strategy_to_improve' and t.split()[0].endswith('s') and t.split()[0] not in ('Focus',): problems.append((n['id'], 'strategy not imperative'))
if problems:
    for p in problems: print('PROBLEM', p)
    sys.exit(1)

bank['statements'].extend(new)
meta['version'] = '5.6'
if 'short' not in meta['statementLengthOptions']: meta['statementLengthOptions'].append('short')
meta['statementCount'] = len(bank['statements'])
cnt = C.Counter(f"{s['stage']}|{s['commentType']}|{s['category']}" for s in bank['statements'])
meta['countsByStageCommentTypeCategory'] = dict(sorted(cnt.items()))
catname = {'P': 'performance', 'C': 'composition', 'L': 'listening', 'M': 'musicology', 'A': 'aural', 'V': 'viva_voce', 'G': 'general_musicianship'}
cc = {ct: C.Counter() for ct in meta['commentTypes']}
for s in bank['statements']: cc[s['commentType']][catname[s['category']]] += 1
meta['counts'] = {ct: dict(v) for ct, v in cc.items()}
meta['sentralCharLimits'] = {'Stage 4': {'perOutput': 150, 'source': 'Justin Ossher, 17 Nov 2026'}}
meta['changeNote'] = (meta.get('changeNote', '') + ' v5.6 (approved 17 Nov 2026): added 155 short Stage 4 records '
                      '(statementLength "short", <=48 characters each) for the 150-character Sentral limit; no existing record changed.').strip()
json.dump(bank, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
L = [len(n['text']) for n in new]
print(f'added {len(new)} records; lengths {min(L)}-{max(L)}; worst-case 3-sentence comment = {3*max(L)+2}; total {len(bank["statements"])}')
