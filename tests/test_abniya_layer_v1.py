# -*- coding: utf-8 -*-
"""طبقة معالجة أبنية سيبويه v1: المصدر المجمَّد لم يتغيّر، وكل سجل له صفّ، والنفي لا يُعمَّم خارج نطاقه."""
import csv, hashlib, os, re

H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(H, 'data', 'abniya_layer_v1')
SRC = os.path.join(H, 'data', 'abniya_sibawayh.csv')


def tsv(name):
    return list(csv.DictReader(open(os.path.join(D, name), encoding='utf-8'), delimiter='\t'))


T = {x['id']: x for x in tsv('ABNIYA_TEMPLATES_v1.tsv')}
E = tsv('ABNIYA_EXAMPLES_v1.tsv')
S = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))


def test_source_frozen():
    assert hashlib.sha256(open(SRC, 'rb').read()).hexdigest().startswith('a1c1f7f94378eb6e')


def test_one_row_per_record():
    assert [x['id'] for x in S] == list(T)
    assert len(T) == 419
    for x in S:
        assert T[x['id']]['pattern_vocalized_src'] == x['pattern_vocalized']


def test_templates_are_pure_arabic():
    for t in T.values():
        for p in [t['template']] + [v.strip() for v in t['template_variants'].split('/') if v.strip()]:
            assert p == '' or re.fullmatch(r'[ء-يً-ْ]+', p), t['id']


def test_negation_keeps_scope():
    for t in T.values():
        if t['status_src'] == 'NOT_FOUND_IN_ARABIC':
            assert t['license_candidate'].startswith('NEGATED_'), t['id']
            if t['license_candidate'].startswith('NEGATED_IN_SCOPE:'):
                assert t['scope_reading'] == 'AGREED_2_BLIND'
                assert t['license_candidate'] == 'NEGATED_IN_SCOPE:' + t['scope']
        else:
            assert not t['license_candidate'].startswith('NEGATED')
    s011 = T['S011']
    assert (s011['scope'], s011['in_fil'], s011['license_candidate']) == ('ISM_SIFA', 'YES', 'NEGATED_IN_SCOPE:ISM_SIFA')


def test_projection_is_marked_inferred():
    for e in E:
        assert e['rank'] == 'CANDIDATE'
        if e['projected']:
            assert e['projection_basis'].startswith('INFERRED_FROM_TEMPLATE')
            assert e['projection_status'].startswith('PROJECTED')
        if e['hfn_root_id']:
            assert e['hfn_root_id'].startswith('HFN-R')


def test_all_candidate_unratified():
    assert {t['rank'] for t in T.values()} == {'CANDIDATE'}
    assert {t['owner_ratified'] for t in T.values()} == {'NO'}
