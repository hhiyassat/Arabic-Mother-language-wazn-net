# -*- coding: utf-8 -*-
"""build_abniya_layer_v1.py — طبقة معالجة لأبنية سيبويه (الكتاب ج4 ص242–303) فوق الملف المجمَّد.

المصدر: data/abniya_sibawayh.csv (= taaqol data/awzan-sibawayh-308.csv)، مجمَّد بالبصمة a1c1f7f9…؛ لا يُعدَّل.
المخرجات (data/abniya_layer_v1/):
  ABNIYA_TEMPLATES_v1.tsv  صفّ لكل سجل (419): القالب النظيف منفصلاً عن الملاحظة، وأساس الضبط، وحالة الترخيص.
  ABNIYA_EXAMPLES_v1.tsv   صفّ لكل مثال: المثال كما كُتب ← إسقاط حركات القالب عليه (ضبط مستنتج من القالب لا منقول)
                           ← الأصول المستخرجة بمطابقة القالب ← مفتاح الجذر K في بنك HFN v11.
كل ما هنا CANDIDATE؛ owner_ratified=NO كما في المصدر.
نطاق النفي والإثبات من قراءة قارئين أعميين لملاحظات السجلات (<out_dir>/readers/SCOPE_AGREED.tsv، من merge_abniya_readers_v1.py).
الاستعمال: python3 scripts/build_abniya_layer_v1.py <HFN_repo> <out_dir>"""
import csv, hashlib, os, re, sys, unicodedata
from collections import Counter
from itertools import product

SRC_SHA = 'a1c1f7f94378eb6e4ad5a994ee180c38c2f5da5058fc9ac1a670f25a3555b1a0'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, 'data', 'abniya_sibawayh.csv')
HFN, OUT = sys.argv[1:3]
BANK = os.path.join(HFN, '02_roots', 'HFN_ROOTS_v11.csv')

HARAKAT = 'ًٌٍَُِْ'          # تنوين + فتحة ضمة كسرة سكون
SHADDA = 'ّ'
DIAC = re.compile('[ً-ْٰـ]')
HAMZA = str.maketrans({'أ': 'ء', 'إ': 'ء', 'آ': 'ء', 'ؤ': 'ء', 'ئ': 'ء', 'ٱ': 'ا', 'ى': 'ي', 'ک': 'ك', 'ی': 'ي'})


def K(s):
    """مفتاح الربط كما في HFN hfn_common.K."""
    s = DIAC.sub('', unicodedata.normalize('NFC', s or '')).translate(HAMZA)
    return re.sub(r'[^ء-ي]', '', s)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(SRC) == SRC_SHA, 'المصدر تغيّر عن البصمة المجمَّدة'
rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
assert len(rows) == 419

# ---------- ١. القالب: فصل الملاحظة والبدائل وعلامة الشكّ ----------
ARABIC_TMPL = re.compile(r'^[ء-يً-ْ]+$')


def split_template(v):
    """→ (قوالب، ملاحظة، حالة). الحالة: CLEAN | NOTE_SPLIT | VARIANTS | UNCERTAIN_MARK | UNDETERMINED"""
    v = (v or '').strip()
    note = ''
    m = re.search(r'\s*\(([^)]*)\)\s*', v)
    if m:
        note = m.group(1).strip()
        v = (v[:m.start()] + v[m.end():]).strip()
    uncertain = v.endswith('?') or v.startswith('?')
    v = v.strip('?').strip()
    if not v:
        return [], note, 'UNDETERMINED'
    parts = [p.strip() for p in v.split('/') if p.strip()]
    if not all(ARABIC_TMPL.match(p) for p in parts):
        return [], (note + ' | ' if note else '') + 'نصّ غير قالبيّ: ' + v, 'UNPARSEABLE'
    if uncertain:
        st = 'UNCERTAIN_MARK'
    elif len(parts) > 1:
        st = 'VARIANTS'
    elif note:
        st = 'NOTE_SPLIT'
    else:
        st = 'CLEAN'
    return parts, note, st


