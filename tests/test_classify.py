"""مصنِّف نوع الجذر من صورة الفعل (ملاحظة ahdath ٢). القيم مضمَّنة، OWNER_RATIFIED=NO."""
import pytest
from core.classify import classify, past_baab
from core.support import Unsupported
from core.types import RootType as R, Baab


@pytest.mark.parametrize("root,verb,rt,mz", [
    ("كتب", "كَتَبَ", R.SAHIH, False), ("عور", "عَوِرَ", R.SAHIH, False), ("قول", "قَالَ", R.AJWAF_WAW, False),
    ("بيع", "بَاعَ", R.AJWAF_YAA, False), ("خوف", "خَافَ", R.AJWAF_WAW, False), ("دعو", "دَعَا", R.NAQIS_WAW, False),
    ("رمي", "رَمَى", R.NAQIS_YAA, False), ("رضو", "رَضِيَ", R.NAQIS_WAW, False), ("سرو", "سَرُوَ", R.NAQIS_WAW, False),
    ("مرر", "مَرَّ", R.MUDAAF, False), ("وصل", "وَصَلَ", R.MITHAL_WAW, False), ("يسر", "يَسَرَ", R.MITHAL_YAA, False),
    ("ءكل", "أَكَلَ", R.SAHIH, True), ("سءل", "سَأَلَ", R.SAHIH, True), ("قرأ", "قَرَأَ", R.SAHIH, True),
])
def test_classify(root, verb, rt, mz):
    k = classify(root, verb)
    assert (k.root_type, k.mahmuz, k.rank) == (rt, mz, "CANDIDATE")


@pytest.mark.parametrize("root,verb,code", [("رءي", "رَأَى", "MAHMUZ"), ("شيء", "شَاءَ", "MAHMUZ"), ("ءدد", "أَدَّ", "MAHMUZ"),
                                            ("طوي", "طَوَى", "LAFIF"), ("وقي", "وَقَى", "LAFIF"), ("دحرج", "دَحْرَجَ", "NOT_TRILITERAL")])
def test_rejected(root, verb, code):
    with pytest.raises(Unsupported) as e:
        classify(root, verb)
    assert e.value.code == code


def test_past_baab():
    assert past_baab("فَعِلَ (ناقص)") is Baab.FAI_YAF_A and past_baab("فَعَلَ/فَعِلَ (أجوف)") is None
