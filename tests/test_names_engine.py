"""الحقلان الأول والخامس من خطة الحقول الخمسة (المالك 2026-11-05).
القيم مضمَّنة، تأليف كلود، OWNER_RATIFIED=NO."""
import pytest

from tests._gold import matches
from core.types import RootType, Baab
from core.support import Unsupported
from engines.names_engine import (derive_names, MafulKind, Transitivity,
                                  TransitivityUnknown, TransitivityConflict)
from engines.derivation_engine import derive
from engines.morphological_engine import conjugate

S, MD = RootType.SAHIH, RootType.MUDAAF

# (الجذر، النوع، الوزن، التعدّي، الحرف، الباب) → (فاعل، مفعول، النوع)
OK = [
    ("كتب", S, "I", "متعدي", None, Baab.FAA_YAF_U, "كَاتِب", "مَكْتُوب", MafulKind.DIRECT),
    ("مرر", MD, "I", "لازم", "ب", Baab.FAA_YAF_U, "مَارّ", "مَمْرُور بِهِ", MafulKind.BI_HARF),
    ("جلس", S, "I", "لازم", None, Baab.FAA_YAF_I, "جَالِس", None, MafulKind.NONE),
    ("ضرب", S, "I", "مشترك", None, Baab.FAA_YAF_I, "ضَارِب", "مَضْرُوب", MafulKind.DIRECT),
    ("رغب", S, "I", "لازم", "في", Baab.FAI_YAF_A, "رَاغِب", "مَرْغُوب فِيهِ", MafulKind.BI_HARF),
    ("كرم", S, "I", "لازم", None, Baab.FAU_YAF_U, "كَارِم", None, MafulKind.NONE),
    ("كسر", S, "VII", "لازم", None, None, "مُنْكَسِر", None, MafulKind.NONE),
    ("كرم", S, "IV", "متعدي", None, None, "مُكْرِم", "مُكْرَم", MafulKind.DIRECT),
    ("حزن", S, "IV", "متعدي", None, None, "مُحْزِن", "مُحْزَن", MafulKind.DIRECT),
]


@pytest.mark.parametrize("l,rt,wz,t,h,b,fa,mf,kind", OK, ids=[f"{o[0]}-{o[2]}-{o[3]}" for o in OK])
def test_names(l, rt, wz, t, h, b, fa, mf, kind):
    n = derive_names(l, rt, wz, t, h, b)
    assert matches(n.ism_faail, [fa]), n.ism_faail
    assert (n.ism_mafuul is None) if mf is None else matches(n.ism_mafuul, [mf]), n.ism_mafuul
    assert n.maful_kind is kind and n.rank == "CANDIDATE"


def test_mushtarak_flagged_not_rejected():
    assert derive_names("ضرب", S, "I", "مشترك").flags == ("MUSHTARAK",)


@pytest.mark.parametrize("t", [None, "", "غير محدد", "متعد"])
def test_unknown_transitivity_rejected(t):
    with pytest.raises(TransitivityUnknown):
        derive_names("كتب", S, "I", t)


@pytest.mark.parametrize("l,wz,t,b", [("كرم", "I", "متعدي", Baab.FAU_YAF_U), ("كسر", "VII", "متعدي", None),
                                       ("حمر", "IX", "مشترك", None), ("كتب", "I", "متعدي+ب", None)],
                         ids=["فعُل-متعدي", "VII-متعدي", "IX-مشترك", "حرف-مع-متعدي"])
def test_conflict_rejected(l, wz, t, b):
    if t == "متعدي+ب":
        with pytest.raises(TransitivityConflict):
            derive_names(l, S, wz, "متعدي", "ب", b)
    else:
        with pytest.raises(TransitivityConflict):
            derive_names(l, S, wz, t, None, b)


def test_unknown_harf_rejected():
    with pytest.raises(ValueError):
        derive_names("مرر", MD, "I", "لازم", "حتى")


# ── الحقل الخامس: الرفض الصريح ──
@pytest.mark.parametrize("l,rt,code", [("ءخذ", S, "MAHMUZ"), ("سءل", S, "MAHMUZ"), ("قرء", S, "MAHMUZ"),
                                       ("رءي", RootType.NAQIS_YAA, "MAHMUZ"), ("طفء", S, "MAHMUZ"),
                                       ("وقي", RootType.LAFIF_MAFRUQ, "LAFIF"), ("دحرج", S, "NOT_TRILITERAL")])
def test_unsupported_rejected_everywhere(l, rt, code):
    sound_mahmuz = code == "MAHMUZ" and rt == S          # مفتوح في derive_names للمجرّد وحده
    for call in ((() if sound_mahmuz else (lambda: derive_names(l, rt, "I", "متعدي"),)) +
                 (lambda: derive_names(l, rt, "IV", "متعدي"),
                 lambda: derive(l, rt, Baab.FAA_YAF_A, [], None, None, None, None, None, None, {}),
                 lambda: conjugate(l, rt, Baab.FAA_YAF_A))):
        with pytest.raises(Unsupported) as e:
            call()
        assert e.value.code == code


# ── المهموز السالم في المجرّد (ملاحظة ahdath ١): الهمزة على كرسيّها، والقيم من اختبارات ahdath ──
@pytest.mark.parametrize("l,fa,mf", [("ءكل", "آكِل", "مَأْكُول"), ("أخذ", "آخِذ", "مَأْخُوذ"),
                                     ("سءل", "سَائِل", "مَسْؤُول/مَسْئُول"), ("قرء", "قَارِئ", "مَقْرُوء")])
def test_sound_mahmuz_names(l, fa, mf):
    n = derive_names(l, S, "I", "متعدي")
    assert matches(n.ism_faail, [fa]) and matches(n.ism_mafuul, mf.split("/")), (n.ism_faail, n.ism_mafuul)


@pytest.mark.parametrize("l,rt", [("رءي", RootType.NAQIS_YAA), ("شيء", RootType.SAHIH), ("ءدد", MD)])
def test_mahmuz_with_weak_or_doubling_rejected(l, rt):
    with pytest.raises(Unsupported):
        derive_names(l, rt, "I", "متعدي")
