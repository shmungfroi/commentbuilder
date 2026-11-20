"""v5.9 Stage 4 short set (approved 20 Nov 2026):
- every Stage 4 sentence 53-65 characters, so any comment is 161-197 (target 161-199)
- classroom music aptitude woven into P/C/L wording
- NEW General Learning Strengths (6 music-aptitude areas x 5 tiers), swappable into one slot
- General Strategies reworked toward music aptitude (same 7 areas, same IDs)
- NEW Guitar / Piano Performance variants (wording says "keyboard"):
  Beats and Tunes: Piano; Sound Lab and Jazz: Guitar + Piano; Rocking the Guitar unchanged
Usage: python3 -I tools/stage4_v59.py <in.json> <out.json>
"""
import json, re, sys, collections as C

SRC, OUT = sys.argv[1], sys.argv[2]
LO, HI = 53, 65
TIERS = ['Extensive', 'Thorough', 'Sound', 'Elementary', 'Basic']
TC = ['EXT', 'THR', 'SND', 'ELE', 'BAS']
UNITS = {'Beats and Tunes': 'BT', 'Rocking the Guitar': 'RTG', 'Sound Lab': 'SL', 'Jazz': 'JZ'}

# [unit][LS|STI][P|C|L|P_GTR|P_PNO] = Extensive -> Basic
T = {
 'Beats and Tunes': {
  'LS': {
   'P': ['Performs rhythm and melody with real control, feel and intent.',
         'Performs rhythms and melodies accurately and right in time.',
         'Performs rhythms and simple melodies with a steady, even pulse.',
         'Performs simple rhythms with a pulse that is growing steadier.',
         'Performs simple rhythms in time when counted in and supported.'],
   'P_PNO': ['Plays keyboard melodies like Ode to Joy fluently and musically.',
             'Plays keyboard melodies accurately, with a secure hand position.',
             'Plays simple keyboard melodies steadily, keeping a clear pulse.',
             'Plays short keyboard melodies, with finger placement improving.',
             'Plays short keyboard patterns when guided note by note.'],
   'C': ['Composes inventive rhythms that groove and hold together well.',
         'Composes well-organised four-bar rhythms with a clear shape.',
         'Composes four-bar rhythms that sit comfortably on a steady pulse.',
         'Composes short rhythms from familiar patterns and note values.',
         'Composes short rhythm patterns with step-by-step support.'],
   'L': ['Hears and describes how the elements work together in a piece.',
         'Picks out musical elements accurately by ear and names each one.',
         'Identifies common musical elements by ear with real confidence.',
         'Identifies some musical elements by ear when guided by questions.',
         'Feels the beat and recognises simple rhythms with support.']},
  'STI': {
   'P': ['Bring more dynamic contrast and feel to each class performance.',
         'Keep faster rhythm passages as accurate as the slower ones.',
         'Count in and feel the pulse in the body before each performance.',
         'Count aloud and move to the beat to keep a steadier pulse.',
         'Clap and say each rhythm aloud before playing it on instruments.'],
   'P_PNO': ['Shape keyboard melodies with dynamics and smooth, linked phrases.',
             'Keep keyboard fingering consistent so melodies flow at tempo.',
             'Practise keyboard parts slowly, then lift the tempo once secure.',
             'Practise each keyboard phrase hands separately until secure.',
             'Find the first keyboard note, then add a few more notes at once.'],
   'C': ['Push rhythm ideas further with bolder contrast and development.',
         'Mark dynamics and tempo so others can play the composition well.',
         'Use repetition and contrast to give each rhythm a clear shape.',
         'Check that each bar adds up to the right number of beats.',
         'Build rhythms from familiar note values, one bar at a time.'],
   'L': ['Back up listening answers with precise moments from the music.',
         'Use more specific musical terms to explain what is heard.',
         'Listen for one element at a time, then put the picture together.',
         'Use the elements list as a guide when listening to each excerpt.',
         'Tap the beat while listening, then describe what changes.']}},
 'Rocking the Guitar': {
  'LS': {
   'P': ['Plays riffs and chords fluently, with real feel for the style.',
         'Plays chords and riffs with secure, well-timed changes in a band.',
         'Plays common chords with steady, even strumming in time.',
         'Plays simple chords, with changes between shapes now smoother.',
         'Plays simple chord shapes and riffs with step-by-step support.'],
   'C': ['Writes inventive riffs, notated clearly in TAB and on the staff.',
         'Writes well-shaped riffs that sit neatly over a chord pattern.',
         'Writes a clear riff over the C, Am, G and F chord progression.',
         'Writes a short riff using familiar notes and simple patterns.',
         'Writes a short riff in TAB with step-by-step support.'],
   'L': ['Explains rock styles and the features of each with real depth.',
         'Identifies rock features and instruments accurately by ear.',
         'Identifies common rock features and band instruments by ear.',
         'Identifies some rock features by ear when guided by questions.',
         'Recognises a guitar riff and the beat in a song with support.']},
  'STI': {
   'P': ['Bring dynamics and feel to Song Ladder songs, not just accuracy.',
         'Keep chord changes clean and in time at full song tempo.',
         'Practise chord changes slowly, then build up to song tempo.',
         'Practise moving between two chords until the change is smooth.',
         'Practise one chord shape a day until the fingers find it easily.'],
   'C': ['Develop riffs further with syncopation, variation and contrast.',
         'Check the TAB and staff versions of each riff match exactly.',
         'Repeat the riff, then vary it to give the piece clear structure.',
         'Use notes from each chord to shape the riff over the progression.',
         'Start the riff on a chord note and repeat it until secure.'],
   'L': ['Connect rock features to the history and context of the style.',
         'Use precise musical terms to describe rock features and sounds.',
         'Listen for the riff, the beat and the chords one at a time.',
         'Name the instruments first, then listen for other features.',
         'Listen for the guitar part in a song and describe what it does.']}},
 'Sound Lab': {
  'LS': {
   'P': ['Performs layered parts in precise time, with a keen ensemble ear.',
         'Holds a part securely while listening to the layers around it.',
         'Keeps a steady part going within a layered class texture.',
         'Performs a simple layer in the class texture with more control.',
         'Performs a simple layer alongside others with teacher support.'],
   'P_GTR': ['Plays guitar layers in precise time, blending well with others.',
             'Holds a guitar part securely while listening to the other layers.',
             'Keeps a steady strummed guitar part going in a layered texture.',
             'Plays a simple guitar layer, keeping time with others more often.',
             'Plays a simple guitar layer alongside others with support.'],
   'P_PNO': ['Plays keyboard layers in precise time, blending well with others.',
             'Holds a keyboard part securely while listening to other layers.',
             'Keeps a steady keyboard part going in a layered class texture.',
             'Plays a simple keyboard layer, keeping time with others more.',
             'Plays a simple keyboard layer alongside others with support.'],
   'C': ['Builds rich, purposeful DAW layers with a clear musical plan.',
         'Builds clear DAW layers with well-chosen contrasts in texture.',
         'Builds a DAW composition with clear layers that fit together.',
         'Builds simple layers in a DAW when guided through each step.',
         'Builds a short DAW piece from loops with step-by-step support.'],
   'L': ['Analyses texture and instrumentation by ear in real detail.',
         'Identifies textures and instruments accurately by ear in class.',
         'Identifies layers and common instruments by ear with confidence.',
         'Identifies some layers and instruments when guided by questions.',
         'Recognises thick and thin textures in music with support.']},
  'STI': {
   'P': ['Balance dynamics within the ensemble so every layer is heard.',
         'Listen across all the layers to lock in timing with others.',
         'Count rests carefully to come in on time with the other layers.',
         'Practise one layer until it feels steady and secure in the mix.',
         'Follow a partner’s part closely to stay in time with the group.'],
   'P_GTR': ['Balance guitar volume and tone so each layer in the mix is heard.',
             'Lock guitar strumming in with the drums and bass in each layer.',
             'Count rests carefully to bring the guitar in on time with others.',
             'Practise the guitar layer slowly until the strumming is steady.',
             'Follow a partner’s part closely to keep the guitar layer in time.'],
   'P_PNO': ['Balance keyboard dynamics so each layer in the ensemble is heard.',
             'Lock the keyboard part in with the drums and bass in each layer.',
             'Count rests carefully to bring the keyboard in on time.',
             'Practise the keyboard layer hands separately until it is steady.',
             'Follow a partner’s part closely to keep the keyboard in time.'],
   'C': ['Shape the texture with more deliberate build-ups and drop-outs.',
         'Add a contrasting section so the DAW piece goes somewhere new.',
         'Give each layer a clear job in the music and listen back often.',
         'Add one new layer at a time and listen back after each change.',
         'Start with a beat layer in the DAW, then add a melody on top.'],
   'L': ['Use evidence from the score to support answers on texture.',
         'Describe textures using precise musical terms and examples.',
         'Count the layers heard in each excerpt and name the instruments.',
         'Listen for which instruments enter and drop out in each excerpt.',
         'Listen for when the music gets thicker or thinner, and say when.']}},
 'Jazz': {
  'LS': {
   'P': ['Improvises with confidence and real swing over the 12-bar blues.',
         'Performs the 12-bar blues securely with a relaxed swing feel.',
         'Performs the 12-bar blues with a steady pulse and clear changes.',
         'Performs sections of the 12-bar blues when guided through it.',
         'Performs simple blues patterns in time with teacher support.'],
   'P_GTR': ['Improvises on guitar with confidence and swing over the blues.',
             'Plays the 12-bar blues on guitar securely, with a relaxed swing.',
             'Plays the 12-bar blues on guitar with steady, even strumming.',
             'Plays sections of the 12-bar blues on guitar when guided.',
             'Plays simple blues chord shapes on guitar with teacher support.'],
   'P_PNO': ['Improvises on keyboard with confidence and real swing over blues.',
             'Plays the 12-bar blues on keyboard securely, with relaxed swing.',
             'Plays the 12-bar blues on keyboard with a steady left-hand pulse.',
             'Plays sections of the 12-bar blues on keyboard when guided.',
             'Plays simple blues patterns on keyboard with teacher support.'],
   'C': ['Creates inventive blues phrases and riffs that are true to style.',
         'Creates clear, shapely melodies from the blues scale with intent.',
         'Creates short, well-formed phrases using the blues scale.',
         'Creates simple riffs from some blues notes with more confidence.',
         'Creates a short blues riff from a few notes with support.'],
   'L': ['Explains jazz styles and the features of each in real depth.',
         'Identifies swing, the blues and the roles in a jazz band well.',
         'Identifies the 12-bar blues and swing feel by ear confidently.',
         'Identifies some jazz features by ear when guided by questions.',
         'Recognises jazz instruments and the swing feel with support.']},
  'STI': {
   'P': ['Shape improvisations with phrasing, space and dynamic contrast.',
         'Keep the swing feel relaxed and steady right through the form.',
         'Count the 12 bars aloud to stay on track through each chorus.',
         'Practise the C7, F7 and G7 changes slowly until each is secure.',
         'Practise the blues scale slowly, a few notes at a time each day.'],
   'P_GTR': ['Shape guitar solos with phrasing, space and dynamic contrast.',
             'Keep guitar comping relaxed and swinging right through the form.',
             'Count the 12 bars aloud while strumming to stay on track.',
             'Practise the C7, F7 and G7 shapes on guitar slowly until secure.',
             'Practise the blues scale on guitar slowly, a few frets at a time.'],
   'P_PNO': ['Shape keyboard solos with phrasing, space and dynamic contrast.',
             'Keep keyboard comping relaxed and swinging through the form.',
             'Count the 12 bars aloud while playing keyboard to stay on track.',
             'Practise C7, F7 and G7 chords on keyboard slowly until secure.',
             'Practise the blues scale on keyboard slowly, a few keys at once.'],
   'C': ['Develop one motif further each time instead of starting fresh.',
         'Answer each phrase with a contrasting idea, like a conversation.',
         'Repeat and vary short blues-scale phrases to build a solo.',
         'Start with three or four blues-scale notes and build from there.',
         'Build a riff from two notes of the blues scale and repeat it.'],
   'L': ['Compare jazz eras using precise musical examples from each.',
         'Use precise terms for swing feel and the roles in a jazz band.',
         'Listen for the walking bass and the chord changes in each chorus.',
         'Count along to hear where the 12-bar form starts again.',
         'Listen for the swing feel and tap along with the drummer.']}},
}