def slots(tmpl, quad):
    """القالب ← خانات [(حرف، دور، حركة، شدّة)]؛ الدور R1..R5 للأصول أو AUG للزائد."""
    out, lams = [], 0
    chars = list(unicodedata.normalize('NFC', tmpl))
    i = 0
    while i < len(chars):
        c = chars[i]
        i += 1
        if c in HARAKAT + SHADDA:
            continue
        h, sh = '', False
        while i < len(chars) and chars[i] in HARAKAT + SHADDA:
            if chars[i] == SHADDA:
                sh = True
            else:
                h += chars[i]
            i += 1
        if c == 'ف':
            role = 'R1'
        elif c == 'ع':
            role = 'R2'
        elif c == 'ل':
            if quad:
                lams += 1
                role = f'R{2 + lams}'
            else:
                role = 'R3'
        else:
            role = 'AUG'
        out.append([c, role, h, sh])
    return out


# ---------- ٢. الأمثلة: تقسيم وإسقاط ----------
SEATS = {'ء': set('ءأإآؤئا'), 'أ': set('ءأإآا'), 'إ': set('ءأإا'), 'ا': set('اأإآ'), 'ى': set('ىيا'), 'ي': set('يى'),
         'ة': set('ةه'), 'ه': set('هة')}


def aug_ok(t, e):
    return e == t or e in SEATS.get(t, ())


def split_examples(s):
    """→ [(المجموعة، المثال)]؛ المجموعة 1 قبل «؛» و2 بعدها."""
    out = []
    if not s or s.strip() in ('—', '-'):
        return out
    for g, part in enumerate(s.split('؛'), 1):
        for w in part.split('،'):
            w = w.strip()
            if w:
                out.append((g, w))
    return out


def project(word, sl):
    """→ (المضبوط، الأصول، الحالة، ملاحظة). لا يُقبل إلا تطابقٌ تامّ في عدد الحروف وحروف الزيادة."""
    raw = word
    note = []
    w = re.sub(r'\([^)]*\)', '', word).replace('…', ' ').strip()
    if re.search(r'[0-9٠-٩]', w):
        return '', '', 'NOT_A_WORD', 'رقم في الخانة'
    if ' ' in w:
        return '', '', 'PHRASE', 'أكثر من كلمة'
    w = DIAC.sub('', w)
    art = False
    n_t = len(sl)
    if w.startswith('ال') and len(w) - 2 == n_t:
        art, w = True, w[2:]
        note.append('ال محذوفة')
    suffix = ''
    if len(w) == n_t + 1 and w[-1] in 'ةه' and sl[-1][0] not in 'ةه':
        suffix, w = 'ة', w[:-1]
        note.append('تاء زائدة على القالب')
    if len(w) != n_t:
        return '', '', 'LENGTH_MISMATCH', f'حروف المثال {len(w)} وحروف القالب {n_t}'
    rad, outc = {}, []
    for (t, role, h, sh), e in zip(sl, w):
        if role == 'AUG':
            if not aug_ok(t, e):
                return '', '', 'AUG_MISMATCH', f'الزائد «{t}» قابله «{e}»'
        else:
            if role in rad and K(rad[role]) != K(e):
                return '', '', 'RADICAL_CONFLICT', f'{role}: «{rad[role]}» و«{e}»'
            rad.setdefault(role, e)
        hh = h
        if art and (t, role, h, sh) == tuple(sl[-1]) and h in ('ٌ', 'ٍ'):
            hh = {'ٌ': 'ُ', 'ٍ': 'ِ'}[h]
        outc.append(e + (SHADDA if sh else '') + hh)
    voc = ('ال' if art else '') + ''.join(outc) + suffix
    roots = [rad[k] for k in sorted(rad)]
    return voc, ''.join(roots), 'PROJECTED', '؛ '.join(note)


# ---------- ٣. البنك ----------
bank = {}
for b in csv.DictReader(open(BANK, encoding='utf-8-sig')):
    bank[b['K']] = b

