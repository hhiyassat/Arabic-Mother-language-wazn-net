"""محرك الفتحات — مطابقة البنية المسندية لبيانات المالك في pilot_roots.json."""
import pytest

from tests._pilot import PILOT_ROOTS
from tests.known_defects import param
from core.types import SemanticType, PrimaryPredicate
from engines.slots_engine import (parse_predicate_from_dict, group_by_signature,
                                  _resolve_sem_type, _resolve_predicate)


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_predicate_parsed_exactly(rd):
    ps = parse_predicate_from_dict(rd)
    pd = rd["predicate"]
    assert ps.root == rd["letters"]
    assert ps.primary_predicate.value == pd["primary_predicate"]
    assert ps.raw_text == pd.get("raw_text", "")
    got = [(s.name, s.sem_type.value, s.optional, s.preposition) for s in ps.slots]
    exp = [(s["name"], s["type"], s.get("optional", False), s.get("preposition"))
           for s in pd["slots"]]
    assert got == exp


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_signature_is_mandatory_types_in_order(rd):
    ps = parse_predicate_from_dict(rd)
    exp = tuple(s["type"] for s in rd["predicate"]["slots"] if not s.get("optional", False))
    assert tuple(t.value for t in ps.signature()) == exp
    assert len(ps.mandatory()) + len(ps.optional_slots()) == len(ps.slots)


def test_group_by_signature_partitions_all_roots():
    structs = [parse_predicate_from_dict(r) for r in PILOT_ROOTS]
    groups = group_by_signature(structs)
    assert sum(len(v) for v in groups.values()) == len(PILOT_ROOTS)


def test_constitution_type_inventory():
    """المبدأ العاشر: ١٥ نوعاً و٢٠ محمولاً."""
    assert len(SemanticType) == 15
    assert len(PrimaryPredicate) == 20


@pytest.mark.parametrize("raw", [SemanticType.MUNJIZ.value, SemanticType.SABAB.value])
def test_exact_type_resolves(raw):
    assert _resolve_sem_type(raw).value == raw


# ── لا استنتاج: سلسلة غير مطابقة يجب أن تُرفض لا أن تُطابَق جزئياً ──
@pytest.mark.parametrize("raw", [param("fuzzy-type-سببية", "سببية"),
                                 param("fuzzy-type-م", "م"),
                                 param("fuzzy-type-مكان_الحدث", "مكان الحدث")])
def test_sem_type_no_partial_match(raw):
    with pytest.raises(ValueError):
        _resolve_sem_type(raw)


@pytest.mark.parametrize("raw", [param("fuzzy-pred-ك", "ك"), param("fuzzy-pred-ل", "ل")])
def test_predicate_no_partial_match(raw):
    with pytest.raises(ValueError):
        _resolve_predicate(raw)