G_LS = {  # NEW: General Learning Strengths (classroom music aptitude), Extensive -> Basic
 'ENSEMBLE_AWARENESS': ['Leads by ear in ensemble work, listening and adjusting with ease.',
                        'Listens closely and fits in well when making music with others.',
                        'Works well in ensembles and keeps an ear on the other parts.',
                        'Joins in ensemble work and is learning to listen to other parts.',
                        'Plays alongside others in group pieces with teacher support.'],
 'MUSICAL_EAR': ['Shows a sharp musical ear, picking up parts and ideas quickly.',
                 'Learns music well by ear and hears when something is out of time.',
                 'Uses a developing ear to copy rhythms and melodies accurately.',
                 'Copies short rhythms and melodies by ear with growing accuracy.',
                 'Echoes short rhythms by ear when each one is modelled clearly.'],
 'REHEARSAL_FOCUS': ['Rehearses with real focus, refining parts without being asked.',
                     'Uses rehearsal time well and works steadily to improve each part.',
                     'Stays on task in rehearsal and works hard to get parts right.',
                     'Works on parts in rehearsal and is building steadier focus.',
                     'Works on rehearsal tasks with clear steps and teacher support.'],
 'CREATIVE_RISK': ['Takes creative risks and tries bold new ideas with confidence.',
                   'Tries new musical ideas willingly and shapes each one with care.',
                   'Is willing to try new musical ideas and build on each in class.',
                   'Tries new musical ideas in class when given a starting point.',
                   'Tries simple musical ideas with encouragement and a clear model.'],
 'CARE_OF_INSTRUMENTS': ['Handles instruments and gear with real care and helps others.',
                         'Sets up and packs away instruments and gear with care and skill.',
                         'Looks after instruments and equipment well during practical work.',
                         'Looks after instruments and equipment by following routines.',
                         'Handles instruments safely with clear routines and support.'],
 'ENGAGEMENT': ['Brings real energy, curiosity and focus to class music-making.',
                'Engages enthusiastically and contributes well to class music.',
                'Brings energy and focus to practical music-making in class.',
                'Joins in class music-making readily and is growing in confidence.',
                'Takes part in class music-making with encouragement and support.'],
}
G_LS_LABEL = {'ENSEMBLE_AWARENESS': 'Ensemble Awareness', 'MUSICAL_EAR': 'Musical Ear', 'REHEARSAL_FOCUS': 'Rehearsal Focus',
              'CREATIVE_RISK': 'Creative Risk-Taking', 'CARE_OF_INSTRUMENTS': 'Care of Instruments', 'ENGAGEMENT': 'Engagement'}

