"""الناقص بحسب حركة العين (إعادة كتابة 2026-11-06). القيم مضمَّنة، OWNER_RATIFIED=NO."""
import pytest
from tests._gold import norm
from core.types import RootType as R, Baab as B
from engines.morphological_engine import conjugate

HU, HI, HUM, HUNNA, ANTA, ANTI = (("غائب", "مفرد", "مذكر"), ("غائب", "مفرد", "مؤنث"), ("غائب", "جمع", "مذكر"),
                                  ("غائب", "جمع", "مؤنث"), ("مخاطب", "مفرد", "مذكر"), ("مخاطب", "مفرد", "مؤنث"))
T = {"PA": ("ماضٍ", "معلوم"), "PP": ("ماضٍ", "مجهول"), "RA": ("مضارع مرفوع", "معلوم"), "RP": ("مضارع مرفوع", "مجهول"),
     "NS": ("مضارع منصوب", "معلوم"), "JZ": ("مضارع مجزوم", "معلوم"), "AM": ("أمر", "معلوم")}
CASES = [
    ("بقي", R.NAQIS_YAA, B.FAI_YAF_A, [("PA", HU, "بَقِيَ"), ("PA", HUM, "بَقُوا"), ("PA", ANTA, "بَقِيتَ"), ("PA", HUNNA, "بَقِينَ"),
                                        ("RA", HU, "يَبْقَى"), ("RA", HUM, "يَبْقَوْنَ"), ("RA", ANTI, "تَبْقَيْنَ"), ("NS", ANTI, "تَبْقَيْ"),
                                        ("JZ", HU, "يَبْقَ"), ("AM", ANTA, "اِبْقَ"), ("AM", ("مخاطب", "جمع", "مذكر"), "اِبْقَوْا")]),
    ("رضو", R.NAQIS_WAW, B.FAI_YAF_A, [("PA", HU, "رَضِيَ"), ("PA", HI, "رَضِيَتْ"), ("RA", HU, "يَرْضَى"), ("RA", ("غائب", "مثنى", "مذكر"), "يَرْضَيَانِ")]),
    ("سعي", R.NAQIS_YAA, B.FAA_YAF_A, [("PA", HU, "سَعَى"), ("RA", HU, "يَسْعَى"), ("JZ", HU, "يَسْعَ"), ("AM", ANTA, "اِسْعَ")]),
    ("سرو", R.NAQIS_WAW, B.FAU_YAF_U, [("PA", HU, "سَرُوَ"), ("PA", HUM, "سَرُوا"), ("PA", ANTA, "سَرُوتَ"), ("RA", HU, "يَسْرُو")]),
    ("رمي", R.NAQIS_YAA, B.FAA_YAF_I, [("RA", HUM, "يَرْمُونَ"), ("RP", HU, "يُرْمَى"), ("RP", ("غائب", "مثنى", "مذكر"), "يُرْمَيَانِ"),
                                        ("PP", HUM, "رُمُوا"), ("PP", HI, "رُمِيَتْ"), ("AM", ANTI, "اِرْمِي")]),
    ("دعو", R.NAQIS_WAW, B.FAA_YAF_U, [("RA", ANTI, "تَدْعِينَ"), ("RA", HUNNA, "يَدْعُونَ"), ("RP", HU, "يُدْعَى"), ("NS", HU, "يَدْعُوَ"),
                                        ("JZ", HU, "يَدْعُ"), ("AM", ANTA, "اُدْعُ"), ("AM", ("مخاطب", "مثنى", "مذكر"), "اُدْعُوَا")]),
]
FLAT = [(l, rt, b, t, g, gold) for l, rt, b, cells in CASES for t, g, gold in cells]


@pytest.mark.parametrize("l,rt,b,t,g,gold", FLAT, ids=[f"{x[0]}-{x[3]}-{x[5]}" for x in FLAT])
def test_naqis(l, rt, b, t, g, gold):
    got = conjugate(l, rt, b).table(*T[t])[g]
    assert norm(got) == norm(gold), got