def engine_use(x):
    """كيف يقرأ arabic-sarf-2026 (sarf/cells.py sibawayh_patterns) هذا السجلّ: يتخطّى غير الموجود وغير المحسوم و«?»،
    ويأخذ pattern_vocalized كما هو؛ فإن كان فيه ملاحظة أو «/» دخلت حروفها خلايا القالب."""
    pv = x['pattern_vocalized']
    if x['status'] not in ('EXISTS', 'RARE') or x['vocalization_basis'] == 'UNDETERMINED' or '?' in pv:
        return 'SKIPPED_BY_ENGINE'
    return 'USED_NOTE_ABSORBED_INTO_CELLS' if any(c in pv for c in '()/ ') else 'USED_CLEAN'


# ---------- ٤. البناء ----------
assert not os.path.exists(os.path.join(OUT, 'ABNIYA_TEMPLATES_v1.tsv')), 'لا كتابة فوق مخرج قائم'
SCOPE = {x['id']: x for x in csv.DictReader(open(os.path.join(OUT, 'readers', 'SCOPE_AGREED.tsv'), encoding='utf-8'), delimiter='\t')}
KHILAF = {x['id'] for x in csv.DictReader(open(os.path.join(OUT, 'readers', 'READERS_KHILAF.tsv'), encoding='utf-8'), delimiter='\t')
          if 'scope' in x['layer']}


def license_of(x):
    """حالة الترخيص: الحالة في المصدر مقيَّدةً بنطاقها المتّفق عليه. لا يصير نفيٌ مقيَّدٌ نفياً عامّاً."""
    st, i = x['status'], x['id']
    has_remark = x['remark'].strip() not in ('', '—')
    sc = SCOPE.get(i, {}).get('scope', '')
    if not has_remark:
        reading = 'NO_REMARK'
    elif i in KHILAF:
        reading = 'KHILAF'
    else:
        reading = 'AGREED_2_BLIND'
    if st == 'NOT_FOUND_IN_ARABIC':
        if reading == 'KHILAF':
            lic = 'NEGATED_SCOPE_KHILAF'
        elif sc in ('', 'NOT_ABOUT_SCOPE'):
            lic = 'NEGATED_SCOPE_UNSTATED'
        elif sc == 'OTHER':
            lic = 'NEGATED_SCOPE_OTHER'
        else:
            lic = 'NEGATED_IN_SCOPE:' + sc
    else:
        lic = LICENSE[st] + (':' + sc if sc not in ('', 'NOT_ABOUT_SCOPE') else '')
    return lic, reading, sc
T_COLS = ['id', 'page', 'url', 'section', 'pattern_as_printed', 'pattern_vocalized_src', 'template', 'template_variants',
          'template_note', 'template_status', 'n_letters', 'radical_slots', 'vocalization_basis_src', 'flags_src',
          'class_src', 'status_src', 'scope', 'in_fil', 'inherit_from', 'scope_reading', 'license_candidate', 'remark_src', 'n_examples', 'n_projected', 'engine_use',
          'rank', 'owner_ratified']
E_COLS = ['id', 'ex_no', 'group', 'group_label', 'example_src', 'template', 'projected', 'projection_basis', 'radicals',
          'root_K', 'hfn_root_id', 'bb_v21_row', 'ref_maqayis', 'projection_status', 'note', 'rank']
