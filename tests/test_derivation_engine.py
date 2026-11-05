"""المحرك الاشتقاقي — مقارنة بالقيم الذهبية (tests/gold/derivation_gold.txt)."""
import pytest

from tests._pilot import PILOT_BY_LETTERS, PILOT_ROOTS
from tests._gold import derivation_cases, matches, ABSENT
from tests.known_defects import param
from core.types import RootType, Baab
from engines.derivation_engine import derive, derive_from_dict

# جدول العمليات — الوثيقة الدستورية، المبدأ الثاني
CONSTITUTION_OPS = {
    "II": "+سببية", "IV": "+سببية", "III": "+ثنائية",
    "V": "+انعكاسية", "VI": "+انعكاسية", "X": "+طلبية",
    "VII": "−أثر فاعلي", "VIII": "−أثر فاعلي", "IX": "+حالة ثابتة",
}
FIELD = {"verb": "verb", "masdar": "masdar", "faail": "ism_faail", "mafuul": "ism_mafuul"}
I_FIELD = {"faail": "ism_faail", "mafuul": "ism_mafuul", "makan": "ism_makan",
           "zaman": "ism_zaman", "aala": "ism_aala"}

_CACHE = {}


def ds(letters):
    if letters not in _CACHE:
        _CACHE[letters] = derive_from_dict(PILOT_BY_LETTERS[letters])
    return _CACHE[letters]


def lookup(letters, key):
    wazn, field = key.split(".")
    d = ds(letters)
    if wazn == "I":
        return getattr(d, I_FIELD[field])
    for m in d.mazidaat:
        if m.wazn == wazn:
            return getattr(m, FIELD[field])
    return None


CASES = derivation_cases()


@pytest.mark.parametrize("root,key,gold", [param(c, r, k, g) for c, r, k, g in CASES])
def test_form_matches_gold(root, key, gold):
    actual = lookup(root, key)
    if gold == [ABSENT]:
        assert actual is None, f"صيغة غير مرخَّصة مُولَّدة: {actual!r}"
        return
    assert actual is not None, "الصيغة غير مُولَّدة"
    assert matches(actual, gold), f"المحرك={actual!r}  الذهبي={gold!r}"


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_stored_data_passes_through(rd):
    d = ds(rd["letters"])
    m = rd["morph"]
    assert d.masadir_samiyya == m["masadir_samiyya"]
    assert d.masdar_qiyasi == m.get("masdar_qiyasi")
    assert [x.wazn for x in d.mazidaat] == list(m["awzaan_maqbuula"])
    assert {x.wazn: x.meaning for x in d.mazidaat} == m["awzaan_maqbuula"]


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_wazn_op_matches_constitution(rd):
    for x in ds(rd["letters"]).mazidaat:
        assert x.wazn_op == CONSTITUTION_OPS[x.wazn], x.wazn


@pytest.mark.parametrize("wazn", [param("unknown-wazn-XI", "XI")])
def test_unknown_wazn_key_is_not_silently_dropped(wazn):
    """مفتاح وزن غير معروف لا يُسقَط بصمت (fail-closed)."""
    with pytest.raises((ValueError, KeyError)):
        derive("كتب", RootType.SAHIH, Baab.FAA_YAF_U, [], None,
               None, None, None, None, None, {wazn: ""})


@pytest.mark.parametrize("letters", [param("rubai-دحرج", "دحرج")])
def test_quadriliteral_not_truncated(letters):
    """الجذر الرباعي لا يُقطع إلى ثلاثة أحرف بصمت."""
    with pytest.raises((ValueError, NotImplementedError)):
        derive(letters, RootType.SAHIH, Baab.FAA_YAF_U, [], None,
               None, None, None, None, None, {})
