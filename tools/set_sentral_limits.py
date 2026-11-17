"""Writes the confirmed Sentral character limits into the bank's metadata
(in place). Statements are not touched. Each limit is either perOutput (both
comment boxes) or per comment type.
Usage: python3 -I tools/set_sentral_limits.py data/statement_bank_v5.6.json"""
import json, sys
p = sys.argv[1]
bank = json.load(open(p, encoding='utf-8'))
bank['metadata']['sentralCharLimits'] = {
    'Stage 4': {'perOutput': 150, 'source': 'Justin Ossher, 17 Nov 2026'},
    'Stage 5': {'learning_strength': 800, 'source': 'Justin Ossher, 17 Nov 2026 (Strategies to Improve not yet confirmed)'},
}
bank['metadata']['version'] = '5.6.1'
json.dump(bank, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('limits set:', bank['metadata']['sentralCharLimits'])