LICENSE = {'EXISTS': 'LICENSED_CANDIDATE', 'RARE': 'RARE_CANDIDATE', 'NOT_FOUND_IN_ARABIC': 'NEGATED_SCOPE_PENDING'}
trows, erows = [], []
for x in rows:
    tm, note, tst = split_template(x['pattern_vocalized'])
    quad = x['section'].startswith(('رباعي', 'خماسي'))
    exs = split_examples(x['examples'])
    cls = x['class']
    labels = {1: 'اسم', 2: 'صفة'} if cls == 'اسم+صفة' else {1: cls if cls not in ('—', '?') else '', 2: ''}
    nproj = 0
    for k, (g, w) in enumerate(exs, 1):
        best = None
        for t in tm or []:
            r = project(w, slots(t, quad))
            if r[2] == 'PROJECTED':
                best = (t,) + r
                break
            best = best or (t,) + r
        if not tm:
            best = ('', '', '', 'NO_TEMPLATE', 'القالب غير محدَّد في المصدر')
        t, voc, rad, st, nt = best
        rk = K(rad) if rad else ''
        b = bank.get(rk) if rk else None
        if st == 'PROJECTED':
            nproj += 1
            if not b:
                # الحرف الظاهر في موضع الأصل قد يكون منقلباً: ء/ا/و/ي ← أحد ء و ي (إعطاء ← عطو، حوائط ← حوط)
                alts = [''.join(p) for p in product(*[('ء', 'و', 'ي') if c in 'ءاوي' else (c,) for c in rk])]
                hits = sorted({a for a in alts if a != rk and a in bank})
                if len(hits) == 1:
                    nt = (nt + '؛ ' if nt else '') + f'الحرف الظاهر {rk} ← الأصل {hits[0]} (حرف علّة أو همزة منقلبة)'
                    rk, b, st = hits[0], bank[hits[0]], 'PROJECTED_ROOT_VIA_WEAK_VARIANT'
                elif hits:
                    nt = (nt + '؛ ' if nt else '') + 'أكثر من أصل محتمل: ' + ' | '.join(hits)
                    st = 'PROJECTED_ROOT_AMBIGUOUS'
                else:
                    st = 'PROJECTED_ROOT_NOT_IN_BANK'
        erows.append(dict(id=x['id'], ex_no=k, group=g, group_label=labels.get(g, ''), example_src=w, template=t,
                          projected=voc,
                          projection_basis='INFERRED_FROM_TEMPLATE (حركات القالب أُسقطت على حروف المثال؛ ليست ضبطاً منقولاً)' if voc else '',
                          radicals=' '.join(rad), root_K=rk, hfn_root_id=b['hfn_root_id'] if b else '',
                          bb_v21_row=b['bb_v21_row'] if b else '', ref_maqayis=b['ref_maqayis'] if b else '',
                          projection_status=st, note=nt, rank='CANDIDATE'))
    pv = x['pattern_vocalized']
    trows.append(dict(id=x['id'], page=x['page'], url=x['url'], section=x['section'],
                      pattern_as_printed=x['pattern_as_printed'], pattern_vocalized_src=pv,
                      template=tm[0] if tm else '', template_variants=' / '.join(tm[1:]), template_note=note,
                      template_status=tst, n_letters=len(slots(tm[0], quad)) if tm else '',
                      radical_slots=' '.join(f'{c}={r}' for c, r, _, _ in slots(tm[0], quad) if r != 'AUG') if tm else '',
                      vocalization_basis_src=x['vocalization_basis'], flags_src=x['flags'], class_src=cls,
                      status_src=x['status'], scope=license_of(x)[2], in_fil=SCOPE.get(x['id'], {}).get('in_fil', ''),
                      inherit_from=SCOPE.get(x['id'], {}).get('inherit_from', ''), scope_reading=license_of(x)[1],
                      license_candidate=license_of(x)[0], remark_src=x['remark'],
                      n_examples=len(exs), n_projected=nproj,
                      engine_use=engine_use(x),
                      rank='CANDIDATE', owner_ratified=x['owner_ratified']))


def dump(name, cols, data):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)


dump('ABNIYA_TEMPLATES_v1.tsv', T_COLS, trows)
dump('ABNIYA_EXAMPLES_v1.tsv', E_COLS, erows)
print('templates', Counter(r['template_status'] for r in trows))
print('examples', len(erows), Counter(r['projection_status'] for r in erows))
print('distinct root_K in bank', len({r['root_K'] for r in erows if r['hfn_root_id']}))
print('license', Counter(r['license_candidate'] for r in trows))
print('engine_use', Counter(r['engine_use'] for r in trows))
