"""Applies the approved v5.5 text changes (A, B, C; approved 17 Nov 2026) to
data/statement_bank_v5.1.json and writes data/statement_bank_v5.5.json plus
data/diffs/v5.1_to_v5.5.json. Only the `text` field of listed records changes."""
import json, copy, os
src = json.load(open('data/statement_bank_v5.1.json', encoding='utf-8'))
prop = json.load(open('proposals/v5.5_text_changes.json', encoding='utf-8'))
new = copy.deepcopy(src)
by = {s['id']: s for s in new['statements']}
for c in prop['changes']:
    assert by[c['id']]['text'] == c['old'], c['id']
    by[c['id']]['text'] = c['new']
new['metadata']['version'] = '5.5'
new['metadata']['changeNote'] = ('v5.5 (approved 17 Nov 2026): A) trailing "as part of senior music study" removed; '
    'B) placeholder topic labels reworded in sentence text; C) 22 deficit-worded Stage 5 strengths reworded. '
    'See data/diffs/v5.1_to_v5.5.json.')
json.dump(new, open('data/statement_bank_v5.5.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
os.makedirs('data/diffs', exist_ok=True)
json.dump({'from': '5.1-fixed-stage6', 'to': '5.5', 'approved': '2026-11-17 by Justin Ossher (A, B, C)',
           'counts': prop['counts'], 'records_changed': prop['records_changed'], 'changes': prop['changes']},
          open('data/diffs/v5.1_to_v5.5.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written; changed', prop['records_changed'])
