"""الحقل الثالث: لا يُعرض مسلك تعدية لم يجتز القياس (2026-11-06)."""
import pytest
from engines import taadiya_engine as T


def test_no_route_accepted_rejects_explicitly():
    if T.ACCEPTED_ROUTES:
        pytest.skip("مسلك مقبول — يُختبر في test_accepted_route")
    with pytest.raises(T.RouteNotAccepted):
        T.taadiya_of("حَزِنَ")


def test_accepted_route_lookup(monkeypatch):
    rows = T._rows("T_JAL")
    if not rows:
        pytest.skip("جدول ahdath غير موجود في هذه البيئة")
    monkeypatch.setitem(T.ACCEPTED_ROUTES, "T_JAL", "test-only")
    got = T.taadiya_of(rows[0]["base"], routes=["T_JAL"])
    assert got and got[0].mutaaddi == rows[0]["verb"] and got[0].rank == "CANDIDATE"
    with pytest.raises(T.NoSamaa):
        T.taadiya_of("لا-فعل", routes=["T_JAL"])
