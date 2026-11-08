#!/usr/bin/env python3
"""HFN form label → wazn-net pattern crosswalk (owner 2026-11-08: «نفذ كل … جدول يربط أسماء الأبنية في HFN بأوزان wazn-net»).

HFN events.form uses 35 labels. Weak verbs carry a surface template plus the base pattern in parentheses («أَفْعَى (أفعل ناقص)»,
«افْتَالَ (افتعل أجوف)»); wazn-net's tables (data/awzaan_af3aal_all.csv) list base patterns only (أَفْعَلَ W15 …). The crosswalk maps
each label to its base pattern, wazn ids and code, and the weak class the label states. Nothing in HFN or wazn-net is changed.

Check (no trust in the mapping by name alone): for every live event whose base pattern is a derived form II–X, the engine
(engines.derivation_engine._apply_wazn) builds the verb from the event's root with the mapped code; the generated past is compared with
HFN's verb (diacritics and ٱ/ا removed). Agreement per label is written next to the mapping. Roots the engine refuses (hamzated,
lafif, quadriliteral: core/support.check_supported) are counted as NOT_SUPPORTED, not as failures.
Input  : HusseinFrameNet release (newest by default; HFN_RELEASE env to pin) events.csv
Output : data/hfn_form_crosswalk.tsv, data/hfn_form_crosswalk_mismatches.tsv
Usage  : python3 scripts/build_hfn_form_crosswalk.py"""
import csv, os, re, sys, collections
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, W)
from core.types import RootType
from engines.derivation_engine import _apply_wazn
NET = os.environ.get('ARABIC_NET_HOME', os.path.dirname(W))
REL = os.environ.get('HFN_RELEASE') or max((d for d in os.listdir(os.path.join(NET, 'HusseinFrameNet', 'release')) if re.fullmatch(r'release_v\d+', d)),
                                           key=lambda d: int(d[9:]))
EV = os.path.join(NET, 'HusseinFrameNet', 'release', REL, 'events.csv')
HAR = re.compile(r'[ً-ْٰـ]')
def bare(s): return HAR.sub('', s or '').replace('ٱ', 'ا').replace('إ', 'ا').replace('أ', 'ا').strip()
def nz(s): return bare(s).replace('ا', '')          # compare consonant skeleton (alif seats/wasl vary)
def pkey(s): return re.sub(r'[\u064b-\u0650\u0652\u0670\u0640]', '', s or '').replace('ٱ', 'ا').replace('إ', 'ا').replace('أ', 'ا').replace('اِ', 'ا').strip()   # keeps shadda
WZ = list(csv.DictReader(open(os.path.join(W, 'data', 'awzaan_af3aal_all.csv'), encoding='utf-8-sig')))
BY = collections.defaultdict(list)
for r in WZ: BY[pkey(r['wazn'])].append(r)
WEAK = {'أجوف': 'AJWAF', 'ناقص': 'NAQIS', 'ناقص واوي': 'NAQIS_WAW', 'ناقص يائي': 'NAQIS_YAA'}
def parse(label):
    m = re.match(r'^(.*?)\s*\((.*)\)\s*$', label)
    surface, paren = (m.group(1), m.group(2)) if m else (label, '')
    base, weak = surface, ''
    if paren:
        p = paren.split()
        if p[0] in WEAK or paren in WEAK: weak = WEAK.get(paren, WEAK.get(p[0], ''))     # «فَعَلَ (ناقص واوي)»
        else: base, weak = p[0], WEAK.get(' '.join(p[1:]), ' '.join(p[1:]))              # «أَفْعَى (أفعل ناقص)»
    if surface == 'فَعَّ': base, weak = 'فَعَلَ', 'MUDAAF'                                    # مَدَّ: فَعَلَ المضاعف
    return surface, base, weak
def root_type(K):
    a, b, c = K
    if sum(x in 'وي' for x in K) >= 2: return None                       # لفيف: not supported by the engine (D-M08)
    if b == c: return RootType.MUDAAF
    if b in 'وي': return RootType.AJWAF_WAW if b == 'و' else RootType.AJWAF_YAA
    if c in 'وي': return RootType.NAQIS_WAW if c == 'و' else RootType.NAQIS_YAA
    if a == 'و': return RootType.MITHAL_WAW
    return RootType.SAHIH
E = [e for e in csv.DictReader(open(EV, encoding='utf-8')) if not e['event_review_v36'].startswith('WITHDRAWN')]
labels = collections.Counter(e['form'] for e in E)
rows, mism = [], []
for label, n in labels.most_common():
    surface, base, weak = parse(label)
    alts = base.split('/')
    hits = list({r['id']: r for a in alts for r in BY.get(pkey(a), [])}.values())
    code = sorted({r['wazn_code'] for r in hits if r['wazn_code']})
    chk = collections.Counter()
    if len(code) == 1 and code[0] in ('II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'):
        for e in (x for x in E if x['form'] == label):
            K = e['root_K']
            if len(K) != 3 or 'ء' in K:
                chk['NOT_SUPPORTED'] += 1; continue
            if root_type(K) is None:
                chk['NOT_SUPPORTED'] += 1; continue
            try:
                v = _apply_wazn(code[0], K[0], K[1], K[2], root_type(K))['verb']
            except Exception as ex:
                chk['NOT_SUPPORTED'] += 1; continue
            ok = any(nz(x) == nz(e['verb']) for x in v.split('/'))
            chk['MATCH' if ok else 'MISMATCH'] += 1
            if not ok: mism.append({'event_id': e['event_id'], 'form': label, 'root_K': K, 'hfn_verb': e['verb'], 'engine_verb': v})
    rows.append({'hfn_form': label, 'n_events_live': n, 'surface_template': surface, 'base_wazn': base,
                 'wazn_ids': '|'.join(r['id'] for r in hits), 'wazn_code': '|'.join(code), 'weak_class': weak,
                 'categories': '|'.join(sorted({r['category'] for r in hits})),
                 'engine_match': chk['MATCH'], 'engine_mismatch': chk['MISMATCH'], 'engine_not_supported': chk['NOT_SUPPORTED'],
                 'status': 'MAPPED' if hits else 'UNMAPPED'})
with open(os.path.join(W, 'data', 'hfn_form_crosswalk.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, list(rows[0]), delimiter='\t'); w.writeheader(); w.writerows(rows)
with open(os.path.join(W, 'data', 'hfn_form_crosswalk_mismatches.tsv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, ['event_id', 'form', 'root_K', 'hfn_verb', 'engine_verb'], delimiter='\t'); w.writeheader(); w.writerows(mism)
print(REL, 'labels', len(rows), 'unmapped', [r['hfn_form'] for r in rows if r['status'] != 'MAPPED'],
      'engine', sum(r['engine_match'] for r in rows), 'match /', sum(r['engine_mismatch'] for r in rows), 'mismatch')
