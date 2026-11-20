"""Build v5.4 from the untouched v5.1 original. The embedded statement data is
copied byte-for-byte; only CSS, three small HTML hooks and the app script change.
Usage: python3 -I build.py <original.html> <app.js> <out.html>"""
import sys, hashlib

src, js, out = sys.argv[1:4]
# v5.5: optional 4th argument = statement bank JSON to embed (default: keep the
# baseline's embedded data byte-for-byte).
bank_path = sys.argv[4] if len(sys.argv) > 4 else None
h = open(src, encoding='utf-8').read()

DATA_OPEN = '<script id="statement-data" type="application/json">'
d0 = h.index(DATA_OPEN)
d1 = h.index('</script>', d0) + len('</script>')
data_block = h[d0:d1]
head, tail = h[:d0], h[d1:]

def rep(text, old, new):
    assert text.count(old) == 1, ('anchor not unique', old[:60], text.count(old))
    return text.replace(old, new)

CSS = """
  /* ---- v5.2 additions ---- */
  button.chip{font-family:inherit;line-height:1.2;}
  .chip:focus-visible,.select-btn:focus-visible,.swap-btn:focus-visible,.actions button:focus-visible,#reset-filters:focus-visible,.dz-card .remove-btn:focus-visible,.char-row input:focus-visible{
    outline:3px solid #F4B183;outline-offset:2px;
  }
  .context-notice{
    font-size:0.8rem;background:#FFF4E5;border:1px solid #F4B183;color:#7a4a12;
    border-radius:6px;padding:6px 10px;margin-bottom:8px;
  }
  .card.locked{cursor:default;}
  .swap-caption{margin-top:8px;font-size:0.72rem;color:#4b3d80;font-weight:600;}
  .swap-row{display:flex;gap:4px;margin-top:4px;flex-wrap:wrap;}
  .swap-btn{
    flex:1;padding:5px 4px;font-size:0.7rem;border-radius:6px;cursor:pointer;
    border:1px solid var(--purple);background:#F1EDFA;color:#4b3d80;font-family:inherit;
  }
  .swap-btn:hover{background:var(--purple);color:#fff;}
  .swap-note{
    display:inline-block;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.03em;
    color:#4b3d80;background:#F1EDFA;border:1px solid var(--purple);border-radius:4px;padding:1px 6px;
  }
  .char-row{
    display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;
    font-size:0.78rem;color:#555;margin:-4px 0 10px 0;
  }
  .char-row .charcount.over{color:var(--red);font-weight:700;}
  .char-row label{display:flex;align-items:center;gap:4px;}
  .char-row input{width:72px;padding:2px 4px;font-size:0.78rem;font-family:inherit;border:1px solid #bbb;border-radius:4px;}
  .validation li.warn{color:#9a5b00;}
  /* ---- v5.3 cross-check ---- */
  .review-text.crosscheck-warn{background:#FFF4E5;border-color:#F4B183;color:#7a4a12;}
  .review-text.crosscheck-ok{background:#EEF7EA;border-color:#B5D6A7;color:#2e5d1f;}
  .review-text ul{margin:0 0 0 16px;padding:0;}
  .crosscheck-note{margin-top:6px;font-size:0.78rem;font-style:italic;}
  /* ---- v5.4 ---- */
  #next-student{
    width:100%;margin:0 0 14px 0;padding:10px 12px;border:none;border-radius:8px;cursor:pointer;
    background:var(--navy);color:#fff;font-family:inherit;font-size:0.95rem;font-weight:600;
  }
  #next-student:hover{filter:brightness(1.15);}
  #next-student:focus-visible{outline:3px solid #F4B183;outline-offset:2px;}
  button.chip.disabled{cursor:not-allowed;}
  /* ---- v5.8 comment dock + order switch ---- */
  @media (min-width:1201px){
    .layout{grid-template-columns:240px 1fr 460px;}
    #builders-panel{position:sticky;top:14px;max-height:calc(100vh - 28px);overflow-y:auto;padding-top:0;}
  }
  .builder-toolbar{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap;
    padding:12px 0 10px 0;background:#fff;}
  .builder-toolbar #next-student{width:auto;margin:0;padding:8px 14px;font-size:0.85rem;}
  .order-switch{display:flex;align-items:center;gap:0;font-size:0.8rem;}
  .order-label{margin-right:8px;color:#555;font-weight:600;}
  .order-btn{font-family:inherit;font-size:0.8rem;font-weight:600;padding:7px 12px;cursor:pointer;
    border:1px solid var(--navy);background:#fff;color:var(--navy);}
  .order-btn:first-of-type{border-radius:6px 0 0 6px;}
  .order-btn:last-of-type{border-radius:0 6px 6px 0;border-left:none;}
  .order-btn[aria-pressed="true"]{background:var(--navy);color:#fff;}
  .order-btn:focus-visible{outline:3px solid #F4B183;outline-offset:2px;}
  #comment-dock{display:flex;flex-direction:column;gap:10px;padding-bottom:12px;margin-bottom:14px;
    border-bottom:2px solid #e3e3e3;background:#fff;}
  @media (min-width:1201px) and (min-height:760px){
    .builder-toolbar{position:sticky;top:0;z-index:6;}
    #comment-dock{position:sticky;top:52px;z-index:5;}
  }
  .comment-card{border:1px solid #c9d6ea;border-left:5px solid var(--navy);border-radius:8px;padding:10px 12px;background:#FAFCFF;}
  .comment-card.strategy{border-color:#bfe0db;border-left-color:var(--teal);background:#F7FCFB;}
  .card-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:6px;flex-wrap:wrap;}
  .card-title{font-weight:700;font-size:0.9rem;color:var(--navy);}
  .comment-card.strategy .card-title{color:#1d6f65;}
  .card-status{font-size:0.75rem;font-weight:600;color:#666;}
  .card-status.ok{color:#2e7d32;} .card-status.warn{color:#9a5b00;} .card-status.fail{color:var(--red);}
  .comment-card .preview-box{font-size:1rem;line-height:1.55;min-height:0;margin-bottom:8px;background:#fff;}
  .preview-box.empty{color:#888;font-style:italic;font-size:0.85rem;border-style:dashed;}
  .preview-box.partial{border-style:dashed;}
  .preview-box.ready{box-shadow:0 0 0 2px #B5D6A7;}
  .comment-card .char-row{margin:0 0 8px 0;}
  .comment-card .actions .copy-btn{flex:3;}
  .comment-card .actions .clear-btn{flex:1;background:#fff;color:var(--red);border:1px solid var(--red);}
  .comment-card .actions .clear-btn:hover{background:#fbeaea;}
  .comment-card .copy-msg{height:auto;min-height:0;margin-top:4px;}
  .comment-card .copy-msg:empty{display:none;}
</style>"""

