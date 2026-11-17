"""Build v5.3 from the untouched v5.1 original. The embedded statement data is
copied byte-for-byte; only CSS, three small HTML hooks and the app script change.
Usage: python3 -I build_v53.py <original.html> <app_v53.js> <out.html>"""
import sys, hashlib

src, js, out = sys.argv[1:4]
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
head = rep(head, '<button id="reset-filters">', '<button type="button" id="reset-filters">')

s0 = tail.index('<script>') + len('<script>')
s1 = tail.index('</script>', s0)
tail = tail[:s0] + '\n' + open(js, encoding='utf-8').read() + '\n' + tail[s1:]

result = head + data_block + tail
open(out, 'w', encoding='utf-8').write(result)

orig_data = hashlib.sha256(data_block.encode()).hexdigest()
o = open(out, encoding='utf-8').read()
e0 = o.index(DATA_OPEN); e1 = o.index('</script>', e0) + len('</script>')
print('data block identical:', o[e0:e1] == data_block, orig_data[:16])
print('bytes:', len(result.encode()))
