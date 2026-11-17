"""Regression / acceptance suite for the Music Report Comment Builder.
Drives the real UI in headless Chrome. Synthetic records only (no student data).
Usage: python3 -I regression_suite.py <app.html> <bank.json> <label> <out.json>
Each test returns True (pass), False (fail) or None (not applicable to this build).
"""
import json, re, sys, time
from playwright.sync_api import sync_playwright

HTML, BANK, LABEL, OUT = sys.argv[1:5]
bankdoc = json.load(open(BANK, encoding='utf-8'))
bank = bankdoc['statements']; meta = bankdoc['metadata']
PROFILES = [p for p in meta['commentProfiles'] if p.startswith('Stage 6')]

def pick(**kw):
    for s in bank:
        if all(s.get(k) == v for k, v in kw.items()):
            return s
    raise LookupError(kw)

results = []
def rec(tid, case, expected, actual, passed):
    results.append(dict(id=tid, case=case, expected=expected, actual=actual, passed=passed))
    print(f"{ {True:'PASS',False:'FAIL',None:'N/A '}[passed] }  {tid:<10} {case}  | {actual}", flush=True)

with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = br.new_context(permissions=['clipboard-read', 'clipboard-write'])
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: m.type == 'error' and errors.append(m.text))

    def load(clear_storage=True):
        page.goto('file://' + HTML)
        page.wait_for_selector('#bank-grid .card')
        if clear_storage:
            page.evaluate('() => { try { localStorage.clear(); } catch(e){} }')
    def chip(group, value):
        page.click(f'#filter-{group} .chip[data-value="{value}"]')
    def chip_active(group, value):
        return page.locator(f'#filter-{group} .chip[data-value="{value}"]').get_attribute('class').split().count('active') == 1
    def ensure(group, value):
        if not chip_active(group, value): chip(group, value)
    def select(sid):
        btn = page.locator(f'#bank-grid .card[data-id="{sid}"] .select-btn')
        if btn.count() == 0: return 'not-in-bank'
        if btn.is_disabled(): return 'disabled:' + btn.inner_text()
        btn.click(); return 'ok'
    def copy_on(pfx): return page.locator(f'#copy-{pfx}').is_enabled()
    def preview(pfx): return page.locator(f'#preview-{pfx}').inner_text()
    def valtext(pfx): return page.locator(f'#validation-{pfx}').inner_text()
    def filled(pfx): return ['filled' in page.locator(f'#dz-{pfx}-{i}').get_attribute('class') for i in (1, 2, 3)]
    def msg(pfx): return page.locator(f'#copy-msg-{pfx}').inner_text()
    def has_hook(): return page.evaluate('() => !!window.__commentBuilderTest')
    def bank_ids(): return page.eval_on_selector_all('#bank-grid .card', 'els => els.map(e => e.dataset.id)')
    def clipboard(): return page.evaluate('navigator.clipboard.readText()')
    byid = {s['id']: s for s in bank}

    # ---------------- D: data ----------------
    load()
    st = page.locator('#data-status').inner_text()
    rec('D01', 'Load offline', '3520 loaded, no JS errors', st, '3520' in st and not errors)
    emb = page.evaluate("() => JSON.parse(document.getElementById('statement-data').textContent)")
    same = emb == bankdoc
    diffs = sum(1 for a, b in zip(emb['statements'], bank) if a != b) + abs(len(emb['statements']) - len(bank))
    rec('D02', 'Embedded bank == statement_bank_v5.1.json', '0 record changes', f'identical={same}; changed records={diffs}', same and diffs == 0)

    # ---------------- Context lock (F1/F2) ----------------
    load()
    ids = [pick(stage='Stage 4', commentType='learning_strength', category='P')['id'],
           pick(stage='Stage 6', commentType='learning_strength', category='C', course='Music 2', stageCourse='HSC')['id'],
           pick(stage='Stage 5', commentType='learning_strength', category='L')['id']]
    r = [select(i) for i in ids]
    rec('F1', 'No Stage: try to mix Stage 4/6/5 in one comment', 'selection blocked; copy disabled', f'{r}; copy={copy_on("LS")}',
        not copy_on('LS') and all(x.startswith('disabled') for x in r))
    notice = page.locator('#context-notice').inner_text() if page.locator('#context-notice').count() else ''
    rec('F1b', 'No Stage: on-screen guidance', 'notice explains Stage needed', notice or '(none)', 'Stage' in notice)

    load(); chip('stage', 'Stage 6')
    ids = [pick(stage='Stage 6', commentType='learning_strength', category='P', course='Music 1', stageCourse='Preliminary')['id'],
           pick(stage='Stage 6', commentType='learning_strength', category='M', course='Music 2', stageCourse='Preliminary')['id'],
           pick(stage='Stage 6', commentType='learning_strength', category='A', course='Music 2', stageCourse='HSC')['id']]
    r = [select(i) for i in ids]
    rec('F2', 'Stage 6, no Course/Level: try to mix M1/M2, Prelim/HSC', 'selection blocked; copy disabled', f'{r}; copy={copy_on("LS")}',
        not copy_on('LS') and all(x.startswith('disabled') for x in r))
    chip('course', 'Music 1')
    r2 = select(ids[0])
    rec('F2b', 'Stage 6, Course set but not Stage Course', 'still blocked', r2, r2.startswith('disabled'))

    # Defence in depth: stale/injected out-of-context record must fail validation
    load(); chip('stage', 'Stage 4')
    for c in 'PCL': select(pick(stage='Stage 4', commentType='learning_strength', category=c)['id'])
    if has_hook():
        page.evaluate("""(s) => { const T = window.__commentBuilderTest; T.state.selected.learning_strength[2] = {statement: s, category: s.category}; }""",
                      pick(stage='Stage 5', commentType='learning_strength', category='L'))
        chip('tier', 'Sound'); chip('tier', 'Sound')  # any filter click re-validates
        rec('V03d', 'Injected Stage 5 record into Stage 4 comment', 'context check fails; copy disabled',
            f'copy={copy_on("LS")}; ' + [l for l in valtext('LS').split('\n') if 'context' in l][0], not copy_on('LS'))
        page.evaluate("() => navigator.clipboard.writeText('SENTINEL')")
        page.evaluate("() => { document.getElementById('copy-LS').disabled = false; }")  # simulate a stale enabled button
        page.click('#copy-LS')
        rec('V03e', 'Copy forced on an invalid comment (stale enabled button)', 'copy-time re-check refuses; clipboard untouched',
            f'msg="{msg("LS")}"; clipboard={clipboard()!r}', clipboard() == 'SENTINEL')
    else:
        rec('V03d', 'Injected out-of-context record', 'context check fails', 'no test hook in this build', None)

    # ---------------- S04 Stage 4 ----------------
    load(); chip('stage', 'Stage 4'); chip('unit', 'Jazz')
    vis = bank_ids()
    unit_ok = all(byid[i]['unit'] == 'Jazz' for i in vis)
    for ct, pfx in (('learning_strength', 'LS'), ('strategy_to_improve', 'STI')):
        for c in 'PCL': select(pick(stage='Stage 4', commentType=ct, category=c, unit='Jazz')['id'])
    labels = [page.locator(f'#dz-label-LS-{i}').text_content() for i in (1, 2, 3)]
    rec('S04', 'Stage 4 Standard, unit Jazz, both outputs', 'P/C/L; unit filter exact; both copyable',
        f'labels={labels}; bank all Jazz={unit_ok} ({len(vis)}); LS={copy_on("LS")} STI={copy_on("STI")}',
        unit_ok and copy_on('LS') and copy_on('STI') and [l.split('. ')[1] for l in labels] == ['Performance', 'Composition', 'Listening'])
    page.click('#copy-STI')
    rec('C01', 'Clipboard equals preview (Stage 4 STI)', 'identical', f'match={clipboard() == preview("STI")}', clipboard() == preview('STI'))

    # Stage 4 unit mix -> allowed with warning (decision Q1)
    load(); chip('stage', 'Stage 4')
    for c, u in (('P', 'Jazz'), ('C', 'Sound Lab'), ('L', 'Beats and Tunes')):
        select(pick(stage='Stage 4', commentType='learning_strength', category=c, unit=u)['id'])
    v = valtext('LS')
    rec('Q1-unit', 'Stage 4: three different units', 'allowed + amber warning', f'copy={copy_on("LS")}; warning={"Mixed units" in v}',
        copy_on('LS') and 'Mixed units' in v)
    chip('unit', 'Jazz')
    rec('Q1-unit2', 'Stage 4: change Unit chip after selecting', 'selections kept (browse filter)', f'filled={filled("LS")}', filled('LS') == [True]*3)

    # ---------------- S05 Stage 5 + instruments ----------------
    load(); chip('stage', 'Stage 5'); chip('category', 'P'); chip('instrument', 'Guitar')
    vis = bank_ids()
    inst_ok = all(byid[i]['instrument'] == 'Guitar' and byid[i]['category'] == 'P' for i in vis)
    chip('category', 'P')  # clear category
    chip('instrument', 'Guitar')  # clear instrument
    for ct in ('learning_strength', 'strategy_to_improve'):
        select(pick(stage='Stage 5', commentType=ct, category='P', instrument='Guitar')['id'])
        for c in 'CL': select(pick(stage='Stage 5', commentType=ct, category=c)['id'])
    rec('S05', 'Stage 5 Standard, Guitar, both outputs', 'instrument filter exact; both copyable',
        f'bank all Guitar P={inst_ok} ({len(vis)}); LS={copy_on("LS")} STI={copy_on("STI")}', inst_ok and copy_on('LS') and copy_on('STI'))

    # ---------------- S06 matrix ----------------
    for course in ('Music 1', 'Music 2'):
        for level in ('Preliminary', 'HSC'):
            for prof in PROFILES:
                cats = meta['commentProfiles'][prof]
                load(); chip('stage', 'Stage 6'); chip('course', course); chip('stageCourse', level); ensure('commentProfile', prof)
                vis = bank_ids()
                leak = [i for i in vis if byid[i]['stage'] != 'Stage 6' or byid[i]['course'] != course
                        or byid[i]['stageCourse'] != level or byid[i]['category'] not in cats]
                for ct in ('learning_strength', 'strategy_to_improve'):
                    for c in cats:
                        select(pick(stage='Stage 6', course=course, stageCourse=level, commentType=ct, category=c)['id'])
                labels = [page.locator(f'#dz-label-LS-{i}').text_content().split('. ', 1)[1] for i in (1, 2, 3)]
                exp_labels = [meta['categoryLabelOverrides'][prof][c] for c in cats]
                ok = not leak and labels == exp_labels and copy_on('LS') and copy_on('STI')
                rec(f'S06', f'{course} {level} — {prof.replace("Stage 6 ", "")}',
                    f'{"/".join(cats)}; no leaks; both copyable',
                    f'{len(vis)} shown, leaks={len(leak)}, labels={"/".join(labels)}, LS={copy_on("LS")} STI={copy_on("STI")}', ok)

    # Stage 6 topic mix -> allowed with warning
    load(); chip('stage', 'Stage 6'); chip('course', 'Music 1'); chip('stageCourse', 'Preliminary')
    for c, t in (('P', 'Baroque Music'), ('M', 'Classical Music'), ('A', 'Popular Music')):
        select(pick(stage='Stage 6', course='Music 1', stageCourse='Preliminary', commentType='learning_strength', category=c, topic=t)['id'])
    v = valtext('LS')
    rec('Q1-topic', 'Music 1 Prelim: three different topics', 'allowed + amber warning', f'copy={copy_on("LS")}; warning={"Mixed topics" in v}',
        copy_on('LS') and 'Mixed topics' in v)
    chip('topic', 'Baroque Music')
    rec('Q1-topic2', 'Change Topic chip after selecting', 'selections kept', f'filled={filled("LS")}', filled('LS') == [True]*3)

    # ---------------- V03 context changes ----------------
    load(); chip('stage', 'Stage 6'); chip('course', 'Music 1'); chip('stageCourse', 'Preliminary')
    select(pick(stage='Stage 6', course='Music 1', stageCourse='Preliminary', commentType='learning_strength', category='P')['id'])
    chip('course', 'Music 2')
    a = filled('LS')
    chip('course', 'Music 1'); select(pick(stage='Stage 6', course='Music 1', stageCourse='Preliminary', commentType='learning_strength', category='P')['id'])
    chip('stageCourse', 'HSC'); b = filled('LS')
    chip('stageCourse', 'Preliminary'); select(pick(stage='Stage 6', course='Music 1', stageCourse='Preliminary', commentType='learning_strength', category='P')['id'])
    chip('commentProfile', 'Stage 6 Composition'); c = filled('LS')
    chip('commentProfile', 'Stage 6 Performance'); select(pick(stage='Stage 6', course='Music 1', stageCourse='Preliminary', commentType='learning_strength', category='P')['id'])
    chip('stage', 'Stage 5'); d = filled('LS')
    rec('V03', 'Change Course / Stage Course / Profile / Stage after selecting', 'all clear selections',
        f'course={a} level={b} profile={c} stage={d}', a == b == c == d == [False]*3)

    # ---------------- V04 wrong builder / category ----------------
    load(); chip('stage', 'Stage 5')
    sid = pick(stage='Stage 5', commentType='strategy_to_improve', category='P')['id']
    page.locator(f'#bank-grid .card[data-id="{sid}"]').drag_to(page.locator('#dz-LS-1'))
    m1 = msg('LS'); f1 = filled('LS')[0]
    sid = pick(stage='Stage 5', commentType='learning_strength', category='C')['id']
    page.locator(f'#bank-grid .card[data-id="{sid}"]').drag_to(page.locator('#dz-LS-1'))
    m2 = msg('LS'); f2 = filled('LS')[0]
    rec('V04', 'Drop Strategy in Strengths; Composition in Performance zone', 'both rejected + explained',
        f'"{m1}" / "{m2}"', not f1 and not f2 and bool(m1) and bool(m2))

    # ---------------- V01 / V02 / R ----------------
    load(); chip('stage', 'Stage 5')
    for c in 'PC': select(pick(stage='Stage 5', commentType='learning_strength', category=c)['id'])
    rec('V02', 'Two of three slots', 'copy disabled', f'copy={copy_on("LS")}', not copy_on('LS'))
    select(pick(stage='Stage 5', commentType='learning_strength', category='L')['id'])
    rec('V01', 'Three valid slots', 'copy enabled, all checks ✔', f'copy={copy_on("LS")}; ✘ count={valtext("LS").count("✘")}', copy_on('LS') and '✘' not in valtext('LS'))
    for c in 'PCL': select(pick(stage='Stage 5', commentType='strategy_to_improve', category=c)['id'])
    chip('tier', 'Basic'); chip('category', 'C'); page.click('#reset-filters')
    rec('R01', 'Reset Filters', 'selections and Stage kept', f'LS={filled("LS")} STI={filled("STI")} stage active={chip_active("stage","Stage 5")}',
        filled('LS') == filled('STI') == [True]*3 and chip_active('stage', 'Stage 5'))
    page.click('#clear-LS')
    rec('R02', 'Clear one output', 'other unaffected', f'LS={filled("LS")} STI={filled("STI")}', filled('LS') == [False]*3 and filled('STI') == [True]*3)

    # ---------------- V05 / V06 validator unit tests (synthetic) ----------------
    load()
    if has_hook():
        cases = [("Plays well. Composes well. Listens well.", 3), ("Plays well? Composes well! Listens well.", 3),
                 ("Uses e.g. scales and arpeggios. Composes well. Listens well.", 3), ("Plays at 1.5 times tempo. Composes. Listens.", 3),
                 ("Plays well. Composes well. Listens well. Extra sentence.", 4), ("Plays well. Composes well", 1),
                 ("Plays “well.” Composes well. Listens (carefully.)", 3)]
        got = page.evaluate("cs => cs.map(c => window.__commentBuilderTest.countSentences(c[0]))", cases)
        bad = [(c[0], c[1], g) for c, g in zip(cases, got) if c[1] != g]
        rec('V06', 'Sentence counter: ?, !, e.g., decimals, quotes, 4 sentences, missing stop', 'all counts correct', f'mismatches={bad}', not bad)

        def synthetic(texts, cats=('P', 'C', 'L')):
            return [dict(id=f'TEST{i}', text=t, stage='Stage 5', commentType='learning_strength', category=c,
                         course=None, stageCourse=None, topic=None, unit=None) for i, (t, c) in enumerate(zip(texts, cats))]
        page.evaluate("() => {}")
        chip('stage', 'Stage 5')
        probes = {
            'pronoun': ['Her technique is secure.', 'Composes with clarity.', 'Listens with focus.'],
            'them': ['Applies feedback given to them.', 'Composes with clarity.', 'Listens with focus.'],
            'first person': ['I am pleased with performance work.', 'Composes with clarity.', 'Listens with focus.'],
            'the student': ['The student performs with control.', 'Composes with clarity.', 'Listens with focus.'],
            'two sentences': ['Performs with control and composes with clarity', 'Also listens.', 'Listens with focus.'],
            'missing stop': ['Performs with control.', 'Composes with clarity.', 'Listens with focus'],
        }
        out = {}
        for name, texts in probes.items():
            out[name] = page.evaluate("""(recs) => { const T = window.__commentBuilderTest;
                T.state.selected.learning_strength = recs.map(r => ({statement: r, category: r.category}));
                const v = T.validateComment('learning_strength');
                return {allPass: v.allPass, failed: v.checks.filter(c => !c.pass).map(c => c.label)}; }""", synthetic(texts))
        ok = all(not v['allPass'] for v in out.values())
        rec('V05', 'Synthetic policy breaches (pronoun, them, first person, "the student", 2 sentences, missing stop)',
            'each rejected', '; '.join(f'{k}: {"rejected" if not v["allPass"] else "ACCEPTED"}' for k, v in out.items()), ok)
    else:
        rec('V06', 'Sentence counter edge cases', 'all counts correct', 'no test hook in this build', None)
        rec('V05', 'Synthetic policy breaches', 'each rejected', 'no test hook in this build', None)

    # ---------------- V07 character count / limit ----------------
    load(); chip('stage', 'Stage 5')
    for c in 'PCL': select(pick(stage='Stage 5', commentType='strategy_to_improve', category=c)['id'])
    if page.locator('#charlimit-STI').count():
        n = len(preview('STI'))
        count_txt = page.locator('#charcount-STI').inner_text()
        page.fill('#charlimit-STI', str(n - 1))
        over_copy = copy_on('STI'); over_txt = page.locator('#charcount-STI').inner_text()
        page.fill('#charlimit-STI', str(n))
        at_copy = copy_on('STI')
        page.fill('#charlimit-STI', str(n - 1))
        load(clear_storage=False); kept = page.locator('#charlimit-STI').input_value()
        page.fill('#charlimit-STI', '')
        rec('V07', 'Character count; limit = length−1, then = length; persists on reload',
            'count visible; over → copy disabled; at limit → enabled; limit remembered',
            f'"{count_txt}" → over: copy={over_copy} "{over_txt}"; at limit: copy={at_copy}; after reload limit={kept}',
            str(n) in count_txt and not over_copy and at_copy and kept == str(n - 1))
        load()
        lim = page.locator('#charlimit-STI').input_value()
        rec('V07b', 'Default limit', 'blank (no Sentral limit assumed)', f'"{lim}"', lim == '')
    else:
        rec('V07', 'Character count / limit', 'visible + configurable', 'no character count in this build', False)

    # ---------------- Q4 General swap (Stage 4/5 Strategies) ----------------
    load(); chip('stage', 'Stage 4')
    g1 = pick(stage='Stage 4', commentType='strategy_to_improve', category='G', subcategory='work_ethic')
    g2 = pick(stage='Stage 4', commentType='strategy_to_improve', category='G', subcategory='home_practice')
    swap = page.locator(f'#bank-grid .card[data-id="{g1["id"]}"] .swap-btn')
    if swap.count() == 3:
        for c in 'PC': select(pick(stage='Stage 4', commentType='strategy_to_improve', category=c)['id'])
        swap.nth(2).click()  # replace Listening
        note = page.locator('#dz-STI-3 .swap-note').text_content() if page.locator('#dz-STI-3 .swap-note').count() else ''
        ok1 = copy_on('STI') and preview('STI').endswith(g1['text'])
        page.locator(f'#bank-grid .card[data-id="{g2["id"]}"] .swap-btn').nth(0).click()  # second General -> should be refused
        m = msg('STI')
        p_still = page.locator('#dz-STI-1 .dz-card').inner_text()
        ok2 = 'Only one General' in m and g2['text'] not in p_still
        rec('Q4', 'Stage 4 Strategies: General replaces Listening; 2nd General refused',
            'copyable with note; second refused', f'copy={copy_on("STI")}; note="{note}"; 2nd msg="{m}"', ok1 and ok2 and 'Listening' in note)
        page.click('#clear-STI')
        for c in 'CL': select(pick(stage='Stage 4', commentType='strategy_to_improve', category=c)['id'])
        page.locator(f'#bank-grid .card[data-id="{g1["id"]}"]').drag_to(page.locator('#dz-STI-1'))
        rec('Q4b', 'Drag General onto Performance slot', 'accepted as swap', f'copy={copy_on("STI")}; filled={filled("STI")}', copy_on('STI') and filled('STI') == [True]*3)
        load(); chip('stage', 'Stage 6'); chip('course', 'Music 2'); chip('stageCourse', 'HSC'); chip('commentProfile', 'Stage 6 Viva Voce')
        has_swap = page.locator('#bank-grid .swap-btn').count()
        rec('Q4c', 'Stage 6 Viva Voce (G is a normal slot)', 'no swap buttons', f'swap buttons={has_swap}', has_swap == 0)
    else:
        rec('Q4', 'Stage 4/5 General strategy usable', 'swap available', f'button: {select(g1["id"])}', False)

    # ---------------- Small fixes ----------------
    load(); chip('stage', 'Stage 4')
    lbl = page.locator('#filter-category .chip[data-value="G"]').inner_text()
    rec('F5', 'Stage 4/5 category chip for G', '"General"', lbl, lbl == 'General')
    load(); chip('stage', 'Stage 6'); chip('commentProfile', 'Stage 6 Performance')
    act = page.locator('#filter-commentProfile .chip.active').count()
    rec('F6', 'Click the active profile chip', 'stays selected', f'active={act}', act == 1)

    # ---------------- X: Strengths <-> Strategies cross-check (v5.3) ----------------
    def xc(): return page.locator('#crosscheck').text_content() if page.locator('#crosscheck').count() else None
    def build_both(stage, ls_kw, sti_kw, extra=None):
        load(); chip('stage', stage)
        if extra: extra()
        for ct, kw in (('learning_strength', ls_kw), ('strategy_to_improve', sti_kw)):
            for c, k in kw.items():
                select(pick(stage=stage, commentType=ct, category=c, **k)['id'])
    if page.locator('#crosscheck').count() or True:
        build_both('Stage 5', {'P': dict(instrument='Guitar'), 'C': {}, 'L': {}}, {'P': dict(instrument='Voice'), 'C': {}, 'L': {}})
        t = xc()
        rec('X01', 'Stage 5: Strengths Guitar vs Strategies Voice', 'instrument reminder; both still copyable',
            f'panel="{(t or "")[:90]}"; LS copy={copy_on("LS")} STI copy={copy_on("STI")}; in LS checklist={"Cross-check" in valtext("LS")}',
            t is not None and 'instrument differs' in t and copy_on('LS') and copy_on('STI') and 'Cross-check' in valtext('LS'))
        build_both('Stage 5', {'P': dict(instrument='Instrument', tier='Sound'), 'C': dict(tier='Sound'), 'L': dict(tier='Sound')},
                   {'P': dict(instrument='Guitar', tier='Sound'), 'C': dict(tier='Sound'), 'L': dict(tier='Sound')})
        t = xc()
        rec('X02', 'Generic "Instrument" vs Guitar, same tiers', 'no reminder (generic is compatible)', f'panel="{(t or "")[:90]}"',
            t is not None and t.startswith('✔'))
        def s6(): chip('course', 'Music 2'); chip('stageCourse', 'Preliminary')
        load(); chip('stage', 'Stage 6'); s6()
        for ct, tp in (('learning_strength', 'Baroque Music'), ('strategy_to_improve', 'Classical Music')):
            for c in ('P', 'M', 'A'):
                select(pick(stage='Stage 6', course='Music 2', stageCourse='Preliminary', commentType=ct, category=c, topic=tp, tier='Thorough')['id'])
        t = xc()
        rec('X03', 'Music 2 Prelim: Strengths Baroque vs Strategies Classical', 'topic reminder', f'panel="{(t or "")[:110]}"',
            t is not None and 'Topic differs' in t and copy_on('LS') and copy_on('STI'))
        build_both('Stage 4', {'P': dict(unit='Jazz', tier='Sound'), 'C': dict(unit='Jazz', tier='Sound'), 'L': dict(unit='Jazz', tier='Sound')},
                   {'P': dict(unit='Sound Lab', tier='Sound'), 'C': dict(unit='Sound Lab', tier='Sound'), 'L': dict(unit='Sound Lab', tier='Sound')})
        t = xc()
        rec('X04', 'Stage 4: Strengths Jazz vs Strategies Sound Lab', 'unit reminder', f'panel="{(t or "")[:110]}"', t is not None and 'Unit differs' in t)
        build_both('Stage 5', {'P': dict(instrument='Piano', tier='Extensive'), 'C': dict(tier='Sound'), 'L': dict(tier='Sound')},
                   {'P': dict(instrument='Piano', tier='Elementary'), 'C': dict(tier='Thorough'), 'L': dict(tier='Sound')})
        t = xc()
        rec('X05', 'Tier gap: P Extensive vs Elementary (2 levels); C Sound vs Thorough (1 level)', 'P flagged, C not',
            f'panel="{(t or "")[:120]}"', t is not None and 'Performance tier gap' in t and 'Composition tier gap' not in t)
        load(); chip('stage', 'Stage 4')
        for c in 'PCL': select(pick(stage='Stage 4', commentType='learning_strength', category=c, unit='Jazz', tier='Extensive')['id'])
        for c in 'PC': select(pick(stage='Stage 4', commentType='strategy_to_improve', category=c, unit='Jazz', tier='Extensive')['id'])
        g = pick(stage='Stage 4', commentType='strategy_to_improve', category='G', tier='Basic')
        if page.locator(f'#bank-grid .card[data-id="{g["id"]}"] .swap-btn').count():
            page.locator(f'#bank-grid .card[data-id="{g["id"]}"] .swap-btn').nth(2).click()
        t = xc()
        rec('X06', 'General (Basic) swapped into Listening vs Listening strength (Extensive)', 'not a tier gap (different category)',
            f'panel="{(t or "")[:110]}"', t is not None and 'tier gap' not in t)
        load(); chip('stage', 'Stage 5')
        select(pick(stage='Stage 5', commentType='learning_strength', category='P')['id'])
        t = xc()
        rec('X07', 'Only Strengths started', 'cross-check waits for both', f'panel="{t}"', t is not None and t.startswith('Shown once'))

    # ---------------- A01 keyboard ----------------
    load()
    info = page.evaluate("""() => { const c = document.querySelector('#filter-stage .chip');
        return {tag: c.tagName, pressed: c.getAttribute('aria-pressed')}; }""")
    kb = False
    if info['tag'] == 'BUTTON':
        page.focus('#filter-stage .chip[data-value="Stage 5"]'); page.keyboard.press('Enter')
        e1 = chip_active('stage', 'Stage 5')
        pressed = page.get_attribute('#filter-stage .chip[data-value="Stage 5"]', 'aria-pressed')
        page.keyboard.press('Space'); e2 = chip_active('stage', 'Stage 5')
        kb = e1 and pressed == 'true' and not e2
    rec('A01', 'Keyboard: focus Stage chip, Enter selects, Space deselects; aria-pressed', 'operable', f'{info}; keyboard ok={kb}', kb)

    rec('E01', 'JavaScript errors during whole run', 'none', str(errors[:3]) if errors else 'none', not errors)
    br.close()

json.dump(dict(build=LABEL, results=results), open(OUT, 'w'), indent=1)
pc = sum(1 for r in results if r['passed'] is True); fc = sum(1 for r in results if r['passed'] is False); na = sum(1 for r in results if r['passed'] is None)
print(f'\n{LABEL}: {pc} pass, {fc} fail, {na} n/a of {len(results)}')
