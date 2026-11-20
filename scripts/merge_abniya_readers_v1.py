# -*- coding: utf-8 -*-
"""merge_abniya_readers_v1.py <READ_A.tsv> <READ_B.tsv> <out_dir>
يقارن قراءتي القارئين الأعميين لملاحظات أبنية سيبويه (BRIEF_ABN1)، صفّاً صفّاً، في طبقتين لكلٍّ حدّه:
  ١. النطاق = (scope، in_fil، inherit_from): يُنشر الصفّ المتّفق عليه إن بلغ Wilson الأدنى لاتفاق الطبقة 0.78.
  ٢. الشروط = مجموعة conditions: كذلك.
الطبقة التي لا تبلغ الحدّ لا يُنشر منها شيء، وتبقى قراءتاها في KHILAF.
(القياس المجمَّع للحقول كلّها يُطبع أيضاً للعلم.)"""
import csv, math, os, sys

A, B, OUT = sys.argv[1:4]
ra = list(csv.DictReader(open(A, encoding='utf-8'), delimiter='\t'))
rb = list(csv.DictReader(open(B, encoding='utf-8'), delimiter='\t'))
assert [x['id'] for x in ra] == [x['id'] for x in rb] and len(ra) == 290
GATE = 0.78


def conds(x, drop=()):
    return ';'.join(sorted(c.strip() for c in (x['conditions'] or 'NONE').split(';') if c.strip() and c.strip() not in drop)) or 'NONE'


def scope(x):
    return (x['scope'].strip(), x['in_fil'].strip(), (x['inherit_from'] or '—').strip())


def wilson(k, n, z=1.96):
    p = k / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


n = len(ra)
s_ok = [scope(a) == scope(b) for a, b in zip(ra, rb)]
c_ok = [conds(a) == conds(b) for a, b in zip(ra, rb)]
c_ok_novoc = [conds(a, ('VOCALIZATION_NOTE',)) == conds(b, ('VOCALIZATION_NOTE',)) for a, b in zip(ra, rb)]
all_ok = [s and c for s, c in zip(s_ok, c_ok)]
ws, wc = wilson(sum(s_ok), n), wilson(sum(c_ok), n)
stats = [('rows', n),
         ('scope_layer_agree', sum(s_ok)), ('scope_layer_wilson', f'{ws:.4f}'), ('scope_layer_published', 'YES' if ws >= GATE else 'NO'),
         ('conditions_layer_agree', sum(c_ok)), ('conditions_layer_wilson', f'{wc:.4f}'),
         ('conditions_layer_published', 'YES' if wc >= GATE else 'NO'),
         ('info_all_fields_agree', sum(all_ok)), ('info_all_fields_wilson', f'{wilson(sum(all_ok), n):.4f}'),
         ('info_conditions_agree_without_VOCALIZATION_NOTE', sum(c_ok_novoc)),
         ('info_conditions_wilson_without_VOCALIZATION_NOTE', f'{wilson(sum(c_ok_novoc), n):.4f}'),
         ('gate', GATE)]
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'READERS_STATS.tsv'), 'w', encoding='utf-8') as f:
    f.writelines(f'{k}\t{v}\n' for k, v in stats)

S_COLS = ['id', 'scope', 'in_fil', 'inherit_from', 'quote', 'reading', 'rank']
C_COLS = ['id', 'conditions', 'reading', 'rank']
K_COLS = ['id', 'layer', 'scope_A', 'scope_B', 'in_fil_A', 'in_fil_B', 'inherit_A', 'inherit_B', 'conditions_A',
          'conditions_B', 'note_A', 'note_B']
sa, ca, kh = [], [], []
for a, b, s, c in zip(ra, rb, s_ok, c_ok):
    if s and ws >= GATE:
        sa.append(dict(id=a['id'], scope=scope(a)[0], in_fil=scope(a)[1], inherit_from=scope(a)[2],
                       quote=a['quote'] if a['quote'] == b['quote'] else a['quote'] or b['quote'],
                       reading='AGREED_2_BLIND', rank='CANDIDATE'))
    if c and wc >= GATE:
        ca.append(dict(id=a['id'], conditions=conds(a), reading='AGREED_2_BLIND', rank='CANDIDATE'))
    layers = [l for l, ok, w in (('scope', s, ws), ('conditions', c, wc)) if not ok or w < GATE]
    if layers:
        kh.append(dict(id=a['id'], layer='+'.join(layers), scope_A=scope(a)[0], scope_B=scope(b)[0],
                       in_fil_A=scope(a)[1], in_fil_B=scope(b)[1], inherit_A=scope(a)[2], inherit_B=scope(b)[2],
                       conditions_A=conds(a), conditions_B=conds(b), note_A=a['note'], note_B=b['note']))
for name, cols, data in (('SCOPE_AGREED.tsv', S_COLS, sa), ('CONDITIONS_AGREED.tsv', C_COLS, ca),
                         ('READERS_KHILAF.tsv', K_COLS, kh)):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)
for k, v in stats:
    print(f'{k}\t{v}')
print('published scope rows', len(sa), '| conditions rows', len(ca), '| khilaf rows', len(kh))
