"""v5.9: version, counts and change note after stage4_v59.py and stage5_v59.py.
Usage: python3 -I tools/finalize_v59.py <in.json> <out.json>"""
import json, sys, collections as C
bank = json.load(open(sys.argv[1], encoding='utf-8')); meta = bank['metadata']; st = bank['statements']
meta['version'] = '5.9'
meta['statementCount'] = len(st)
meta['countsByStageCommentTypeCategory'] = dict(sorted(C.Counter(f"{s['stage']}|{s['commentType']}|{s['category']}" for s in st).items()))
catname = {'P': 'performance', 'C': 'composition', 'L': 'listening', 'M': 'musicology', 'A': 'aural', 'V': 'viva_voce', 'G': 'general_musicianship'}
cc = {ct: C.Counter() for ct in meta['commentTypes']}
for s in st: cc[s['commentType']][catname[s['category']]] += 1
meta['counts'] = {ct: dict(v) for ct, v in cc.items()}
ids = [s['id'] for s in st]; assert len(ids) == len(set(ids))
meta['changeNote'] += (' v5.9 (20 Nov 2026): Stage 4 sentences 53-65 characters (comments 161-199), Guitar/Piano Performance variants, '
                       'General Learning Strengths (classroom music aptitude) and music-focused General strategies; Stage 5 sentences '
                       '83-99 characters (comments 250-300) and General Learning Strengths.')
json.dump(bank, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('v5.9 bank:', len(st), 'statements')