G_STI = {  # reworked toward music aptitude, same IDs
 'WORK_ETHIC': ['Take more initiative in refining musical work beyond what is set.',
                'Act on feedback promptly and test each change by playing it back.',
                'Stay focused through to the end of each practical music task.',
                'Ask for help early when a musical task or part is unclear.',
                'Complete each step of a music task before moving on to the next.'],
 'CLASSROOM_BEHAVIOUR': ['Model focused, respectful music-making for others in the class.',
                         'Listen respectfully while others play, then add ideas musically.',
                         'Settle quickly and be ready to play at the start of each lesson.',
                         'Follow instructions promptly during practical music-making.',
                         'Follow music room routines each lesson with teacher support.'],
 'ORGANISATION': ['Plan rehearsal time with clear musical goals before each task.',
                  'Prepare instruments, music and materials before each activity.',
                  'Keep notes, scores and digital files organised and easy to find.',
                  'Bring required materials and a charged device to every lesson.',
                  'Use a simple checklist to get ready for each music lesson.'],
 'PARTICIPATION': ['Lead ensemble tasks with more confidence and musical initiative.',
                   'Share musical ideas more often in class discussion and rehearsal.',
                   'Contribute regularly to group music-making and ensemble work.',
                   'Join in practical music tasks more readily and with more energy.',
                   'Take part in each music activity, starting with small roles.'],
 'TASK_COMPLETION': ['Extend finished work through independent musical refinement.',
                     'Check work carefully, by eye and by ear, before submitting.',
                     'Complete each composition and performance task by the due date.',
                     'Break music tasks into smaller steps and tick each one off.',
                     'Finish music tasks by following the guided steps one at a time.'],
 'HOME_PRACTICE': ['Set one clear musical goal for each home practice session.',
                   'Practise at home several times each week to build confidence.',
                   'Practise class material at home each week, even for a short time.',
                   'Practise for ten minutes at home on a regular basis each week.',
                   'Practise one short musical task at home each week with a plan.'],
 'MUSIC_PRACTICE': ['Target the trickiest passages first when practising each piece.',
                    'Use a metronome to build accuracy, control and steady time.',
                    'Practise slowly and in time before gradually increasing speed.',
                    'Repeat short sections until each one feels secure and steady.',
                    'Practise short sections with teacher guidance and a clear model.'],
}

