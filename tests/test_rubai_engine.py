"""الرباعي المجرّد ومزيده (طلب المالك 2026-11-05). القيم مضمَّنة، OWNER_RATIFIED=NO."""
import pytest
from tests._gold import matches, norm
from core.types import RootType
from core.support import Unsupported
from engines.rubai_engine import conjugate_rubai, derive_rubai
from engines.names_engine import derive_names, TransitivityConflict

HU, HUNNA, ANTA, ANTI = ("غائب", "مفرد", "مذكر"), ("غائب", "جمع", "مؤنث"), ("مخاطب", "مفرد", "مذكر"), ("مخاطب", "مفرد", "مؤنث")
T = {"PA": ("ماضٍ", "معلوم"), "PP": ("ماضٍ", "مجهول"), "RA": ("مضارع مرفوع", "معلوم"),
     "RP": ("مضارع مرفوع", "مجهول"), "JZ": ("مضارع مجزوم", "معلوم"), "AM": ("أمر", "معلوم")}
CELLS = [
    ("دحرج", "Q1", "PA", HU, "دَحْرَجَ"), ("دحرج", "Q1", "PA", ANTA, "دَحْرَجْتَ"), ("دحرج", "Q1", "PP", HU, "دُحْرِجَ"),
    ("دحرج", "Q1", "RA", HU, "يُدَحْرِجُ"), ("دحرج", "Q1", "RP", HU, "يُدَحْرَجُ"), ("دحرج", "Q1", "AM", ANTA, "دَحْرِجْ"),
    ("دحرج", "Q2", "PA", HU, "تَدَحْرَجَ"), ("دحرج", "Q2", "RA", HU, "يَتَدَحْرَجُ"), ("دحرج", "Q2", "AM", ANTA, "تَدَحْرَجْ"),
    ("حرجم", "Q3", "PA", HU, "اِحْرَنْجَمَ"), ("حرجم", "Q3", "RA", HU, "يَحْرَنْجِمُ"), ("حرجم", "Q3", "AM", ANTA, "اِحْرَنْجِمْ"),
    ("قشعر", "Q4", "PA", HU, "اِقْشَعَرَّ"), ("قشعر", "Q4", "PA", ANTA, "اِقْشَعْرَرْتَ"), ("قشعر", "Q4", "PA", HUNNA, "اِقْشَعْرَرْنَ"),
    ("قشعر", "Q4", "RA", HU, "يَقْشَعِرُّ"), ("قشعر", "Q4", "RA", HUNNA, "يَقْشَعْرِرْنَ"),
    ("قشعر", "Q4", "JZ", HU, "يَقْشَعِرَّ/يَقْشَعْرِرْ"), ("قشعر", "Q4", "AM", ANTA, "اِقْشَعِرَّ/اِقْشَعْرِرْ"),
    ("قشعر", "Q4", "AM", ANTI, "اِقْشَعِرِّي"),
]


@pytest.mark.parametrize("l,w,t,g,gold", CELLS, ids=[f"{c[0]}-{c[1]}-{c[2]}-{len(c[4])}" for c in CELLS])
def test_cells(l, w, t, g, gold):
    got = conjugate_rubai(l, w).table(*T[t])[g]
    assert {norm(x) for x in got.split("/")} == {norm(x) for x in gold.split("/")}, got


@pytest.mark.parametrize("l,w,masdar,fa,mf", [
    ("دحرج", "Q1", "دَحْرَجَة/دِحْرَاج", "مُدَحْرِج", "مُدَحْرَج"), ("دحرج", "Q2", "تَدَحْرُج", "مُتَدَحْرِج", "مُتَدَحْرَج"),
    ("حرجم", "Q3", "اِحْرِنْجَام", "مُحْرَنْجِم", "مُحْرَنْجَم"), ("قشعر", "Q4", "اِقْشِعْرَار", "مُقْشَعِرّ", "مُقْشَعَرّ")])
def test_derive(l, w, masdar, fa, mf):
    d = derive_rubai(l, w)
    assert {norm(x) for x in d["masdar"].split("/")} == {norm(x) for x in masdar.split("/")}
    assert matches(d["ism_faail"], [fa]) and matches(d["ism_mafuul"], [mf])


def test_paradigm_size():
    for w in ("Q1", "Q2", "Q3", "Q4"):
        assert len(conjugate_rubai("دحرج", w).cells) == 90


@pytest.mark.parametrize("l,code", [("طمءن", "MAHMUZ"), ("كتب", "NOT_QUADRILITERAL"), ("سلقي", "NAQIS_RUBAI")])
def test_rejected(l, code):
    with pytest.raises(Unsupported) as e:
        conjugate_rubai(l, "Q1")
    assert e.value.code == code


def test_names_rubai():
    n = derive_names("دحرج", RootType.SAHIH, "Q1", "متعدي")
    assert matches(n.ism_mafuul, ["مُدَحْرَج"])
    assert derive_names("قشعر", RootType.SAHIH, "Q4", "لازم").ism_mafuul is None
    with pytest.raises(TransitivityConflict):
        derive_names("حرجم", RootType.SAHIH, "Q3", "متعدي")


# ── لام نونية + نون النسوة/«نا» → نون مشدّدة، في الثلاثي والرباعي ──
@pytest.mark.parametrize("cell,gold", [
    ((("ماضٍ", "معلوم"), HUNNA), "سَكَنَّ"), ((("ماضٍ", "معلوم"), ("متكلم", "جمع", "-")), "سَكَنَّا"),
    ((("مضارع مرفوع", "معلوم"), HUNNA), "يَسْكُنَّ"), ((("أمر", "معلوم"), ("مخاطب", "جمع", "مؤنث")), "اُسْكُنَّ"),
    ((("ماضٍ", "معلوم"), ANTA), "سَكَنْتَ")])
def test_triliteral_final_nun(cell, gold):
    from engines.morphological_engine import conjugate
    from core.types import Baab
    got = conjugate("سكن", RootType.SAHIH, Baab.FAA_YAF_U).table(*cell[0])[cell[1]]
    assert norm(got) == norm(gold), got


def test_ajwaf_final_nun():
    from engines.morphological_engine import conjugate
    from core.types import Baab
    assert norm(conjugate("كون", RootType.AJWAF_WAW, Baab.FAA_YAF_U).table("ماضٍ", "معلوم")[HUNNA]) == norm("كُنَّ")


def test_rubai_final_nun():
    assert norm(conjugate_rubai("فرجن", "Q1").table("ماضٍ", "معلوم")[HUNNA]) == norm("فَرْجَنَّ")