def char_row(prefix):
    return (f'\n      <div class="char-row">\n'
            f'        <span class="charcount" id="charcount-{prefix}" aria-live="polite">0 characters</span>\n'
            f'        <label for="charlimit-{prefix}" title="Enter the verified Sentral limit for this field. Leave blank until confirmed.">'
            f'Sentral limit <input type="number" min="1" step="1" inputmode="numeric" id="charlimit-{prefix}" placeholder="not set"></label>\n'
            f'      </div>\n')

head = rep(head, '</style>', CSS)
head = rep(head, '<div id="bank-count"></div>',
           '<div id="bank-count"></div>\n    <div id="context-notice" class="context-notice" role="status"></div>')
head = rep(head, '<div class="preview-box" id="preview-LS">Select one statement for each category in the current profile.</div>\n',
           '<div class="preview-box" id="preview-LS" aria-live="polite">Select one statement for each category in the current profile.</div>\n' + char_row('LS'))
head = rep(head, '<div class="preview-box strategy" id="preview-STI">Select one statement for each category in the current profile.</div>\n',
           '<div class="preview-box strategy" id="preview-STI" aria-live="polite">Select one statement for each category in the current profile.</div>\n' + char_row('STI'))
head = rep(head, '<h3 class="strategy">Strategies to Improve</h3>\n        <div class="review-text empty" id="review-STI">Not yet complete.</div>\n      </div>',
           '<h3 class="strategy">Strategies to Improve</h3>\n        <div class="review-text empty" id="review-STI">Not yet complete.</div>\n      </div>\n'
           '      <div class="review-block">\n        <h3>Strengths ↔ Strategies cross-check</h3>\n'
           '        <div class="review-text empty" id="crosscheck" aria-live="polite">Shown once both outputs have at least one statement.</div>\n      </div>')
head = rep(head, '<!-- BUILDERS PANEL -->\n  <div class="panel">', '<!-- BUILDERS PANEL -->\n  <div class="panel" id="builders-panel">')
head = rep(head, '<button id="reset-filters">', '<button type="button" id="reset-filters">')

head = rep(head, '<!-- LEARNING STRENGTHS BUILDER -->',
           '<button type="button" id="next-student" title="Clears both comments, the tier and the instrument. Keeps Stage, Course, Profile, Topic and Unit.">Next student</button>\n\n    <!-- LEARNING STRENGTHS BUILDER -->')
s0 = tail.index('<script>') + len('<script>')
s1 = tail.index('</script>', s0)
tail = tail[:s0] + '\n' + open(js, encoding='utf-8').read() + '\n' + tail[s1:]

if bank_path:
    import json
    bank_text = json.dumps(json.load(open(bank_path, encoding='utf-8')), ensure_ascii=False, indent=2)
    assert '</' not in bank_text, 'bank text would break the script element'
    data_block = DATA_OPEN + '\n' + bank_text + '\n</script>'
result = head + data_block + tail
open(out, 'w', encoding='utf-8').write(result)

orig_data = hashlib.sha256(data_block.encode()).hexdigest()
o = open(out, encoding='utf-8').read()
e0 = o.index(DATA_OPEN); e1 = o.index('</script>', e0) + len('</script>')
print('data block as intended:', o[e0:e1] == data_block, orig_data[:16])
if bank_path:
    import json
    emb = json.loads(o[e0 + len(DATA_OPEN):e1 - len('</script>')])
    print('embedded bank == file:', emb == json.load(open(bank_path, encoding='utf-8')), 'version', emb['metadata']['version'])
print('bytes:', len(result.encode()))
