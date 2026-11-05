"""باب فَعِلَ يَفْعِلُ (حَسِبَ يَحْسِبُ، وَرِثَ يَرِثُ) — أُضيف 2026-11-05 بطلب المالك.

لا جذر تجريبي في pilot_roots.json على هذا الباب، فالقيم هنا مضمَّنة في الاختبار.
تأليف كلود، OWNER_RATIFIED=NO. الاصطلاحات كما في tests/gold/GOLD_CONVENTIONS.md.
"""
import pytest

from tests._gold import matches
from tests.known_defects import param
from core.types import RootType, Baab
from engines.morphological_engine import conjugate
from engines.derivation_engine import derive

ROOTS = {"حسب": RootType.SAHIH, "ورث": RootType.MITHAL_WAW}
TABLES = {"PA": ("ماضٍ", "معلوم"), "PP": ("ماضٍ", "مجهول"), "RA": ("مضارع مرفوع", "معلوم"),
          "RP": ("مضارع مرفوع", "مجهول"), "NS": ("مضارع منصوب", "معلوم"),
          "JZ": ("مضارع مجزوم", "معلوم"), "AM": ("أمر", "معلوم")}
HU, ANTI, ANTA = ("غائب", "مفرد", "مذكر"), ("مخاطب", "مفرد", "مؤنث"), ("مخاطب", "مفرد", "مذكر")
TAG = {HU: "هو", ANTI: "أنتِ", ANTA: "أنتَ"}

CONJ = [  # (الجذر، الجدول، الشخص، الذهبي)
    ("حسب", "PA", HU, "حَسِبَ"), ("حسب", "PP", HU, "حُسِبَ"), ("حسب", "RA", HU, "يَحْسِبُ"),
    ("حسب", "RA", ANTI, "تَحْسِبِينَ"), ("حسب", "RP", HU, "يُحْسَبُ"), ("حسب", "NS", HU, "يَحْسِبَ"),
    ("حسب", "JZ", HU, "يَحْسِبْ"), ("حسب", "AM", ANTA, "اِحْسِبْ"),
    ("ورث", "PA", HU, "وَرِثَ"), ("ورث", "PP", HU, "وُرِثَ"), ("ورث", "RA", HU, "يَرِثُ"),
    ("ورث", "RA", ANTI, "تَرِثِينَ"), ("ورث", "RP", HU, "يُورَثُ"), ("ورث", "NS", HU, "يَرِثَ"),
    ("ورث", "JZ", HU, "يَرِثْ"), ("ورث", "AM", ANTA, "رِثْ"),
]
DERIV = [  # (الجذر، الحقل، البدائل)
    ("حسب", "ism_faail", "حَاسِب"), ("حسب", "ism_mafuul", "مَحْسُوب"),
    ("حسب", "ism_makan", "مَحْسِب"), ("حسب", "ism_aala", "مِحْسَب/مِحْسَبَة/مِحْسَاب"),
    ("ورث", "ism_faail", "وَارِث"), ("ورث", "ism_mafuul", "مَوْرُوث"),
    ("ورث", "ism_makan", "مَوْرِث"), ("ورث", "ism_aala", "مِيرَث/مِيرَثَة/مِيرَاث"),
]


def test_baab_value():
    assert Baab("فَعِلَ يَفْعِلُ") is Baab.FAI_YAF_I


@pytest.mark.parametrize("root,table,pgn,gold",
                         [param(f"{r}-{t}-{TAG[p]}", r, t, p, g) for r, t, p, g in CONJ])
def test_conjugation(root, table, pgn, gold):
    actual = conjugate(root, ROOTS[root], Baab.FAI_YAF_I).table(*TABLES[table]).get(pgn)
    assert actual is not None and matches(actual, [gold]), f"المحرك={actual!r}  الذهبي={gold!r}"


@pytest.mark.parametrize("root,field,gold",
                         [param(f"{r}-{f.replace('ism_', 'I.')}", r, f, g) for r, f, g in DERIV])
def test_derivation(root, field, gold):
    d = derive(root, ROOTS[root], Baab.FAI_YAF_I, [], None, None, None, None, None, None, {})
    actual = getattr(d, field)
    assert actual is not None and matches(actual, gold.split("/")), f"المحرك={actual!r}  الذهبي={gold!r}"
