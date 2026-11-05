"""المحرك الصرفي — مقارنة بالقيم الذهبية (tests/gold/conjugation_gold.txt)."""
import pytest

from tests._pilot import PILOT_BY_LETTERS
from tests._gold import TABLES, conjugation_cases, matches, stacked_vowels, PGN14, PGN_IMP
from tests.known_defects import param, DEFECTS
from core.types import RootType, Baab
from engines.morphological_engine import conjugate

_CACHE = {}


def paradigm(letters):
    if letters not in _CACHE:
        r = PILOT_BY_LETTERS[letters]
        _CACHE[letters] = conjugate(letters, RootType(r["root_type"]), Baab(r["morph"]["baab"]))
    return _CACHE[letters]


CASES = conjugation_cases()


@pytest.mark.parametrize("root,table,pgn,gold",
                         [param(cid, r, t, p, g) for cid, r, t, p, g in CASES])
def test_cell_matches_gold(root, table, pgn, gold):
    mood, voice = TABLES[table]
    actual = paradigm(root).table(mood, voice).get(pgn)
    assert actual is not None, "الخلية غير مُولَّدة"
    assert matches(actual, gold), f"المحرك={actual!r}  الذهبي={gold!r}"


def test_gold_covers_every_pilot_root():
    assert {c[1] for c in CASES} == set(PILOT_BY_LETTERS)


@pytest.mark.parametrize("letters", sorted(PILOT_BY_LETTERS))
def test_paradigm_shape(letters):
    p = paradigm(letters)
    assert len(p.cells) == 90
    for code, (mood, voice) in TABLES.items():
        keys = set(p.table(mood, voice))
        assert keys == set(PGN_IMP if code == "AM" else PGN14), code


@pytest.mark.parametrize("letters,table,pgn", [
    param(f"stack-{l}-{c.mood}-{c.voice}-{'/'.join((c.person, c.number, c.gender))}",
          l, (c.mood, c.voice), (c.person, c.number, c.gender))
    for l in sorted(PILOT_BY_LETTERS) for c in paradigm(l).cells
])
def test_no_stacked_vowels(letters, table, pgn):
    form = paradigm(letters).table(*table)[pgn]
    assert not stacked_vowels(form), f"حركتان على حرف واحد: {form!r}"


# ── عيوب بنيوية (fail-closed): نوعٌ لا مصرِّف له يجب ألا يُصرَّف بصمت كالصحيح ──
@pytest.mark.parametrize("letters,rt", [
    param("unsupported-لفيف_مفروق", "وقي", RootType.LAFIF_MAFRUQ),
    param("unsupported-لفيف_مقرون", "طوي", RootType.LAFIF_MAQRUN),
])
def test_unsupported_root_type_fails_closed(letters, rt):
    with pytest.raises((ValueError, NotImplementedError)):
        conjugate(letters, rt, Baab.FAA_YAF_I)
