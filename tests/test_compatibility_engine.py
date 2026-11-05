"""محرك التوافق — مطابقة الشبكة والاستثناءات لبيانات المالك، وخاصية دستورية واحدة."""
import pytest

from tests._pilot import PILOT_ROOTS
from tests.known_defects import param
from engines.compatibility_engine import (build_compatibility_map, parse_network_from_dict,
                                          parse_exceptions_from_dict, semantic_neighbors)

REL = ["yushbih", "yuaakis", "yastlzim", "yasbiq", "aamma", "akhass"]


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_network_parsed_exactly(rd):
    net = parse_network_from_dict(rd)
    for k in REL:
        assert getattr(net, k) == rd.get("network", {}).get(k, []), k


@pytest.mark.parametrize("rd", PILOT_ROOTS, ids=lambda r: r["letters"])
def test_exceptions_parsed_exactly(rd):
    got = [(e.slot, e.override_type, e.note) for e in parse_exceptions_from_dict(rd)]
    exp = [(e["slot"], e["override_type"], e.get("note", "")) for e in rd["compatibility_exceptions"]]
    assert got == exp


def test_map_covers_all_unordered_pairs():
    rcm = build_compatibility_map(PILOT_ROOTS)
    n = len(PILOT_ROOTS)
    assert len(rcm.results) == n * (n - 1) // 2
    assert len({frozenset(k) for k in rcm.results}) == len(rcm.results)


def test_semantic_neighbors_reads_network():
    nets = {r["letters"]: parse_network_from_dict(r) for r in PILOT_ROOTS}
    r0 = PILOT_ROOTS[0]
    assert semantic_neighbors(r0["letters"], nets, "يشبه") == r0["network"]["yushbih"]


# ── المبدأ الثالث + المحظور الأول: القابلية شرط نوعي لا احتمال ──
@pytest.mark.parametrize("dummy", [param("P3-binary-verdict", 0)])
def test_compatibility_verdict_is_binary(dummy):
    rcm = build_compatibility_map(PILOT_ROOTS)
    for res in rcm.results.values():
        assert not hasattr(res, "score"), "درجة احتمالية [0..1] — يخالف م٣ والمحظور ١"


def test_verdict_values_and_basis():
    rcm = build_compatibility_map(PILOT_ROOTS)
    for res in rcm.results.values():
        assert res.verdict in ("ACCEPT", "DEFER", "BLOCK")
        assert res.is_compatible == (res.verdict == "ACCEPT")
        if res.verdict == "ACCEPT":
            assert {"CHAIN_AB", "CHAIN_BA"} & set(res.basis) and "BARRIER_OPPOSES" not in res.basis