bank = json.load(open(SRC, encoding='utf-8'))
meta = bank['metadata']
byid = {s['id']: s for s in bank['statements']}
short = [s for s in bank['statements'] if s['stage'] == 'Stage 4' and s.get('statementLength') == 'short']
assert len(short) == 155

def newrec(id_, ct, cat, tier, unit, text, instrument=None, sub=None, sublabel=None):
    tags = [ct, 'stage4', 'year7', 'year8', cat, {'P': 'performance', 'G': 'general'}[cat], tier.lower(), 'short']
    if unit: tags += [unit.lower().replace(' ', '_'), 'unit_specific']
    if instrument: tags.append(instrument.lower())
    if sub: tags.append(sub)
    return {'id': id_, 'stage': 'Stage 4', 'commentType': ct, 'category': cat,
            'categoryLabel': 'Performance' if cat == 'P' else 'General',
            'subcategory': sub, 'subcategoryLabel': sublabel, 'tier': tier, 'tierCode': TC[TIERS.index(tier)],
            'instrument': instrument, 'unit': unit, 'specificity': 'unit_specific' if unit else None,
            'course': None, 'stageCourse': None, 'courseProfile': None, 'topic': None, 'voiceTag': None,
            'statementLength': 'short', 'text': text, 'tags': tags}

