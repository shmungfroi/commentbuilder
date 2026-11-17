"""Verifies that bank B differs from bank A only in the records and text listed in the diff."""
import json, sys
a = json.load(open(sys.argv[1], encoding='utf-8')); b = json.load(open(sys.argv[2], encoding='utf-8'))
d = {c['id']: c for c in json.load(open(sys.argv[3], encoding='utf-8'))['changes']}
A = {s['id']: s for s in a['statements']}; B = {s['id']: s for s in b['statements']}
assert list(A) == list(B), 'ids or order differ'
bad = []
for i in A:
    x, y = A[i], B[i]
    other = [k for k in x if k != 'text' and x[k] != y.get(k)] + [k for k in y if k not in x]
    if other: bad.append((i, 'non-text field changed', other))
    if i in d:
        if x['text'] != d[i]['old'] or y['text'] != d[i]['new']: bad.append((i, 'text not as approved'))
    elif x['text'] != y['text']: bad.append((i, 'unlisted text change'))
meta = [k for k in a['metadata'] if a['metadata'][k] != b['metadata'].get(k)] + [k for k in b['metadata'] if k not in a['metadata']]
print(f"records: {len(A)} -> {len(B)}; listed changes: {len(d)}; problems: {len(bad)}; metadata keys changed: {meta}")
for x in bad[:10]: print('  ', x)
sys.exit(1 if bad else 0)