texts, added = {}, []
CT = {'LS': 'learning_strength', 'STI': 'strategy_to_improve'}
for unit, code in UNITS.items():
    for ct, cats in T[unit].items():
        for key, five in cats.items():
            assert len(five) == 5, (unit, ct, key)
            for i, text in enumerate(five):
                if key in 'PCL':
                    texts[f'S4S_{ct}_{key}_{TC[i]}_{code}'] = text
                else:
                    inst = {'P_GTR': 'Guitar', 'P_PNO': 'Piano'}[key]
                    r = newrec(f'S4S_{ct}_P_{TC[i]}_{code}_{key[2:]}', CT[ct], 'P', TIERS[i], unit, text, instrument=inst)
                    added.append(r); texts[r['id']] = text
for sub, five in G_STI.items():
    for i, text in enumerate(five): texts[f'S4S_STI_G_{TC[i]}_{sub}'] = text
for sub, five in G_LS.items():
    assert len(five) == 5
    for i, text in enumerate(five):
        r = newrec(f'S4S_LS_G_{TC[i]}_{sub}', 'learning_strength', 'G', TIERS[i], None, text,
                   sub=sub.lower(), sublabel=G_LS_LABEL[sub])
        added.append(r); texts[r['id']] = text

existing_ids = {s['id'] for s in short}
assert existing_ids <= set(texts), existing_ids - set(texts)
assert not ({r['id'] for r in added} & set(byid))

PRON = re.compile(r'\b(he|she|they|his|her|their|him|them|hers|theirs|himself|herself|themselves|I|me|my|we|our|you|your)\b', re.I)
problems, cnt = [], C.Counter(texts.values())
others = {s['text'] for s in bank['statements'] if s['id'] not in texts}
ctype = {**{s['id']: s['commentType'] for s in short}, **{r['id']: r['commentType'] for r in added}}
for id_, t in texts.items():
    if not LO <= len(t) <= HI: problems.append((id_, len(t), t))
    if PRON.search(t): problems.append((id_, 'pronoun ' + PRON.search(t).group()))
    if not t.endswith('.') or re.search(r'[.!?]\s+\S', t): problems.append((id_, 'not one sentence'))
    if re.search(r'\b(limited|poor|weak|fail|lazy|careless)\b', t, re.I): problems.append((id_, 'deficit'))
    if re.search(r'ize\b|izing|color|center\b', t): problems.append((id_, 'US spelling'))
    if cnt[t] > 1 or t in others: problems.append((id_, 'duplicate'))
    w = t.split()[0]
    if ctype[id_] == 'learning_strength' and not w.endswith('s'): problems.append((id_, 'strength not 3rd person'))
    if ctype[id_] == 'strategy_to_improve' and w.endswith('s') and w != 'Focus': problems.append((id_, 'strategy not imperative'))
if problems:
    for p in problems: print('PROBLEM', p)
    sys.exit(1)

changes = []
for s in short:
    if s['text'] != texts[s['id']]:
        changes.append({'id': s['id'], 'old': s['text'], 'new': texts[s['id']]}); s['text'] = texts[s['id']]
bank['statements'].extend(added)
json.dump({'changed': changes, 'added': [{'id': r['id'], 'text': r['text']} for r in added]},
          open('data/diffs/v5.7_to_v5.9_stage4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

for sub, lab in G_LS_LABEL.items():
    if sub.lower() not in meta['generalSubcategories']: meta['generalSubcategories'].append(sub.lower())
meta['sentralCharLimits']['Stage 4']['targetRange'] = [161, 199]
json.dump(bank, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
L = [len(t) for t in texts.values()]
print(f'Stage 4: changed {len(changes)}, added {len(added)}; sentence lengths {min(L)}-{max(L)}; comments {3*min(L)+2}-{3*max(L)+2}')
